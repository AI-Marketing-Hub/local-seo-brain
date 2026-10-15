#!/usr/bin/env python3
"""
Ingest a citation export (Whitespark, BrightLocal, Moz Local, or generic CSV).

Writes:
  - Raw copy under .raw/clients/<client>/citations/
  - One source note under wiki/sources/
  - One citation note per row under wiki/citations/
  - Updates relevant hubs

V0.1 scope: CSV file ingest only. No live API calls, no automatic submission.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from runtime import touch_note_updated, vault_mutation, immutable_raw_target, install_immutable_raw, parse_as_of, require_source, require_vault, safe_slug, update_raw_manifest


KNOWN_HEADERS = {
    "whitespark": {"directory", "url", "status"},
    "brightlocal": {"directory_name", "listing_url", "accuracy"},
    "moz_local": {"location_name", "directory", "listing_status"},
}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--file", required=True, help="Citation export CSV")
    parser.add_argument("--client", required=True)
    parser.add_argument("--location", default=None)
    parser.add_argument("--limit", type=int, default=200, help="max rows to materialize as notes")
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.limit < 1:
        raise SystemExit("ERROR: --limit must be at least 1")

    vault = require_vault(args.vault)
    with vault_mutation(vault, dry_run=args.dry_run):
        source = require_source(args.file, suffixes={".csv"})

        client = safe_slug(args.client)
        location = safe_slug(args.location or args.client)
        today = parse_as_of(args.as_of)

        # 1. Copy raw
        raw_dir = vault / ".raw" / "clients" / client / "citations"
        raw, digest = immutable_raw_target(raw_dir, source, today)
        if not args.dry_run:
            install_immutable_raw(source, raw, digest)
        parse_source = source if args.dry_run else raw

        # 2. Parse CSV
        rows, header = read_csv(parse_source, limit=args.limit)
        platform = detect_platform(header)
        if args.dry_run:
            print(f"DRY-RUN: would ingest {len(rows)} {platform} citation rows for {client}/{location}")
            return 0
        raw_dir.mkdir(parents=True, exist_ok=True)
        install_immutable_raw(source, raw, digest)
        update_raw_manifest(vault, raw_path=raw, digest=digest, kind="citations", as_of=today, client=client)

        # 3. Write source note
        src_slug = safe_slug(f"Citations Export {client} {today} {digest[:12]}")
        src_path = vault / "wiki" / "sources" / f"{src_slug}.md"
        src_path.write_text(
            source_note(src_slug, raw.relative_to(vault).as_posix(), digest, len(rows), platform, today, location),
            encoding="utf-8",
        )

        # 4. Write citation notes
        cit_dir = vault / "wiki" / "citations"
        cit_dir.mkdir(parents=True, exist_ok=True)
        cit_slugs: list[str] = []
        for row in rows:
            directory = pick_field(row, ["directory", "directory_name", "name", "site"]) or "unknown"
            url = pick_field(row, ["url", "listing_url", "link"]) or ""
            status = pick_field(row, ["status", "accuracy", "listing_status"]) or "unknown"
            slug = safe_slug(f"{client}-{directory}")
            cit_path = cit_dir / f"{slug}.md"
            cit_path.write_text(
                citation_note(slug, directory, url, status, location, src_slug, today),
                encoding="utf-8",
            )
            cit_slugs.append(slug)

        # 5. Update hubs
        update_hub(vault, "sources", src_slug, today)
        for slug in cit_slugs:
            update_hub(vault, "citations", slug, today)

        append_log(vault, f"Citation export ingested for {client} ({platform}, {len(cit_slugs)} citations).", today)
        print(f"OK: {len(cit_slugs)} citation notes written. Source: {src_path}")
        return 0

def read_csv(path: Path, *, limit: int) -> tuple[list[dict[str, str]], list[str]]:
    rows: list[dict[str, str]] = []
    header: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh)
        header = [h.lower().strip() for h in (reader.fieldnames or [])]
        for i, row in enumerate(reader):
            if i >= limit:
                break
            rows.append({(k or "").lower().strip(): (v or "").strip() for k, v in row.items()})
    return rows, header


def detect_platform(header: list[str]) -> str:
    cols = set(header)
    for name, expected in KNOWN_HEADERS.items():
        if expected.issubset(cols):
            return name
    return "generic"


def pick_field(row: dict[str, str], keys: list[str]) -> str:
    for key in keys:
        if key in row and row[key]:
            return row[key]
    return ""


def source_note(slug: str, raw_rel: str, digest: str, count: int, platform: str, today: str, location: str) -> str:
    return f"""---
type: "source"
title: "Citations Export ({today})"
created: "{today}"
updated: "{today}"
status: "imported"
tags: ["type/source", "domain/citations", "provenance/raw"]
source_kind: "citation-csv-export"
source_path: "{raw_rel}"
source_hash: "sha256:{digest}"
location: "{location}"
platform: "{platform}"
---

# Citations Export ({today})

## Source

- Path: `{raw_rel}`
- SHA-256: `{digest}`
- Retrieved: {today}
- Platform: {platform}
- Rows ingested: {count}

## Compiled Truth

Citation snapshot for [[{location}]] from a {platform} export. {count} directory
listings were materialized as individual notes under `wiki/citations/`.

This adapter captures only the directory name, URL, and exported status. It
does not calculate a NAP difference or competitor gap. Compare each listing
with owner-confirmed canonical data before proposing a correction.

## Refusal

- No mass submission to low-quality directories.
- No fake-business citations.
- No directory scraping that violates ToS.

## Related

- [[{location}]]
- [[wiki/citations/_index|Citations Hub]]
- [[Citation Audit Workflow]]
- [[backlinking-local-citations|Backlinking: Local Citations]]
"""


def citation_note(slug: str, directory: str, url: str, status: str, location: str, src_slug: str, today: str) -> str:
    return f"""---
type: "citation"
title: "{directory}"
directory: "{directory}"
url: "{url}"
status: "{status}"
location: "{location}"
created: "{today}"
updated: "{today}"
tags: ["type/citation", "domain/citations"]
---

# {directory}

## Listing

- URL: {url or "(unknown)"}
- Status: {status}

## NAP review (not computed)

| Field | Listed | Canonical | Match |
|---|---|---|---|
| Name | not present in this adapter | see [[{location}]] | not evaluated |
| Address | not present in this adapter | see [[{location}]] | not evaluated |
| Phone | not present in this adapter | see [[{location}]] | not evaluated |

Any proposed listing correction requires owner confirmation and an Approval
Queue entry. This export alone does not authorize a directory change.

## Source

Ingested from [[{src_slug}]] on {today}.

## Related

- [[{location}]]
- [[wiki/citations/_index|Citations Hub]]
- [[Citation Audit Workflow]]
"""


def update_hub(vault: Path, folder: str, slug: str, today: str) -> None:
    hub = vault / "wiki" / folder / "_index.md"
    text = hub.read_text(encoding="utf-8") if hub.exists() else f"# {folder.title()} Hub\n\n## Notes\n"
    link = f"- [[{slug}]]"
    if link not in text:
        if "## Notes\n\n- None yet" in text:
            text = text.replace("## Notes\n\n- None yet", f"## Notes\n\n{link}")
        elif "## Notes" in text:
            text = re.sub(r"## Notes\n", f"## Notes\n\n{link}\n", text, count=1)
        else:
            text = text.rstrip() + f"\n\n## Notes\n\n{link}\n"
    hub.write_text(text, encoding="utf-8")
    touch_note_updated(hub, today)


def append_log(vault: Path, message: str, today: str) -> None:
    log = vault / "wiki" / "log.md"
    text = log.read_text(encoding="utf-8") if log.exists() else "# Log\n"
    line = f"- {today} - {message}"
    if line not in text:
        log.write_text(text.rstrip() + f"\n{line}\n", encoding="utf-8")
        touch_note_updated(log, today)


if __name__ == "__main__":
    raise SystemExit(main())

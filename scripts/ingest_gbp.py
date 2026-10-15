#!/usr/bin/env python3
"""
Ingest a Google Business Profile Insights/Performance CSV export.

Writes:
  - Raw copy under .raw/clients/<client>/gbp/
  - One source note under wiki/sources/
  - One location note under wiki/locations/ (or appends to existing)
  - One log entry

V0.1 scope: CSV file ingest only. No GBP API mutation. Brain stays advisory.
"""
from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

from runtime import touch_note_updated, vault_mutation, immutable_raw_target, install_immutable_raw, parse_as_of, require_source, require_vault, safe_slug, update_raw_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--file", required=True, help="GBP CSV export path")
    parser.add_argument("--client", required=True, help="client slug, e.g. acme-plumbing")
    parser.add_argument("--location", default=None, help="location slug; defaults to client slug")
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    vault = require_vault(args.vault)
    with vault_mutation(vault, dry_run=args.dry_run):
        source = require_source(args.file, suffixes={".csv"})

        client = safe_slug(args.client)
        location = safe_slug(args.location or args.client)
        today = parse_as_of(args.as_of)

        # 1. Copy raw
        raw_dir = vault / ".raw" / "clients" / client / "gbp"
        raw, digest = immutable_raw_target(raw_dir, source, today)
        if not args.dry_run:
            install_immutable_raw(source, raw, digest)
        parse_source = source if args.dry_run else raw

        # 2. Parse CSV summary
        summary = summarize_csv(parse_source)
        if args.dry_run:
            print(f"DRY-RUN: would ingest {source} for {client}/{location}; rows: {summary.get('rows', 0)}")
            return 0
        raw_dir.mkdir(parents=True, exist_ok=True)
        install_immutable_raw(source, raw, digest)
        update_raw_manifest(vault, raw_path=raw, digest=digest, kind="gbp", as_of=today, client=client)

        # 3. Write source note
        src_dir = vault / "wiki" / "sources"
        src_dir.mkdir(parents=True, exist_ok=True)
        src_title = f"GBP Export - {client} - {today}"
        src_slug = safe_slug(f"{src_title} {digest[:12]}")
        src_path = src_dir / f"{src_slug}.md"
        src_path.write_text(source_note(src_title, raw.relative_to(vault).as_posix(), digest, summary, today, location), encoding="utf-8")

        # 4. Append/update location note
        loc_dir = vault / "wiki" / "locations"
        loc_dir.mkdir(parents=True, exist_ok=True)
        loc_path = loc_dir / f"{location}.md"
        if loc_path.exists():
            existing = loc_path.read_text(encoding="utf-8")
            entry = f"\n- {today} - GBP export ingested → [[{src_slug}]] (sha256:{digest[:8]})"
            if entry.strip() not in existing:
                loc_path.write_text(existing.rstrip() + entry + "\n", encoding="utf-8")
        else:
            loc_path.write_text(location_note(location, client, today, src_slug, digest), encoding="utf-8")

        # 5. Update hubs
        update_hub(vault, "sources", src_slug, today)
        update_hub(vault, "locations", location, today)
        append_log(vault, f"GBP export ingested for {client}/{location}. Source: [[{src_slug}]].", today)

        print(f"OK: {src_path}")
        print(f"OK: {loc_path}")
        return 0

def summarize_csv(path: Path) -> dict[str, object]:
    """Lightweight CSV introspection — rows, columns, sample header."""
    try:
        with path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
            reader = csv.reader(fh)
            header = next(reader, [])
            count = sum(1 for _ in reader)
        return {
            "rows": count,
            "columns": len(header),
            "header_sample": ", ".join(header[:8]) + ("..." if len(header) > 8 else ""),
        }
    except Exception as exc:
        return {"error": str(exc), "rows": 0, "columns": 0, "header_sample": ""}


def source_note(title: str, raw_rel: str, digest: str, summary: dict, today: str, location: str) -> str:
    return f"""---
type: "source"
title: "{title}"
created: "{today}"
updated: "{today}"
status: "imported"
tags: ["type/source", "domain/gbp", "provenance/raw"]
source_kind: "gbp-csv-export"
source_path: "{raw_rel}"
source_hash: "sha256:{digest}"
location: "{location}"
---

# {title}

## Source

- Path: `{raw_rel}`
- SHA-256: `{digest}`
- Retrieved: {today}
- Kind: Google Business Profile CSV export (Insights or Performance)

## Compiled Truth

CSV introspection:

- Rows: {summary.get("rows", 0)}
- Columns: {summary.get("columns", 0)}
- Header sample: `{summary.get("header_sample", "")}`

> This adapter records file-level provenance and structural CSV metadata. It
> does not calculate performance trends or infer causes from the export.

## Refusal

This source does not authorize any GBP profile mutation. All recommendations
derived from this data route through [[Approval Queue]] before execution.

## Related

- [[{location}]]
- [[wiki/sources/_index|Sources Hub]]
- [[GBP Optimization Workflow]]
- [[wiki/gbp/_index|GBP Hub]]
"""


def location_note(location: str, client: str, today: str, src_slug: str, digest: str) -> str:
    pretty = location.replace("-", " ").title()
    return f"""---
type: "location"
title: "{pretty}"
location_slug: "{location}"
client: "{client}"
created: "{today}"
updated: "{today}"
status: "active"
tags: ["type/location", "domain/gbp"]
---

# {pretty}

## Canonical NAP

- **Name**: TBD — confirm with client
- **Address**: TBD — confirm with client
- **Phone**: TBD — confirm with client

> Lock NAP before any GBP or citation work. NAP drift across citations
> becomes a fix list under [[Citation Audit Workflow]].

## GBP

- Profile URL: TBD
- Verification status: TBD
- Categories: TBD
- Service area: TBD

## Sources

- [[{src_slug}]] - first GBP export ({today})

## Audits

- Property: not yet started → [[Property Audit Workflow]]
- GBP: not yet started → [[GBP Optimization Workflow]]
- Citations: not yet started → [[Citation Audit Workflow]]

## Timeline

- {today} - GBP export ingested → [[{src_slug}]] (sha256:{digest[:8]})

## Related

- [[wiki/locations/_index|Locations Hub]]
- [[wiki/sources/_index|Sources Hub]]
- [[Index]]
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

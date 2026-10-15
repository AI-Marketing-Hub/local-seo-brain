#!/usr/bin/env python3
"""
Ingest a geo-grid rank-tracker scan (Local Falcon, GeoRanker, Local Viking CSV).

Writes:
  - Raw copy under .raw/clients/<client>/geogrid/
  - Source note under wiki/sources/
  - One scan note per keyword under wiki/keywords/

V0.1 scope: aggregate per-keyword average position. No heatmap math
(that lands in v0.2 along with the generate_geogrid_svg.py renderer).
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict
from pathlib import Path
from statistics import mean

from runtime import touch_note_updated, vault_mutation, immutable_raw_target, install_immutable_raw, parse_as_of, require_source, require_vault, safe_slug, update_raw_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--file", required=True, help="Geo-grid CSV export")
    parser.add_argument("--client", required=True)
    parser.add_argument("--location", default=None)
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
        raw_dir = vault / ".raw" / "clients" / client / "geogrid"
        raw, digest = immutable_raw_target(raw_dir, source, today)
        if not args.dry_run:
            install_immutable_raw(source, raw, digest)
        parse_source = source if args.dry_run else raw

        # 2. Parse
        scans, header = parse_geogrid(parse_source)
        if not scans:
            raise SystemExit("ERROR: no parseable scan rows. Expected columns containing keyword and rank/position.")

        by_keyword: dict[str, list[float]] = defaultdict(list)
        by_keyword_coverage: dict[str, int] = defaultdict(int)
        by_keyword_top3: dict[str, int] = defaultdict(int)
        for s in scans:
            kw = s["keyword"]
            rank = s["rank"]
            if rank is None:
                continue
            by_keyword[kw].append(float(rank))
            by_keyword_coverage[kw] += 1
            if rank <= 3:
                by_keyword_top3[kw] += 1
        if args.dry_run:
            print(f"DRY-RUN: would ingest {len(scans)} grid points for {len(by_keyword)} keywords")
            return 0
        raw_dir.mkdir(parents=True, exist_ok=True)
        install_immutable_raw(source, raw, digest)
        update_raw_manifest(vault, raw_path=raw, digest=digest, kind="geogrid", as_of=today, client=client)

        # 3. Source note
        src_slug = safe_slug(f"Geogrid Scan {client} {today} {digest[:12]}")
        src_path = vault / "wiki" / "sources" / f"{src_slug}.md"
        src_path.write_text(
            source_note(src_slug, raw.relative_to(vault).as_posix(), digest, len(scans), len(by_keyword), today, location, header),
            encoding="utf-8",
        )

        # 4. Per-keyword notes
        kw_dir = vault / "wiki" / "keywords"
        kw_dir.mkdir(parents=True, exist_ok=True)
        written: list[str] = []
        for kw, ranks in by_keyword.items():
            slug = safe_slug(f"{client}-{kw}")
            path = kw_dir / f"{slug}.md"
            avg = mean(ranks)
            top3_share = by_keyword_top3[kw] / by_keyword_coverage[kw] if by_keyword_coverage[kw] else 0.0
            path.write_text(
                keyword_note(slug, kw, location, ranks, avg, top3_share, src_slug, today),
                encoding="utf-8",
            )
            written.append(slug)

        # 5. Hubs + log
        update_hub(vault, "sources", src_slug, today)
        for slug in written:
            update_hub(vault, "keywords", slug, today)
        append_log(vault, f"Geo-grid scan ingested for {client} ({len(written)} keywords, {len(scans)} grid points).", today)

        print(f"OK: {len(written)} keyword notes. Source: {src_path}")
        return 0

def parse_geogrid(path: Path) -> tuple[list[dict[str, object]], list[str]]:
    rows: list[dict[str, object]] = []
    header: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
        reader = csv.DictReader(fh)
        header = [h.lower().strip() for h in (reader.fieldnames or [])]
        for row in reader:
            lower = {(k or "").lower().strip(): (v or "").strip() for k, v in row.items()}
            kw = pick(lower, ["keyword", "query", "search_term", "term"])
            rank = pick(lower, ["rank", "position", "pos", "ranking"])
            lat = pick(lower, ["lat", "latitude"])
            lng = pick(lower, ["lng", "lon", "long", "longitude"])
            if not kw:
                continue
            rows.append({
                "keyword": kw.strip(),
                "rank": coerce_rank(rank),
                "lat": coerce_float(lat),
                "lng": coerce_float(lng),
            })
    return rows, header


def coerce_rank(val: object) -> int | None:
    if val is None or val == "":
        return None
    try:
        n = int(float(val))
        return n if n > 0 else None
    except (TypeError, ValueError):
        return None


def coerce_float(val: object) -> float | None:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def pick(d: dict, keys: list[str]) -> str:
    for k in keys:
        if k in d and d[k]:
            return str(d[k])
    return ""


def source_note(slug: str, raw_rel: str, digest: str, count: int, kw_count: int, today: str, location: str, header: list[str]) -> str:
    return f"""---
type: "source"
title: "Geo-grid Scan ({today})"
created: "{today}"
updated: "{today}"
status: "imported"
tags: ["type/source", "domain/geogrid", "provenance/raw"]
source_kind: "geogrid-csv"
source_path: "{raw_rel}"
source_hash: "sha256:{digest}"
location: "{location}"
---

# Geo-grid Scan ({today})

## Source

- Path: `{raw_rel}`
- SHA-256: `{digest}`
- Retrieved: {today}
- Grid points: {count}
- Keywords: {kw_count}
- Header: `{", ".join(header[:8])}`

## Compiled Truth

Geo-grid scan ingested for [[{location}]]. Per-keyword aggregate notes are
materialized under `wiki/keywords/`.

The adapter reports descriptive aggregates only. It does not infer a cause,
forecast movement, or claim a complete view of the local market.

## Related

- [[{location}]]
- [[wiki/keywords/_index|Keywords Hub]]
- [[Citation Audit Workflow]]
"""


def keyword_note(slug: str, keyword: str, location: str, ranks: list[float], avg: float, top3_share: float, src_slug: str, today: str) -> str:
    rank_min = min(ranks)
    rank_max = max(ranks)
    return f"""---
type: "keyword-scan"
title: "{keyword}"
keyword: "{keyword}"
location: "{location}"
avg_rank: {avg:.2f}
min_rank: {int(rank_min)}
max_rank: {int(rank_max)}
top3_share: {top3_share:.3f}
grid_points: {len(ranks)}
created: "{today}"
updated: "{today}"
status: "observed"
tags: ["type/keyword-scan", "domain/geogrid"]
---

# {keyword}

## Headline

Average rank **{avg:.1f}** across {len(ranks)} grid points. Best **#{int(rank_min)}**,
worst **#{int(rank_max)}**. Top-3 coverage: **{top3_share * 100:.0f}%**.

## Interpretation boundary

The average and top-three share describe this export's sampled coordinates,
query, device, locale, collection window, and provider settings. They do not
identify a cause or justify address, category, content, citation, or proximity
changes by themselves. Compare like-for-like scans before proposing an action.

## Source

[[{src_slug}]]

## Related

- [[{location}]]
- [[wiki/keywords/_index|Keywords Hub]]
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

#!/usr/bin/env python3
"""
Ingest a review export (Google reviews JSON or generic CSV with rating/date/text).

Writes:
  - Raw copy under .raw/clients/<client>/reviews/
  - One source note under wiki/sources/
  - One aggregated review-summary note under wiki/reviews/

V0.1 scope: stats only (rating distribution, count, date range). No
per-review notes by default to keep the vault scannable. No PII — author
names are hashed before storage.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

from runtime import touch_note_updated, vault_mutation, immutable_raw_target, install_immutable_raw, parse_as_of, require_source, require_vault, safe_slug, update_raw_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--file", required=True, help="Reviews JSON or CSV export")
    parser.add_argument("--client", required=True)
    parser.add_argument("--location", default=None)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    vault = require_vault(args.vault)
    with vault_mutation(vault, dry_run=args.dry_run):
        source = require_source(args.file, suffixes={".json", ".csv"})

        client = safe_slug(args.client)
        location = safe_slug(args.location or args.client)
        today = parse_as_of(args.as_of)

        # 1. Copy raw
        raw_dir = vault / ".raw" / "clients" / client / "reviews"
        raw, digest = immutable_raw_target(raw_dir, source, today)
        if not args.dry_run:
            install_immutable_raw(source, raw, digest)
        parse_source = source if args.dry_run else raw

        # 2. Parse
        reviews = parse_reviews(parse_source)
        if not reviews:
            raise SystemExit("ERROR: no parseable reviews found. Expected JSON list or CSV with rating/date columns.")

        stats = aggregate(reviews)
        if args.dry_run:
            print(f"DRY-RUN: would ingest {stats['count']} reviews for {client}/{location}; derived notes omit author identity")
            return 0
        raw_dir.mkdir(parents=True, exist_ok=True)
        install_immutable_raw(source, raw, digest)
        update_raw_manifest(vault, raw_path=raw, digest=digest, kind="reviews", as_of=today, client=client)

        # 3. Write source note
        src_slug = safe_slug(f"Reviews Export {client} {today} {digest[:12]}")
        src_path = vault / "wiki" / "sources" / f"{src_slug}.md"
        src_path.write_text(
            source_note(src_slug, raw.relative_to(vault).as_posix(), digest, stats, today, location),
            encoding="utf-8",
        )

        # 4. Write aggregated review summary note
        rev_dir = vault / "wiki" / "reviews"
        rev_dir.mkdir(parents=True, exist_ok=True)
        rev_slug = safe_slug(f"{client}-review-summary-{today}")
        rev_path = rev_dir / f"{rev_slug}.md"
        rev_path.write_text(review_summary_note(rev_slug, stats, src_slug, location, today), encoding="utf-8")

        # 5. Hubs + log
        update_hub(vault, "sources", src_slug, today)
        update_hub(vault, "reviews", rev_slug, today)
        append_log(vault, f"Reviews ingested for {client} ({stats['count']} reviews, avg {stats['avg']:.2f}).", today)

        print(f"OK: {rev_path}")
        print(f"OK: {src_path}")
        return 0

def parse_reviews(path: Path) -> list[dict[str, object]]:
    """Accept JSON list or CSV; normalize to {rating, date, text, author_hash}."""
    suffix = path.suffix.lower()
    out: list[dict[str, object]] = []
    if suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8", errors="replace"))
        items = data if isinstance(data, list) else data.get("reviews") or data.get("items") or []
        for r in items:
            if not isinstance(r, dict):
                continue
            rating = pick(r, ["rating", "stars", "score"])
            date_val = pick(r, ["date", "createTime", "publishedAtDate"])
            text = pick(r, ["text", "comment", "review"])
            author = pick(r, ["author", "reviewer", "author_name", "displayName"])
            if rating is None:
                continue
            out.append({
                "rating": coerce_rating(rating),
                "date": normalize_date(date_val),
                "text": str(text or "").strip(),
                "author_hash": author_hash(str(author or "")),
            })
    elif suffix == ".csv":
        with path.open("r", encoding="utf-8", errors="replace", newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                lower = {(k or "").lower().strip(): (v or "").strip() for k, v in row.items()}
                rating = pick(lower, ["rating", "stars", "score"])
                if not rating:
                    continue
                out.append({
                    "rating": coerce_rating(rating),
                    "date": normalize_date(pick(lower, ["date", "created", "published"])),
                    "text": pick(lower, ["text", "comment", "review", "body"]) or "",
                    "author_hash": author_hash(pick(lower, ["author", "name", "reviewer"]) or ""),
                })
    return out


def aggregate(reviews: list[dict[str, object]]) -> dict[str, object]:
    ratings = [r["rating"] for r in reviews if isinstance(r["rating"], (int, float))]
    dates = sorted([r["date"] for r in reviews if r["date"]])
    distribution = Counter(round(r) for r in ratings if r is not None)
    return {
        "count": len(reviews),
        "avg": (sum(ratings) / len(ratings)) if ratings else 0.0,
        "min_date": dates[0] if dates else "",
        "max_date": dates[-1] if dates else "",
        "distribution": dict(sorted(distribution.items())),
        "sample_themes": top_themes([r["text"] for r in reviews if r["text"]]),
    }


def top_themes(texts: list[str], top_n: int = 5) -> list[str]:
    """Very rough keyword frequency — V0.1 only. Replace with sentiment/topic model in v0.2."""
    stopwords = set("the a an and or of to in for on with at by from is was were be been being i we you they he she my our your their this that these those very really".split())
    words: Counter[str] = Counter()
    for t in texts:
        for tok in re.findall(r"[A-Za-z]{4,}", t.lower()):
            if tok not in stopwords:
                words[tok] += 1
    return [w for w, _ in words.most_common(top_n)]


def coerce_rating(val: object) -> float | None:
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        # Sometimes "FIVE" / "FOUR" enum form
        words = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}
        return words.get(str(val).upper())


def normalize_date(val: object) -> str:
    if not val:
        return ""
    s = str(val)
    for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ", "%m/%d/%Y"):
        try:
            return datetime.strptime(s[:len(fmt)], fmt).date().isoformat()
        except ValueError:
            continue
    return s[:10] if len(s) >= 10 else s


def author_hash(name: str) -> str:
    """Hash author identity to preserve uniqueness without storing PII."""
    if not name:
        return ""
    return "anon-" + hashlib.sha256(name.encode("utf-8")).hexdigest()[:8]


def pick(d: dict, keys: list[str]) -> object:
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return None


def source_note(slug: str, raw_rel: str, digest: str, stats: dict, today: str, location: str) -> str:
    return f"""---
type: "source"
title: "Reviews Export ({today})"
created: "{today}"
updated: "{today}"
status: "imported"
tags: ["type/source", "domain/reviews", "provenance/raw"]
source_kind: "review-export"
source_path: "{raw_rel}"
source_hash: "sha256:{digest}"
location: "{location}"
---

# Reviews Export ({today})

## Source

- Path: `{raw_rel}`
- SHA-256: `{digest}`
- Retrieved: {today}

## Compiled Truth

- Reviews ingested: {stats["count"]}
- Average rating: {stats["avg"]:.2f}
- Date range: {stats["min_date"]} → {stats["max_date"]}

## Refusal

- Derived notes omit reviewer names and store no per-review identity.
- The immutable raw export may contain personal data supplied by the operator;
  keep the client vault access-controlled and follow the retention policy.
- No fake-review generation.
- No review gating recommendations.

## Related

- [[{location}]]
- [[wiki/reviews/_index|Reviews Hub]]
"""


def review_summary_note(slug: str, stats: dict, src_slug: str, location: str, today: str) -> str:
    dist_lines = "\n".join(
        f"| {stars}★ | {count} | {(count / stats['count'] * 100):.1f}% |"
        for stars, count in sorted(stats["distribution"].items(), reverse=True)
    ) or "| — | 0 | 0% |"
    themes = ", ".join(stats.get("sample_themes", [])) or "(none extracted)"
    return f"""---
type: "review-summary"
title: "Review Summary ({today})"
location: "{location}"
review_count: {stats["count"]}
avg_rating: {stats["avg"]:.2f}
created: "{today}"
updated: "{today}"
status: "observed"
tags: ["type/review-summary", "domain/reviews", "privacy/derived"]
---

# Review Summary ({today})

## Headline

**{stats["count"]}** reviews | **{stats["avg"]:.2f}**★ average | {stats["min_date"]} → {stats["max_date"]}

## Rating distribution

| Stars | Count | Share |
|---|---:|---:|
{dist_lines}

## Common themes (rough keyword frequency, v0.1)

{themes}

## Source

[[{src_slug}]]

## Refusal

- This derived note contains no reviewer names or per-review identity.
- The raw export can contain personal data and must remain access-controlled.
- No fake reviews. No review gating. No review extortion.

## Interpretation boundary

These are descriptive statistics from one authorized export. They do not
establish a ranking weight, universal benchmark, causal explanation, or reply
deadline. Any action proposal needs an explicit claim ID, source, and owner
approval.

## Related

- [[{location}]]
- [[wiki/reviews/_index|Reviews Hub]]
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

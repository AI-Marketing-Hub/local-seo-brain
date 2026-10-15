#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from runtime import touch_note_updated, vault_mutation, parse_as_of, require_vault, write_text


def main() -> int:
    parser = argparse.ArgumentParser(description="Synthesize starter Local SEO Brain deliverables from source notes.")
    parser.add_argument("--vault", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    vault = require_vault(args.vault)
    with vault_mutation(vault, dry_run=args.dry_run):
        today = parse_as_of(args.as_of)
        sources = sorted((vault / "wiki" / "sources").glob("*.md"))
        sources = [p for p in sources if p.name != "_index.md"]
        source_links = [f"[[{p.stem}]]" for p in sources]
        source_block = "\n".join(f"- {link}" for link in source_links) or "- None yet"
        outputs = {
        vault / "wiki" / "deliverables" / "Health Scorecard.md": f"""---
type: "deliverable"
title: "Health Scorecard"
created: "{today}"
updated: "{today}"
status: "draft"
tags: ["type/deliverable", "domain/local-seo", "evidence/no-data"]
---

# Health Scorecard

Current score: **Draft** until domain-specific scoring is implemented.

## Source Coverage

{source_block}

## Related

- [[wiki/deliverables/_index|Deliverables Hub]]
- [[Action Roadmap]]
- [[Approval Queue]]
""",
        vault / "wiki" / "deliverables" / "Action Roadmap.md": f"""---
type: "deliverable"
title: "Action Roadmap"
created: "{today}"
updated: "{today}"
status: "draft"
tags: ["type/deliverable", "domain/local-seo", "evidence/no-data"]
---

# Action Roadmap

## Week 1

- Review imported sources.
- Define domain-specific gates.
- Move any proposed action through [[Approval Queue]].

## Evidence Sources

{source_block}

## Related

- [[Health Scorecard]]
- [[Weekly Report]]
""",
        vault / "wiki" / "reports" / "Weekly Report.md": f"""---
type: "report"
title: "Weekly Report"
created: "{today}"
updated: "{today}"
status: "draft"
tags: ["type/report", "domain/local-seo", "evidence/no-data"]
---

# Weekly Report

## Summary

Local SEO Brain has {len(sources)} imported source notes.

## Sources

{source_block}

## Next Actions

- Review [[Health Scorecard]].
- Review [[Action Roadmap]].
- Update [[Approval Queue]].
"""
        }
        if args.dry_run:
            changed = sum(not path.exists() or path.read_text(encoding="utf-8") != text.rstrip() + "\n" for path, text in outputs.items())
            print(f"DRY-RUN: would update {changed} deliverables; source notes: {len(sources)}")
            return 0
        for path, text in outputs.items():
            write_text(path, text)
        append_log(vault, "Synthesized starter deliverables.", today)
        print("Synthesis complete")
        return 0


def append_log(vault: Path, message: str, today: str) -> None:
    log = vault / "wiki" / "log.md"
    text = log.read_text(encoding="utf-8") if log.exists() else "# Log\n"
    line = f"- {today} - {message}"
    if line not in text:
        write_text(log, text.rstrip() + f"\n{line}\n")
        touch_note_updated(log, today)

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, date
from zoneinfo import ZoneInfo
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the next action from a brain vault.")
    parser.add_argument("--vault", required=True)
    parser.add_argument("--as-of", default=datetime.now(ZoneInfo("UTC")).date().isoformat())
    args = parser.parse_args()
    try:
        reviewed_on = date.fromisoformat(args.as_of)
    except ValueError:
        raise SystemExit("ERROR: --as-of must be an ISO date")
    hot = Path(args.vault).expanduser().resolve() / "wiki" / "hot.md"
    if not hot.exists():
        raise SystemExit(f"ERROR: missing {hot}")
    text = hot.read_text(encoding="utf-8")
    vault = hot.parent.parent
    ledger = vault / "wiki/meta/ledgers/source-ledger.json"
    if not ledger.is_file():
        print("Next: needs_input, inspect source evidence before client recommendations")
        return 1
    try:
        sources = json.loads(ledger.read_text())["sources"]
        sources = list(sources.values()) if isinstance(sources, dict) else sources
        due = [s.get("canonical_id", s.get("id", "unknown")) for s in sources
               if s.get("review_status", s.get("review_state")) == "active"
               and date.fromisoformat(s["refresh_due"]) <= reviewed_on]
        due += [p.relative_to(vault).as_posix() for p in (vault / "wiki").rglob("*.md")
                if (m := re.search(r'^refresh_due:\s*[\"\']?(\d{4}-\d{2}-\d{2})', p.read_text(), re.M))
                and date.fromisoformat(m.group(1)) <= reviewed_on]
    except (ValueError, KeyError, TypeError):
        raise SystemExit("ERROR: invalid evidence metadata; review before client recommendations")
    if due:
        print("Next: refresh evidence before client recommendations: " + ", ".join(sorted(set(due))))
        return 1
    block = re.search(r"^## Next action\s*\n(.*?)(?=\n## |\Z)", text, re.I | re.M | re.S)
    if block:
        print("Next: " + block.group(1).strip())
    else:
        print("Next: read wiki/index.md and update wiki/hot.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

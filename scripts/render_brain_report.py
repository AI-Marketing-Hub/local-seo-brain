#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


def render_markdown(text: str) -> str:
    """Render the small Markdown subset used by the generated weekly report."""
    blocks: list[str] = []
    in_list = False
    for raw in text.splitlines():
        line = raw.rstrip()
        if line.startswith("- "):
            if not in_list:
                blocks.append("<ul>")
                in_list = True
            blocks.append(f"<li>{html.escape(line[2:])}</li>")
            continue
        if in_list:
            blocks.append("</ul>")
            in_list = False
        if not line:
            continue
        heading = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading:
            level = len(heading.group(1))
            blocks.append(f"<h{level}>{html.escape(heading.group(2))}</h{level}>")
        else:
            blocks.append(f"<p>{html.escape(line)}</p>")
    if in_list:
        blocks.append("</ul>")
    return "\n".join(blocks)


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Local SEO Brain weekly report to HTML.")
    parser.add_argument("--vault", required=True)
    parser.add_argument("--html-only", action="store_true", help="Compatibility flag; HTML is the only output format")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    vault = Path(args.vault).expanduser().resolve()
    report = vault / "wiki" / "reports" / "Weekly Report.md"
    if not report.exists():
        raise SystemExit(f"ERROR: missing report: {report}")
    text = report.read_text(encoding="utf-8")
    text = re.sub(r"^---.*?---\s*", "", text, flags=re.S)
    body = render_markdown(text)
    out = vault / f"{vault.name}-weekly-report.html"
    if args.dry_run:
        print(f"DRY-RUN: would render {out}")
        return 0
    out.write_text(f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Local SEO Brain Weekly Report</title>
<style>body{{font-family:Inter,Arial,sans-serif;max-width:860px;margin:40px auto;line-height:1.55;color:#172033}} h1{{color:#2f7f87}}</style>
</head><body>{body}</body></html>
""", encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

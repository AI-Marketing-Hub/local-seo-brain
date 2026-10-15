#!/usr/bin/env python3
"""
Lint a brain vault.

Checks:
  1. Frontmatter present in every wiki note.
  2. Wikilinks `[[Target]]` resolve to a note, attachment, or Canvas.
  3. Markdown anchor links `[Text](#fragment)` don't dangle — these are
     Google Docs export artifacts and must be wikilinks.
  4. Markdown relative links `[Text](slug.md)` resolve.
  5. Graph connectivity — every wiki note has at least one incoming and
     one outgoing wikilink.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


WIKILINK_RE = re.compile(r"!??\[\[([^\]]+)\]\]")
MD_LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True)
    args = parser.parse_args()
    vault = Path(args.vault).expanduser().resolve()
    if not vault.is_dir():
        print(f"ERROR: vault not found: {vault}", file=sys.stderr)
        return 1

    errors: list[str] = []
    notes = [p for p in (vault / "wiki").rglob("*.md") if ".raw" not in p.parts]
    stems = {p.stem.lower(): p for p in notes}
    rels = {p.relative_to(vault).with_suffix("").as_posix().lower(): p for p in notes}
    indeg = {p: 0 for p in notes}
    outdeg = {p: 0 for p in notes}

    for path in notes:
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"missing frontmatter: {path.relative_to(vault)}")

        # 1. Wikilinks
        for raw in WIKILINK_RE.findall(text):
            raw_target = raw.split("|", 1)[0].split("#", 1)[0].strip()
            target = raw_target.replace(".md", "").replace(".canvas", "").strip().lower()
            if not target:
                continue
            outdeg[path] += 1
            if target in stems:
                indeg[stems[target]] += 1
            elif target in rels:
                indeg[rels[target]] += 1
            elif not (vault / "_attachments" / raw_target).exists() and not any(vault.rglob(raw_target)):
                errors.append(f"dead wikilink in {path.relative_to(vault)}: {raw}")

        # 2. Markdown anchor / relative links — Google Docs export artifacts
        for link_text, url in MD_LINK_RE.findall(text):
            # Skip real URLs, mailto, data URIs, root-absolute paths
            if url.startswith(("http://", "https://", "mailto:", "data:", "/", "tel:")):
                continue
            # Skip URL fragments that look like real anchors to current doc (we don't have those in wiki notes)
            # Anything else is a dangling reference
            errors.append(
                f"non-wikilink markdown link in {path.relative_to(vault)}: [{link_text}]({url}) — should be [[wikilink]]"
            )

    wiki_notes = [p for p in notes if p.relative_to(vault).as_posix().startswith("wiki/")]
    zero_in = [p.relative_to(vault).as_posix() for p in wiki_notes if indeg[p] == 0]
    zero_out = [p.relative_to(vault).as_posix() for p in wiki_notes if outdeg[p] == 0]
    if zero_in:
        errors.append("zero incoming wiki notes: " + ", ".join(zero_in[:20]))
    if zero_out:
        errors.append("zero outgoing wiki notes: " + ", ".join(zero_out[:20]))

    if errors:
        for error in errors:
            print("ERROR:", error, file=sys.stderr)
        return 1
    print("Vault lint passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

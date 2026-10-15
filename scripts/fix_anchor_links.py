#!/usr/bin/env python3
"""
Convert Google-Docs-export anchor links like `[Text](#some-fragment)` into
proper Obsidian wikilinks `[[matched-slug|Text]]`.

Resolves fragments against the actual set of wiki note stems. If no match
is found, leaves the link alone and prints it.
"""
from __future__ import annotations

import re
import sys
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "assets" / "template-brain" / "wiki"


def normalize_fragment(fragment: str) -> str:
    """Turn a Google-Docs fragment into a candidate wiki slug."""
    f = fragment.lstrip("#").strip()
    # Strip robot emoji and other emojis
    f = re.sub(r"[\U0001F300-\U0001FAFF☀-➿]", "", f)
    # Strip leftover quotes
    f = f.strip("\"'")
    # Replace `:`, `+`, `?`, `!` etc. with nothing
    f = re.sub(r"[:?!,.()'\"]+", "", f)
    # Replace any non-alphanumeric with `-`
    f = re.sub(r"[^a-z0-9]+", "-", f.lower())
    # Collapse runs of `-`
    f = re.sub(r"-+", "-", f).strip("-")
    return f


def build_slug_index(wiki: Path) -> dict[str, Path]:
    """slug (lowercased file stem) -> file path."""
    out: dict[str, Path] = {}
    for p in wiki.rglob("*.md"):
        if p.name == "_index.md":
            continue
        out[p.stem.lower()] = p
    return out


def best_match(fragment: str, slug_index: dict[str, Path]) -> str | None:
    """Try exact then progressive fuzzy matches against the slug index."""
    cand = normalize_fragment(fragment)
    if cand in slug_index:
        return cand
    # Try without trailing/leading common prefixes
    variants = [
        cand,
        cand.replace("content-", "content-"),  # noop placeholder
    ]
    # Some Google Docs fragments include colons that turn into double dashes
    # e.g. "content:-blog-post-outline" -> already normalized
    # Try removing common stop suffixes
    for v in variants:
        if v in slug_index:
            return v
    # Substring match — pick the longest matching key that contains the cand
    matches = [k for k in slug_index if cand in k or k in cand]
    if matches:
        matches.sort(key=len, reverse=True)
        return matches[0]
    return None


MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((#[^)]+)\)")


def fix_file(path: Path, slug_index: dict[str, Path], *, dry_run: bool = False) -> tuple[int, list[str]]:
    text = path.read_text(encoding="utf-8")
    unresolved: list[str] = []
    fixes = 0

    def repl(m: re.Match) -> str:
        nonlocal fixes
        link_text, fragment = m.group(1), m.group(2)
        match = best_match(fragment, slug_index)
        if match is None:
            unresolved.append(f"{fragment} (text: {link_text!r})")
            return m.group(0)  # leave it
        fixes += 1
        return f"[[{match}|{link_text}]]"

    new = MD_LINK_RE.sub(repl, text)
    if new != text and not dry_run:
        path.write_text(new, encoding="utf-8")
    return fixes, unresolved


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    wiki = Path(args.vault).expanduser().resolve() / "wiki"
    if not wiki.is_dir():
        raise SystemExit(f"ERROR: vault has no wiki/: {wiki.parent}")
    slug_index = build_slug_index(wiki)
    total_fixed = 0
    total_unresolved: list[tuple[Path, str]] = []
    for md in sorted(wiki.rglob("*.md")):
        if md.name == "_index.md":
            continue
        fixes, unresolved = fix_file(md, slug_index, dry_run=args.dry_run)
        if fixes:
            print(f"  +{fixes:>3}  {md.relative_to(wiki).as_posix()}")
            total_fixed += fixes
        for u in unresolved:
            total_unresolved.append((md.relative_to(wiki), u))

    print()
    print(f"=== TOTAL FIXED: {total_fixed} links ===")
    if total_unresolved:
        print(f"\n=== UNRESOLVED ({len(total_unresolved)}) — manual review needed ===")
        for path, frag in total_unresolved:
            print(f"  {path}: {frag}")
    else:
        print("=== All anchor links resolved ===")
    return 0 if not total_unresolved else 1


if __name__ == "__main__":
    sys.exit(main())

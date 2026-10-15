#!/usr/bin/env python3
"""Render or verify an exact path manifest relative to a Git baseline."""
from __future__ import annotations

import argparse
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CATEGORY_ORDER = ("governance", "evidence", "archive", "generator", "wiki", "tests", "docs", "sample")


def category_for(path: str) -> str:
    """Map every refreshed path to the semantic groups in the handoff contract."""
    if path.startswith("examples/"):
        return "sample"
    if path.startswith("assets/archive/"):
        return "archive"
    if path.startswith("assets/template-brain/"):
        return "wiki"
    if path.startswith(("data/", "references/", "schemas/")):
        return "evidence"
    if path.startswith("tests/"):
        return "tests"
    if path.startswith(("scripts/", "patches/")) or path in {"install.sh", "uninstall.sh"}:
        return "generator"
    if path.startswith("docs/") or path.startswith("assets/svg/") or path in {
        "CHANGELOG.md",
        "PUBLISHING_NOTICE.md",
        "README.md",
        "OPEN-IN-OBSIDIAN.md",
        "RELEASE_CHECKLIST.md",
        "SKILL.md",
        "THIRD_PARTY_NOTICES.md",
        "marketplace.json",
    }:
        return "docs"
    if path.startswith((".claude-plugin/", ".github/", "agents/", "specs/")) or path in {
        "AGENTS.md",
        ".gitignore",
        "CLAUDE.md",
        "CONTRIBUTING.md",
        "GEMINI.md",
        "SECURITY.md",
        "SUPPORT.md",
        "pyproject.toml",
    }:
        return "governance"
    raise ValueError(f"unclassified changed path: {path}")


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout


def changes(base: str, output: Path) -> list[tuple[str, str]]:
    rows: dict[str, str] = {}
    for line in git("diff", "--name-status", base, "--").splitlines():
        fields = line.split("\t")
        status = fields[0]
        if status.startswith("R") or status.startswith("C"):
            rows[fields[1]] = f"{status}:old"
            rows[fields[2]] = f"{status}:new"
        else:
            rows[fields[1]] = status
    for path in git("ls-files", "--others", "--exclude-standard").splitlines():
        rows.setdefault(path, "A")
    try:
        output_rel = output.relative_to(ROOT).as_posix()
    except ValueError:
        pass
    else:
        rows.setdefault(output_rel, "A")
    return sorted((path, status) for path, status in rows.items())


def render(base: str, output: Path) -> str:
    grouped: dict[str, list[tuple[str, str]]] = defaultdict(list)
    rows = changes(base, output)
    for path, status in rows:
        grouped[category_for(path)].append((path, status))
    lines = [
        "# Verified change manifest",
        "",
        f"Baseline: `{base}`",
        "",
        f"Changed paths: **{len(rows)}**",
        "",
        "Status values follow `git diff --name-status`; untracked additions are `A`.",
        "Paths are grouped by the semantic categories required by the handoff contract.",
    ]
    for group in CATEGORY_ORDER:
        lines.extend(("", f"## {group.title()} ({len(grouped[group])})", ""))
        lines.extend(f"- `{status}` `{path}`" for path, status in grouped[group])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    output = Path(args.out).expanduser().resolve()
    expected = render(args.base, output)
    if args.check:
        if not output.exists() or output.read_text(encoding="utf-8") != expected:
            raise SystemExit(f"ERROR: change manifest drift: {output}")
        print(f"Change manifest passed: {output}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(expected, encoding="utf-8")
    print(f"Rendered {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

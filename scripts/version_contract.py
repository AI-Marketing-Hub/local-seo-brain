#!/usr/bin/env python3
"""Check version and Python-requirement projections against pyproject.toml."""
from __future__ import annotations

import json
import re
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
    version = project["version"]
    python = project["requires-python"]
    marketplace = json.loads((ROOT / "marketplace.json").read_text(encoding="utf-8"))
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    errors = []
    if marketplace.get("version") != version or plugin.get("version") != version:
        errors.append("version projection mismatch")
    if marketplace.get("compatible_with", {}).get("python") != python:
        errors.append("Python requirement mismatch")
    if f"Version: {version}" not in readme:
        errors.append("README version badge mismatch")
    if not re.search(rf"^## {re.escape(version)}\s", changelog, re.M):
        errors.append("CHANGELOG has no current version heading")
    if errors:
        raise SystemExit("ERROR: " + "; ".join(errors))
    print(f"Version contract passed: {version}, Python {python}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run the installed Brainstein anatomy audit against this repository.

This is a repository-local, read-only entry point. It intentionally preserves
Brainstein's result and exit status instead of translating the local evidence
schema or manufacturing a release-ready score.
"""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--no-strict-vault", action="store_true")
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Return zero after a completed audit while preserving its findings.",
    )
    args = parser.parse_args()

    command = ["brainstein", "audit-brain", str(ROOT)]
    if args.json:
        command.append("--json")
    if args.strict:
        command.append("--strict")
    if args.no_strict_vault:
        command.append("--no-strict-vault")
    result = subprocess.run(command, cwd=ROOT, check=False)
    return 0 if args.report_only else result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

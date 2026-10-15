#!/usr/bin/env python3
"""Move one explicit client vault to an explicit recovery directory."""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--trash-dir", required=True)
    parser.add_argument("--confirm", required=True, choices=("MOVE_TO_TRASH",))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    vault = Path(args.vault).expanduser().resolve()
    trash = Path(args.trash_dir).expanduser().resolve()
    if not vault.is_dir() or not (vault / "wiki").is_dir():
        raise SystemExit(f"ERROR: target is not a Local SEO Brain vault: {vault}")
    if vault in {Path("/").resolve(), Path.home().resolve(), ROOT.resolve()} or vault.is_relative_to(ROOT):
        raise SystemExit(f"ERROR: refusing protected target: {vault}")
    if trash.is_relative_to(vault) or trash.is_relative_to(ROOT):
        raise SystemExit("ERROR: recovery directory must be outside the vault and repository")
    destination = trash / vault.name
    if destination.exists() or destination.is_symlink():
        raise SystemExit(f"ERROR: recovery destination exists: {destination}")
    if args.dry_run:
        print(f"DRY-RUN: would move {vault} to {destination}")
        return 0
    trash.mkdir(parents=True, exist_ok=True)
    shutil.move(str(vault), str(destination))
    print(f"Moved to recoverable location: {destination}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

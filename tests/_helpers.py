from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
AS_OF = json.loads((ROOT / "references/source-ledger.json").read_text())["as_of"]


def run(*args: str, check: bool = True, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [sys.executable, *args],
        cwd=cwd,
        check=False,
        text=True,
        capture_output=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if check and result.returncode:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def scaffold(parent: Path, name: str = "test-client") -> Path:
    run(
        "scripts/scaffold_vault.py",
        "--client", name,
        "--owner", "Fixture Owner",
        "--out-dir", str(parent),
        "--as-of", AS_OF,
    )
    return parent / name


def tree_hash(root: Path, *, exclude_names: set[str] | None = None) -> str:
    excluded = exclude_names or set()
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file() and not item.is_symlink()):
        if path.name in excluded:
            continue
        rel = path.relative_to(root).as_posix()
        digest.update(rel.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def file_snapshot(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(item for item in root.rglob("*") if item.is_file() and not item.is_symlink())
    }

from __future__ import annotations

import tempfile
from pathlib import Path

from _helpers import AS_OF, run, tree_hash, file_snapshot


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="lsb-demo-a-") as a, tempfile.TemporaryDirectory(prefix="lsb-demo-b-") as b:
        first = Path(a) / "sample-vault"
        second = Path(b) / "sample-vault"
        for target in (first, second):
            run("scripts/build_demo_vault.py", "--out", str(target), "--as-of", AS_OF)
        assert tree_hash(first) == tree_hash(second)
        raw_before = file_snapshot(first / ".raw")
        manifest_before = (first / ".raw/.manifest.json").read_bytes()
        run("scripts/build_demo_vault.py", "--out", str(first), "--as-of", AS_OF, "--replace")
        assert file_snapshot(first / ".raw") == raw_before
        assert (first / ".raw/.manifest.json").read_bytes() == manifest_before
        assert tree_hash(first) == tree_hash(second)
        checked = Path("examples/sample-vault")
        if checked.is_dir() and Path("examples/sample-vault.sha256").is_file():
            expected = Path("examples/sample-vault.sha256").read_text(encoding="utf-8").split()[0]
            assert tree_hash(checked, exclude_names={"sample-vault.sha256"}) == expected
            assert tree_hash(first) == expected
    print("test_demo_determinism.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

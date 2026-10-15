from __future__ import annotations
import json
import sys
import tempfile
import subprocess
import copy
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path
from _helpers import AS_OF, ROOT, run
sys.path.insert(0, str(ROOT / "scripts"))
import package_release as package
import verification_receipt as receipt


def main():
    with tempfile.TemporaryDirectory(prefix="lsb-receipt-") as value:
        tmp = Path(value); audit = tmp / "audit.json"
        for data in ["{", "[]", json.dumps({"brain_anatomy": {"total_score":100, "grade":"SSS+", "maturity":"market-ready"}, "market_ready":True, "critical_failures":[]})]:
            audit.write_text(data)
            result = run("scripts/package_release.py", "--out", str(tmp / "out"), "--base", "HEAD", "--as-of", AS_OF, "--version", "0.3.0", "--release-type", "private-paid", "--market-ready-audit", str(audit), "--obsidian-cli", "/bin/false", "--brainstein-root", str(tmp), "--dry-run", check=False)
            assert result.returncode and "ERROR:" in result.stderr and "Traceback" not in result.stderr
            assert not (tmp / "out").exists()
        for wrong in [{}, {"schema": receipt.SCHEMA, "evaluation_date":"2099-12-31"}]:
            try:
                receipt.validate_receipt(wrong, as_of=AS_OF, require_clean=False)
            except ValueError:
                pass
            else:
                raise AssertionError("forged or future receipt accepted")
        # A content manifest changes when bytes change; receipt cannot be reused.
        rows = [{"path":"one", "sha256":"a", "bytes":1}]
        assert receipt.tree_hash(rows) != receipt.tree_hash([{"path":"one", "sha256":"b", "bytes":1}])
        # A clean candidate must agree on lexical package order and still check
        # whitespace introduced in committed changes after the review baseline.
        subprocess.run(["git", "init", "-q", str(tmp / "repo")], check=True)
        repo = tmp / "repo"
        def git(*args):
            return subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", *args], cwd=repo, check=True, capture_output=True, text=True)
        for name in ["examples/sample-vault.sha256", "examples/sample-vault/.obsidian/graph.json"]:
            path = repo / name; path.parent.mkdir(parents=True, exist_ok=True); path.write_text("clean\n")
        git("add", "."); git("commit", "-qm", "baseline")
        baseline = git("rev-parse", "HEAD").stdout.strip()
        old_package, old_receipt = package.ROOT, receipt.ROOT
        try:
            package.ROOT = receipt.ROOT = repo
            staged = [{"path": p.relative_to(repo).as_posix(), "sha256": receipt.hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size} for p in package.tracked_files()]
            assert staged == receipt.manifest()
            (repo / "examples/sample-vault.sha256").write_text("committed trailing space \n")
            git("add", "."); git("commit", "-qm", "candidate")
            assert not git("status", "--porcelain").stdout
            assert subprocess.run(receipt.check_diff(baseline), cwd=repo, capture_output=True).returncode != 0
            (repo / "examples/sample-vault.sha256").write_text("clean candidate\n")
            (repo / "references").mkdir()
            reviewed = datetime.now(ZoneInfo("UTC")).date().isoformat()
            (repo / "references/source-ledger.json").write_text(json.dumps({"as_of": reviewed}))
            (repo / "pyproject.toml").write_text('[project]\nversion="0.3.0"\n')
            git("add", "."); git("commit", "-qm", "reviewed candidate")
            gates = {name: {"exit_code": 0, "output_sha256": "a" * 64} for name in {"historical", "version", "evidence", "projection", "freshness", "coverage", "vault", "obsidian", "sample_vault", "sample_obsidian", "brainstein", "brainstein_release", "next", "safety", "diff", "content"} | {f"test_{t}" for t in receipt.TESTS}}
            valid = {"schema": receipt.SCHEMA, "evaluation_date": reviewed, "evidence_date": reviewed, "version": "0.3.0", "git_head": git("rev-parse", "HEAD").stdout.strip(), "baseline_sha": baseline, "tree_unchanged": True, "files": receipt.manifest(), "dirty": False, "gates": gates, "tools": {name: {"identity": name, "version": "test-fixture", "sha256": "b" * 64} for name in ("python", "obsidian", "brainstein")}, "brainstein_audit": {"brain_anatomy": {"total_score": 100, "grade": "SSS+", "maturity": "market-ready"}, "market_ready": True, "critical_failures": []}}
            valid["tree_sha256"] = receipt.tree_hash(valid["files"])
            receipt.validate_receipt(valid, as_of=reviewed)
            mutations = [
                {"version": "9.9.9"}, {"evaluation_date": "2099-12-31"},
                {"evaluation_date": (datetime.fromisoformat(reviewed).date() - timedelta(days=1)).isoformat()},
                {"evidence_date": "2099-12-31"}, {"gates": {}}, {"tools": {}},
                {"gates": {**gates, "diff": {"exit_code": 1, "output_sha256": "c" * 64}}},
            ]
            for change in mutations:
                bad = copy.deepcopy(valid); bad.update(change)
                try:
                    receipt.validate_receipt(bad, as_of=reviewed)
                except ValueError:
                    pass
                else:
                    raise AssertionError(f"invalid receipt accepted: {list(change)}")
            (repo / "examples/sample-vault.sha256").write_text("changed after review\n")
            try:
                receipt.validate_receipt(valid, as_of=reviewed)
            except ValueError:
                pass
            else:
                raise AssertionError("changed package input accepted")
        finally:
            package.ROOT, receipt.ROOT = old_package, old_receipt
    print("test_release_receipt.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

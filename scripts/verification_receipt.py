#!/usr/bin/env python3
"""Run required gates and bind their results to the reviewed repository bytes."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
SCHEMA = "local-seo-brain.verification-receipt.v1"
TESTS = ["pipeline", "domain_ingestors", "reseed_preserves_overlays", "citation_contract",
         "demo_determinism", "cli_safety", "privacy_and_refusals", "version_consistency",
         "documentation_claims", "scaffold", "freshness", "raw_integrity", "release_receipt", "safety_scan"]


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip()


def manifest() -> list[dict]:
    names = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.split("\0")
    result = []
    for name in sorted(set(n for n in names if n)):
        p = ROOT / name
        if p.is_symlink():
            raise ValueError(f"unsafe or missing package input: {name}")
        if not p.exists():
            continue  # A reviewed local deletion is absent from package inputs.
        if not p.is_file():
            raise ValueError(f"unsafe package input: {name}")
        result.append({"path": name, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "bytes": p.stat().st_size})
    return result


def tree_hash(rows: list[dict]) -> str:
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def check_diff(baseline: str) -> list[str]:
    # Include committed, staged and working changes in the reviewed candidate.
    return ["git", "diff", "--check", baseline]


def version() -> str:
    import tomllib
    return tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]


def checker_identity(root: Path, package: str, launcher: Path) -> dict:
    folder = root / package
    if not folder.is_dir() or folder.is_symlink():
        raise ValueError(f"missing checker source package: {package}")
    rows = []
    for path in sorted(folder.rglob("*")):
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ValueError("checker source contains a symlink")
        if path.is_file():
            rows.append({"path": path.relative_to(root).as_posix(), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    rows.append({"path": "launcher", "sha256": hashlib.sha256(launcher.read_bytes()).hexdigest()})
    if package == "brainstein":
        import tomllib
        metadata = root / "pyproject.toml"
        checker_version = tomllib.loads(metadata.read_text())["project"]["version"]
    else:
        metadata = root / ".claude-plugin/plugin.json"
        checker_version = json.loads(metadata.read_text())["version"]
    rows.append({"path": metadata.relative_to(root).as_posix(), "sha256": hashlib.sha256(metadata.read_bytes()).hexdigest()})
    return {"identity": package, "version": checker_version, "sha256": tree_hash(rows), "files": len(rows)}


def validate_receipt(data: dict, *, as_of: str, require_clean: bool = True) -> None:
    today = datetime.now(ZoneInfo("UTC")).date().isoformat()
    if not isinstance(data, dict):
        raise ValueError("receipt must be an object")
    if data.get("schema") != SCHEMA or data.get("evaluation_date") != as_of or as_of != today:
        raise ValueError("receipt must use today's evaluation date")
    snapshot = json.loads((ROOT / "references/source-ledger.json").read_text())["as_of"]
    if data.get("evidence_date") != snapshot or date.fromisoformat(snapshot) > date.fromisoformat(as_of):
        raise ValueError("receipt evidence date mismatch")
    if data.get("version") != version() or data.get("git_head") != git("rev-parse", "HEAD"):
        raise ValueError("receipt version or Git identity mismatch")
    if not isinstance(data.get("baseline_sha"), str) or data["baseline_sha"] != git("rev-parse", "--verify", f"{data['baseline_sha']}^{{commit}}"):
        raise ValueError("receipt lacks concrete baseline")
    rows = manifest()
    if data.get("tree_unchanged") is not True:
        raise ValueError("tree changed during verification")
    if data.get("files") != rows or data.get("tree_sha256") != tree_hash(rows):
        raise ValueError("reviewed tree changed after verification")
    if require_clean and (git("status", "--porcelain") or data.get("dirty") is not False or data["baseline_sha"] == git("rev-parse", "HEAD")):
        raise ValueError("packaging requires a clean reviewed tree")
    expected = {"historical", "version", "evidence", "projection", "freshness", "coverage", "vault", "obsidian", "sample_vault", "sample_obsidian", "brainstein", "brainstein_release", "next", "safety", "diff", "content"} | {f"test_{t}" for t in TESTS}
    gates = data.get("gates", {})
    if set(gates) != expected or any(g.get("exit_code") != 0 or not g.get("output_sha256") for g in gates.values()):
        raise ValueError("receipt has missing or failing gates")
    tools = data.get("tools", {})
    if set(tools) != {"python", "obsidian", "brainstein"} or any(not t.get("identity") or not t.get("version") or not t.get("sha256") for t in tools.values()):
        raise ValueError("receipt lacks checker identities")
    audit = data.get("brainstein_audit", {})
    anatomy = audit.get("brain_anatomy", {})
    if anatomy.get("total_score", 0) < 90 or anatomy.get("grade") != "SSS+" or anatomy.get("maturity") != "market-ready" or audit.get("market_ready") is not True or audit.get("critical_failures"):
        raise ValueError("Brainstein release gate did not pass")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--obsidian-cli", required=True)
    parser.add_argument("--brainstein-root", required=True)
    args = parser.parse_args()
    out = Path(args.out).resolve()
    if out.is_relative_to(ROOT):
        raise SystemExit("ERROR: receipt output must be outside the reviewed tree")
    snapshot = json.loads((ROOT / "references/source-ledger.json").read_text())["as_of"]
    try:
        evaluated = date.fromisoformat(args.as_of)
        if evaluated != datetime.now(ZoneInfo("UTC")).date() or date.fromisoformat(snapshot) > evaluated:
            raise ValueError("receipt requires today's evaluation date after the evidence snapshot")
    except ValueError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    args.obsidian_cli = str(Path(args.obsidian_cli).resolve())
    brainstein_root = Path(args.brainstein_root).resolve()
    origin = subprocess.run(
        [sys.executable, "-P", "-c", "import brainstein; print(brainstein.__file__)"],
        cwd=ROOT, check=True, capture_output=True, text=True,
        env={**os.environ, "PYTHONPATH": str(brainstein_root), "PYTHONDONTWRITEBYTECODE": "1"},
    ).stdout.strip()
    if Path(origin).resolve() != brainstein_root / "brainstein/__init__.py":
        raise SystemExit("ERROR: imported Brainstein differs from selected checker source")
    checkers = {
        "python": {"identity": Path(sys.executable).name, "version": sys.version.split()[0], "sha256": hashlib.sha256(Path(sys.executable).resolve().read_bytes()).hexdigest()},
        "obsidian": checker_identity(Path(args.obsidian_cli).parent.parent, "claude_obsidian", Path(args.obsidian_cli)),
        "brainstein": checker_identity(brainstein_root, "brainstein", brainstein_root / "brainstein/__main__.py"),
    }
    baseline = git("rev-parse", "--verify", f"{args.base}^{{commit}}")
    if baseline == git("rev-parse", "HEAD") and not git("status", "--porcelain"):
        raise SystemExit("ERROR: baseline must precede the release candidate commit")
    if subprocess.run(["git", "merge-base", "--is-ancestor", baseline, "HEAD"], cwd=ROOT).returncode:
        raise SystemExit("ERROR: baseline must be an ancestor of the release candidate")
    py = sys.executable
    scratch = tempfile.TemporaryDirectory(prefix="lsb-checker-output-")
    audit_file = Path(scratch.name) / "brainstein.json"
    commands = {
        "historical": [py, "scripts/historical_seed_contract.py"],
        "version": [py, "scripts/version_contract.py"],
        "evidence": [py, "scripts/evidence_contract.py", "validate", "--as-of", snapshot],
        "projection": [py, "scripts/evidence_contract.py", "check", "--as-of", snapshot, "--vault", "assets/template-brain"],
        "freshness": [py, "scripts/evidence_contract.py", "freshness", "--as-of", args.as_of, "--format", "json"],
        "coverage": [py, "scripts/coverage_matrix.py", "check"],
        "content": [py, "scripts/working_content_contract.py"],
        "vault": [py, "scripts/lint_vault.py", "--vault", "assets/template-brain"],
        "obsidian": [py, args.obsidian_cli, "lint", "--vault", "assets/template-brain", "--as-of", args.as_of, "--format", "json", "--strict"],
        "sample_vault": [py, "scripts/lint_vault.py", "--vault", "examples/sample-vault"],
        "sample_obsidian": [py, args.obsidian_cli, "lint", "--vault", "examples/sample-vault", "--as-of", args.as_of, "--format", "json", "--strict"],
        "brainstein": [py, "-P", "-m", "brainstein", "audit-brain", str(ROOT), "--json"],
        "brainstein_release": [py, "scripts/brainstein_gate.py", str(audit_file)],
        "next": [py, "-P", "-m", "brainstein", "next", str(ROOT), "--json", "--limit", "10"],
        **{f"test_{t}": [py, f"tests/test_{t}.py"] for t in TESTS},
        "safety": [py, "scripts/repository_safety_scan.py", "--base", baseline],
        "diff": check_diff(baseline),
    }
    before = manifest()
    data = {"schema": SCHEMA, "baseline_sha": baseline, "version": version(), "evidence_date": snapshot, "evaluation_date": args.as_of,
            "git_head": git("rev-parse", "HEAD"), "dirty": bool(git("status", "--porcelain")),
            "files": before, "tree_sha256": tree_hash(before), "gates": {}, "tools": checkers}
    for name, command in commands.items():
        result = subprocess.run(command, cwd=ROOT, capture_output=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPATH": str(brainstein_root), "CLAUDE_OBSIDIAN_REVIEW_TIMEZONE": "UTC", "TZ": "UTC"})
        output = result.stdout + result.stderr
        data["gates"][name] = {"exit_code": result.returncode, "output_sha256": hashlib.sha256(output).hexdigest()}
        if name == "brainstein":
            try:
                data["brainstein_audit"] = json.loads(result.stdout)
            except ValueError:
                data["brainstein_audit"] = {}
            audit_file.write_text(json.dumps(data["brainstein_audit"]))
        print(f"{name}: exit {result.returncode}", flush=True)
    scratch.cleanup()
    data["tree_unchanged"] = manifest() == before
    if checkers["obsidian"] != checker_identity(Path(args.obsidian_cli).parent.parent, "claude_obsidian", Path(args.obsidian_cli)) or checkers["brainstein"] != checker_identity(brainstein_root, "brainstein", brainstein_root / "brainstein/__main__.py"):
        data["tree_unchanged"] = False
    try:
        validate_receipt(data, as_of=args.as_of)
        data["release_ready"] = True
    except (ValueError, KeyError, TypeError) as exc:
        data["release_ready"] = False
        data["readiness_error"] = str(exc)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    return 0 if data["release_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

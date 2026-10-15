#!/usr/bin/env python3
"""Build a deterministic private review archive after a verified market-ready audit.

The market-ready evidence is the tree-bound verification receipt from
scripts/verification_receipt.py, which embeds the pinned Brainstein audit; this
repository does not ship a separate audit_brain.py report.

The archive contains SHA256SUMS and RELEASE_MANIFEST.json. It never publishes,
tags, pushes, or builds a sanitized-public release surface. The receipt is bound to the reviewed tree. Packaging independently reruns
verification with the explicitly selected checkers before accepting it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import tempfile
import zipfile
from datetime import date, datetime
from pathlib import Path

from runtime import parse_as_of, protect_repo_target
from verification_receipt import validate_receipt, version, tree_hash
from repository_safety_scan import archive_name


ROOT = Path(__file__).resolve().parent.parent


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"], cwd=ROOT, check=True, capture_output=True
    )
    paths = [ROOT / value.decode("utf-8") for value in result.stdout.split(b"\0") if value]
    return sorted(
        (path for path in paths if path.is_file() and not path.is_symlink()),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def verify_audit(path: Path, as_of: str) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        validate_receipt(data, as_of=as_of)
    except (ValueError, KeyError, TypeError, AttributeError, OSError) as exc:
        raise SystemExit(f"ERROR: invalid verification receipt: {exc}") from exc
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--obsidian-cli", required=True)
    parser.add_argument("--brainstein-root", required=True)
    parser.add_argument("--base", required=True)
    parser.add_argument("--out", required=True, help="Explicit output directory outside the repository")
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--version", required=True)
    parser.add_argument("--release-type", required=True, choices=("private-paid", "sanitized-public"))
    parser.add_argument("--verification-receipt", "--market-ready-audit", dest="verification_receipt", required=True, help="Tree-bound verification receipt; old audit flag is a deprecated alias")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    as_of = parse_as_of(args.as_of)
    if args.release_type != "private-paid":
        raise SystemExit("ERROR: sanitized-public packaging is not implemented; use a separately reviewed sanitizer")
    audit_path = Path(args.verification_receipt).expanduser().resolve()
    audit = verify_audit(audit_path, as_of)
    if args.version != version():
        raise SystemExit("ERROR: --version differs from canonical version")
    out = Path(args.out).expanduser().resolve()
    protect_repo_target(out, allow_repo_target=False)
    archive = out / f"local-seo-brain-{args.version}-{args.release_type}.zip"
    if archive.exists():
        raise SystemExit(f"ERROR: archive exists: {archive}")
    if audit["baseline_sha"] != subprocess.run(["git", "rev-parse", "--verify", f"{args.base}^{{commit}}"], cwd=ROOT, check=True, capture_output=True, text=True).stdout.strip():
        raise SystemExit("ERROR: baseline differs from verification receipt")
    files = tracked_files()
    try:
        names = [archive_name(p.relative_to(ROOT).as_posix()) for p in files]
    except ValueError as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    if len(names) != len(set(names)):
        raise SystemExit("ERROR: ambiguous archive member names")
    if set(names) & {"sha256sums", "release_manifest.json"}:
        raise SystemExit("ERROR: reserved release manifest input")
    with tempfile.TemporaryDirectory(prefix="lsb-reverify-") as verification_dir:
        verified = Path(verification_dir) / "receipt.json"
        result = subprocess.run([__import__("sys").executable, str(ROOT / "scripts/verification_receipt.py"), "--out", str(verified), "--base", args.base, "--as-of", as_of, "--obsidian-cli", args.obsidian_cli, "--brainstein-root", args.brainstein_root], cwd=ROOT)
        if result.returncode:
            raise SystemExit("ERROR: independent release verification failed")
        audit = verify_audit(verified, as_of)
    validate_receipt(audit, as_of=as_of)
    if args.dry_run:
        print(json.dumps({"archive": str(archive), "files": len(files), "as_of": as_of}, sort_keys=True))
        return 0

    payloads = {path: path.read_bytes() for path in files}
    staged_rows = [{"path": path.relative_to(ROOT).as_posix(), "sha256": hashlib.sha256(payloads[path]).hexdigest(), "bytes": len(payloads[path])} for path in files]
    if staged_rows != audit["files"] or tree_hash(staged_rows) != audit["tree_sha256"]:
        raise SystemExit("ERROR: staged bytes differ from independently verified inputs")
    validate_receipt(audit, as_of=as_of)
    manifest_rows = []
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        digest = hashlib.sha256(payloads[path]).hexdigest()
        manifest_rows.append((rel, digest, len(payloads[path])))
    manifest = {
        "schema": "local-seo-brain.release-manifest.v1",
        "release-type": args.release_type,
        "version": args.version,
        "as_of": as_of,
        "market-ready": True,
        "brainstein_score": audit["brainstein_audit"]["brain_anatomy"]["total_score"],
        "files": [{"path": rel, "sha256": digest, "bytes": size} for rel, digest, size in manifest_rows],
    }
    sums = "".join(f"{digest}  {rel}\n" for rel, digest, _ in manifest_rows)
    timestamp = datetime.combine(date.fromisoformat(as_of), datetime.min.time()).timetuple()[:6]
    out.mkdir(parents=True, exist_ok=True)
    try:
        with tempfile.TemporaryDirectory(prefix=".local-seo-package-", dir=out) as build:
            staged_archive = Path(build) / "candidate.zip"
            with zipfile.ZipFile(staged_archive, "x", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as handle:
                for path in files:
                    rel = path.relative_to(ROOT).as_posix()
                    info = zipfile.ZipInfo(rel, date_time=timestamp)
                    info.external_attr = (stat.S_IFREG | 0o644) << 16
                    handle.writestr(info, payloads[path])
                for rel, content in (
                    ("SHA256SUMS", sums.encode("utf-8")),
                    ("RELEASE_MANIFEST.json", (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")),
                ):
                    info = zipfile.ZipInfo(rel, date_time=timestamp)
                    info.external_attr = (stat.S_IFREG | 0o644) << 16
                    handle.writestr(info, content)
            with zipfile.ZipFile(staged_archive) as handle:
                expected = {r[0]: r[1] for r in manifest_rows}
                if handle.testzip() or len(handle.namelist()) != len(set(handle.namelist())) or set(handle.namelist()) != set(expected) | {"SHA256SUMS", "RELEASE_MANIFEST.json"}:
                    raise ValueError("archive member mismatch")
                if any(hashlib.sha256(handle.read(name)).hexdigest() != digest for name, digest in expected.items()):
                    raise ValueError("archive bytes differ from verification")
            validate_receipt(audit, as_of=as_of)
            os.link(staged_archive, archive)
    except (ValueError, OSError, zipfile.BadZipFile) as exc:
        raise SystemExit(f"ERROR: archive verification failed: {exc}") from exc
    print(archive)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

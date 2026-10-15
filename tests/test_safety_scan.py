from __future__ import annotations
import io
import stat
import sys
import zipfile
import zlib
import json
import subprocess
import tempfile
from pathlib import Path
from _helpers import ROOT
sys.path.insert(0, str(ROOT / "scripts"))
import repository_safety_scan as scanner
from repository_safety_scan import inspect_payload, SECRET_PATTERNS, contains_review_identity


def main():
    for name, mode in [("../outside", 0), ("..\\outside", 0), ("C:\\outside", 0), ("link", stat.S_IFLNK | 0o777)]:
        stream = io.BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            info = zipfile.ZipInfo(name); info.external_attr = mode << 16
            archive.writestr(info, "target")
        assert inspect_payload(stream.getvalue(), "fixture")[1]
    secret = ("sk-" + "A" * 32).encode()
    chunk = b"Comment\0\1\0\0\0" + zlib.compress(secret)
    png = b"\x89PNG\r\n\x1a\n" + len(chunk).to_bytes(4, "big") + b"iTXt" + chunk + b"\0" * 4
    payloads, errors = inspect_payload(png, "fixture")
    assert not errors and any(SECRET_PATTERNS["openai-legacy-key"].search(p) for p in payloads)
    assert contains_review_identity(json.dumps([{"rating": 5, "author": "Synthetic Person"}]).encode())
    assert not contains_review_identity(b'[{"rating":5,"text":"Synthetic review"}]')
    # Deleted and added opaque binaries must remain visible in the churn scan.
    with tempfile.TemporaryDirectory(prefix="lsb-scan-") as value:
        repo = Path(value)
        def git(*args):
            return subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", *args], cwd=repo, check=True, capture_output=True, text=True)
        git("init", "-q")
        (repo / "old.dat").write_bytes(b"\xfforiginal")
        git("add", "."); git("commit", "-qm", "baseline")
        (repo / "old.dat").unlink(); (repo / "new.dat").write_bytes(b"\xffadded")
        legacy_jpg = "examples/sample-vault/_attachments/images/diagrams/unreviewed.jpg"
        (repo / legacy_jpg).parent.mkdir(parents=True)
        (repo / legacy_jpg).write_bytes(b"\xffunreviewed illustration")
        old_root, old_argv = scanner.ROOT, sys.argv
        try:
            import contextlib
            scanner.ROOT = repo; sys.argv = ["scan", "--base", "HEAD"]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                assert scanner.main() == 1
            result = json.loads(output.getvalue())
            assert result["modified_binary"] == ["old.dat"]
            assert result["unexpected_added_binary"] == [legacy_jpg, "new.dat"]
            assert not result["inspection_errors"]
        finally:
            scanner.ROOT, sys.argv = old_root, old_argv
    # A reviewed relocation preserves exact bytes and grants no permanent
    # exemption when a later baseline already contains (or removes) the move.
    with tempfile.TemporaryDirectory(prefix="lsb-asset-move-") as value:
        repo = Path(value)
        def git(*args):
            return subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", *args], cwd=repo, check=True, capture_output=True, text=True)
        git("init", "-q")
        old = "assets/template-brain/_attachments/images/image1.png"
        new = "assets/template-brain/.raw/source-material/archived-attachments/images/image1.png"
        payload = b"\xffsynthetic asset"
        (repo / old).parent.mkdir(parents=True); (repo / old).write_bytes(payload)
        git("add", "."); git("commit", "-qm", "baseline")
        (repo / new).parent.mkdir(parents=True); (repo / old).rename(repo / new)
        (repo / "references").mkdir()
        manifest = {"schema":"local-seo-brain.asset-retention.v1", "moves":[{"from":old,"to":new,"action":"move","sha256":scanner.hashlib.sha256(payload).hexdigest(),"bytes":len(payload)}]}
        (repo / "references/asset-retention.json").write_text(json.dumps(manifest))
        old_root, old_argv = scanner.ROOT, sys.argv
        try:
            scanner.ROOT = repo
            assert scanner.reviewed_asset_moves("HEAD") == {old:"D",new:"A"}
            (repo / new).write_bytes(b"\xfftampered")
            try:
                scanner.reviewed_asset_moves("HEAD")
            except ValueError:
                pass
            else:
                raise AssertionError("tampered retained asset accepted")
            (repo / new).write_bytes(payload)
            git("add", "."); git("commit", "-qm", "retained move")
            assert scanner.reviewed_asset_moves("HEAD") == {}
            git("rm", new); git("commit", "-qm", "remove retained destination")
            (repo / new).parent.mkdir(parents=True, exist_ok=True); (repo / new).write_bytes(payload)
            sys.argv = ["scan", "--base", "HEAD"]
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                assert scanner.main() == 1
            assert json.loads(output.getvalue())["unexpected_added_binary"] == [new]
        finally:
            scanner.ROOT, sys.argv = old_root, old_argv
    # A reviewed withdrawal of the operator-supplied bundle is hash-bound and
    # grants nothing once the baseline no longer contains the file.
    with tempfile.TemporaryDirectory(prefix="lsb-asset-withdraw-") as value:
        repo = Path(value)
        def git(*args):
            return subprocess.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid", *args], cwd=repo, check=True, capture_output=True, text=True)
        git("init", "-q")
        gone = "assets/template-brain/.raw/source-material/LOCAL-seo-Knowledge-Base.zip"
        payload = b"\xffsynthetic bundle"
        (repo / gone).parent.mkdir(parents=True); (repo / gone).write_bytes(payload)
        git("add", "."); git("commit", "-qm", "baseline")
        (repo / gone).unlink()
        (repo / "references").mkdir()
        manifest = {"schema":"local-seo-brain.asset-retention.v1", "moves":[], "withdrawals":[{"path":gone,"action":"withdraw","sha256":scanner.hashlib.sha256(payload).hexdigest(),"bytes":len(payload)}]}
        (repo / "references/asset-retention.json").write_text(json.dumps(manifest))
        old_root, old_argv = scanner.ROOT, sys.argv
        try:
            scanner.ROOT = repo; sys.argv = ["scan", "--base", "HEAD"]
            assert scanner.reviewed_asset_withdrawals("HEAD") == {gone}
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                assert scanner.main() == 0
            result = json.loads(output.getvalue())
            assert result["reviewed_asset_withdrawal_paths"] == [gone] and not result["modified_binary"]
            manifest["withdrawals"][0]["bytes"] += 1
            (repo / "references/asset-retention.json").write_text(json.dumps(manifest))
            try:
                scanner.reviewed_asset_withdrawals("HEAD")
            except ValueError:
                pass
            else:
                raise AssertionError("mismatched withdrawal accepted")
            manifest["withdrawals"][0]["bytes"] -= 1
            (repo / "references/asset-retention.json").write_text(json.dumps(manifest))
            git("add", "."); git("commit", "-qm", "withdrawn")
            assert scanner.reviewed_asset_withdrawals("HEAD") == set()
        finally:
            scanner.ROOT, sys.argv = old_root, old_argv
    print("test_safety_scan.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

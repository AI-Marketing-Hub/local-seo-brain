#!/usr/bin/env python3
"""Fail on credential signatures, private paths, cache files, or binary churn."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import hashlib
import io
import zipfile
import zlib
import stat
from pathlib import PurePosixPath, PureWindowsPath
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SECRET_PATTERNS = {
    "aws-access-key": re.compile(rb"AKIA[0-9A-Z]{16}"),
    "github-token": re.compile(rb"gh[pousr]_[A-Za-z0-9]{30,}"),
    "openai-project-key": re.compile(rb"sk-(?:proj|svcacct)-[A-Za-z0-9_-]{20,}"),
    "openai-legacy-key": re.compile(rb"sk-[A-Za-z0-9]{32,}"),
    "anthropic-key": re.compile(rb"sk-ant-[A-Za-z0-9_-]{20,}"),
    "google-api-key": re.compile(rb"AIza[0-9A-Za-z_-]{20,}"),
    "private-key": re.compile(rb"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
PRIVATE_PATH = re.compile(
    rb"/(?:var/)?home/[A-Za-z0-9_.-]+/(?:Desktop|Documents|Developer|Downloads)"
)
BINARY_SUFFIXES = {".docx", ".jpg", ".jpeg", ".png", ".zip", ".pdf", ".bin", ".gif", ".webp", ".ico", ".mp3", ".mp4", ".xlsx", ".pptx", ".exe", ".so", ".sqlite", ".gz", ".tar", ".woff", ".woff2"}


def contains_review_identity(payload: bytes) -> bool:
    """Detect identity-bearing structured reviews, without retaining values."""
    try:
        data = json.loads(payload)
    except (ValueError, UnicodeDecodeError):
        return False
    def walk(value):
        if isinstance(value, list):
            return any(walk(v) for v in value)
        if isinstance(value, dict):
            keys = {k.casefold().replace("_", ""): v for k, v in value.items()}
            review = any(k in keys for k in ("rating", "starrating", "reviewrating", "reviewid"))
            identity = any(keys.get(k) for k in ("author", "authorname", "reviewer", "reviewername", "authorattribution", "profilephotourl", "authorurl"))
            return (review and identity) or any(walk(v) for v in value.values())
        return False
    return walk(data)


def archive_name(name: str) -> str:
    posix, windows = PurePosixPath(name), PureWindowsPath(name)
    if not name or "\\" in name or posix.is_absolute() or windows.is_absolute() or windows.drive or ".." in posix.parts or any(ord(c) < 32 or ord(c) == 127 for c in name):
        raise ValueError("unsafe archive member name")
    return posix.as_posix().rstrip("/").casefold()


def inspect_payload(data: bytes, label: str, *, depth: int = 0, budget: list[int] | None = None) -> tuple[list[bytes], list[str]]:
    """Inspect archive text and image metadata without modifying original bytes."""
    payloads, errors = [data], []
    budget = budget if budget is not None else [64 * 1024 * 1024]
    if zipfile.is_zipfile(io.BytesIO(data)):
        if depth >= 3:
            return payloads, [f"{label}: archive nesting limit"]
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                if sum(m.file_size for m in archive.infolist()) > 64 * 1024 * 1024:
                    return payloads, [f"{label}: archive inspection size limit"]
                seen = set()
                for member in archive.infolist():
                    try:
                        normalized = archive_name(member.filename)
                    except ValueError:
                        errors.append(f"{label}: unsafe archive member")
                        continue
                    mode = member.external_attr >> 16
                    if member.flag_bits & 1 or normalized in seen or stat.S_IFMT(mode) not in {0, stat.S_IFREG, stat.S_IFDIR}:
                        errors.append(f"{label}: unsafe or encrypted archive member")
                        continue
                    seen.add(normalized)
                    payloads.append(member.filename.encode())
                    if not member.is_dir():
                        budget[0] -= member.file_size
                        if budget[0] < 0:
                            errors.append(f"{label}: recursive archive expansion limit")
                            break
                        nested, failures = inspect_payload(archive.read(member), label, depth=depth + 1, budget=budget)
                        payloads.extend(nested)
                        errors.extend(failures)
        except (OSError, ValueError, RuntimeError, zipfile.BadZipFile):
            errors.append(f"{label}: unreadable archive")
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        offset = 8
        while offset + 12 <= len(data):
            size = int.from_bytes(data[offset:offset + 4], "big")
            kind, chunk = data[offset + 4:offset + 8], data[offset + 8:offset + 8 + size]
            if len(chunk) != size:
                errors.append(f"{label}: truncated PNG")
                break
            if kind == b"tEXt":
                payloads.append(chunk)
            if kind == b"iTXt":
                try:
                    _, rest = chunk.split(b"\0", 1)
                    flag, method, rest = rest[0], rest[1], rest[2:]
                    _, _, text = rest.split(b"\0", 2)
                    if flag == 1 and method == 0:
                        inflater = zlib.decompressobj()
                        text = inflater.decompress(text, 1024 * 1024)
                        if inflater.unconsumed_tail or not inflater.eof:
                            errors.append(f"{label}: PNG metadata inspection limit")
                    elif flag != 0 or method != 0:
                        errors.append(f"{label}: invalid PNG compression")
                    payloads.append(text)
                except (ValueError, IndexError, zlib.error):
                    errors.append(f"{label}: malformed PNG metadata")
            if kind == b"zTXt":
                try:
                    compressed = chunk.split(b"\0", 1)[1][1:]
                    inflater = zlib.decompressobj()
                    expanded = inflater.decompress(compressed, 1024 * 1024)
                    if inflater.unconsumed_tail or not inflater.eof:
                        errors.append(f"{label}: PNG metadata inspection limit")
                    payloads.append(expanded)
                except (ValueError, IndexError, zlib.error):
                    errors.append(f"{label}: malformed PNG metadata")
            offset += size + 12
    return payloads, errors


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout


def changed_statuses(base: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for line in git("diff", "--name-status", base, "--").splitlines():
        fields = line.split("\t")
        status = fields[0]
        if status.startswith(("R", "C")):
            statuses[fields[1]] = f"{status}:old"
            statuses[fields[2]] = f"{status}:new"
        else:
            statuses[fields[1]] = status
    for path in git("ls-files", "--others", "--exclude-standard").splitlines():
        statuses.setdefault(path, "A")
    return statuses


def reviewed_asset_moves(base: str) -> dict[str, str]:
    """Recognize only the reviewed, byte-preserving historical asset relocation."""
    path = ROOT / "references/asset-retention.json"
    if not path.is_file():
        return {}
    data = json.loads(path.read_text())
    if data.get("schema") != "local-seo-brain.asset-retention.v1":
        raise ValueError("asset-retention schema mismatch")
    allowed = {}
    seen_sources, move_targets = set(), set()
    withdrawn = {row["path"]: row for row in data.get("withdrawals", []) if row.get("action") == "withdraw"}
    for row in data["moves"]:
        old, new, digest = row["from"], row["to"], row["sha256"]
        prefix = next((p for p in ("assets/template-brain", "examples/sample-vault") if old.startswith(p + "/_attachments/images/")), None)
        historical = prefix and old.startswith(prefix + "/_attachments/images/image") and old.endswith(".png")
        expected = old.replace(prefix + "/_attachments/", prefix + "/.raw/source-material/archived-attachments/", 1) if historical else "assets/archive/legacy-diagrams/" + Path(old).name
        action = row.get("action")
        source_key, target_key = archive_name(old), archive_name(new)
        if prefix is None or new != expected or action not in {"move", "deduplicate"} or (action == "deduplicate" and (historical or not old.startswith("examples/sample-vault/"))) or source_key in seen_sources or (action == "move" and target_key in move_targets):
            raise ValueError("invalid or duplicate asset relocation")
        seen_sources.add(source_key)
        if action == "move":
            move_targets.add(target_key)
        original = subprocess.run(["git", "show", f"{base}:{old}"], cwd=ROOT, capture_output=True)
        if original.returncode:
            # Once the baseline includes the migration, it grants no allowance
            # for a later addition or deletion at the retained destination.
            continue
        target = ROOT / new
        withdrawal = withdrawn.get(new)
        if withdrawal is not None:
            if (ROOT / old).exists() or target.exists() or target.is_symlink() or len(original.stdout) != row["bytes"] or hashlib.sha256(original.stdout).hexdigest() != digest or withdrawal["sha256"] != digest or withdrawal["bytes"] != row["bytes"]:
                raise ValueError("withdrawn relocation does not match baseline bytes")
            allowed[old] = "D"
            continue
        if (ROOT / old).exists() or target.is_symlink() or any(p.is_symlink() for p in target.parents) or not target.is_file() or len(original.stdout) != row["bytes"] or target.stat().st_size != row["bytes"] or hashlib.sha256(original.stdout).hexdigest() != digest or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            raise ValueError("asset relocation does not preserve baseline bytes")
        allowed[old] = "D"
        prior_target = subprocess.run(["git", "cat-file", "-e", f"{base}:{new}"], cwd=ROOT, capture_output=True)
        if action == "move" and prior_target.returncode:
            allowed[new] = "A"
    return allowed


def reviewed_asset_withdrawals(base: str) -> set[str]:
    """Recognize only the reviewed removal of the operator-supplied historical bundle."""
    path = ROOT / "references/asset-retention.json"
    if not path.is_file():
        return set()
    data = json.loads(path.read_text())
    if data.get("schema") != "local-seo-brain.asset-retention.v1":
        raise ValueError("asset-retention schema mismatch")
    allowed: set[str] = set()
    for row in data.get("withdrawals", []):
        rel, digest = row["path"], row["sha256"]
        if row.get("action") != "withdraw" or "/.raw/source-material/" not in f"/{rel}" or rel in allowed:
            raise ValueError("invalid or duplicate asset withdrawal")
        original = subprocess.run(["git", "show", f"{base}:{rel}"], cwd=ROOT, capture_output=True)
        if original.returncode:
            # Once the baseline no longer holds the file, the record grants nothing.
            continue
        if (ROOT / rel).exists() or len(original.stdout) != row["bytes"] or hashlib.sha256(original.stdout).hexdigest() != digest:
            raise ValueError("asset withdrawal does not match baseline bytes")
        allowed.add(rel)
    return allowed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True, help="Verified Git baseline commit")
    args = parser.parse_args()

    secret_hits: list[dict[str, str]] = []
    private_path_hits: list[str] = []
    cache_paths: list[str] = []
    inventory: list[dict] = []
    inspection_errors: list[str] = []
    review_identity_hits: list[str] = []
    statuses = changed_statuses(args.base)
    inputs = set(git("ls-files", "--cached", "--others", "--exclude-standard", "-z").split("\0")) - {""}
    for path in sorted(ROOT / name for name in inputs):
        if path.is_symlink():
            inspection_errors.append(f"{path.relative_to(ROOT)}: symlink input")
            continue
        rel = path.relative_to(ROOT).as_posix()
        if not path.exists() and statuses.get(rel, "").startswith(("D", "R")):
            continue
        if path.is_dir():
            if path.name == "__pycache__":
                cache_paths.append(rel)
            continue
        if path.suffix == ".pyc":
            cache_paths.append(rel)
        try:
            data = path.read_bytes()
        except OSError:
            inspection_errors.append(f"{rel}: unreadable input")
            continue
        try:
            data.decode("utf-8")
            binary = False
        except UnicodeDecodeError:
            binary = True
        if binary or path.suffix.lower() in BINARY_SUFFIXES:
            inventory.append({"path": rel, "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data),
                              "surface": "historical-private" if ".raw" in path.parts else "repository-asset"})
        payloads, failures = inspect_payload(data, rel)
        inspection_errors.extend(failures)
        if any(contains_review_identity(p) for p in payloads):
            review_identity_hits.append(rel)
        for name, pattern in SECRET_PATTERNS.items():
            if any(pattern.search(p) for p in payloads):
                secret_hits.append({"kind": name, "path": rel})
        if any(PRIVATE_PATH.search(p) for p in payloads):
            private_path_hits.append(rel)

    modified_binary: list[str] = []
    try:
        relocated = reviewed_asset_moves(args.base)
        withdrawn = reviewed_asset_withdrawals(args.base)
    except (ValueError, KeyError, OSError, TypeError) as exc:
        relocated, withdrawn = {}, set()
        inspection_errors.append("asset retention validation failed: " + type(exc).__name__)
    asset_relocations: list[str] = []
    asset_withdrawals: list[str] = []
    unexpected_added_binary: list[str] = []
    known_binary = {row["path"] for row in inventory}
    for rel, status in sorted(statuses.items()):
        binary = rel in known_binary or Path(rel).suffix.lower() in BINARY_SUFFIXES
        if not binary and status.startswith(("D", "R", "C")):
            prior = subprocess.run(["git", "show", f"{args.base}:{rel}"], cwd=ROOT, capture_output=True)
            try:
                prior.stdout.decode("utf-8")
            except UnicodeDecodeError:
                binary = True
        if not binary:
            continue
        if rel in relocated and (status == relocated[rel] or status.startswith(("R", "C"))):
            asset_relocations.append(rel)
        elif rel in withdrawn and status == "D":
            asset_withdrawals.append(rel)
        elif status == "A":
            unexpected_added_binary.append(rel)
        else:
            modified_binary.append(rel)

    result = {
        "schema": "local-seo-brain.repository-safety.v1",
        "base": args.base,
        "secret_hits": secret_hits,
        "review_identity_hits": review_identity_hits,
        "private_path_hits": private_path_hits,
        "cache_paths": cache_paths,
        "modified_binary": modified_binary,
        "reviewed_asset_relocation_paths": asset_relocations,
        "reviewed_asset_withdrawal_paths": asset_withdrawals,
        "unexpected_added_binary": unexpected_added_binary,
        "binary_inventory": inventory,
        "inspection_errors": inspection_errors,
        "inspection_scope": "bytes, archive members/text, PNG text metadata; no pixel OCR",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    failures = secret_hits + review_identity_hits + private_path_hits + cache_paths + modified_binary + unexpected_added_binary + inspection_errors
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Shared deterministic and safety helpers for Local SEO Brain scripts."""
from __future__ import annotations

import hashlib
import json
import re
import os
import tempfile
import fcntl
from contextlib import contextmanager
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def parse_as_of(value: str) -> str:
    """Return a normalized pinned date or fail without writing."""
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise SystemExit(f"ERROR: --as-of must be an ISO date (YYYY-MM-DD): {value!r}") from exc


def require_vault(value: str) -> Path:
    vault = Path(value).expanduser().resolve()
    if not vault.is_dir() or not (vault / "wiki").is_dir():
        raise SystemExit(f"ERROR: vault not found or missing wiki/: {vault}")
    validate_raw_manifest(vault)
    return vault


def require_source(value: str, *, suffixes: set[str] | None = None) -> Path:
    source = Path(value).expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"ERROR: source file not found: {source}")
    if suffixes and source.suffix.lower() not in suffixes:
        expected = ", ".join(sorted(suffixes))
        raise SystemExit(f"ERROR: expected one of {expected}: {source}")
    return source


def protect_repo_target(path: Path, *, allow_repo_target: bool) -> None:
    """Block accidental writes into the tracked checkout."""
    path = path.resolve()
    if path.is_relative_to(ROOT) and not allow_repo_target:
        raise SystemExit(
            f"ERROR: refusing tracked-worktree target {path}; use a temporary/external target "
            "or pass --allow-repo-target for an intentional reviewed repository build"
        )


def safe_slug(value: str, *, limit: int = 80) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise SystemExit("ERROR: slug is empty after normalization")
    return slug[:limit]


def safe_name(value: str) -> str:
    value = re.sub(r'[\\/:*?"<>|#^[\]\x00-\x1f\x7f]+', "-", value).strip()
    return value[:110].strip(" .") or "source"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def immutable_raw_target(raw_dir: Path, source: Path, as_of: str) -> tuple[Path, str]:
    """Choose a stable content-addressed raw path; repeated ingest reuses it."""
    digest = sha256(source)
    target = raw_dir / f"{as_of}-{digest[:12]}-{safe_name(source.name)}"
    if target.is_symlink() or (target.exists() and (not target.is_file() or sha256(target) != digest)):
        raise SystemExit("ERROR: immutable raw target hash mismatch or unsafe target")
    return target, digest


def validate_raw_manifest(vault: Path) -> None:
    manifest = vault / ".raw" / ".manifest.json"
    reject_symlink_components(vault, manifest)
    historical = vault / ".vault-meta" / "historical-seed.json"
    reject_symlink_components(vault, historical)
    if historical.is_file():
        try:
            for row in json.loads(historical.read_text())["files"]:
                target = vault / row["path"]
                reject_symlink_components(vault, target)
                if target.is_symlink() or target.is_dir():
                    raise ValueError("historical seed path is not a regular file")
                # The historical bundle is operator-supplied and not shipped.
                # An absent file is allowed; a present file must match its receipt.
                if target.is_file() and sha256(target) != row["sha256"]:
                    raise ValueError("historical seed hash mismatch")
        except (OSError, ValueError, KeyError, TypeError) as exc:
            raise SystemExit("ERROR: historical raw integrity failed") from exc
    if not manifest.exists():
        return
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        if data.get("schema") != "local-seo-brain.raw-manifest.v1" or not isinstance(data.get("sources"), list):
            raise ValueError("invalid schema")
        seen = set()
        for row in data["sources"]:
            rel = Path(row["path"])
            target = vault / rel
            reject_symlink_components(vault, target)
            if rel.is_absolute() or ".." in rel.parts or not rel.parts or rel.parts[0] != ".raw":
                raise ValueError("unsafe path")
            if str(rel) in seen or target.is_symlink() or not target.resolve().is_relative_to(vault.resolve()):
                raise ValueError("duplicate or unsafe target")
            seen.add(str(rel))
            if not target.is_file() or sha256(target) != row["sha256"]:
                raise ValueError("stored bytes differ from manifest")
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit(f"ERROR: raw manifest integrity failed ({type(exc).__name__}); no derived writes permitted") from exc


def reject_symlink_components(vault: Path, path: Path) -> None:
    try:
        rel = path.relative_to(vault)
    except ValueError:
        raise SystemExit("ERROR: vault path escape")
    if ".." in rel.parts:
        raise SystemExit("ERROR: vault path escape")
    current = vault
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            raise SystemExit("ERROR: symlink within vault mutation target")


@contextmanager
def vault_mutation(vault: Path, *, dry_run: bool = False):
    if dry_run:
        yield
        return
    lock = vault / ".vault-meta" / "ingest.lock"
    reject_symlink_components(vault, lock)
    lock.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise SystemExit("ERROR: another vault mutation is in progress; retry after it completes")
        validate_raw_manifest(vault)
        yield
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def install_immutable_raw(source: Path, target: Path, digest: str) -> None:
    if target.is_symlink() or any(parent.is_symlink() for parent in target.parents):
        raise SystemExit("ERROR: unsafe raw target")
    if target.exists():
        if not target.is_file() or sha256(target) != digest:
            raise SystemExit("ERROR: immutable raw target hash mismatch")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".raw-copy-", dir=target.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            with source.open("rb") as original:
                for chunk in iter(lambda: original.read(1024 * 1024), b""):
                    handle.write(chunk)
            handle.flush()
            os.fsync(handle.fileno())
        if sha256(temp) != digest:
            raise SystemExit("ERROR: source changed during raw copy")
        try:
            os.link(temp, target)
        except FileExistsError:
            if target.is_symlink() or not target.is_file() or sha256(target) != digest:
                raise SystemExit("ERROR: concurrent raw target conflict")
    finally:
        temp.unlink(missing_ok=True)


def update_raw_manifest(
    vault: Path,
    *,
    raw_path: Path,
    digest: str,
    kind: str,
    as_of: str,
    client: str,
    dry_run: bool = False,
) -> bool:
    """Upsert one immutable raw receipt in the canonical ingestion manifest."""
    manifest = vault / ".raw" / ".manifest.json"
    reject_symlink_components(vault, manifest)
    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"ERROR: invalid raw manifest: {exc}") from exc
    else:
        data = {"schema": "local-seo-brain.raw-manifest.v1", "sources": []}
    if data.get("schema") != "local-seo-brain.raw-manifest.v1" or not isinstance(data.get("sources"), list):
        raise SystemExit("ERROR: unsupported raw manifest schema")
    rel = raw_path.relative_to(vault).as_posix()
    record = {
        "as_of": as_of,
        "client": client,
        "kind": kind,
        "path": rel,
        "sha256": digest,
    }
    by_path = {item.get("path"): item for item in data["sources"] if isinstance(item, dict)}
    existing = by_path.get(rel)
    if existing is not None and existing != record:
        raise SystemExit(f"ERROR: immutable raw manifest conflict for {rel}")
    by_path[rel] = record
    data["sources"] = sorted(by_path.values(), key=lambda item: item["path"])
    return write_text(manifest, json_text(data), dry_run=dry_run)


def write_text(path: Path, text: str, *, dry_run: bool = False) -> bool:
    normalized = text.rstrip() + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == normalized:
        return False
    if not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".write-", dir=path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(normalized)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
            directory = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
            try:
                os.fsync(directory)
            finally:
                os.close(directory)
        finally:
            Path(temporary).unlink(missing_ok=True)
    return True


def json_text(data: object) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def yaml_list(values: list[str]) -> str:
    return json.dumps(values, ensure_ascii=False)


def yaml_scalar(value: object) -> str:
    """Return a JSON scalar, which is also a safe YAML scalar."""
    return json.dumps(value, ensure_ascii=False)


def directory_sha256(root: Path, *, exclude: set[str] | None = None) -> str:
    """Hash relative paths plus file bytes for a deterministic tree receipt."""
    ignored = exclude or set()
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file() and not item.is_symlink()):
        rel = path.relative_to(root).as_posix()
        if rel in ignored:
            continue
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        digest.update(b"\0")
    return digest.hexdigest()


def touch_note_updated(path: Path, as_of: str) -> None:
    """Set only the note modification date after an actual content write."""
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        front, sep, body = text[4:].partition("\n---\n")
        if sep:
            front = re.sub(r'^updated:.*$', f'updated: "{as_of}"', front, flags=re.M)
            write_text(path, "---\n" + front + sep + body)

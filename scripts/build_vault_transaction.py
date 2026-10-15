#!/usr/bin/env python3
"""Build a deterministic Claude Obsidian transaction from a staged vault."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


RESEARCH_PATHS = {
    "wiki/meta/ledgers/source-ledger.json",
    "wiki/meta/ledgers/claim-ledger.json",
    "wiki/meta/Claim Ledger.md",
    "wiki/sources/research-pack-2026-local-seo.md",
    "wiki/sources/_index.md",
    "wiki/index.md",
    "wiki/hot.md",
    "wiki/log.md",
}
METADATA_PATHS = {".raw/.manifest.json", ".obsidian/graph.json"}
VISUAL_PATHS = {"_attachments/brain-relationship-map.svg"}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def regular_files(root: Path) -> set[str]:
    paths = set()
    for path in root.rglob("*"):
        if path.is_file() and not path.is_symlink():
            paths.add(path.relative_to(root).as_posix())
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--staged-vault", required=True)
    parser.add_argument("--scope", required=True, choices=("research", "content", "metadata", "visual"))
    parser.add_argument("--operation-id", required=True)
    parser.add_argument("--operation-type", required=True, choices=("save", "autoresearch", "migration", "generic"))
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.scope == "visual":
        parser.error("attachment writes are outside the Obsidian transaction scope; use the reviewed visual renderer")
    expected_type = {"content": "save", "research": "autoresearch", "metadata": "migration", "visual": "generic"}[args.scope]
    if args.operation_type != expected_type:
        parser.error(f"{args.scope} scope requires {expected_type} operation type")
    vault = Path(args.vault).expanduser().resolve()
    staged = Path(args.staged_vault).expanduser().resolve()
    if not (vault / "wiki").is_dir() or not (staged / "wiki").is_dir():
        raise SystemExit("ERROR: both --vault and --staged-vault must contain wiki/")
    staged_files = regular_files(staged)
    if args.scope == "research":
        candidates = RESEARCH_PATHS
    elif args.scope == "metadata":
        candidates = METADATA_PATHS
    elif args.scope == "visual":
        candidates = VISUAL_PATHS
    else:
        candidates = {path for path in staged_files if path.startswith("wiki/")} - RESEARCH_PATHS
    expected_hashes: dict[str, str | None] = {}
    writes = []
    for rel in sorted(candidates):
        target = vault / rel
        source = staged / rel
        if not source.is_file() or source.is_symlink():
            raise SystemExit(f"ERROR: staged source missing or unsafe: {rel}")
        content = source.read_bytes()
        if target.exists():
            if not target.is_file() or target.is_symlink():
                raise SystemExit(f"ERROR: target is not a regular file: {rel}")
            current = target.read_bytes()
            if current == content:
                continue
            expected_hashes[rel] = digest(current)
            mode = "replace"
        else:
            expected_hashes[rel] = None
            mode = "create"
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SystemExit(f"ERROR: transaction content must be UTF-8: {rel}") from exc
        writes.append({"path": rel, "mode": mode, "content": text, "sha256": digest(content)})
    if not writes:
        raise SystemExit("ERROR: selected scope has no drift")
    bundle = {
        "schema": "claude-obsidian.transaction.v1",
        "operation_id": args.operation_id,
        "operation_type": args.operation_type,
        "expected_hashes": expected_hashes,
        "writes": writes,
        "address_requests": [],
        "source_manifest_updates": {},
    }
    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(bundle, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"bundle": str(out), "scope": args.scope, "writes": len(writes)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

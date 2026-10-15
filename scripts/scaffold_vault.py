#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import tempfile
import os
import json
import hashlib
from pathlib import Path

from runtime import parse_as_of, protect_repo_target, safe_slug, validate_raw_manifest


ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "assets" / "template-brain"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a Local SEO Brain client vault.")
    parser.add_argument("--client", required=True)
    parser.add_argument("--owner", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--as-of", required=True, help="Pinned build date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Validate and print the target without writing")
    parser.add_argument("--allow-repo-target", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    today = parse_as_of(args.as_of)
    slug = safe_slug(args.client)
    out = Path(args.out_dir).expanduser().resolve() / slug
    protect_repo_target(out, allow_repo_target=args.allow_repo_target)
    if out.exists():
        raise SystemExit(f"ERROR: vault exists: {out}")
    for source in TEMPLATE.rglob("*"):
        if source.is_symlink():
            raise SystemExit("ERROR: template symlinks are forbidden")
        if source.is_file() and ".raw" not in source.relative_to(TEMPLATE).parts and source.suffix in {".md", ".json", ".canvas", ".css"}:
            source.read_text(encoding="utf-8")
    validate_raw_manifest(TEMPLATE)
    if args.dry_run:
        print(f"DRY-RUN: would scaffold {out} as of {today}")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{slug}-staging-", dir=out.parent) as temporary:
        staged = Path(temporary) / "vault"
        def ignore_history(directory, names):
            return ["transactions"] if Path(directory) == TEMPLATE / ".vault-meta" else []
        shutil.copytree(TEMPLATE, staged, ignore=ignore_history)
        # Template operations were not applied to this client. Keep their exact
        # journals in the repository and bind the copied input tree separately.
        digest = hashlib.sha256()
        files = sorted(p for p in staged.rglob("*") if p.is_file())
        for path in files:
            digest.update(path.relative_to(staged).as_posix().encode() + b"\0")
            digest.update(path.read_bytes() + b"\0")
        provenance = {"schema": "local-seo-brain.template-provenance.v1", "template_sha256": digest.hexdigest(), "template_files": len(files), "scaffold_as_of": today, "copied_transaction_history": False}
        (staged / ".vault-meta/template-provenance.json").write_text(json.dumps(provenance, indent=2, sort_keys=True) + "\n")
        replacements = {"{{date}}": today, "{{client_name}}": args.client.replace("-", " ").title(), "{{owner}}": args.owner}
        for path in staged.rglob("*"):
            if ".raw" not in path.relative_to(staged).parts and path.is_file() and path.suffix in {".md", ".json", ".canvas", ".css"}:
                text = path.read_text(encoding="utf-8")
                for old, new in replacements.items():
                    text = text.replace(old, new)
                if path.suffix == ".md":
                    text = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
                path.write_text(text, encoding="utf-8")
        validate_raw_manifest(staged)
        if out.exists() or out.is_symlink():
            raise SystemExit("ERROR: output appeared during staging; refusing replacement")
        os.rename(staged, out)
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

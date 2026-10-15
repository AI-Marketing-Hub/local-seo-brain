#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
import json
import hashlib
from pathlib import Path

from runtime import parse_as_of, protect_repo_target


ROOT = Path(__file__).resolve().parent.parent


def run(*args: str) -> None:
    subprocess.run([sys.executable, *args], cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a deterministic sample Local SEO Brain vault from fixtures.")
    parser.add_argument("--out", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--replace", action="store_true", help="Replace the exact --out target after a successful staged build")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--allow-repo-target", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    as_of = parse_as_of(args.as_of)
    sample = Path(args.out).expanduser().resolve()
    protect_repo_target(sample, allow_repo_target=args.allow_repo_target)
    if sample.exists() and not args.replace:
        raise SystemExit(f"ERROR: output exists; pass --replace for this exact target: {sample}")
    if args.dry_run:
        print(f"DRY-RUN: would build fixture-only sample at {sample} as of {as_of}")
        return 0
    with tempfile.TemporaryDirectory(prefix="local-seo-brain-demo-") as tmp_value:
        tmp = Path(tmp_value)
        client = sample.name
        run("scripts/scaffold_vault.py", "--client", client, "--owner", "Demo Owner", "--out-dir", str(tmp), "--as-of", as_of)
        built = tmp / client
        # Retain the checked-in July sample inputs in fresh and repeated builds.
        # These fixture bytes are historical evidence, not refreshed observations.
        if client == "sample-vault":
            history = ROOT / "tests/fixtures/sample-history/.raw"
            shutil.copytree(history, built / ".raw", dirs_exist_ok=True)
            receipt = built / ".vault-meta/historical-seed.json"
            data = json.loads(receipt.read_text())
            for row in data["files"]:
                # Historical bundle files are operator-supplied; absent files keep their receipt.
                if (built / row["path"]).is_file():
                    row["sha256"] = hashlib.sha256((built / row["path"]).read_bytes()).hexdigest()
            receipt.write_text(json.dumps(data, indent=2) + "\n")
        if sample.exists():
            # A replace operation may add current fixtures but cannot discard or
            # rewrite stored historical material. Metadata is merged by path.
            old_manifest = json.loads((sample / ".raw/.manifest.json").read_text())
            new_manifest = json.loads((built / ".raw/.manifest.json").read_text())
            rows = {row["path"]: row for row in new_manifest["sources"]}
            for source in (sample / ".raw").rglob("*"):
                if not source.is_file() or source.name == ".manifest.json":
                    continue
                target = built / source.relative_to(sample)
                if target.exists() and target.read_bytes() != source.read_bytes():
                    raise SystemExit("ERROR: sample replacement would change historical raw bytes")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            for row in old_manifest["sources"]:
                if row["path"] in rows and rows[row["path"]] != row:
                    raise SystemExit("ERROR: sample raw manifest conflict")
                rows[row["path"]] = row
            new_manifest["sources"] = sorted(rows.values(), key=lambda row: row["path"])
            (built / ".raw/.manifest.json").write_text(json.dumps(new_manifest, indent=2, sort_keys=True) + "\n")
        common = ("--vault", str(built), "--client", client, "--as-of", as_of)
        run("scripts/ingest_source.py", *common, "--file", "tests/fixtures/sample-source.md", "--label", "Sample Source")
        run("scripts/ingest_gbp.py", *common, "--file", "tests/fixtures/sample-gbp.csv")
        run("scripts/ingest_citations.py", *common, "--file", "tests/fixtures/sample-citations.csv")
        run("scripts/ingest_reviews.py", *common, "--file", "tests/fixtures/sample-reviews.json")
        run("scripts/ingest_geogrid.py", *common, "--file", "tests/fixtures/sample-geogrid.csv")
        manifest = json.loads((built / ".raw/.manifest.json").read_text())
        historical = [row for row in manifest["sources"] if row["as_of"] < as_of]
        if historical:
            guide = built / "wiki/sources/Source Manifest Guide.md"
            lines = ["## Historical fixture receipts", "", "These synthetic fixture inputs are retained by pinned operation date. They are manifest-only history, not current business observations or recommendations.", "", "| Pinned date | Kind | Immutable raw path | SHA-256 |", "|---|---|---|---|"]
            lines += [f"| {row['as_of']} | {row['kind']} | `{row['path']}` | `{row['sha256']}` |" for row in historical]
            guide.write_text(guide.read_text().replace("## Related", "\n".join(lines) + "\n\n## Related"))
        run("scripts/synthesize_brain.py", "--vault", str(built), "--as-of", as_of)
        run("scripts/generate_vault_visuals.py", "--vault", str(built))
        run("scripts/render_brain_report.py", "--vault", str(built), "--html-only")
        run("scripts/lint_vault.py", "--vault", str(built))
        sample.parent.mkdir(parents=True, exist_ok=True)
        if sample.exists():
            shutil.rmtree(sample)
        shutil.copytree(built, sample)
    print(f"Demo vault generated at {sample}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render or check the deterministic file-by-file claim coverage matrix."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "references/claim-coverage-matrix.md"
PUBLIC_FILES = (
    "README.md",
    "SKILL.md",
    "marketplace.json",
    "docs/OPERATOR_KIT.md",
    "docs/PRODUCT_BOUNDARIES.md",
    "references/product-spec.md",
    "RELEASE_CHECKLIST.md",
    "PUBLISHING_NOTICE.md",
)
BEHAVIOR_FILES = (
    "scripts/scaffold_vault.py",
    "scripts/ingest_knowledge_base.py",
    "scripts/ingest_source.py",
    "scripts/ingest_gbp.py",
    "scripts/ingest_citations.py",
    "scripts/ingest_reviews.py",
    "scripts/ingest_geogrid.py",
    "scripts/synthesize_brain.py",
    "scripts/build_demo_vault.py",
    "scripts/generate_vault_visuals.py",
    "scripts/render_brain_report.py",
    "scripts/lint_vault.py",
    "scripts/guide_next_action.py",
    "scripts/repository_safety_scan.py",
)


def matrix_text() -> str:
    overlays = json.loads((ROOT / "data/knowledge-overlays.json").read_text(encoding="utf-8"))["notes"]
    claims = json.loads((ROOT / "references/claim-ledger.json").read_text(encoding="utf-8"))["claims"]
    claims_by_path: dict[str, list[str]] = {}
    for claim in claims:
        for location in claim["locations"]:
            path = location.split("#", 1)[0]
            claims_by_path.setdefault(path, []).append(claim["id"])
    rows: list[tuple[str, str, str, str, str]] = []
    for rel, entry in sorted(overlays.items()):
        full = f"assets/template-brain/{rel}"
        kind = "prompt" if "/prompts/" in rel else "chapter"
        claim_ids = entry["claim_ids"] or ["legacy-seed-boundary"]
        rows.append((full, kind, entry["assessment"], entry["confidence"], ", ".join(claim_ids)))
    for path in sorted((ROOT / "assets/template-brain/wiki/freshness").glob("2026-*.md")):
        rel = path.relative_to(ROOT).as_posix()
        ids = sorted(set(claims_by_path.get(rel, [])))
        declared = re.search(r'^claim_ids:\s*(\[.*\])', path.read_text(), re.M)
        if declared and set(json.loads(declared.group(1))) != set(ids):
            raise SystemExit(f"ERROR: freshness note claim locations disagree: {rel}")
        rows.append((rel, "freshness", "claim-ledger", "mixed", ", ".join(ids) or "no material claim"))
    reviewed_docs = set(PUBLIC_FILES)
    reviewed_docs.update(p.relative_to(ROOT).as_posix() for folder in (ROOT, ROOT / "docs", ROOT / "references", ROOT / "references/canon", ROOT / "agents") for p in folder.glob("*.md"))
    reviewed_docs.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "assets/svg").glob("*.svg"))
    for rel in sorted(reviewed_docs):
        ids = sorted(set(claims_by_path.get(rel, [])))
        historical = rel in {"docs/VERIFICATION_REPORT.md", "docs/VERIFIED_CHANGE_MANIFEST.md"}
        disposition = "historical snapshot" if historical else "claim-ledger" if ids else "reviewed procedure or inventory"
        rows.append((rel, "public-doc", disposition, "historical" if historical else "scoped", ", ".join(ids) or "no independent empirical assertion"))
    for rel in sorted(path.relative_to(ROOT).as_posix() for path in (ROOT / "scripts").glob("*.py")):
        ids = sorted(set(claims_by_path.get(rel, [])))
        tests = json.loads((ROOT / "data/behavior-contracts.json").read_text()).get(rel, [])
        if any(not (ROOT / test).is_file() for test in tests):
            raise SystemExit(f"ERROR: missing behavior test for {rel}")
        rows.append((rel, "script", "behavioral checks" if tests else "untested", "local-check" if tests else "unknown", ", ".join(tests) or "untested"))
    lines = [
        "# File-by-File Claim Coverage Matrix",
        "",
        "Generated from `data/knowledge-overlays.json` and `references/claim-ledger.json`. The matrix is an inventory projection; the canonical ledgers control claim wording and source relationships.",
        "",
        f"Coverage: {sum(row[1] == 'chapter' for row in rows)} chapters, {sum(row[1] == 'prompt' for row in rows)} prompts, {sum(row[1] == 'freshness' for row in rows)} freshness notes, {sum(row[1] == 'public-doc' for row in rows)} public docs, and {sum(row[1] == 'script' for row in rows)} described scripts.",
        "",
        "| File | Surface | Disposition | Confidence | Claim or contract IDs |",
        "|---|---|---|---|---|",
    ]
    for rel, surface, disposition, confidence, ids in rows:
        lines.append(f"| `{rel}` | {surface} | {disposition} | {confidence} | {ids} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("render", "check"))
    args = parser.parse_args()
    expected = matrix_text()
    if args.command == "check":
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            raise SystemExit("ERROR: references/claim-coverage-matrix.md has drift")
        print("Coverage matrix check passed")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

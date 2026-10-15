# Release Checklist: Local SEO Brain 0.3.0

This checklist verifies a local review candidate. Commit, push, PR, publication, release, and account changes require separate authority. A failed gate stays failed.

## Dates, baseline, and isolated checkers

The snapshot date comes from the canonical ledger. The evaluation date is the actual review date in UTC. Snapshot determinism does not imply current evidence.

```bash
export PYTHONDONTWRITEBYTECODE=1
export CLAUDE_OBSIDIAN_REVIEW_TIMEZONE=UTC
export TZ=UTC
SNAPSHOT=$(python3 -c 'import json; print(json.load(open("references/source-ledger.json"))["as_of"])')
REVIEW_ON=$(date +%F)
BASE=c37420fce1087a5814af804b1f9eb96b4d58c779
```

Use isolated checkouts of Claude Obsidian `32ac5a02c4e082e4a5628ca810776375e134708e` and Brainstein `32b14a2e35819ae4c0dec9278a3dd3cd2df8dff1`, matching CI. Apply `patches/claude-obsidian-review-timezone.patch` to the first and `patches/brainstein-evidence-ledger-compat.patch` with `git apply --unidiff-zero` to the second. Set `OBSIDIAN_CLI` to its `scripts/claude-obsidian.py` and `BRAINSTEIN_ROOT` to the Brainstein source checkout. Receipts hash the full verifier packages and invoke Brainstein with a controlled source path. Do not change global installations. Keep verifier checkouts and outputs outside package inputs.

## Evidence, content, and generation

```bash
python3 scripts/historical_seed_contract.py
python3 scripts/version_contract.py
python3 scripts/evidence_contract.py validate --as-of "$SNAPSHOT"
python3 scripts/evidence_contract.py check --as-of "$SNAPSHOT" --vault assets/template-brain
python3 scripts/evidence_contract.py freshness --as-of "$REVIEW_ON" --format json
python3 scripts/coverage_matrix.py check
python3 scripts/working_content_contract.py
```

Require immutable historical bytes, reciprocal evidence relationships, review intervals, exact generated projections, supported working claims, resolved navigation, and explicit unsupported dispositions. Material changes to wiki pages require inspected hash-bound transactions. Preserve failed and historical evidence.

## Regression suite

```bash
python3 tests/test_pipeline.py
python3 tests/test_domain_ingestors.py
python3 tests/test_reseed_preserves_overlays.py
python3 tests/test_citation_contract.py
python3 tests/test_demo_determinism.py
python3 tests/test_cli_safety.py
python3 tests/test_privacy_and_refusals.py
python3 tests/test_version_consistency.py
python3 tests/test_documentation_claims.py
python3 tests/test_scaffold.py
python3 tests/test_freshness.py
python3 tests/test_raw_integrity.py
python3 tests/test_release_receipt.py
python3 tests/test_safety_scan.py
```

Tests build only in temporary directories. Require two identical sample builds for identical inputs and snapshot date, overlay persistence after reseeding, and equality with the checked-in sample receipt.

## Vault and external checker gates

```bash
python3 scripts/lint_vault.py --vault assets/template-brain
python3 scripts/lint_vault.py --vault examples/sample-vault
python3 "$OBSIDIAN_CLI" lint --vault assets/template-brain --as-of "$REVIEW_ON" --format json --strict
python3 "$OBSIDIAN_CLI" lint --vault examples/sample-vault --as-of "$REVIEW_ON" --format json --strict
PYTHONPATH="$BRAINSTEIN_ROOT" python3 -P -m brainstein audit-brain . --json
PYTHONPATH="$BRAINSTEIN_ROOT" python3 -P -m brainstein next . --json --limit 10
python3 scripts/guide_next_action.py --vault assets/template-brain --as-of "$REVIEW_ON"
```

The release threshold remains anatomy at least 90, SSS+, market-ready, `market_ready: true`, and no critical failures. Record checker incompatibilities and actual findings. Task completeness, support, and relevant navigation govern content quality; never add lines or links to manufacture maturity.

## Final safety and reviewed receipt

Run safety after tests and generated writes. The scanner inspects tracked and nonignored inputs, archive members, and binary metadata. It reports kinds and paths without sensitive values; it does not perform image OCR or certify live accounts.

```bash
python3 scripts/repository_safety_scan.py --base "$BASE"
git diff --check "$BASE"
git status --short
python3 scripts/verification_receipt.py --out /tmp/local-seo-verification.json --base "$BASE" --as-of "$REVIEW_ON" --obsidian-cli "$OBSIDIAN_CLI" --brainstein-root "$BRAINSTEIN_ROOT"
```

A dirty local tree may receive a review receipt with `release_ready: false`. Packaging requires a clean committed candidate, a prior ancestor baseline, current verification, all gates, exact reviewed bytes, canonical version, and explicit checker identities. The package command independently reruns verification. `--market-ready-audit` is only a deprecated alias for the new receipt format. A legacy or manually fabricated audit cannot authorize a package.

The dated verification report must identify passed and failed checks, scope, remaining gaps, and remote-verification limitations. A local report is neither publication nor a release-ready claim.

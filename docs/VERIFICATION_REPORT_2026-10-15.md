# Local SEO Brain maintenance verification, 2026-10-15

## Result and scope

The local maintenance diff refreshes the evidence snapshot, replaces working content, and enforces freshness and immutable ingestion. Version remains **0.3.0**. It is a review candidate with a **failing Brainstein release gate**, not a market-ready or published release. All 14 repository regression scripts pass. Repository and strict Claude Obsidian lints pass for both template and generated sample.

The deeper [vault quality review](VAULT_QUALITY_2026-10-15.md) records the final graph, task-specific editorial corrections, attachment archives, and scaffold provenance repair.

The path inventory is in `CHANGE_MANIFEST_2026-10-15.md`.

Review baseline: `c37420fce1087a5814af804b1f9eb96b4d58c779`, branch `codex/local-seo-brain-evidence-refresh-2026`. The initial working tree was clean. This report concerns local source, fixture behavior, and inspected primary documentation. It does not establish live account, vendor integration, production, ranking, accessibility-device, or client acceptance.

## Evidence and content reviewed

- Revisited all 66 previous sources, added four controlling primary sources, and reviewed all 39 previous claim dispositions. The current ledgers contain **70 sources and 50 claims**. Review outcomes: 37 unchanged, 27 changed, two superseded in part, four added. No source required an unavailable disposition in this pass; alternate primary URLs are identified where used. These outcomes describe inspected claim-bearing passages, not whole-page byte equality.
- Current claim dispositions: 40 accepted, six unsupported, two provisional, one contested, one deprecated. Unsupported formulas and causal promises remain explicitly unsupported. Provisional studies retain population, method, date, and generalization limits.
- Replaced all **59 chapter and 37 prompt** working bodies through overlays. Reviewed six freshness notes, task hubs, operating instructions, source maps, canon entries, product descriptions, and eight SVG surfaces. Stable slugs and raw provenance links remain. Prompt roles specify inputs, missing-input behavior, output acceptance, and human review.
- Added scoped coverage of review disclosure versus Maps incentives, regional Search units, generative-AI content guidance, Search documentation/update events, and GBP API fields. Documentation of a field does not establish a live integration.
- Removed fixed page, word, line, link, ranking-weight, and cadence promises from working guidance. The old Core 30 visual now shows task-based page planning. Marketing and pipeline labels describe descriptive adapters and Draft synthesis. Historical July verification and ledgers remain labeled snapshots.

The exact source IDs, URLs, review dates, locators, alternate inspected URLs, scope, and dispositions are in `references/source-review-2026-10-15.json`, the canonical ledgers, and the generated claim coverage matrix. No full third-party pages were copied into the repository.

## Enforcement implemented

`evidence_contract.py freshness --as-of YYYY-MM-DD --format json` evaluates age independently of deterministic snapshot validation. The internal review intervals are seven days for ranking/documentation update feeds, 14 days for GBP API sources, and 30 days otherwise. Deadlines require review on the due date. Claim deadlines include supporting and contradicting evidence; overlay deadlines inherit their earliest claim. Impossible date order, future verification/publication dates, unknown IDs, graph mismatches, and unavailable active support fail validation.

Hot, Dashboard, and the next-action helper direct operators to refresh evidence before client recommendations. The helper accepts an explicit evaluation date. CI is read-only, runs freshness on pushes, PRs, manual dispatch, and Mondays at 06:00 UTC, and never fetches accounts, rewrites evidence, or sends messages. Hosted execution of this workflow remains unverified.

All five ingestors and synthesis verify stored raw bytes and manifest hashes before derived writes. Vault mutations are serialized. Existing payloads cannot be overwritten on reuse. The sample generator preserves July payloads, retains their manifest rows, and appends current fixture receipts. Replacing a sample at a later date accumulates history, so that historical build may differ from a fresh later-date build.

Verification receipts bind the actual file manifest, Git identity, prior baseline, canonical version, snapshot date, evaluation date, full external checker source hashes, and required gate results. Brainstein executes with a controlled module path and import-origin check. Packaging requires a clean committed tree and independently reruns verification before comparing exact staged bytes and constructing a temporary, verified archive. The deprecated `--market-ready-audit` flag accepts only the new receipt format.

## Verification commands and results

The complete executable procedure is `RELEASE_CHECKLIST.md`. Local tests used Python 3.14.4; CI declares Python 3.11, and that hosted runtime was not executed here. The following checks were run locally with `PYTHONDONTWRITEBYTECODE=1`, and the review timezone exported as `TZ` and `CLAUDE_OBSIDIAN_REVIEW_TIMEZONE`, as `RELEASE_CHECKLIST.md` describes.

| Check | Command or exact scope | Result |
|---|---|---|
| Historical seed | `python3 scripts/historical_seed_contract.py` | Pass, 50 integrity-checked files (three course inputs, 31 extracted PNGs, 16 archived authored JPGs) |
| Original raw payloads | Compare every tracked `.raw` payload, excluding mutable manifests, against baseline Git bytes | Pass, 13 original tracked payloads, no modification or deletion |
| Version | `python3 scripts/version_contract.py` | Pass, 0.3.0 |
| Snapshot evidence | `python3 scripts/evidence_contract.py validate --as-of 2026-10-15` | Pass, 70 sources and 50 claims |
| Projection | `python3 scripts/evidence_contract.py check --as-of 2026-10-15 --vault assets/template-brain` | Pass, five projections with no drift |
| Current freshness | `python3 scripts/evidence_contract.py freshness --as-of 2026-10-15 --format json` | Pass, no due or overdue current evidence; first review deadline October 22 |
| Coverage | `python3 scripts/coverage_matrix.py check` | Pass, chapters, prompts, freshness, docs, visuals, and named behavior checks or explicit untested states |
| Working content | `python3 scripts/working_content_contract.py` | Pass, exact overlays, task prompts, citations, no repeated links, all 96 working notes reachable from Index within two hops |
| Tests | Every `tests/test_*.py` script listed below | Pass, 14 of 14 scripts |
| Repository vault lint | `python3 scripts/lint_vault.py --vault assets/template-brain` and `--vault examples/sample-vault` | Both pass |
| Strict Obsidian | Isolated pinned CLI, `lint --vault <template-or-sample> --as-of 2026-10-15 --format json --strict` | Both pass, zero findings |
| Deterministic builds | `tests/test_demo_determinism.py` builds two temporary samples, verifies repeated replacement, and compares the checked-in receipt | Pass |
| Brainstein audit and next | `PYTHONPATH=<isolated-root> python3 -P -m brainstein audit-brain . --json` and `next . --json --limit 10` | Both commands complete and return JSON; audit is not release-ready |
| Brainstein release gate | `python3 scripts/brainstein_gate.py <saved-audit.json>` | **Fail**, anatomy 89, grade SS, maturity demo-verified, `market_ready: false` |
| Safety after tests | `python3 scripts/repository_safety_scan.py --base c37420fce1087a5814af804b1f9eb96b4d58c779` | Pass, 93 binary inventory entries, with 172 explicitly reviewed relocation paths, no secret signatures, structured review identities, private paths, cache paths, inspection errors, or unintended binary churn |
| Patch hygiene | `git diff --check c37420fce1087a5814af804b1f9eb96b4d58c779` | Pass |
| Python syntax | In-memory `compile()` of scripts and tests, without writing bytecode | Pass |
| Receipt runner | `python3 scripts/verification_receipt.py --out <external-receipt.json> --base c37420fce1087a5814af804b1f9eb96b4d58c779 --as-of 2026-10-15 --obsidian-cli <isolated-cli> --brainstein-root <isolated-root>` | Returns failure and records `release_ready: false`, as required for this dirty tree and failing maturity gate |

Regression scripts: `test_pipeline.py`, `test_domain_ingestors.py`, `test_reseed_preserves_overlays.py`, `test_citation_contract.py`, `test_demo_determinism.py`, `test_cli_safety.py`, `test_privacy_and_refusals.py`, `test_version_consistency.py`, `test_documentation_claims.py`, `test_scaffold.py`, `test_freshness.py`, `test_raw_integrity.py`, `test_release_receipt.py`, and `test_safety_scan.py`.

The regressions cover deadline boundaries and future dates, stale supporting and contradicting dependencies, unknown overlays and graph mismatches, all five raw-ingestor corruption paths, synthesis corruption, symlink paths, concurrent mutation locks, malformed/stale/future/mismatched/incomplete/failing receipts, changed package inputs, committed whitespace, canonical package ordering, unsafe archive members, compressed image metadata, structured review identities, and opaque binary additions/deletions.

Sample tree SHA-256: `edeabdb9d12b324d80906e09b95e79d222615e6218b09ea2315aa4bd0f11f83e`. The two independent temporary builds and checked-in sample agree. The sample manifest contains five preserved July rows and five October rows. Fixture ingestion dates are pinned build dates, not newly observed business measurements.

## Canonical write and verifier provenance

Canonical wiki updates were staged, inspected, and applied through 12 hash-bound Claude Obsidian transactions. Completed journals remain under the canonical template's `.vault-meta/transactions/`. New scaffolds exclude those journals and record a separate template-provenance receipt instead. A scope correction changed two notes; the final transaction aligned 25 generated chapter links with current prompt titles. Generated visual attachments use their reviewed repository renderer because the Obsidian API accepts wiki content only.

The checked tool versions are Claude Obsidian 2.2.0 (lint engine 1.1.1) and Brainstein 1.2.0. Claude Obsidian is pinned to `32ac5a02c4e082e4a5628ca810776375e134708e`, with the explicit review-timezone patch. Brainstein is pinned to `32b14a2e35819ae4c0dec9278a3dd3cd2df8dff1`, with the existing evidence-ledger compatibility patch. Both run from isolated temporary checkouts consistent with CI. No global installation changed. The timezone patch selects the real review calendar date; transaction timestamps remain UTC, and explicit dates remain explicit. The old unavailable Obsidian pin was not claimed as tested.

## Failed gates and remaining limits

Brainstein still applies average line and link quotas (80 lines and eight links per note). These fail after removal of padding and redundant navigation. Its packaging detector also warns that `package_release.py` lacks the literal legacy `audit_brain.py` hook, even though packaging now independently runs the broader verification receipt. The audit has zero critical failures, an uncapped score of 90, and a capped score of 89. These are recorded external-checker results. No score, marker, or note padding was added to satisfy them. The release threshold was not weakened.

Packaging success was deliberately not claimed or attempted: the tree is uncommitted and the required release gate fails. Rejection behavior is tested. External-account and paid-provider behavior is outside this review. The safety scan checks byte signatures, structured review identity fields, archive members/text, and PNG text metadata; it does not perform pixel OCR, exhaustive semantic PII detection, or certify compliance of arbitrary future exports.

Origin is locally configured as `https://github.com/AI-Marketing-Hub/local-seo-brain.git`. Final read-only rechecks still returned GitHub connector 404 and shell DNS failure. Latest remote identity, upstream changes, hosted CI execution, and branch synchronization remain unverified. Local work was preserved, with no commit, push, PR, tag, package, publication, release, paid call, or account mutation.

# Local SEO Brain Operator Kit

## Maturity and intended use

Local SEO Brain is an advisory, read-only operating brain. Maturity is measured by fresh Brainstein JSON and repository evidence, never by marketing prose. A checkout is market-ready only when the release checklist, both vault lints, deterministic tests, privacy checks, evidence gates, and Brainstein SSS+ gate all pass.

## Quick start

1. Scaffold into an explicit output directory with `scripts/scaffold_vault.py` and a pinned `--as-of` date.
2. Keep client exports outside the repository until an approved ingest command copies them into the client vault's immutable `.raw/` area.
3. Run the relevant GBP, citation, review, or geo-grid importer with an explicit vault, client, and location.
4. Synthesize only measured outputs. Missing inputs produce `no_data` or `needs_input`, never estimated values.
5. Review recommendations in the Approval Queue. The brain does not apply them to external accounts.
6. Run both lints and the relevant tests before sharing a report.

## Evidence workflow

Official Google policy controls policy claims. Official product documentation controls feature and API claims. Independent studies may support scoped observations, but they do not rewrite policy. Every material claim has a stable claim ID, assessment, confidence tag, source locator, verification date, and refresh date in the canonical ledgers.

## Generated-content workflow

The historical seed is immutable and operator-supplied; it is third-party material and is not shipped. The generated notes are committed, so regeneration is optional. If you hold the bundle, place it under `assets/template-brain/.raw/source-material/` and `scripts/historical_seed_contract.py` verifies it against the recorded hashes. `scripts/ingest_knowledge_base.py` generates notes, applies `data/knowledge-overlays.json`, adds citations and confidence metadata, and writes hubs. `scripts/evidence_contract.py` owns ledger projections. Use the same `--as-of` value for reproducible output, and require projection check mode to report no drift.

## Approval and rollback

The Approval Queue records the proposed change, source, owner, target account, risk, expected result, and rollback. Approval is a recommendation state; it is not authority for this repository to call a live API.

## Incident handling

If a source is stale, a transaction hash conflicts, an output changes unexpectedly, or private data appears, stop the affected operation. Preserve evidence, record the exact path and command, rotate exposed credentials outside the repository if applicable, and rebuild from the last verified inputs.

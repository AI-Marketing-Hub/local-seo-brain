---
name: local-seo-brain
description: >
  Scaffold and operate an evidence-led Local SEO Obsidian vault from authorized
  exports. Use for current doctrine lookup, source intake, descriptive GBP,
  citation, review, and geo-grid ingestion, Draft synthesis, linting, and
  approval-first planning. Never use it to mutate live accounts.
---

# Local SEO Brain

Use this skill when the user asks to create or operate a Local SEO Brain client vault, ingest an authorized export, inspect current evidence, produce Draft deliverables, or identify the next approval-first action.

## Read first

1. Read `AGENTS.md` and `docs/PRODUCT_BOUNDARIES.md`.
2. Read the target vault's `CODEX.md`, `wiki/hot.md`, and `wiki/index.md`.
3. For doctrine-bearing work, read `references/claim-ledger.json`, `references/source-ledger.json`, and `references/safety-gates.md`.
4. Pin an explicit ISO `--as-of` date. Unknown values remain unknown.

## Operating contract

- External systems are read-only. Do not edit Business Profile, Maps, Places, Search Console, analytics, review, citation, social, or website accounts.
- Store only operator-authorized exports. Raw review data can contain personal data; keep client vaults access-controlled and follow the operator's retention policy.
- Derived review notes omit reviewer names and per-review identity.
- Do not infer ranking causality from descriptive export metrics.
- Do not generate numeric or letter scores unless a documented formula, inputs, no-data behavior, and tests exist. The bundled synthesizer emits **Draft**.
- Proposed account changes go through `wiki/decisions/Approval Queue.md` with source, owner, risk, and rollback.
- Refuse address/proximity gaming, virtual-office abuse, fake reviews, review gating, PBN/link spam, doorway pages, hidden text, mass low-quality citations, prohibited Places storage, credentials, and guaranteed ranking claims.

## Commands

Scaffold outside the tracked checkout:

```bash
python3 scripts/scaffold_vault.py \
  --client CLIENT_SLUG --owner "OWNER" \
  --out-dir /absolute/output/parent --as-of YYYY-MM-DD
```

Ingest one manual evidence file:

```bash
python3 scripts/ingest_source.py \
  --vault /absolute/vault --client CLIENT_SLUG \
  --file /absolute/source --label "SOURCE LABEL" --as-of YYYY-MM-DD
```

Ingest supported domain exports:

```bash
python3 scripts/ingest_gbp.py \
  --vault /absolute/vault --client CLIENT_SLUG \
  --file /absolute/gbp.csv --as-of YYYY-MM-DD

python3 scripts/ingest_citations.py \
  --vault /absolute/vault --client CLIENT_SLUG \
  --file /absolute/citations.csv --as-of YYYY-MM-DD

python3 scripts/ingest_reviews.py \
  --vault /absolute/vault --client CLIENT_SLUG \
  --file /absolute/reviews.json --as-of YYYY-MM-DD

python3 scripts/ingest_geogrid.py \
  --vault /absolute/vault --client CLIENT_SLUG \
  --file /absolute/geogrid.csv --as-of YYYY-MM-DD
```

Regenerate seed notes in a client vault from the canonical overlay:

```bash
python3 scripts/ingest_knowledge_base.py \
  --vault /absolute/vault --as-of YYYY-MM-DD --dry-run
```

Remove `--dry-run` only after reviewing the exact target and overlay date.

Produce and inspect Draft outputs:

```bash
python3 scripts/synthesize_brain.py --vault /absolute/vault --as-of YYYY-MM-DD
python3 scripts/lint_vault.py --vault /absolute/vault
python3 scripts/render_brain_report.py --vault /absolute/vault
python3 scripts/guide_next_action.py --vault /absolute/vault
```

## Output interpretation

- GBP adapter: file provenance, row/column counts, and a location shell. No performance trend calculation.
- Citation adapter: exported directory, URL, and status. No computed NAP or competitor gap.
- Review adapter: count, average, observed date range, rating distribution, and rough token frequency. No causal or universal benchmark claim.
- Geo-grid adapter: observed average rank, range, and top-three share for the supplied sample. No causal diagnosis.
- Synthesis: Draft source coverage and review steps. No fabricated grade or recommendation priority.

## Current evidence

Official policy controls policy claims. Independent research can support scoped empirical observations but cannot override policy. Historical seed prescriptions remain only in immutable raw provenance; working guidance cites current claims and sources. Use the vault's `Claim Ledger` and `Local SEO Evidence Research Pack` for current dispositions.

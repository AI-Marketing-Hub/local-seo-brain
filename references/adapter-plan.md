# Local SEO Brain Adapter Contract

Reviewed 2026-10-15 against the implemented scripts and domain-ingestor tests.

## Inputs and storage

The five ingestors accept manual evidence, GBP CSV, citation CSV, review JSON/CSV, and geo-grid CSV exports. Parsers implement their documented field aliases and missing-data checks. The published JSON Schemas describe ledgers and overlays; they are not universal client-export schemas.

Commands require explicit vault, client, source, and as-of inputs. Raw files are content-addressed, existing bytes and manifest hashes are verified before reuse, and mutations hold a vault lock. Dry runs do not install raw files or write derived notes. Private client exports belong in authorized external vaults, never repository fixtures.

## Descriptive outputs

GBP notes report exported rows and columns. Citation notes report supplied directory, URL, and status, without calculating a NAP difference. Review summaries report ratings, dates, and token frequencies and omit author identity. Geo-grid notes summarize supplied observed ranks. These are descriptive adapters, with no causal ranking model or account integration.

## Synthesis and rendering

Synthesis emits Draft source-coverage deliverables, review steps, and report content. It does not calculate a health grade, inferred ranking impact, or competitor gaps. HTML and SVG renderers present those outputs. Owner review and rollback belong in the Approval Queue before external actions.

## Verification

Named behavior checks are mapped in `data/behavior-contracts.json`. They exercise temporary fixture vaults, immutability, privacy, idempotency, deterministic builds, help, and dry runs. Live vendor or client behavior has not been tested by these local checks.

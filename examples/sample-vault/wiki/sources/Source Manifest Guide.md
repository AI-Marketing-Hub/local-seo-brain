---
type: "source-guide"
title: "Source Manifest Guide"
created: "2026-07-18"
updated: "2026-10-15"
status: "active"
tags: ["type/source-guide", "domain/sources", "provenance/ledger"]
---

# Source Manifest Guide

## Imported evidence

`.raw/.manifest.json` records each imported path, SHA-256, kind, client slug, and pinned operation date (`as_of`). The operation date is not proof that the business observation or source publication occurred that day. Record collection date, owner, trust, and reuse scope separately during [[Source Intake Workflow]].

Keep older raw rows when a new export arrives. They establish historical provenance; they do not support current advice merely because their hashes still match. The generated sample lists its retained historical fixture receipts below this guidance.

## Historical and template provenance

`.vault-meta/historical-seed.json` verifies the original course bundle and its extracted images. The images under `.raw/source-material/archived-attachments/` are private historical derivatives, retained for preservation. They are not current working illustrations or evidence for ranking advice.

The repository separately retains old project-authored illustrations in `assets/archive/legacy-diagrams/`, with exact hashes in `references/asset-retention.json`. These illustrative drafts are not client observations and are not copied into new vaults.

`.vault-meta/template-provenance.json` binds a newly scaffolded vault to the template bytes copied before client substitution. Canonical template transaction journals stay in the repository. They are not client transactions and are not copied or rewritten during scaffolding.

## Historical fixture receipts

These synthetic fixture inputs are retained by pinned operation date. They are manifest-only history, not current business observations or recommendations.

| Pinned date | Kind | Immutable raw path | SHA-256 |
|---|---|---|---|
| 2026-07-18 | citations | `.raw/clients/sample-vault/citations/2026-07-18-6cb34216fcc6-sample-citations.csv` | `6cb34216fcc62b084165bdefcc45c4653a88d9bd0f7d1fd2c4a62eb6e4725cec` |
| 2026-07-18 | gbp | `.raw/clients/sample-vault/gbp/2026-07-18-7998909694aa-sample-gbp.csv` | `7998909694aab450b69b8c673170e8e46c5c356919e29d8202ead4b00a061f30` |
| 2026-07-18 | geogrid | `.raw/clients/sample-vault/geogrid/2026-07-18-ac73cd2ed9e7-sample-geogrid.csv` | `ac73cd2ed9e70dbf1e2014a0607382c37694335967187874003e1e85de3d36e7` |
| 2026-07-18 | reviews | `.raw/clients/sample-vault/reviews/2026-07-18-2facece74728-sample-reviews.json` | `2facece74728b252eaf1e4f006a8b123519dc24ad5ed5a874c0ac556163eaf59` |
| 2026-07-18 | manual | `.raw/sources/manual/2026-07-18-a6617dd8575d-sample-source.md` | `a6617dd8575d8d5d01b79527bb92d6f6496e8cafd31ed67dd8dbeb4fc1056a33` |

## Related
- [[wiki/sources/_index|Sources Hub]]

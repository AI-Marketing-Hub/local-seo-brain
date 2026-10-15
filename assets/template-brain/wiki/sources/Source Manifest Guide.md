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

## Related
- [[wiki/sources/_index|Sources Hub]]

---
type: "prompt"
title: "Structured Data Validation Review"
parent: "Schema Explanation"
parent_folder: "frameworks"
created: "2026-10-15"
updated: "2026-10-15"
status: "active"
tags: ["type/prompt", "domain/local-seo", "evidence/provisional"]
claim_ids: ["operator-evidence-review", "truthful-firsthand-content", "structured-data-vocabulary-distinction", "structured-data-no-guarantee", "own-business-review-markup-ineligible"]
assessment: "provisional"
confidence: "PRACTITIONER"
verified_at: "2026-10-15"
refresh_due: "2026-11-14"
seed_source: ".raw/source-material/LOCAL-seo-Knowledge-Base.md"
seed_hash: "sha256:b9ad72ce8f09950826442f779bf3e3df4851cd13406b2841ab7d11b776f3b161"
---

# Structured Data Validation Review

> Draft prompt for [[schema-explanation|Schema Explanation]]. Use only authorized evidence and review the result before external use.

## Evidence status

- Assessment: **provisional**
- Confidence: **PRACTITIONER**
- Verified: **2026-10-15**
- Refresh due: **2026-11-14**
- Claim IDs: operator-evidence-review, truthful-firsthand-content, structured-data-vocabulary-distinction, structured-data-no-guarantee, own-business-review-markup-ineligible

## Task

Check JSON syntax, Schema.org vocabulary, the named Google feature requirements, and visible-page parity separately. Do not report a validator pass unless its result is supplied or actually observed.

## Required inputs

Draft JSON-LD, visible page content, property/evidence matrix, and actual validator outputs.

## Output and acceptance

Findings by validation layer, repaired Draft where supported, and checks still unverified.

Tie factual assertions to supplied source IDs and locators. Retain needs_input for missing facts. The operator reviews scope, factual support, and privacy; any proposed external change needs owner approval and rollback.

## Related

- [[wiki/prompts/_index|Prompts Hub]]
- [[Index]]

---
type: "prompt"
title: "Structured Data Draft"
parent: "Schema Explanation"
parent_folder: "frameworks"
created: "2026-10-15"
updated: "2026-10-15"
status: "active"
tags: ["type/prompt", "domain/local-seo", "evidence/provisional"]
claim_ids: ["operator-evidence-review", "truthful-firsthand-content", "structured-data-formats", "structured-data-no-guarantee", "own-business-review-markup-ineligible"]
assessment: "provisional"
confidence: "PRACTITIONER"
verified_at: "2026-10-15"
refresh_due: "2026-11-14"
seed_source: ".raw/source-material/LOCAL-seo-Knowledge-Base.md"
seed_hash: "sha256:b9ad72ce8f09950826442f779bf3e3df4851cd13406b2841ab7d11b776f3b161"
---

# Structured Data Draft

> Draft prompt for [[schema-explanation|Schema Explanation]]. Use only authorized evidence and review the result before external use.

## Evidence status

- Assessment: **provisional**
- Confidence: **PRACTITIONER**
- Verified: **2026-10-15**
- Refresh due: **2026-11-14**
- Claim IDs: operator-evidence-review, truthful-firsthand-content, structured-data-formats, structured-data-no-guarantee, own-business-review-markup-ineligible

## Task

Draft JSON-LD using only approved values. Keep entity identities consistent and omit unsupported optional properties. If required information is missing, explain the gap instead of producing apparently eligible markup.

## Required inputs

The approved property/evidence matrix and confirmed visible page content.

## Output and acceptance

Draft JSON-LD, property-to-visible-content mapping, and remaining validation tasks.

Tie factual assertions to supplied source IDs and locators. Retain needs_input for missing facts. The operator reviews scope, factual support, and privacy; any proposed external change needs owner approval and rollback.

## Related

- [[wiki/prompts/_index|Prompts Hub]]
- [[Index]]

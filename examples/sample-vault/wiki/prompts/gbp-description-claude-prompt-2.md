---
type: "prompt"
title: "Business Description Policy Review"
parent: "GBP Description"
parent_folder: "gbp"
created: "2026-10-15"
updated: "2026-10-15"
status: "active"
tags: ["type/prompt", "domain/local-seo", "evidence/provisional"]
claim_ids: ["operator-evidence-review", "truthful-firsthand-content", "gbp-truthful-fields", "gbp-name-and-categories"]
assessment: "provisional"
confidence: "PRACTITIONER"
verified_at: "2026-10-15"
refresh_due: "2026-11-14"
seed_source: ".raw/source-material/LOCAL-seo-Knowledge-Base.md"
seed_hash: "sha256:b9ad72ce8f09950826442f779bf3e3df4851cd13406b2841ab7d11b776f3b161"
---

# Business Description Policy Review

> Draft prompt for [[gbp-description|GBP Description]]. Use only authorized evidence and review the result before external use.

## Evidence status

- Assessment: **provisional**
- Confidence: **PRACTITIONER**
- Verified: **2026-10-15**
- Refresh due: **2026-11-14**
- Claim IDs: operator-evidence-review, truthful-firsthand-content, gbp-truthful-fields, gbp-name-and-categories

## Task

Check factual support, promotional or irrelevant material, and current field constraints. Measure text length if a verified limit is provided; otherwise mark that constraint unverified.

## Required inputs

Draft description, supporting business facts, and current applicable representation guidance.

## Output and acceptance

A compliance/edit table, revised Draft, and exact rules or limits still needing verification.

Tie factual assertions to supplied source IDs and locators. Retain needs_input for missing facts. The operator reviews scope, factual support, and privacy; any proposed external change needs owner approval and rollback.

## Related

- [[wiki/prompts/_index|Prompts Hub]]
- [[Index]]

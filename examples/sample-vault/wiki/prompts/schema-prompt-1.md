---
type: "prompt"
title: "Structured Data Workflow Entry Point"
parent: "Schema Explanation"
parent_folder: "frameworks"
created: "2026-10-15"
updated: "2026-10-15"
status: "active"
tags: ["type/prompt", "domain/local-seo", "evidence/provisional"]
claim_ids: ["operator-evidence-review", "truthful-firsthand-content", "structured-data-formats", "structured-data-vocabulary-distinction", "own-business-review-markup-ineligible"]
assessment: "provisional"
confidence: "PRACTITIONER"
verified_at: "2026-10-15"
refresh_due: "2026-11-14"
seed_source: ".raw/source-material/LOCAL-seo-Knowledge-Base.md"
seed_hash: "sha256:b9ad72ce8f09950826442f779bf3e3df4851cd13406b2841ab7d11b776f3b161"
---

# Structured Data Workflow Entry Point

> Draft prompt for [[schema-explanation|Schema Explanation]]. Use only authorized evidence and review the result before external use.

## Evidence status

- Assessment: **provisional**
- Confidence: **PRACTITIONER**
- Verified: **2026-10-15**
- Refresh due: **2026-11-14**
- Claim IDs: operator-evidence-review, truthful-firsthand-content, structured-data-formats, structured-data-vocabulary-distinction, own-business-review-markup-ineligible

## Task

Run [[claude-prompt-1|Structured Data Fact Intake]], then [[claude-prompt-2|Structured Data Draft]], then [[follow-up-prompt|Structured Data Validation Review]]. Stop at missing required evidence rather than fabricating eligibility.

## Required inputs

Visible page content, current markup, and intended search feature.

## Output and acceptance

The three linked review records: fact intake, markup Draft, and validation findings.

Tie factual assertions to supplied source IDs and locators. Retain needs_input for missing facts. The operator reviews scope, factual support, and privacy; any proposed external change needs owner approval and rollback.

## Related

- [[wiki/prompts/_index|Prompts Hub]]
- [[Index]]

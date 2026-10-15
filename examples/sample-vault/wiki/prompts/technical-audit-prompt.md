---
type: "prompt"
title: "Evidence-Based Technical Review"
parent: "Property Technical Audit"
parent_folder: "audits"
created: "2026-10-15"
updated: "2026-10-15"
status: "active"
tags: ["type/prompt", "domain/local-seo", "evidence/provisional"]
claim_ids: ["operator-evidence-review", "truthful-firsthand-content", "core-web-vitals-scoped", "product-no-fabricated-metrics"]
assessment: "provisional"
confidence: "PRACTITIONER"
verified_at: "2026-10-15"
refresh_due: "2026-11-14"
seed_source: ".raw/source-material/LOCAL-seo-Knowledge-Base.md"
seed_hash: "sha256:b9ad72ce8f09950826442f779bf3e3df4851cd13406b2841ab7d11b776f3b161"
---

# Evidence-Based Technical Review

> Draft prompt for [[property-technical-audit|Property Technical Audit]]. Use only authorized evidence and review the result before external use.

## Evidence status

- Assessment: **provisional**
- Confidence: **PRACTITIONER**
- Verified: **2026-10-15**
- Refresh due: **2026-11-14**
- Claim IDs: operator-evidence-review, truthful-firsthand-content, core-web-vitals-scoped, product-no-fabricated-metrics

## Task

Check only what the supplied evidence supports: access, indexing controls, canonical consistency, rendering observations, and measured user experience. Separate untested conditions from failures and avoid a mandatory report word count.

## Required inputs

Authorized crawl/indexing/performance reports, tested URLs, collection dates, and available response/markup evidence.

## Output and acceptance

Finding/evidence/scope/next-check table; actual validation results and explicitly skipped checks.

Tie factual assertions to supplied source IDs and locators. Retain needs_input for missing facts. The operator reviews scope, factual support, and privacy; any proposed external change needs owner approval and rollback.

## Related

- [[wiki/prompts/_index|Prompts Hub]]
- [[Index]]

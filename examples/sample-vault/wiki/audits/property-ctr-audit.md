---
type: "knowledge"
title: "Property CTR Audit"
folder: "audits"
created: "2026-10-15"
updated: "2026-10-15"
status: "active"
tags: ["type/knowledge", "domain/audits", "evidence/unsupported"]
claim_ids: ["behavior-formulas-unsupported", "operator-evidence-review"]
assessment: "unsupported"
confidence: "CONTESTED"
verified_at: "2026-10-15"
refresh_due: "2026-11-14"
seed_source: ".raw/source-material/LOCAL-seo-Knowledge-Base.md"
seed_hash: "sha256:b9ad72ce8f09950826442f779bf3e3df4851cd13406b2841ab7d11b776f3b161"
---

# Property CTR Audit

## Evidence status

- Assessment: **unsupported**
- Confidence: **CONTESTED**
- Verified: **2026-10-15**
- Refresh due: **2026-11-14**
- Claim IDs: behavior-formulas-unsupported, operator-evidence-review

## Working guidance

Compare impressions and clicks within the supplied report’s query, page, device, country, and date scope. Check title relevance; treat changes as observations rather than proof of a ranking mechanism.

## Use this note

Inputs: The click/impression export, its filters and date window, and the current page titles and descriptions.

Result: Comparable click and impression observations, snippet-relevance findings, and explicit limits on causal interpretation.

## Evidence and limits

Aggregated interaction data has been described in primary trial evidence, but this does not validate GA bounce-rate formulas, dwell-time thresholds, CTR manipulation, or local-ranking guarantees. (Claim: behavior-formulas-unsupported; contrary evidence: doj-google-interaction-testimony.)

## AI Prompts

- [[ctr-audit-prompt|Scoped Click-Through Review]]


## Related

- [[wiki/audits/_index|Audits Hub]]
- [[Claim Verification Flow]]

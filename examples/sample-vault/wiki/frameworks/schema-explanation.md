---
type: "knowledge"
title: "Schema Explanation"
folder: "frameworks"
created: "2026-10-15"
updated: "2026-10-15"
status: "active"
tags: ["type/knowledge", "domain/frameworks", "evidence/accepted"]
claim_ids: ["structured-data-formats", "structured-data-no-guarantee", "structured-data-vocabulary-distinction", "own-business-review-markup-ineligible", "operator-evidence-review", "review-markup-incentive-disclosure"]
assessment: "accepted"
confidence: "EVIDENCE-BASED"
verified_at: "2026-10-15"
refresh_due: "2026-11-14"
seed_source: ".raw/source-material/LOCAL-seo-Knowledge-Base.md"
seed_hash: "sha256:b9ad72ce8f09950826442f779bf3e3df4851cd13406b2841ab7d11b776f3b161"
---

# Schema Explanation

## Evidence status

- Assessment: **accepted**
- Confidence: **EVIDENCE-BASED**
- Verified: **2026-10-15**
- Refresh due: **2026-11-14**
- Claim IDs: structured-data-formats, structured-data-no-guarantee, structured-data-vocabulary-distinction, own-business-review-markup-ineligible, operator-evidence-review, review-markup-incentive-disclosure

## Working guidance

Select vocabulary that matches visible, supported page facts, then check the relevant Google feature requirements. Record separate syntax and eligibility results.

## Use this note

Inputs: Visible page facts, existing markup, candidate Schema.org types, and the specific Google feature requirements.

Result: A fact-to-property map or Draft markup, separate syntax/eligibility results, and unsupported properties left out.

## Evidence and limits

Google Search supports JSON-LD, Microdata, and RDFa for structured data; JSON-LD is recommended for maintainability but is not the only supported format. (Claim: structured-data-formats; sources: google-structured-data-guidelines, google-structured-data-intro.)

Valid structured data creates feature eligibility and can help understanding, but Google does not guarantee rich-result appearance or document a direct organic-rank or AI-citation lift. (Claim: structured-data-no-guarantee; sources: google-structured-data-guidelines, google-localbusiness-structured-data.)

Schema.org defines vocabulary and its validator checks vocabulary/syntax; Google documentation and the Rich Results Test govern Google feature eligibility. (Claim: structured-data-vocabulary-distinction; sources: schema-localbusiness, schema-validator, google-rich-results-test.)

Self-serving reviews on an entity's own LocalBusiness or Organization pages are ineligible for Google star review features; ratings must not be aggregated from other sites. (Claim: own-business-review-markup-ineligible; sources: google-localbusiness-structured-data, google-review-snippet.)

For Google Search review-snippet eligibility, fake or undisclosed incentivized reviews are prohibited; a provided benefit must be clearly and prominently disclosed. This does not relax Maps incentive prohibitions or guarantee rich results. (Claim: review-markup-incentive-disclosure; sources: google-review-snippet, google-maps-prohibited-content.)

## AI Prompts

- [[schema-prompt-1|Structured Data Workflow Entry Point]]
- [[follow-up-prompt|Structured Data Validation Review]]
- [[claude-prompt-1|Structured Data Fact Intake]]
- [[claude-prompt-2|Structured Data Draft]]


## Related

- [[wiki/frameworks/_index|Frameworks Hub]]
- [[Claim Verification Flow]]

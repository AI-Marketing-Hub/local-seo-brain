---
type: "workflow"
title: "Evidence Refresh Flow"
created: "2026-07-18"
updated: "2026-10-15"
status: "active"
tags: ["type/workflow", "domain/local-seo", "evidence/reviewed"]
claim_ids: ["operator-evidence-review", "product-deterministic-overlays"]
verified_at: "2026-10-15"
refresh_due: "2026-11-14"
---

# Evidence Refresh Flow

## Procedure

1. Evaluate the existing evidence snapshot against the actual review date using `evidence_contract.py freshness --as-of YYYY-MM-DD --format json`.
2. Inspect each controlling primary source and exact claim locator. Record changed, unchanged, superseded, or unavailable, plus the actual review date.
3. Reassess scope, contradictions, confidence, and missing inputs. Do not advance verification dates for an unavailable source.
4. Update canonical source and claim records, reconcile reverse links, and derive claim and overlay deadlines from their dependencies.
5. Generate in staging, inspect the hash-bound transaction, and verify the applied result with both lints and deterministic tests.

## Internal review intervals

Search status and documentation feeds: seven days. GBP API sources: 14 days. Other current doctrine: 30 days. These are maintenance choices, not Google requirements. At the deadline evidence is due for review.

## Related

- [[Claim Verification Flow]]
- [[research-pack-2026-local-seo|Local SEO Evidence Research Pack]]
- [[wiki/flows/_index|Flows Hub]]
- [[Hot]]

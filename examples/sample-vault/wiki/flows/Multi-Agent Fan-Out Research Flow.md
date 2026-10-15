---
type: "flow"
title: "Multi-Agent Fan-Out Research Flow"
created: "2026-07-18"
updated: "2026-07-18"
status: "active"
tags: ["domain/local-seo", "type/flow", "governance/research"]
---

# Multi-Agent Fan-Out Research Flow

## Trigger

Several independent, bounded source classes or file inventories can be researched in parallel.

## Prerequisites

The lead defines questions, exclusions, per-worker round/source budgets, stop conditions, output schema, and a read-only draft boundary. Only the lead may write shared repository or vault state.

## Steps

1. Partition work by non-overlapping topic or source authority.
2. Give each worker the exact scope, date, budget, and no-write rule.
3. Require URLs, titles, publishers, dates, locators, limitations, and contradictions.
4. Have the lead deduplicate sources by canonical URL and independence key.
5. Resolve policy versus empirical evidence without averaging contradictions away.
6. Update canonical ledgers and overlays through the lead only.

## Outputs

Bounded worker drafts, one deduplicated source map, claim dispositions, contradiction register, and a lead-owned transaction plan.

## Gates

Workers stay read-only; no invented dates or quotes; source budgets and stop conditions are respected; the lead validates every adopted claim.

## Failure modes

Stop a worker on repeated sources, inaccessible authority, scope drift, unverifiable metadata, or an attempted shared-state write.

## Rollback

Discard unadopted drafts. If lead-owned canonical state changed, use the repository patch or transaction recovery path appropriate to that state.

## Related

- [[Claim Verification Flow]]
- [[Context Compaction Routine]]
- [[research-pack-2026-local-seo|Local SEO Evidence Research Pack]]
- [[Source Intake Workflow]]
- [[Uncertainty Eval Policy]]
- [[Index]]

---
type: "flow"
title: "Claim Verification Flow"
created: "2026-07-18"
updated: "2026-07-18"
status: "active"
tags: ["domain/local-seo", "type/flow", "provenance/claims"]
---

# Claim Verification Flow

## Trigger

A material policy, product-status, empirical, recommendation, safety, quantitative, or volatile claim is added or refreshed.

## Prerequisites

Define the exact claim scope, research budget, exclusions, source classes, and stop conditions. Read the canonical ledgers and current policy-gap register.

## Steps

1. State one falsifiable claim with its locale, product, feature, query class, and date scope.
2. Classify it as policy, product status, empirical observation, recommendation, or historical material.
3. Prefer the controlling official source for policy and product status. Record the exact locator and verification date.
4. For empirical claims, record sample, query set, locale/device, collection window, method, limitations, sponsor, and independence key.
5. Require two independent active sources for a high-risk accepted empirical claim. A direct controlling policy statement may use one official source when no operational inference is added.
6. Record contradictions rather than averaging them away.
7. Assign `accepted`, `provisional`, `contested`, `unsupported`, or `deprecated` plus a confidence label.
8. Set `verified_at` and `refresh_due`; stale evidence cannot remain active.
9. Update canonical ledgers and overlays, regenerate in staging, check drift, and apply a reviewed transaction.

## Outputs

Updated source and claim records, contradiction disposition, coverage entry, overlay change when generated content is affected, and a cited vault projection.

## Gates

High-risk empirical independence, official policy authority, referential integrity, freshness, projection drift, and both vault lints must pass.

## Failure modes

Stop on unsupported dates or quotes, stale evidence, conflicting transaction hashes, missing source rights, insufficient independence, or an unscoped universal conclusion.

## Rollback

Do not overwrite the last valid ledger or canonical vault. Revert the staged draft, preserve the evidence and error, and rebuild a new transaction from current hashes.

## Stop conditions

Stop when the claim is adequately scoped and evidenced, the search budget is exhausted, or additional sources repeat the same evidence. Never invent dates, quotes, weights, page numbers, or feature status.

## Related

- [[CONVENTIONS|Evidence and Vault Conventions]]
- [[Claim Ledger]]
- [[research-pack-2026-local-seo|Local SEO Evidence Research Pack]]
- [[Index]]

---
type: "flow"
title: "GBP Review Workflow"
created: "2026-07-18"
updated: "2026-07-18"
status: "active"
tags: ["domain/local-seo", "type/flow", "domain/flows"]
---

# GBP Review Workflow

This is a read-only review workflow. It does not mutate a Business Profile.

## Preconditions

- Confirm the real-world business name and whether customers are served at the address.
- Read [[gbp-overview|GBP Overview]], [[gbp-verification|GBP Verification]], and [[2026-gbp-changes|Current GBP Doctrine]].
- Keep an authorized performance CSV outside the repository until ingest.

## Ingest

```bash
python3 scripts/ingest_gbp.py \
  --vault /absolute/client-vault --client CLIENT_SLUG \
  --file /absolute/gbp.csv --as-of YYYY-MM-DD --dry-run
```

The adapter records provenance and structural CSV metadata. It does not calculate a performance trend or identify a ranking cause.

## Review

1. Verify eligibility, address visibility, service area, name, category, hours, and verification guidance against active claim IDs.
2. Treat category selection as a factual representation decision; no universal category weight or quota is documented.
3. Treat posts, photos, services, and replies as customer-information activities; no universal ranking cadence or deadline is documented.
4. Do not claim EXIF/GPS metadata causes ranking gains.
5. Put every proposed profile change in [[Approval Queue]] with owner approval and rollback.

## Refuse

No virtual-office abuse, borrowed address, staged signage or verification evidence, sensitive identity documents in video, fake or gated reviews, keyword-stuffed name, or ranking guarantee.

## Related

- [[Claim Verification Flow]]
- [[wiki/gbp/_index|GBP Hub]]
- Approval Queue
- [[Index]]

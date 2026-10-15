---
type: "source"
title: "Reviews Export (2026-10-15)"
created: "2026-10-15"
updated: "2026-10-15"
status: "imported"
tags: ["type/source", "domain/reviews", "provenance/raw"]
source_kind: "review-export"
source_path: ".raw/clients/sample-vault/reviews/2026-10-15-2facece74728-sample-reviews.json"
source_hash: "sha256:2facece74728b252eaf1e4f006a8b123519dc24ad5ed5a874c0ac556163eaf59"
location: "sample-vault"
---

# Reviews Export (2026-10-15)

## Source

- Path: `.raw/clients/sample-vault/reviews/2026-10-15-2facece74728-sample-reviews.json`
- SHA-256: `2facece74728b252eaf1e4f006a8b123519dc24ad5ed5a874c0ac556163eaf59`
- Retrieved: 2026-10-15

## Compiled Truth

- Reviews ingested: 8
- Average rating: 4.50
- Date range: 2026-03-22 → 2026-05-01

## Refusal

- Derived notes omit reviewer names and store no per-review identity.
- The immutable raw export may contain personal data supplied by the operator;
  keep the client vault access-controlled and follow the retention policy.
- No fake-review generation.
- No review gating recommendations.

## Related

- [[sample-vault]]
- [[wiki/reviews/_index|Reviews Hub]]

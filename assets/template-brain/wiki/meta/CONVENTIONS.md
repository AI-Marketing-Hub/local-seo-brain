---
type: "meta"
title: "Evidence and Vault Conventions"
created: "2026-07-18"
updated: "2026-07-18"
status: "active"
tags: ["domain/local-seo", "type/meta", "provenance/claims"]
---

# Evidence and Vault Conventions

## Authority order

Official policy controls policy claims. Official product documentation controls feature and API status. Independent research supports only the measured scope it documents. Practitioner guidance remains labeled and does not override policy.

## Claim states

- `accepted`: supported within its stated scope
- `provisional`: useful but incomplete or context-dependent
- `contested`: credible evidence conflicts or the operational interpretation is unresolved
- `unsupported`: reviewed evidence does not establish the claim
- `deprecated`: historical material retained only for provenance

Confidence labels are `EVIDENCE-BASED`, `PRACTITIONER`, `CONTESTED`, and `FOLKLORE`. Confidence never replaces a source or assessment.

## Dates and missing data

Pin every operation to an ISO `--as-of` date. Unknown values remain `null`, `no_data`, `needs_input`, or `unsupported`. Never infer a publication date, metric, score, feature status, or completed action.

## Generated content

Generated chapters and prompts are owned by the historical seed, `data/knowledge-overlays.json`, and the generator. Durable corrections belong in the overlay. Template-vault changes use a reviewed, hash-bound transaction.

Every Markdown note requires YAML frontmatter and resolvable Obsidian wikilinks. A note must be linked from an active index or MOC in the same transaction that creates it.

## Privacy and action

Client raw exports remain access-controlled. Derived review notes omit reviewer identity. The product is read-only for external systems. Account-touching proposals require an [[Approval Queue]] record with source, owner, risk, and rollback.

## Publish and release

The vault is private by default. Public packaging must exclude `.raw/`, private ledgers, local paths, client data, reviewer identity, and transaction records. A clean lint or version number does not authorize a publish, push, tag, or release.

## Related

- [[Claim Ledger]]
- [[Claim Verification Flow]]
- [[research-pack-2026-local-seo|Local SEO Evidence Research Pack]]
- [[Index]]

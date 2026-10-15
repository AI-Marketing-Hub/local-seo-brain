# Safety Gates

Verified: 2026-10-15. Review before every release and whenever controlling policy changes.

## External systems

All external platforms are read-only. No live Google Business Profile, Search Console, GA4, Maps, Places, citation directory, review platform, publishing system, or client-account mutation is permitted. No paid API call is permitted in this release.

## Credentials and privacy

No credentials, tokens, cookies, private client data, or review-author PII may enter repository artifacts. Derived review notes omit reviewer identities. If private data appears, stop, remove it from derived outputs, preserve the incident record without the sensitive value, and rotate credentials outside the repository when applicable.

## Local SEO policy refusals

Reject address gaming, virtual offices presented as real storefronts, ineligible co-working locations, fake or incentivized reviews, review gating, competitor manipulation, PBN tactics, doorway pages, hidden text, mass low-quality citations, prohibited Places storage, and guaranteed ranking language.

## Evidence and product truth

Every material claim cites a canonical source record and locator. High-risk accepted empirical claims require two independent active sources. Unknown means `null`, `unsupported`, `no_data`, or `needs_input`. No score, grade, traffic share, ranking weight, cadence, deadline, update cause, feature status, test result, or maturity claim may be invented.

## Approval and rollback

Recommendations that would affect an account require explicit owner approval and a documented rollback. The repository may prepare an approval record but may not execute the external change.

## Repository mutations

Preserve historical `.raw/` inputs byte-for-byte. Use deterministic overlays for generated-note corrections. Canonical vault changes require expected SHA-256 hashes, transaction inspection, exact allowed paths, and apply with the inspection approval hash. Deletions, out-of-scope writes, unresolved conflicts, push, PR, tag, release, or publishing require a separate user checkpoint.

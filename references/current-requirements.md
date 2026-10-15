# Current Local SEO Requirements

Verified: 2026-10-15. Retrieval date for every linked source record: 2026-10-15.

This is the operating doctrine distilled from the canonical source and claim ledgers. It separates controlling platform policy from empirical evidence and practitioner judgment. Exact claim wording, locators, scopes, contradictions, and refresh dates live in `references/claim-ledger.json`.

## Google Search

- Build crawlable, people-first pages that satisfy a real audience need. Google publishes no preferred word count, keyword density, page count, publishing cadence, or ideal link count.
- Link-analysis systems, including evolved PageRank, are only part of Google’s systems. Do not use fixed authority-point arithmetic, anchor ratios, placement weights, or guarantees.
- Reject hidden text used for manipulation, doorway pages, scaled low-value pages, PBNs, paid ranking links without qualification, and automated forum/comment links. Ordinary user-facing accordions and tabs are allowed.
- Treat Core Web Vitals as user-experience diagnostics, not a ranking guarantee or a special local-ranking weight.
- Valid structured data can create feature eligibility and help understanding. Google supports JSON-LD, Microdata, and RDFa. Schema.org vocabulary, Google feature eligibility, and Search ranking are separate concerns.
- Do not add self-serving LocalBusiness or Organization review markup as a star-result tactic. Do not aggregate ratings copied from other platforms.
- FAQ rich results stopped appearing in Google Search on 2026-05-07. Do not sell FAQ or HowTo markup as a current ordinary rich-result or AI-growth mechanism.

## Google AI features

- Ordinary Search eligibility, indexability, snippet controls, visible content, and matching structured data remain the documented requirements. Google documents no special AIO schema stack, AI text file, or guaranteed optimization tactic.
- Search Console’s generative-AI impression report is documented as available worldwide from 2026-08-31. Do not infer dedicated click or conversion reporting that is not documented.
- Two independent observational datasets support only the directional conclusion that AI-summary pages are associated with fewer external-result clicks. Do not generalize a single percentage.
- Fixed citation counts, Reddit citation shares, mandatory community activity, and universal GEO recipes are unsupported. Record platform, locale, query set, device, collection window, method, and limitations for every measurement.

## Google Business Profile and Maps

- Use the real-world business name and the fewest accurate categories needed to describe the core business. There is no official category quota or public category weight.
- A service-area business that does not serve customers at its address should remove or hide it. Virtual offices are ineligible. A coworking storefront requires permanent signage, customer reception, and the business’s own staff during stated hours.
- Verification methods are selected by Google and vary by profile. Evidence must be authentic. A verification video must be live, unique, unedited, and free of faces, identity documents, and other sensitive information. Never stage signage or conceal another identity.
- Google’s public local-ranking frame is relevance, distance, and prominence/popularity. Google publishes no weights, thresholds, cadence, decay formula, or guaranteed lift.
- Reviews must reflect genuine, unbiased experiences. Fake, paid, incentivized, gated, quota-driven, conflict-of-interest, competitor, or wording-manipulated reviews are prohibited.
- Official post documentation covers formats, moderation, scheduling, recurrence, and archiving; it does not establish a twice-weekly ranking requirement, a 30-day visibility cliff, or a universal photo cadence.
- The My Business Q&A API was discontinued on 2025-11-03. That does not prove consumer place Q&A disappeared everywhere or that Ask Maps replaced it across locales, devices, accounts, and categories.
- Places content has attribution, caching, storage, and license restrictions. Authorized Business Profile exports and public Places competitor discovery are different data boundaries.

## Product boundary

- Local SEO Brain is advisory. It ingests authorized exports, stores immutable raw receipts, and drafts evidence-linked recommendations.
- Any profile, account, control, publishing, outreach, listing, or third-party mutation requires explicit owner approval, a scoped plan, and a rollback path.
- Missing data produces `Draft`, `no data`, or a grounded refusal. It never produces a fabricated score, grade, metric, cause, result, or completed action.
- Derived review notes omit author identity. Authorized raw exports remain access-controlled and are not copied into public deliverables.

## Current additions

- Accurate authorship, evidence, and experience support reader trust; E-E-A-T is not a specific ranking factor. Claim: eeat-trust-context.
- Titles and descriptions should be accurate and page-specific; Google can choose page content for a snippet. Claim: metadata-accurate-descriptive.
- Descriptions, services, and hours must reflect confirmed business operations. Claim: gbp-truthful-fields.

- Review markup in Google Search prohibits fake and undisclosed incentivized reviews. Any benefit requires clear, prominent disclosure. Maps separately prohibits incentives themselves, including disclosed incentives. Sources: google-review-snippet, google-maps-prohibited-content. Claim: review-markup-incentive-disclosure.
- EEA local-business aggregator and supplier units have region-specific participation requirements. Supplier units appear alongside aggregator units; these are not universal Map Pack rules. Claim: eea-local-business-search-units.
- Site-reputation manual-action effects differ inside and outside the EEA from 2026-08-30. This is an enforcement distinction, not permission to create spam. Claim: eea-site-reputation-enforcement.
- AI-assisted content needs original user value and human verification of content and metadata. Claim: generative-ai-content-quality.
- My Business API v4.9 documents reviewReplyUrl retrieval from 2026-07-24 and food-menu GLUTEN_FREE / DAIRY_FREE values from 2026-10-09. These are documented API capabilities, not Local SEO Brain integrations. Claims: gbp-api-review-reply-url, gbp-api-food-menu-dietary-restrictions.
- The official ranking history includes August and September 2026 spam updates. Dates establish events, not a site's ranking cause. Claim: search-update-events.
- Operators separate observed facts, hypotheses, missing inputs, and proposed changes in a source-cited Draft. Claim: operator-evidence-review.

## Refresh triggers

Use references/freshness-policy.json: seven days for Search status/documentation feeds, 14 days for GBP API sources, and 30 days for other current doctrine. These are internal review intervals. Evaluate existing snapshots against the actual review date with evidence_contract.py freshness. Do not advance verification dates without inspecting the source.

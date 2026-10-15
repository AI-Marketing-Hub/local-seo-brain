# Publishing Notice

## Rights boundary

Local SEO Brain is open source under the MIT license in `LICENSE`. The license covers the code, the authored guide chapters and prompts, the evidence ledgers, the generated template and sample vaults, and the project visuals. Third-party documentation, trademarks, and the operator-supplied historical course bundle retain their own rights and are described in `THIRD_PARTY_NOTICES.md`.

## What can be public

Everything in this repository is published under the MIT license. Source links, compliant brief excerpts, generated sample data, deterministic test evidence, and sanitized summaries may be quoted and reused. A source citation does not grant republication rights over the cited source.

## What must stay private

The historical course bundle under `.raw/source-material/` (the Markdown, DOCX, and ZIP exports and the images extracted from them), credentials, private client exports, review-author identity, approval records containing client details, local filesystem paths, and unreviewed research dossiers stay out of the repository. `.gitignore` excludes `.raw/source-material/` and `.raw/secrets/`; the repository safety scan checks every tracked and nonignored input before a release.

The canonical ledgers `references/source-ledger.json` and `references/claim-ledger.json` are published. They hold the source evidence boundary of the product: public source locators, dates, and claim dispositions only. Never add client data, credentials, or private paths to them.

This notice does not authorize a push, pull request, tag, release, site deployment, or external account mutation. Those actions require separate user authority and a clean market-ready gate report.

# Repository Instructions

Local SEO Brain is an advisory, source-cited, approval-first knowledge system. Read this file, `SKILL.md`, `docs/PRODUCT_BOUNDARIES.md`, and the target vault's `CODEX.md` before changing repository or vault state.

## Read order

1. Inspect Git status and preserve unrelated work.
2. Read `specs/local-seo-brain.yaml` and `references/safety-gates.md`.
3. Read `assets/template-brain/CODEX.md`, `wiki/hot.md`, and `wiki/index.md`.
4. Read the canonical source and claim ledgers before changing evidence-bearing content.
5. Read generator ownership in `references/REPOSITORY_OWNERSHIP.md` before editing generated notes or the sample vault.

## Boundaries

- External systems are read-only. Do not mutate Google Business Profile, Search Console, GA4, Maps, Places, citation, review, or client accounts.
- No credentials, tokens, cookies, private client data, or review-author PII in repository artifacts.
- Preserve `.raw/` inputs byte-for-byte. Never rewrite historical evidence to make it appear current.
- Unknown values stay `null`, `unsupported`, `no_data`, or `needs_input`.
- Never invent sources, dates, quotations, rankings, traffic, weights, scores, cadences, tests, or maturity.
- Every account-touching recommendation requires owner approval and a rollback note.

## Write discipline

- The lead agent is the only repository writer. Research workers are read-only and draft-only.
- Root code, schemas, ledgers, and docs use reviewed repository patches.
- Canonical writes under `assets/template-brain/wiki/` use a hash-bound Claude Obsidian transaction after inspection.
- Generated knowledge notes are fixed through `data/knowledge-overlays.json` and the build pipeline, never by durable one-off edits.
- `examples/sample-vault/` is generated only. Tests write to temporary directories.
- Use explicit `--vault`, `--out-dir`, `--as-of`, and `--dry-run` options for mutating commands.

## Required verification

Run the full commands in `RELEASE_CHECKLIST.md`. At minimum require repository lint, strict Claude Obsidian lint, all contract tests, deterministic build hashes, Brainstein audit and next-action JSON, `git diff --check`, and secret/PII scans.

Local commits are allowed on `codex/` branches. Push, pull request, tag, release, publishing, deletion of canonical pages, or live-account mutation requires separate user authority.

# Historical verification snapshot, 2026-07-18

This record describes the July reviewed tree only. It is not current freshness or release evidence. See VERIFICATION_REPORT_2026-10-15.md for this maintenance review.

# Local SEO Brain refresh verification

- As of: **2026-07-18**
- Branch: `codex/local-seo-brain-evidence-refresh-2026`
- Baseline and `origin/main`: `248db4dc0fc2f43158eb637c098254040687ec74`
- Release status: **VERIFIED — every acceptance gate passes, and the user authorized a direct fast-forward update of `main`. No pull request, tag, release, package, deployment, or live-account mutation was authorized.**

## Delivered state

- Product version is consistently `0.3.0`; Python support is consistently `>=3.11`.
- The three historical seed files match `references/historical-seed.sha256`. (Update, 2026-10-15: the third-party bundle was withdrawn from the public tree before the MIT release; the contract now verifies present files and tolerates the absent bundle. See `THIRD_PARTY_NOTICES.md`.)
- The evidence corpus contains 66 active sources: 56 official-authority and 10 primary-authority sources; 55 are official Google sources. There are no contested or deprecated source records and no stale active records.
- The claim ledger contains 39 dispositions: 29 accepted, six unsupported, two provisional, one contested, and one deprecated. It contains 23 high-risk claims, five deliberately uncited high-risk unsupported claims, and zero uncited accepted high-risk claims. The one accepted high-risk empirical claim has two independent sources.
- Deterministic overlays cover all 59 chapter notes and 37 prompt notes. The coverage projection also includes six freshness notes, eight public-document surfaces, and 14 script surfaces.
- The canonical vault contains 161 linted pages and 1,347 resolved links. The strict Claude Obsidian lint and repository lint both report zero findings.
- The checked-in sample vault regenerates deterministically from template and fixtures.

## Lint comparison

| Gate | Baseline | Final | Delta |
|---|---:|---:|---:|
| Repository lint findings | 0 | 0 | 0 |
| Claude Obsidian findings | 144 | 0 | -144 |
| Claude Obsidian pages | 144 | 161 | +17 |
| Claude Obsidian links | 1,287 | 1,347 | +60 |

## Evidence inventory

### Sources

| Dimension | Count |
|---|---:|
| Total / active | 66 / 66 |
| Contested / deprecated / stale | 0 / 0 / 0 |
| Official authority / primary authority | 56 / 10 |
| Official Google | 55 |
| `official-doc` | 50 |
| `first-party-blog` | 7 |
| `primary-research` | 5 |
| `standard` | 3 |
| `independent-study` | 1 |

### Claims

| Dimension | Count |
|---|---:|
| Total | 39 |
| Accepted / provisional / contested | 29 / 2 / 1 |
| Unsupported / deprecated | 6 / 1 |
| `EVIDENCE-BASED` / `PRACTITIONER` | 30 / 1 |
| `CONTESTED` / `FOLKLORE` | 2 / 6 |
| High / medium / low risk | 23 / 15 / 1 |
| Uncited high-risk | 5 |
| Uncited accepted high-risk | 0 |

The five uncited high-risk claims are deliberately `unsupported`; absence of adequate evidence is their disposition, not an evidence omission. The one accepted high-risk empirical claim uses two active sources with different independence keys.

## Deterministic receipts

- Canonical template tree SHA-256: `bdf8309952d4500a40dee4cae2942233f58d4b628719fbef76265c16172bb8d7`
- Sample vault tree SHA-256: `0ca419a8fbbcd5ee6448b5c198e7dc32425a412088d7597eaf78b8371a4f9be2`
- Historical DOCX: `6e91f9a329ed87fa121a6f98703dd5de679038d29a3f41c37c7743ad4348d785`
- Historical Markdown: `b9ad72ce8f09950826442f779bf3e3df4851cd13406b2841ab7d11b776f3b161`
- Historical ZIP: `27120fa1281605db58b9241b59a1e7897cf12b6a0854258d2a80ffdb065e2579`

## Official doctrine materially incorporated

- Search Status events are recorded from the March 2024 core/spam updates through the June 2026 spam update. Dates prove rollout only; they do not assign causal mechanisms.
- Google AI Overviews and AI Mode retain ordinary Search eligibility and policy requirements, with no mandatory special schema, AI text file, Reddit activity, or citation formula.
- Search Console's June 2026 generative-AI reporting is treated as a staged, impression-oriented surface; undocumented click or conversion fields are not inferred.
- GBP guidance now enforces real-world names, minimal accurate categories, hidden addresses for non-storefront service-area businesses, virtual-office ineligibility, coworking storefront conditions, authentic verification, and fake/review-gating prohibitions.
- The My Business Q&A API's 2025-11-03 discontinuation is separated from consumer place Q&A and the scoped March 2026 Ask Maps rollout.
- Places attribution, storage, caching, licensing, and authorized-export boundaries are explicit.
- JSON-LD, Microdata, and RDFa are correctly separated from schema.org vocabulary and Google feature eligibility; self-serving review markup, FAQ rich-result status, direct ranking lifts, and AI-citation causality are constrained.
- Core Web Vitals use LCP, INP, and CLS as page-experience diagnostics without a fabricated local-ranking weight.

## Claim disposition summary

- Removed or marked unsupported: fixed ranking/category weights, 60–70% Map Pack traffic, mandatory post/photo/reply cadence, EXIF ranking gains, PageRank arithmetic, fixed AI citation/share formulas, schema-to-ranking/AIO causality, and update-winner mechanisms.
- Qualified: local ranking as relevance/distance/prominence without weights; Core Web Vitals without guarantees; structured data as eligibility; AI-summary click direction as observational; review-demand research to its historical sample; and all geo-grid output as descriptive rather than causal.
- Contested: the claim that GBP Q&A disappeared universally or that Ask Maps replaced it everywhere.
- Retained as practitioner guidance: bounded GEO experiments only, with platform/query/date scope and no universal recipe.
- Deprecated behind the historical boundary: unsafe SAB/address and verification advice, PBN/link manipulation, JSON-LD-only and own-business rating defaults, FAQ/HowTo growth claims, LSI/bounce/dwell doctrine, fake anecdotes, and fabricated community identities.

## Verification gates

The following all exit zero:

- Ten regression programs: pipeline, domain ingestors, reseed preservation, citation contract, demo determinism, CLI safety, privacy/refusals, version consistency, documentation claims, and scaffold compatibility.
- Historical seed, version, evidence validation, evidence projection, coverage matrix, and exact change-manifest contracts.
- Repository vault lint, strict Claude Obsidian lint, and `git diff --check`.
- The repository-local Brainstein wrapper in report-only mode.

Safety scans found zero AWS, GitHub, OpenAI project/service-account, Anthropic, Google, or private-key signatures; zero local private absolute paths; and zero modified tracked binaries. The 16 new binary files are the expected deterministic sample-vault JPEG diagram projections already inventoried by the third-party notice. Review-derived notes omit author identity; raw fixture data remains under the documented access-control boundary.

## Exact command and exit evidence

All commands ran from the repository root. `PYTHONDONTWRITEBYTECODE=1` was set for Python verification commands.

| Command | Exit |
|---|---:|
| `python3 tests/test_pipeline.py` | 0 |
| `python3 tests/test_domain_ingestors.py` | 0 |
| `python3 tests/test_reseed_preserves_overlays.py` | 0 |
| `python3 tests/test_citation_contract.py` | 0 |
| `python3 tests/test_demo_determinism.py` | 0 |
| `python3 tests/test_cli_safety.py` | 0 |
| `python3 tests/test_privacy_and_refusals.py` | 0 |
| `python3 tests/test_version_consistency.py` | 0 |
| `python3 tests/test_documentation_claims.py` | 0 |
| `python3 tests/test_scaffold.py` | 0 |
| `python3 scripts/historical_seed_contract.py` | 0 |
| `python3 scripts/version_contract.py` | 0 |
| `python3 scripts/evidence_contract.py validate --as-of 2026-07-18` | 0 |
| `python3 scripts/evidence_contract.py check --as-of 2026-07-18 --vault assets/template-brain` | 0 |
| `python3 scripts/coverage_matrix.py check` | 0 |
| `python3 scripts/change_manifest.py --base 248db4dc0fc2f43158eb637c098254040687ec74 --out docs/VERIFIED_CHANGE_MANIFEST.md --check` | 0 |
| `python3 scripts/repository_safety_scan.py --base 248db4dc0fc2f43158eb637c098254040687ec74` | 0 |
| `python3 scripts/lint_vault.py --vault assets/template-brain` | 0 |
| `python3 ../../Skills/Private/claude-obsidian/scripts/claude-obsidian.py lint --vault assets/template-brain --format markdown --strict` | 0 |
| `git diff --check 248db4dc0fc2f43158eb637c098254040687ec74..HEAD` | 0 |
| `PYTHONPATH=../Brainstein-local-seo-compat python3 scripts/audit_brain.py --json --report-only` | 0 |
| `PYTHONPATH=../Brainstein-local-seo-compat python3 -m brainstein audit-brain . --json` | 0 |
| `PYTHONPATH=../Brainstein-local-seo-compat python3 -m brainstein next . --json --limit 10` | 0 |
| `python3 scripts/brainstein_gate.py /tmp/local-seo-brain-final-audit-20260718.json` | 0 |

## Brainstein compatibility repair and final audit

Installed Brainstein reports CLI `1.1.1`, editable distribution metadata `1.2.0`, from checkout commit `32b14a2e35819ae4c0dec9278a3dd3cd2df8dff1`. Claude Obsidian reports `2.0.0`.

| Brainstein anatomy | Baseline | Pre-repair refresh | Verified final |
|---|---:|---:|---:|
| Spec | 2 | 6 | 6 |
| Sources | 0 | 8 | 10 |
| Adapters | 4 | 9 | 9 |
| Vault | 8 | 12 | 12 |
| Demo | 2 | 9 | 9 |
| Release | 0 | 10 | 11 |
| Brand | 1 | 10 | 10 |
| Substance | 3 | 30 | 33 |
| Uncapped total | 20 | 94 | 100 |

The authorized Brainstein repair was isolated in the sibling `Brainstein-local-seo-compat` worktree on branch `codex/brainstein-evidence-ledger-compat`. Commit `4931342f49143ba9e0c187944621e7fab40034ff` repairs the evidence contract; commit `266ef782326d8e2d755dd2c4fba4124ab3b446ec` makes script validation read-only. The original checkout and its unrelated `.obsidian/` and `specs/velorn-video-workflow-brain.yaml` files were preserved unchanged.

The repair:

- accepts the current source vocabulary and `supports_claims` while retaining legacy `source_type` and `claims` compatibility;
- permits empty claim lists on canon-only sources while still requiring mapped claim coverage at ledger level;
- counts explicit `authority` when evaluating official/primary coverage;
- resolves research packs through configured wiki roots;
- respects a spec-declared private publish surface instead of requiring an unauthorized Quartz site;
- tightens OpenAI-key detection so Google's `sk-maps-immersive-navigation` URL is not a false credential while real legacy, project, and service-account key shapes remain blocked;
- propagates the contract into newly generated brains, refreshes the deterministic sample, and adds regression coverage.
- compiles audited scripts in memory so validation cannot create repository-local bytecode caches.

Brainstein's compile, 29-check test harness, strict generated-sample validation, self-brain lint, and self-brain market-ready audit all exit zero. Applied to Local SEO Brain, all 51 anatomy checks pass: total and uncapped score `100`, grade `SSS+`, maturity `market-ready`, `market_ready: true`, zero critical failures, and zero warnings. `brainstein next` returns an empty action list, the repository release gate passes, and the audit leaves no `__pycache__` behind.

The original Brainstein `main` checkout remains at the same commit as remote `main` (`32b14a2e35819ae4c0dec9278a3dd3cd2df8dff1`). The compatibility repair is a local commit only; it was not pushed or released.

Until that upstream repair is separately authorized for publication, CI checks out the pinned baseline and applies the reviewed zero-context runtime compatibility patch at `patches/brainstein-evidence-ledger-compat.patch` before installation. Its SHA-256 is `4014b0c7a3ea1149e64884575dfadf3d07cbc650f6f61d3bd835776be72e95e8`; `git apply --check --unidiff-zero` against the pinned baseline passes. This keeps the CI result reproducible without weakening the Local SEO evidence contract or depending on an unpublished branch.

## Repository and remote status

Logical implementation commits before this privacy-safe publication receipt:

| Commit | Purpose |
|---|---|
| `8b5c7a0fa23d5f98ab6f2229ce0e79b066caa93f` | Evidence-led v0.3 governance contracts |
| `51e8b8ebc41999ec1f31ac65b777d76faaf0041d` | Deterministic generators and release gates |
| `5b9fb0ab9eca82416e710748d95623294e7bf3d4` | Canonical Obsidian evidence vault |
| `da3b5b4f4ba350f940a1d78b051cbf7cc38cd130` | Deterministic sample vault |
| `e851d9dc174e33a5efe224d69b4a604155acff1c` | Initial verification receipts |
| `6a3dec3a3d47a6bbf2ff2f6606f0e75bf1d809b2` | Complete acceptance audit trail |
| `74b833fe8d9aa37543e83345474ffad791b22cb5` | Verified Brainstein compatibility integration |

GitHub's email-privacy gate rejected the first push before any remote update. The unpublished commits were then rewritten to use `223140489+AgriciDaniel@users.noreply.github.com`; a local backup branch preserves the original objects. At the final pre-push check, `origin/main` remained at the baseline and was an ancestor of this branch. The publication-receipt commit hash is supplied by the handoff response to avoid a self-referential file hash. No pull request, tag, release, package, deployment, or live-account mutation occurred.

## Canonical vault transactions

All eight authorized Claude Obsidian transactions are complete and hash-bound:

| Operation | Type | Paths | Approval SHA-256 | Expanded bundle SHA-256 |
|---|---|---:|---|---|
| `local-seo-research-20260718` | autoresearch | 8 | `306d998e78eceebb6b189a548f88e6e8931e812a1500fc5ee4c18fd63f508927` | `fd466560e7f96b88e511565f126bcc8ef8661efde41d20297362d1a9250093f4` |
| `local-seo-doctrine-20260718` | save | 140 | `a912167fcee8179f5005acd52e951e4894900c48afb4c5a7278e454fa8bf2287` | `b346ef1ed4fe169e5a37f3af4be8f8245d2ef34ab04471075213af2403a60289` |
| `local-seo-vault-metadata-20260718` | migration | 2 | `60b9eb70d7db7c21c3eea83326812f96560607cbc86c3ce721870013e75595bb` | `91409e9916edc0a7b37d407223874402e8f74ce8077e2a809f88fd4cc1fa0caf` |
| `local-seo-operator-workflows-20260718` | save | 19 | `5e95c7b21a370d6c453766e80ea12ada9cc005ab9049f5263e564f444c105915` | `74963892942cddc19bfc8ed69b81a1cc39506b012ca8e86a0e60ffdeabe5f5f4` |
| `local-seo-evidence-index-refresh-20260718` | autoresearch | 2 | `a64a370cf80f20a6a1f9e36ea56d4893a28ba43d81068e01b15107a0e7d4e394` | `878fc4ffc9b4cfbd86f5ccb5aca712ad5cf2a349d1de2a3be8e3bdc1731653f9` |
| `local-seo-governance-depth-20260718` | save | 15 | `d8f13eb64e7ccf04ff7d7516f5ba912148e5cb026ee4400e778e525e88860284` | `e497cab08ef04897341dbffcb16d5fd489181d5b629e883bb8f4c666f0125c88` |
| `local-seo-governance-index-20260718` | autoresearch | 1 | `547350ccbd348d89eff25ccbd6b9f0cbe54e06a9b464924b945c535447a388bd` | `e24c4f63932f7cd010d533cf0541e162d0e33872e98e098ae12143f2f4094b58` |
| `local-seo-graph-density-20260718` | save | 14 | `770880392c4a8b1608bad235a99952cfca8266d016dabafde35e5839b8fadf81` | `9dc679da6da75d28cc56a312edeb34e0caabf1cae764b465c18975f1d767c5fa` |

The exact 706-path change list, grouped by governance, evidence, generator, wiki, tests, docs, and sample status, is in `docs/VERIFIED_CHANGE_MANIFEST.md`.

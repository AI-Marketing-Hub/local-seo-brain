# Changelog

## Unreleased changes since 0.3.0, 2026-10-15

### Changed

- Rewrote `README.md` in plain language for local business owners and agencies. The technical content moved unchanged into a collapsed "For engineers and contributors" section.
- Added original light and dark README visuals under `assets/svg/` (map pack, how it works, refusals) with provenance in `assets/NOTICE.md`.
- Replaced the SSH clone line in the README with the HTTPS URL.
- Relicensed the project under the MIT license. `LICENSE` is now the MIT text, `marketplace.json` and `specs/local-seo-brain.yaml` say MIT, and the README, `PUBLISHING_NOTICE.md`, `THIRD_PARTY_NOTICES.md`, and `SUPPORT.md` describe the open source terms and point to the AI Marketing Hub Pro community for the deeper dive.
- `scripts/historical_seed_contract.py` tolerates an absent operator-supplied bundle, still fails on a present file that drifts, and gains `--render-outline`. `scripts/freshness.py` derives expected overlay note IDs from the committed outline when the bundle is absent and checks the bundle against the outline when present.
- `scripts/repository_safety_scan.py` recognizes reviewed, hash-bound asset withdrawals recorded in `references/asset-retention.json`.
- Regenerated `examples/sample-vault` and its receipt without the bundle.

### Added

- `references/historical-seed-outline.json`: the 96 generated note IDs and the seed hash, with no seed text.

### Removed

- The third-party historical course bundle (`.raw/source-material/` in the template vault, the sample vault, and the test fixtures). It is now gitignored and operator-supplied. The committed generated notes do not depend on it.

## Maintenance review, 2026-10-15 (version 0.3.0 retained)

- Re-review source and claim evidence, replace working chapters and prompts, and preserve historical raw inputs.
- Enforce source, claim, and overlay freshness, with weekly read-only CI evaluation.
- Verify stored raw imports and bind packaging to independently rerun, tree-bound verification receipts.
- Correct task contracts and prompt placement, archive unused illustrations, and keep template journals out of client scaffolds.
- Record failing external maturity checks explicitly in the dated verification report.

## 0.3.0 - 2026-07-18

### Added

- Brainstein v3 repository specification and cross-runtime governance.
- Canonical source and claim ledgers, validation schemas, deterministic Obsidian projections, confidence tags, source map, safety gates, contradiction register, and current official doctrine.
- Evidence overlays covering all 59 generated chapters and 37 generated prompt notes.
- Hash-bound Claude Obsidian research, doctrine, and metadata transactions.
- Explicit target/date/dry-run safety, content-addressed raw receipts, deterministic sample builds, CI, and the required standalone regression suite.

### Changed

- Qualified the historical seed as provenance rather than current authority.
- Replaced unsafe or unsupported address, review, link, schema, cadence, ranking-weight, AI-model, and community-participation guidance with sourced boundaries.
- Narrowed the public product contract to behavior the scripts and tests demonstrate. The scorecard remains Draft until a transparent scoring model exists.
- Aligned the canonical version, Python requirement, knowledge counts, marketplace metadata, plugin metadata, operator docs, release gates, licensing notices, and privacy wording.

### Fixed

- Prevented `ingest_knowledge_base.py --dry-run` from deleting generated notes.
- Made same-input domain ingestion idempotent with content-addressed raw files and digest-qualified source notes.
- Removed misleading NAP-diff and causal geo-grid language from adapter output.
- Rendered weekly-report headings and lists as HTML instead of escaped Markdown with line breaks.

## 0.2.2 · 2026-05-20 (personas illustration)

### Added

- **`assets/img/personas.jpg`** (90 KB) embedded above the buyer table
  in the "Who this is for" section. Three persona cards side by side
  matching the three table rows: **Agency** (woman with tablet,
  citation lists, search result, map with pins), **Multi-location
  operator** (man with clipboard in front of a pin-covered map), and
  **SAB owner** (tradesperson with a phone showing reviews next to a
  small storefront with a map pin). Compressed from 574 KB source PNG
  to JPEG q81 at 1200px wide, 4:2:0 chroma, stripped, progressive
  encoded. 84% reduction. Brings the README visual layer to four
  embedded illustrations: hero, personas (new), vault graph in Why,
  map pack annotation in GBP.

## 0.2.1 · 2026-05-20 (hero + vault-graph swap)

### Changed

- **Hero image** (`assets/img/hero-banner.jpg`) swapped to the new
  wordmarked editorial illustration: brand wordmark "Local SEO Brain" in
  the center, fragmented data scatter (CSVs, sticky notes, GBP screen) on
  the left, a connected brain-shaped knowledge graph over a faint street
  map on the right. Source PNG was 1.87 MB at 2172×724; compressed in
  place to JPEG q83 at 1500×500, **126 KB** (a 93% reduction). The
  previous editorial map hero is no longer referenced in the README.
- **"Why Local SEO Brain" section illustration** swapped from
  `fragmented-to-unified.jpg` to `assets/img/vault-graph-view.jpg`: a
  compressed snapshot of the actual Obsidian graph view, showing 200+
  colored nodes (one cluster colour per folder) and 1,271 wikilinks on
  the brand-canvas dark background. Source was the original 398 KB PNG
  carried over from v0.1.x; flattened over `#1F1B16`, JPEG q82 at 1400px
  wide, **139 KB** (65% reduction). The vault graph is now visible above
  the value-prop bullets instead of the redundant before-and-after
  illustration — the new hero already tells the before-and-after story,
  so the "Why" slot moves to showing the actual product output.

### Retained

- `assets/img/fragmented-to-unified.jpg`, `-funnel.jpg`,
  `-cards.jpg`: kept on disk as swappable alternates.
- `assets/img/map-pack-explained.jpg`: still embedded under the GBP
  phase in "The 3 phases of Local SEO".
- `assets/png/graph-view.png`: original 398 KB legacy hero PNG kept in
  place since it is referenced by older release artifacts and historical
  CHANGELOG entries.

## 0.2.0 · 2026-05-20 (SSS+ visual + content refit)

### Added

- **Editorial hero illustration** (`assets/img/hero-banner.jpg`, 76KB)
  promoted to line 1 of the README: stylized neighborhood map with
  connected business storefronts and a "local seo brain" search chip on
  the right. 1600px wide, JPEG q80 with 4:2:0 chroma subsampling. Replaces
  the SVG-figlet hero in the rendered README. The animated SVG banner is
  retained at `assets/svg/banner.svg` (8KB, 4.2s breathing gradient, OS
  window chrome) for use in decks, social cards, and HTML embeds where
  SMIL animation is preserved.
- **"Why" section illustration** (`assets/img/fragmented-to-unified.jpg`,
  90KB) at the top of "Why Local SEO Brain": diagonal-split illustration
  contrasting fragmented spreadsheets / sticky notes / CSV exports
  against a unified brain-shaped graph of connected pins, storefronts,
  and reports. Visualizes the value prop in one frame.
- **Map Pack annotation** (`assets/img/map-pack-explained.jpg`, 62KB)
  inside "The 3 phases of Local SEO" under the GBP bullet: annotated
  Google search mock with sticky-note labels pointing at the Local Pack
  and the GBP Card.
- **Two alternates** kept in `assets/img/` for future swapping: the
  funnel variant (37KB) and the before/after comparison-cards variant
  (64KB) of the fragmented-to-unified concept.

Total image budget for the 5 raster illustrations: **329KB** (down from
4.1MB at source, a 92% reduction). All five files sit under rule 9's
100KB-per-image cap.
- **`marketplace.json`** discovery manifest with name, tagline,
  description, version, license, topics, entrypoints, scripts, refusal
  rules, compatibility matrix, and support links. Distinct `name`
  (`local-seo-brain`) per sibling-repo rule.
- **2 new SVG diagrams** to complete the rule-2 visual set of 5:
  - `assets/svg/pipeline.svg`: four-stage operator pipeline (raw sources to
    ingestors to wiki memory to deliverables), with explicit script names
    inline as text so crawlers and AI Overviews can index the structure.
  - `assets/svg/roadmap.svg`: v0.1 to v1.0 timeline with shipped milestones
    in brand orange and upcoming in stone, "YOU ARE HERE" marker on v0.2.0.
- **6 new README sections** per rule 8: Methodology (with pipeline diagram
  + 3 framework diagrams), Sample Output (literal scorecard excerpt with
  sourced priorities), Use Cases (6-row buyer-scenario table), Compared
  to other tools (6-row contrast table), FAQ (10 questions), Limitations
  (explicit "does not do in V1" list, placed directly after the roadmap
  diagram per rule 3).
- **"Why Local SEO Brain"** bullet block immediately after the header
  (rule 1).
- **"Which version are you installing?"** install preamble with Pro vs
  Community swap rule (rule 4).
- **Third install method**: Community ZIP (Obsidian-only) added alongside
  private repo install and tagged release archive (rule 4: 3 methods).
- **5-link maintainer block** (Blog, Skool free, Skool Pro, YouTube,
  GitHub) per rule 5.

### Changed

- **README rewritten end to end** to the 2026 SSS+ standard, sized at
  29.2KB (well under the 50KB cap from rule 9). Zero em-dashes, zero
  en-dashes in user-facing copy per rule 8.
- **Roadmap section** now leads with the SVG diagram, then the textual
  bullet list, then Limitations directly below (rule 3 ordering).
- **Badge row** rebuilt: License, Version (brand orange), Python 3.11+,
  Knowledge chapters, Prompts, Wikilinks. Six badges per rule 1.

### Diagrams

The five-diagram set is now complete:

| Diagram | Role | File |
|---|---|---|
| Banner | Header visual | `assets/svg/banner.svg` |
| Architecture / relationship map | Shows raw to wiki to deliverable | `assets/svg/brain-relationship-map.svg` |
| Pipeline | 4-stage operator flow | `assets/svg/pipeline.svg` |
| Framework: 3 Phases | Strategic frame | `assets/svg/three-phases-of-local-seo.svg` |
| Framework: Core 30 | Content strategy | `assets/svg/core-30-content-map.svg` |
| Framework: LLM SEO factors | AI search factors | `assets/svg/llm-seo-ranking-factors.svg` |
| Roadmap | v0.1 to v1.0 timeline | `assets/svg/roadmap.svg` |

All diagrams use the unified palette (`#D97757` brand orange, `#1F1B16`
canvas, `#2f7f87` teal, `#B084CC` purple) and Inter + JetBrains Mono.

## 0.1.2 — 2026-05-19 (interlinking deep-fix)

### Fixed

- **48 broken Google-Docs-export anchor links** across 30 files. The source
  markdown used inline anchor links like `[Internal Anchor Text Guidelines](#content:-internal-anchor-text-guidelines)`
  which Obsidian could not resolve. Built `scripts/fix_anchor_links.py`
  (idempotent, fragment → slug resolver) that converted all of them to
  proper wikilinks like `[[content-internal-anchor-text-guidelines|Internal Anchor Text Guidelines]]`.
  All 48 resolved, 0 unresolved.
- **47 missing reverse cross-link edges** added. If A linked to B in its
  cross-link block but B didn't link back to A, the reverse edge was
  added. Bidirectional graph now.

### Improved

- **Lint script upgraded** (`scripts/lint_vault.py`) to also catch Google
  Docs-style `[Text](#fragment)` links and dangling relative markdown
  links going forward. Previously only wikilinks were checked.
- Wikilink count grew **1,176 → 1,271** (+95 across this slice).

### Dev convenience

- Root `.obsidian/` mirrored from `assets/template-brain/.obsidian/` so the
  graph is colored whether you open the repo root or the inner vault.
- `OPEN-IN-OBSIDIAN.md` added explaining both views.
- Root `.obsidian/appearance.json` enables the `brain` CSS snippet by default.

## 0.1.1 — 2026-05-19 (same-day audit + freshness layer)

### Added

- **2026 freshness layer** under `wiki/freshness/` — 6 current-state notes
  citing trusted 2026 sources, supplementing seeded chapters that became
  stale since they were written:
  - `2026-llm-model-lineup.md` — GPT-5.5, Claude Opus 4.7, Gemini 3.1 Pro
    replaced GPT o1, Claude 3.5, and Gemini 1.5/2.0 references.
  - `2026-ai-overviews-state.md` — citation patterns stabilized to 3-5
    sources per overview; Map Pack pressure documented.
  - `2026-gbp-changes.md` — GBP Chat sunset 2024-07-31, Q&A API sunset
    2025-11-03, free website builder discontinued, Ask Maps (Gemini)
    replaces manual Q&A, 2× weekly post cadence mandatory, 30-day
    inactivity decay is steep.
  - `2026-december-core-update.md` — E-E-A-T extended beyond YMYL to all
    competitive queries; behavioral signals (bounce/dwell) weight up.
  - `2026-reddit-llm-citation-engine.md` — Reddit at ~40% LLM citation
    share; Google licensing formalized.
  - `2026-schema-modernization.md` — industry-specific subtypes
    mandatory; Person schema load-bearing post-Dec-2025.
- **22 stale-warning callouts** injected into affected seeded chapters,
  each linking to the relevant freshness note.
- **Curated cross-link blocks** added to 58 seeded chapters with 4-5
  topically-adjacent chapter links (e.g., GBP Categories ↔ GBP Services ↔
  GBP Description). Vault now has 1,176 wikilinks total.
- **3 new SVG diagrams** embedded in their parent chapters:
  - `three-phases-of-local-seo.svg` (in The 3 Phases chapter)
  - `core-30-content-map.svg` (in Core 30 Content Strategy)
  - `llm-seo-ranking-factors.svg` (in LLM Ranking Factors)
- **Onboarding Canvas** rewritten with a real 15-node, 14-edge layout
  showing Start Here → 3 Phases → flows → hubs → deliverables.
- **Obsidian visual theme** updated:
  - `graph.json` with 14 color groups (one per logical cluster including
    freshness layer)
  - `brain.css` with phase palette (teal/coral/amber/purple), callout
    styling for `[!warning]` freshness blocks, table density tweaks.
- **CODEX updates** documenting the freshness layer + 90-day re-verify
  cadence.

### Verified

- Coverage audit: 59 source H1 chapters → 59 wiki notes (100%); 37 AI
  prompts → 37 wiki notes (100%); 31 images → 31 embedded references
  (100% — zero orphans); all 33 ⚠️, 12 💡 Pro Tip, 2 🔍 Key Insight
  callouts survived ingestion.
- 5 missing images (image27-31, not in supplied zip) recovered from
  base64 inline data in the source markdown.
- Both template and sample vault lint clean post-enhancement.

## 0.1.0 — 2026-05-19

### Added

- Scaffolded from `brain-builder` skill (pattern proven by Marketing Brain
  and Ads Brain).
- Seeded knowledge base from
  `LOCAL-seo-Knowledge-Base.md` (Google Docs export, 3.3MB markdown +
  31 reference images extracted from base64 inline data).
- **59 chapter notes** across glossary, concepts, frameworks, audits, GBP,
  content, backlinks, and LLM SEO.
- **37 AI prompts** materialized as standalone reusable notes under
  `wiki/prompts/`, each linked back to its parent chapter.
- **31 reference images** under `_attachments/images/`.
- Operating files customized for Local SEO Brain: `CODEX.md`, `Hot`,
  `Index`, `Overview`, `Start Here`, `Dashboard`.
- 3 workflow notes: `Property Audit Workflow`, `GBP Optimization Workflow`,
  `Citation Audit Workflow`.
- 4 Local-SEO-shaped templates under `_templates/`: `location`,
  `competitor`, `audit-finding`, `keyword-cluster`.
- 4 domain ingest scripts: `ingest_gbp`, `ingest_citations`,
  `ingest_reviews`, `ingest_geogrid` (CSV/JSON, no API in V1).
- `ingest_knowledge_base.py` — idempotent bulk re-seed script.
- Local-SEO-specific SVG relationship map showing the 3 phases architecture.
- 4 test fixtures for smoke-testing domain ingest paths.
- Refusal rules in `SKILL.md`: no GBP mutation, no fake reviews, no PII,
  no mass low-quality citations, no proximity tactics, no keyword stuffing.

### Verified

- Template vault lint passes (zero dead wikilinks, zero orphans).
- Sample vault lint passes.
- Full pipeline end-to-end: scaffold → ingest (GBP/citations/reviews/geo-grid)
  → synthesize → render → lint → next.

### Roadmap

- 0.2.0 — Real per-platform parsing in the domain ingestors (NAP diff,
  rating distribution, geo-grid heatmap math).
- 0.3.0 — Synthesis upgrade: priority audit per location, citation gap
  vs top-3 competitors.
- 0.4.0 — DataForSEO enrichment (local SERP, local maps).
- 0.5.0 — Dashboard polish, brand-kit deck for product page.
- 1.0.0 — Approval-gated GBP mutation with rollback.

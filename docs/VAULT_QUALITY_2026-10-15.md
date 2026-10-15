# Vault organization and editorial review, 2026-10-15

The active template and generated sample have no orphan notes, unreachable notes, broken or ambiguous links, empty sections, or unreferenced active attachments. The review found editorial and provenance defects that link lint alone did not detect. Those defects were corrected before this result was recorded.

## Structure and navigation

| Check | Template | Generated sample |
|---|---:|---:|
| Markdown notes | 162 | 180 |
| Note-to-note links (unique targets per note) | 728 | 835 |
| Orphan notes | 0 | 0 |
| Notes without an outgoing note link | 0 | 0 |
| Notes unreachable from Index | 0 | 0 |
| Maximum clicks from Index | 2 | 2 |
| Active attachments | 1 | 1 |
| Unreferenced active attachments | 0 | 0 |

Repository lint and pinned strict Claude Obsidian lint both pass for both vaults, with no exclusions or dangling-link allowances. Strict lint scans 730 links in the template and 865 in the sample; these totals also include non-note targets such as the relationship SVG and onboarding canvas. The 96 generated working notes agree with the canonical overlays. Every note is reachable from Index within two hops.

The active route is Hot, Index, then the relevant task hub or workflow. Canonical evidence belongs in `references/`, replacement guidance in `data/knowledge-overlays.json`, and working pages in `assets/template-brain/wiki/`. `examples/sample-vault/` remains generator-owned. Historical raw files and archived visuals are provenance, not current advice.

## Editorial corrections

All 59 chapter input/result contracts are now distinct and task-specific. The review removed mismatched category wrappers, including AI-observation inputs on community participation and schema tasks. Local-citation and internal-link notes no longer repeat irrelevant external link-scheme warnings.

The 37 prompts retain distinct roles, required inputs, missing-input behavior, output acceptance, and human review. Customer Question Editing now belongs with keyword research. Stable filenames and raw provenance remain unchanged. Hub legends explain that unsupported labels concern a reviewed claim or legacy proposition, rather than condemning the whole usable note. GBP and LLM SEO casing, workflow placement, the regional Search section order, setup counts, and the overview's replacement-only description are corrected.

The shared prompt footer still repeats evidence, missing-input, privacy, approval, and rollback requirements. That repetition is intentional and task-relevant. Manual review found no remaining material filler or task-placement blocker in the reviewed working chapters and prompts. This is an editorial finding, not a claim that word-pattern checks can prove universal absence of weak prose.

## Assets and provenance

Three misleading decorative chart embeds were removed from active hubs. Their unmeasured review figures, rating, and NAP grades are not product evidence.

The 31 extracted course PNGs were retained byte-for-byte under `.raw/source-material/archived-attachments/` with historical hash receipts and private-use notices. (Update, 2026-10-15: the whole third-party bundle, including these PNGs, was withdrawn from the public tree before the MIT release. The hash receipts and reviewed withdrawal records remain in `references/`.) The 16 old project-authored JPGs are retained once under `assets/archive/legacy-diagrams/`; they are not source evidence or scaffold inputs. Three unused SVG vault copies were removed; governed current SVGs remain under `assets/svg/`. The active vault attachment is the generated operating map used by Overview.

`references/asset-retention.json` records 78 exact moves and 16 sample deduplications. The safety scanner verifies baseline source bytes, size, digest, source absence, fixed destination, and retained target bytes. It grants no allowance for a later arbitrary addition at that destination. Regressions reject tampered retained assets, later re-additions, and unreviewed JPGs in the former permissive sample directory. The historical/retained-asset contract verifies 50 unique repository files: three original course inputs, 31 extracted PNGs, and 16 authored JPGs. Existing original raw payloads remain unchanged.

Canonical template transaction journals stay intact in the repository. New scaffolds exclude them and record a separate SHA-bound copied-template receipt. They no longer substitute client values into old bundles while retaining unrelated approval hashes. The sample also exposes its five retained July fixture rows in Source Manifest Guide as manifest-only historical receipts. Source hubs and logs update their modification dates when ingestors actually write them.

## Verification scope

The full release runner executes all 14 regression scripts, both lints on both vaults, evidence and freshness contracts, deterministic regeneration, raw/asset integrity, safety, and patch hygiene. The dated maintenance verification report records final results and the generated sample hash.

The organization and content corrections do not clear the separate release gate. Brainstein remains 89, SS, demo-verified, with zero critical failures and a legacy package-hook warning. Local changes are uncommitted. Remote synchronization and hosted CI remain unverified; no account mutation, paid call, push, or publication occurred.

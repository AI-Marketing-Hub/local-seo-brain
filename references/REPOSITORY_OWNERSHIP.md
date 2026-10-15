# Repository Ownership Map

| Surface | Canonical owner | Change route |
|---|---|---|
| Version | `pyproject.toml` | Patch canonical value, then align tested projections |
| Source evidence | `references/source-ledger.json` | Reviewed repository patch and contract validation |
| Claim evidence | `references/claim-ledger.json` | Reviewed repository patch and contract validation |
| Generated note corrections | `data/knowledge-overlays.json` | Update overlay, regenerate in staging, transact canonical vault |
| Visual diagrams | `scripts/generate_vault_visuals.py` and SVG sources | Reviewed repository build; the Obsidian transaction API accepts wiki content only |
| Historical seed | `assets/template-brain/.raw/source-material/` | Immutable; never rewrite |
| Ledger projections | `scripts/evidence_contract.py` | Generate in staging, check drift, transact canonical vault |
| Template wiki | `assets/template-brain/wiki/` | Hash-bound Claude Obsidian transaction only |
| Sample vault | `scripts/build_demo_vault.py` + `tests/fixtures/` | Deterministic reviewed repository build only |
| Public behavior claims | README, SKILL, marketplace, docs | Must be demonstrated by tests |

Generator-owned files must not receive durable one-off fixes. Change their canonical input or generator and prove a clean regeneration.

The sample-history fixtures preserve the original sample raw bytes. Sample rebuilds retain all existing raw evidence paths, append integrity-manifest rows, and reject conflicts. Raw manifests are mutable integrity metadata; source payloads remain immutable.

Historical course extracts are retained under `.raw/source-material/archived-attachments/`. Old authored diagram drafts are retained once in `assets/archive/legacy-diagrams/`. Reviewed hash-preserving moves are listed in `references/asset-retention.json`; those archives do not support current claims. Scaffolds exclude template transaction history and record a separate copied-template receipt.

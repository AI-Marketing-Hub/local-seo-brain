---
type: "flow"
title: "Source Intake Workflow"
created: "2026-07-18"
updated: "2026-07-18"
status: "active"
tags: ["domain/local-seo", "type/flow", "domain/flows"]
---

# Source Intake Workflow

1. Confirm the operator is authorized to use the source and choose a pinned `--as-of` date.
2. Keep the source outside the repository; call the matching adapter with explicit `--vault`, `--client`, `--file`, and `--as-of` values.
3. Run `--dry-run` and review the exact target.
4. The adapter copies the source to a content-addressed `.raw/` path and records its SHA-256 in `.raw/.manifest.json`.
5. Verify the source note and link only observations supported by the file.
6. Keep raw review data access-controlled and omit reviewer identity from derived notes.
7. Use [[Claim Verification Flow]] before promoting an observation into current guidance.

Do not manually overwrite a raw receipt, fabricate metadata, or treat an export as authority beyond its measured scope.

## Related

- [[wiki/sources/_index|Sources Hub]]
- [[Source Manifest Guide]]
- [[CONVENTIONS|Evidence and Vault Conventions]]
- [[Index]]

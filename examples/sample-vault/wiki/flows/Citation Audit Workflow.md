---
type: "flow"
title: "Citation Audit Workflow"
created: "2026-07-18"
updated: "2026-07-18"
status: "active"
tags: ["domain/local-seo", "type/flow", "domain/flows"]
---

# Citation Audit Workflow

## Preconditions

- Owner-confirmed canonical business name, address visibility/service area, and phone are recorded in a location note.
- An authorized citation CSV is available outside the repository.
- The operator has read [[backlinking-local-citations|Backlinking: Local Citations]] and its Evidence status.

## Ingest

```bash
python3 scripts/ingest_citations.py \
  --vault /absolute/client-vault --client CLIENT_SLUG \
  --file /absolute/citations.csv --as-of YYYY-MM-DD --dry-run
```

The adapter materializes exported directory name, URL, and status. It does **not** compute a NAP difference, directory quality tier, competitor gap, or prioritization score.

## Review

1. Verify the source receipt and content hash.
2. Compare a listing with owner-confirmed canonical data only when the export contains the necessary fields.
3. Mark missing fields as not evaluated.
4. Reject fake-business citations, automated low-quality submissions, and collection that violates applicable terms.
5. Put each proposed correction in [[Approval Queue]] with the current value, proposed value, owner, source, risk, and rollback.

## Done when

- Every reported observation is traceable to the exported row or explicitly marked not evaluated.
- No submission or directory mutation has occurred.
- The Draft deliverables distinguish evidence from proposed action.

## Related

- [[Claim Verification Flow]]
- [[wiki/citations/_index|Citations Hub]]
- [[Source Intake Workflow]]
- [[Index]]

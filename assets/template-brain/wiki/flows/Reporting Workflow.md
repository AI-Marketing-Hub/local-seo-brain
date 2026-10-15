---
type: "flow"
title: "Reporting Workflow"
created: "2026-07-18"
updated: "2026-07-18"
status: "active"
tags: ["domain/local-seo", "type/flow", "domain/flows"]
---

# Reporting Workflow

1. Confirm every material statement is an observed value, active claim, or explicit unknown.
2. Keep the scorecard and roadmap Draft when no transparent scoring model exists.
3. Separate what changed from why it may matter; do not infer cause from timing.
4. Include sources, limitations, owner, approval state, and rollback for proposed changes.
5. Render HTML only after lint passes:

```bash
python3 scripts/lint_vault.py --vault /absolute/client-vault
python3 scripts/render_brain_report.py --vault /absolute/client-vault
```

## Related

- [[Weekly Report]]
- [[wiki/reports/_index|Reports Hub]]
- [[Claim Verification Flow]]
- [[Index]]

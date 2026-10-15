---
type: "flow"
title: "Synthesis Workflow"
created: "2026-07-18"
updated: "2026-07-18"
status: "active"
tags: ["domain/local-seo", "type/flow", "domain/flows"]
---

# Synthesis Workflow

1. Verify imported source receipts and current claim IDs.
2. Separate observed facts, policy, operational interpretation, practitioner judgment, and unknowns.
3. Run the bundled synthesizer with an explicit date:

```bash
python3 scripts/synthesize_brain.py --vault /absolute/client-vault --as-of YYYY-MM-DD --dry-run
```

4. Review the planned Draft output, then remove `--dry-run` if appropriate.
5. Keep missing evidence as `no_data` or `needs_input`.
6. Put proposed account changes in [[Approval Queue]].

The bundled synthesizer reports source coverage and review steps. It does not calculate a grade, priority score, causal lift, or completed action.

## Related

- [[Claim Verification Flow]]
- [[Health Scorecard]]
- [[Action Roadmap]]
- Approval Queue
- [[Index]]

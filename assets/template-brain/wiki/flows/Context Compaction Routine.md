---
type: "flow"
title: "Context Compaction Routine"
created: "2026-07-18"
updated: "2026-07-18"
status: "active"
tags: ["domain/local-seo", "type/flow", "governance/context"]
---

# Context Compaction Routine

## Trigger

The active task has enough evidence, commands, transaction IDs, or pending gates that losing state would create rework or safety risk.

## Prerequisites

Identify the current objective, completed work, canonical files, immutable inputs, transaction hashes, active blockers, and next exact command.

## Steps

1. Record the verified baseline and branch.
2. Separate completed work from pending work.
3. Preserve exact file paths, hashes, dates, source counts, and transaction IDs.
4. State which skills/contracts govern the next mutation.
5. Record known incompatibilities and actions that are not authorized.
6. Continue from the next uncompleted gate without repeating finished work.

## Outputs

A compact continuation record that is sufficient to resume safely without inventing or redoing state.

## Gates

No secret or private client data enters the compaction; hashes and dates are exact; permissions and stop boundaries remain explicit.

## Failure modes

Do not compact away unresolved contradictions, failed gates, user-owned changes, or the distinction between staged and canonical vault state.

## Rollback

If the continuation record conflicts with current files, trust fresh read-only inspection, flag the conflict, and rebuild the record before writing.

## Related

- [[Explore Plan Code Commit]]
- [[Multi-Agent Fan-Out Research Flow]]
- [[CONVENTIONS|Evidence and Vault Conventions]]
- [[Uncertainty Eval Policy]]
- [[Log]]
- [[Index]]

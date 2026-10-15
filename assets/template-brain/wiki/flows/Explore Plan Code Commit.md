---
type: "flow"
title: "Explore Plan Code Commit"
created: "2026-07-18"
updated: "2026-07-18"
status: "active"
tags: ["domain/local-seo", "type/flow", "governance/change"]
---

# Explore Plan Code Commit

## Trigger

A repository change is requested and cannot be answered read-only.

## Prerequisites

Confirm scope, authority, Git status, governing instructions, generator ownership, and whether canonical vault paths require a transaction.

## Steps

1. Explore the smallest relevant file and evidence surface.
2. Record baseline commands and hashes.
3. Plan bounded changes and explicit verification.
4. Patch canonical inputs or code; never hand-patch generated notes.
5. Stage vault output, lint it, inspect the transaction, and apply only the bound plan.
6. Run repository, evidence, deterministic-build, privacy, and Brainstein gates.
7. Create a scoped local commit only after reporting unresolved blockers.

## Outputs

A reviewed diff, exact test evidence, transaction IDs where applicable, local commit hash, and a no-remote-mutation statement.

## Gates

No unrelated changes, generated drift, secret/private-data finding, stale source, failed lint, or unsupported product claim.

## Failure modes

Stop on dirty overlapping work, ambiguous destructive target, missing rights, schema incompatibility, or a gate that cannot be represented honestly.

## Rollback

Use transaction recovery for vault operations. For repository changes, preserve user work and reverse only the scoped commit through an approved recoverable Git action.

## Related

- [[Claim Verification Flow]]
- [[Memory Governance Policy]]
- [[Approval Queue]]
- [[Uncertainty Eval Policy]]
- [[Log]]
- [[Index]]

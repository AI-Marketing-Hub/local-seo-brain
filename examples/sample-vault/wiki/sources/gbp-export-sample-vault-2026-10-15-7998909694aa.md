---
type: "source"
title: "GBP Export - sample-vault - 2026-10-15"
created: "2026-10-15"
updated: "2026-10-15"
status: "imported"
tags: ["type/source", "domain/gbp", "provenance/raw"]
source_kind: "gbp-csv-export"
source_path: ".raw/clients/sample-vault/gbp/2026-10-15-7998909694aa-sample-gbp.csv"
source_hash: "sha256:7998909694aab450b69b8c673170e8e46c5c356919e29d8202ead4b00a061f30"
location: "sample-vault"
---

# GBP Export - sample-vault - 2026-10-15

## Source

- Path: `.raw/clients/sample-vault/gbp/2026-10-15-7998909694aa-sample-gbp.csv`
- SHA-256: `7998909694aab450b69b8c673170e8e46c5c356919e29d8202ead4b00a061f30`
- Retrieved: 2026-10-15
- Kind: Google Business Profile CSV export (Insights or Performance)

## Compiled Truth

CSV introspection:

- Rows: 5
- Columns: 6
- Header sample: `Date, Impressions, Search Views, Direction Requests, Phone Calls, Website Clicks`

> This adapter records file-level provenance and structural CSV metadata. It
> does not calculate performance trends or infer causes from the export.

## Refusal

This source does not authorize any GBP profile mutation. All recommendations
derived from this data route through [[Approval Queue]] before execution.

## Related

- [[sample-vault]]
- [[wiki/sources/_index|Sources Hub]]
- [[GBP Optimization Workflow]]
- [[wiki/gbp/_index|GBP Hub]]

---
type: "source"
title: "Citations Export (2026-10-15)"
created: "2026-10-15"
updated: "2026-10-15"
status: "imported"
tags: ["type/source", "domain/citations", "provenance/raw"]
source_kind: "citation-csv-export"
source_path: ".raw/clients/sample-vault/citations/2026-10-15-6cb34216fcc6-sample-citations.csv"
source_hash: "sha256:6cb34216fcc62b084165bdefcc45c4653a88d9bd0f7d1fd2c4a62eb6e4725cec"
location: "sample-vault"
platform: "whitespark"
---

# Citations Export (2026-10-15)

## Source

- Path: `.raw/clients/sample-vault/citations/2026-10-15-6cb34216fcc6-sample-citations.csv`
- SHA-256: `6cb34216fcc62b084165bdefcc45c4653a88d9bd0f7d1fd2c4a62eb6e4725cec`
- Retrieved: 2026-10-15
- Platform: whitespark
- Rows ingested: 8

## Compiled Truth

Citation snapshot for [[sample-vault]] from a whitespark export. 8 directory
listings were materialized as individual notes under `wiki/citations/`.

This adapter captures only the directory name, URL, and exported status. It
does not calculate a NAP difference or competitor gap. Compare each listing
with owner-confirmed canonical data before proposing a correction.

## Refusal

- No mass submission to low-quality directories.
- No fake-business citations.
- No directory scraping that violates ToS.

## Related

- [[sample-vault]]
- [[wiki/citations/_index|Citations Hub]]
- [[Citation Audit Workflow]]
- [[backlinking-local-citations|Backlinking: Local Citations]]

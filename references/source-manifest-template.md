# Raw provenance contracts

Manual and domain imports use `.raw/.manifest.json`, schema local-seo-brain.raw-manifest.v1. Each record contains path, SHA-256, ingestion as_of, client slug, and kind. Derived source notes carry the supplied-file scope and descriptive output.

The licensed historical seed uses the independent `.vault-meta/historical-seed.json` receipt. Its hashes are checked before ingestion and synthesis. The repository also retains references/historical-seed.sha256 as the unchanged historical baseline.

Every listed raw input is verified against its stored bytes. Imported raw copies are installed atomically without overwrite, and one live ingestion at a time may update a vault. Dry-run does not create locks or files. Neither manifest authorizes an external account operation.

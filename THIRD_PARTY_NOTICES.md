# Third-Party Notices

Local SEO Brain is released under the MIT license in `LICENSE`. The material below has rights that are separate from that license.

## Historical Local SEO source bundle

The first 59 chapter notes and 37 prompt notes were generated from an operator-supplied historical course export: `LOCAL-seo-Knowledge-Base.md`, its DOCX form, its ZIP bundle, and 31 images extracted from it. That bundle is third-party material. The project metadata does not establish a public redistribution license for it, so it is not included in this repository and is excluded by `.gitignore` under `.raw/source-material/`.

What the repository keeps is provenance, not content: the file hashes in `references/historical-seed.sha256` and `references/archived-assets.sha256`, the vault historical receipts, the reviewed withdrawal records in `references/asset-retention.json`, and `references/historical-seed-outline.json`, which lists the generated note IDs and the seed hash without any seed text. Every committed generated note carries replacement content from `data/knowledge-overlays.json` written for this project; none reproduces the bundle text or embeds its images. An operator who holds the bundle under its own rights can place it under `assets/template-brain/.raw/source-material/` to regenerate notes locally. Do not redistribute the bundle outside the rights granted by its owner.

## Official documentation and standards

Google Search, Google Business Profile, Google Maps Platform, Search Status Dashboard, schema.org, and other external names and documentation remain the property of their respective owners. The repository stores links, metadata, factual paraphrases, and brief attributed excerpts where permitted; it does not claim ownership of those sources. Google and related product names are trademarks of Google LLC.

## Visual and font references

The project-authored visual surfaces are the files under `assets/img/`, `assets/png/`, and `assets/svg/`, plus the diagrams retained under `assets/archive/legacy-diagrams/`. They use original project compositions and may reference product interfaces or trademarks descriptively. No font binaries are bundled. Inter and JetBrains Mono are named only as CSS/design references; any bundled font files added later must carry their upstream license text. ANSI Shadow is credited as banner typography inspiration.

Before any public release, verify that the package excludes the historical bundle and private raw data, contains only assets with documented rights, and includes the applicable license texts and attributions.

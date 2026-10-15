#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

from runtime import (
    touch_note_updated,
    immutable_raw_target,
    vault_mutation,
    install_immutable_raw,
    parse_as_of,
    require_source,
    require_vault,
    safe_name,
    write_text,
    safe_slug,
    update_raw_manifest,
)


TEXT_SUFFIXES = {".md", ".txt", ".csv", ".json", ".html", ".yml", ".yaml"}


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest a raw source into a brain vault.")
    parser.add_argument("--vault", required=True)
    parser.add_argument("--file", required=True)
    parser.add_argument("--label", default="")
    parser.add_argument("--client", required=True)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    vault = require_vault(args.vault)
    with vault_mutation(vault, dry_run=args.dry_run):
        source = require_source(args.file)
        today = parse_as_of(args.as_of)
        client = safe_slug(args.client)
        raw_dir = vault / ".raw" / "sources" / "manual"
        raw, digest = immutable_raw_target(raw_dir, source, today)
        title = args.label or source.stem.replace("-", " ").replace("_", " ").title()
        note = vault / "wiki" / "sources" / f"{safe_slug(title)}-{digest[:8]}.md"
        if args.dry_run:
            print(f"DRY-RUN: would ingest {source} as {raw.relative_to(vault)} and {note.relative_to(vault)}")
            return 0
        raw_dir.mkdir(parents=True, exist_ok=True)
        install_immutable_raw(source, raw, digest)
        update_raw_manifest(vault, raw_path=raw, digest=digest, kind="manual", as_of=today, client=client)
        summary = summarize(raw)
        write_text(note, f"""---
type: "source"
title: "{title}"
created: "{today}"
updated: "{today}"
status: "imported"
tags: ["type/source", "domain/local-seo", "provenance/raw"]
source_path: "{raw.relative_to(vault).as_posix()}"
source_hash: "sha256:{digest}"
---

# {title}

Imported source for human review. Check this excerpt against the preserved input before using it as evidence.

## Source summary

{summary}

## Source

- Path: `{raw.relative_to(vault).as_posix()}`
- SHA-256: `{digest}`

## Related

- [[wiki/sources/_index|Sources Hub]]
- [[Synthesis Workflow]]
""")
        update_sources_hub(vault, note.stem, today)
        append_log(vault, f"Ingested source [[{note.stem}]].", today)
        print(note)
        return 0

def summarize(path: Path) -> str:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return "Binary or unsupported text source imported. Summarize manually before synthesis."
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"(?m)^#{1,6}\s+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return (text[:700] + "...") if len(text) > 700 else (text or "Empty source.")


def update_sources_hub(vault: Path, stem: str, today: str) -> None:
    hub = vault / "wiki" / "sources" / "_index.md"
    text = hub.read_text(encoding="utf-8") if hub.exists() else "# Sources Hub\n\n## Notes\n"
    link = f"[[{stem}]]"
    if link not in text:
        text = text.rstrip() + f"\n- {link}\n"
    hub.write_text(text, encoding="utf-8")
    touch_note_updated(hub, today)


def append_log(vault: Path, message: str, today: str) -> None:
    log = vault / "wiki" / "log.md"
    text = log.read_text(encoding="utf-8") if log.exists() else "# Log\n"
    line = f"- {today} - {message}"
    if line not in text:
        log.write_text(text.rstrip() + f"\n{line}\n", encoding="utf-8")
        touch_note_updated(log, today)


if __name__ == "__main__":
    raise SystemExit(main())

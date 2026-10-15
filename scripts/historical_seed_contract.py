#!/usr/bin/env python3
"""Verify immutable historical inputs and explicitly retained asset bytes.

The historical course bundle under `.raw/source-material/` is third-party
material supplied by the operator. It is not shipped with the repository, so
its files may be absent. A file that is present must match its recorded hash.
Project-authored retained assets must always be present and unchanged.

`--render-outline` derives `references/historical-seed-outline.json` from the
bundle: the generated note IDs the seed produces, plus the seed hash, without
any of the seed text. The outline is the contract used when the bundle is
absent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "references/historical-seed.sha256"
RETAINED = ROOT / "references/archived-assets.sha256"
BUNDLE_MARKER = "/.raw/source-material/"
sys.path.insert(0, str(Path(__file__).resolve().parent))


def render_outline(seed: Path) -> int:
    from freshness import SEED_OUTLINE, SEED_OUTLINE_SCHEMA, seed_notes_from_text

    if not seed.is_file():
        raise SystemExit(f"ERROR: historical seed not found: {seed}")
    expected = next((line.split(maxsplit=1)[0] for line in MANIFEST.read_text(encoding="utf-8").splitlines() if line.strip().endswith(".md")), None)
    digest = hashlib.sha256(seed.read_bytes()).hexdigest()
    if expected and digest != expected:
        raise SystemExit("ERROR: seed does not match references/historical-seed.sha256")
    outline = {
        "schema": SEED_OUTLINE_SCHEMA,
        "seed_sha256": digest,
        "notes": sorted(seed_notes_from_text(seed.read_text(encoding="utf-8"))),
    }
    SEED_OUTLINE.write_text(json.dumps(outline, indent=2) + "\n", encoding="utf-8")
    print(f"Historical seed outline rendered: {len(outline['notes'])} note IDs")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--render-outline", action="store_true", help="Regenerate the committed seed outline from the bundle")
    parser.add_argument("--seed", help="Seed markdown path for --render-outline (defaults to the template vault copy)")
    args = parser.parse_args()
    from freshness import SEED_SOURCE, expected_seed_notes

    if args.render_outline:
        return render_outline(Path(args.seed).expanduser().resolve() if args.seed else SEED_SOURCE)
    checked = absent = 0
    for line in (MANIFEST.read_text(encoding="utf-8") + RETAINED.read_text(encoding="utf-8")).splitlines():
        if not line.strip():
            continue
        expected, rel = line.split(maxsplit=1)
        path = ROOT / rel
        if path.is_symlink():
            raise SystemExit(f"ERROR: historical seed path is a symlink: {rel}")
        if not path.exists() and BUNDLE_MARKER in f"/{rel}":
            absent += 1
            continue
        if not path.is_file():
            raise SystemExit(f"ERROR: retained asset missing: {rel}")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"ERROR: historical seed drift: {rel}")
        checked += 1
    try:
        notes = expected_seed_notes()
    except (OSError, ValueError, KeyError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    print(
        f"Historical and retained-asset contract passed: {checked} files verified, "
        f"{absent} operator-supplied bundle files not shipped, {len(notes)} outline note IDs"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

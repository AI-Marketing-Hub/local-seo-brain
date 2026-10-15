from __future__ import annotations

import json
import tempfile
from pathlib import Path

from _helpers import AS_OF, ROOT, run, scaffold


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="lsb-privacy-") as value:
        parent = Path(value)
        vault = scaffold(parent)
        private = parent / "reviews.json"
        private.write_text(json.dumps([{
            "author": "Private Fixture Person",
            "rating": 5,
            "date": AS_OF,
            "text": "Prompt and professional service.",
        }]), encoding="utf-8")
        run(
            "scripts/ingest_reviews.py", "--vault", str(vault), "--file", str(private),
            "--client", "test-client", "--as-of", AS_OF,
        )
        derived = "\n".join(
            path.read_text(encoding="utf-8")
            for folder in (vault / "wiki/reviews", vault / "wiki/sources")
            for path in folder.glob("*.md")
        )
        assert "Private Fixture Person" not in derived
        raw = next((vault / ".raw/clients/test-client/reviews").glob("*"))
        assert "Private Fixture Person" in raw.read_text(encoding="utf-8")
        assert "access-controlled" in derived

    refusal_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ("docs/PRODUCT_BOUNDARIES.md", "references/safety-gates.md", "SKILL.md")
    ).lower()
    for phrase in ("virtual-office", "review gating", "pbn", "doorway", "guaranteed ranking"):
        assert phrase in refusal_text
    print("test_privacy_and_refusals.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

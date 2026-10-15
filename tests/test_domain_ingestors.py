from __future__ import annotations

import json
import tempfile
from pathlib import Path

from _helpers import AS_OF, run, scaffold, tree_hash


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="lsb-domains-") as value:
        vault = scaffold(Path(value))
        common = ("--vault", str(vault), "--client", "test-client", "--as-of", AS_OF)
        commands = (
            ("scripts/ingest_gbp.py", "tests/fixtures/sample-gbp.csv"),
            ("scripts/ingest_citations.py", "tests/fixtures/sample-citations.csv"),
            ("scripts/ingest_reviews.py", "tests/fixtures/sample-reviews.json"),
            ("scripts/ingest_geogrid.py", "tests/fixtures/sample-geogrid.csv"),
        )
        for script, fixture in commands:
            run(script, *common, "--file", fixture)
        first = tree_hash(vault)
        for script, fixture in commands:
            run(script, *common, "--file", fixture)
        assert tree_hash(vault) == first, "same-date repeated ingestion must be byte-identical"
        manifest = json.loads((vault / ".raw/.manifest.json").read_text(encoding="utf-8"))
        assert len(manifest["sources"]) == 4
        assert {item["kind"] for item in manifest["sources"]} == {"gbp", "citations", "reviews", "geogrid"}
        assert all(len(item["sha256"]) == 64 for item in manifest["sources"])
        raw_files = [p for p in (vault / ".raw/clients/test-client").rglob("*") if p.is_file()]
        assert len(raw_files) == 4
        citation = (vault / "wiki/citations/test-client-yelp.md").read_text(encoding="utf-8")
        assert "not evaluated" in citation and "requires owner confirmation" in citation
        geogrid = (vault / "wiki/keywords/test-client-plumber-near-me.md").read_text(encoding="utf-8")
        assert "They do not" in geogrid and "identify a cause" in geogrid
    print("test_domain_ingestors.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

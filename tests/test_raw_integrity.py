from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path
from _helpers import AS_OF, ROOT, run, scaffold, file_snapshot
sys.path.insert(0, str(ROOT / "scripts"))
from runtime import vault_mutation


def main():
    fixtures = {"source": "sample-source.md", "gbp": "sample-gbp.csv", "citations": "sample-citations.csv", "reviews": "sample-reviews.json", "geogrid": "sample-geogrid.csv"}
    with tempfile.TemporaryDirectory(prefix="lsb-integrity-") as tmp:
        parent = Path(tmp)
        for kind, filename in fixtures.items():
            vault = scaffold(parent, kind)
            command = (f"scripts/ingest_{kind}.py", "--vault", str(vault), "--client", kind, "--file", str(ROOT / "tests/fixtures" / filename), "--as-of", AS_OF)
            run(*command)
            records = json.loads((vault / ".raw/.manifest.json").read_text())["sources"]
            raw = vault / records[0]["path"]
            raw.write_bytes(b"TAMPERED")
            before = file_snapshot(vault)
            result = run(*command, check=False)
            assert result.returncode and "integrity failed" in result.stderr
            assert file_snapshot(vault) == before
            assert run("scripts/synthesize_brain.py", "--vault", str(vault), "--as-of", AS_OF, check=False).returncode
        vault = scaffold(parent, "symlink")
        external = parent / "external.json"; external.write_text('{"schema":"local-seo-brain.raw-manifest.v1","sources":[]}')
        manifest = vault / ".raw/.manifest.json"; manifest.unlink(); manifest.symlink_to(external)
        before = external.read_bytes()
        result = run("scripts/ingest_source.py", "--vault", str(vault), "--client", "symlink", "--file", str(ROOT / "tests/fixtures/sample-source.md"), "--as-of", AS_OF, "--dry-run", check=False)
        assert result.returncode and external.read_bytes() == before
        vault = scaffold(parent, "historical")
        seed = vault / ".raw/source-material/LOCAL-seo-Knowledge-Base.md"
        seed.parent.mkdir(parents=True, exist_ok=True)
        seed.write_text("corrupt")
        assert run("scripts/synthesize_brain.py", "--vault", str(vault), "--as-of", AS_OF, check=False).returncode
        vault = scaffold(parent, "locked")
        with vault_mutation(vault):
            result = run("scripts/synthesize_brain.py", "--vault", str(vault), "--as-of", AS_OF, check=False)
            assert result.returncode and "another vault mutation" in result.stderr
    print("test_raw_integrity.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

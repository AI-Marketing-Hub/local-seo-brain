from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from _helpers import AS_OF, ROOT, file_snapshot, run, scaffold


def main() -> int:
    raw_seed = ROOT / "assets/template-brain/.raw/source-material/LOCAL-seo-Knowledge-Base.md"
    if not raw_seed.is_file():
        # The third-party bundle is operator-supplied and not shipped. Without it
        # the generator must refuse clearly instead of writing anything.
        with tempfile.TemporaryDirectory(prefix="lsb-reseed-") as value:
            vault = scaffold(Path(value))
            before = file_snapshot(vault)
            result = run("scripts/ingest_knowledge_base.py", "--vault", str(vault), "--as-of", AS_OF, check=False)
            assert result.returncode and "historical seed not found" in result.stderr
            assert file_snapshot(vault) == before
        print("test_reseed_preserves_overlays.py: ok (seed bundle not present, regeneration skipped)")
        return 0
    baseline_seed = hashlib.sha256(raw_seed.read_bytes()).hexdigest()
    overlays = json.loads((ROOT / "data/knowledge-overlays.json").read_text(encoding="utf-8"))["notes"]
    with tempfile.TemporaryDirectory(prefix="lsb-reseed-") as value:
        vault = scaffold(Path(value))
        before = file_snapshot(vault)
        run(
            "scripts/ingest_knowledge_base.py", "--vault", str(vault),
            "--as-of", AS_OF, "--dry-run",
        )
        assert file_snapshot(vault) == before, "dry-run changed a vault"
        command = (
            "scripts/ingest_knowledge_base.py", "--vault", str(vault),
            "--as-of", AS_OF,
        )
        run(*command)
        first = file_snapshot(vault)
        run(*command)
        assert file_snapshot(vault) == first
        generated = [
            path for path in (vault / "wiki").rglob("*.md")
            if "seed_source:" in path.read_text(encoding="utf-8", errors="replace")
        ]
        assert len(generated) == 96
        for path in generated:
            text = path.read_text(encoding="utf-8")
            assert "## Evidence status" in text
            assert "claim_ids:" in text
            rel = path.relative_to(vault).as_posix()
            if overlays[rel].get("mode", "annotate") == "annotate":
                assert "Retained for provenance; not current operating guidance" in text
        assert "staged magnets" not in (vault / "wiki/gbp/gbp-verification.md").read_text(encoding="utf-8").lower()
    assert hashlib.sha256(raw_seed.read_bytes()).hexdigest() == baseline_seed
    print("test_reseed_preserves_overlays.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

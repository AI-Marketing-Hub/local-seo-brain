from __future__ import annotations

import tempfile
from pathlib import Path

from _helpers import AS_OF, ROOT, run, scaffold


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="lsb-pipeline-") as value:
        vault = scaffold(Path(value))
        assert not (vault / ".vault-meta/transactions").exists()
        assert not (ROOT / "assets/template-brain/.vault-meta/transactions").exists()
        import json
        provenance = json.loads((vault / ".vault-meta/template-provenance.json").read_text())
        assert provenance["copied_transaction_history"] is False
        assert len(provenance["template_sha256"]) == 64
        run(
            "scripts/ingest_source.py", "--vault", str(vault),
            "--file", "tests/fixtures/sample-source.md", "--label", "Sample Source",
            "--client", "test-client", "--as-of", AS_OF,
        )
        run("scripts/synthesize_brain.py", "--vault", str(vault), "--as-of", AS_OF)
        run("scripts/generate_vault_visuals.py", "--vault", str(vault))
        run("scripts/render_brain_report.py", "--vault", str(vault), "--html-only")
        run("scripts/lint_vault.py", "--vault", str(vault))
        scorecard = (vault / "wiki/deliverables/Health Scorecard.md").read_text(encoding="utf-8")
        assert "Current score: **Draft**" in scorecard
        assert "evidence/no-data" in scorecard
        assert '\n---\n\n# Health Scorecard\n' in scorecard
        source = next((vault / "wiki/sources").glob("sample-source-*.md")).read_text()
        assert '\n---\n\n# Sample Source\n' in source
        assert all(line == line.rstrip() for line in source.splitlines())
        assert not any(token in scorecard for token in ("Current score: **A", "Current score: **B", "Current score: **C"))
        assert (vault / "test-client-weekly-report.html").is_file()
        assert (vault / ".raw/.manifest.json").is_file()
        assert f'updated: "{AS_OF}"' in (vault / "wiki/sources/_index.md").read_text()
        assert f'updated: "{AS_OF}"' in (vault / "wiki/log.md").read_text()
    print("test_pipeline.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

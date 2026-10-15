from __future__ import annotations

import tempfile
from pathlib import Path

from _helpers import AS_OF, ROOT, file_snapshot, run, scaffold


def main() -> int:
    before = file_snapshot(ROOT)
    scripts = sorted((ROOT / "scripts").glob("*.py"))
    for script in scripts:
        result = run(str(script.relative_to(ROOT)), "--help", check=False)
        assert result.returncode == 0, f"--help failed for {script.name}: {result.stderr}"
    assert file_snapshot(ROOT) == before, "--help changed repository files"
    for shell_script in ("install.sh", "uninstall.sh"):
        result = run("-c", f"import subprocess; raise SystemExit(subprocess.run(['bash', '{shell_script}', '--help']).returncode)")
        assert result.returncode == 0

    with tempfile.TemporaryDirectory(prefix="lsb-cli-") as value:
        parent = Path(value)
        target = parent / "dry-client"
        run(
            "scripts/scaffold_vault.py", "--client", "dry-client", "--owner", "Owner",
            "--out-dir", str(parent), "--as-of", AS_OF, "--dry-run",
        )
        assert not target.exists()
        vault = scaffold(parent, "live-client")
        snapshot = file_snapshot(vault)
        common = ("--vault", str(vault), "--client", "live-client", "--as-of", AS_OF, "--dry-run")
        for script, fixture in (
            ("scripts/ingest_source.py", "tests/fixtures/sample-source.md"),
            ("scripts/ingest_gbp.py", "tests/fixtures/sample-gbp.csv"),
            ("scripts/ingest_citations.py", "tests/fixtures/sample-citations.csv"),
            ("scripts/ingest_reviews.py", "tests/fixtures/sample-reviews.json"),
            ("scripts/ingest_geogrid.py", "tests/fixtures/sample-geogrid.csv"),
        ):
            run(script, *common, "--file", fixture)
        run("scripts/synthesize_brain.py", "--vault", str(vault), "--as-of", AS_OF, "--dry-run")
        run("scripts/generate_vault_visuals.py", "--vault", str(vault), "--dry-run")
        run("scripts/render_brain_report.py", "--vault", str(vault), "--dry-run")
        assert file_snapshot(vault) == snapshot, "a dry-run changed the vault"

    blocked = run(
        "scripts/scaffold_vault.py", "--client", "unsafe", "--owner", "Owner",
        "--out-dir", str(ROOT / "examples"), "--as-of", AS_OF,
        check=False,
    )
    assert blocked.returncode != 0 and "refusing tracked-worktree target" in blocked.stderr
    with tempfile.TemporaryDirectory(prefix="lsb-recovery-") as value:
        base = Path(value)
        vault = scaffold(base)
        command = ("scripts/uninstall_vault.py", "--vault", str(vault), "--confirm", "MOVE_TO_TRASH")
        assert run(*command, "--trash-dir", str(vault / "recovery"), "--dry-run", check=False).returncode
        recovery = base / "recovery"
        run(*command, "--trash-dir", str(recovery), "--dry-run")
        assert vault.is_dir() and not recovery.exists()
        run(*command, "--trash-dir", str(recovery))
        assert not vault.exists() and (recovery / vault.name / "wiki").is_dir()
    print("test_cli_safety.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

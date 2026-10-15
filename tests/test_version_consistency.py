from __future__ import annotations

import json
import re
import tomllib

from _helpers import ROOT


def main() -> int:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    version = project["project"]["version"]
    marketplace = json.loads((ROOT / "marketplace.json").read_text(encoding="utf-8"))
    plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert version == "0.3.0"
    assert marketplace["version"] == plugin["version"] == version
    assert f"Version: {version}" in readme
    assert re.search(rf"^## {re.escape(version)}\s", changelog, re.M)
    assert project["project"]["requires-python"] == marketplace["compatible_with"]["python"] == ">=3.11"
    print("test_version_consistency.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

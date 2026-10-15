from __future__ import annotations

import json
import re

from _helpers import ROOT, run


def main() -> int:
    template = ROOT / "assets/template-brain/wiki"
    overlays = json.loads((ROOT / "data/knowledge-overlays.json").read_text(encoding="utf-8"))
    chapter_paths = [path for path in overlays["notes"] if "/prompts/" not in path]
    prompt_paths = [path for path in overlays["notes"] if "/prompts/" in path]
    assert len(chapter_paths) == 59
    assert len(prompt_paths) == 37
    assert len(list((template / "freshness").glob("2026-*.md"))) == 6
    assert all((ROOT / "assets/template-brain" / path).is_file() for path in overlays["notes"])
    matrix = (ROOT / "references/claim-coverage-matrix.md").read_text(encoding="utf-8")
    assert "Coverage: 59 chapters, 37 prompts, 6 freshness notes" in matrix
    assert all(f"`assets/template-brain/{path}`" in matrix for path in overlays["notes"])

    docs = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in ("README.md", "SKILL.md", "marketplace.json", "docs/OPERATOR_KIT.md", "references/product-spec.md")
    )
    forbidden = (
        r"60\s*(?:to|-)\s*70% of local clicks",
        r"roughly 40% of LLM citation",
        r"2[x×]\s*weekly.*mandatory",
        r"every recommendation links to the raw export",
        r"the vault converges, never doubles",
    )
    for pattern in forbidden:
        assert not re.search(pattern, docs, re.I), pattern
    for line in docs.splitlines():
        if re.search(r"guarantee(?:d)?\s+(?:a\s+)?(?:#?1|ranking|map pack)", line, re.I):
            context = line.lower()
            assert any(term in context for term in ("no ", "refuse", "refusal", "does not", "without")), context
    assert "59 chapters" in docs and "37" in docs
    assert "Draft" in docs and "does not" in docs
    run("scripts/working_content_contract.py")
    print("test_documentation_claims.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

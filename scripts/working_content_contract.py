#!/usr/bin/env python3
"""Verify overlay persistence, task specificity, citations, and working navigation."""
from __future__ import annotations
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    vault = ROOT / "assets/template-brain"
    overlays = json.loads((ROOT / "data/knowledge-overlays.json").read_text())["notes"]
    notes = list((vault / "wiki").rglob("*.md"))
    names = {p.stem.casefold(): p for p in notes}
    names.update({p.relative_to(vault).with_suffix("").as_posix().casefold(): p for p in notes})
    edges, failures = {}, []
    for p in notes:
        text = p.read_text()
        targets = [s.split("|", 1)[0].split("#", 1)[0].strip().casefold() for s in re.findall(r"!?\[\[([^\]]+)\]\]", text)]
        edges[p] = [names[s] for s in targets if s in names]
        if any(n > 1 for n in Counter(targets).values()):
            failures.append(f"duplicate links: {p.relative_to(vault)}")
    for rel, entry in overlays.items():
        text = (vault / rel).read_text()
        if entry["replacement_body"] not in text or "## Historical seed material" in text or "sources: ." in text:
            failures.append(f"overlay content drift: {rel}")
        if "/prompts/" in rel:
            if any(s not in text for s in ("## Task", "## Required inputs", "## Output and acceptance")) or "Produce a Draft for" in text:
                failures.append(f"incomplete prompt: {rel}")
    contracts = []
    for rel, entry in overlays.items():
        if "/prompts/" not in rel:
            match = re.search(r'Inputs: (.*?)\n\nResult: (.*?)(?=\n\n|$)', entry["replacement_body"], re.S)
            if not match:
                failures.append(f"missing chapter task contract: {rel}")
            else:
                contracts.append(match.groups())
    if len(contracts) != len(set(contracts)):
        failures.append("duplicate chapter task contracts")
    all_text = "\n".join(p.read_text() for p in notes)
    for path in (vault / "_attachments").rglob("*"):
        if path.is_file() and path.name not in all_text:
            failures.append(f"unreferenced active attachment: {path.relative_to(vault)}")
    if "paa-question-rewording-prompt" not in (vault / "wiki/concepts/keyword-research.md").read_text() or "paa-question-rewording-prompt" in (vault / "wiki/audits/property-audit-part-2.md").read_text():
        failures.append("customer-question prompt in wrong task chapter")
    root = vault / "wiki/index.md"
    reached, frontier = {root}, {root}
    for _ in range(2):
        frontier = {q for p in frontier for q in edges[p]} - reached
        reached.update(frontier)
    failures += [f"note beyond two hops: {p.relative_to(vault)}" for p in notes if p not in reached]
    if failures:
        print("\n".join(failures))
        return 1
    print(f"Working content contract passed: {len(overlays)} notes, exact overlays, task prompts, citations, two-hop navigation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

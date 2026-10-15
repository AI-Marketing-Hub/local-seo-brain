"""Read-only evidence age, deadline, dependency, and overlay contracts."""
from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def policy() -> dict:
    data = json.loads((ROOT / "references/freshness-policy.json").read_text())
    if data.get("schema") != "local-seo-brain.freshness-policy.v1" or data.get("default_days") != 30:
        raise ValueError("invalid freshness policy")
    if not isinstance(data.get("source_days"), dict) or any(type(v) is not int or v not in {7, 14} for v in data["source_days"].values()):
        raise ValueError("invalid source review intervals")
    return data


def source_interval(source_id: str) -> int:
    rules = policy()
    return rules["source_days"].get(source_id, rules["default_days"])


def check_deadline(verified: str, due: str, days: int, label: str) -> None:
    if not isinstance(verified, str) or not isinstance(due, str):
        raise ValueError(f"{label}: dates must be ISO strings")
    start, end = date.fromisoformat(verified), date.fromisoformat(due)
    if not start < end <= start + timedelta(days=days):
        raise ValueError(f"{label}: refresh_due must be after verification and within {days} days")


SEED_SOURCE = ROOT / "assets/template-brain/.raw/source-material/LOCAL-seo-Knowledge-Base.md"
SEED_OUTLINE = ROOT / "references/historical-seed-outline.json"
SEED_OUTLINE_SCHEMA = "local-seo-brain.historical-seed-outline.v1"


def seed_notes_from_text(raw: str) -> set[str]:
    """Generated note IDs that the historical seed produces, without its text."""
    from ingest_knowledge_base import split_by_h1, strip_base64_refs, clean_chapter_title, normalize_key, classify, title_to_slug, extract_prompts
    expected_paths: set[str] = set()
    for title, body in split_by_h1(strip_base64_refs(raw)):
        title = clean_chapter_title(title)
        folder = classify(normalize_key(title)) if title else None
        if folder:
            expected_paths.add(f"wiki/{folder}/{title_to_slug(title)}.md")
            expected_paths.update(f"wiki/prompts/{title_to_slug(p[0])}.md" for p in extract_prompts(body)[1])
    return expected_paths


def load_seed_outline() -> dict:
    data = json.loads(SEED_OUTLINE.read_text(encoding="utf-8"))
    if data.get("schema") != SEED_OUTLINE_SCHEMA or not isinstance(data.get("notes"), list) or not isinstance(data.get("seed_sha256"), str):
        raise ValueError("invalid historical seed outline")
    return data


def expected_seed_notes() -> set[str]:
    """Expected overlay note IDs.

    The historical course bundle is third-party material and is not shipped.
    When an operator has placed it under `.raw/source-material/`, the IDs are
    derived from its text and must match the committed outline. Otherwise the
    committed outline is the contract.
    """
    outline = set(load_seed_outline()["notes"])
    if SEED_SOURCE.is_file():
        derived = seed_notes_from_text(SEED_SOURCE.read_text(encoding="utf-8"))
        if derived != outline:
            raise ValueError("historical seed outline drift; rerun scripts/historical_seed_contract.py --render-outline")
    return outline


def validate_overlays(data: dict, claims: dict, sources: dict, *, expected_as_of: str | None = None) -> None:
    if data.get("schema") != "local-seo-brain.knowledge-overlays.v1" or not isinstance(data.get("notes"), dict):
        raise ValueError("invalid overlay schema")
    snapshot = date.fromisoformat(data["as_of"])
    expected_as_of = expected_as_of or max(c["verified_at"] for c in claims.values())
    if data["as_of"] != expected_as_of:
        raise ValueError("overlay snapshot differs from evidence snapshot")
    expected_paths = expected_seed_notes()
    if set(data["notes"]) != expected_paths:
        raise ValueError("unknown or missing overlay note IDs for the immutable seed")
    if set(policy()["source_days"]) - set(sources):
        raise ValueError("freshness policy references unknown sources")
    for path, note in data["notes"].items():
        if not path.startswith("wiki/") or ".." in Path(path).parts:
            raise ValueError(f"unsafe overlay path: {path}")
        if note.get("task_parent") and (note["task_parent"] not in expected_paths or "/prompts/" in note["task_parent"] or "/prompts/" not in path):
            raise ValueError(f"{path}: invalid task parent")
        if date.fromisoformat(note["verified_at"]) > snapshot:
            raise ValueError(f"{path}: future overlay verification")
        if note["assessment"] not in {"accepted", "provisional", "contested", "unsupported", "deprecated"} or note["confidence"] not in {"EVIDENCE-BASED", "PRACTITIONER", "CONTESTED", "FOLKLORE"}:
            raise ValueError(f"{path}: invalid assessment or confidence")
        ids = note["claim_ids"]
        if not isinstance(ids, list) or not ids or len(set(ids)) != len(ids) or set(ids) - set(claims):
            raise ValueError(f"{path}: unknown or missing overlay claim IDs")
        if note.get("mode") != "replace" or not note.get("replacement_body", "").strip():
            raise ValueError(f"{path}: working notes require replacement content")
        check_deadline(note["verified_at"], note["refresh_due"], policy()["default_days"], path)
        if note["refresh_due"] > min(claims[c]["refresh_due"] for c in ids):
            raise ValueError(f"{path}: overlay outlives a claim")
        for callout in note.get("callouts", []):
            if set(callout["claim_ids"]) - set(ids):
                raise ValueError(f"{path}: callout claim absent from overlay dependencies")
            if set(callout["claim_ids"]) - set(claims) or set(callout["source_ids"]) - set(sources):
                raise ValueError(f"{path}: unknown callout evidence ID")
            related = {s for c in callout["claim_ids"] for s in claims[c]["source_ids"] + claims[c]["contradicting_source_ids"]}
            if set(callout["source_ids"]) - related:
                raise ValueError(f"{path}: unrelated callout source")
        for cid in ids:
            if not any(loc.partition("#")[0] == f"assets/template-brain/{path}" for loc in claims[cid]["locations"]):
                raise ValueError(f"{path}: claim {cid} lacks reverse location")


def evaluate(source_data: dict, claim_data: dict, overlays: dict, as_of: date) -> dict:
    if as_of < date.fromisoformat(source_data["as_of"]):
        raise ValueError("evaluation date precedes evidence snapshot")
    sources = {s["id"]: s for s in source_data["sources"]}
    claims = {c["id"]: c for c in claim_data["claims"]}
    rows = []
    def add(kind: str, key: str, due: str, usable: bool = True) -> None:
        deadline = date.fromisoformat(due)
        state = "needs_input" if not usable else "overdue" if as_of > deadline else "due" if as_of == deadline else "fresh"
        rows.append({"kind": kind, "id": key, "refresh_due": due, "state": state})
    for s in sources.values():
        if s["review_state"] == "active":
            add("source", s["id"], s["refresh_due"])
    for c in claims.values():
        if c["assessment"] == "deprecated":
            continue
        deps = [sources[s] for s in c["source_ids"] + c["contradicting_source_ids"]]
        usable = all(s["review_state"] == "active" for s in deps)
        due = min([c["refresh_due"]] + [s["refresh_due"] for s in deps])
        add("claim", c["id"], due, usable)
    for path, note in overlays["notes"].items():
        dependencies = [r for r in rows if r["kind"] == "claim" and r["id"] in note["claim_ids"]]
        usable = len(dependencies) == len(note["claim_ids"]) and all(r["state"] != "needs_input" for r in dependencies)
        due = min([note["refresh_due"]] + [r["refresh_due"] for r in dependencies])
        add("overlay", path, due, usable)
    actionable = [r for r in rows if r["state"] != "fresh"]
    return {"schema": "local-seo-brain.freshness.v1", "as_of": as_of.isoformat(),
            "snapshot_as_of": source_data["as_of"], "ok": not actionable,
            "records": rows, "actionable": actionable}

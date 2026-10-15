from __future__ import annotations
import copy
import json
import sys
from datetime import date, timedelta
from pathlib import Path
from _helpers import AS_OF, ROOT, run
sys.path.insert(0, str(ROOT / "scripts"))
import evidence_contract as ec
import freshness as f


def rejects(fn):
    try:
        fn()
    except (ValueError, ec.ContractError):
        return
    raise AssertionError("invalid evidence accepted")


def main():
    sources = json.loads((ROOT / "references/source-ledger.json").read_text())
    claims = json.loads((ROOT / "references/claim-ledger.json").read_text())
    overlay = json.loads((ROOT / "data/knowledge-overlays.json").read_text())
    sm = {s["id"]: s for s in sources["sources"]}
    cm = {c["id"]: c for c in claims["claims"]}
    today = date.fromisoformat(AS_OF)
    assert f.evaluate(sources, claims, overlay, today)["ok"]
    due = date.fromisoformat(sm["google-search-doc-updates"]["refresh_due"])
    result = f.evaluate(sources, claims, overlay, due)
    assert not result["ok"] and any(r["state"] == "due" for r in result["actionable"])
    assert any(r["state"] == "overdue" for r in f.evaluate(sources, claims, overlay, due + timedelta(days=1))["actionable"])
    rejects(lambda: f.evaluate(sources, claims, overlay, today - timedelta(days=1)))
    bad = copy.deepcopy(sources); bad["sources"][0]["refresh_due"] = "2099-12-31"
    rejects(lambda: ec.validate_source_ledger(bad, today))
    for field, value in [("date", "2099-12-31"), ("updated_at", "2099-12-31"), ("refresh_result", "unavailable")]:
        bad = copy.deepcopy(sources); bad["sources"][0][field] = value
        rejects(lambda: ec.validate_source_ledger(bad, today))
    bad_overlay = copy.deepcopy(overlay); first = next(iter(bad_overlay["notes"].values())); first["claim_ids"] = ["invented-claim"]
    rejects(lambda: f.validate_overlays(bad_overlay, cm, sm))
    bad_overlay = copy.deepcopy(overlay)
    bad_overlay["notes"]["wiki/prompts/invented-note.md"] = copy.deepcopy(next(iter(bad_overlay["notes"].values())))
    rejects(lambda: f.validate_overlays(bad_overlay, cm, sm))
    bad_overlay = copy.deepcopy(overlay)
    bad_overlay["notes"]["wiki/prompts/paa-question-rewording-prompt.md"]["task_parent"] = "wiki/concepts/invented-parent.md"
    rejects(lambda: f.validate_overlays(bad_overlay, cm, sm))
    bad_overlay = copy.deepcopy(overlay); bad_overlay["schema"] = "wrong"
    rejects(lambda: f.validate_overlays(bad_overlay, cm, sm))
    for field, value in [("as_of", "2099-01-01"), ("schema", "wrong")]:
        bad_overlay = copy.deepcopy(overlay); bad_overlay[field] = value
        rejects(lambda: f.validate_overlays(bad_overlay, cm, sm))
    for field, value in [("assessment", "banana"), ("confidence", "???")]:
        bad_overlay = copy.deepcopy(overlay); next(iter(bad_overlay["notes"].values()))[field] = value
        rejects(lambda: f.validate_overlays(bad_overlay, cm, sm))
    review = json.loads((ROOT / "references/source-review-2026-10-15.json").read_text())
    assert len(review["reviews"]) == len(sm) == len({r["source_id"] for r in review["reviews"]})
    for row in review["reviews"]:
        assert row["source_id"] in sm and all(row.get(k) for k in ("reviewed_at", "result", "locator", "scope", "inspected_url"))
        assert row["result"] == sm[row["source_id"]]["refresh_result"]
    broken = copy.deepcopy(claims); broken["claims"][0]["contradicting_source_ids"] = broken["claims"][0]["source_ids"][:]
    rejects(lambda: ec.validate_claim_ledger(broken, sm, today))
    # Negative-evidence assertions must age with their contradicting sources.
    negative = copy.deepcopy(claims); target = negative["claims"][0]
    target.update(assessment="unsupported", source_ids=[], contradicting_source_ids=["google-search-doc-updates"])
    row = next(r for r in f.evaluate(sources, negative, overlay, due)["records"] if r["kind"] == "claim" and r["id"] == target["id"])
    assert row["state"] == "due"
    assert run("scripts/evidence_contract.py", "freshness", "--as-of", "invalid", check=False).returncode == 2
    result = run("scripts/guide_next_action.py", "--vault", "assets/template-brain", "--as-of", (due + timedelta(days=1)).isoformat(), check=False)
    assert result.returncode == 1 and "refresh evidence" in result.stdout
    print("test_freshness.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

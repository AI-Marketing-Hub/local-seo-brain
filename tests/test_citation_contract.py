from __future__ import annotations

import copy
import sys
import importlib.util
import json
from datetime import date

from _helpers import AS_OF, ROOT, run
sys.path.insert(0, str(ROOT / "scripts"))


def load_contract():
    spec = importlib.util.spec_from_file_location("evidence_contract", ROOT / "scripts/evidence_contract.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    run("scripts/evidence_contract.py", "validate", "--as-of", AS_OF)
    run(
        "scripts/evidence_contract.py", "check", "--as-of", AS_OF,
        "--vault", "assets/template-brain",
    )
    contract = load_contract()
    sources = json.loads((ROOT / "references/source-ledger.json").read_text(encoding="utf-8"))
    claims = json.loads((ROOT / "references/claim-ledger.json").read_text(encoding="utf-8"))
    by_source, stale_sources = contract.validate_source_ledger(sources, date.fromisoformat(AS_OF))
    assert not stale_sources
    _, stale_claims = contract.validate_claim_ledger(claims, by_source, date.fromisoformat(AS_OF))
    assert not stale_claims

    expired = copy.deepcopy(sources)
    expired["sources"][0]["refresh_due"] = "2026-07-17"
    try:
        contract.validate_source_ledger(expired, date.fromisoformat(AS_OF))
    except ValueError as exc:
        assert "refresh_due" in str(exc)
    else:
        raise AssertionError("invalid deadline ordering accepted")

    broken = copy.deepcopy(claims)
    target = next(item for item in broken["claims"] if item["risk"] == "high" and item.get("claim_type") != "policy" and item["assessment"] == "accepted")
    target["source_ids"] = target["source_ids"][:1]
    try:
        contract.validate_claim_ledger(broken, by_source, date.fromisoformat(AS_OF))
    except contract.ContractError as exc:
        assert "two independent" in str(exc)
    else:
        raise AssertionError("high-risk independence failure was accepted")
    print("test_citation_contract.py: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

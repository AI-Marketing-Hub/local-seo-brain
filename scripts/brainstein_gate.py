#!/usr/bin/env python3
"""Enforce the release-level Brainstein anatomy contract on saved audit JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit_json")
    args = parser.parse_args()
    path = Path(args.audit_json).expanduser().resolve()
    data = json.loads(path.read_text(encoding="utf-8"))
    anatomy = data.get("brain_anatomy") or {}
    failures = []
    if anatomy.get("total_score", 0) < 90:
        failures.append(f"anatomy score {anatomy.get('total_score')} < 90")
    if anatomy.get("grade") != "SSS+":
        failures.append(f"grade is {anatomy.get('grade')!r}, expected 'SSS+'")
    if anatomy.get("maturity") != "market-ready":
        failures.append(f"maturity is {anatomy.get('maturity')!r}, expected 'market-ready'")
    if data.get("market_ready") is not True:
        failures.append("market_ready is not true")
    critical = data.get("critical_failures") or []
    if critical:
        failures.append(f"{len(critical)} critical failure(s)")
    if failures:
        raise SystemExit("ERROR: Brainstein gate failed: " + "; ".join(failures))
    print("Brainstein release gate passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

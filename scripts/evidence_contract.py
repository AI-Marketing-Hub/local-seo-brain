#!/usr/bin/env python3
"""Validate canonical evidence and render deterministic ledger projections."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit
from freshness import check_deadline, source_interval, validate_overlays, evaluate


ROOT = Path(__file__).resolve().parent.parent
SOURCE_LEDGER = ROOT / "references" / "source-ledger.json"
CLAIM_LEDGER = ROOT / "references" / "claim-ledger.json"
CLAIM_MARKDOWN = ROOT / "references" / "claim-ledger.md"

SOURCE_TYPES = {
    "official-doc", "primary-research", "first-party-blog", "standard",
    "independent-study", "practitioner", "community",
}
AUTHORITIES = {"official", "primary", "secondary", "community", "synthetic", "unknown"}
SOURCE_STATES = {"unreviewed", "active", "superseded", "rejected"}
ASSESSMENTS = {"accepted", "provisional", "contested", "unsupported", "deprecated"}
CONFIDENCE = {"EVIDENCE-BASED", "PRACTITIONER", "CONTESTED", "FOLKLORE"}
RISKS = {"high", "medium", "low"}
CLAIM_TYPES = {"policy", "product", "empirical", "recommendation", "historical"}
SHA256_RE = re.compile(r"^[a-f0-9]{64}$")
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9.-]*$")


class ContractError(ValueError):
    pass


def parse_iso(value: object, label: str, *, nullable: bool = False) -> date | None:
    if value is None and nullable:
        return None
    if not isinstance(value, str):
        raise ContractError(f"{label}: expected ISO date string")
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ContractError(f"{label}: invalid ISO date {value!r}") from exc


def load_object(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ContractError(f"missing {path.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ContractError(f"{path.relative_to(ROOT)}:{exc.lineno}: invalid JSON: {exc.msg}") from exc
    if not isinstance(data, dict):
        raise ContractError(f"{path.relative_to(ROOT)}: top level must be an object")
    return data


def require_keys(record: dict, keys: set[str], label: str) -> None:
    missing = sorted(keys - set(record))
    if missing:
        raise ContractError(f"{label}: missing {', '.join(missing)}")


def canonical_url(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise ContractError(f"{label}: URL must be a string")
    parts = urlsplit(value)
    if parts.scheme != "https" or not parts.netloc:
        raise ContractError(f"{label}: URL must be absolute HTTPS")
    if parts.fragment:
        raise ContractError(f"{label}: canonical URL must not contain a fragment")
    return value


def validate_source_ledger(data: dict, as_of: date) -> tuple[dict[str, dict], list[str]]:
    if data.get("schema") != "local-seo-brain.source-ledger.v1":
        raise ContractError("source ledger: unsupported schema")
    if parse_iso(data.get("as_of"), "source ledger as_of") != as_of:
        raise ContractError("source ledger as_of must match --as-of")
    sources = data.get("sources")
    if not isinstance(sources, list) or not sources:
        raise ContractError("source ledger: sources must be a non-empty array")
    required = {
        "id", "url", "title", "publisher", "date", "updated_at", "retrieved",
        "retrieved_at", "last_verified", "refresh_due", "source_type", "authority",
        "review_state", "independence_key", "jurisdiction", "payload_sha256",
        "raw_path", "supports_claims", "locator",
    }
    by_id: dict[str, dict] = {}
    stale: list[str] = []
    seen_urls: dict[str, str] = {}
    for index, source in enumerate(sources, start=1):
        label = f"source #{index}"
        if not isinstance(source, dict):
            raise ContractError(f"{label}: must be an object")
        require_keys(source, required, label)
        source_id = source["id"]
        if not isinstance(source_id, str) or not SLUG_RE.fullmatch(source_id):
            raise ContractError(f"{label}: invalid id")
        if source_id in by_id:
            raise ContractError(f"{label}: duplicate id {source_id}")
        url = canonical_url(source["url"], label)
        if url in seen_urls:
            raise ContractError(f"{label}: duplicate canonical URL also used by {seen_urls[url]}")
        seen_urls[url] = source_id
        for key in ("title", "publisher", "independence_key", "jurisdiction", "locator"):
            if not isinstance(source[key], str) or not source[key].strip():
                raise ContractError(f"{label}: {key} must be non-empty")
        published = parse_iso(source["date"], f"{label} date", nullable=True)
        updated = parse_iso(source["updated_at"], f"{label} updated_at", nullable=True)
        retrieved = parse_iso(source["retrieved"], f"{label} retrieved")
        retrieved_at = parse_iso(source["retrieved_at"], f"{label} retrieved_at")
        verified = parse_iso(source["last_verified"], f"{label} last_verified")
        refresh = parse_iso(source["refresh_due"], f"{label} refresh_due")
        check_deadline(source["last_verified"], source["refresh_due"], source_interval(source_id), label)
        if retrieved > verified:
            raise ContractError(f"{label}: retrieval is after verification")
        if retrieved != retrieved_at:
            raise ContractError(f"{label}: retrieved compatibility alias differs from retrieved_at")
        if (published and updated and published > updated) or any(d and d > retrieved for d in (published, updated)):
            raise ContractError(f"{label}: impossible publication/update/retrieval ordering")
        if any(value and value > as_of for value in (retrieved, verified)):
            raise ContractError(f"{label}: verification date is after --as-of")
        if source["source_type"] not in SOURCE_TYPES:
            raise ContractError(f"{label}: unsupported source_type")
        if source["authority"] not in AUTHORITIES:
            raise ContractError(f"{label}: unsupported authority")
        if source["review_state"] not in SOURCE_STATES:
            raise ContractError(f"{label}: unsupported review_state")
        if source.get("refresh_result") == "unavailable" and source["review_state"] == "active":
            raise ContractError(f"{label}: unavailable source cannot support current advice")
        digest = source["payload_sha256"]
        if digest is not None and (not isinstance(digest, str) or not SHA256_RE.fullmatch(digest)):
            raise ContractError(f"{label}: invalid payload_sha256")
        if source["raw_path"] is not None and not isinstance(source["raw_path"], str):
            raise ContractError(f"{label}: raw_path must be string or null")
        if not isinstance(source["supports_claims"], list) or not all(isinstance(v, str) for v in source["supports_claims"]):
            raise ContractError(f"{label}: supports_claims must be a string array")
        if source["review_state"] == "active" and refresh and refresh <= as_of:
            stale.append(source_id)
        by_id[source_id] = source
    return by_id, stale


def validate_claim_ledger(data: dict, sources: dict[str, dict], as_of: date, *, vault: Path | None = None) -> tuple[dict[str, dict], list[str]]:
    if data.get("schema") != "local-seo-brain.claim-ledger.v1":
        raise ContractError("claim ledger: unsupported schema")
    if parse_iso(data.get("as_of"), "claim ledger as_of") != as_of:
        raise ContractError("claim ledger as_of must match --as-of")
    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ContractError("claim ledger: claims must be a non-empty array")
    required = {
        "id", "statement", "locations", "risk", "assessment", "confidence",
        "source_ids", "contradicting_source_ids", "scope", "verified_at",
        "refresh_due", "owner", "notes",
    }
    by_id: dict[str, dict] = {}
    stale: list[str] = []
    for index, claim in enumerate(claims, start=1):
        label = f"claim #{index}"
        if not isinstance(claim, dict):
            raise ContractError(f"{label}: must be an object")
        require_keys(claim, required, label)
        claim_id = claim["id"]
        if not isinstance(claim_id, str) or not SLUG_RE.fullmatch(claim_id):
            raise ContractError(f"{label}: invalid id")
        if claim_id in by_id:
            raise ContractError(f"{label}: duplicate id {claim_id}")
        if not isinstance(claim["statement"], str) or not claim["statement"].strip():
            raise ContractError(f"{label}: statement must be non-empty")
        if not isinstance(claim["locations"], list) or not claim["locations"] or not all(isinstance(v, str) and v for v in claim["locations"]):
            raise ContractError(f"{label}: locations must be a non-empty string array")
        for location in claim["locations"]:
            rel, _, anchor = location.partition("#")
            rel_path = Path(rel)
            if rel_path.is_absolute() or ".." in rel_path.parts:
                raise ContractError(f"{label}: unsafe location {location!r}")
            target = ROOT / rel_path
            prefix = Path("assets/template-brain")
            if vault is not None and rel_path.is_relative_to(prefix):
                target = vault / rel_path.relative_to(prefix)
            if not target.is_file():
                raise ContractError(f"{label}: location path does not exist: {rel}")
            if anchor:
                text = target.read_text(encoding="utf-8", errors="replace")
                headings = {
                    re.sub(r"\s+#+\s*$", "", match.group(1)).strip().casefold()
                    for match in re.finditer(r"^#{1,6}\s+(.+)$", text, flags=re.M)
                }
                if anchor.strip().casefold() not in headings:
                    raise ContractError(f"{label}: location heading does not exist: {location}")
        if claim["risk"] not in RISKS or claim["assessment"] not in ASSESSMENTS or claim["confidence"] not in CONFIDENCE:
            raise ContractError(f"{label}: invalid risk, assessment, or confidence")
        claim_type = claim.get("claim_type", "empirical")
        if claim_type not in CLAIM_TYPES:
            raise ContractError(f"{label}: invalid claim_type")
        for key in ("source_ids", "contradicting_source_ids"):
            if not isinstance(claim[key], list) or not all(isinstance(v, str) for v in claim[key]):
                raise ContractError(f"{label}: {key} must be a string array")
            missing = sorted(set(claim[key]) - set(sources))
            if missing:
                raise ContractError(f"{label}: unknown source ids: {', '.join(missing)}")
        if set(claim["source_ids"]) & set(claim["contradicting_source_ids"]):
            raise ContractError(f"{label}: source cannot both support and contradict")
        for key in ("source_ids", "contradicting_source_ids", "locations"):
            if len(set(claim[key])) != len(claim[key]):
                raise ContractError(f"{label}: duplicate {key}")
        verified = parse_iso(claim["verified_at"], f"{label} verified_at")
        refresh = parse_iso(claim["refresh_due"], f"{label} refresh_due")
        if verified and verified > as_of:
            raise ContractError(f"{label}: verified_at is after --as-of")
        check_deadline(claim["verified_at"], claim["refresh_due"], 30, label)
        if claim["source_ids"] + claim["contradicting_source_ids"] and refresh > min(parse_iso(sources[s]["refresh_due"], s) for s in claim["source_ids"] + claim["contradicting_source_ids"]):
            raise ContractError(f"{label}: claim outlives its sources")
        if claim["assessment"] in {"accepted", "provisional", "contested", "unsupported"} and refresh and refresh <= as_of:
            stale.append(claim_id)
        active_sources = [sources[sid] for sid in claim["source_ids"] if sources[sid]["review_state"] == "active"]
        if claim["assessment"] == "accepted":
            if any(sources[s]["review_state"] != "active" or sources[s]["refresh_due"] <= as_of.isoformat() for s in claim["source_ids"]):
                raise ContractError(f"{label}: accepted claim requires fresh active support")
            if not active_sources:
                raise ContractError(f"{label}: accepted claim has no active source")
            if claim["risk"] == "high" and claim_type != "policy":
                independent = {source["independence_key"] for source in active_sources}
                if len(independent) < 2:
                    raise ContractError(f"{label}: high-risk accepted non-policy claim needs two independent active sources")
            if claim["risk"] == "high" and claim_type == "policy" and not any(source["authority"] == "official" for source in active_sources):
                raise ContractError(f"{label}: high-risk accepted policy claim needs an active official source")
        by_id[claim_id] = claim
    for source_id, source in sources.items():
        unknown = sorted(set(source["supports_claims"]) - set(by_id))
        if unknown:
            raise ContractError(f"source {source_id}: supports unknown claims: {', '.join(unknown)}")
    for claim in by_id.values():
        for sid in claim["source_ids"] + claim["contradicting_source_ids"]:
            if claim["id"] not in sources[sid]["supports_claims"]:
                raise ContractError(f"{claim['id']}: missing reverse source relationship {sid}")
    for sid, source in sources.items():
        for cid in source["supports_claims"]:
            if sid not in by_id[cid]["source_ids"] + by_id[cid]["contradicting_source_ids"]:
                raise ContractError(f"{sid}: unrelated claim {cid}")
    return by_id, stale


def json_text(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def markdown_text(claims: list[dict]) -> str:
    lines = [
        "# Claim Ledger",
        "",
        "Generated from `references/claim-ledger.json`. Do not edit this projection independently.",
        "",
        "High-risk accepted empirical claims require a second independent active source. `SINGLE-SOURCE` marks claims that have fewer than two listed supporting sources; direct official policy may legitimately remain single-source when no operational inference is added.",
        "",
        "| Claim | Statement | Risk | Verdict | Confidence | Sources | Second source | Locations | Refresh due |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for claim in sorted(claims, key=lambda item: item["id"]):
        statement = claim["statement"].replace("|", "\\|").replace("\n", " ")
        locations = "<br>".join(claim["locations"]).replace("|", "\\|")
        source_ids = claim["source_ids"]
        second = "SECOND SOURCE" if len(source_ids) >= 2 else "SINGLE-SOURCE"
        lines.append(
            f"| {claim['id']} | {statement} | {claim['risk']} | {claim['assessment']} | "
            f"{claim['confidence']} | {', '.join(source_ids) or 'none'} | {second} | "
            f"{locations} | {claim['refresh_due']} |"
        )
    return "\n".join(lines) + "\n"


def research_pack_text(sources: list[dict], as_of: date) -> str:
    lines = [
        "---",
        'type: "source-pack"',
        'title: "Local SEO Evidence Research Pack"',
        f'created: "{as_of.isoformat()}"',
        f'updated: "{as_of.isoformat()}"',
        'status: "active"',
        'tags: ["type/source-pack", "domain/local-seo", "provenance/ledger"]',
        "---",
        "",
        "# Local SEO Evidence Research Pack",
        "",
        "This projection lists reviewed source metadata. Direct statements, inference, policy, and recommendations remain separated in the canonical claim ledger. Quotes are verified and attributed; otherwise source summaries are paraphrases.",
        "",
        "## Sources",
        "",
    ]
    for source in sorted(sources, key=lambda item: item["id"]):
        date_value = source["date"] or "date unavailable"
        lines.append(
            f"- **{source['id']}**: [{source['title']}]({source['url']}) - {source['publisher']}; "
            f"published: {date_value}; updated: {source['updated_at'] or 'date unavailable'}; verified: {source['last_verified']}; "
            f"refresh due: {source['refresh_due']}; authority: {source['authority']}; "
            f"locator: {source['locator']}."
        )
    lines.extend(["", "## Related", "", "- [[Index]]", "- [[Source Manifest Guide]]", ""])
    return "\n".join(lines)


def claude_source_id(source: dict) -> str:
    content_hash = source["payload_sha256"] or ""
    digest = hashlib.sha256(f"url\0{source['url']}\0{content_hash}".encode("utf-8")).hexdigest()
    return f"src-{digest[:20]}"


def claude_claim_id(claim: dict) -> str:
    digest = hashlib.sha256(claim["id"].encode("utf-8")).hexdigest()
    return f"clm-{digest[:20]}"


def claude_source_projection(source_data: dict, as_of: date) -> dict:
    page = "wiki/sources/research-pack-2026-local-seo.md"
    records = {}
    for source in source_data["sources"]:
        records[claude_source_id(source)] = {
            "origin": {"kind": "url", "locator": source["url"]},
            "content_kind": "webpage",
            "authority": source["authority"],
            "review_status": source["review_state"],
            "title": source["title"],
            "content_sha256": source["payload_sha256"],
            "ingested_at": None,
            "retrieved_at": source["retrieved_at"],
            "refresh_due": source["refresh_due"],
            "pages": [page],
            "independence_key": source["independence_key"],
            "supersedes": None,
            "canonical_id": source["id"],
            "canonical_locator": source["locator"],
        }
    return {
        "schema": "claude-obsidian.source-ledger.v1",
        "generated_at": f"{as_of.isoformat()}T00:00:00Z",
        "sources": records,
    }


def claude_claim_projection(claim_data: dict, source_data: dict, as_of: date) -> dict:
    sources = {source["id"]: source for source in source_data["sources"]}
    records = {}
    for claim in claim_data["claims"]:
        evidence = []
        for source_id in claim["source_ids"]:
            source = sources[source_id]
            evidence.append({
                "source_id": claude_source_id(source),
                "relation": "supports",
                "locator": source["locator"],
            })
        for source_id in claim["contradicting_source_ids"]:
            source = sources[source_id]
            evidence.append({
                "source_id": claude_source_id(source),
                "relation": "contradicts",
                "locator": source["locator"],
            })
        confidence = {
            "EVIDENCE-BASED": "high",
            "PRACTITIONER": "medium",
            "CONTESTED": "low",
            "FOLKLORE": "low",
        }[claim["confidence"]]
        # The canonical contract permits a controlling official source for a
        # high-risk policy claim. Claude Obsidian's binary `high` risk carries
        # a stricter two-independent-source meaning, so the adapter reserves
        # it for high-risk non-policy claims and records canonical risk below.
        adapter_risk = "high" if claim["risk"] == "high" and claim.get("claim_type", "empirical") != "policy" else "normal"
        note_parts = [
            f"Canonical ID: {claim['id']}.",
            f"Canonical risk: {claim['risk']}.",
            f"Scope: {claim['scope']}.",
        ]
        if claim["notes"]:
            note_parts.append(str(claim["notes"]))
        records[claude_claim_id(claim)] = {
            "text": claim["statement"],
            "risk": adapter_risk,
            "assessment": claim["assessment"],
            "confidence": confidence,
            "location": {
                "path": "wiki/meta/Claim Ledger.md",
                "anchor": claim["id"],
            },
            "reviewed_at": claim["verified_at"],
            "notes": " ".join(note_parts),
            "supersedes": None,
            "evidence": evidence,
            "canonical_id": claim["id"],
        }
    return {
        "schema": "claude-obsidian.claim-ledger.v1",
        "generated_at": f"{as_of.isoformat()}T00:00:00Z",
        "claims": records,
    }


def vault_claim_markdown(claims: list[dict], as_of: date) -> str:
    lines = [
        "---",
        'type: "ledger"',
        'title: "Claim Ledger"',
        f'created: "{as_of.isoformat()}"',
        f'updated: "{as_of.isoformat()}"',
        'status: "active"',
        'tags: ["type/ledger", "domain/local-seo", "provenance/claims"]',
        "---",
        "",
        "# Claim Ledger",
        "",
        "Deterministic Obsidian projection of the canonical repository claim ledger.",
        "",
    ]
    for claim in sorted(claims, key=lambda item: item["id"]):
        lines.extend([
            f"## {claim['id']}",
            "",
            claim["statement"],
            "",
            f"- Assessment: {claim['assessment']}",
            f"- Confidence: {claim['confidence']}",
            f"- Risk: {claim['risk']}",
            f"- Sources: {', '.join(claim['source_ids']) or 'none'}",
            f"- Contrary evidence: {', '.join(claim['contradicting_source_ids']) or 'none'}",
            f"- Scope: {claim['scope']}",
            f"- Refresh due: {claim['refresh_due']}",
            "",
        ])
    lines.extend(["## Related", "", "- [[Index]]", "- [[research-pack-2026-local-seo|Local SEO Evidence Research Pack]]", ""])
    return "\n".join(lines)


def expected_outputs(source_data: dict, claim_data: dict, vault: Path, as_of: date) -> dict[Path, str]:
    return {
        CLAIM_MARKDOWN: markdown_text(claim_data["claims"]),
        vault / "wiki" / "meta" / "ledgers" / "source-ledger.json": json_text(claude_source_projection(source_data, as_of)),
        vault / "wiki" / "meta" / "ledgers" / "claim-ledger.json": json_text(claude_claim_projection(claim_data, source_data, as_of)),
        vault / "wiki" / "meta" / "Claim Ledger.md": vault_claim_markdown(claim_data["claims"], as_of),
        vault / "wiki" / "sources" / "research-pack-2026-local-seo.md": research_pack_text(source_data["sources"], as_of),
    }


def validate_all(as_of: date, *, vault: Path | None = None) -> tuple[dict, dict, dict[str, dict], dict[str, dict]]:
    source_data = load_object(SOURCE_LEDGER)
    claim_data = load_object(CLAIM_LEDGER)
    sources, stale_sources = validate_source_ledger(source_data, as_of)
    claims, stale_claims = validate_claim_ledger(claim_data, sources, as_of, vault=vault)
    validate_overlays(load_object(ROOT / "data/knowledge-overlays.json"), claims, sources, expected_as_of=as_of.isoformat())
    for path in (ROOT / "references/canon").glob("[0-9]*.md"):
        text = path.read_text(encoding="utf-8")
        match = re.search(r"^source_ids: \[([^\]]+)\]$", text, re.M)
        if not match:
            raise ContractError(f"{path.name}: missing canon source IDs")
        ids = [v.strip() for v in match[1].split(",")]
        if any(sid not in sources for sid in ids):
            raise ContractError(f"{path.name}: unknown canon source ID")
        due = re.search(r"^refresh_due: (\S+)$", text, re.M)
        verified = re.search(r"^verified_at: (\S+)$", text, re.M)
        if not due or not verified or parse_iso(verified[1], path.name) > as_of or parse_iso(due[1], path.name) > min(parse_iso(sources[sid]["refresh_due"], sid) for sid in ids):
            raise ContractError(f"{path.name}: canon date exceeds controlling evidence")
    if stale_sources:
        raise ContractError(f"stale active sources: {', '.join(stale_sources)}")
    if stale_claims:
        raise ContractError(f"stale active claims: {', '.join(stale_claims)}")
    return source_data, claim_data, sources, claims


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("validate", "render", "check"):
        command = sub.add_parser(name)
        command.add_argument("--as-of", required=True, help="Pinned evidence date (YYYY-MM-DD)")
        if name in {"render", "check"}:
            command.add_argument("--vault", required=True)
    fresh = sub.add_parser("freshness")
    fresh.add_argument("--as-of", required=True)
    fresh.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()
    try:
        as_of = parse_iso(args.as_of, "--as-of")
        assert as_of is not None
        if args.command == "freshness":
            source_data, claim_data = load_object(SOURCE_LEDGER), load_object(CLAIM_LEDGER)
            snapshot = parse_iso(source_data["as_of"], "snapshot")
            sources, _ = validate_source_ledger(source_data, snapshot)
            claims, _ = validate_claim_ledger(claim_data, sources, snapshot)
            overlays = load_object(ROOT / "data/knowledge-overlays.json")
            validate_overlays(overlays, claims, sources, expected_as_of=source_data["as_of"])
            result = evaluate(source_data, claim_data, overlays, as_of)
            if args.format == "json":
                print(json.dumps(result, indent=2, sort_keys=True))
            else:
                print("# Evidence freshness\n\n" + "\n".join(f"- {r['kind']} {r['id']}: {r['state']} ({r['refresh_due']})" for r in result["actionable"]))
            return 0 if result["ok"] else 1
        source_data, claim_data, sources, claims = validate_all(as_of, vault=Path(args.vault).expanduser().resolve() if args.command in {"render", "check"} else None)
        if args.command == "validate":
            print(json.dumps({"sources": len(sources), "claims": len(claims), "as_of": args.as_of}, sort_keys=True))
            return 0
        vault = Path(args.vault).expanduser().resolve()
        if not (vault / "wiki").is_dir():
            raise ContractError(f"vault has no wiki directory: {vault}")
        outputs = expected_outputs(source_data, claim_data, vault, as_of)
        if args.command == "check":
            drift = []
            for path, expected in outputs.items():
                actual = path.read_text(encoding="utf-8") if path.exists() else None
                if actual != expected:
                    drift.append(path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) else str(path))
            if drift:
                print(json.dumps({"drift": drift}, indent=2), file=sys.stderr)
                return 1
            print(json.dumps({"drift": [], "outputs": len(outputs)}, sort_keys=True))
            return 0
        for path, expected in outputs.items():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(expected, encoding="utf-8")
        print(json.dumps({"rendered": len(outputs), "sources": len(sources), "claims": len(claims)}, sort_keys=True))
        return 0
    except (ContractError, ValueError, KeyError, TypeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Bulk-ingest the seed Local SEO Knowledge Base markdown into wiki notes.

Splits by H1, classifies into folders (glossary, concepts, frameworks, audits,
gbp, content, backlinks, llm-seo), extracts H2 "AI prompts" as standalone
notes in wiki/prompts/, strips inline base64 image refs, rewrites image links
to Obsidian wiki syntax, and writes proper frontmatter with source citation.

Idempotent: deletes prior seed notes before regenerating.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from runtime import touch_note_updated, parse_as_of, protect_repo_target, require_source, require_vault, sha256, yaml_list

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "assets" / "template-brain"
DEFAULT_SOURCE = TEMPLATE / ".raw" / "source-material" / "LOCAL-seo-Knowledge-Base.md"
DEFAULT_OVERLAY = ROOT / "data" / "knowledge-overlays.json"

# H1 chapter -> folder classification. Match against UPPERCASE-NORMALIZED key.
CHAPTER_MAP: dict[str, str] = {
    "GLOSSARY": "glossary",
    "WHAT IS LOCAL SEO": "concepts",
    "KEY GOOGLE RANK FACTORS": "concepts",
    "HOW SEO AUTHORITY IS PASSED": "concepts",
    "AI OVERVIEW IN SEARCH": "concepts",
    "WHAT IS E-E-A-T?": "concepts",
    "KEYWORD RESEARCH": "concepts",
    "WHICH AI TOOLS TO USE": "concepts",
    "CREATING AN AUDIENCE AVATAR": "concepts",
    "THE 3 PHASES OF LOCAL SEO": "frameworks",
    "LOCAL LINK OVERVIEW": "frameworks",
    "DUE DILIGENCE EXPLANATION": "frameworks",
    "SCHEMA EXPLANATION": "frameworks",
    "THE CORE 30 CONTENT STRATEGY": "frameworks",
    "PROPERTY AUDIT QUICK WINS": "audits",
    "PROPERTY AUDIT PART 1": "audits",
    "PROPERTY AUDIT PART 2": "audits",
    "CONTENT PLANNING: TOPICAL RELEVANCE PART 1": "audits",
    "CONTENT PLANNING: TOPICAL RELEVANCE PART 2": "audits",
    "CONTENT PLANNING: GEOGRAPHICAL RELEVANCE PART 1": "audits",
    "CONTENT PLANNING: GEOGRAPHICAL RELEVANCE PART 2": "audits",
    "CONTENT AUDIT : OVERVIEW": "audits",
    "CONTENT AUDIT: OVERVIEW": "audits",
    "CONTENT AUDIT: HOMEPAGE": "audits",
    "CONTENT AUDIT: SUPPORTING PAGES": "audits",
    'E-E-A-T WITH "ABOUT US" PAGE': "audits",
    "E-E-A-T WITH “ABOUT US” PAGE": "audits",
    "PROPERTY TECHNICAL AUDIT": "audits",
    "PROPERTY CTR AUDIT": "audits",
    "PROPERTY CONTENT WITH EXISTING AUTHORITY AUDIT": "audits",
    "GBP OVERVIEW": "gbp",
    "GBP VERIFICATION": "gbp",
    "GBP DESCRIPTION": "gbp",
    "GBP SERVICES": "gbp",
    "GBP CATEGORIES": "gbp",
    "GBP CATEGORIES EDGE CASES (RE-THEMING)": "gbp",
    "WARNING FOR GBP CHANGES": "gbp",
    "GBP HOLIDAY HOURS MAINTENANCE + AUTOMATED CALLS": "gbp",
    "GBP HOLIDAY HOURS MAINTENANCE \\+ AUTOMATED CALLS": "gbp",
    "GBP OPTIMIZATION": "gbp",
    "GBP + WEBSITE IMAGE GEOTAGGING": "gbp",
    "GBP \\+ WEBSITE IMAGE GEOTAGGING": "gbp",
    "GBP POSTS": "gbp",
    "CONTENT : BLOG POST OUTLINE": "content",
    "CONTENT: BLOG POST OUTLINE": "content",
    "CONTENT: BLOG POST WRITING": "content",
    "CONTENT: HOMEPAGE": "content",
    "CONTENT: SERVICE PAGES": "content",
    "CONTENT: SUPPORTING PAGES": "content",
    "CONTENT: HIDDEN CONTENT": "content",
    "CONTENT: INTERNAL ANCHOR TEXT GUIDELINES": "content",
    "CONTENT: OUTBOUND AUTHORITY LINKS": "content",
    "METADATA: SEO TITLES AND DESCRIPTIONS": "content",
    "CONTENT REVIEW: COMPETITIVE COMPARISON": "content",
    "BACKLINKING OVERVIEW": "backlinks",
    "BACKLINKING: NO FOLLOW LINKS": "backlinks",
    "BACKLINKING ANCHORS": "backlinks",
    "BACKLINKING: LOCAL CITATIONS": "backlinks",
    "BACKLINKING : COMPETITIVE RESEARCH TO FIND OPPORTUNITIES": "backlinks",
    "BACKLINKING: COMPETITIVE RESEARCH TO FIND OPPORTUNITIES": "backlinks",
    "SOCIAL SIGNALS": "backlinks",
    "LLM SEO": "llm-seo",
    "LLM RANKING FACTORS": "llm-seo",
    "LLM SCHEMA": "llm-seo",
    "LLM REDDIT IMPORTANCE": "llm-seo",
}

NEW_FOLDERS = ["glossary", "frameworks", "audits", "gbp", "content", "backlinks", "llm-seo", "prompts"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Source markdown; defaults to <vault>/.raw/source-material")
    parser.add_argument("--vault", required=True, help="Path to template vault (or client vault)")
    parser.add_argument("--overlay", default=str(DEFAULT_OVERLAY), help="Canonical evidence overlay JSON")
    parser.add_argument("--as-of", required=True, help="Pinned evidence/build date (YYYY-MM-DD)")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs and report the plan without writing")
    parser.add_argument("--allow-repo-target", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    today = parse_as_of(args.as_of)
    vault = require_vault(args.vault)
    protect_repo_target(vault, allow_repo_target=args.allow_repo_target)
    source_value = args.source or str(vault / ".raw" / "source-material" / DEFAULT_SOURCE.name)
    if not Path(source_value).expanduser().is_file():
        raise SystemExit(
            "ERROR: historical seed not found: "
            f"{source_value}\nThe historical course bundle is operator-supplied and is not shipped "
            "with the repository. Place it under <vault>/.raw/source-material/ or pass --source. "
            "The committed template vault already contains the generated notes."
        )
    source = require_source(source_value, suffixes={".md"})
    overlay = load_overlay(Path(args.overlay).expanduser().resolve(), today)

    raw = source.read_text(encoding="utf-8")
    digest = sha256(source)

    # 1. Strip base64 image reference definitions
    cleaned = strip_base64_refs(raw)

    # 2. Rewrite image refs from `![image.png][imageN]` to `![[images/imageN.png]]`
    cleaned = rewrite_image_refs(cleaned)

    # Parse and validate the entire plan before any target mutation. `--dry-run`
    # must remain byte-for-byte read-only even when seeded notes already exist.
    chapters = split_by_h1(cleaned)
    if args.dry_run:
        print(
            f"DRY-RUN: would regenerate {len(chapters)} source chapters in {vault} "
            f"with {len(overlay['notes'])} evidence overlays as of {today}"
        )
        return 0

    # 3. Ensure target folders exist
    for folder in NEW_FOLDERS:
        (vault / "wiki" / folder).mkdir(parents=True, exist_ok=True)

    # 4. Clean any prior seed notes (idempotent re-run)
    for folder in NEW_FOLDERS + ["concepts"]:
        target = vault / "wiki" / folder
        if not target.is_dir():
            continue
        for path in target.glob("*.md"):
            if path.name == "_index.md":
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if "seed_source:" in text:
                path.unlink()

    # 5. Split by H1
    source_rel = source.relative_to(vault).as_posix() if source.is_relative_to(vault) else str(source)

    written: dict[str, list[str]] = {folder: [] for folder in NEW_FOLDERS + ["concepts"]}
    prompts_written: list[tuple[str, str, str]] = []  # (title, slug, parent_slug)
    unclassified: list[str] = []
    chapter_titles = {title_to_slug(clean_chapter_title(t)): clean_chapter_title(t) for t, _ in chapters if clean_chapter_title(t)}
    moved_links: dict[str, list[str]] = {}
    for rel, entry in overlay["notes"].items():
        if entry.get("task_parent"):
            parent = Path(entry["task_parent"]).stem
            moved_links.setdefault(parent, []).append(f"- [[{Path(rel).stem}|{entry['title']}]]")

    for title, body in chapters:
        clean_title = clean_chapter_title(title)
        if not clean_title:
            continue
        key = normalize_key(clean_title)
        folder = classify(key)
        if not folder:
            unclassified.append(clean_title)
            continue

        # Extract H2 AI prompts as separate notes
        body_no_prompts, prompts = extract_prompts(body)
        slug = title_to_slug(clean_title)
        note_path = vault / "wiki" / folder / f"{slug}.md"
        prompt_links: list[str] = list(moved_links.get(slug, []))
        for prompt_title, prompt_body in prompts:
            p_slug = title_to_slug(prompt_title)
            prompt_path = vault / "wiki" / "prompts" / f"{p_slug}.md"
            entry = overlay_for(overlay, vault, prompt_path)
            task_parent = Path(entry.get("task_parent", f"wiki/{folder}/{slug}.md"))
            task_slug, task_folder = task_parent.stem, task_parent.parent.name
            write_prompt_note(
                prompt_path,
                prompt_title,
                prompt_body,
                parent_title=chapter_titles[task_slug],
                parent_slug=task_slug,
                parent_folder=task_folder,
                today=today,
                source_rel=source_rel,
                digest=digest,
                overlay=entry,
            )
            prompts_written.append((entry.get("title", prompt_title), p_slug, task_slug))
            if task_slug == slug:
                prompt_links.append(f"- [[{p_slug}|{entry.get('title', prompt_title)}]]")

        write_chapter_note(
            note_path,
            clean_title,
            body_no_prompts,
            folder=folder,
            today=today,
            source_rel=source_rel,
            digest=digest,
            prompt_links=prompt_links,
            overlay=overlay_for(overlay, vault, note_path),
        )
        written[folder].append(slug)

    # 6. Write hub _index.md files
    for folder in NEW_FOLDERS:
        if folder == "prompts":
            write_prompts_hub(vault, prompts_written, today)
        else:
            write_folder_hub(vault, folder, written.get(folder, []), today)

    # Also update concepts hub if we wrote anything there
    if written.get("concepts"):
        write_folder_hub(vault, "concepts", written["concepts"], today)

    # 7. Normalize all generated and operator-template frontmatter. This is a
    # deterministic build step, not a one-off vault patch.
    normalize_frontmatter(vault, today, overlay.get("defaults", {}))

    # 8. Append to log
    log = vault / "wiki" / "log.md"
    if log.exists():
        log_text = log.read_text(encoding="utf-8")
        line = f"\n- {today} - Seed knowledge base ingested. Chapters: {sum(len(v) for v in written.values())}. Prompts: {len(prompts_written)}."
        if line not in log_text:
            log.write_text(log_text.rstrip() + line + "\n", encoding="utf-8")
            touch_note_updated(log, today)

    # 9. Report
    total_chapters = sum(len(v) for v in written.values())
    print(f"OK: Wrote {total_chapters} chapter notes and {len(prompts_written)} prompt notes")
    for folder, notes in written.items():
        if notes:
            print(f"  wiki/{folder}/: {len(notes)} notes")
    if unclassified:
        print(f"WARN: {len(unclassified)} unclassified chapters: {unclassified[:5]}...")
    return 0


def strip_base64_refs(text: str) -> str:
    """Remove inline base64 image reference definitions at the bottom of the file."""
    pattern = re.compile(r"^\[image\d+\]:\s*<data:image/[^>]+>\s*$", re.MULTILINE)
    return pattern.sub("", text)


def load_overlay(path: Path, as_of: str) -> dict:
    if not path.is_file():
        raise SystemExit(f"ERROR: overlay not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"ERROR: invalid overlay JSON at line {exc.lineno}: {exc.msg}") from exc
    if not isinstance(data, dict) or data.get("schema") != "local-seo-brain.knowledge-overlays.v1":
        raise SystemExit("ERROR: unsupported knowledge overlay schema")
    if data.get("as_of") != as_of:
        raise SystemExit("ERROR: overlay as_of must match --as-of")
    notes = data.get("notes")
    if not isinstance(notes, dict):
        raise SystemExit("ERROR: overlay notes must be an object")
    for rel, entry in notes.items():
        if not isinstance(rel, str) or not rel.startswith("wiki/") or ".." in Path(rel).parts:
            raise SystemExit(f"ERROR: unsafe overlay path: {rel!r}")
        if not isinstance(entry, dict):
            raise SystemExit(f"ERROR: overlay entry must be an object: {rel}")
        required = {"claim_ids", "assessment", "confidence", "verified_at", "refresh_due"}
        missing = sorted(required - set(entry))
        if missing:
            raise SystemExit(f"ERROR: overlay {rel} missing: {', '.join(missing)}")
        if entry.get("mode", "annotate") == "replace" and not str(entry.get("replacement_body", "")).strip():
            raise SystemExit(f"ERROR: replacement overlay has no body: {rel}")
    from freshness import validate_overlays
    root = Path(__file__).resolve().parent.parent
    claims = json.loads((root / "references/claim-ledger.json").read_text())["claims"]
    sources = json.loads((root / "references/source-ledger.json").read_text())["sources"]
    try:
        validate_overlays(data, {c["id"]: c for c in claims}, {s["id"]: s for s in sources}, expected_as_of=as_of)
    except (ValueError, KeyError) as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    return data


def overlay_for(data: dict, vault: Path, path: Path) -> dict:
    rel = path.relative_to(vault).as_posix()
    entry = data["notes"].get(rel)
    if entry is None:
        raise SystemExit(f"ERROR: canonical overlay has no entry for generated note: {rel}")
    return entry


def evidence_block(entry: dict) -> str:
    blocks = [
        "## Evidence status",
        "",
        f"- Assessment: **{entry['assessment']}**",
        f"- Confidence: **{entry['confidence']}**",
        f"- Verified: **{entry['verified_at']}**",
        f"- Refresh due: **{entry['refresh_due']}**",
        f"- Claim IDs: {', '.join(entry['claim_ids']) or 'none'}",
        "",
    ]
    for callout in entry.get("callouts", []):
        metadata = (
            f"Claims: {', '.join(callout['claim_ids']) or 'none'}. "
            f"Sources: {', '.join(callout['source_ids']) or 'none'}."
        )
        body_lines = str(callout["body"]).strip().splitlines()
        blocks.append(f"> [!{callout['kind']}] {callout['title']}")
        blocks.extend(f"> {line}" if line else ">" for line in body_lines)
        blocks.append(f"> {metadata}")
        blocks.append("> See [[research-pack-2026-local-seo|Local SEO Evidence Research Pack]].")
        blocks.append("")
    return "\n".join(blocks).rstrip()


def historical_body(body: str, entry: dict) -> str:
    if entry.get("mode", "annotate") == "replace":
        return str(entry["replacement_body"]).strip()
    return (
        "## Historical seed material\n\n"
        "> [!warning] Retained for provenance; not current operating guidance\n"
        "> The source material below is preserved from the operator-supplied historical seed. "
        "Any number, ranking mechanism, or prescription that is not restated above with a "
        "claim ID and active source is unsupported and must not drive client work.\n\n"
        + body.strip()
    )


def rewrite_image_refs(text: str) -> str:
    """Convert `![image.png][imageN]` (or `![anything][imageN]`) to `![[images/imageN.png]]`."""
    pattern = re.compile(r"!\[[^\]]*\]\[image(\d+)\]")
    return pattern.sub(lambda m: f"![[images/image{m.group(1)}.png]]", text)


def split_by_h1(text: str) -> list[tuple[str, str]]:
    """Return list of (h1_title, body) pairs."""
    lines = text.split("\n")
    out: list[tuple[str, str]] = []
    current_title: str | None = None
    current_body: list[str] = []
    for line in lines:
        if line.startswith("# ") and not line.startswith("# # "):
            if current_title is not None:
                out.append((current_title, "\n".join(current_body).strip()))
            current_title = line[2:].strip()
            current_body = []
        else:
            if current_title is not None:
                current_body.append(line)
    if current_title is not None:
        out.append((current_title, "\n".join(current_body).strip()))
    return out


def extract_prompts(body: str) -> tuple[str, list[tuple[str, str]]]:
    """Split body into (body_without_prompts, [(prompt_title, prompt_body), ...]).
    A prompt is an H2 section whose title contains the robot emoji."""
    lines = body.split("\n")
    body_lines: list[str] = []
    prompts: list[tuple[str, str]] = []
    in_prompt = False
    cur_title = ""
    cur_body: list[str] = []
    for line in lines:
        m = re.match(r"^##\s+(.*?)\s*(?:\{#.*\})?\s*$", line)
        if m and ("🤖" in m.group(1) or "PROMPT" in m.group(1).upper()):
            if in_prompt:
                prompts.append((cur_title, "\n".join(cur_body).strip()))
            in_prompt = True
            cur_title = clean_prompt_title(m.group(1))
            cur_body = []
            continue
        if in_prompt and (line.startswith("# ") or (line.startswith("## ") and "🤖" not in line)):
            prompts.append((cur_title, "\n".join(cur_body).strip()))
            in_prompt = False
            body_lines.append(line)
            continue
        if in_prompt:
            cur_body.append(line)
        else:
            body_lines.append(line)
    if in_prompt:
        prompts.append((cur_title, "\n".join(cur_body).strip()))
    return "\n".join(body_lines).strip(), prompts


ACRONYMS = {
    "SEO", "GBP", "GMB", "AI", "CTR", "LLM", "E-E-A-T", "EEAT", "NAP", "SAB", "URL",
    "YMYL", "PAA", "GSC", "GA4", "CRO", "B2B", "B2C", "HVAC", "DIY", "FAQ",
    "PDF", "HTML", "CSS", "JS", "API", "JSON", "CSV", "ID", "IDs", "USA", "UK",
    "Q&A", "PT", "PT.", "WI", "AZ", "TX", "FL",
}
SMALL_WORDS = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "of", "on", "or", "the", "to", "vs", "with"}


def smart_title_case(title: str) -> str:
    """Title-case while preserving acronyms and small connective words."""
    title = re.sub(r"\s*\{#[^}]+\}\s*$", "", title).strip()
    title = re.sub(r"\\\+", "+", title)  # un-escape +
    title = re.sub(r"\\\-", "-", title)  # un-escape -

    def cap_token(token: str, is_first: bool) -> str:
        if not token:
            return token
        upper = token.upper().strip(":,.;")
        # Preserve acronyms whole
        if upper in ACRONYMS:
            # Keep the original punctuation around it
            return re.sub(r"[A-Za-z][A-Za-z0-9-]*", upper, token, count=1)
        lower = token.lower()
        if not is_first and lower.strip(":,.;") in SMALL_WORDS:
            return lower
        # Otherwise: capitalize first letter, lowercase rest
        return token[0].upper() + token[1:].lower() if len(token) > 1 else token.upper()

    parts = title.split(" ")
    out = []
    for i, p in enumerate(parts):
        # Handle hyphenated/slash sub-tokens
        subs = re.split(r"([-/:])", p)
        new_subs = []
        for j, s in enumerate(subs):
            if s in {"-", "/", ":"}:
                new_subs.append(s)
            else:
                new_subs.append(cap_token(s, is_first=(i == 0 and j == 0)))
        out.append("".join(new_subs))
    return " ".join(out)


def clean_chapter_title(title: str) -> str:
    return smart_title_case(title)


def clean_prompt_title(title: str) -> str:
    title = re.sub(r"🤖", "", title).strip()
    title = re.sub(r"\s+", " ", title)
    title = title.strip(" :;,.-")
    return title


def normalize_key(title: str) -> str:
    norm = title.upper().strip()
    norm = re.sub(r"\\\+", "+", norm)
    return norm


def classify(key: str) -> str | None:
    if key in CHAPTER_MAP:
        return CHAPTER_MAP[key]
    # Try permissive matches
    for k, folder in CHAPTER_MAP.items():
        if k in key or key in k:
            return folder
    return None


def title_to_slug(title: str) -> str:
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")
    return slug[:80] or "untitled"


def write_chapter_note(
    path: Path,
    title: str,
    body: str,
    *,
    folder: str,
    today: str,
    source_rel: str,
    digest: str,
    prompt_links: list[str],
    overlay: dict,
) -> None:
    related = f"- [[wiki/{folder}/_index|{hub_name(folder)} Hub]]\n- [[Claim Verification Flow]]"
    prompts_block = ""
    if prompt_links:
        prompts_block = "\n\n## AI Prompts\n\n" + "\n".join(prompt_links) + "\n"

    evidence_tag = "evidence/" + overlay["assessment"]
    fm = (
        "---\n"
        f'type: "knowledge"\n'
        f'title: "{escape_yaml(title)}"\n'
        f'folder: "{folder}"\n'
        f'created: "{today}"\n'
        f'updated: "{today}"\n'
        f'status: "active"\n'
        f'tags: {yaml_list(["type/knowledge", f"domain/{folder}", evidence_tag])}\n'
        f'claim_ids: {yaml_list(overlay["claim_ids"])}\n'
        f'assessment: "{overlay["assessment"]}"\n'
        f'confidence: "{overlay["confidence"]}"\n'
        f'verified_at: "{overlay["verified_at"]}"\n'
        f'refresh_due: "{overlay["refresh_due"]}"\n'
        f'seed_source: "{source_rel}"\n'
        f'seed_hash: "sha256:{digest}"\n'
        "---\n"
    )
    rendered_body = historical_body(body, overlay)
    md = f"{fm}\n# {title}\n\n{evidence_block(overlay)}\n\n{rendered_body}{prompts_block}\n\n## Related\n\n{related}\n"
    path.write_text(md, encoding="utf-8")


def write_prompt_note(
    path: Path,
    title: str,
    body: str,
    *,
    parent_title: str,
    parent_slug: str,
    parent_folder: str,
    today: str,
    source_rel: str,
    digest: str,
    overlay: dict,
) -> None:
    title = overlay.get("title", title)
    evidence_tag = "evidence/" + overlay["assessment"]
    fm = (
        "---\n"
        f'type: "prompt"\n'
        f'title: "{escape_yaml(title)}"\n'
        f'parent: "{escape_yaml(parent_title)}"\n'
        f'parent_folder: "{parent_folder}"\n'
        f'created: "{today}"\n'
        f'updated: "{today}"\n'
        f'status: "active"\n'
        f'tags: {yaml_list(["type/prompt", "domain/local-seo", evidence_tag])}\n'
        f'claim_ids: {yaml_list(overlay["claim_ids"])}\n'
        f'assessment: "{overlay["assessment"]}"\n'
        f'confidence: "{overlay["confidence"]}"\n'
        f'verified_at: "{overlay["verified_at"]}"\n'
        f'refresh_due: "{overlay["refresh_due"]}"\n'
        f'seed_source: "{source_rel}"\n'
        f'seed_hash: "sha256:{digest}"\n'
        "---\n"
    )
    prompt_body = historical_body("## Prompt\n\n" + body.strip(), overlay)
    md = (
        f"{fm}\n# {title}\n\n"
        f"> Draft prompt for [[{parent_slug}|{parent_title}]]. "
        f"Use only authorized evidence and review the result before external use.\n\n"
        f"{evidence_block(overlay)}\n\n"
        f"{prompt_body}\n\n"
        "## Related\n\n"
        f"- [[wiki/prompts/_index|Prompts Hub]]\n"
        f"- [[Index]]\n"
    )
    path.write_text(md, encoding="utf-8")


def chapter_related_links(folder: str) -> str:
    base = [
        "- [[Index]]",
        "- [[Hot]]",
        f"- [[wiki/{folder}/_index|{folder.title()} Hub]]",
    ]
    if folder == "glossary":
        base.append("- [[wiki/concepts/_index|Concepts Hub]]")
    if folder == "concepts":
        base.append("- [[wiki/frameworks/_index|Frameworks Hub]]")
    if folder == "frameworks":
        base.append("- [[wiki/audits/_index|Audits Hub]]")
    if folder == "audits":
        base.append("- [[wiki/content/_index|Content Hub]]")
        base.append("- [[wiki/gbp/_index|GBP Hub]]")
    if folder == "gbp":
        base.append("- [[Property Audit Workflow]]")
    if folder == "content":
        base.append("- [[wiki/backlinks/_index|Backlinks Hub]]")
    if folder == "backlinks":
        base.append("- [[wiki/llm-seo/_index|LLM SEO Hub]]")
    if folder == "llm-seo":
        base.append("- [[wiki/concepts/_index|Concepts Hub]]")
    return "\n".join(base)


def write_folder_hub(vault: Path, folder: str, slugs: list[str], today: str) -> None:
    pretty = hub_name(folder)
    note_lines = "\n".join(f"- [[{slug}]] - " + re.search(r'^assessment: "(.+)"', (vault / "wiki" / folder / f"{slug}.md").read_text(), re.M).group(1) for slug in sorted(slugs)) or "- None yet"
    text = (
        "---\n"
        f'type: "index"\n'
        f'title: "{pretty} Hub"\n'
        f'created: "{today}"\n'
        f'updated: "{today}"\n'
        f'status: "active"\n'
        f'tags: {yaml_list(["type/index", f"domain/{folder}"])}\n'
        "---\n\n"
        f"# {pretty} Hub\n\n"
        "## Connects To\n\n"
        "- [[Index]]\n"
        "- [[Dashboard]]\n"
        "- [[Hot]]\n\n"
        "## Notes\n\n"
        "Labels describe the reviewed claim or legacy proposition, not the usefulness of the whole current note. Read each note's Evidence status for scope; unsupported legacy formulas can coexist with usable review guidance.\n\n"
        f"{note_lines}\n\n"
        "## Maintenance\n\n"
        f"Keep this hub linked to every note in `wiki/{folder}/`.\n"
    )
    (vault / "wiki" / folder / "_index.md").write_text(text, encoding="utf-8")


def hub_name(folder: str) -> str:
    return {"gbp": "GBP", "llm-seo": "LLM SEO"}.get(folder, folder.replace("-", " ").title())


def write_prompts_hub(vault: Path, prompts: list[tuple[str, str, str]], today: str) -> None:
    # Group prompts by parent_slug
    by_parent: dict[str, list[tuple[str, str]]] = {}
    for title, slug, parent in prompts:
        by_parent.setdefault(parent, []).append((title, slug))

    groups = []
    for parent in sorted(by_parent.keys()):
        groups.append(f"### From [[{parent}]]\n")
        for title, slug in sorted(by_parent[parent]):
            groups.append(f"- [[{slug}|{title}]]")
        groups.append("")

    body = "\n".join(groups) or "- None yet"
    text = (
        "---\n"
        f'type: "index"\n'
        f'title: "Prompts Hub"\n'
        f'created: "{today}"\n'
        f'updated: "{today}"\n'
        f'status: "active"\n'
        f'tags: {yaml_list(["type/index", "domain/prompts"])}\n'
        "---\n\n"
        "# Prompts Hub\n\n"
        "Reviewed task prompts requiring authorized evidence and human approval. Each prompt links back "
        "to its parent chapter for context.\n\n"
        "## Connects To\n\n"
        "- [[Index]]\n"
        "- [[Dashboard]]\n"
        "- [[Hot]]\n\n"
        f"## Prompts ({len(prompts)} total)\n\n"
        f"{body}\n\n"
        "## Maintenance\n\n"
        "When you add a new prompt, link it from its parent chapter and add a row here.\n"
    )
    (vault / "wiki" / "prompts" / "_index.md").write_text(text, encoding="utf-8")


def escape_yaml(value: str) -> str:
    return value.replace('"', "\\\"")


def normalize_frontmatter(vault: Path, as_of: str, defaults: dict) -> None:
    default_status = str(defaults.get("status", "active"))
    default_tags = defaults.get("tags", ["domain/local-seo"])
    if not isinstance(default_tags, list) or not all(isinstance(tag, str) for tag in default_tags):
        raise SystemExit("ERROR: overlay defaults.tags must be a string array")
    for path in sorted((vault / "wiki").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        text = text.replace("{{date}}", as_of)
        if not text.startswith("---\n"):
            raise SystemExit(f"ERROR: note missing frontmatter: {path.relative_to(vault)}")
        end = text.find("\n---\n", 4)
        if end < 0:
            raise SystemExit(f"ERROR: unterminated frontmatter: {path.relative_to(vault)}")
        frontmatter = text[4:end]
        body = text[end + 5:]
        rel = path.relative_to(vault).as_posix()
        folder = path.parent.name.lower().replace(" ", "-")
        type_match = re.search(r'^type:\s*["\']?([^"\'\n]+)', frontmatter, re.MULTILINE)
        note_type = type_match.group(1).strip() if type_match else "note"
        additions = []
        if not re.search(r"^status:\s*", frontmatter, re.MULTILINE):
            additions.append(f'status: "{default_status}"')
        if not re.search(r"^tags:\s*", frontmatter, re.MULTILINE):
            additions.append(f"tags: {yaml_list([*default_tags, f'type/{note_type}', f'domain/{folder}'])}")
        if additions:
            frontmatter = frontmatter.rstrip() + "\n" + "\n".join(additions)
        normalized = f"---\n{frontmatter}\n---\n{body}"
        path.write_text(normalized, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())

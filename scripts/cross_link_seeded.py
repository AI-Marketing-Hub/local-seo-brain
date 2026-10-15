#!/usr/bin/env python3
"""
Inject curated 'Related Chapters' cross-links into seeded notes.

Idempotent: replaces an existing block if present, otherwise injects before
the final ## Related section.
"""
from __future__ import annotations

import re
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WIKI = ROOT / "assets" / "template-brain" / "wiki"

# Map of slug -> [(slug, display)] for curated, topically-adjacent links.
LINKS: dict[str, list[tuple[str, str]]] = {
    # === Concepts foundation ===
    "what-is-local-seo": [
        ("key-google-rank-factors", "Key Google Rank Factors"),
        ("the-3-phases-of-local-seo", "The 3 Phases of Local SEO"),
        ("ai-overview-in-search", "AI Overview in Search"),
        ("glossary", "Glossary"),
    ],
    "key-google-rank-factors": [
        ("what-is-local-seo", "What is Local SEO"),
        ("how-seo-authority-is-passed", "How SEO Authority is Passed"),
        ("what-is-e-e-a-t", "What is E-E-A-T?"),
        ("the-3-phases-of-local-seo", "The 3 Phases of Local SEO"),
    ],
    "how-seo-authority-is-passed": [
        ("key-google-rank-factors", "Key Google Rank Factors"),
        ("backlinking-overview", "Backlinking Overview"),
        ("content-internal-anchor-text-guidelines", "Internal Anchor Text Guidelines"),
        ("local-link-overview", "Local Link Overview"),
    ],
    "ai-overview-in-search": [
        ("llm-seo", "LLM SEO"),
        ("llm-ranking-factors", "LLM Ranking Factors"),
        ("what-is-e-e-a-t", "What is E-E-A-T?"),
        ("schema-explanation", "Schema Explanation"),
    ],
    "what-is-e-e-a-t": [
        ("e-e-a-t-with-about-us-page", "E-E-A-T with About Us Page"),
        ("key-google-rank-factors", "Key Google Rank Factors"),
        ("content-audit-overview", "Content Audit: Overview"),
        ("property-content-with-existing-authority-audit", "Property Content with Existing Authority Audit"),
    ],
    "keyword-research": [
        ("creating-an-audience-avatar", "Creating an Audience Avatar"),
        ("content-planning-topical-relevance-part-1", "Content Planning: Topical Relevance Part 1"),
        ("content-planning-geographical-relevance-part-1", "Content Planning: Geographical Relevance Part 1"),
        ("which-ai-tools-to-use", "Which AI Tools to Use"),
    ],
    "which-ai-tools-to-use": [
        ("creating-an-audience-avatar", "Creating an Audience Avatar"),
        ("keyword-research", "Keyword Research"),
        ("llm-seo", "LLM SEO"),
    ],
    "creating-an-audience-avatar": [
        ("which-ai-tools-to-use", "Which AI Tools to Use"),
        ("keyword-research", "Keyword Research"),
        ("content-planning-topical-relevance-part-1", "Content Planning: Topical Relevance Part 1"),
    ],

    # === Frameworks ===
    "the-3-phases-of-local-seo": [
        ("property-audit-quick-wins", "Phase 1 entry: Property Audit Quick Wins"),
        ("gbp-overview", "Phase 2 entry: GBP Overview"),
        ("backlinking-overview", "Phase 3 entry: Backlinking Overview"),
        ("the-core-30-content-strategy", "The Core 30 Content Strategy"),
    ],
    "the-core-30-content-strategy": [
        ("content-planning-topical-relevance-part-1", "Content Planning: Topical Relevance Part 1"),
        ("content-planning-geographical-relevance-part-1", "Content Planning: Geographical Relevance Part 1"),
        ("content-audit-overview", "Content Audit: Overview"),
        ("content-homepage", "Content: Homepage"),
        ("content-service-pages", "Content: Service Pages"),
    ],
    "local-link-overview": [
        ("backlinking-overview", "Backlinking Overview"),
        ("backlinking-local-citations", "Backlinking: Local Citations"),
        ("how-seo-authority-is-passed", "How SEO Authority is Passed"),
    ],
    "due-diligence-explanation": [
        ("backlinking-overview", "Backlinking Overview"),
        ("backlinking-local-citations", "Backlinking: Local Citations"),
        ("backlinking-competitive-research-to-find-opportunities", "Backlinking: Competitive Research"),
    ],
    "schema-explanation": [
        ("property-technical-audit", "Property Technical Audit"),
        ("llm-schema", "LLM Schema"),
        ("content-service-pages", "Content: Service Pages"),
    ],

    # === Audits ===
    "property-audit-quick-wins": [
        ("property-audit-part-1", "Property Audit Part 1"),
        ("property-audit-part-2", "Property Audit Part 2"),
        ("content-audit-overview", "Content Audit: Overview"),
        ("property-technical-audit", "Property Technical Audit"),
    ],
    "property-audit-part-1": [
        ("property-audit-quick-wins", "Property Audit Quick Wins"),
        ("property-audit-part-2", "Property Audit Part 2"),
        ("property-technical-audit", "Property Technical Audit"),
        ("content-audit-overview", "Content Audit: Overview"),
    ],
    "property-audit-part-2": [
        ("property-audit-part-1", "Property Audit Part 1"),
        ("property-ctr-audit", "Property CTR Audit"),
        ("property-content-with-existing-authority-audit", "Property Content with Existing Authority Audit"),
    ],
    "content-planning-topical-relevance-part-1": [
        ("content-planning-topical-relevance-part-2", "Content Planning: Topical Relevance Part 2"),
        ("the-core-30-content-strategy", "The Core 30 Content Strategy"),
        ("keyword-research", "Keyword Research"),
        ("content-planning-geographical-relevance-part-1", "Content Planning: Geographical Relevance Part 1"),
    ],
    "content-planning-topical-relevance-part-2": [
        ("content-planning-topical-relevance-part-1", "Content Planning: Topical Relevance Part 1"),
        ("content-planning-geographical-relevance-part-2", "Content Planning: Geographical Relevance Part 2"),
        ("the-core-30-content-strategy", "The Core 30 Content Strategy"),
    ],
    "content-planning-geographical-relevance-part-1": [
        ("content-planning-geographical-relevance-part-2", "Content Planning: Geographical Relevance Part 2"),
        ("content-planning-topical-relevance-part-1", "Content Planning: Topical Relevance Part 1"),
        ("keyword-research", "Keyword Research"),
    ],
    "content-planning-geographical-relevance-part-2": [
        ("content-planning-geographical-relevance-part-1", "Content Planning: Geographical Relevance Part 1"),
        ("content-planning-topical-relevance-part-2", "Content Planning: Topical Relevance Part 2"),
        ("the-core-30-content-strategy", "The Core 30 Content Strategy"),
    ],
    "content-audit-overview": [
        ("content-audit-homepage", "Content Audit: Homepage"),
        ("content-audit-supporting-pages", "Content Audit: Supporting Pages"),
        ("e-e-a-t-with-about-us-page", "E-E-A-T with About Us Page"),
    ],
    "content-audit-homepage": [
        ("content-audit-overview", "Content Audit: Overview"),
        ("content-audit-supporting-pages", "Content Audit: Supporting Pages"),
        ("content-homepage", "Content: Homepage (production)"),
    ],
    "content-audit-supporting-pages": [
        ("content-audit-overview", "Content Audit: Overview"),
        ("content-audit-homepage", "Content Audit: Homepage"),
        ("content-supporting-pages", "Content: Supporting Pages (production)"),
    ],
    "e-e-a-t-with-about-us-page": [
        ("what-is-e-e-a-t", "What is E-E-A-T?"),
        ("content-audit-overview", "Content Audit: Overview"),
        ("property-content-with-existing-authority-audit", "Property Content with Existing Authority Audit"),
    ],
    "property-technical-audit": [
        ("property-audit-quick-wins", "Property Audit Quick Wins"),
        ("schema-explanation", "Schema Explanation"),
        ("property-ctr-audit", "Property CTR Audit"),
    ],
    "property-ctr-audit": [
        ("property-technical-audit", "Property Technical Audit"),
        ("metadata-seo-titles-and-descriptions", "Metadata: SEO Titles and Descriptions"),
        ("property-audit-part-2", "Property Audit Part 2"),
    ],
    "property-content-with-existing-authority-audit": [
        ("e-e-a-t-with-about-us-page", "E-E-A-T with About Us Page"),
        ("content-audit-overview", "Content Audit: Overview"),
        ("what-is-e-e-a-t", "What is E-E-A-T?"),
    ],

    # === GBP cluster ===
    "gbp-overview": [
        ("gbp-verification", "GBP Verification"),
        ("gbp-description", "GBP Description"),
        ("gbp-categories", "GBP Categories"),
        ("gbp-services", "GBP Services"),
        ("gbp-optimization", "GBP Optimization"),
        ("the-3-phases-of-local-seo", "The 3 Phases of Local SEO"),
    ],
    "gbp-verification": [
        ("gbp-overview", "GBP Overview"),
        ("gbp-description", "GBP Description"),
        ("warning-for-gbp-changes", "Warning for GBP Changes"),
    ],
    "gbp-description": [
        ("gbp-overview", "GBP Overview"),
        ("gbp-services", "GBP Services"),
        ("gbp-categories", "GBP Categories"),
    ],
    "gbp-services": [
        ("gbp-categories", "GBP Categories"),
        ("gbp-description", "GBP Description"),
        ("content-service-pages", "Content: Service Pages"),
    ],
    "gbp-categories": [
        ("gbp-categories-edge-cases-re-theming", "GBP Categories Edge Cases (Re-Theming)"),
        ("gbp-services", "GBP Services"),
        ("gbp-overview", "GBP Overview"),
    ],
    "gbp-categories-edge-cases-re-theming": [
        ("gbp-categories", "GBP Categories"),
        ("warning-for-gbp-changes", "Warning for GBP Changes"),
    ],
    "warning-for-gbp-changes": [
        ("gbp-categories-edge-cases-re-theming", "GBP Categories Edge Cases (Re-Theming)"),
        ("gbp-verification", "GBP Verification"),
        ("gbp-overview", "GBP Overview"),
    ],
    "gbp-holiday-hours-maintenance-automated-calls": [
        ("gbp-overview", "GBP Overview"),
        ("gbp-optimization", "GBP Optimization"),
    ],
    "gbp-optimization": [
        ("gbp-overview", "GBP Overview"),
        ("gbp-posts", "GBP Posts"),
        ("gbp-website-image-geotagging", "GBP + Website Image Geotagging"),
        ("gbp-categories", "GBP Categories"),
    ],
    "gbp-website-image-geotagging": [
        ("gbp-optimization", "GBP Optimization"),
        ("gbp-posts", "GBP Posts"),
    ],
    "gbp-posts": [
        ("gbp-optimization", "GBP Optimization"),
        ("gbp-overview", "GBP Overview"),
        ("gbp-website-image-geotagging", "GBP + Website Image Geotagging"),
    ],

    # === Content cluster ===
    "content-blog-post-outline": [
        ("content-blog-post-writing", "Content: Blog Post Writing"),
        ("the-core-30-content-strategy", "The Core 30 Content Strategy"),
        ("metadata-seo-titles-and-descriptions", "Metadata: SEO Titles and Descriptions"),
    ],
    "content-blog-post-writing": [
        ("content-blog-post-outline", "Content: Blog Post Outline"),
        ("content-internal-anchor-text-guidelines", "Internal Anchor Text Guidelines"),
        ("content-outbound-authority-links", "Outbound Authority Links"),
        ("metadata-seo-titles-and-descriptions", "Metadata: SEO Titles and Descriptions"),
    ],
    "content-homepage": [
        ("content-service-pages", "Content: Service Pages"),
        ("content-audit-homepage", "Content Audit: Homepage"),
        ("e-e-a-t-with-about-us-page", "E-E-A-T with About Us Page"),
    ],
    "content-service-pages": [
        ("content-homepage", "Content: Homepage"),
        ("content-supporting-pages", "Content: Supporting Pages"),
        ("gbp-services", "GBP Services"),
        ("schema-explanation", "Schema Explanation"),
    ],
    "content-supporting-pages": [
        ("content-homepage", "Content: Homepage"),
        ("content-service-pages", "Content: Service Pages"),
        ("content-audit-supporting-pages", "Content Audit: Supporting Pages"),
    ],
    "content-hidden-content": [
        ("content-homepage", "Content: Homepage"),
        ("content-supporting-pages", "Content: Supporting Pages"),
    ],
    "content-internal-anchor-text-guidelines": [
        ("content-outbound-authority-links", "Outbound Authority Links"),
        ("how-seo-authority-is-passed", "How SEO Authority is Passed"),
        ("content-blog-post-writing", "Content: Blog Post Writing"),
    ],
    "content-outbound-authority-links": [
        ("content-internal-anchor-text-guidelines", "Internal Anchor Text Guidelines"),
        ("how-seo-authority-is-passed", "How SEO Authority is Passed"),
    ],
    "metadata-seo-titles-and-descriptions": [
        ("property-ctr-audit", "Property CTR Audit"),
        ("content-blog-post-writing", "Content: Blog Post Writing"),
        ("content-service-pages", "Content: Service Pages"),
    ],
    "content-review-competitive-comparison": [
        ("content-audit-overview", "Content Audit: Overview"),
        ("backlinking-competitive-research-to-find-opportunities", "Backlinking: Competitive Research"),
    ],

    # === Backlinks cluster ===
    "backlinking-overview": [
        ("backlinking-no-follow-links", "Backlinking: No Follow Links"),
        ("backlinking-anchors", "Backlinking Anchors"),
        ("backlinking-local-citations", "Backlinking: Local Citations"),
        ("backlinking-competitive-research-to-find-opportunities", "Backlinking: Competitive Research"),
        ("local-link-overview", "Local Link Overview"),
    ],
    "backlinking-no-follow-links": [
        ("backlinking-overview", "Backlinking Overview"),
        ("backlinking-anchors", "Backlinking Anchors"),
    ],
    "backlinking-anchors": [
        ("backlinking-overview", "Backlinking Overview"),
        ("backlinking-no-follow-links", "Backlinking: No Follow Links"),
        ("content-internal-anchor-text-guidelines", "Internal Anchor Text Guidelines"),
    ],
    "backlinking-local-citations": [
        ("backlinking-overview", "Backlinking Overview"),
        ("due-diligence-explanation", "Due Diligence Explanation"),
        ("local-link-overview", "Local Link Overview"),
    ],
    "backlinking-competitive-research-to-find-opportunities": [
        ("backlinking-overview", "Backlinking Overview"),
        ("backlinking-local-citations", "Backlinking: Local Citations"),
        ("content-review-competitive-comparison", "Content Review: Competitive Comparison"),
    ],
    "social-signals": [
        ("llm-reddit-importance", "LLM Reddit Importance"),
        ("backlinking-overview", "Backlinking Overview"),
    ],

    # === LLM cluster ===
    "llm-seo": [
        ("llm-ranking-factors", "LLM Ranking Factors"),
        ("llm-schema", "LLM Schema"),
        ("llm-reddit-importance", "LLM Reddit Importance"),
        ("ai-overview-in-search", "AI Overview in Search"),
    ],
    "llm-ranking-factors": [
        ("llm-seo", "LLM SEO"),
        ("llm-schema", "LLM Schema"),
        ("llm-reddit-importance", "LLM Reddit Importance"),
    ],
    "llm-schema": [
        ("schema-explanation", "Schema Explanation"),
        ("llm-seo", "LLM SEO"),
        ("llm-ranking-factors", "LLM Ranking Factors"),
    ],
    "llm-reddit-importance": [
        ("llm-seo", "LLM SEO"),
        ("social-signals", "Social Signals"),
        ("backlinking-overview", "Backlinking Overview"),
    ],
}

START = "<!-- cross-link:start -->"
END = "<!-- cross-link:end -->"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    wiki = Path(args.vault).expanduser().resolve() / "wiki"
    if not wiki.is_dir():
        raise SystemExit(f"ERROR: vault has no wiki/: {wiki.parent}")
    injected = 0
    skipped = 0
    for slug, links in LINKS.items():
        matches = list(wiki.rglob(f"{slug}.md"))
        if not matches:
            print(f"  MISS: {slug}")
            skipped += 1
            continue
        path = matches[0]
        text = path.read_text(encoding="utf-8")
        block_lines = ["", START, "## Related Chapters", ""]
        for link_slug, display in links:
            block_lines.append(f"- [[{link_slug}|{display}]]")
        block_lines.extend(["", END, ""])
        block = "\n".join(block_lines)

        if START in text:
            new = re.sub(
                rf"{re.escape(START)}.*?{re.escape(END)}",
                f"{START}\n## Related Chapters\n\n"
                + "\n".join(f"- [[{ls}|{disp}]]" for ls, disp in links)
                + f"\n\n{END}",
                text,
                flags=re.S,
            )
        else:
            # Insert before "## Related" (general hub section), else append
            if "\n## Related\n" in text:
                new = text.replace("\n## Related\n", block + "\n## Related\n", 1)
            else:
                new = text.rstrip() + "\n" + block

        if new != text:
            injected += 1
            if not args.dry_run:
                path.write_text(new, encoding="utf-8")

    print(f"Cross-linked: {injected} chapters")
    print(f"Skipped: {skipped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

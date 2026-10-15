#!/usr/bin/env python3
"""Generate the Local SEO Brain SVG visual layer for a client vault."""
from __future__ import annotations

import argparse
from pathlib import Path


RELATIONSHIP_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 580" role="img" aria-labelledby="title desc">
<title id="title">Local SEO Brain relationship map</title>
<desc id="desc">Raw sources to wiki memory to gates to deliverables, organized by the 3 phases of Local SEO.</desc>
<defs>
  <style>
    .h1 { font: 700 28px Inter, Arial, sans-serif; fill: #172033; }
    .h2 { font: 700 14px Inter, Arial, sans-serif; fill: #172033; }
    .lbl { font: 500 12px Inter, Arial, sans-serif; fill: #334155; }
    .phase { font: 700 13px 'JetBrains Mono', monospace; fill: #ffffff; letter-spacing: 0.5px; }
    .box { fill: #ffffff; stroke-width: 2.5; }
    .arrow { stroke: #64748b; stroke-width: 2.5; fill: none; }
  </style>
  <marker id="arrowhead" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto">
    <path d="M0,0 L10,5 L0,10 z" fill="#64748b"/>
  </marker>
</defs>

<rect width="1080" height="580" fill="#fafaf7"/>

<text x="40" y="50" class="h1">Local SEO Brain: Operating Map</text>
<text x="40" y="76" class="lbl">Raw sources → wiki memory → gates → deliverables. Organized by task.</text>

<text x="60" y="120" class="h2">RAW SOURCES (.raw/)</text>
<g><rect x="50" y="135" width="200" height="48" rx="6" class="box" stroke="#586f92"/>
<text x="62" y="158" class="lbl">GBP CSV export</text><text x="62" y="173" class="lbl">→ ingest_gbp</text></g>
<g><rect x="50" y="193" width="200" height="48" rx="6" class="box" stroke="#586f92"/>
<text x="62" y="216" class="lbl">Citation export CSV</text><text x="62" y="231" class="lbl">→ ingest_citations</text></g>
<g><rect x="50" y="251" width="200" height="48" rx="6" class="box" stroke="#586f92"/>
<text x="62" y="274" class="lbl">Reviews JSON / CSV</text><text x="62" y="289" class="lbl">→ ingest_reviews</text></g>
<g><rect x="50" y="309" width="200" height="48" rx="6" class="box" stroke="#586f92"/>
<text x="62" y="332" class="lbl">Geo-grid CSV</text><text x="62" y="347" class="lbl">→ ingest_geogrid</text></g>
<g><rect x="50" y="367" width="200" height="48" rx="6" class="box" stroke="#586f92"/>
<text x="62" y="390" class="lbl">Manual evidence file</text><text x="62" y="405" class="lbl">→ ingest_source</text></g>

<text x="320" y="120" class="h2">WIKI MEMORY</text>

<g><rect x="310" y="135" width="220" height="100" rx="6" class="box" stroke="#2f7f87"/>
<rect x="310" y="135" width="220" height="22" rx="6" fill="#2f7f87"/>
<text x="320" y="151" class="phase">PHASE 1: PROPERTY</text>
<text x="320" y="178" class="lbl">audits/ · content/</text>
<text x="320" y="196" class="lbl">concepts/ · frameworks/</text>
<text x="320" y="214" class="lbl">locations/ · keywords/</text>
<text x="320" y="230" class="lbl">Evidence review playbooks</text></g>

<g><rect x="310" y="247" width="220" height="100" rx="6" class="box" stroke="#c85f4d"/>
<rect x="310" y="247" width="220" height="22" rx="6" fill="#c85f4d"/>
<text x="320" y="263" class="phase">PHASE 2: GBP</text>
<text x="320" y="290" class="lbl">gbp/: guarded working notes</text>
<text x="320" y="308" class="lbl">verification · description</text>
<text x="320" y="326" class="lbl">categories · services · posts</text>
<text x="320" y="342" class="lbl">geotagging · holiday hours</text></g>

<g><rect x="310" y="359" width="220" height="100" rx="6" class="box" stroke="#f0b33d"/>
<rect x="310" y="359" width="220" height="22" rx="6" fill="#f0b33d"/>
<text x="320" y="375" class="phase">PHASE 3: BACKLINKS</text>
<text x="320" y="402" class="lbl">backlinks/ · citations/</text>
<text x="320" y="420" class="lbl">Earned-link review guidance</text>
<text x="320" y="438" class="lbl">Listing status review</text>
<text x="320" y="454" class="lbl">citation evidence snapshots</text></g>

<g><rect x="310" y="471" width="220" height="60" rx="6" class="box" stroke="#7c4ddb" stroke-dasharray="4 3"/>
<text x="320" y="491" class="h2">LLM SEO (cross-cutting)</text>
<text x="320" y="510" class="lbl">llm-seo/ · prompts/</text>
<text x="320" y="526" class="lbl">schema · Reddit · AI Overviews</text></g>

<text x="600" y="120" class="h2">GATES &amp; CHECKS</text>
<g><rect x="590" y="135" width="190" height="42" rx="6" class="box" stroke="#c85f4d"/>
<text x="600" y="161" class="lbl">No source → no recommend</text></g>
<g><rect x="590" y="187" width="190" height="42" rx="6" class="box" stroke="#c85f4d"/>
<text x="600" y="213" class="lbl">External systems read-only</text></g>
<g><rect x="590" y="239" width="190" height="42" rx="6" class="box" stroke="#c85f4d"/>
<text x="600" y="265" class="lbl">Edits → approval queue</text></g>
<g><rect x="590" y="291" width="190" height="42" rx="6" class="box" stroke="#c85f4d"/>
<text x="600" y="317" class="lbl">No PII in review notes</text></g>
<g><rect x="590" y="343" width="190" height="42" rx="6" class="box" stroke="#c85f4d"/>
<text x="600" y="369" class="lbl">No spam / fake reviews</text></g>
<g><rect x="590" y="395" width="190" height="42" rx="6" class="box" stroke="#c85f4d"/>
<text x="600" y="421" class="lbl">No mass low-quality citations</text></g>

<text x="850" y="120" class="h2">DELIVERABLES</text>
<g><rect x="840" y="135" width="200" height="48" rx="6" class="box" stroke="#f0b33d"/>
<text x="852" y="158" class="lbl">Draft Health Scorecard</text>
<text x="852" y="173" class="lbl">deliverables/</text></g>
<g><rect x="840" y="193" width="200" height="48" rx="6" class="box" stroke="#f0b33d"/>
<text x="852" y="216" class="lbl">Draft Action Roadmap</text>
<text x="852" y="231" class="lbl">deliverables/</text></g>
<g><rect x="840" y="251" width="200" height="48" rx="6" class="box" stroke="#f0b33d"/>
<text x="852" y="274" class="lbl">Draft Weekly Report</text>
<text x="852" y="289" class="lbl">reports/</text></g>
<g><rect x="840" y="309" width="200" height="48" rx="6" class="box" stroke="#f0b33d"/>
<text x="852" y="332" class="lbl">Approval Queue</text>
<text x="852" y="347" class="lbl">decisions/</text></g>
<g><rect x="840" y="367" width="200" height="48" rx="6" class="box" stroke="#f0b33d"/>
<text x="852" y="390" class="lbl">Audit Findings</text>
<text x="852" y="405" class="lbl">audits/</text></g>

<path d="M 250 275 H 310" class="arrow" marker-end="url(#arrowhead)"/>
<path d="M 530 275 H 590" class="arrow" marker-end="url(#arrowhead)"/>
<path d="M 780 275 H 840" class="arrow" marker-end="url(#arrowhead)"/>
</svg>
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    vault = Path(args.vault).expanduser().resolve()
    if not (vault / "wiki").is_dir():
        raise SystemExit(f"ERROR: vault has no wiki/: {vault}")
    out_dir = vault / "_attachments"
    target = out_dir / "brain-relationship-map.svg"
    if args.dry_run:
        print(f"DRY-RUN: would render {target}")
        return 0
    out_dir.mkdir(parents=True, exist_ok=True)
    target.write_text(RELATIONSHIP_SVG, encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

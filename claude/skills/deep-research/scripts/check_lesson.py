import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_map_geometry as geo
from lesson_rules import (
    ANCHOR,
    BARE_URL,
    CHAPTER_OF,
    HREF,
    SUMMARY_MIN_WORDS,
    TAG_CODE,
    TIMESTAMP,
    YOUTUBE,
    prose_problems,
    word_count,
)

SRC = re.compile(r'src="([^"]+)"')
SURTITLE = re.compile(r'<p[^>]*class="[^"]*surtitle[^"]*"[^>]*>.*?</p>', re.S | re.I)
QUIZ = re.compile(r'<div[^>]*class="[^"]*quiz[^"]*"', re.I)
FOOTER_RE = re.compile(
    r"<[^>]*lesson-footer[^>]*>(.*?)(?:</footer>|</div>)", re.S | re.I
)
CAPS_RUN = re.compile(r"\b(?:[A-Z]{2,}\s+){2,}[A-Z]{2,}\b")
META_P = re.compile(r'<p[^>]*class="[^"]*meta[^"]*"[^>]*>(.*?)</p>', re.S | re.I)
KICKER_P = re.compile(r'<p[^>]*class="[^"]*kicker[^"]*"', re.I)
HTML_COMMENT = re.compile(r"<!--(.*?)-->", re.S)
REVIEW_COMMENT_TEXT = re.compile(r"stray content flag|flagged for (?:human )?review", re.I)
BAR_RE = re.compile(r'<header[^>]*class="[^"]*A-bar[^"]*"([^>]*)>(.*?)</header>', re.S | re.I)
BODY_RE = re.compile(r"</header>(.*?)(?=<[^>]*lesson-footer|\Z)", re.S | re.I)
DATE_LINE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
INDEX_ROW = re.compile(r'<li[^>]*id="ch\d+"[^>]*>(.*?)</li>', re.S | re.I)
ROW_TEXT = re.compile(r"^\d+ · \S")
EDGE_TOKEN = re.compile(r"^var\(--d(?:[1-6]|-neutral)\)$")
SWATCH = re.compile(r'class="swatch"[^>]*background:\s*(var\(--d[^)]*\))')
SVG_BLOCK = re.compile(r"<svg\b.*?</svg>", re.S)
MAP_FIGURE = re.compile(r'<figure\b[^>]*class="[^"]*\bmap\b[^"]*"[^>]*>.*?</figure>', re.S | re.I)
SUMMARY_BLOCK = re.compile(r"<h2[^>]*>\s*summary\s*</h2>\s*<p\b.*?</p>", re.S | re.I)
MAX_DIAGRAMS = 2


def stray_timestamps(tag_stripped):
    stray = []
    for m in TIMESTAMP.finditer(tag_stripped):
        tail = tag_stripped[m.end() : m.end() + 4]
        if re.match(r"-c[rv]\b", tail):
            continue
        stray.append(m.group(0))
    return sorted(set(stray))


def page_type(path):
    norm = path.replace(os.sep, "/")
    if "/lessons/" in norm:
        return "lesson"
    if (
        "learning-records/" in norm
        or "/transcripts/" in norm
        or norm.endswith("lesson.stencil.html")
    ):
        return "skip"
    base = os.path.basename(norm)
    if "/reference/" in norm:
        return "timeline" if base == "timeline.html" else "reference"
    if base == "index.html":
        return "index"
    return "lesson"


def bar_issues(html, ptype):
    issues = []
    bars = BAR_RE.findall(html)
    if len(bars) != 1:
        issues.append(f"A-bar: expected exactly one top bar, found {len(bars)}")
    attrs, bar = bars[0] if bars else ("", "")
    home = 'data-state="home"' in attrs
    if ptype == "index" and not home:
        issues.append('A-bar: index pages carry the home bar (data-state="home": Topic picker, Chapter picker, Aa)')
    if home:
        if not re.search(r"<select[^>]*data-topic", bar):
            issues.append("A-bar: home bar missing the Topic picker (data-topic)")
        if not re.search(r'class="lbl">\s*Topic\s*<', bar):
            issues.append("A-bar: home bar labels its topic picker 'Topic'")
        if not (re.search(r"<select[^>]*data-index", bar) and re.search(r'class="lbl">\s*Chapter\s*<', bar)):
            issues.append("A-bar: home bar carries a labelled Chapter picker (data-index)")
    else:
        if not re.search(r'<span[^>]*class="[^"]*title[^"]*"[^>]*>\s*\S', bar):
            issues.append("A-bar: missing non-empty topic name")
        if not re.search(r"<select[^>]*data-index", bar):
            issues.append("A-bar: missing chapter dropdown (data-index)")
    if bars and not (re.search(r'class="aa"', bar) and re.search(r'class="sep"', bar)):
        issues.append("A-bar: text settings sit after a divider behind an 'Aa' mark")
    font_sel = re.search(r"<select[^>]*data-font-select[^>]*>(.*?)</select>", bar, re.S | re.I)
    if not font_sel:
        issues.append("A-bar: missing font menu (data-font-select)")
    elif len(re.findall(r"<option", font_sel.group(1))) < 12:
        issues.append("A-bar: font menu has fewer than 12 fonts")
    size_sel = re.search(r"<select[^>]*data-size-select[^>]*>(.*?)</select>", bar, re.S | re.I)
    if not size_sel:
        issues.append("A-bar: missing size menu (data-size-select)")
    else:
        sizes = [s.strip() for s in re.findall(r"<option[^>]*>([^<]+)", size_sel.group(1))]
        if sorted(sizes) != ["L", "M", "S", "XL"]:
            issues.append(f"A-bar: size menu must offer exactly S/M/L/XL, found {sizes}")
    if not re.search(r'<script[^>]*src="[^"]*course-index\.js"', html):
        issues.append("A-bar: missing <script src=...course-index.js> (chapter list feed)")
    if not re.search(r'<script[^>]*src="[^"]*shell\.js"', html):
        issues.append("A-bar: missing <script src=...shell.js> (bar behaviour)")
    if ptype == "lesson" and bars:
        title = re.search(r'<span[^>]*class="[^"]*title[^"]*"[^>]*>(.*?)</span>', bar, re.S)
        if title and 'href="../index.html"' not in title.group(1):
            issues.append("A-bar: the topic name links the course index (../index.html)")
    return issues


def svg_issues(html):
    """The geometry gate: every overlap fails; colour, direction and legend rules."""
    issues = []
    svgs = SVG_BLOCK.findall(html)
    ids = re.findall(r'\bid="([^"]+)"', "".join(svgs))
    for dup in sorted({i for i in ids if ids.count(i) > 1}):
        issues.append(f"diagram: id '{dup}' repeats across the page's SVGs (scope ids per diagram)")
    figures = MAP_FIGURE.findall(html)
    if len(figures) > MAX_DIAGRAMS:
        issues.append(f"diagram: {len(figures)} diagrams, the cap is {MAX_DIAGRAMS} per chapter")
    for n, svg in enumerate(svgs, start=1):
        tag = f"diagram {n}"
        home = next((f for f in figures if svg in f), None)
        if home is None:
            issues.append(f'{tag}: the SVG sits outside <figure class="map">')
        legend = set(SWATCH.findall(home or ""))
        if re.search(r"<(?:path|polyline|polygon|circle|ellipse)\b", re.sub(r"<defs>.*?</defs>", "", svg, flags=re.S)):
            issues.append(f"{tag}: every edge is a straight <line>: no <path>, <polyline> or curves")
        h = geo.analyze(svg)
        for key, what in (
            ("edge_box", "a line passes through a box"),
            ("box_box", "boxes overlap"),
            ("label_box", "a label covers a box"),
            ("label_label", "labels overlap"),
            ("label_line", "a label sits on a line"),
            ("arrow", "arrowheads merge"),
            ("bounds", "content lies outside the viewBox"),
        ):
            if h[key]:
                issues.append(f"{tag}: {what} ({len(h[key])}x): {str(h[key][0])[:120]}")
        if re.search(r"stroke-dasharray", svg):
            issues.append(f"{tag}: dashed line: every line is solid")
        if re.search(r"<text\b[^>]*\btransform=", svg):
            issues.append(f"{tag}: rotated text: labels sit beside their line, unrotated")
        edges = [geo.attrs(t) for t in re.findall(r"<line\b[^>]*>", svg)]
        for e in edges:
            if not EDGE_TOKEN.match(e.get("stroke", "")):
                issues.append(f"{tag}: line colour '{e.get('stroke')}' is not a palette token (var(--d1)..var(--d6), var(--d-neutral))")
        counts = {}
        for e in edges:
            counts[e.get("stroke", "")] = counts.get(e.get("stroke", ""), 0) + 1
        for tok, n_used in counts.items():
            if tok != "var(--d-neutral)" and n_used < 2:
                issues.append(f"{tag}: colour {tok} marks one line: a colour needs a relationship type that repeats (2+ lines); a one-off is neutral")
            if EDGE_TOKEN.match(tok) and tok not in legend:
                issues.append(f"{tag}: colour {tok} has no legend row")
        if len(re.findall(r'class="elabel"', svg)) != len(edges):
            issues.append(f"{tag}: every line carries its own label")
        defs = set(re.findall(r'<marker[^>]*\bid="([^"]+)"', svg))
        for ref in re.findall(r'marker-end="url\(#([^)]+)\)"', svg):
            if ref not in defs:
                issues.append(f"{tag}: arrowhead marker '{ref}' is not defined in the SVG")
    return issues


def check(path):
    issues = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        html = fh.read()
    low = html.lower()
    ptype = page_type(path)
    href_all = HREF.findall(html)
    anchor_stripped = ANCHOR.sub(" ", html)
    tag_stripped = re.sub(r"<[^>]*>", " ", html)

    if any(REVIEW_COMMENT_TEXT.search(c) for c in HTML_COMMENT.findall(html)):
        issues.append(
            "internal review-comment HTML leaked into the page — resolve or remove before publishing, never ship as an HTML comment"
        )

    if QUIZ.search(html):
        issues.append("quiz block present: no quizzes/questionnaires in lessons")
    if "quiz" in low:
        issues.append("'quiz' mentioned: no quizzes/questionnaires in lessons")
    if "ask your teacher" in low or "box-teacher" in low or "your teacher" in low:
        issues.append("teacher reference: lessons carry no teacher apparatus")

    for phrase in (
        "boundar",
        "nothing past",
        "stops there",
        "this lesson covers chapter",
    ):
        if phrase in low:
            issues.append(
                f"boundary narration found: '{phrase}' — lessons never mention boundaries or stop points"
            )

    if CHAPTER_OF.search(tag_stripped):
        issues.append("'Chapter N of M' present: no chapter count anywhere on the page")
    if "book / video" in low:
        issues.append("'Book / Video' present: the label is 'Topic'")
    if ptype == "lesson":
        if SURTITLE.search(html):
            issues.append("surtitle present: the chapter header is the chapter name alone")
        if KICKER_P.search(html):
            issues.append("kicker present: the topic name lives in the bar, the header is the chapter name alone")
        stray = stray_timestamps(tag_stripped)
        if stray:
            issues.append(
                f"timestamps found (no timestamps anywhere on the page): {stray[:5]}"
            )
    if ptype == "index":
        if DATE_LINE.search(tag_stripped) or stray_timestamps(tag_stripped):
            issues.append("date line present: index pages carry no date or time")

    if YOUTUBE.search(html):
        issues.append("YouTube URL present: a YouTube video is never a source")
    if "canon-checked" in low or "canon checked" in low:
        issues.append(
            "'canon-checked' wording present: name the source, never a 'canon'"
        )

    if "how this treatise was built" in low:
        issues.append("method box: lessons carry no method block")
    if re.search(r"<strong>\s*primary source", low):
        issues.append("primary-source block: lessons carry no primary-source box")
    if "next on request" in low:
        issues.append("next-steps line: lessons carry no 'next on request'")

    if ptype == "lesson" and not re.search(r'href="https?://', html):
        issues.append(
            "no hyperlinked sources (each cited source links to its actual page)"
        )
    bare = BARE_URL.findall(anchor_stripped)
    if bare:
        issues.append(f"bare URL text (wrap it in a link): {bare[:3]}")
    tag_hit = TAG_CODE.findall(anchor_stripped)
    if tag_hit:
        issues.append(
            f"bare tag code (points nowhere — use a real hyperlink on the source-naming words): {sorted(set(tag_hit))[:5]}"
        )

    if ptype == "lesson":
        m = BODY_RE.search(html)
        prose = m.group(1) if m else html
        seen = set()
        for rule, detail in prose_problems(prose):
            if rule in ("bare-url", "tag-code", "timestamp"):
                continue
            if rule not in seen:
                issues.append(f"{rule}: {detail}")
                seen.add(rule)
        if SUMMARY_BLOCK.search(prose):
            text_only = re.sub(r"<h1[^>]*>.*?</h1>", " ", MAP_FIGURE.sub(" ", SUMMARY_BLOCK.sub(" ", prose)), flags=re.S | re.I)
            if word_count(text_only) < SUMMARY_MIN_WORDS:
                issues.append(
                    f"summary present in a short chapter ({word_count(text_only)} words): a summary only when the chapter needs one (>= {SUMMARY_MIN_WORDS} words)"
                )
        issues.extend(svg_issues(html))

    if re.search(r"<h2[^>]*>[^<]*(fact-check|what the record shows|record box)", low):
        issues.append(
            "standalone fact-check/record section: fold the facts into the prose"
        )
    if "box-fact" in low or "box-record" in low:
        issues.append(
            "fact/record box present: fold the facts into the prose, never a box"
        )
    if "open threads" in low:
        issues.append("open-threads section: lessons carry no Open Threads")
    if re.search(r"<h[1-6][^>]*>[^<]*(sources|references|bibliography)", low):
        issues.append(
            "Sources/References/Bibliography heading present: citations are links in the prose, no list anywhere"
        )
    caps_hits = CAPS_RUN.findall(tag_stripped)
    if caps_hits:
        issues.append(f"all-caps text run (3+ words): {caps_hits[:3]}")

    if ptype in ("lesson", "reference", "timeline") and "lesson-footer" not in low:
        issues.append("missing lesson footer")

    if ptype in ("lesson", "reference", "timeline", "index"):
        issues.extend(bar_issues(html, ptype))

    if ptype == "lesson":
        if re.search(r'<p[^>]*class="[^"]*meta[^"]*"', html, re.I):
            issues.append(
                "meta row present: lessons carry no <p class=meta>; topic, chapters and text settings live in the A-bar"
            )
        footer_m = FOOTER_RE.search(html)
        if footer_m:
            for h in HREF.findall(footer_m.group(1)):
                base_h = h.split("#")[0]
                if (
                    base_h in ("../../index.html", "../index.html")
                    or "glossary" in h.lower()
                    or "cast-map" in h.lower()
                ):
                    issues.append(
                        f"lesson footer holds a nav link (index/glossary/cast belong in the course index): {h}"
                    )

    if ptype == "index":
        for phrase, fix in (
            (
                "eight treatises",
                "eight-treatises wording present: use 'Section treatises'",
            ),
            (
                "<td>Live</td>",
                "Live cell present: drop the Status column, standings live in prose",
            ),
            (
                "<th>Status</th>",
                "Status column present: drop it, standings live in prose",
            ),
            (
                "The pages</h2>",
                "links section present: companion listing lives in the generated home, not here",
            ),
            (
                "How this course works</h2>",
                "how-works section present: method lives in lessons, not here",
            ),
            ("Workspace:", "workspace footer line present: footers carry nav only"),
            (
                "Cast roster ·",
                "old 'Cast roster · Glossary' section: Cast, Glossary and Timeline sit inside the index",
            ),
        ):
            if phrase.lower() in low or phrase in html:
                issues.append(f"index: {fix}")
        if re.search(r"\bspine\b", low):
            issues.append("spine wording present: use 'course source', never 'spine'")
        if re.search(r"\bstatus\b", low) and "status code" not in low:
            issues.append("status wording present: use 'standing', never 'status'")
        if re.search(r"\bmission\b", low) and "permission" not in low:
            issues.append(
                "mission wording present: no MISSION file, slug names the source"
            )
        if "provisional" in low:
            issues.append("provisional wording present: no draft-status labels")
        if (
            not re.search(r'href="lessons/', html)
            and len([h for h in href_all if h.endswith("/index.html")]) < 2
        ):
            issues.append(
                "index: no chapter links (index lists its lessons or workspace homes)"
            )
        for row in INDEX_ROW.findall(html):
            text = " ".join(re.sub(r"<[^>]*>", " ", row).split())
            if not ROW_TEXT.match(text):
                issues.append(f"index: chapter row '{text[:40]}' reads 'N · name'")
        extras = re.search(r'<nav[^>]*class="index-extras"[^>]*>(.*?)</nav>', html, re.S | re.I)
        inside = set(HREF.findall(extras.group(1))) if extras else set()
        outside = [h for h in href_all if h.startswith("reference/") and h not in inside]
        if outside:
            issues.append(
                f'index: Cast, Glossary and Timeline links sit inside <nav class="index-extras">: {outside[:3]}'
            )

    if ptype in ("reference", "timeline"):
        if KICKER_P.search(html):
            issues.append(
                "kicker present: reference pages carry no kicker, H1 opens the page"
            )
        meta_m = META_P.search(html)
        if meta_m and (
            "lessons/" in meta_m.group(1) or "transcripts/" in meta_m.group(1)
        ):
            issues.append(
                "header meta lists lessons/slices: keep the short cross-link line (cast · glossary · timeline)"
            )
        if re.search(r"<h2[^>]*>\s*Links\s*</h2>", html):
            issues.append(
                "links section present: companion listing lives in the generated home, not here"
            )
        if "How to read this page" in html:
            issues.append("how-read box present: pages open cold, no reading guide")
        if "Workspace:" in html:
            issues.append("workspace footer line present: footers carry nav only")
        footer_m = FOOTER_RE.search(html)
        if footer_m and "<p" in footer_m.group(1):
            issues.append("footer paragraph present: reference footers carry nav only")

    if ptype == "timeline":
        if re.search(r'class="tag', html):
            issues.append(
                "kind tag present: timeline entries carry standing words, no colour tags"
            )
        if re.search(r"<h2[^>]*>[^<]*[Ll]egend", html):
            issues.append("legend present: no kind legend on text-only timelines")
        if "seven kinds" in low:
            issues.append(
                "kinds wording present: no kind taxonomy on text-only timelines"
            )

    base = os.path.dirname(os.path.abspath(path))

    allow = ["../../index.html", "../index.html"]
    if ptype == "index":
        allow.append("index.html")

    home_hrefs = [h for h in href_all if h == "../../index.html"]
    if ptype == "lesson" and len(home_hrefs) > 1:
        issues.append(
            f"home link repeated {len(home_hrefs)}x (budget: ../../index.html at most once)"
        )
    backlink_hrefs = [h for h in href_all if h.split("#")[0] == "../index.html"]
    if ptype == "lesson" and len(backlink_hrefs) > 1:
        issues.append(
            f"course-index link repeated {len(backlink_hrefs)}x (budget: ../index.html* at most once)"
        )
    gloss_hrefs = [h for h in href_all if "glossary" in h.lower()]
    if ptype == "lesson" and len(gloss_hrefs) > 1:
        issues.append(
            f"glossary link repeated {len(gloss_hrefs)}x (budget: glossary at most once)"
        )
    castmap_hrefs = [h for h in href_all if "cast-map" in h.lower()]
    if ptype == "lesson" and len(castmap_hrefs) > 1:
        issues.append(
            f"cast-map link repeated {len(castmap_hrefs)}x (budget: cast-map at most once)"
        )

    for href in href_all:
        if href.startswith(("http://", "https://", "#", "mailto:", "data:")):
            continue
        if href in allow or href.split("#")[0] in allow:
            continue
        target = href.split("#")[0]
        if not target:
            continue
        if not os.path.exists(os.path.normpath(os.path.join(base, target))):
            issues.append(f"dangling link: {href}")
    for src in SRC.findall(html):
        if src.startswith(("http://", "https://", "data:")):
            continue
        target = src.split("?")[0]
        if target and not os.path.exists(os.path.normpath(os.path.join(base, target))):
            issues.append(f"missing asset: {src}")
    return issues


def main():
    ap = argparse.ArgumentParser(
        description="Check any course page against the workspace rules by path: lessons/ gets full lesson rules (A-bar with topic name, chapter dropdown and Aa settings; chapter name alone as header; unnumbered headings; citations as links on source-naming words; no verification narration, correction ledger or teacher voice; summary only when long; diagrams pass the geometry gate with palette-token colours, solid lines and legend rows); workspace index gets index rules (home bar, 'N · name' rows, Cast/Glossary/Timeline inside the index, no date line); reference/ gets header/footer rules (no kicker, short cross-link meta, no Links section, no how-read box, nav-only footer); timeline adds text-only rules (no kind tags, no legend). Fragments, slices, and stencil copies report SKIP."
    )
    ap.add_argument("files", nargs="+", help="course HTML file(s)")
    args = ap.parse_args()

    failed = 0
    for path in args.files:
        if page_type(path) == "skip":
            print("SKIP (not a gated page type) " + path)
            continue
        issues = check(path)
        print(("OK " if not issues else "PROBLEMS ") + path)
        for issue in issues:
            print("   - " + issue)
        if issues:
            failed += 1
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

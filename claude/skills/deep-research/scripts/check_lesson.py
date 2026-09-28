import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lesson_rules import (
    ANCHOR,
    BARE_URL,
    HREF,
    SECTION_REF,
    TAG_CODE,
    TIMESTAMP,
    VERDICT,
    YOUTUBE,
    find_unsuperscripted_repeats,
)

SRC = re.compile(r'src="([^"]+)"')
OPTION_VALUE = re.compile(r'<option[^>]*value="([^"]*)"')
HEADING = re.compile(r"<h2[^>]*>\s*(\d+)[.)]")
SURTITLE = re.compile(r'<p[^>]*class="[^"]*surtitle[^"]*"[^>]*>.*?</p>', re.S | re.I)
QUIZ = re.compile(r'<div[^>]*class="[^"]*quiz[^"]*"', re.I)
FOOTER_RE = re.compile(
    r"<[^>]*lesson-footer[^>]*>(.*?)(?:</footer>|</div>)", re.S | re.I
)
SUP_BLOCK = re.compile(r"<sup>.*?</sup>", re.S | re.I)
CAPS_RUN = re.compile(r"\b(?:[A-Z]{2,}\s+){2,}[A-Z]{2,}\b")
META_P = re.compile(r'<p[^>]*class="[^"]*meta[^"]*"[^>]*>(.*?)</p>', re.S | re.I)
KICKER_P = re.compile(r'<p[^>]*class="[^"]*kicker[^"]*"', re.I)
HTML_COMMENT = re.compile(r"<!--(.*?)-->", re.S)
REVIEW_COMMENT_TEXT = re.compile(r"stray content flag|flagged for (?:human )?review", re.I)


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

    if ptype == "lesson" and not SURTITLE.search(html):
        issues.append(
            'missing surtitle: <p class="surtitle">Chapter N of M</p> under the H1'
        )
    if ptype == "lesson":
        stray = stray_timestamps(tag_stripped)
        if stray:
            issues.append(
                f"timestamps found (no timestamps anywhere on the page): {stray[:5]}"
            )

    if YOUTUBE.search(html):
        issues.append("YouTube URL present: a YouTube video is never a source")
    if "canon-checked" in low or "canon checked" in low:
        issues.append(
            "'canon-checked' wording present: verdicts use confirmed/corrected/etc, not 'canon'"
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
            f"bare tag code (points nowhere — use a real hyperlink beside bare numerals): {sorted(set(tag_hit))[:5]}"
        )

    if ptype == "lesson":
        for target, _ in find_unsuperscripted_repeats(html):
            issues.append(
                f"repeat citation not superscripted: {target} - every mention after the first must be <sup><a href=...>"
            )
        for m in SUP_BLOCK.finditer(html):
            if not ANCHOR.search(m.group(0)):
                issues.append(
                    f"bare superscript marker, no link inside: {m.group(0)[:40]} - superscript IS the citation, never a bare marker"
                )

    if re.search(r"<h2[^>]*>[^<]*(fact-check|what the record shows|record box)", low):
        issues.append(
            "standalone fact-check/record section: verdicts live inline in the narrative"
        )
    if "box-fact" in low or "box-record" in low:
        issues.append(
            "fact/record box present: verdicts live inline in the narrative, never in a box"
        )
    if "open threads" in low:
        issues.append("open-threads section: lessons carry no Open Threads")
    if re.search(r"<h[1-6][^>]*>[^<]*(sources|references|bibliography)", low):
        issues.append(
            "Sources/References/Bibliography heading present: citations are inline-only, no footer block anywhere"
        )
    caps_hits = CAPS_RUN.findall(tag_stripped)
    if caps_hits:
        issues.append(f"all-caps text run (3+ words): {caps_hits[:3]}")
    if ptype == "lesson":
        verdicts = VERDICT.findall(low)
        if len(verdicts) < 2:
            issues.append(
                "no inline verdicts in narrative (verdict words like confirmed/corrected/unfindable beside the quoted wording)"
            )

    if ptype in ("lesson", "reference", "timeline") and "lesson-footer" not in low:
        issues.append("missing lesson footer")

    if ptype == "lesson":
        navs = re.findall(
            r'<nav[^>]*class="[^"]*top-nav[^"]*"[^>]*>(.*?)</nav>', html, re.S | re.I
        )
        if len(navs) != 1:
            issues.append(
                f"top-nav: expected exactly one merged nav row, found {len(navs)}"
            )
        nav = navs[0] if navs else ""
        for label, pat in (
            ("Home", r">Home<"),
            ("Chapter Index", r">Chapter Index<"),
            ("Glossary", r">Glossary<"),
            ("Cast Map", r">Cast Map<"),
        ):
            if not re.search(pat, nav):
                issues.append(
                    f"top-nav: missing Title Case cell '{label}' in merged nav"
                )
        if re.search(r'<p[^>]*class="[^"]*meta[^"]*"', html, re.I):
            issues.append(
                "meta row present: lessons carry no <p class=meta>; the merged nav holds Home · Chapter Index · Glossary · Cast Map"
            )
        if not re.search(r'href="[^"]*glossary[^"]*"', low):
            issues.append(
                "top-nav: no glossary link (glossary link sits in the merged top nav)"
            )
        if 'href="../../index.html"' not in html:
            issues.append(
                'top-nav: no home link (needs href="../../index.html" inside <nav class="top-nav">)'
            )
        if not re.search(r'href="\.\./index\.html#ch\d+"', html):
            issues.append(
                'top-nav: no chapter-index backlink (needs href="../index.html#chN")'
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
                "header meta lists lessons/slices: keep the short cross-link line (cast roster · glossary · chapter index)"
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

    if ptype == "lesson":
        headings = {int(n) for n in HEADING.findall(html)}
        if headings:
            for match in SECTION_REF.findall(html):
                for num in (int(t) for t in re.findall(r"\d+", match)):
                    if num not in headings:
                        issues.append(
                            f"section reference to {num} but no such heading (headings: {sorted(headings)})"
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
            f"chapter-index link repeated {len(backlink_hrefs)}x (budget: ../index.html* at most once)"
        )
    gloss_hrefs = [h for h in href_all if "glossary" in h.lower()]
    if ptype == "lesson" and len(gloss_hrefs) > 1:
        issues.append(
            f"glossary link repeated {len(gloss_hrefs)}x (budget: glossary at most once, merged nav only)"
        )
    castmap_hrefs = [h for h in href_all if "cast-map" in h.lower()]
    if ptype == "lesson" and len(castmap_hrefs) > 1:
        issues.append(
            f"cast-map link repeated {len(castmap_hrefs)}x (budget: cast-map at most once, merged nav only)"
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
        description="Check any course page against the workspace rules by path: lessons/ gets full lesson rules (merged nav, inline verdicts + inline-only citations with superscript repeats, no bare tag codes, no Sources/References block, no fact-check boxes or Open Threads, no all-caps runs, hyperlinked sources, links/assets); workspace index gets index rules (chapter links, no Status/Spine/Live/Pages/How-works/Mission wording, nav-only footer); reference/ gets header/footer rules (no kicker, short cross-link meta, no Links section, no how-read box, nav-only footer); timeline adds text-only rules (no kind tags, no legend). Fragments, slices, and stencil copies report SKIP."
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

import argparse
import os
import re
import sys

HREF = re.compile(r'href="([^"]+)"')
SRC = re.compile(r'src="([^"]+)"')
HEADING = re.compile(r"<h2[^>]*>\s*(\d+)[.)]")
SECTION_REF = re.compile(
    r"(?:§|\bsections?\b)\s*(\d+(?:\s*(?:,|and|&|through)\s*\d+)*)", re.I
)
SURTITLE = re.compile(r'<p[^>]*class="[^"]*surtitle[^"]*"[^>]*>.*?</p>', re.S | re.I)
TIMESTAMP = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
ANCHOR = re.compile(r"<a\b.*?</a>", re.S | re.I)
QUIZ = re.compile(r'<div[^>]*class="[^"]*quiz[^"]*"', re.I)
FOOTER_RE = re.compile(
    r"<[^>]*lesson-footer[^>]*>(.*?)(?:</footer>|</div>)", re.S | re.I
)
SUP_BLOCK = re.compile(r"<sup>.*?</sup>", re.S | re.I)
SUP_WRAP = re.compile(r"<sup>\s*$")
CAPS_RUN = re.compile(r"\b(?:[A-Z]{2,}\s+){2,}[A-Z]{2,}\b")


def stray_timestamps(html):
    text = re.sub(r"<[^>]*>", " ", html)
    stray = []
    for m in TIMESTAMP.finditer(text):
        tail = text[m.end() : m.end() + 4]
        if re.match(r"-c[rv]\b", tail):
            continue
        stray.append(m.group(0))
    return sorted(set(stray))


def check(path):
    issues = []
    with open(path, encoding="utf-8", errors="replace") as fh:
        html = fh.read()
    low = html.lower()

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

    if not SURTITLE.search(html):
        issues.append(
            'missing surtitle: <p class="surtitle">Chapter N of M</p> under the H1'
        )
    stray = stray_timestamps(html)
    if stray:
        issues.append(
            f"timestamps found (no timestamps anywhere on the page): {stray[:5]}"
        )

    if re.search(r"youtube\.com|youtu\.be", html, re.I):
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

    if not re.search(r'href="https?://', html):
        issues.append(
            "no hyperlinked sources (each cited source links to its actual page)"
        )
    bare = re.findall(r"https?://\S+", ANCHOR.sub(" ", html))
    if bare:
        issues.append(f"bare URL text (wrap it in a link): {bare[:3]}")
    tag_hit = re.findall(r"\[[A-Z]{1,3}\d+[a-z]?\]", ANCHOR.sub(" ", html))
    if tag_hit:
        issues.append(
            f"bare tag code (points nowhere — use a real hyperlink beside bare numerals): {sorted(set(tag_hit))[:5]}"
        )

    seen_citations = set()
    for m in ANCHOR.finditer(html):
        hrefs = HREF.findall(m.group(0))
        if not hrefs or not hrefs[0].startswith(("http://", "https://")):
            continue
        target = hrefs[0].split("#")[0]
        if target in seen_citations:
            preceding = html[: m.start()]
            if not SUP_WRAP.search(preceding):
                issues.append(
                    f"repeat citation not superscripted: {target} - every mention after the first must be <sup><a href=...>"
                )
        else:
            seen_citations.add(target)
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
    caps_hits = CAPS_RUN.findall(re.sub(r"<[^>]*>", " ", html))
    if caps_hits:
        issues.append(f"all-caps text run (3+ words): {caps_hits[:3]}")
    verdicts = re.findall(
        r"\b(confirmed|corrected|partially correct|wrong|unfindable|unverified|allegation)\b",
        low,
    )
    if len(verdicts) < 2:
        issues.append(
            "no inline verdicts in narrative (verdict words like confirmed/corrected/unfindable beside the quoted wording)"
        )

    if "lesson-footer" not in low:
        issues.append("missing lesson footer")
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
            issues.append(f"top-nav: missing Title Case cell '{label}' in merged nav")
    if re.search(r'<p[^>]*class="[^"]*meta[^"]*"', html, re.I):
        issues.append(
            "meta row present: lessons carry no <p class=meta>, nav holds Lesson NN"
        )
    if re.search(r"\bspine\b", low):
        issues.append("spine wording present: use 'course source', never 'spine'")
    if re.search(r"eight treatises", low):
        issues.append("eight-treatises wording present: use 'Section treatises'")
    if re.search(r"\bstatus\b", low) and "status code" not in low:
        issues.append("status wording present: use 'standing', never 'status'")
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
    footer_m = FOOTER_RE.search(html)
    footer_block = footer_m.group(1) if footer_m else ""
    footer_hrefs = HREF.findall(footer_block)

    headings = {int(n) for n in HEADING.findall(html)}
    if headings:
        for match in SECTION_REF.findall(html):
            for num in (int(t) for t in re.findall(r"\d+", match)):
                if num not in headings:
                    issues.append(
                        f"section reference to {num} but no such heading (headings: {sorted(headings)})"
                    )

    base = os.path.dirname(os.path.abspath(path))

    home_hrefs = [h for h in HREF.findall(html) if h == "../../index.html"]
    if len(home_hrefs) > 1:
        issues.append(
            f"home link repeated {len(home_hrefs)}x (budget: ../../index.html at most once)"
        )
    backlink_hrefs = [
        h for h in HREF.findall(html) if h.split("#")[0] == "../index.html"
    ]
    if len(backlink_hrefs) > 1:
        issues.append(
            f"chapter-index link repeated {len(backlink_hrefs)}x (budget: ../index.html* at most once)"
        )
    gloss_hrefs = [h for h in HREF.findall(html) if "glossary" in h.lower()]
    if len(gloss_hrefs) > 1:
        issues.append(
            f"glossary link repeated {len(gloss_hrefs)}x (budget: glossary at most once, merged nav only)"
        )
    castmap_hrefs = [h for h in HREF.findall(html) if "cast-map" in h.lower()]
    if len(castmap_hrefs) > 1:
        issues.append(
            f"cast-map link repeated {len(castmap_hrefs)}x (budget: cast-map at most once, merged nav only)"
        )

    for href in HREF.findall(html):
        if href.startswith(("http://", "https://", "#", "mailto:", "data:")):
            continue
        if href == "../../index.html" or href.split("#")[0] == "../index.html":
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
        description="Check a chapter lesson against the workspace rules (no quizzes, surtitle-only timestamps, inline verdicts + inline-only citations with superscript repeats, no Sources/References block anywhere, no fact-check boxes or Open Threads, no all-caps text runs, hyperlinked sources, links/assets)."
    )
    ap.add_argument("files", nargs="+", help="lesson HTML file(s)")
    args = ap.parse_args()

    failed = 0
    for path in args.files:
        issues = check(path)
        print(("OK " if not issues else "PROBLEMS ") + path)
        for issue in issues:
            print("   - " + issue)
        if issues:
            failed += 1
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()

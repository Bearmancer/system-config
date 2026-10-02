"""Shared regexes, content rules and A-bar markup for check_lesson.py,
stamp_lesson.py and publish_teach.py.

check_lesson.py and stamp_lesson.py enforce the same lesson-page rules at two
points (pre-stamp YAML text vs rendered HTML); this module is the one place
those rules live, so the two never drift.
"""

import re

TAG_CODE = re.compile(r"\[[A-Z]{1,3}\d+[a-z]?\]")
BARE_URL = re.compile(r"https?://\S+")
TIMESTAMP = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
SECTION_REF = re.compile(r"§\s*\d+")
YOUTUBE = re.compile(r"youtube\.com|youtu\.be", re.I)
ANCHOR = re.compile(r"<a\b.*?</a>", re.S | re.I)
HREF = re.compile(r'href="([^"]+)"')
SUP = re.compile(r"<sup\b", re.I)
NUMBERED_HEADING = re.compile(r"<h[2-6][^>]*>\s*\d{1,2}[.)]\s", re.I)
CHAPTER_OF = re.compile(r"\bchapter\s+\d+\s+of\s+\d+\b", re.I)

VERIFY_NARRATION = re.compile(
    r"\b(?:confirmed|checked|cross-checked|corrected|verified)\s+against\b"
    r"|\b(?:is|was|stays|remains)\s+(?:un)?verified\b(?!\s+by\b)"
    r"|\bpartially correct\b|\bunfindable\b",
    re.I,
)
VERDICT_LABEL = re.compile(
    r"<strong>\s*(?:confirmed|corrected|wrong|allegation)\s*</strong>", re.I
)
CORRECTION_LEDGER = re.compile(
    r"<(?:p|li|strong|h[1-6])\b[^>]*>\s*(?:<strong>\s*)?corrections?\s*(?:</strong>\s*)?:"
    r"|<h[1-6]\b[^>]*>\s*corrections?\s*</h[1-6]>",
    re.I,
)
TEACHER_VOICE = re.compile(
    r"\b(?:the|this) (?:lesson|closing line|opening line) "
    r"(?:works|delivers|teaches|shows|builds|argues|sets up)\b"
    r"|\bworks as a ladder\b|\bkey takeaways?\b|\blet'?s (?:see|look|start|dive|explore|walk|begin)\b"
    r"|\bwe(?:'ll| will) (?:see|learn|explore)\b",
    re.I,
)
WEAK_LINK_TEXT = re.compile(
    r"^(?:\[?\d+\]?|here|link|source|sources|this|this link|click here|read more|ref|reference)$",
    re.I,
)
SUMMARY_MIN_WORDS = 1200

FONTS = (
    "Literata", "Source Serif 4", "Newsreader", "Crimson Pro", "EB Garamond",
    "Merriweather", "Lora", "Libre Baskerville", "Atkinson Hyperlegible",
    "Inter", "IBM Plex Sans",
)


def strip_tags(html):
    return re.sub(r"<[^>]*>", " ", html)


def chapter_label(number, title):
    return f"{number} · {title}"


def word_count(html):
    return len(strip_tags(html).split())


def weak_anchor_texts(html):
    """Visible text of every anchor that names no source (a numeral, "here", ...)."""
    weak = []
    for m in ANCHOR.finditer(html):
        text = " ".join(strip_tags(m.group(0)).split())
        if not text or WEAK_LINK_TEXT.match(text):
            weak.append(text or "(empty)")
    return weak


def prose_problems(html):
    """Style violations in lesson prose (summary, body); (rule, detail) pairs."""
    text = strip_tags(html)
    out = []
    if SUP.search(html):
        out.append(("superscript", "citations are hyperlinks on the words naming the source, never <sup>"))
    for w in weak_anchor_texts(html):
        out.append(("weak-link", f"link text '{w}' names no source: put the link on the words naming the source"))
    if BARE_URL.search(ANCHOR.sub(" ", html)):
        out.append(("bare-url", "bare URL text: wrap it in a link on the source-naming words"))
    tag = TAG_CODE.search(ANCHOR.sub(" ", html))
    if tag:
        out.append(("tag-code", f"bare tag code {tag.group(0)} points nowhere"))
    if TIMESTAMP.search(text):
        out.append(("timestamp", "timestamps appear nowhere on the page"))
    if SECTION_REF.search(text):
        out.append(("section-ref", "no § section references: headings carry no numbers"))
    if NUMBERED_HEADING.search(html):
        out.append(("numbered-heading", "headings carry no hardcoded numbers"))
    if re.search(r"<h[1-6][^>]*>\s*machinery\b", html, re.I):
        out.append(("machinery", "no 'Machinery' heading: name the section for what it explains"))
    m = VERIFY_NARRATION.search(text)
    if m:
        out.append(("verify-narration", f"'{m.group(0)}' narrates verification: state the fact, cite it"))
    if VERDICT_LABEL.search(html):
        out.append(("verdict-label", "no bold verdict labels: fold the correction into the sentence"))
    if CORRECTION_LEDGER.search(html):
        out.append(("correction-ledger", "no 'Corrections:' ledger: fold each correction where the fact appears"))
    m = TEACHER_VOICE.search(text)
    if m:
        out.append(("teacher-voice", f"'{m.group(0)}' is teacher-voice framing: explain directly"))
    return out


def _bar_type_panel():
    font_opts = "\n".join(f"\t\t\t\t\t\t<option>{f}</option>" for f in FONTS)
    return f"""\t\t\t\t<span class="sep" aria-hidden="true"></span>
\t\t\t\t<div class="type-panel">
\t\t\t\t\t<span class="aa" aria-hidden="true">Aa</span>
\t\t\t\t\t<select aria-label="Font" data-font-select>
{font_opts}
\t\t\t\t\t\t<option selected>Charter</option>
\t\t\t\t\t</select>
\t\t\t\t\t<select aria-label="Size" data-size-select>
\t\t\t\t\t\t<option>S</option>
\t\t\t\t\t\t<option selected>M</option>
\t\t\t\t\t\t<option>L</option>
\t\t\t\t\t\t<option>XL</option>
\t\t\t\t\t</select>
\t\t\t\t</div>"""


def render_bar(title, options, current="", base="", home=False,
               title_href="", topic_feed="", topic_base=""):
    """Stdlib-only A-bar builder shared by the lesson stamp, --refresh-bar and
    publish_teach.py: the one home of the bar markup and font/size rosters.

    Chapter state (default): topic name (a link when `title_href` is set), a
    chapter dropdown, then the text settings behind an "Aa" mark.
    Home state (`home=True`): a labelled Topic picker, a labelled Chapter
    picker, then the text settings. With `topic_feed` (a course index page) the
    Topic picker reads that site-level feed and navigates on change; without it
    (the site hub) the picker reads COURSE_INDEX and a topic change fills the
    Chapter picker from that topic's own feed.
    `options` are static (label, href) entries for the chapter dropdown; the
    chapter list is injected at runtime by shell.js from window.COURSE_INDEX,
    prefixed with `base` when hrefs need a depth fix; topic hrefs take
    `topic_base`.
    """
    opt_html = "\n".join(
        f'\t\t\t\t\t<option value="{href}">{label}</option>' for label, href in options
    )
    current_attr = f' data-current="{current}"' if current else ""
    base_attr = f' data-base="{base}"' if base else ""
    if home:
        feed_attr = f' data-feed="{topic_feed}"' if topic_feed else ""
        topic_base_attr = f' data-base="{topic_base}"' if topic_base else ""
        topic_hint = "" if current else ' data-placeholder="Select a topic"'
        follows = "" if topic_feed else " data-follows-topic"
        head = (
            '<header class="A-bar" data-state="home">\n\t\t\t<div class="row">\n'
            '\t\t\t\t<label class="grp"><span class="lbl">Topic</span>'
            f'<select aria-label="Topic" data-topic{current_attr}{feed_attr}{topic_base_attr}{topic_hint}></select></label>\n'
            '\t\t\t\t<label class="grp"><span class="lbl">Chapter</span>'
            f'<select aria-label="Chapter" data-index data-placeholder="Select a chapter"{follows}{base_attr}>\n{opt_html}\n\t\t\t\t</select></label>\n'
        )
    else:
        label = f'<a href="{title_href}">{title}</a>' if title_href else title
        head = (
            '<header class="A-bar">\n\t\t\t<div class="row">\n'
            f'\t\t\t\t<span class="title">{label}</span>\n'
            f'\t\t\t\t<select aria-label="Chapter" data-index{current_attr}{base_attr}>\n{opt_html}\n\t\t\t\t</select>\n'
        )
    return head + _bar_type_panel() + "\n\t\t\t</div>\n\t\t</header>"


def bar_scripts(prefix):
    """Both script tags the A-bar needs, at the given path prefix (e.g.
    '../assets/', 'assets/'). Returned joined so callers append once."""
    return (
        f'\t\t<script src="{prefix}course-index.js"></script>\n'
        f'\t\t<script src="{prefix}shell.js"></script>'
    )

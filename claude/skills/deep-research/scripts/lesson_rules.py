"""Shared regexes and citation-repeat check for check_lesson.py and stamp_lesson.py.

Both scripts enforce the same lesson-page rules at two different points
(pre-stamp YAML text vs. post-stamp rendered HTML) — this module is the one
place those rules live, so the two never drift out of sync.
"""

import re

VERDICT = re.compile(
    r"\b(confirmed|corrected|partially correct|wrong|unfindable|unverified|allegation)\b",
    re.I,
)
TAG_CODE = re.compile(r"\[[A-Z]{1,3}\d+[a-z]?\]")
BARE_URL = re.compile(r"https?://\S+")
TIMESTAMP = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
SECTION_REF = re.compile(
    r"(?:§|\bsections?\b)\s*(\d+(?:\s*(?:,|and|&|through)\s*\d+)*)", re.I
)
YOUTUBE = re.compile(r"youtube\.com|youtu\.be", re.I)
ANCHOR = re.compile(r"<a\b.*?</a>", re.S | re.I)
HREF = re.compile(r'href="([^"]+)"')
SUP_WRAP = re.compile(r"<sup>\s*$")


FONTS = (
    "Literata", "Source Serif 4", "Newsreader", "Crimson Pro", "EB Garamond",
    "Merriweather", "Lora", "Libre Baskerville", "Atkinson Hyperlegible",
    "Inter", "IBM Plex Sans",
)


def render_bar(title, options, current="", base=""):
    """Stdlib-only A-bar builder shared by stamp_lesson.py's --refresh-bar
    mode (reference/index pages) and publish_teach.py (hub page), so the
    bar markup and font/size rosters exist in exactly one place outside the
    lesson stencil (which renders its own copy of this same shape).
    `options` is a list of (label, href) for the static utility entries;
    the chapter/course list is injected at runtime by shell.js from
    window.COURSE_INDEX, prefixed with `base` when hrefs need a depth fix.
    """
    opt_html = "\n".join(f'\t\t\t\t\t<option value="{href}">{label}</option>' for label, href in options)
    current_attr = f' data-current="{current}"' if current else ""
    base_attr = f' data-base="{base}"' if base else ""
    font_opts = "\n".join(f"\t\t\t\t\t\t<option>{f}</option>" for f in FONTS)
    return f"""<header class="A-bar">
\t\t\t<div class="row">
\t\t\t\t<span class="title">{title}</span>
\t\t\t\t<select aria-label="Chapter index" data-index{current_attr}{base_attr}>
{opt_html}
\t\t\t\t</select>
\t\t\t\t<div class="type-panel">
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
\t\t\t\t</div>
\t\t\t</div>
\t\t</header>"""


def bar_scripts(prefix):
    """Both script tags the A-bar needs, at the given path prefix (e.g.
    '../assets/', 'assets/'). Returned joined so callers append once."""
    return (
        f'\t\t<script src="{prefix}course-index.js"></script>\n'
        f'\t\t<script src="{prefix}shell.js"></script>'
    )


def find_unsuperscripted_repeats(*texts):
    """Walk anchors across all `texts` (a shared "seen" set, so a citation
    repeated across e.g. narrative+machinery is still caught); return a list
    of (target_url, matched_text) for every repeat citation not preceded by
    an open `<sup>`.
    """
    seen = set()
    violations = []
    for text in texts:
        for m in ANCHOR.finditer(text):
            hrefs = HREF.findall(m.group(0))
            if not hrefs or not hrefs[0].startswith(("http://", "https://")):
                continue
            target = hrefs[0].split("#")[0]
            if target in seen:
                preceding = text[: m.start()]
                if not SUP_WRAP.search(preceding):
                    violations.append((target, m.group(0)))
            else:
                seen.add(target)
    return violations

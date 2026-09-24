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
ANCHOR = re.compile(r"<a\b.*?</a>", re.S | re.I)
HREF = re.compile(r'href="([^"]+)"')
SUP_WRAP = re.compile(r"<sup>\s*$")


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

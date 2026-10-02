import argparse
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))
LESSONS = os.path.join(BASE, "index-home", "lessons")

ap = argparse.ArgumentParser()
ap.add_argument("--check-dir", default=os.path.dirname(BASE))
args = ap.parse_args()
sys.path.insert(0, args.check_dir)
from check_lesson import check, FOOTER_RE

HREF = re.compile(r'href="([^"]+)"')


def footer_hrefs(path):
    html = open(path, encoding="utf-8", errors="replace").read()
    m = FOOTER_RE.search(html)
    return HREF.findall(m.group(1)) if m else None


fails = []


def expect_clean(label, path):
    issues = check(path)
    if issues:
        fails.append(f"{label} expected [] got {issues}")
    return issues


def expect_issues(label, path, *fragments):
    issues = check(path)
    joined = " | ".join(issues).lower()
    for fragment in fragments:
        if fragment.lower() not in joined:
            fails.append(f"{label} expected an issue naming '{fragment}', got {issues}")
    return issues


p = expect_clean("pass.html", os.path.join(LESSONS, "pass.html"))
rp = expect_clean("pass-real-footer.html", os.path.join(LESSONS, "pass-real-footer.html"))
hi = expect_clean("index-home/index.html", os.path.join(BASE, "index-home", "index.html"))
hu = expect_clean("hub-home/index.html", os.path.join(BASE, "hub-home", "index.html"))
rg = expect_clean(
    "index-home/reference/glossary.html",
    os.path.join(BASE, "index-home", "reference", "glossary.html"),
)
rc = expect_clean(
    "index-home/reference/cast-map.html",
    os.path.join(BASE, "index-home", "reference", "cast-map.html"),
)

o = expect_issues(
    "fail-old.html",
    os.path.join(LESSONS, "fail-old.html"),
    "chapter N of M",
    "surtitle",
    "kicker",
    "superscript",
    "numbered-heading",
    "verify-narration",
    "correction-ledger",
    "a-bar",
    "sources/references",
)
rn = expect_issues(
    "fail-footer-nonav.html",
    os.path.join(LESSONS, "fail-footer-nonav.html"),
    "footer holds a nav link",
    "glossary",
)

ph = footer_hrefs(os.path.join(LESSONS, "pass-real-footer.html"))
if ph is None:
    fails.append("pass-real-footer.html: footer parse yielded None (regex missed </footer>)")
elif "../../index.html" in ph or re.search(r"\.\./index\.html", " ".join(ph)):
    fails.append(
        f"pass-real-footer.html: footer should hold only previous/next links, got {ph}"
    )

nh = footer_hrefs(os.path.join(LESSONS, "fail-footer-nonav.html"))
if nh is None:
    fails.append("fail-footer-nonav.html: footer parse yielded None (regex missed </footer>)")
elif "../index.html" not in nh:
    fails.append(f"fail-footer-nonav.html: footer hrefs should carry the leaked nav link, got {nh}")

if fails:
    print("RED:")
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("GREEN: all fixtures behave per spec")
print("  pass issues:", p)
print("  fail-old issues:", o)
print("  pass-real-footer issues:", rp)
print("  fail-footer-nonav issues:", rn)
print("  index-home + hub-home + reference pages:", hi, hu, rg, rc)
print("  pass-real-footer hrefs:", ph)
print("  fail-footer-nonav hrefs:", nh)

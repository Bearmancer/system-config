import argparse
import os
import re
import sys

BASE = os.path.dirname(os.path.abspath(__file__))

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

p = check(os.path.join(BASE, "pass.html"))
if p:
    fails.append(f"pass.html expected [] got {p}")

o = check(os.path.join(BASE, "fail-old.html"))
low = " | ".join(o).lower()
if not ("home" in low and ("index.html" in low)):
    fails.append(f"fail-old.html expected missing-home issue, got {o}")
if not ("ch" in low and "back" in low or "chapter" in low and "index.html" in low):
    fails.append(f"fail-old.html expected missing-backlink issue, got {o}")

b = check(os.path.join(BASE, "fail-budget.html"))
blow = " | ".join(b).lower()
if not ("repeated" in blow and "../index.html" in blow):
    fails.append(f"fail-budget.html expected dup issue for ../index.html, got {b}")

rp = check(os.path.join(BASE, "pass-real-footer.html"))
if rp:
    fails.append(f"pass-real-footer.html expected [] got {rp}")

hi = check(os.path.join(BASE, "index-home", "index.html"))
if hi:
    fails.append(f"index-home/index.html expected [] got {hi}")

hu = check(os.path.join(BASE, "hub-home", "index.html"))
if hu:
    fails.append(f"hub-home/index.html expected [] got {hu}")

rn = check(os.path.join(BASE, "fail-footer-nonav.html"))
rnl = " | ".join(rn).lower()
if not ("home" in rnl and "index.html" in rnl):
    fails.append(f"fail-footer-nonav.html expected missing-home issue, got {rn}")
if not ("ch" in rnl and "back" in rnl or "chapter" in rnl and "index.html" in rnl):
    fails.append(f"fail-footer-nonav.html expected missing-backlink issue, got {rn}")


ph = footer_hrefs(os.path.join(BASE, "pass-real-footer.html"))
if ph is None:
    fails.append(
        "pass-real-footer.html: footer parse yielded None (regex missed </footer>)"
    )
elif "../../index.html" in ph or re.search(r"\.\./index\.html#ch\d+", " ".join(ph)):
    fails.append(
        f"pass-real-footer.html: footer should hold only previous/next links "
        f"(home + chapter-index backlink belong in top-nav), got {ph}"
    )

nh = footer_hrefs(os.path.join(BASE, "fail-footer-nonav.html"))
if nh is None:
    fails.append(
        "fail-footer-nonav.html: footer parse yielded None (regex missed </footer>)"
    )
elif "../../index.html" in nh or re.search(r"\.\./index\.html#ch\d+", " ".join(nh)):
    fails.append(
        f"fail-footer-nonav.html: footer hrefs should lack nav targets, got {nh}"
    )

if fails:
    print("RED:")
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("GREEN: all 7 fixtures behave per new spec")
print("  pass issues:", p)
print("  fail-old issues:", o)
print("  fail-budget issues:", b)
print("  pass-real-footer issues:", rp)
print("  fail-footer-nonav issues:", rn)
print("  pass-real-footer hrefs:", ph)
print("  fail-footer-nonav hrefs:", nh)

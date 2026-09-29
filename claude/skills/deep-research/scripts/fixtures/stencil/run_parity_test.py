#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml"]
# ///

import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
SCRIPTS = BASE.parents[1]
STAMP = SCRIPTS / "stamp_lesson.py"
PUBLISH = SCRIPTS / "publish_teach.py"

SHARED = r"(?i)-ch0*(\d+)"
FALLBACK = r"^(\d+)"

SCRIPT_LIB = STAMP.read_text(encoding="utf-8")
PUBLISH_TEXT = PUBLISH.read_text(encoding="utf-8")

fails = []

for label, text in (
    ("stamp_lesson.py", SCRIPT_LIB),
    ("publish_teach.py", PUBLISH_TEXT),
):
    if SHARED not in text:
        fails.append(
            f"{label}: shared row-id pattern {SHARED!r} missing (contract drift)"
        )
    if FALLBACK not in text:
        fails.append(f"{label}: fallback pattern {FALLBACK!r} missing (contract drift)")

sys.path.insert(0, str(SCRIPTS))
from stamp_lesson import row_id_from_filename

cases = {
    "07-ch13-1996.html": "ch13",
    "01-ch7-dresden-kgb-years.html": "ch7",
    "02-ch8-sobchak.html": "ch8",
    "12-ch18-conclusion.html": "ch18",
}
for name, expected in cases.items():
    got = row_id_from_filename(name)
    if got != expected:
        fails.append(f"{name}: stamp id {got!r} != expected {expected!r}")


def publisher_id(rel, fallback_num):
    fname = rel.split("/")[-1]
    m = re.search(SHARED, fname)
    if m:
        return f"ch{m.group(1)}"
    n = re.search(FALLBACK, fname)
    if n:
        return f"lesson-{n.group(1)}"
    return f"lesson-{fallback_num}"


for name, expected in cases.items():
    pub = publisher_id(f"lessons/{name}", 1)
    if pub != expected:
        fails.append(f"{name}: publisher id {pub!r} != stamp id {expected!r}")


legacy = "01-dresden-kgb-years.html"
if publisher_id(f"lessons/{legacy}", 1) != "lesson-01":
    fails.append(f"{legacy}: publisher fallback should be lesson-01")

if fails:
    for f in fails:
        print("FAIL " + f)
    print(f"\n{len(fails)} parity failures")
    sys.exit(1)
print("PARITY OK: stamp and publisher derive identical row ids for all fixtures")
print(f"  shared pattern: {SHARED}")
print(f"  fixtures: {', '.join(cases)}")

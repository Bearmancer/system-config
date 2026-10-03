#!/usr/bin/env python3

import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
SCRIPTS = BASE.parents[1]
STAMP = SCRIPTS / "stamp_lesson.py"
sys.path.insert(0, str(SCRIPTS))
from check_lesson import check

GOLDEN = (BASE / "golden-07-ch13-1996.yaml").read_text(encoding="utf-8")
WS = BASE / "ws"


def run_stamp(yaml_text, name, ws=WS):
    tmp = Path(tempfile.mkdtemp(prefix="stencil-", dir=str(BASE)))
    work = tmp / "ws"
    shutil.copytree(ws, work)
    shutil.copytree(SCRIPTS.parent / "assets", tmp / "assets", ignore=shutil.ignore_patterns("*.stencil.html"))
    lessons = work / "lessons"
    yaml_path = lessons / name
    yaml_path.write_text(yaml_text, encoding="utf-8")
    proc = subprocess.run(
        ["uv", "run", str(STAMP), str(yaml_path), "--lessons-dir", str(lessons)],
        capture_output=True,
        text=True,
    )
    target = lessons / name.replace(".yaml", ".html")
    return proc.returncode, (proc.stdout + proc.stderr), target, tmp


def expect_ok(name, yaml_text, fname):
    rc, out, target, tmp = run_stamp(yaml_text, fname)
    ok = rc == 0 and target.exists()
    gate = check(str(target)) if target.exists() else ["(no target)"]
    shutil.rmtree(tmp, ignore_errors=True)
    if not ok:
        return False, f"{name}: stamp rc={rc}\n{out[:400]}"
    if gate:
        return False, f"{name}: gate issues: {gate}"
    return True, f"{name}: stamp rc=0, gate OK"


def expect_fail(name, yaml_text, fname, tag):
    rc, out, target, tmp = run_stamp(yaml_text, fname)
    shutil.rmtree(tmp, ignore_errors=True)
    if rc == 0:
        return False, f"{name}: expected failure, stamp exited 0"
    if tag.lower() not in out.lower():
        return False, f"{name}: expected tag '{tag}' not in output:\n{out[:400]}"
    return True, f"{name}: failed as expected ({tag})"


def mutate(fn):
    return fn(GOLDEN)


cases = []


cases.append(expect_ok("golden", GOLDEN, "07-ch13-1996.yaml"))


cases.append(expect_fail("no-chapter-filename", GOLDEN, "07-1996.yaml", "filename"))


cases.append(
    expect_fail(
        "chapter-mismatch",
        GOLDEN.replace("chapter: 13", "chapter: 12"),
        "07-ch13-1996.yaml",
        "chapter mismatch",
    )
)


cases.append(
    expect_fail(
        "missing-title",
        re.sub(r"(?m)^title: .*\n", "", GOLDEN),
        "07-ch13-1996.yaml",
        "missing field: title",
    )
)


cases.append(
    expect_fail(
        "empty-sources",
        re.sub(r"(?s)sources:.*$", "sources: []\n", GOLDEN),
        "07-ch13-1996.yaml",
        "sources",
    )
)


cases.append(
    expect_fail(
        "superscript-citation",
        GOLDEN.replace(
            "<p>Loans-for-shares",
            '<p>Total<sup><a href="https://www.rferl.org/example">2</a></sup>.</p><p>Loans-for-shares',
        ),
        "07-ch13-1996.yaml",
        "superscript in body",
    )
)


cases.append(
    expect_fail(
        "weak-link-text",
        GOLDEN.replace("official record", "record").replace(
            '<a href="https://www.rferl.org/example">record</a>',
            '<a href="https://www.rferl.org/example">here</a>',
        ),
        "07-ch13-1996.yaml",
        "weak-link in body",
    )
)


cases.append(
    expect_fail(
        "bare-url",
        GOLDEN.replace(
            "Turnout is given only",
            "See https://example.com/raw for the tally. Turnout is given only",
        ),
        "07-ch13-1996.yaml",
        "bare-url in body",
    )
)


cases.append(
    expect_fail(
        "section-ref",
        GOLDEN.replace(
            "<p>Loans-for-shares", "<p>See §7 for details.</p><p>Loans-for-shares"
        ),
        "07-ch13-1996.yaml",
        "section-ref in body",
    )
)


cases.append(
    expect_fail(
        "stray-timestamp",
        GOLDEN.replace('"We won."', '"We won at 1:23."'),
        "07-ch13-1996.yaml",
        "timestamp in body",
    )
)


cases.append(
    expect_fail(
        "numbered-heading",
        GOLDEN.replace("<h2>The Vote</h2>", "<h2>1. The Vote</h2>"),
        "07-ch13-1996.yaml",
        "numbered-heading in body",
    )
)


cases.append(
    expect_fail(
        "verification-narration",
        GOLDEN.replace("according to the", "confirmed against the"),
        "07-ch13-1996.yaml",
        "verify-narration in body",
    )
)


cases.append(
    expect_fail(
        "correction-ledger",
        GOLDEN.replace("<p>Loans-for-shares", "<p>Corrections: none.</p><p>Loans-for-shares"),
        "07-ch13-1996.yaml",
        "correction-ledger in body",
    )
)


cases.append(
    expect_fail(
        "open-threads",
        GOLDEN.replace(
            "<p>Loans-for-shares", "<p>Open threads remain.</p><p>Loans-for-shares"
        ),
        "07-ch13-1996.yaml",
        "banned phrase",
    )
)


cases.append(
    expect_fail(
        "summary-on-a-short-chapter",
        GOLDEN + "\nsummary: A short version.\n",
        "07-ch13-1996.yaml",
        "summary: only a chapter",
    )
)


for legacy, extra in (
    ("kicker", 'kicker: "Series"'),
    ("chapters_total", "chapters_total: 18"),
    ("lead", 'lead: "A lead."'),
    ("cast", "cast: []"),
    ("machinery", 'machinery: "<p>x</p>"'),
):
    cases.append(
        expect_fail(
            f"retired-{legacy}",
            GOLDEN + f"\n{extra}\n",
            "07-ch13-1996.yaml",
            f"retired field: {legacy}",
        )
    )


cases.append(
    expect_fail(
        "diagram-line-through-a-box",
        GOLDEN.replace(
            "  edges:\n",
            "  edges:\n    - {from: yeltsin, to: voters, label: skips, directed: true}\n",
        ).replace(
            "    - - {id: oligarchs",
            "    - - {id: mid, name: Middle}\n    - - {id: oligarchs",
        ),
        "07-ch13-1996.yaml",
        "diagram:",
    )
)


def check_stamped_golden_shape():
    rc, out, target, tmp = run_stamp(GOLDEN, "07-ch13-1996.yaml")
    html = target.read_text(encoding="utf-8") if target.exists() else ""
    feed = (target.parent.parent / "assets" / "course-index.js").read_text(encoding="utf-8") if target.exists() else ""
    shutil.rmtree(tmp, ignore_errors=True)
    bad = []
    if '<span class="title"><a href="../index.html">Test Course</a></span>' not in html:
        bad.append("topic name link missing from the bar")
    for banned in ("surtitle", "kicker", "Chapter 13 of", "<h2>Summary</h2>", "<h2>2. Cast", "Machinery"):
        if banned in html:
            bad.append(f"page carries '{banned}'")
    if "<h1>1996</h1>" not in html:
        bad.append("H1 is not the chapter name alone")
    if '"label": "7 \\u00b7 1996"' not in feed:
        bad.append(f"index label not 'N · name': {feed[:200]}")
    if bad:
        return False, "stamped-shape: " + "; ".join(bad)
    return True, "stamped-shape: bar, header and 'N · name' index label per spec"


def with_diagrams(count):
    block = re.search(r"(?s)diagram:\n(.*?)\nbody:", GOLDEN).group(1)
    listed = "".join("  -\n" + "".join("  " + ln + "\n" for ln in block.splitlines()) for _ in range(count))
    return re.sub(r"(?s)diagram:\n.*?\nbody:", lambda _: "diagram:\n" + listed + "body:", GOLDEN)


cases.append(expect_ok("two-diagrams", with_diagrams(2), "07-ch13-1996.yaml"))
cases.append(expect_fail("three-diagrams", with_diagrams(3), "07-ch13-1996.yaml", "cap is 2"))


cases.append(check_stamped_golden_shape())


def check_refresh_bar_idempotent():
    tmp = Path(tempfile.mkdtemp(prefix="stencil-", dir=str(BASE)))
    work = tmp / "ws"
    shutil.copytree(WS, work)
    bar_issue = re.compile(r"^A-bar", re.I)
    (work / "index.html").write_text(
        "<!DOCTYPE html><html><head><title>Home</title></head><body><h1>Home</h1></body></html>",
        encoding="utf-8",
    )
    for _ in range(2):
        proc = subprocess.run(
            ["uv", "run", str(STAMP), "--refresh-bar", str(work)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            shutil.rmtree(tmp, ignore_errors=True)
            return False, f"refresh-bar: rc={proc.returncode}\n{proc.stdout + proc.stderr}"
    refs = sorted((work / "reference").glob("*.html")) + [work / "index.html"]
    bad = []
    for ref in refs:
        html = ref.read_text(encoding="utf-8")
        if len(re.findall(r'<header[^>]*class="[^"]*A-bar', html)) != 1:
            bad.append(f"{ref.name}: not exactly one A-bar after 2 refreshes")
        if ref.name == "index.html" and 'data-state="home"' not in html:
            bad.append("index.html: refreshed bar is not the home state")
        issues = [i for i in check(str(ref)) if bar_issue.match(i)]
        if issues:
            bad.append(f"{ref.name}: {issues}")
    shutil.rmtree(tmp, ignore_errors=True)
    if bad:
        return False, "refresh-bar: " + "; ".join(bad)
    return True, f"refresh-bar: idempotent, bar OK on {[r.name for r in refs]}"


cases.append(check_refresh_bar_idempotent())

failed = 0
for ok, msg in cases:
    print(("PASS " if ok else "FAIL ") + msg)
    if not ok:
        failed += 1
print(f"\n{len(cases) - failed}/{len(cases)} cases pass")
sys.exit(1 if failed else 0)

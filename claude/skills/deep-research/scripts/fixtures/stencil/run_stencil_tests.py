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
        "no-verdicts",
        GOLDEN.replace("confirmed", "checked").replace("unverified", "unknown"),
        "07-ch13-1996.yaml",
        "verdicts",
    )
)


cases.append(
    expect_fail(
        "triple-link",
        GOLDEN.replace(
            "The June runoff result is",
            'See <a href="https://www.rferl.org/example">a</a> and <a href="https://www.rferl.org/example">b</a>; the June runoff result is',
        ),
        "07-ch13-1996.yaml",
        "repeat citation",
    )
)


cases.append(
    expect_fail(
        "bare-url",
        GOLDEN.replace(
            "The turnout figure stays",
            "See https://example.com/raw for the tally. The turnout figure stays",
        ),
        "07-ch13-1996.yaml",
        "bare URL",
    )
)


cases.append(
    expect_fail(
        "section-ref",
        GOLDEN.replace(
            "<p>Loans-for-shares", "<p>See §7 for details.</p><p>Loans-for-shares"
        ),
        "07-ch13-1996.yaml",
        "section ref",
    )
)


cases.append(
    expect_fail(
        "stray-timestamp",
        GOLDEN.replace('"We won."', '"We won at 1:23."'),
        "07-ch13-1996.yaml",
        "timestamp",
    )
)


cases.append(
    expect_fail(
        "orphan-cast",
        GOLDEN.replace("ref: 8", "ref: 99"),
        "07-ch13-1996.yaml",
        "cast ref",
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


SVG = '<svg viewBox="0 0 10 10"><rect width="10" height="10"/></svg>'
cases.append(
    expect_ok(
        "subgraph-passthrough", GOLDEN + f"\nsubgraph: {SVG}\n", "07-ch13-1996.yaml"
    )
)
cases.append(
    expect_fail(
        "subgraph-external",
        GOLDEN + '\nsubgraph: <svg><image href="https://x/y.png"/></svg>\n',
        "07-ch13-1996.yaml",
        "subgraph",
    )
)

def check_refresh_bar_idempotent():
    tmp = Path(tempfile.mkdtemp(prefix="stencil-", dir=str(BASE)))
    work = tmp / "ws"
    shutil.copytree(WS, work)
    bar_issue = re.compile(r"^A-bar", re.I)
    for _ in range(2):
        proc = subprocess.run(
            [sys.executable, str(STAMP), "--refresh-bar", str(work)],
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            shutil.rmtree(tmp, ignore_errors=True)
            return False, f"refresh-bar: rc={proc.returncode}\n{proc.stdout + proc.stderr}"
    refs = sorted((work / "reference").glob("*.html"))
    bad = []
    for ref in refs:
        html = ref.read_text(encoding="utf-8")
        if len(re.findall(r'<header[^>]*class="[^"]*A-bar', html)) != 1:
            bad.append(f"{ref.name}: not exactly one A-bar after 2 refreshes")
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

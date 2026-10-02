#!/usr/bin/env python3
"""Verify published lesson pages against the live site in one command.

Downloads a workspace's lessons plus the files their relative links resolve
against (assets, reference pages, course index), mirrored into a temp tree so
check_lesson.py's dangling-link and asset checks resolve exactly as they do
locally. Then gates every downloaded lesson, asserts no `.md` hrefs survived
publishing (the publisher flattens them), and byte-compares each local asset
against its live copy.

Usage:
    python scripts/verify_live.py <workspace-dir> <site-workspace-url>
Example:
    python scripts/verify_live.py ~/Dev/bearmancer.github.io/historians-on-trump https://bearmancer.github.io/historians-on-trump

Exit 0 only when every lesson gates OK, no `.md` hrefs remain live, and all
assets match. Anything else exits 1 with the failing paths named.
"""

import re
import shutil
import sys
import tempfile
import urllib.request
import urllib.error
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from check_lesson import check

MD_HREF = re.compile(r'href="[^"]*\.md"')


def fetch(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "deep-research-verify/1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, resp.read()


def normalize_eol(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def get(url, timeout=20):
    try:
        return fetch(url, timeout)
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception:
        return 0, b""


def main():
    if len(sys.argv) != 3:
        print(
            "usage: verify_live.py <workspace-dir> <site-workspace-url>",
            file=sys.stderr,
        )
        sys.exit(2)
    ws = Path(sys.argv[1])
    site = sys.argv[2].rstrip("/")
    lessons = sorted((ws / "lessons").glob("*.html"))
    if not lessons:
        print(f"no lessons in {ws}/lessons", file=sys.stderr)
        sys.exit(2)

    tmp = Path(tempfile.mkdtemp(prefix="live-verify-"))
    (tmp / "lessons").mkdir()
    (tmp / "assets").mkdir()
    (tmp / "reference").mkdir()
    failures = []

    def pull(rel, required=True):
        code, body = get(f"{site}/{rel}")
        if code != 200:
            code2, body2 = get(f"{site}/{rel}")
            code, body = (code2, body2) if code2 == 200 else (code, body)
        if code != 200:
            if required:
                failures.append(f"{rel}: HTTP {code}")
            return None
        target = tmp / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(body)
        return target

    for lesson in lessons:
        pull(f"lessons/{lesson.name}")
    pull("index.html")
    for asset in sorted((ws / "assets").glob("*")):
        if asset.is_file():
            local = asset.read_bytes()
            target = pull(f"assets/{asset.name}", required=False)
            if target is not None and normalize_eol(
                target.read_bytes()
            ) != normalize_eol(local):
                failures.append(f"assets/{asset.name}: live bytes differ from local")
    for ref in sorted((ws / "reference").glob("*.html")):
        pull(f"reference/{ref.name}", required=False)

    for lesson in lessons:
        target = tmp / "lessons" / lesson.name
        if not target.exists():
            continue
        issues = check(str(target))
        print(("OK " if not issues else "PROBLEMS ") + f"{site}/lessons/{lesson.name}")
        for issue in issues:
            print("   - " + issue)
        if issues:
            failures.append(f"lessons/{lesson.name}: gate issues")

    md_left = []
    for html in sorted(tmp.rglob("*.html")):
        text = html.read_text(encoding="utf-8", errors="replace")
        if MD_HREF.search(text):
            md_left.append(str(html.relative_to(tmp)))
    if md_left:
        failures.append(f".md hrefs live (flatten missing): {md_left}")

    print(
        f"\n{len(lessons) - len([f for f in failures if f.startswith('lessons/')])}/{len(lessons)} live lessons gate OK"
    )
    shutil.rmtree(tmp, ignore_errors=True)
    if failures:
        print("FAIL:")
        for failure in failures:
            print("  - " + failure)
        sys.exit(1)
    print("LIVE VERIFIED")


if __name__ == "__main__":
    main()

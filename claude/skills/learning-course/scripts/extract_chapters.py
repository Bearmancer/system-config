#!/usr/bin/env python3

import argparse
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile


def _load_slice_module():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slice_chapter.py")
    spec = importlib.util.spec_from_file_location("slice_chapter", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sc = _load_slice_module()

LEGACY_CACHES = (
    os.path.join(tempfile.gettempdir(), "opencode", "learning-course"),
    os.path.join(tempfile.gettempdir(), "opencode", "yt-chapter-course"),
)

CLOCK_PREFIX = re.compile(r"^\s*(?:\d{1,2}:\d{2}(?::\d{2})?|\d+)\s*[-–—.:)]\s*")
CHAPTER_PREFIX = re.compile(r"^\s*chapter\s*\d+\s*[-–—.:)]?\s*", re.I)


def slugify(title):
    s = CLOCK_PREFIX.sub("", title or "")
    s = CHAPTER_PREFIX.sub("", s)
    s = s.replace("'", "").replace("\u2019", "").lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "chapter"


def stamp(seconds):
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}h{m:02d}m{sec:02d}s" if h else f"{m}m{sec:02d}s"


def default_cache_root():
    home = os.path.expanduser("~")
    return os.path.join(home, ".omo", "cache", "learning-course")


def resolve_id(source):
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", source):
        return source
    r = sc.run(["yt-dlp", "--no-warnings", "--skip-download", "--print", "%(id)s", source])
    if r.returncode != 0:
        print("yt-dlp could not resolve the video:\n" + r.stderr)
        sys.exit(1)
    return r.stdout.strip().splitlines()[-1].strip()


def adopt_legacy(vid, dest):
    if os.path.exists(os.path.join(dest, "info.json")) and os.path.exists(
        os.path.join(dest, "subs.en.vtt")
    ):
        return False
    for root in LEGACY_CACHES:
        src = os.path.join(root, vid)
        if not os.path.isdir(src):
            continue
        os.makedirs(dest, exist_ok=True)
        moved = []
        for name in ("info.json", "subs.en.vtt"):
            if os.path.exists(os.path.join(src, name)):
                shutil.copy2(os.path.join(src, name), os.path.join(dest, name))
                moved.append(name)
        if moved:
            print(f"adopted from old cache {src}: {', '.join(moved)}")
            return True
    return False


def fetch(source, dest, force):
    have = os.path.exists(os.path.join(dest, "info.json")) and os.path.exists(
        os.path.join(dest, "subs.en.vtt")
    )
    if have and not force:
        print("cache: warm (" + dest + ")")
        return
    fetch_script = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "fetch_video.py"
    )
    args = [sys.executable, fetch_script, source, "--outdir", dest]
    if force:
        args.append("--force")
    r = sc.run(args)
    sys.stdout.write(r.stdout)
    if r.returncode != 0:
        sys.stderr.write(r.stderr)
        print("fetch failed")
        sys.exit(1)


def load_chapters(dest):
    with open(os.path.join(dest, "info.json"), encoding="utf-8") as fh:
        info = json.load(fh)
    chapters = info.get("chapters") or []
    if not chapters:
        print(
            "This video has NO chapter markers - nothing to derive. Ask the user how to segment."
        )
        sys.exit(2)
    return info, chapters


def select(chapters, spec):
    if not spec or spec.lower() == "all":
        return list(range(len(chapters)))
    picked = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
        if m:
            lo, hi = sorted((int(m.group(1)), int(m.group(2))))
            picked += [i for i in range(lo - 1, hi) if 0 <= i < len(chapters)]
            continue
        if part.isdigit():
            i = int(part) - 1
            if 0 <= i < len(chapters):
                picked.append(i)
            continue
        hits = [
            i
            for i, ch in enumerate(chapters)
            if part.lower() in (ch.get("title") or "").lower()
        ]
        picked += hits
    return sorted(set(picked))


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("source")
    ap.add_argument("--out")
    ap.add_argument("--cache", default=default_cache_root())
    ap.add_argument("--chapters", default="all")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--title", action="store_true")
    a = ap.parse_args()

    vid = resolve_id(a.source)
    dest = os.path.join(a.cache, vid)
    os.makedirs(dest, exist_ok=True)
    adopt_legacy(vid, dest)
    fetch(a.source, dest, a.force)
    info, chapters = load_chapters(dest)

    if a.list or a.dry_run:
        print(f"{info.get('title', '')}  [{vid}]  {len(chapters)} chapters")
        for i, ch in enumerate(chapters, 1):
            print(
                f"  {i:>2}. {sc.fmt_clock(ch['start_time'])}-{sc.fmt_clock(ch['end_time'])}  "
                f"{int(ch['start_time'])}-{int(ch['end_time'])} s  {ch.get('title', '')}"
            )
        if a.list:
            return

    idx = select(chapters, a.chapters)
    if not idx:
        print(f"no chapter matched {a.chapters!r}; use --list to see the table")
        sys.exit(1)

    outdir = a.out or os.path.join(dest, "transcripts")
    os.makedirs(outdir, exist_ok=True)
    cues = sc.collapse(sc.load_cues(os.path.join(dest, "subs.en.vtt")))

    for i in idx:
        ch = chapters[i]
        start, end = int(ch["start_time"]), int(ch["end_time"])
        slug = slugify(ch.get("title") or f"chapter-{i + 1}")
        target = os.path.join(outdir, f"{slug}-{stamp(start)}-{stamp(end)}.md")

        before, after, sel = sc.boundary_split(cues, start, end)

        head_title = ch.get("title") if a.title else slug
        header, body = sc.render_slice(head_title, start, end, before, after, sel)
        if not a.dry_run:
            with open(target, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(header + body)

        print(
            f"ch{i + 1:>2} {slug}: {len(sel)} cues | first {sc.fmt_clock(sel[0][0]) if sel else '-'} | "
            f"last {sc.fmt_clock(sel[-1][0]) if sel else '-'} | "
            f"before: {sc.fmt_clock(before[-1][0]) if before else '-'} "
            f"('{(before[-1][1] if before else '')[:50]}') | "
            f"after: {sc.fmt_clock(after[0][0]) if after else '-'} "
            f"('{(after[0][1] if after else '')[:50]}')"
        )
        print("  " + ("would write: " if a.dry_run else "written: ") + target)


if __name__ == "__main__":
    main()

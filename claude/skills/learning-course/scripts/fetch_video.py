#!/usr/bin/env python3

import importlib.util
import json
import os
import sys

MARKERS = ["@@TITLE@@", "@@DURATION@@", "@@CHAPTERS@@", "@@DESCRIPTION@@", "@@URL@@"]


def _load_slice_module():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slice_chapter.py")
    spec = importlib.util.spec_from_file_location("slice_chapter", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sc = _load_slice_module()
run = sc.run
fmt_time = sc.fmt_clock


def report(info, info_path, vtt, chapters):
    title = info.get("title", "")
    print("title:    " + title)
    print("duration: " + fmt_time(info["duration"]) + f" ({info['duration']} s)")
    print("info:     " + info_path)
    print("captions: " + vtt)
    if chapters:
        print(f"chapters: {len(chapters)}")
        for i, ch in enumerate(chapters):
            print(
                f"  {i + 1:>2}. {fmt_time(ch['start_time'])}-{fmt_time(ch['end_time'])}  "
                f"{int(ch['start_time'])}-{int(ch['end_time'])} s  {ch['title']}"
            )
        print(
            "\nNext: extract whole chapters in one command (ranges come from this metadata, nothing to compute):"
        )
        print(
            f'  python extract_chapters.py "{info.get("url") or info.get("id")}" '
            f"--out <workspace>/reference/transcripts --chapters all"
        )
    else:
        print(
            "chapters: NONE - this video has no chapter markers. "
            "Tell the user; ask how to segment."
        )


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0 if len(sys.argv) > 1 else 1)

    url = sys.argv[1]
    outdir = None
    force = "--force" in sys.argv
    if "--outdir" in sys.argv:
        outdir = sys.argv[sys.argv.index("--outdir") + 1]

    r = run(["yt-dlp", "--no-warnings", "--skip-download", "--print", "%(id)s", url])
    if r.returncode != 0:
        print("yt-dlp failed to resolve the video:\n" + r.stderr)
        sys.exit(1)
    vid = r.stdout.strip().splitlines()[-1].strip()

    if outdir is None:
        outdir = os.path.join(
            os.path.expanduser("~"), ".omo", "cache", "learning-course", vid
        )
    os.makedirs(outdir, exist_ok=True)

    info_path = os.path.join(outdir, "info.json")
    vtt = os.path.join(outdir, "subs.en.vtt")
    if os.path.exists(info_path) and os.path.exists(vtt) and not force:
        try:
            with open(info_path, encoding="utf-8") as fh:
                cached = json.load(fh)
        except (OSError, json.JSONDecodeError):
            cached = None
        if cached:
            print(f"cache: warm ({outdir}) - nothing fetched; use --force to refresh")
            report(cached, info_path, vtt, cached.get("chapters") or [])
            return

    args = ["yt-dlp", "--no-warnings", "--skip-download"]
    args += ["--print", MARKERS[0], "--print", "%(title)s"]
    args += ["--print", MARKERS[1], "--print", "%(duration)s"]
    args += ["--print", MARKERS[2], "--print", "%(chapters)j"]
    args += ["--print", MARKERS[3], "--print", "%(description)s"]
    args += ["--print", MARKERS[4], "--print", "%(webpage_url)s"]
    args += [url]

    r = run(args)
    if r.returncode != 0:
        print("yt-dlp metadata call failed:\n" + r.stderr)
        sys.exit(1)

    text = r.stdout
    sections = {}
    for i, label in enumerate(MARKERS):
        start = text.find(label)
        if start == -1:
            sections[label] = ""
            continue
        start += len(label)
        end = len(text)
        for other in MARKERS[i + 1 :]:
            p = text.find(other, start)
            if p != -1:
                end = min(end, p)
                break
        sections[label] = text[start:end].strip()

    title = sections["@@TITLE@@"]
    duration = (
        sections["@@DURATION@@"].splitlines()[0].strip()
        if sections["@@DURATION@@"]
        else ""
    )
    chapters_raw = (
        sections["@@CHAPTERS@@"].splitlines()[0].strip()
        if sections["@@CHAPTERS@@"]
        else ""
    )
    description = sections["@@DESCRIPTION@@"]
    page_url = (
        sections["@@URL@@"].splitlines()[0].strip() if sections["@@URL@@"] else url
    )

    chapters = []
    if chapters_raw and chapters_raw not in ("NA", "None"):
        try:
            chapters = json.loads(chapters_raw)
        except json.JSONDecodeError:
            print("Warning: could not parse chapters JSON; continuing without it.")

    info = {
        "id": vid,
        "title": title,
        "duration": int(duration) if duration.isdigit() else duration,
        "chapters": chapters,
        "description": description,
        "url": page_url,
        "source": "yt-dlp metadata",
    }
    info_path = os.path.join(outdir, "info.json")
    with open(info_path, "w", encoding="utf-8") as fh:
        json.dump(info, fh, ensure_ascii=False, indent=2)

    args = [
        "yt-dlp",
        "--no-warnings",
        "--skip-download",
        "--write-auto-subs",
        "--write-subs",
        "--sub-langs",
        "en",
        "--sub-format",
        "vtt",
        "-o",
        os.path.join(outdir, "subs.%(ext)s"),
        url,
    ]
    r = run(args)
    vtt = os.path.join(outdir, "subs.en.vtt")
    if not os.path.exists(vtt):
        print("Warning: captions not found at " + vtt)
        print(r.stdout[-2000:])
        print(r.stderr[-2000:])
    else:
        print("captions: " + vtt)

    report(info, info_path, vtt, chapters)


if __name__ == "__main__":
    main()

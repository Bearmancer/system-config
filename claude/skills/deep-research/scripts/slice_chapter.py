#!/usr/bin/env python3

import os
import re
import subprocess
import sys

TS = re.compile(r"(\d+):(\d+):(\d+)\.(\d+)")
TAG = re.compile(r"<[^>]*>")


def run(args):
    return subprocess.run(
        args, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )


def parse_time(s):
    s = s.strip()
    if ":" in s:
        parts = [int(p) for p in s.split(":")]
        while len(parts) < 3:
            parts.insert(0, 0)
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    return int(s)


def fmt_clock(t):
    t = int(t or 0)
    h, rem = divmod(t, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def load_cues(vtt_path):
    with open(vtt_path, encoding="utf-8") as fh:
        raw = fh.read()
    cues = []
    for block in raw.split("\n\n"):
        lines = block.strip().splitlines()
        if not lines:
            continue
        m = TS.match(lines[0])
        if not m:
            continue
        t = (
            int(m.group(1)) * 3600
            + int(m.group(2)) * 60
            + int(m.group(3))
            + int(m.group(4)) / 1000
        )
        text = re.sub(r"\s+", " ", TAG.sub("", " ".join(lines[1:]))).strip()
        cues.append((t, text))
    return cues


def collapse(cues):
    out = []
    prev = []
    for t, text in cues:
        toks = text.split()
        if not toks:
            continue
        overlap = 0
        for j in range(min(len(toks), len(prev)), 0, -1):
            if prev[-j:] == toks[:j]:
                overlap = j
                break
        new = toks[overlap:]
        prev = toks
        if new:
            out.append((t, " ".join(new)))
    return out


def boundary_split(cues, start, end):
    before = [c for c in cues if c[0] < start]
    after = [c for c in cues if c[0] >= end]
    sel = [c for c in cues if start <= c[0] < end]
    return before, after, sel


def render_slice(head_title, start, end, before, after, sel):
    header = f"""# Transcript slice — {head_title}

- Range: **{fmt_clock(start)}-{fmt_clock(end)}** ({int(start)}-{int(end)} s), per the video's own chapter metadata.
- Source: YouTube auto-captions (en, VTT). Rolling-caption duplicates collapsed by word overlap; each `[mm:ss]` marks where that phrase first appears. Captions lag the visual cut by a few seconds.
- Boundary check: last preceding cue at {fmt_clock(before[-1][0]) if before else "?"} ("{before[-1][1] if before else "?"}"); first following cue at {fmt_clock(after[0][0]) if after else "?"} ("{after[0][1] if after else "?"}").
- Cue count in slice: {len(sel)}.

## Transcript

"""
    body = "\n".join(f"[{fmt_clock(t)}] {text}" for t, text in sel) + "\n"
    return header, body


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    vtt_path, outdir = sys.argv[1], sys.argv[2]
    specs = sys.argv[3:]
    os.makedirs(outdir, exist_ok=True)

    cues = collapse(load_cues(vtt_path))

    for spec in specs:
        title = None
        if "|" in spec:
            spec, title = spec.split("|", 1)
        try:
            rng, slug = spec.rsplit(":", 1)
            start_s, end_s = rng.split("-", 1)
        except ValueError:
            print(f"Error: invalid spec format '{spec}'", file=sys.stderr)
            print(f"Expected format: start-end:slug[|title]", file=sys.stderr)
            sys.exit(1)
        start, end = parse_time(start_s), parse_time(end_s)

        before, after, sel = boundary_split(cues, start, end)

        head_title = title or slug
        header, body = render_slice(head_title, start, end, before, after, sel)
        dest = os.path.join(outdir, slug + ".md")
        with open(dest, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(header + body)

        print(
            f"{slug}: {len(sel)} cues | first {fmt_clock(sel[0][0]) if sel else '-'} | "
            f"last {fmt_clock(sel[-1][0]) if sel else '-'} | "
            f"before: {fmt_clock(before[-1][0]) if before else '-'} "
            f"('{(before[-1][1] if before else '')[:60]}') | "
            f"after: {fmt_clock(after[0][0]) if after else '-'} "
            f"('{(after[0][1] if after else '')[:60]}')"
        )
        print("  written: " + dest)


if __name__ == "__main__":
    main()

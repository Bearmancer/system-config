#!/usr/bin/env python3
"""Drop repeated lines from song lyrics, keeping the first occurrence of each.

Usage:
    python dedupe_lyrics.py song.txt      # or pipe text on stdin
Prints the unique lines (one per line) to stdout and a summary to stderr.

Lines count as duplicates when they match after normalisation, so a chorus
repeated with different punctuation, casing, Urdu vowel marks, Devanagari
nukta, Latin accents or a trailing "(x2)" is still caught. Section labels
such as [Chorus] or "Verse 2:" are dropped.
"""
import re
import sys
import unicodedata

# Arabic-script marks that differ between sources: harakat, tatweel, small marks.
_ARABIC_MARKS = re.compile("[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]")
_VARIANTS = str.maketrans({
    "\u064A": "\u06CC",  # Arabic yeh   -> Farsi yeh
    "\u0649": "\u06CC",  # alef maksura -> Farsi yeh
    "\u0643": "\u06A9",  # Arabic kaf   -> keheh
    "\u0647": "\u06C1",  # Arabic heh   -> heh goal
    "\u0629": "\u06C1",  # teh marbuta  -> heh goal
})
_NUKTA = "\u093C"  # Devanagari nukta (ज़ vs ज are often typed inconsistently)

_REPEAT_MARK = re.compile(
    r"[\(\[\{]?\s*(?:x\s*\d+|\d+\s*x|\u00d7\s*\d+|\d+\s*\u00d7|\d+\s*times|repeat(?:\s*x?\d+)?)"
    r"\s*[\)\]\}]?\s*$",
    re.I,
)
_HEADER = re.compile(
    r"^\s*[\[\(\{]?\s*(?:intro|verse|chorus|pre[- ]?chorus|bridge|outro|hook|refrain|"
    r"interlude|instrumental|mukhda|antara|sthayi|pallavi|anupallavi|charanam|repeat\s+\w+)"
    r"\s*\d*\s*[\]\)\}]?\s*:?\s*(?:x\s*\d+|\d+\s*x)?\s*$",
    re.I,
)


def key(line: str) -> str:
    """Comparison key: equal keys mean 'same line' for dedupe purposes."""
    s = unicodedata.normalize("NFD", unicodedata.normalize("NFKC", line))
    s = _ARABIC_MARKS.sub("", s).translate(_VARIANTS).replace(_NUKTA, "")
    s = "".join(c for c in s if not 0x300 <= ord(c) <= 0x36F)  # Latin accents only
    out = []
    for c in s.casefold():
        cat = unicodedata.category(c)
        if cat[0] in "PSZ" or c.isspace():
            out.append(" ")  # punctuation / hyphens / spaces all collapse
        elif cat in ("Cf", "Cc"):
            continue  # zero-width joiners etc.
        else:
            out.append(c)
    return " ".join("".join(out).split())


def dedupe(text: str):
    seen, kept, removed = set(), [], 0
    for raw in text.lstrip("\ufeff").splitlines():
        line = raw.strip()
        if not line or _HEADER.match(line):
            continue
        line = _REPEAT_MARK.sub("", line).strip()
        k = key(line)
        if not k:  # only punctuation / music symbols
            continue
        if k in seen:
            removed += 1
            continue
        seen.add(k)
        kept.append(line)
    return kept, removed


def main() -> None:
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8-sig") as f:
            text = f.read()
    else:
        sys.stdin.reconfigure(encoding="utf-8")
        text = sys.stdin.read()
    kept, removed = dedupe(text)
    sys.stdout.reconfigure(encoding="utf-8")
    print("\n".join(kept))
    print(f"kept {len(kept)}, removed {removed} duplicate line(s)", file=sys.stderr)


if __name__ == "__main__":
    main()

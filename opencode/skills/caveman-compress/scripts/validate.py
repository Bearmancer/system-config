#!/usr/bin/env python3
import re
from collections import Counter
from pathlib import Path

URL_REGEX = re.compile(r"https?://[^\s)]+")
FENCE_OPEN_REGEX = re.compile(r"^(\s{0,3})(`{3,}|~{3,})(.*)$")


FENCE_MARKER_LINE_REGEX = re.compile(r"^\s*(?:`{3,}|~{3,})[^`~]*$")


MAX_REPORTED_SPAN = 60
HEADING_REGEX = re.compile(r"^(#{1,6})\s+(.*)", re.MULTILINE)
BULLET_REGEX = re.compile(r"^\s*[-*+]\s+", re.MULTILINE)


LIST_ITEM_REGEX = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s")


PATH_REGEX = re.compile(
    r"(?:\./|\.\./|/|[A-Za-z]:\\)[\w\-/\\\.]+|[\w\-\.]+[/\\][\w\-/\\\.]+"
)


DEFINITE_PATH_REGEX = re.compile(
    r"^(?:\./|\.\./|/|[A-Za-z]:\\)|[^/\\]*\.[A-Za-z0-9]{1,8}$"
)


class ValidationResult:
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []

    def add_error(self, msg):
        self.is_valid = False
        self.errors.append(msg)

    def add_warning(self, msg):
        self.warnings.append(msg)


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_headings(text):
    return [(level, title.strip()) for level, title in HEADING_REGEX.findall(text)]


def extract_code_blocks(text):
    blocks = []
    lines = text.split("\n")
    i = 0
    n = len(lines)
    while i < n:
        m = FENCE_OPEN_REGEX.match(lines[i])
        if not m:
            i += 1
            continue
        start = i
        fence_char = m.group(2)[0]
        fence_len = len(m.group(2))
        open_line = lines[i]
        block_lines = [open_line]
        i += 1
        closed = False
        while i < n:
            close_m = FENCE_OPEN_REGEX.match(lines[i])
            if (
                close_m
                and close_m.group(2)[0] == fence_char
                and len(close_m.group(2)) >= fence_len
                and close_m.group(3).strip() == ""
            ):
                block_lines.append(lines[i])
                closed = True
                i += 1
                break
            block_lines.append(lines[i])
            i += 1
        if closed:
            blocks.append((start, "\n".join(block_lines)))

    ordered = sorted(
        blocks + extract_indented_code_blocks(text), key=lambda pair: pair[0]
    )
    return [block_text for _, block_text in ordered]


def extract_indented_code_blocks(text):
    blocks = []
    lines = text.split("\n")
    fenced = set()
    for block in extract_fenced_spans(lines):
        fenced.update(block)
    in_list = False
    previous_blank = True
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        stripped = line.strip()
        if i in fenced:
            in_list, previous_blank = in_list, False
            i += 1
            continue
        if not stripped:
            previous_blank = True
            i += 1
            continue
        indent = len(line) - len(line.lstrip(" \t"))
        if LIST_ITEM_REGEX.match(line):
            in_list = True
        elif indent == 0:
            in_list = False
        if not in_list and previous_blank and indent >= 4:
            start = i
            run = []
            while i < n and i not in fenced:
                current = lines[i]
                if not current.strip():
                    lookahead = i + 1
                    while lookahead < n and not lines[lookahead].strip():
                        lookahead += 1
                    if (
                        lookahead < n
                        and lookahead not in fenced
                        and len(lines[lookahead]) - len(lines[lookahead].lstrip(" \t"))
                        >= 4
                    ):
                        run.extend(lines[i:lookahead])
                        i = lookahead
                        continue
                    break
                if len(current) - len(current.lstrip(" \t")) < 4:
                    break
                run.append(current)
                i += 1
            if run:
                blocks.append((start, "\n".join(run)))
            previous_blank = False
            continue
        previous_blank = False
        i += 1
    return blocks


def extract_fenced_spans(lines):
    spans = []
    i = 0
    n = len(lines)
    while i < n:
        m = FENCE_OPEN_REGEX.match(lines[i])
        if not m:
            i += 1
            continue
        fence_char = m.group(2)[0]
        fence_len = len(m.group(2))
        start = i
        i += 1
        while i < n:
            close_m = FENCE_OPEN_REGEX.match(lines[i])
            if (
                close_m
                and close_m.group(2)[0] == fence_char
                and len(close_m.group(2)) >= fence_len
                and close_m.group(3).strip() == ""
            ):
                i += 1
                break
            i += 1
        spans.append(range(start, i))
    return spans


def extract_urls(text):
    return set(URL_REGEX.findall(text))


def extract_paths(text):
    return set(PATH_REGEX.findall(text))


def count_bullets(text):
    return len(BULLET_REGEX.findall(text))


def extract_inline_codes(text):
    text_without_fences = text
    for block in extract_code_blocks(text):
        text_without_fences = text_without_fences.replace(block, "", 1)
    text_without_fences = "\n".join(
        "" if FENCE_MARKER_LINE_REGEX.match(line) else line
        for line in text_without_fences.split("\n")
    )
    return re.findall(r"`([^`]+)`", text_without_fences)


def validate_headings(orig, comp, result):
    h1 = extract_headings(orig)
    h2 = extract_headings(comp)

    if len(h1) != len(h2):
        result.add_error(f"Heading count mismatch: {len(h1)} vs {len(h2)}")
        return

    t1 = [text for _, text in h1]
    t2 = [text for _, text in h2]
    if t1 != t2:
        lost = [t for t in t1 if t not in t2]
        added = [t for t in t2 if t not in t1]
        result.add_error(f"Heading text/order changed: lost={lost}, added={added}")
    elif h1 != h2:
        result.add_warning("Heading levels changed")


def validate_code_blocks(orig, comp, result):
    c1 = extract_code_blocks(orig)
    c2 = extract_code_blocks(comp)

    if c1 != c2:
        result.add_error("Code blocks not preserved exactly")


def validate_urls(orig, comp, result):
    u1 = extract_urls(orig)
    u2 = extract_urls(comp)

    if u1 != u2:
        result.add_error(f"URL mismatch: lost={u1 - u2}, added={u2 - u1}")


def validate_paths(orig, comp, result):
    p1 = extract_paths(orig)
    p2 = extract_paths(comp)
    lost = p1 - p2
    added = p2 - p1

    definite = {p for p in lost if DEFINITE_PATH_REGEX.search(p)}
    if definite:
        result.add_error(f"File paths lost: {sorted(definite)}")
    if (lost - definite) or added:
        result.add_warning(f"Path mismatch: lost={sorted(lost)}, added={sorted(added)}")


def validate_bullets(orig, comp, result):
    b1 = count_bullets(orig)
    b2 = count_bullets(comp)

    if b1 == 0:
        return

    diff = abs(b1 - b2) / b1

    if diff > 0.15:
        result.add_warning(f"Bullet count changed too much: {b1} -> {b2}")


def validate_inline_codes(orig, comp, result):
    def _render_spans(spans):
        out = []
        for span in sorted(spans):
            flat = span.replace("\n", "\\n")
            if len(flat) > MAX_REPORTED_SPAN:
                flat = flat[:MAX_REPORTED_SPAN] + "…"
            out.append(repr(flat))
        return "{" + ", ".join(out) + "}"

    c1 = Counter(extract_inline_codes(orig))
    c2 = Counter(extract_inline_codes(comp))

    if c1 != c2:
        lost = set(c1.keys()) - set(c2.keys())
        added = set(c2.keys()) - set(c1.keys())
        for code, count in c1.items():
            if code in c2 and c2[code] < count:
                lost.add(f"{code} (lost {count - c2[code]} of {count} occurrences)")
        if lost:
            result.add_error(f"Inline code lost: {_render_spans(lost)}")
        if added:
            result.add_warning(f"Inline code added: {_render_spans(added)}")


def validate(original_path: Path, compressed_path: Path) -> ValidationResult:
    result = ValidationResult()

    orig = read_file(original_path)
    comp = read_file(compressed_path)

    validate_headings(orig, comp, result)
    validate_code_blocks(orig, comp, result)
    validate_urls(orig, comp, result)
    validate_paths(orig, comp, result)
    validate_bullets(orig, comp, result)
    validate_inline_codes(orig, comp, result)

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python validate.py <original> <compressed>")
        sys.exit(1)

    orig = Path(sys.argv[1]).resolve()
    comp = Path(sys.argv[2]).resolve()

    res = validate(orig, comp)

    print(f"\nValid: {res.is_valid}")

    if res.errors:
        print("\nErrors:")
        for e in res.errors:
            print(f"  - {e}")

    if res.warnings:
        print("\nWarnings:")
        for w in res.warnings:
            print(f"  - {w}")

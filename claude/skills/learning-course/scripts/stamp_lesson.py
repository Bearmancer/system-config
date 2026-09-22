#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml"]
# ///

import argparse
import html as html_mod
import re
import sys
from pathlib import Path

import yaml

SKILL = Path(__file__).resolve().parent.parent
DEFAULT_STENCIL = SKILL / "assets" / "lesson.stencil.html"

VERDICT = re.compile(
    r"\b(confirmed|corrected|partially correct|wrong|unfindable|unverified|allegation)\b",
    re.I,
)
BARE = re.compile(r"https?://\S+")
TS = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
SECTION_REF = re.compile(r"(?:§|\bsections?\b)\s*(\d+)", re.I)
ANCHOR = re.compile(r"<a\b.*?</a>", re.S | re.I)
HREF = re.compile(r'href="([^"]+)"')
BANNED = (
    "open threads",
    "quiz",
    "your teacher",
    "how this treatise was built",
    "next on request",
    "boundar",
    "nothing past",
    "stops there",
)
REQUIRED = (
    "kicker",
    "title",
    "chapter",
    "chapters_total",
    "time_range",
    "transcript",
    "lead",
    "cast",
    "narrative",
    "machinery",
    "sources",
)


class StampError(Exception):
    pass


def parse_yaml(text: str) -> dict:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise StampError(f"unparsable YAML: {e}") from e
    if not isinstance(data, dict):
        raise StampError("YAML root must be a mapping (key: value pairs)")
    return data


def lesson_number(name):
    m = re.match(r"^(\d+)", name)
    return int(m.group(1)) if m else None


def row_id_from_filename(name):
    m = re.search(r"(?i)-ch0*(\d+)", name)
    return f"ch{m.group(1)}" if m else None


def sorted_lessons(lessons_dir, self_name):
    names = [p.name for p in lessons_dir.glob("*.html") if p.name != self_name]
    if self_name not in names:
        names.append(self_name)

    def key(n):
        m = re.match(r"^(\d+)", n)
        return (int(m.group(1)) if m else 10**6, n)

    return sorted(names, key=key)


def sibling_title(lessons_dir, name):
    y = lessons_dir / (Path(name).stem + ".yaml")
    if y.exists():
        d = parse_yaml(y.read_text(encoding="utf-8"))
        if d.get("title"):
            return str(d["title"])
    f = lessons_dir / name
    if f.exists():
        m = re.search(
            r"(?s)<h1[^>]*>(.*?)</h1>", f.read_text(encoding="utf-8", errors="replace")
        )
        if m:
            return re.sub(r"<[^>]+>", "", m.group(1)).strip()
    return Path(name).stem


def chapter_sibling(lessons_dir, ref):
    try:
        ref_n = int(ref)
    except (TypeError, ValueError):
        raise StampError(f"cast ref: '{ref}' is not a valid chapter number")
    for p in lessons_dir.glob("*.html"):
        m = re.search(r"(?i)-ch0*(\d+)-", p.name)
        if m and int(m.group(1)) == ref_n:
            return p.name
    return None


SUP_WRAP = re.compile(r"<sup>\s*$")


def check_citation_wrapping(*texts):
    seen = set()
    for text in texts:
        for m in ANCHOR.finditer(text):
            hrefs = HREF.findall(m.group(0))
            if not hrefs:
                continue
            target = hrefs[0].split("#")[0]
            if not target or target.startswith(("#", "mailto:", "data:")):
                continue
            if target in seen:
                preceding = text[: m.start()]
                if not SUP_WRAP.search(preceding):
                    raise StampError(
                        f"repeat citation not superscripted: {target} - "
                        "every mention after the first must be <sup><a href=...>"
                    )
            else:
                seen.add(target)


def stamp(yaml_path, lessons_dir, stencil_path):
    name = yaml_path.name
    stem = yaml_path.stem
    if not re.match(r"^\d{2}-ch\d+-", stem):
        raise StampError(
            f"filename rule: '{name}' must be NN-chK-<slug>.yaml (chapter in the filename)"
        )
    rid = row_id_from_filename(stem)
    if not rid:
        raise StampError(f"filename rule: cannot derive a chapter id from '{stem}'")

    data = parse_yaml(yaml_path.read_text(encoding="utf-8"))
    for field in REQUIRED:
        if field not in data or data[field] in ("", None, []):
            raise StampError(f"missing field: {field}")

    try:
        chapter = int(data["chapter"])
    except (TypeError, ValueError):
        raise StampError(f"chapter: '{data['chapter']}' is not a valid integer")
    mch = re.search(r"(?i)-ch0*(\d+)-", stem)
    file_ch = mch.group(1) if mch else None
    if file_ch is None or int(file_ch) != chapter:
        raise StampError(
            f"chapter mismatch: filename says ch{file_ch} but the content says {chapter}"
        )

    sources = data["sources"]
    if not isinstance(sources, list) or not sources:
        raise StampError("sources: at least one source with label+url is required")
    for s in sources:
        if not isinstance(s, dict) or not s.get("label") or not s.get("url"):
            raise StampError("sources: every entry needs label and url")
        if re.search(r"youtube\.com|youtu\.be", s["url"], re.I):
            raise StampError(
                "sources: a YouTube URL is not a source — cite the non-YouTube primary"
            )

    check_citation_wrapping(data["narrative"], data["machinery"])

    def scan(textval, what):
        low = textval.lower()
        for phrase in BANNED:
            if phrase in low:
                raise StampError(f"banned phrase in {what}: '{phrase}'")
        if BARE.search(ANCHOR.sub(" ", textval)):
            raise StampError(f"bare URL in {what}: wrap it in a link")
        if TS.search(textval):
            raise StampError(
                f"timestamp in {what}: no timestamps anywhere on the page, not even the surtitle"
            )
        for ref in SECTION_REF.findall(textval):
            if not 1 <= int(ref) <= 4:
                raise StampError(f"section ref {ref} in {what}: sections run 1-4")

    scan(data["lead"], "lead")
    scan(data["narrative"], "narrative")
    scan(data["machinery"], "machinery")
    if len(VERDICT.findall(data["narrative"])) < 2:
        raise StampError(
            "verdicts: the narrative needs at least two verdict words (confirmed / corrected / unfindable ...)"
        )

    lesson_no = lesson_number(stem)
    cast_rows = []
    for c in data["cast"]:
        role = html_mod.escape(str(c.get("role", "")))
        if c.get("ref") is not None:
            sib = chapter_sibling(lessons_dir, c["ref"])
            if not sib:
                raise StampError(
                    f"cast ref: chapter {c['ref']} has no sibling lesson file"
                )
            role += f' <a href="{sib}">(chapter {c["ref"]})</a>'
        cast_rows.append(
            f"<tr><td>{html_mod.escape(str(c.get('name', '')))}</td><td>{role}</td></tr>"
        )

    subgraph = str(data.get("subgraph", "") or "").strip()
    if subgraph:
        if not (subgraph.startswith("<svg") and subgraph.endswith("</svg>")):
            raise StampError("subgraph: must be a single inline <svg>…</svg> fragment")
        low_svg = subgraph.lower()
        if 'href="http' in low_svg or 'src="http' in low_svg:
            raise StampError("subgraph: no external references (inline only)")
        subgraph = f'<figure class="map">\n{subgraph}\n</figure>'

    order = sorted_lessons(lessons_dir, f"{stem}.html")
    idx = order.index(f"{stem}.html")
    prev_link = next_link = ""
    if idx > 0:
        p = order[idx - 1]
        prev_link = f'    <a href="{p}">Previous: {html_mod.escape(sibling_title(lessons_dir, p))}</a>'
    if idx < len(order) - 1:
        n = order[idx + 1]
        next_link = f'    <a href="{n}">Next: {html_mod.escape(sibling_title(lessons_dir, n))}</a>'

    try:
        chapters_total = int(data["chapters_total"])
    except (TypeError, ValueError):
        raise StampError(
            f"chapters_total: '{data['chapters_total']}' is not a valid integer"
        )

    meta = (
        f'Lesson {lesson_no:02d} · <a href="../reference/cast-map.html">cast map</a> · '
        f'<a href="../reference/glossary.html">glossary</a>'
    )
    stencil = stencil_path.read_text(encoding="utf-8")
    subs = {
        "PAGE_TITLE": f"Lesson {lesson_no:02d} — {data['title']}",
        "KICKER": html_mod.escape(str(data["kicker"])),
        "TITLE": html_mod.escape(str(data["title"])),
        "CHAPTER_N": chapter,
        "CHAPTER_M": chapters_total,
        "META_LINE": meta,
        "LEAD": f"<p>{html_mod.escape(str(data['lead']))}</p>",
        "SUBGRAPH": subgraph,
        "CAST_ROWS": "\n".join(cast_rows),
        "NARRATIVE": data["narrative"],
        "MACHINERY": data["machinery"],
        "PREV_LINK": prev_link,
        "NEXT_LINK": next_link,
        "ROW_ID": rid,
    }
    rendered = stencil
    for k, v in subs.items():
        rendered = rendered.replace("{{" + k + "}}", str(v))

    if lessons_dir.name != "lessons":
        raise StampError("write path: the target directory must be named 'lessons'")
    target = lessons_dir / f"{stem}.html"
    before = target.stat().st_size if target.exists() else 0
    target.write_text(rendered, encoding="utf-8")
    after = target.stat().st_size
    print(
        f"stamped {target} ({before} -> {after} bytes, mtime {int(target.stat().st_mtime)})"
    )
    return target


def main():
    ap = argparse.ArgumentParser(
        description="Stamp a lesson HTML from YAML + the canonical stencil."
    )
    ap.add_argument("yaml")
    ap.add_argument("--lessons-dir", required=True)
    ap.add_argument("--stencil", default=str(DEFAULT_STENCIL))
    args = ap.parse_args()
    try:
        stamp(Path(args.yaml), Path(args.lessons_dir), Path(args.stencil))
    except StampError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lesson_rules import (
    ANCHOR,
    SECTION_REF,
    TAG_CODE,
    TIMESTAMP as TS,
    VERDICT,
    BARE_URL as BARE,
    find_unsuperscripted_repeats,
)

SKILL = Path(__file__).resolve().parent.parent
DEFAULT_STENCIL = SKILL / "assets" / "lesson.stencil.html"

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
    "narrative",
    "machinery",
    "sources",
)
# cast is optional-but-explicit: absent/None/"" refuses (fail-closed);
# explicit `cast: []` omits §2 Cast (no humans this chapter).


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

    repeats = find_unsuperscripted_repeats(data["narrative"], data["machinery"])
    if repeats:
        target, _ = repeats[0]
        raise StampError(
            f"repeat citation not superscripted: {target} - "
            "every mention after the first must be <sup><a href=...>"
        )

    def scan(textval, what):
        low = textval.lower()
        for phrase in BANNED:
            if phrase in low:
                raise StampError(f"banned phrase in {what}: '{phrase}'")
        if BARE.search(ANCHOR.sub(" ", textval)):
            raise StampError(f"bare URL in {what}: wrap it in a link")
        tag_hit = TAG_CODE.search(ANCHOR.sub(" ", textval))
        if tag_hit:
            raise StampError(
                f"bare tag code in {what}: '{tag_hit.group(0)}' points nowhere — "
                "use a real hyperlink beside bare numerals"
            )
        if TS.search(textval):
            raise StampError(
                f"timestamp in {what}: no timestamps anywhere on the page, not even the surtitle"
            )
        for match in SECTION_REF.findall(textval):
            for ref in re.findall(r"\d+", match):
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
    if "cast" not in data or data["cast"] in ("", None):
        raise StampError(
            "missing field: cast (use explicit `cast: []` when no humans appear)"
        )
    cast = data["cast"]
    if not isinstance(cast, list):
        raise StampError(
            "cast: must be a list (use explicit `cast: []` when no humans appear)"
        )
    has_cast = len(cast) > 0
    cast_block = ""
    if has_cast:
        cast_rows = []
        for c in cast:
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
                raise StampError(
                    "subgraph: must be a single inline <svg>…</svg> fragment"
                )
            low_svg = subgraph.lower()
            if 'href="http' in low_svg or 'src="http' in low_svg:
                raise StampError("subgraph: no external references (inline only)")
            subgraph = f'<figure class="map">\n{subgraph}\n</figure>'
        cast_block = (
            "\n\t\t<h2>2. Cast</h2>\n"
            + (f"{subgraph}\n" if subgraph else "")
            + '\t\t<table class="cast">\n\t\t\t<thead>\n\t\t\t\t<tr>\n\t\t\t\t\t<th>Name</th>\n\t\t\t\t\t<th>Role This Chapter</th>\n\t\t\t\t</tr>\n\t\t\t</thead>\n\t\t\t<tbody>\n'
            + "\n".join(cast_rows)
            + "\n\t\t\t</tbody>\n\t\t</table>\n\n"
        )
    else:
        if str(data.get("subgraph", "") or "").strip():
            raise StampError("subgraph: no cast — omit subgraph when `cast: []`")
        for textval, what in (
            (data["lead"], "lead"),
            (data["narrative"], "narrative"),
            (data["machinery"], "machinery"),
        ):
            for ref in SECTION_REF.findall(textval):
                if int(ref) == 2:
                    raise StampError(
                        f"section ref 2 in {what}: no §2 Cast when `cast: []`"
                    )

    order = sorted_lessons(lessons_dir, f"{stem}.html")
    idx = order.index(f"{stem}.html")
    prev_link = next_link = ""
    if idx > 0:
        p = order[idx - 1]
        prev_link = f'<a href="{p}">Previous: {html_mod.escape(sibling_title(lessons_dir, p))}</a>'
    if idx < len(order) - 1:
        n = order[idx + 1]
        next_link = f'<a href="{n}">Next: {html_mod.escape(sibling_title(lessons_dir, n))}</a>'

    try:
        chapters_total = int(data["chapters_total"])
    except (TypeError, ValueError):
        raise StampError(
            f"chapters_total: '{data['chapters_total']}' is not a valid integer"
        )

    stencil = stencil_path.read_text(encoding="utf-8")
    subs = {
        "PAGE_TITLE": f"Lesson {lesson_no:02d} — {data['title']}",
        "KICKER": html_mod.escape(str(data["kicker"])),
        "TITLE": html_mod.escape(str(data["title"])),
        "CHAPTER_N": chapter,
        "CHAPTER_M": chapters_total,
        "CAST_BLOCK": cast_block,
        "LEAD": f"<p>{html_mod.escape(str(data['lead']))}</p>",
        "NARRATIVE": data["narrative"],
        "MACHINERY": data["machinery"],
        "NAV_LINKS": " ".join(link for link in (prev_link, next_link) if link),
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

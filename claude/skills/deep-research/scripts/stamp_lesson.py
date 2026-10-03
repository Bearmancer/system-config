#!/usr/bin/env python3
# /// script
# dependencies = ["pyyaml"]
# ///

import argparse
import html as html_mod
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from layout_diagram import DiagramError, layout as layout_diagram
from lesson_rules import (
    SUMMARY_MIN_WORDS,
    YOUTUBE,
    bar_scripts,
    chapter_label,
    prose_problems,
    render_bar,
    word_count,
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
REQUIRED = ("topic", "title", "chapter", "time_range", "transcript", "body", "sources")
# summary and diagram are optional; each renders only when present.
MAX_DIAGRAMS = 2
RETIRED = {
    "kicker": "the topic name is `topic`",
    "chapters_total": "no 'Chapter N of M' anywhere",
    "lead": "use `summary`, only for a chapter long enough to need one",
    "narrative": "one `body`, headings unnumbered",
    "machinery": "fold into `body` under a heading that names what it explains",
    "cast": "the cast lives on reference/cast-map.html",
    "subgraph": "use `diagram`, a mapping (or a list of up to 2) the layout computes",
}


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


def write_course_index(lessons_dir, order):
    """Refresh <workspace>/assets/course-index.js: the A-bar's chapter select
    reads this at runtime, so adding a lesson updates one file instead of
    restamping every already-stamped page."""
    assets_dir = lessons_dir.parent / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    entries = []
    for name in order:
        stem = Path(name).stem
        rid = row_id_from_filename(stem)
        if not rid:
            continue
        entries.append(
            {
                "id": rid,
                "label": chapter_label(lesson_number(name) or 0, sibling_title(lessons_dir, name)),
                "href": name,
            }
        )
    js = "window.COURSE_INDEX = " + json.dumps(entries) + ";\n"
    (assets_dir / "course-index.js").write_text(js, encoding="utf-8")


BAR_BLOCK_RE = re.compile(
    r'<header[^>]*class="[^"]*A-bar[^"]*"[^>]*>.*?</header>', re.S | re.I
)
BODY_OPEN_RE = re.compile(r"(<body[^>]*>)", re.I)
BODY_CLOSE_RE = re.compile(r"(</body>)", re.I)


def upsert_bar(html_text, bar_html, scripts_html):
    """Idempotent: replace an existing A-bar in place, else insert one right
    after <body>; add the two script tags only if either is missing."""
    if BAR_BLOCK_RE.search(html_text):
        html_text = BAR_BLOCK_RE.sub(lambda m: bar_html, html_text, count=1)
    else:
        html_text = BODY_OPEN_RE.sub(
            lambda m: m.group(1) + "\n\t\t" + bar_html, html_text, count=1
        )
    has_course_index = re.search(r'<script[^>]*src="[^"]*course-index\.js"', html_text)
    has_shell = re.search(r'<script[^>]*src="[^"]*shell\.js"', html_text)
    if not (has_course_index and has_shell):
        html_text = BODY_CLOSE_RE.sub(
            lambda m: scripts_html + "\n\t" + m.group(1), html_text, count=1
        )
    return html_text


def workspace_topic(workspace: Path) -> str:
    lessons_dir = workspace / "lessons"
    if lessons_dir.is_dir():
        for y in sorted(lessons_dir.glob("*.yaml")):
            topic = parse_yaml(y.read_text(encoding="utf-8")).get("topic")
            if topic:
                return str(topic)
    return workspace.name.replace("-", " ").title()


def refresh_bar(workspace: Path) -> list[Path]:
    """Inject/refresh the A-bar (+course-index.js) on a workspace's
    hand-authored reference/index pages — the one shared path so those pages
    never drift from the lesson stencil's shell by hand-editing."""
    lessons_dir = workspace / "lessons"
    order = []
    if lessons_dir.is_dir():
        order = sorted(
            (p.name for p in lessons_dir.glob("*.html")),
            key=lambda n: (lesson_number(n) or 10**6, n),
        )
        write_course_index(lessons_dir, order)

    topic = html_mod.escape(workspace_topic(workspace))
    touched = []
    ref_dir = workspace / "reference"
    if ref_dir.is_dir():
        for html in sorted(ref_dir.glob("*.html")):
            bar = render_bar(
                topic, [], title_href="../index.html", base="../lessons/" if order else ""
            )
            text = upsert_bar(
                html.read_text(encoding="utf-8"), bar, bar_scripts("../assets/", "../../assets/")
            )
            html.write_text(text, encoding="utf-8")
            touched.append(html)

    index_html = workspace / "index.html"
    if index_html.is_file():
        bar = render_bar(
            topic,
            [],
            current=workspace.name,
            base="lessons/" if order else "",
            home=True,
            topic_feed="../assets/course-index.js",
            topic_base="../",
        )
        text = upsert_bar(
            index_html.read_text(encoding="utf-8"), bar, bar_scripts("assets/", "../assets/")
        )
        index_html.write_text(text, encoding="utf-8")
        touched.append(index_html)

    return touched


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
    for field, why in RETIRED.items():
        if field in data:
            raise StampError(f"retired field: {field} ({why})")
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
    for src in sources:
        if not isinstance(src, dict) or not src.get("label") or not src.get("url"):
            raise StampError("sources: every entry needs label and url")
        if YOUTUBE.search(src["url"]):
            raise StampError(
                "sources: a YouTube URL is not a source — cite the non-YouTube primary"
            )

    summary = str(data.get("summary") or "").strip()
    body = str(data["body"])

    def scan(textval, what):
        low = textval.lower()
        for phrase in BANNED:
            if phrase in low:
                raise StampError(f"banned phrase in {what}: '{phrase}'")
        for rule, detail in prose_problems(textval):
            raise StampError(f"{rule} in {what}: {detail}")

    scan(summary, "summary")
    scan(body, "body")
    if not re.search(r'<a\s[^>]*href="https://', body):
        raise StampError("body: cite at least one source as a link on the words naming it")
    if summary and word_count(body) < SUMMARY_MIN_WORDS:
        raise StampError(
            f"summary: only a chapter of {SUMMARY_MIN_WORDS}+ words needs one (body has {word_count(body)})"
        )

    diagram_block = ""
    specs = data.get("diagram") or []
    if isinstance(specs, dict):
        specs = [specs]
    if not isinstance(specs, list) or not all(isinstance(d, dict) for d in specs):
        raise StampError("diagram: must be a mapping (or a list of up to 2) with rows, types and edges")
    if len(specs) > MAX_DIAGRAMS:
        raise StampError(f"diagram: {len(specs)} diagrams, the cap is {MAX_DIAGRAMS} per chapter")
    for i, spec in enumerate(specs, start=1):
        try:
            diagram = layout_diagram(spec, uid=f"d{i}")
        except DiagramError as e:
            raise StampError(str(e)) from e
        if diagram.crossings:
            print(f"WARN: diagram {i}: {diagram.crossings} line crossings")
        else:
            print(f"diagram {i}: 0 line crossings")
        diagram_block += f"\t\t{diagram.figure}\n\n"

    order = sorted_lessons(lessons_dir, f"{stem}.html")
    write_course_index(lessons_dir, order)
    idx = order.index(f"{stem}.html")
    prev_link = next_link = ""
    if idx > 0:
        p = order[idx - 1]
        prev_link = f'<a href="{p}">Previous: {html_mod.escape(sibling_title(lessons_dir, p))}</a>'
    if idx < len(order) - 1:
        n = order[idx + 1]
        next_link = f'<a href="{n}">Next: {html_mod.escape(sibling_title(lessons_dir, n))}</a>'

    topic = html_mod.escape(str(data["topic"]))
    title = html_mod.escape(str(data["title"]))
    summary_block = (
        f"\t\t<h2>Summary</h2>\n\t\t<p>{html_mod.escape(summary)}</p>\n\n" if summary else ""
    )
    stencil = stencil_path.read_text(encoding="utf-8")
    subs = {
        "PAGE_TITLE": f"{title} — {topic}",
        "BAR": render_bar(topic, [], current=rid, title_href="../index.html"),
        "TITLE": title,
        "SUMMARY_BLOCK": summary_block,
        "DIAGRAM_BLOCK": diagram_block,
        "BODY": body,
        "NAV_LINKS": " ".join(link for link in (prev_link, next_link) if link),
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
        description="Stamp a lesson HTML from YAML + the canonical stencil, "
        "or refresh the A-bar on a workspace's reference/index pages."
    )
    ap.add_argument("yaml", nargs="?")
    ap.add_argument("--lessons-dir")
    ap.add_argument("--stencil", default=str(DEFAULT_STENCIL))
    ap.add_argument(
        "--refresh-bar",
        metavar="WORKSPACE",
        help="inject/refresh the A-bar + course-index.js on "
        "<workspace>/reference/*.html and <workspace>/index.html",
    )
    args = ap.parse_args()
    if args.refresh_bar:
        for path in refresh_bar(Path(args.refresh_bar)):
            print(f"refreshed {path}")
        return
    if not args.yaml or not args.lessons_dir:
        ap.error("yaml and --lessons-dir are required unless --refresh-bar is given")
    try:
        stamp(Path(args.yaml), Path(args.lessons_dir), Path(args.stencil))
    except StampError as e:
        print(f"REFUSED: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

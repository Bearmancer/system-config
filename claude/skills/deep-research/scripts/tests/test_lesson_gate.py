import re
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SCRIPTS))
import check_lesson
import layout_diagram
from lesson_rules import SUMMARY_MIN_WORDS, render_bar
from test_layout_diagram import SPEC

GOOD_BODY = (
    '<h2>The Vote</h2>\n'
    '<p>The <a href="https://example.org/report">Example Institute report</a> puts the total at 28,000.</p>'
)
FOOTER = (
    '<footer class="lesson-footer"><nav>'
    '<a href="https://example.org/next">Next: Following Chapter</a></nav></footer>'
)


def write_page(tmp_path, rel, html):
    ws = tmp_path / "ws"
    path = ws / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    (ws / "assets").mkdir(exist_ok=True)
    for asset in ("course-index.js", "shell.js"):
        (ws / "assets" / asset).write_text("", encoding="utf-8")
    path.write_text(html, encoding="utf-8")
    return str(path)


def lesson(tmp_path, body=GOOD_BODY, before="", bar=None, footer=FOOTER, head_extra=""):
    bar = bar if bar is not None else render_bar("Topic Name", [], current="ch1", title_href="../index.html")
    html = (
        '<!DOCTYPE html><html lang="en"><head><title>t</title></head><body>\n'
        f"{bar}\n<h1>Chapter Name</h1>\n{head_extra}{before}{body}\n{footer}\n"
        '<script src="../assets/course-index.js"></script>\n<script src="../assets/shell.js"></script>\n'
        "</body></html>"
    )
    return check_lesson.check(write_page(tmp_path, "lessons/01-ch1-a.html", html))


def has(issues, fragment):
    return any(fragment in i for i in issues)


def test_a_vnext_lesson_passes(tmp_path):
    assert lesson(tmp_path) == []


@pytest.mark.parametrize(
    "prose,fragment",
    [
        ('<p>Total <sup><a href="https://example.org/report">2</a></sup>.</p>', "superscript"),
        ('<p>See <a href="https://example.org/report">1</a>.</p>', "weak-link"),
        ('<p>See <a href="https://example.org/report">here</a>.</p>', "weak-link"),
        ("<h2>1. Overview</h2>", "numbered-heading"),
        ("<h2>4) Overview</h2>", "numbered-heading"),
        ("<h2>Machinery</h2>", "machinery"),
        ("<p>The total was confirmed against the record.</p>", "verify-narration"),
        ("<p>The claim is verified.</p>", "verify-narration"),
        ("<p>The total was verified.</p>", "verify-narration"),
        ("<p>The figure remains unverified.</p>", "verify-narration"),
        ("<p>The figure is unfindable.</p>", "verify-narration"),
        ("<p>The date was checked against the record.</p>", "verify-narration"),
        ("<p>It stays unverified.</p>", "verify-narration"),
        ("<p>The figure is partially correct.</p>", "verify-narration"),
        ("<p>The total is <strong>corrected</strong> to 28,000.</p>", "verdict-label"),
        ("<p>Corrections: the total was 28,000.</p>", "correction-ledger"),
        ("<p><strong>Corrections:</strong> the total was 28,000.</p>", "correction-ledger"),
        ("<ul><li>Corrections: the total was 28,000.</li></ul>", "correction-ledger"),
        ("<h2>Corrections</h2>", "correction-ledger"),
        ("<p>The chapter works as a ladder.</p>", "teacher-voice"),
        ("<p>The closing line delivers the thesis whole.</p>", "teacher-voice"),
        ("<p>Key takeaway: it failed.</p>", "teacher-voice"),
        ("<p>Let's see what happened next.</p>", "teacher-voice"),
        ("<p>See §3 for the vote.</p>", "section-ref"),
        ("<p>The vote closed at 1:23.</p>", "timestamps"),
    ],
)
def test_prose_rules_fail_lessons(tmp_path, prose, fragment):
    assert has(lesson(tmp_path, body=GOOD_BODY + prose), fragment)


@pytest.mark.parametrize(
    "prose",
    [
        "<p>The Senate confirmed Garland to the seat.</p>",
        "<p>The court corrected the docket entry in 1996.</p>",
        "<p>Let's Encrypt issued the certificate.</p>",
        "<h2>1996: The Vote</h2>",
        "<h2>Why the Vote Failed</h2>",
        "<p>The verification desk reviewed it.</p>",
        "<p>UN monitors verified 1,200 civilian deaths.</p>",
        "<p>The Taliban dismissed the unverified video.</p>",
        "<p>The report was verified by two independent labs.</p>",
        "<p>The ministry issued corrections: two names changed.</p>",
        "<h2>1996. The Vote</h2>",
        "<p>The chapter shows the siege of Grozny.</p>",
        "<p>The chapter argues that money decided it.</p>",
    ],
)
def test_prose_rules_spare_ordinary_wording(tmp_path, prose):
    assert lesson(tmp_path, body=GOOD_BODY + prose) == []


def test_chapter_header_is_the_name_alone(tmp_path):
    assert has(lesson(tmp_path, before='<p class="kicker">Series</p>'), "kicker")
    assert has(lesson(tmp_path, before='<p class="surtitle">Chapter 3</p>'), "surtitle")
    assert has(lesson(tmp_path, before="<p>Chapter 3 of 7</p>"), "Chapter N of M")


def test_summary_only_when_the_chapter_is_long(tmp_path):
    summary = "<h2>Summary</h2><p>Short version.</p>"
    assert has(lesson(tmp_path, before=summary), "summary present in a short chapter")
    long_body = GOOD_BODY + "<p>" + "word " * SUMMARY_MIN_WORDS + "</p>"
    assert lesson(tmp_path, body=long_body, before=summary) == []


def test_no_book_video_label(tmp_path):
    assert has(lesson(tmp_path, body=GOOD_BODY + "<p>Book / Video</p>"), "Topic")


def test_no_sources_heading_or_reference_list(tmp_path):
    assert has(lesson(tmp_path, body=GOOD_BODY + "<h2>References</h2>"), "Sources/References")


def test_bar_shape(tmp_path):
    good = render_bar("Topic Name", [], current="ch1", title_href="../index.html")
    assert has(lesson(tmp_path, bar=good.replace('<span class="aa" aria-hidden="true">Aa</span>', "")), "'Aa' mark")
    assert has(lesson(tmp_path, bar=good.replace('<a href="../index.html">Topic Name</a>', "Topic Name")), "links the course index")
    assert has(lesson(tmp_path, bar=good.replace('href="../index.html"', 'href="../../index.html"')), "links the course index")
    assert has(lesson(tmp_path, bar=good.replace(" data-index", "")), "chapter dropdown")
    assert has(lesson(tmp_path, bar=good + good), "exactly one top bar")
    assert has(lesson(tmp_path, bar=""), "exactly one top bar")


def test_footer_holds_previous_next_only(tmp_path):
    leak = '<footer class="lesson-footer"><nav><a href="../index.html">Index</a></nav></footer>'
    assert has(lesson(tmp_path, footer=leak), "footer holds a nav link")


def test_diagram_from_the_layout_passes_the_gate(tmp_path):
    assert lesson(tmp_path, before=layout_diagram.layout(SPEC).figure) == []


def mutated_diagram(fn):
    d = layout_diagram.layout(SPEC)
    return fn(d.svg), d.legend


@pytest.mark.parametrize(
    "mutate,fragment",
    [
        (lambda s: s.replace('stroke-width="2.5"', 'stroke-width="2.5" stroke-dasharray="4"', 1), "dashed"),
        (lambda s: s.replace('class="elabel"', 'class="elabel" transform="rotate(20)"', 1), "rotated"),
        (lambda s: s.replace('stroke="var(--d1)"', 'stroke="#b3261e"', 1), "not a palette token"),
        (lambda s: s.replace('stroke="var(--d-neutral)"', 'stroke="var(--d2)"', 1), "marks one line"),
        (lambda s: s.replace('marker-end="url(#ah-d-d1)"', 'marker-end="url(#ah-d-zz)"', 1), "not defined"),
        (lambda s: re.sub(r'(class="elabel" x=")[\d.]+(" y=")[\d.]+', r"\g<1>1\g<2>1", s, count=1), "outside the viewBox"),
    ],
)
def test_diagram_gate_fails(tmp_path, mutate, fragment):
    svg, legend = mutated_diagram(mutate)
    assert has(lesson(tmp_path, before=f'<figure class="map">{svg}{legend}</figure>'), fragment)


def test_label_on_a_line_or_over_a_box_fails(tmp_path):
    d = layout_diagram.layout(SPEC)
    nodes = re.findall(r'<rect class="node" x="([\d.]+)" y="([\d.]+)"', d.svg)
    x, y = nodes[0]
    moved = re.sub(
        r'(class="elabel" x=")[\d.]+(" y=")[\d.]+', rf"\g<1>{float(x) + 20}\g<2>{float(y) + 10}", d.svg, count=1
    )
    issues = lesson(tmp_path, before=f'<figure class="map">{moved}{d.legend}</figure>')
    assert has(issues, "a label covers a box")
    line = re.search(r'<line class="edge"[^>]*x1="([\d.]+)" y1="([\d.]+)" x2="([\d.]+)" y2="([\d.]+)"', d.svg)
    x1, y1, x2, y2 = (float(v) for v in line.groups())
    on_line = re.sub(
        r'(class="elabel" x=")[\d.]+(" y=")[\d.]+',
        rf"\g<1>{(x1 + x2) / 2}\g<2>{(y1 + y2) / 2 + 3}",
        d.svg,
        count=1,
    )
    assert has(lesson(tmp_path, before=f'<figure class="map">{on_line}{d.legend}</figure>'), "a label sits on a line")


def test_diagram_colour_needs_a_legend_row(tmp_path):
    d = layout_diagram.layout(SPEC)
    legend = re.sub(r'<li class="legend-row"><span class="swatch" style="background:var\(--d1\)">.*?</li>', "", d.legend)
    assert has(lesson(tmp_path, before=f'<figure class="map">{d.svg}{legend}</figure>'), "no legend row")


def test_marker_ids_repeating_across_diagrams_fail(tmp_path):
    fig = layout_diagram.layout(SPEC).figure
    assert has(lesson(tmp_path, before=fig + fig), "repeats across")


def test_two_diagrams_with_their_own_ids_pass_and_a_third_fails(tmp_path):
    figs = [layout_diagram.layout(SPEC, uid=f"d{i}").figure for i in (1, 2, 3)]
    assert lesson(tmp_path, before=figs[0] + figs[1]) == []
    assert has(lesson(tmp_path, before="".join(figs)), "the cap is 2")


def test_each_diagram_carries_its_own_legend(tmp_path):
    first = layout_diagram.layout(SPEC, uid="d1").figure
    second = layout_diagram.layout(SPEC, uid="d2")
    bare = re.sub(r'<li class="legend-row"><span class="swatch" style="background:var\(--d1\)">.*?</li>', "", second.legend)
    page = first + f'<figure class="map">{second.svg}{bare}</figure>'
    assert has(lesson(tmp_path, before=page), "no legend row")


def test_edges_must_be_straight_lines(tmp_path):
    d = layout_diagram.layout(SPEC)
    curved = d.svg.replace("</svg>", '<path d="M0,0 L10,10" stroke="var(--d-neutral)"/></svg>')
    assert has(lesson(tmp_path, before=f'<figure class="map">{curved}{d.legend}</figure>'), "straight <line>")


def test_summary_length_ignores_the_diagram_and_the_summary(tmp_path):
    figure = layout_diagram.layout(SPEC).figure
    summary = "<h2>Summary</h2><p>" + "word " * SUMMARY_MIN_WORDS + "</p>"
    assert has(lesson(tmp_path, before=summary + figure), "summary present in a short chapter")


@pytest.mark.parametrize(
    "extra,fragment",
    [
        ('<p><a href="../index.html">the course</a></p>', "course-index link repeated"),
        (
            '<p><a href="../reference/glossary.html">terms</a> <a href="../reference/glossary.html">again</a></p>',
            "glossary link repeated",
        ),
        (
            '<p><a href="../reference/cast-map.html">who</a> <a href="../reference/cast-map.html">again</a></p>',
            "cast-map link repeated",
        ),
    ],
)
def test_link_budget_violations_fail(tmp_path, extra, fragment):
    assert has(lesson(tmp_path, body=GOOD_BODY + extra), fragment)


def test_layout_labels_edges_and_overlap_together(tmp_path):
    d = layout_diagram.layout(SPEC)
    unlabelled = d.svg.replace('class="elabel"', 'class="other"', 1)
    assert has(lesson(tmp_path, before=f'<figure class="map">{unlabelled}{d.legend}</figure>'), "carries its own label")


def index_page(tmp_path, rows=None, extras=None, bar=None, extra=""):
    bar = bar or render_bar(
        "Topic Name", [], current="ws", base="lessons/", home=True,
        topic_feed="../assets/course-index.js", topic_base="../",
    )
    rows = rows if rows is not None else (
        '<li id="ch1"><a href="lessons/01-ch1-a.html">1 · Opening</a></li>\n'
        '<li id="ch2"><a href="lessons/02-ch2-b.html">2 · Middle</a></li>'
    )
    extras = extras if extras is not None else (
        '<nav class="index-extras"><a href="reference/cast-map.html">Cast</a>'
        '<a href="reference/glossary.html">Glossary</a><a href="reference/timeline.html">Timeline</a></nav>'
    )
    html = (
        f'<!DOCTYPE html><html><head><title>Course</title></head><body>{bar}<h1>Topic Name</h1>'
        f'<ol class="index-rows">{rows}</ol>{extras}{extra}'
        '<script src="assets/course-index.js"></script><script src="assets/shell.js"></script></body></html>'
    )
    ws = tmp_path / "ws"
    for rel in ("lessons/01-ch1-a.html", "lessons/02-ch2-b.html", "reference/cast-map.html",
                "reference/glossary.html", "reference/timeline.html"):
        (ws / rel).parent.mkdir(parents=True, exist_ok=True)
        (ws / rel).write_text("x", encoding="utf-8")
    return check_lesson.check(write_page(tmp_path, "index.html", html))


def test_index_page_passes(tmp_path):
    assert index_page(tmp_path) == []


def test_hub_home_bar_passes(tmp_path):
    bar = render_bar("Index", [], home=True)
    assert index_page(tmp_path, bar=bar) == []


@pytest.mark.parametrize(
    "kwargs,fragment",
    [
        ({"rows": '<li id="ch1"><a href="lessons/01-ch1-a.html">ch1</a></li>'}, "reads 'N · name'"),
        ({"rows": '<li id="ch1"><a href="lessons/01-ch1-a.html">1. Opening</a></li>'}, "reads 'N · name'"),
        ({"extra": "<p>Published 2026-09-29 15:22</p>"}, "date line"),
        ({"extra": "<p>Pick a Book / Video</p>"}, "Topic"),
        ({"extra": "<h2>Cast roster · Glossary</h2>"}, "Cast roster"),
        ({"extras": '<a href="reference/cast-map.html">Cast</a>'}, "index-extras"),
        ({"bar": render_bar("Topic Name", [], title_href="../index.html")}, "home bar"),
    ],
)
def test_index_rules_fail(tmp_path, kwargs, fragment):
    assert has(index_page(tmp_path, **kwargs), fragment)


def test_geometry_regression_fixture_keeps_its_two_defects():
    fixture = SCRIPTS.parent / "evals" / "fixtures" / "geom-fixture.html"
    out = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_map_geometry.py"), str(fixture)],
        capture_output=True, text=True,
    ).stdout
    assert "box-overlaps=1" in out and "labels-on-boxes=1" in out
    assert "edges-through-boxes=0" in out and "labels-on-labels=0" in out and "out-of-bounds=0" in out


def test_fixture_runners_are_green():
    for runner in ("fixtures/run_gate.py", "fixtures/stencil/run_stencil_tests.py", "fixtures/stencil/run_parity_test.py"):
        proc = subprocess.run(
            ["uv", "run", str(SCRIPTS / runner)], capture_output=True, text=True
        )
        assert proc.returncode == 0, runner + "\n" + proc.stdout + proc.stderr

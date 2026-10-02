# Lesson content schema (YAML)

One YAML per lesson: `<workspace>/lessons/<NN>-ch<K>-<slug>.yaml`. `scripts/stamp_lesson.py` reads it + `assets/lesson.stencil.html`, writes the lesson HTML. Page rules: `references/course/page-design.md`. Plain-text fields are HTML-escaped; `body` accepts restricted HTML: `<h2> <h3> <p> <blockquote> <ul> <ol> <li> <strong> <em> <a>`.

## Fields

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `topic` | string | yes | topic name shown left in the bar, e.g. `Afghanistan Turning Against Taliban` |
| `title` | string | yes | chapter name; the H1, alone |
| `chapter` | int | yes | absolute source chapter; MUST equal `<K>` in the filename |
| `time_range` | string | yes | `1:55:38–2:08:19` (en dash); admin-only (NOTES.md chapter map); never rendered |
| `transcript` | string | yes | slice filename under `reference/transcripts/`; admin-only; never rendered |
| `summary` | string | no | plain text, one paragraph; refused unless `body` has >= 1200 words |
| `diagram` | mapping or list of <= 2 mappings | no | relationship diagram spec(s); layout computed at stamp time, each figure with its own marker ids `d1`, `d2` (`diagram-spec.md`) |
| `body` | text | yes | restricted HTML; unnumbered headings named for what each section explains; >= 1 `<a href="https://...">` |
| `sources` | list | yes | `{label, url, note?}`; non-empty; every `url` starts `https://`; YouTube URLs refused. Admin-only: feeds RESOURCES; never rendered |

Derived by the stamp, never authored: `<title>`, the bar (topic name linking `../index.html`, the course index, chapter dropdown, `Aa` settings), prev/next links (filename order; text `Previous: <title>` / `Next: <title>`), row id `chK` from the filename, `<workspace>/assets/course-index.js` (labels `N · title`, `N` = filename lesson number) and a copy of `assets/shell.js`. No surtitle, kicker, "Chapter N of M", date, cast table, reference list, footer text beyond prev/next.

Retired fields refuse with a message naming the replacement: `kicker` (use `topic`), `chapters_total`, `lead` (use `summary`), `narrative` + `machinery` (use `body`), `cast` (cast page is course-level), `subgraph` (use `diagram`).

## Body prose

- Link the words that name the source: `the <a href="https://...">Frontelligence Insight projection</a>`. The same source may be linked again the same way.
- State the fact and its correction in one sentence; never narrate checking. Unfindable claim: attribute it to the source's own account.
- No `<sup>`, numeral or "here" link text, bare URL, `[C4]` tag code, timestamp, `§N`, numbered heading, "Machinery" heading, "Corrections:" ledger, teacher-voice framing.

## Fail-closed rules (stamp exits 2, message names the rule)

1. Filename not `NN-chK-<slug>.yaml` -> refuse.
2. `chapter` != filename `K` -> refuse.
3. Required field missing/empty -> `missing field: <name>`.
4. Retired field present -> `retired field: <name>`.
5. `sources` empty, entry lacks `label`/`url`, or url matches `youtube.com`/`youtu.be` -> refuse.
6. Banned phrase (open threads, quiz, teacher, boundary wording) -> `banned phrase`.
7. Prose rule violation in `summary` or `body` -> `<rule> in <field>`; rules: `superscript`, `weak-link`, `bare-url`, `tag-code`, `timestamp`, `section-ref`, `numbered-heading`, `machinery`, `verify-narration`, `verdict-label`, `correction-ledger`, `teacher-voice` (defined once in `scripts/lesson_rules.py`).
8. `body` without a `https` link -> refuse.
9. `summary` with a `body` under 1200 words -> refuse.
10. `diagram` invalid, wrongly typed, more than 2, or not placeable (unknown node, line through a box, label with no clear spot) -> `diagram: ...`.
11. Write target outside `<workspace>/lessons/` -> refuse.

## Golden example

`scripts/fixtures/stencil/golden-07-ch13-1996.yaml` (stamps gate-green; includes a diagram). Shape:

```yaml
topic: "Test Course"
title: "1996"
chapter: 13
time_range: "1:55:38–2:08:19"
transcript: "1996-1h55m38s-2h08m19s.md"
diagram:
  rows:
    - - {id: yeltsin, name: "Boris Yeltsin", note: "President"}
      - {id: sobchak, name: "Anatoly Sobchak", note: "Mayor of Petersburg"}
    - - {id: oligarchs, name: "Bankers", note: "Loans-for-shares owners"}
      - {id: voters, name: "Voters", note: "June runoff"}
  types:
    fund: "Funding"
  edges:
    - {from: oligarchs, to: yeltsin, label: "Bankers fund the campaign", type: fund, directed: true}
    - {from: oligarchs, to: sobchak, label: "Banks back Petersburg rivals", type: fund, directed: true}
    - {from: voters, to: sobchak, label: "Voters oust Sobchak", directed: true}
body: |
  <h2>The Vote</h2>
  <p>The June runoff went to Yeltsin, according to the <a href="https://www.rferl.org/example">official record</a>.</p>
sources:
  - label: "RFE/RL report"
    url: "https://www.rferl.org/example"
```

## Tests

`python scripts/fixtures/stencil/run_stencil_tests.py`: golden stamps gate-green; each corrupt variant fails with its rule name. `uv run --with pytest pytest scripts/tests -q` covers the gate, layout, CSS contrast, publisher.

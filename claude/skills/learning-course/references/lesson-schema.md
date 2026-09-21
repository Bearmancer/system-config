# Lesson content schema (YAML) — W2b

One YAML per lesson: `<workspace>/lessons/<NN>-ch<K>-<slug>.yaml`. The stamp
(`scripts/stamp_lesson.py`) reads schema + `assets/lesson.stencil.html` and
writes the lesson HTML. Plain text fields are HTML-escaped; only `narrative`
and `machinery` accept a restricted HTML subset: `<p> <blockquote> <ul> <ol>
<li> <strong> <em> <a>`.

## Fields

| Field | Type | Required | Notes |
|---|---|---|---|
| `kicker` | string | yes | series line, e.g. `Putin: The Rise to Power` |
| `title` | string | yes | H1 text |
| `chapter` | int | yes | absolute chapter; MUST equal the `<K>` in the filename |
| `chapters_total` | int | yes | surtitle denominator |
| `chapter_label` | string | no | defaults to plain number; e.g. `7` or `14` |
| `time_range` | string | yes | `1:55:38–2:08:19` (en dash) |
| `transcript` | string | yes | slice filename under `reference/transcripts/` |
| `lead` | string | yes | §1 paragraph (plain text) |
| `cast` | list | yes | `{name, role, ref?}` — `ref` = chapter number for the `(chapter N)` link |
| `subgraph` | bool | no | default false; true renders a placeholder comment slot |
| `narrative` | text | yes | §3 restricted HTML; MUST carry ≥2 verdict words (confirmed / corrected / partially correct / wrong / unfindable / unverified / allegation) |
| `machinery` | text | yes | §4 restricted HTML |
| `sources` | list | yes | `{label, url, note?}` — non-empty; every `url` starts `https://` |

Derived by the stamp (never authored): page `<title>`, surtitle, meta line,
cast-table `(chapter N)` hrefs (resolved against sibling lesson files),
prev/next links (from filename order; text `Previous: <target title>` read
from the sibling YAML or H1), row id from the filename, footer line
(`Workspace: <course title> · Lesson NN · chapter K of M` — course title from
`MISSION.md` H1). No Sources block, no footer bibliography — the stamp
renders no separate citation list at all.

**Citations are author-written inline, not stamp-derived.** Write the first
mention of a source directly in `narrative`/`machinery` as a full `<a
href="...">`. Write every later mention of that same URL as
`<sup><a href="...">n</a></sup>` yourself — the stamp does not auto-convert
repeats. The stamp only ENFORCES the shape: a target's first occurrence may
be a bare `<a>`; every occurrence after the first must be wrapped in
`<sup>...</sup>`, or the stamp refuses.

## Fail-closed rules (stamp exits non-zero, message names the rule)

1. Filename not `NN-chK-<slug>.html`-shaped → refuse.
2. `chapter` ≠ filename `K` → refuse.
3. Any required field missing/empty → refuse.
4. `sources` empty or a source lacks `label`/`url` → refuse.
5. Narrative verdict words < 2 → refuse.
6. Any link target's occurrence after the first not wrapped in `<sup>...</sup>` → refuse (first occurrence may be bare; every repeat must be a live superscript link).
7. Bare `http(s)://` text outside an anchor in any field → refuse.
8. §-reference to a section number outside 1–6 → refuse.
9. Timestamp pattern in narrative/machinery/lead (surtitle owns timestamps) →
   refuse.
10. `cast[].ref` pointing at a chapter with no sibling lesson file → refuse.
11. Write target outside `<workspace>/lessons/` → refuse.

## Golden example (must stamp gate-green)

```yaml
kicker: "Putin: The Rise to Power"
title: "1996"
chapter: 13
chapters_total: 18
time_range: "1:55:38–2:08:19"
transcript: "1996-1h55m38s-2h08m19s.md"
lead: "The hinge year: Yeltsin climbs back from single digits while Sobchak loses Petersburg."
cast:
  - name: "Boris Yeltsin"
    role: "President; reelected via spin, loans and a ceasefire"
    ref: 8
narrative: |
  <p>The June runoff result is <strong>confirmed</strong> against the <a href="https://www.rferl.org/example">official record</a> beside the quoted wording.</p>
  <blockquote>"We won."</blockquote>
  <p>The turnout figure stays <strong>unverified</strong> outside the source's account, per the same <sup><a href="https://www.rferl.org/example">1</a></sup> report.</p>
machinery: |
  <p>Loans-for-shares converts political access into ownership.</p>
sources:
  - label: "RFE/RL report"
    url: "https://www.rferl.org/example"
    note: "accessed 2026-09-21"
```

## Corrupt variants (W4 fixtures — each MUST fail with its named rule)

| Fixture | Mutation | Expected rule |
|---|---|---|
| `corrupt-empty-sources.yaml` | `sources: []` | 4 |
| `corrupt-bad-filename.html` | filename without `-chK-` | 1 |
| `corrupt-chapter-mismatch.yaml` | `chapter: 12` on a `ch13` file | 2 |
| `corrupt-open-threads.yaml` | "Open threads" phrase in narrative | gate scan (11 in contract) |
| `corrupt-triple-link.yaml` | same URL appears twice, neither repeat wrapped in `<sup>` | 6 |
| `corrupt-bare-url.yaml` | plain URL text in narrative | 7 |
| `corrupt-section-ref.yaml` | "see §7" with six sections | 8 |
| `corrupt-stray-time.yaml` | `1:23` inside narrative | 9 |
| `corrupt-missing-title.yaml` | no `title` | 3 |
| `corrupt-orphan-cast.yaml` | `cast[].ref: 99` | 10 |

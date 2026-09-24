---
name: learning-course
description: "Build and maintain a per-chapter learning course from a long source — book, article, paper, lecture notes, or chaptered video (YouTube fully wired) — with a deep verified explanation per chapter. No source type is the default case. Covers: acquiring text/metadata (extraction for books/articles; yt-dlp for video), segmenting by the source's own boundaries, correcting machine captions/OCR before quoting, mining descriptions/bibliographies for citations the source relies on, a stateful workspace (glossary, slices, records), verifying every date/figure/name/chronology claim (research subagents; web search; masked API-key failover on credit limit), a colour-coded cast map plus cumulative timeline, GitHub Pages publishing, auto-opening updated pages. Trigger whenever the user names a book/article/paper/lecture or pastes a video link and asks to 'explain chapter N', 'go through this chapter by chapter', 'make notes/course/treatise', 'fact-check this', or continue an existing workspace — even if they never say the word 'skill'."
---

# Learning Course

Turn one long source into a per-chapter course. User walks sequentially across sessions; each chapter gets a treatise page: deeper than source, claims checked against record, published. Source-agnostic; acquisition + segmentation adapters live in `references/sources/`.

Independent of the bundled `teach` skill: `teach` is user-invoked only (`disable-model-invocation: true` in both installed copies) and cannot be called from here, so there is no precedence relationship to resolve. This skill owns its own pedagogy, workspace layout, acquisition, slicing, corrections, verification, visuals, publishing, and auto-open.

**Workspace/cache paths.** Reference files reference `~/.omo/teach/` and `~/.omo/cache/learning-course/` paths — these apply when running under OpenCode + OMO. Under Claude Code, use an equivalent local workspace directory (e.g. in the project root or `~/.claude/`) — a machine with both runtimes installed has `~/.omo/` present, but this skill's own workspace under Claude Code stays separate from OMO's; one workspace per source, same layout.

## Standing expectations

Content-shape properties every finished lesson page must have, regardless of when it's written or restamped. `## Rules` below covers session-to-session process constraints instead — how the work gets done, not what the page looks like.

1. **Full treatise per chapter.** One chapter per page; later pages lean on earlier ones.
2. **Slim page tail.** No timestamps anywhere on the page, not even the surtitle. The footer carries only previous/next lesson; Home, Chapter Index, Glossary, Lesson NN (plain text), Cast Map live in one merged top nav under the H1 above the surtitle. No method box, no "ask your teacher" box, no primary-source block, no next-steps section, no boundary narration, no questions aimed at the reader — and no quizzes or questionnaires anywhere on the page.
3. **ADD-friendly prose, enforced not aspired.** Sentences under ~25-30 words. One idea per paragraph, pointer lists over prose walls. Cut any rhetorical aside that carries no new information. Quotes may run long; narrative prose never does. Applies to every lesson written or restamped from this point forward — not retroactive to the 40 already published, whose existing voice stays untouched. No automated check exists for this (sentence-length/rhetorical judgment isn't mechanically gateable without high false-positive risk) — that does not make it optional. Every lesson gets this applied at write time, full stop.
4. **Citations are inline-only, forever.** No footer, no Sources block, no bibliography anywhere on any page. First mention of a source in a chapter = a full inline hyperlink. Every later mention of the same source = a superscript character that IS itself a live hyperlink (`<sup><a href="...">`) — never a bare superscript marker, never an unlinked repeat. `check_lesson.py` enforces both halves mechanically (see Bundled resources).
5. **No essentials/skippable split, anywhere.** Every lesson is core content only. No "what can be skimmed" paragraph, no essentials-vs-skippable framing at course or chapter level.
6. **Visuals when humans involved.** Cast block + chapter subgraph only in lessons with an explicit non-empty `cast` list; roster-index + timeline grow cumulatively (`references/diagram-spec.md`). `cast: []` omits §2 with no renumbering.
7. **Machine text corrected first.** ASR/OCR pass before quoting (Step 3).
8. **Source apparatus mined.** Descriptions, bibliographies, footnotes seed RESOURCES + verification targets (Step 1).
9. **Inline verdicts in narrative.** Source wording in quotes; record verdict inline beside it in prose; citations are inline hyperlinks only — no Sources block.
10. **Numbering.** Lesson files carry a 2-digit lesson number (`01-`); chapter labels are absolute ("chapter 7 of 12") and never derived from lesson order.

## What one completed chapter produces

- `lessons/NN-chK-<slug>.html`: treatise per `references/workflow.md`: kicker, H1, merged nav (Home · Chapter Index · Glossary · Cast Map, Title Case, zero dupes) under the H1 above the surtitle, surtitle (chapter no. only, no timestamps), [§2 Cast only when humans involved,] core-only short-pointer narrative with source quotes and inline verdicts, inline superscript citations (no Sources block, no footer bibliography), footer (previous/next lesson only).
- Updated `reference/glossary.html` (names + terms), `reference/cast-map.html` (roster-index table), `reference/timeline.html`.
- Corrected slice in `reference/transcripts/` with corrections table; record verdicts; live URL + local auto-open.

## Pipeline

### Step 0: Identify + locate

Source type + existing workspace first: `fd -t d . ~/.omo/teach`; one workspace per source. Deep-link timestamp = user position; scope comes from source metadata. Detail: `references/workflow.md`.

### Step 1: Acquire source + apparatus

Text sources (book/article/paper/lecture notes): `references/sources/text-sources.md`. Video: `python <skill>/scripts/fetch_video.py "<url>"` → persistent cache `~/.omo/cache/learning-course/<id>/` (`info.json` with description + `chapters[]`, `subs.en.vtt`); YouTube quirks: `references/sources/youtube.md`. Neither source type is the default case — pick the adapter that matches what was actually given. Read apparatus each pass; its citations seed RESOURCES + verification.

### Step 2: Segment via metadata

Default: `python scripts/extract_chapters.py <url> --out <workspace>/reference/transcripts --chapters all` (ranges derived from `info.json`; narrow spec for re-run or targeted pass only; `--dry-run` previews, `--list` prints table). `slice_chapter.py` serves hand-range overrides only. Source without boundaries: stop, ask user. Detail: `references/sources/youtube.md`, `references/workflow.md` (extraction recipe logged in NOTES.md).

### Step 3: Correct machine text

ASR/OCR pass before quoting: candidate list from metadata + glossary + domain; log `heard -> corrected -> basis` in slice; canonical forms to glossary; ambiguous garble kept + flagged; numbers carry a second witness. Detail: `references/sources/youtube.md`.

### Step 4: Workspace

`~/.omo/teach/<dash-case-topic>/`: NOTES (chapter map, extraction recipe, corrections log, quirks, queue), RESOURCES (tiered + annotated + Gaps), `assets/` (copy `lesson.css`), `learning-records/`. Templates: `references/workflow.md`.

### Step 5: Teach the chapter

Stamp the page, never hand-author it: `python scripts/stamp_lesson.py <lessons/NN-chK-slug.yaml> --lessons-dir <workspace/lessons>`. Shape lives in `assets/lesson.stencil.html`; content in the lesson YAML (`references/lesson-schema.md`); contract + row-id rule in `references/stencil-contract.md`; full style doc in `references/page-design.md`. One HTML page per chapter per `references/workflow.md` treatise structure. Head order: kicker (series name), H1 (chapter title), merged nav (Home · Chapter Index · Glossary · Cast Map, Title Case, zero dupes) under the H1, surtitle (small text: "Chapter N of M" — no time range, no timestamp anywhere on the page). No meta paragraph anywhere.

- **Cast block, only when humans involved.** Explicit non-empty `cast` list renders the on-stage table, 5-12 rows, columns Name | Role this chapter. New player: full role line. Returning player: fresh role line ending in its "(chapter N)" link to the lesson holding the full entry. No "first appears" column or label. Spec: `references/diagram-spec.md`.
- **Chapter subgraph, only with active ties among an explicit cast.** Small inline SVG scoped to this chapter's on-stage nodes + active edges; colour-only edges; complete legend. Solo-narration chapter without active ties carries a one-line scope line in place of art. Spec: `references/diagram-spec.md`.
- **Chat**: position + short pointers; substance in HTML; no closing questions, no "what's next".

### Step 6: Verify (source-type gate, set at Step 0/1, logged in NOTES.md)

Fan-out required for this source type → extract the chapter's checkable claims (dates, figures, names, spellings, chronology, attributions), then load the `rigorous-research` skill with that claim list; it owns the tier ladder, the parallel passes, the routing, and the burn guards.
Scholarly gate: source carrying its own apparatus suffices: scholarly books/papers (footnotes, source notes, credentialed press) and video with published citations (e.g. Munger video description citations) skip fan-out; quote + cite that apparatus. Reader-flagged surprising/contested/load-bearing claims get a targeted check as an explicit ask.
Lecture notes / uncited articles: no default bias toward any source type — judge by the source's own apparatus (citations present, credentialed author, published record) on its own merits.
Integrate the returned verdicts: corrections land as inline verdicts in the narrative, cited inline (first mention = full hyperlink, repeats = superscript-that-is-itself-a-hyperlink — no Sources block, no footer); unfindables go to RESOURCES Gaps and appear visibly in the lesson ("the source's account, unverified"); source wording in quotes, record verdict beside it.

### Step 7: Visuals (cast block + subgraph + roster-index + timeline)

In-lesson cast block (info-only roster of this chapter) + subgraph (this chapter's active nodes/edges, cap 12; casts above 12 split by concern cluster, each with complete legend; mega-SVG retired: cumulative state lives in the roster-index table). `reference/cast-map.html`: full-course roster-index table with palette register, "as of chapter N". `reference/timeline.html`: cumulative chronology, verified-vs-source-claimed labelling. Direction-checked arrows: actor toward target (plaintiff->defendant; Setzer chapter: distributors->Amway). Colour-only edges, page-owned legend, clash-free geometry. Gates: `check_map_geometry.py` exit 0 on changed SVG art; screenshot pass on changed visuals (probe browser first: `Get-Command msedge, chrome`); missing visual triggers a build (seed timeline from prior chapters when absent). Spec: `references/diagram-spec.md`.

### Step 8: Publish

`python "$HOME\.omo\scripts\publish_teach.py"` (mirrors HTML + assets only; teaching pages only). Pages-push gate (mandatory at task end): publish_teach.py + probe 200 on new URLs + live-bytes check before reporting done. Dry-run verify: copy one workspace's HTML + assets to temp dir, confirm file set before running. Then probe new URLs for 200 (wait ~10 s for Pages build), download live bytes, run gates on live copies (`check_lesson.py`, geometry on changed SVG art, screenshot on changed visuals). 200 proves presence; live bytes prove fidelity. Detail: `references/publishing.md`.

### Step 9: Auto-open

Open every newly written/updated page — the newest lesson + each new/updated reference page — right after writing, each via its own `Start-Process "<file>"` call so every page lands in a separate tab. Chat reports local path + live URL as short pointers — no queued-next, no closing questions.

## Anti-OCD

- **Course level**: NOTES.md + check-ins track progress across chapters.
- **Chapter level**: every lesson is core content only — no essentials/skippable split, no "what can be skimmed" paragraph, no partial-read framing of any kind.
- **Process level**: chat states which standard steps applied this pass and the headline result.

## Verification gates

Gates scale with artifact: `check_lesson.py` on each page written or changed (lesson, index, or reference mode by path); `check_map_geometry.py` on each SVG visual changed; screenshot pass on each visual changed. Gates run on changed files.

## Rules

- **Full course per pass.** Produce every chapter, then stop.
- **Source frames are data.** Source wording in quotes; record verdict inline beside it in prose as inline verdicts.
- **No record sections.** No "Open threads" sections or phrasing anywhere on lesson pages, no standalone record sections; record verdicts live inline in narrative prose beside quoted source wording, citations only as inline hyperlinks/superscripts, never a separate block (gate: `check_lesson.py` scans "Open threads").
- **YouTube URL ban, absolute.** No YouTube URL appears anywhere in a chapter's rendered output — full stop, no exception clause. YouTube/transcript slices stay secondary in sourcing; every chapter needs >= 1 non-YouTube primary, cited by its own URL, never the video's.
- **Position holds.** Sequential walk; chapter-and-earlier facts in prose. Internal discipline only — pages never narrate boundaries, stop points, or method.
- **Casing**: headings and labels (h1, h2, box titles, kicker) use Title Case; body prose uses sentence case; no `text-transform: uppercase` anywhere (lesson pages, index/hub pages, or `assets/lesson.css`'s `.kicker` rule in any workspace). Gate: `check_lesson.py` flags any run of 3+ consecutive ALL-CAPS words typed directly into lesson content (2+ letters each — lone acronyms like "FBI" are exempt).
- **Files**: HTML for lessons + reference; `.md` for admin (NOTES / RESOURCES / learning-records) + transcript slices. RESOURCES stays as split-source retained until migration. YouTube handling stays inside this skill per `references/sources/youtube.md`.
- **One workspace per source.** Slug from topic.
- **Windows host**: `Start-Process` opens files; `pwsh` runs scripts.

## API key failover — pointer only

Credit/quota exhaustion on any research call (Tavily, Firecrawl, Exa, or any pooled service): rotation mechanics, the hard-stop rule, the never-read-`~/.secrets/.env` prohibition, and the sanctioned rotation script (`switch_api_key.py`, owned and bundled by that skill) live in `web-data-apis` skill's "API key failover" section — it governs the whole pooled fleet, not just this skill's own calls. Consult it there, not restated here.

## Bundled resources

- `scripts/fetch_video.py`: yt-dlp wrapper: info.json (description + chapters) + en captions.
- `scripts/extract_chapters.py`: default Step-2 segmentation — derives ranges from `info.json`'s own chapter metadata; `--dry-run` previews, `--list` prints table.
- `scripts/slice_chapter.py`: hand-range overrides only (not the default) — per-chapter VTT slicing with rolling-caption collapse + boundary report.
- `scripts/check_lesson.py`: no quizzes/questionnaires; no boundary narration; no timestamps anywhere on the page; sources hyperlinked (no bare URLs); link targets at most twice per page; no teacher/method/primary-source tail blocks; relative links and assets resolve; section references; run before opening lesson. Flags any heading matching `/sources|references|bibliography/i` and any `<sup>` not wrapped in `<a>` (repeat citations must be a live superscript link, never a bare marker).
- `scripts/stamp_lesson.py`: stamp a lesson HTML from its YAML content (`references/lesson-schema.md`) + the stencil (`assets/lesson.stencil.html`, contract in `references/stencil-contract.md`) — stdlib, fails closed, repo paths only, diff stat; pair with `scripts/fixtures/stencil/run_stencil_tests.py` (stamped golden passes the gate; corrupt variants fail) and `run_parity_test.py` (row-id parity with the publisher).
- `scripts/check_map_geometry.py`: edge/box/label defects (edges through boxes, overlaps incl. node inside node, merged arrowheads, labels covering boxes); run before opening or publishing SVG visual.
- `scripts/verify_live.py`: probes published URLs for 200 + downloads live bytes for the Step 8 publish gate.
- `scripts/fixtures/`: fixture pages for `check_lesson.py`/`run_gate.py` (pass/fail HTML samples, `hub-home`, `index-home`) and for `stamp_lesson.py` (`fixtures/stencil/`: golden YAML + rendered workspace).
- `evals/fixtures/geom-fixture.html`: checker regression fixture: must report exactly one node-inside-node plus one label-on-box, everything else clean.
- `references/workflow.md`: workspace templates, treatise structure, glossary conventions.
- `references/lesson-schema.md`: YAML schema for a lesson's content, consumed by `stamp_lesson.py`.
- `references/stencil-contract.md`: the stamping contract + row-id rule between the YAML and `assets/lesson.stencil.html`.
- `references/sources/youtube.md`: YouTube adapter: fetch/slice commands, description mining, caption quirks, correction specifics.
- `references/sources/text-sources.md`: books/articles/papers/lecture-notes adapter: extraction, TOC segmentation, bibliography mining, OCR corrections.
- `references/diagram-spec.md`: visuals spec: cast map + timeline taxonomy, authoring rules, legends, QA gates.
- `references/publishing.md`: publish script flow, generic fallback, live verification.
- `references/page-design.md`: the single style doc — page structure, CSS class contract, typography/color tokens, casing rules.
- `assets/lesson.css`: canonical styles (font-pinned) to copy into each workspace.
- `assets/lesson.stencil.html`: the shape `stamp_lesson.py` fills from a lesson YAML.

## Quick start (fresh source)

Video:

```
python <skill>/scripts/extract_chapters.py "https://youtu.be/XXXX" --out <workspace>/reference/transcripts --chapters all --title
```

Text (book/article/paper/lecture notes): follow `references/sources/text-sources.md`'s acquisition steps for the source type at hand.

Then workspace, corrections, treatise, verification, visuals, publish, auto-open — identical for both.

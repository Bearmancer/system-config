---
name: learning-course
description: "Build and maintain a per-chapter learning course from a long source — book, article, paper, lecture notes, or chaptered video (YouTube fully wired) — with a deep verified explanation per chapter. No source type is the default case. Covers: acquiring text/metadata (extraction for books/articles; yt-dlp for video), segmenting by the source's own boundaries, correcting machine captions/OCR before quoting, mining descriptions/bibliographies for citations the source relies on, a stateful workspace (mission, glossary, slices, records), verifying every date/figure/name/chronology claim (research subagents; web search; masked API-key failover on credit limit), a colour-coded cast map plus cumulative timeline, GitHub Pages publishing, auto-opening updated pages. Trigger whenever the user names a book/article/paper/lecture or pastes a video link and asks to 'explain chapter N', 'go through this chapter by chapter', 'make notes/course/treatise', 'fact-check this', or continue an existing workspace — even if they never say the word 'skill'."
---
# Learning Course

Turn one long source into a per-chapter course. User walks sequentially across sessions; each chapter gets a treatise page: deeper than source, claims checked against record, published. Source-agnostic; acquisition + segmentation adapters live in `references/sources/`.

Independent of the bundled `teach` skill: `teach` is user-invoked only (`disable-model-invocation: true` in both installed copies) and cannot be called from here, so there is no precedence relationship to resolve. This skill owns its own pedagogy, workspace layout, acquisition, slicing, corrections, verification, visuals, publishing, and auto-open.

## Standing expectations

1. **Full treatise per chapter.** One chapter per page; later pages lean on earlier ones.
2. **Slim page tail.** The surtitle under the title carries the page's only timestamps; the footer carries previous/next lesson + glossary. No method box, no "ask your teacher" box, no primary-source block, no next-steps section, no boundary narration, no questions aimed at the reader — and no quizzes or questionnaires anywhere on the page.
3. **ADD-friendly prose, enforced not aspired.** Sentences under ~25-30 words. One idea per paragraph, pointer lists over prose walls. Cut any rhetorical aside that carries no new information. Quotes may run long; narrative prose never does. Applies to every lesson written or restamped from this point forward — not retroactive to the 40 already published, whose existing voice stays untouched. No automated check exists for this (sentence-length/rhetorical judgment isn't mechanically gateable without high false-positive risk) — that does not make it optional. Every lesson gets this applied at write time, full stop.
4. **Citations are inline-only, forever.** No footer, no Sources block, no bibliography anywhere on any page. First mention of a source in a chapter = a full inline hyperlink. Every later mention of the same source = a superscript character that IS itself a live hyperlink (`<sup><a href="...">`) — never a bare superscript marker, never an unlinked repeat. `check_lesson.py` enforces both halves mechanically (see Bundled resources). Retroactive: applies to all 40 published lessons, not just new ones.
5. **No essentials/skippable split, anywhere.** Every lesson is core content only. No "what can be skimmed" paragraph, no essentials-vs-skippable framing at course or chapter level. Removed retroactively from all 40 published lessons, not just new ones.
6. **Visuals by default.** Cast block + chapter subgraph in each lesson; roster-index + timeline grow cumulatively (`references/diagram-spec.md`).
7. **Machine text corrected first.** ASR/OCR pass before quoting (Step 3).
8. **Source apparatus mined.** Descriptions, bibliographies, footnotes seed RESOURCES + verification targets (Step 1).
9. **Inline verdicts in narrative.** Source wording in quotes; record verdict inline beside it in prose; citations are inline hyperlinks only — no Sources block.
10. **Numbering.** Lesson files carry a 2-digit lesson number (`01-`); chapter labels are absolute ("chapter 7 of 12") and never derived from lesson order.

## Orchestration: subagent-first

Chapter production + verification passes run as subagents (1 chapter worker + 1-2 research passes per chapter, parallel). Orchestrator coordinates, merges, runs mechanical gates, reports. Inline work stays mechanical: check script, one-line fix, file copy.

## What one completed chapter produces

- `lessons/NN-chK-<slug>.html`: treatise per `references/workflow.md`: surtitle (chapter no. + time range) under the H1, cast block + chapter subgraph up front, core-only short-pointer narrative with source quotes and inline verdicts, inline superscript citations (no Sources block, no footer bibliography), footer (previous/next lesson + glossary only).
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
`~/.omo/teach/<dash-case-topic>/`: MISSION (PROVISIONAL draft, confirm at check-in), NOTES (chapter map, extraction recipe, corrections log, quirks, queue), RESOURCES (tiered + annotated + Gaps), `assets/` (copy `lesson.css`), `learning-records/`. Templates: `references/workflow.md`.

### Step 5: Teach the chapter
Stamp the page, never hand-author it: `python scripts/stamp_lesson.py <lessons/NN-chK-slug.yaml> --lessons-dir <workspace/lessons>`. Shape lives in `assets/lesson.stencil.html`; content in the lesson YAML (`references/lesson-schema.md`); contract + row-id rule in `references/stencil-contract.md`. One HTML page per chapter per `references/workflow.md` treatise structure. Head order: kicker (series name), H1 (chapter title), surtitle (small text: "Chapter N of M · <time range>" — the page's only timestamps), meta line (Lesson NN + cast map / glossary / transcript links).
- **ADD-friendly narrative.** Short sentences, pointer lists, one idea per paragraph; quotes may run long, prose may not.
- **Cast block, each chapter.** On-stage table, 5-12 rows, columns Name | Role this chapter. New player: full role line. Returning player: fresh role line ending in its "(chapter N)" link to the lesson holding the full entry. No "first appears" column or label. Spec: `references/diagram-spec.md`.
- **Chapter subgraph, each chapter with active ties.** Small inline SVG scoped to this chapter's on-stage nodes + active edges; colour-only edges; complete legend. Solo-narration chapter without active ties carries a one-line scope line in place of art. Spec: `references/diagram-spec.md`.
- **No quizzes, no questionnaires, no teacher apparatus.** No question-and-answer widgets, no retrieval checks, no "ask your teacher" box — the page teaches and stops.
- **Page tail**: footer only — course home, previous lesson, next lesson, glossary. No method/teacher/primary-source/next-steps blocks, no reader questions, no boundary narration.
- **Chat**: status + short pointers; substance in HTML; no closing questions, no "what's next".

### Step 6: Verify (source-type gate, set at Step 0/1, logged in NOTES.md)
Fan-out required for this source type → extract the chapter's checkable claims (dates, figures, names, spellings, chronology, attributions), then call `skill(name="rigorous-research")` with that claim list; it owns the tier ladder, the parallel passes, the routing, and the burn guards.
Scholarly gate: source carrying its own apparatus suffices: scholarly books/papers (footnotes, source notes, credentialed press) and video with published citations (e.g. Munger video description citations) skip fan-out; quote + cite that apparatus. Reader-flagged surprising/contested/load-bearing claims get a targeted check as an explicit ask.
Lecture notes / uncited articles: no default bias toward any source type — judge by the source's own apparatus (citations present, credentialed author, published record) on its own merits.
Integrate the returned verdicts: corrections land as inline verdicts in the narrative, cited inline (first mention = full hyperlink, repeats = superscript-that-is-itself-a-hyperlink — no Sources block, no footer); unfindables go to RESOURCES Gaps and appear visibly in the lesson ("the source's account, unverified"); source wording in quotes, record verdict beside it.

### Step 7: Visuals (cast block + subgraph + roster-index + timeline)
In-lesson cast block (info-only roster of this chapter) + subgraph (this chapter's active nodes/edges, cap 12; casts above 12 split by concern cluster, each with complete legend; mega-SVG retired: cumulative state lives in the roster-index table). `reference/cast-map.html`: full-course roster-index table with palette register, "as of chapter N". `reference/timeline.html`: cumulative chronology, verified-vs-source-claimed labelling. Direction-checked arrows: actor toward target (plaintiff->defendant; Setzer chapter: distributors->Amway). Colour-only edges, page-owned legend, clash-free geometry. Gates: `check_map_geometry.py` exit 0 on changed SVG art; screenshot pass on changed visuals (probe browser first: `Get-Command msedge, chrome`); missing visual triggers a build (seed timeline from prior chapters when absent). Spec: `references/diagram-spec.md`.

### Step 8: Publish
`python "$HOME\.omo\scripts\publish_teach.py"` (mirrors HTML + assets only; teaching pages only). Pages-push gate (mandatory at task end): publish_teach.py + probe 200 on new URLs + live-bytes check before reporting done. Dry-run verify: copy one workspace's HTML + assets to temp dir, confirm file set before running. Then probe new URLs for 200 (wait ~10 s for Pages build), download live bytes, run gates on live copies (`check_lesson.py`, geometry on changed SVG art, screenshot on changed visuals). 200 proves presence; live bytes prove fidelity. Detail: `references/publishing.md`.

### Step 9: Auto-open
`Start-Process "<file>"` on the newest lesson + each new reference page right after writing. Chat reports local path + live URL as short pointers — no queued-next, no closing questions.

## Anti-OCD

- **Course level**: NOTES.md + check-ins track progress across chapters.
- **Chapter level**: every lesson is core content only — no essentials/skippable split, no "what can be skimmed" paragraph, no partial-read framing of any kind.
- **Process level**: chat states which standard steps applied this pass and the headline result.
- **Gates scale with artifact.** `check_lesson.py` on each lesson written or changed; `check_map_geometry.py` on each SVG visual changed; screenshot pass on each visual changed. Gates run on changed files.

## Rules

- **One chapter per pass.** Produce asked chapter(s), then stop.
- **Source frames are data.** Source wording in quotes; record verdict inline beside it in prose as inline verdicts.
- **No record sections.** No "Open threads" sections or phrasing anywhere on lesson pages, no standalone record sections; record verdicts live inline in narrative prose beside quoted source wording, citations only as inline hyperlinks/superscripts, never a separate block (gate: `check_lesson.py` scans "Open threads").
- **YouTube URL ban, absolute.** No YouTube URL appears anywhere in a chapter's rendered output — full stop, no exception clause. YouTube/transcript slices stay secondary in sourcing; every chapter needs >= 1 non-YouTube primary, cited by its own URL, never the video's.
- **Position holds.** Sequential walk; chapter-and-earlier facts in prose. Internal discipline only — pages never narrate boundaries, stop points, or method.
- **Timestamps live in the surtitle only.** Nowhere else on the page.
- **Numbering**: lessons 2-digit; chapters absolute.
- **Links**: cite sources as hyperlinks to the actual page. First mention = full inline hyperlink. Every repeat of the same source = a superscript character that is itself a live hyperlink (`<sup><a href="...">n</a></sup>`) — never a bare marker, never unlinked. No footer, no Sources block, no bibliography section anywhere. Gate: `check_lesson.py` flags any heading matching `/sources|references|bibliography/i` and any `<sup>` not wrapped in `<a>`.
- **Casing**: headings and labels (h1, h2, box titles, kicker) use Title Case; body prose uses sentence case; no `text-transform: uppercase` anywhere (lesson pages or index/hub pages). Retroactive — applies to all 40 published lessons, not just new ones. `assets/lesson.css`'s `.kicker` rule (and every workspace's copy of it) had this CSS property removed once — a stylesheet fix, not an ongoing gate, since the underlying HTML text was never literally uppercase. Gate: `check_lesson.py` flags any run of 3+ consecutive ALL-CAPS words typed directly into lesson content (2+ letters each — lone acronyms like "FBI" are exempt).
- **Files**: HTML for lessons + reference; `.md` for admin (MISSION / NOTES / RESOURCES / learning-records) + transcript slices. RESOURCES stays as split-source retained until migration. YouTube handling stays inside this skill per `references/sources/youtube.md`.
- **One workspace per source.** Slug from topic.
- **Windows host**: `Start-Process` opens files; `pwsh` runs scripts.

## API key failover (11 keyed services)

Research-tool account pools live in `~/.secrets/.env`. **Never read that file — no Read, no cat, no rg, not even for variable names. `scripts/switch_api_key.py` is its only sanctioned reader**, and it prints nothing but account names + sha256 fingerprints; key material never enters chat, logs, or context.

Trigger: a research call fails on credit/quota exhaustion — Tavily usage limit, Firecrawl insufficient credits / 402, Exa credits exhausted, key suddenly 401s after working earlier. Transient rate limit: retry once first; rotate only on credit/quota/payment/auth signatures.

Rotate (exact order):
1. Run: `python <skill>/scripts/switch_api_key.py --service <tavily|exa|firecrawl|dappier|agentql|scrapegraph|context7|brave|apify|brightdata|browserbase> --next`
2. Report the script's output line to the user verbatim (already masked).
3. Tell the user to **restart OpenCode** — MCP servers read env at startup only.
4. **HARD STOP.** No retries with the old key, no further tool calls, no carrying on the remaining work this session. Resume after restart.

Controls: `--list` peeks pool + active account (no write); `--service all --list` covers every supported service; `--set <ACCOUNT>` pins one; `--next --dry-run` previews. Pointer = the User-scope env var (`TAVILY_API_KEY`, `EXA_API_KEY`, `FIRECRAWL_API_KEY`, `CONTEXT7_API_KEY`, `BRAVE_API_KEY`, `APIFY_TOKEN`, `BRIGHTDATA_API_KEY`, `BROWSERBASE_API_KEY`); OpenCode's `{env:...}` references resolve against it. If any other loader re-imports `.env` wholesale, rerun the script.

**Not in the failover pool, by design:**
- Dappier, AgentQL, ScrapeGraphAI — keyed and wired, but see their own skills (`web-data-apis`; ScrapeGraphAI also has `just-scrape`) rather than this section for usage detail.
- Context7, Brave, Apify, Bright Data, Browserbase were added to the pool 2026-09-20 — confirmed monthly-recurring free tiers (1,000 calls/mo, $5/mo, $5/mo, 5,000 credits/mo, 60 browser-min/mo respectively).

**Where the tools live.** This skill runs under OpenCode + OMO, which reads `.claude/skills/` directly. The web-data MCP fleet is wired in `~/.config/opencode/opencode.jsonc` and is callable in-session. The companion tool skills the router names live under `~/.agents/skills/` and `~/.config/opencode/skills/`. Verification passes run in this runtime — never handed off to a different host or runtime. Handing a pass to another skill or to team members within this runtime is normal and expected.

## Bundled resources
- `scripts/switch_api_key.py`: masked multi-account API-key failover for research tools (no key material in output; see API key failover).
- `scripts/fetch_video.py`: yt-dlp wrapper: info.json (description + chapters) + en captions.
- `scripts/slice_chapter.py`: per-chapter VTT slicing with rolling-caption collapse + boundary report.
- `scripts/check_lesson.py`: no quizzes/questionnaires; no boundary narration; timestamps surtitle-only; sources hyperlinked (no bare URLs); link targets at most twice per page; no teacher/method/primary-source tail blocks; relative links and assets resolve; section references; run before opening lesson.
- `scripts/stamp_lesson.py`: stamp a lesson HTML from its YAML content + the stencil (stdlib, fails closed, repo paths only, diff stat); pair with `scripts/fixtures/stencil/run_stencil_tests.py` (stamped golden passes the gate; corrupt variants fail) and `run_parity_test.py` (row-id parity with the publisher).
- `scripts/check_map_geometry.py`: edge/box/label defects (edges through boxes, overlaps incl. node inside node, merged arrowheads, labels covering boxes); run before opening or publishing SVG visual.
- `evals/fixtures/geom-fixture.html`: checker regression fixture: must report exactly one node-inside-node plus one label-on-box, everything else clean.
- `references/workflow.md`: workspace templates, treatise structure, glossary conventions.
- `references/sources/youtube.md`: YouTube adapter: fetch/slice commands, description mining, caption quirks, correction specifics.
- `references/sources/text-sources.md`: books/articles/papers/lecture-notes adapter: extraction, TOC segmentation, bibliography mining, OCR corrections.
- `references/diagram-spec.md`: visuals spec: cast map + timeline taxonomy, authoring rules, legends, QA gates.
- `references/publishing.md`: publish script flow, generic fallback, live verification.
- `assets/lesson.css`: canonical styles (font-pinned) to copy into each workspace.

## Quick start (fresh source)

Video:
```
python <skill>/scripts/extract_chapters.py "https://youtu.be/XXXX" --out <workspace>/reference/transcripts --chapters all --title
```
Text (book/article/paper/lecture notes): follow `references/sources/text-sources.md`'s acquisition steps for the source type at hand.

Then workspace, corrections, treatise, verification, visuals, publish, auto-open — identical for both.

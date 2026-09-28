# Workflow — full detail

## Workspace discovery & creation

1. Search `~/Dev/deep-research` (`fd -t d --max-depth 1 . ~/Dev/deep-research`) before creating anything. One workspace per source; its slug names the source directory.
2. Topic slug: dash-case, content-based (`amway-tools-cult`, `putin-rise-to-power`); derive it from the topic.
3. Layout:
   ```
   ~/Dev/deep-research/<slug>/
   ├── NOTES.md              # chapter map, extraction recipe, corrections log, quirks, queue/standing
   ├── RESOURCES.md          # tiered sources, every entry annotated, + Gaps
   ├── assets/lesson.css     # copy from this skill's assets/ (font-pinned)
   ├── index.html            # course home — chapters + reference pages, linked from the root hub
   ├── lessons/01-ch2-slug.html
   ├── reference/glossary.html
   ├── reference/cast-map.html   # full-course roster/index (not a per-chapter reading aid)
   ├── reference/timeline.html
   ├── reference/transcripts/<chapter>-<range>.md
   └── learning-records/000N-slug.md
   ```
   Lesson filenames: `NN-chK-<slug>.html` — a **2-digit lesson number** (`01`, `02`, …) plus the **absolute chapter number** (`ch2` = the source's chapter 2). The lesson number is navigation order only; chapter labels never derive from it. `learning-records/` keeps its own sequence (admin log of sessions).

## NOTES.md essentials

- **Chapter map table** (from the source's own metadata — video `chapters[]`, book TOC — cross-checked with the description/introduction):
  ```
  | # | Time/Pages | Chapter | Essential? |
  |---|------------|---------|------------|
  | 1 | 00:00–06:26 | Intro & Road Map | yes |
  ```
- **Extraction recipe** (so any future session can re-derive): fetch command, slicing command, boundary rules, temp-dir location. Default extraction for video sources:
  ```
  python <skill>/scripts/extract_chapters.py "<video-url>" --out <workspace>/reference/transcripts --chapters all
  ```
  `--chapters all` is the default; narrow to a subset only for a re-run or a targeted pass. Ranges come from the video's own `info.json` metadata, so hand-typed ranges stay override-only.
- **Corrections log**: recurring garble patterns for this source (ASR mangling, OCR artifacts) and the canonical forms they resolve to.
- **Quirks**: caption lag, missing captions, edition/translation notes, machine-specific findings.
- **Queue & standing**: what's done (with date + fact-check headline) and what's still queued.

## RESOURCES.md tiers

`[C]` course source · `[B]` books · `[D]` documents/records · `[S]` press/scholarship · `[W]` wisdom/communities — plus explicit **Gaps** (unlocated primaries, unfindable claims). Annotate every entry with use + caution; mark entries the source itself cites (`cited by the source`) because those are the first verification targets. Label advocacy sources as advocacy; treat distributor-run wikis as a second source alongside a primary.

## The treatise (per-chapter lesson structure)

Page structure, casing, citation, timestamp, and stamp-contract rules: `references/course/page-design.md` (the single style + contract doc). Content-field contract: `references/course/lesson-schema.md`.

## The stencil (stamp-only lesson writing)

Lessons are stamped, never hand-authored. Shape lives in `assets/lesson.stencil.html`; content lives in `<workspace>/lessons/<NN>-chK-<slug>.yaml` (filename carries the chapter; stamp refuses names without `-chK-`).

- Stamp: `python scripts/stamp_lesson.py <lessons/NN-chK-slug.yaml> --lessons-dir <workspace/lessons>`
  — stdlib only, fails closed, writes repo paths only, prints a diff stat.
- Writer rule: **no hand-written lesson HTML.** A lesson task's report must
  carry the stamp output (repo path + diff stat + mtime) and the gate exit —
  self-reports without both are rejected at review.
- Tests: `python scripts/fixtures/stencil/run_stencil_tests.py` (stamped golden
  must pass the gate; every corrupt variant must fail with its rule tag) and
  `python scripts/fixtures/stencil/run_parity_test.py` (stamp and publisher
  derive identical row ids — drift alarm).
- Migration: courses moved from `~/.omo/teach` are restamped wholesale with the current shell; lesson prose keeps its voice, only the shell changes.


## Glossary conventions (glossary stays distinct from the cast map)

- The glossary page is `reference/glossary.html`, titled **Glossary** — canonical names + terms. The cast map is the relationship page; the two are never merged into one title ("Glossary & cast" is out).
- Header states the position: "as of chapter N", coverage sentence, "lessons must use these names".
- Canonical spellings, evidence-adjusted; canonical forms from the corrections pass land here; flag variants ("captions show 'Yeager'; canonical: Yager").
- Sections by domain (company / roles / practice / people / lineage). Update once per chapter or when new players arrive.
- Entry pattern: **Term** — one-paragraph definition, source-vs-record notes inline where a check changed the wording.

## Learning records

Write one when the position advances with new insight, a verification norm emerges, or the user's preferences crystallize (depth, diagrams, method transparency). Format: title + standing + 1–3 sentences + evidence + implications. Verification findings use the per-chapter verdict format: claim → verdict (confirmed / partially correct / wrong / unfindable) → URL → quote, one line per claim.

## Standing behaviours

- **Subagent-first.** Chapter production and the verification passes run as subagent tasks; the orchestrating session coordinates, runs the mechanical gates, and merges results. Substantive work happens in subagents; the orchestrator holds coordination.
- **Stay at the user's chapter position.** Teach chapter-and-earlier facts only — as internal discipline; the page itself never narrates the boundary.

Gates, chat/report etiquette, publish, and auto-open: `references/modes/course.md` Steps 6-9 and `references/course/publishing.md`.

## Sandbox / eval runs

Test mode: copy the existing workspace into the outputs folder; write everything for the task into **one tree** (outputs root, or one named subfolder — pick one, keep the whole task inside it). Two trees for one workspace = the recurring failure mode here.

Pre-existing files in the outputs folder you didn't create this session: leave untouched, say so in the report (usually residue from an earlier/sibling attempt; deleting someone else's evidence is worse than leaving it). Own earlier partial tree: state plainly which tree is the deliverable.

Confine all writes to the outputs tree; leave `~/Dev/deep-research` untouched; publish/open steps are for live runs only.

# Workflow — full detail

## Workspace discovery & creation

1. Search `~/.omo/teach` (`fd -t d . ~/.omo/teach`) before creating anything. One workspace per source; its `MISSION.md` names the source and the user's position.
2. Topic slug: dash-case, content-based (`amway-tools-cult`, `putin-rise-to-power`); derive it from the topic.
3. Layout:
   ```
   ~/.omo/teach/<slug>/
   ├── MISSION.md            # provisional from first request; confirm at check-in
   ├── NOTES.md              # chapter map, extraction recipe, corrections log, quirks, queue/status
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
- **Queue & status**: what's done (with date + fact-check headline) and which chapters are skippable.

## MISSION.md (provisional pattern)

Keep to a screen: Why (the user's real goal, best guess), Success looks like, Constraints (sequence discipline, terse chat, verification norm), Out of scope. Mark `Status: PROVISIONAL — drafted from the first request`, and confirm when the user is next around.

## RESOURCES.md tiers

`[C]` course source (the spine) · `[B]` books · `[D]` documents/records · `[S]` press/scholarship · `[W]` wisdom/communities — plus explicit **Gaps** (unlocated primaries, unfindable claims). Annotate every entry with use + caution; mark entries the source itself cites (`cited by the source`) because those are the first verification targets. Label advocacy sources as advocacy; treat distributor-run wikis as a second source alongside a primary.

## The treatise (per-chapter lesson structure)

Page head: kicker (series name) → H1 (chapter title) → **surtitle** — small text under the title, `Chapter N of M · <time range>`; this is the page's **only** place for timestamps — → meta line (`Lesson NN` + links: cast map · glossary · transcript slice).

Numbered sections, in this order (adapt; keep ~8–10 sections):

1. What the chapter does — lead paragraph, the chapter's argument.
2. **Cast block** — info-only table of who's on stage this chapter: 5–12 rows, columns **Name | Role this chapter**. New player = full role line. Returning player = fresh role line for this chapter ending in its "(chapter N)" link to the lesson that holds the full entry; that chapter number is absolute. No "first appears" column, no continuity claims. The full-course roster lives at `reference/cast-map.html`.
3. **What matters — and what you can skip** — 2–4 essentials for the mission, then the parts that can be skimmed or were abstracted away. This block is the user's explicit anti-OCD ask; include it in every chapter.
4. The narrative — following the chapter, its own quotes in blockquotes (post-corrections), with inline verdicts beside the quoted wording in prose: source wording in quotes, record verdict inline next to it (confirmed / corrected / unfindable, in the sentence — never a separate box). **ADD-friendly**: short sentences, pointer lists, one idea per paragraph; quotes may run long, prose may not.
5. The machinery — what the chapter establishes structurally (the mechanism at work: a relationship, a method, an institution — whatever the chapter's own throughline is; frame it in the chapter's own terms).
6. The Sources block — the per-chapter Sources block: every checked claim's hyperlinked citations live here, each as a hyperlink to the actual page (no bare URLs, no unlinked citations). Max-twice hyperlink rule: each link target appears at most twice per page, once in context and once in the Sources block. Corrections already stated as inline verdicts in the narrative point here; unfindables read "the source's account, unverified" in narrative and land in RESOURCES Gaps too. RESOURCES stays split-source retained until migration.
7. Footer — navigation only: course home · previous lesson · next lesson · glossary. Nothing after the footer and nothing else in the tail: no method box, no "ask your teacher" box, no primary-source paragraph, no next-steps block, no anchors line, and no quizzes/questionnaires anywhere on the page.

## The stencil (stamp-only lesson writing)

Lessons are stamped, never hand-authored. Shape lives in the template; content
lives in YAML.

- Template: `assets/lesson.stencil.html` (fixed section order, fixed footer).
- Schema + golden + corrupt-variant list: `references/lesson-schema.md`.
- Contract (owners, row-id rule, parity test): `references/stencil-contract.md`.
- Stamp: `python scripts/stamp_lesson.py <lessons/NN-chK-slug.yaml> --lessons-dir <workspace/lessons>`
  — stdlib only, fails closed, writes repo paths only, prints a diff stat.
- Content: one `<workspace>/lessons/<NN>-chK-<slug>.yaml` per lesson. The
  filename carries the chapter; the stamp refuses names without `-chK-`.
- Writer rule: **no hand-written lesson HTML.** A lesson task's report must
  carry the stamp output (repo path + diff stat + mtime) and the gate exit —
  self-reports without both are rejected at review.
- Tests: `python scripts/fixtures/stencil/run_stencil_tests.py` (stamped golden
  must pass the gate; every corrupt variant must fail with its rule tag) and
  `python scripts/fixtures/stencil/run_parity_test.py` (stamp and publisher
  derive identical row ids — drift alarm).
- Migration: option **B, on-touch** — new lessons stamp; an existing lesson is
  restamped when it is next edited. No wholesale backfill until a 3-lesson
  pilot yields a per-lesson cost.

## Verification fan-out pattern
Moved. The tier ladder, parallel-pass contract, pass budget, burn guards, and all source-selection rules (apparatus-first, preference ordering, pairing, advocacy labelling, attribution hygiene) now live in the `rigorous-research` skill; tool selection lives in `web-data-apis`; API-key credit failover is in this skill's own "API key failover" section (SKILL.md), which owns switch_api_key.py. The scholarly-gate exemption — a source carrying its own citation apparatus skips fan-out — is stated in SKILL.md Step 6.

## Glossary conventions (glossary stays distinct from the cast map)

- The glossary page is `reference/glossary.html`, titled **Glossary** — canonical names + terms. The cast map is the relationship page; the two are never merged into one title ("Glossary & cast" is out).
- Header states the position: "as of chapter N", coverage sentence, "lessons must use these names".
- Canonical spellings, evidence-adjusted; canonical forms from the corrections pass land here; flag variants ("captions show 'Yeager'; canonical: Yager").
- Sections by domain (company / roles / practice / people / lineage). Update once per chapter or when new players arrive.
- Entry pattern: **Term** — one-paragraph definition, source-vs-record notes inline where a check changed the wording.

## Learning records

Write one when the position advances with new insight, a verification norm emerges, or the user's preferences crystallize (depth, diagrams, method transparency). Format: title + Status + 1–3 sentences + evidence + implications. Verification findings use the per-chapter verdict format: claim → verdict (confirmed / partially correct / wrong / unfindable) → URL → quote, one line per claim.

## Chat etiquette

Terse status/pointers; the substance lives in the pages. Report as short lines: page path, live URL, the one or two headline fact-check findings. No queued-next lines, no closing questions, no offers to continue. Mention any standard step skipped as unnecessary (optionality rule) — as a statement, not a question.

## Standing behaviours

- **Subagent-first.** Chapter production and the verification passes run as subagent tasks; the orchestrating session coordinates, runs the mechanical gates, and merges results. Substantive work happens in subagents; the orchestrator holds coordination.
- **Gates scale with the artifact.** (1) `check_lesson.py` on any lesson written or changed → exit 0 (no quizzes/questionnaires; no boundary narration; timestamps surtitle-only; hyperlinked sources with no bare URLs; max-twice hyperlink rule; no teacher/method/primary-source tail blocks; links and assets resolve; dangling section references). (2) `check_map_geometry.py` on any SVG visual changed → exit 0 (edges through boxes, box overlaps including a node drawn inside another node, merged arrowheads, labels covering a box they do not belong to; label-on-line warnings reviewed and fixed when they matter) — and after editing the checker itself, re-run it on `evals/fixtures/geom-fixture.html`, which must report exactly one box overlap and one label-on-box. (3) A screenshot of any changed visual, looked at — keep the window height ≤2400, quote the `--window-size` value, verify the PNG is not a 756x488 fallback, and use iframe bands for long pages (details in `references/diagram-spec.md`). Each gate exists because a defect class shipped past the others: stray timestamps, edges through boxes, merged arrowheads, caption overflow, wrong cross-reference targets.
- **Auto-open** every newly written/updated page (`Start-Process <file>`).
- **Publish** when a teaching task completes (`~/.omo/scripts/publish_teach.py`), probe new URLs for 200, and on later visits verify the live bytes alongside the status code. Report without queued-next lines.
- **Stay at the user's chapter position.** Teach chapter-and-earlier facts only — as internal discipline; the page itself never narrates the boundary.

## Sandbox / eval runs

When told to work in test mode: copy the existing workspace into the outputs folder and write everything for the task into **one tree** — either directly at the outputs root or in a single named subfolder; pick one and keep the whole task inside it. A second copy of the same workspace is the most common artifact problem in these runs: three of six continuation runs in the 2026-09 eval batches produced two trees, and every one of them then spent time reconciling or cleaning them.

If files are already in the outputs folder that you did not create this session, leave them untouched and say so in your report — they are usually residue from an earlier attempt of the same task or from a sibling run, and deleting someone else's evidence is worse than leaving it. If your own earlier attempt left a partial tree, say plainly which tree is the deliverable so nobody has to guess.

Throughout: confine all writes to the outputs tree; leave `~/.omo/teach` untouched and the publish/open steps for live runs.

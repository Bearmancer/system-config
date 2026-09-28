# Course mode

One source or topic becomes a per-chapter course. Each chapter = one treatise page: deeper than source, claims checked against record, published to GitHub Pages. Source-agnostic; acquisition adapters in `references/course/sources/`.

Paths: course data `~/Dev/deep-research/<slug>/`; video cache `~/.cache/deep-research/video/<id>/` (transient); pages clone `~/Dev/bearmancer.github.io`. Windows host: `Start-Process` opens files; `pwsh` runs scripts.

## Page standards: every lesson

1. One chapter per page; later pages lean on earlier ones.
2. Slim tail. No timestamps anywhere, surtitle included. Footer = previous/next lesson only. Top bar (loft variant A) holds title, index dropdown, font/size menus. No method box, teacher box, primary-source block, next-steps section, boundary narration, reader questions, quizzes.
3. ADD-friendly prose at write time: sentences under ~25-30 words, one idea per paragraph, pointer lists over walls, no rhetorical aside without new information. Quotes may run long. Restamping migrated lessons keeps their prose voice.
4. Citations inline only. No Sources block, footer bibliography, or heading matching sources/references/bibliography. First mention = full inline hyperlink; later mentions = `<sup><a href="...">` live link, never bare marker. `check_lesson.py` enforces.
5. Core content only. No essentials/skippable split, no "what can be skimmed".
6. Visuals only with explicit non-empty `cast`: cast block + chapter subgraph; roster-index + timeline grow cumulatively. `cast: []` omits §2, no renumbering. Spec: `references/course/diagram-spec.md`.
7. Machine text corrected before quoting (Step 3).
8. Source apparatus mined (Step 1).
9. Source wording in quotes; record verdict inline beside it in prose. No "Open threads" section or standalone record section.
10. Lesson files carry 2-digit lesson number (`01-`); chapter labels absolute ("chapter 7 of 12"), never derived from lesson order.
11. Casing: headings, labels, kicker in Title Case; body sentence case; no `text-transform: uppercase` anywhere. `check_lesson.py` flags 3+ consecutive ALL-CAPS words (lone acronyms exempt).
12. YouTube URL ban, absolute: no YouTube URL in rendered output. Every chapter needs >= 1 non-YouTube primary cited by its own URL.

## Steps

0. Locate. `fd -t d --max-depth 1 . ~/Dev/deep-research`; one workspace per source, slug from topic. Deep-link timestamp = user position. Topic input without source: research candidate chapter list (SKILL.md passes), put syllabus to user via AskUserQuestion, build nothing until approved. Done when workspace path + approved chapter list exist.
1. Acquire source + apparatus. Text: `references/course/sources/text-sources.md`. Video: `python <skill>/scripts/fetch_video.py "<url>"` (writes `info.json` with description + `chapters[]`, `subs.en.vtt`); quirks `references/course/sources/youtube.md`. Pick adapter by what was given. Apparatus citations seed RESOURCES + verification. Done when text + apparatus cached.
2. Segment. `python <skill>/scripts/extract_chapters.py <url> --out <workspace>/reference/transcripts --chapters all` (`--dry-run` previews, `--list` prints table). `slice_chapter.py` = hand-range override only. No boundaries in source: ask user. Recipe logged in NOTES.md. Done when every chapter has a slice.
3. Correct machine text. Candidate list from metadata + glossary + domain; log `heard -> corrected -> basis` in slice; canonical forms to glossary; ambiguous garble kept + flagged; numbers carry second witness. Done when every quoted line is corrected.
4. Workspace. NOTES, RESOURCES (tiered, annotated, Gaps), `assets/` (copy `<skill>/assets/lesson.css`), `learning-records/`. Templates: `references/course/workflow.md`. Done when layout matches workflow.md.
5. Stamp each chapter, never hand-author: `python <skill>/scripts/stamp_lesson.py <lessons/NN-chK-slug.yaml> --lessons-dir <workspace>/lessons`. Content in YAML (`references/course/lesson-schema.md`); shape in `assets/lesson.stencil.html`; contract in `references/course/page-design.md`. Cast block: 5-12 rows, Name | Role this chapter; returning player's role line ends in "(chapter N)" link. Subgraph only with active ties among explicit cast. Done when every chapter stamped.
6. Verify. Source carrying own apparatus (scholarly book/paper, credentialed press, video with published citations): quote + cite apparatus, skip fan-out; reader-flagged or load-bearing claims still get targeted check. Otherwise extract checkable claims (dates, figures, names, spellings, chronology, attributions) and run SKILL.md passes. Corrections land as inline verdicts; unfindables go to RESOURCES Gaps and show in lesson as "the source's account, unverified". Gate logged in NOTES.md. Done when every claim has a verdict.
7. Visuals. Cast block + subgraph per lesson (cap 12 nodes; split larger casts by concern, each with full legend). `reference/cast-map.html` roster-index "as of chapter N"; `reference/timeline.html` cumulative, verified vs source-claimed labelled. Arrows actor -> target; colour-only edges; page-owned legend. Done when `check_map_geometry.py` exits 0 on changed SVG and screenshot pass clean (probe browser first: `Get-Command msedge, chrome`).
8. Publish. Dry run: copy one workspace's HTML + assets to temp, confirm file set. Then `python <skill>/scripts/publish_teach.py` (HTML + assets only). Probe new URLs for 200 (Pages build ~10 s+; wait via monitor), `python <skill>/scripts/verify_live.py <workspace> <site-url>` downloads live bytes, rerun gates on live copies. Done when live bytes pass gates.
9. Open every new/updated page, each by its own `Start-Process "<file>"`. Chat: local path + live URL, short pointers, no closing questions.

## Gates: changed files only

- `check_lesson.py` per page written or changed (lesson/index/reference mode by path).
- `check_map_geometry.py` per SVG visual changed.
- Screenshot pass per visual changed.

## Progress

- Full course per pass: produce every chapter, then stop.
- Sequential position: chapter-and-earlier facts only; pages never narrate the boundary.
- NOTES.md tracks progress across sessions; chat states which steps ran + headline result.
- HTML for lessons + reference; `.md` for NOTES, RESOURCES, learning-records, transcript slices.

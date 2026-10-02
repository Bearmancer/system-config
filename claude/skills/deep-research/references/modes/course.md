# Course mode

One source or topic becomes a per-chapter course: one chapter at a time, in order, each building on the last. Each chapter = one treatise page: deeper than source, claims checked against record, published to GitHub Pages. Source-agnostic; acquisition adapters in `references/course/sources/`.

Paths: site repo `~/Dev/bearmancer.github.io`; `<site>` = `~/Dev/bearmancer.github.io/<slug>/` (published pages, `assets/`); `<work>` = `~/Dev/bearmancer.github.io/work/<slug>/` (NOTES, RESOURCES, learning-records, transcript slices; gitignored); video cache `~/.cache/deep-research/video/<id>/` (transient). Windows host: `Start-Process` opens files; `pwsh` runs scripts.

## Page standards: every lesson

1. One chapter per page; later pages lean on earlier ones.
2. Slim page. H1 = chapter name alone: no kicker, surtitle, "Chapter N of M", date, timestamps. Footer = previous/next lesson only. Bar = topic name (links course index), chapter dropdown, `Aa` text settings; index/hub pages carry Topic + Chapter pickers. No method box, teacher box, primary-source block, next-steps section, boundary narration, reader questions, quizzes.
3. Prose per SKILL.md Voice, ADD-friendly at write time: sentences under ~25-30 words, paragraphs that build one line of thought, pointer lists over walls, no rhetorical aside without new information. Quotes may run long. Restamping migrated lessons keeps their prose voice.
4. Citations = hyperlink on the words that name the source. No `<sup>`, numeral or "here" link text, reference list, or heading matching sources/references/bibliography. `check_lesson.py` enforces.
5. Core content only. No essentials/skippable split, no "what can be skimmed".
6. Visuals: chapter `diagram` only when the chapter has relationships to draw (layout computed, geometry-gated); course-level `reference/cast-map.html` only for a long-running narrative, listing only its important recurring people; `reference/timeline.html` cumulative. Cast, Glossary, Timeline are reached from the course index. Spec: `references/course/diagram-spec.md`.
7. Machine text corrected before quoting (Step 3).
8. Source apparatus mined (Step 1).
9. Source wording in quotes; a correction folds into the sentence where the fact appears, cited by link. No verification narration ("confirmed against", "verified"), correction ledger, meta framing, "Open threads" or standalone record section. Headings unnumbered; no "Machinery" heading; a Summary only in a chapter of 1200+ words.
10. Lesson files carry a 2-digit lesson number (`01-`) plus the absolute source chapter (`ch7`). The course index row reads `N · name` with `N` = lesson number, consecutive; `chK` is the row id only. Merge two short source chapters into one lesson when it reads better (filename carries the first chapter).
11. Casing: headings and labels in Title Case; body sentence case; no `text-transform: uppercase` anywhere. `check_lesson.py` flags 3+ consecutive ALL-CAPS words (lone acronyms exempt).
12. YouTube URL ban, absolute: no YouTube URL in rendered output. Every chapter needs >= 1 non-YouTube primary cited by its own URL.

## Steps

0. Locate. `fd -t d --max-depth 1 . ~/Dev/bearmancer.github.io/work` plus published dirs `fd -t d --max-depth 1 . ~/Dev/bearmancer.github.io`; one workspace per source, slug from topic. Deep-link timestamp = user position. Topic input without source: research candidate chapter list (SKILL.md passes), put syllabus to user via AskUserQuestion, build nothing until approved. Done when workspace path + approved chapter list exist.
1. Acquire source + apparatus. Text: `references/course/sources/text-sources.md`. Video: `python <skill>/scripts/fetch_video.py "<url>"` (writes `info.json` with description + `chapters[]`, `subs.en.vtt`); quirks `references/course/sources/youtube.md`. Pick adapter by what was given. Apparatus citations seed RESOURCES + verification. Done when text + apparatus cached.
2. Segment. `python <skill>/scripts/extract_chapters.py <url> --out <work>/reference/transcripts --chapters all` (`--dry-run` previews, `--list` prints table). `slice_chapter.py` = hand-range override only. No boundaries in source: ask user. Recipe logged in NOTES.md. Done when every chapter has a slice.
3. Correct machine text. Candidate list from metadata + glossary + domain; log `heard -> corrected -> basis` in slice; canonical forms to glossary; ambiguous garble kept + flagged; numbers carry second witness. Done when every quoted line is corrected.
4. Workspace. `<work>`: NOTES, RESOURCES (tiered, annotated, Gaps), `learning-records/`; `<site>`: `assets/` (copy `<skill>/assets/lesson.css`). Templates: `references/course/workflow.md`. Done when layout matches workflow.md.
5. Stamp each chapter, never hand-author: `uv run <skill>/scripts/stamp_lesson.py <lessons/NN-chK-slug.yaml> --lessons-dir <site>/lessons` (PEP 723 header pulls `pyyaml`). Content in YAML (`references/course/lesson-schema.md`); shape in `assets/lesson.stencil.html`; contract in `references/course/page-design.md`. Optional `diagram` mapping for relationships. Done when every chapter stamped.
6. Verify. Source carrying own apparatus (scholarly book/paper, credentialed press, video with published citations): quote + cite apparatus, skip fan-out; reader-flagged or load-bearing claims still get targeted check. Otherwise extract checkable claims (dates, figures, names, spellings, chronology, attributions) and run SKILL.md passes. Corrections fold into the prose where the fact appears; unfindables go to RESOURCES Gaps and read in the lesson as the source's own account. Gate logged in NOTES.md. Done when every claim has a verdict.
7. Visuals. `diagram` per lesson where relationships matter (up to 2 per chapter, cap 12 nodes each; colour = relationship type, only for types repeating 2+ times; arrows actor -> target; solid lines). `reference/cast-map.html` for important recurring people only; `reference/timeline.html` cumulative, source-claimed dates labelled. Done when `check_lesson.py` (geometry gate) passes and the screenshot pass is clean (probe browser first: `Get-Command msedge, chrome`).
8. Publish. Dry run: `python <skill>/scripts/publish_teach.py --no-push` (builds indexes in the site repo, no commit). Then `python <skill>/scripts/publish_teach.py` (commit + push of the site repo only). Probe new URLs for 200 (Pages build ~10 s+; wait via monitor), `python <skill>/scripts/verify_live.py <site> <site-url>` downloads live bytes, rerun gates on live copies. Done when live bytes pass gates.
9. Open every new/updated page, each by its own `Start-Process "<file>"`. Chat: local path + live URL, short pointers, no closing questions.

## Gates: changed files only

- `check_lesson.py` per page written or changed (lesson/index/reference mode by path).
- `check_map_geometry.py` per hand-edited SVG (stamped diagrams already pass through `check_lesson.py`).
- Screenshot pass per visual changed.

## Progress

- Full course per pass: produce every chapter, then stop.
- Sequential position: chapter-and-earlier facts only; pages never narrate the boundary.
- NOTES.md tracks progress across sessions; chat states which steps ran + headline result.
- HTML for lessons + reference in `<site>`; `.md` for NOTES, RESOURCES, learning-records, transcript slices in `<work>`.

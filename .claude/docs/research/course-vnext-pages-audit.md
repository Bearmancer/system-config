# Course pages audit for the vNext rebuild

## Question

Issue #57 (Refs #55, the "deep-research course vNext" map) asks: which Bearmancer course pages exist now, which were deleted or reverted, and which of each need a rebuild under the vNext rules? For every live lesson it also asks for the vNext violations. This document answers that, as of 2026-09-30, from `Bearmancer/bearmancer.github.io` at `105c42e` (main), the then-private `Bearmancer/deep-research` repo at `35b0de6` (main), and the local workspaces in `C:\Users\Lance\Dev\deep-research\`.

The rules used are the signed captain directives listed in issue #55 (letters d, h, i, j, k, l, n, o, q, s) plus the checks listed in issue #57. Where a directive and a check name the same thing, both are counted once.

## Answer in brief

- Three courses are live: Afghanistan, Ark Nova, and Russia. All three violate the vNext rules and all three have their sources on hand, so all three should be rebuilt.
- Nine courses were deleted (six in one publish, `e3d6838`). None has a workspace or a copy in `deep-research`, so no course has its raw sources on hand. The published pages are still recoverable from git. Two courses (Amway, Watergate) name a YouTube video id and can be rebuilt from it; the other seven cannot until a source is identified or supplied.
- The two reverts (`34a19d2`, `c83ada7`) hit answer pages (a verdict and a recommendation), not courses. They are outside the course rebuild.
- `orchestral-instruments` is an empty scaffold: three empty folders in the workspace, nothing in the site repo, never committed.

## Course table

Status is as of `105c42e`. "Sources on hand" is y only when the raw source (transcript or book text) is available locally or in `deep-research`; an old page in git does not count, and neither does a source that could be re-fetched. The rebuild column follows the destination text in issue #55: every course worth keeping "where sources exist". Where sources are on hand or a named video id makes them re-fetchable the answer is y; otherwise n, and the reason says what would flip it. "Violations" counts are grep-based (method and limits below).

| Course | Status | Sources on hand | Violations found | Rebuild? |
|---|---|---|---|---|
| `afghanistan-turning-against-taliban` (7 lessons) | Live | y. Workspace and `deep-research` identical (`diff -rq --strip-trailing-cr`, 0 differences); 7 files under `reference/transcripts/` | 22 numbered headings; 7 "Chapter N of 7"; 7 "Machinery" sections; 7 Summary sections on lessons averaging 6.1 KB; 52 bold verification tags; 1 sup-plus-link citation; 1 "Cast" section that is an SVG, not a table; 0 trailing Corrections; 0 lesson date stamps | y. Every lesson carries the structural violations; only 43,046 bytes of lessons, so the rebuild is cheap |
| `ark-nova` (8 lessons) | Live | y. Workspace and `deep-research` identical; 8 transcript files | 24 numbered headings; 8 "Chapter N of 8"; 8 "Machinery"; 8 Summary sections on lessons averaging 5.9 KB; 6 of 8 summaries in second person; 26 verification tags; 3 sup-plus-link citations; 0 Cast tables; 0 Corrections; 0 date stamps | y. It is a rules course, so shape it with the board-game work (map #56, sources ticket #64) rather than the explanation-course template |
| `russia-military-morale-crisis` (14 lessons) | Live | y. Workspace and `deep-research` identical; 14 transcript files plus `full-attempt/` and `new-sources/` folders | 54 numbered headings; 14 "Chapter N of 14"; 14 "Machinery" sections that each open "The chapter works"; 12 Cast tables with 23 rows, 8 of them generic or unnamed groups; 6 trailing "Corrections:" paragraphs; 7 date-stamp paragraphs ("Tier2 verdicts observed 2026-09-29"); 14 Summary sections on lessons averaging 4.9 KB; 9 sup-plus-link citations, 5 repeating a URL already linked in the same paragraph; 85 verification tags | y. It has every violation on the list and is the largest live course (68,010 bytes). Also stop publishing `reference/transcripts/full-attempt/transparrot_page.html`, a raw scrape on the live site |
| `fascism-american-discourse` (3 lessons) | Deleted in `e3d6838` (last live `7b4351c`) | n. No workspace, not in `deep-research` | At `7b4351c`: 3 "Chapter N of 3"; 19 numbered headings; superscript footnotes with backlinks; no Cast or Machinery headings | n. No source ids survive on the pages; the footnotes name published works (for example Rosenfeld and Ward), so this flips to y if the captain wants those re-collected. It was the most carefully cited course (`ebbc59a..7b4351c`) |
| `control-story` (13 lessons) | Deleted in `e3d6838` | n | At `7b4351c`: 52 numbered headings; 13 "Chapter N of 13"; 13 Machinery headings; 13 Cast headings (table entries not inspected) | n. No source id or title found on the pages by a `git grep` for YouTube ids, "Video:" lines and author names |
| `historians-on-trump` (8) | Deleted in `e3d6838` | n | At `7b4351c`: 32 numbered headings; 8 "Chapter N of 8"; 8 Machinery; 8 Cast headings; 6 files with superscript notes | n. Sources were several outlets' transcripts (glossary text names NYT, C-SPAN, MTP), with no single id to re-fetch |
| `political-spectrum` (1) | Deleted in `e3d6838` | n | At `7b4351c`: 4 numbered headings; 1 "Chapter N of 1"; Machinery and Cast headings; 1 verification-narration phrase | n. One lesson, no source identified |
| `soviet-afghan-war` (3) | Deleted in `e3d6838` | n | At `7b4351c`: 12 numbered headings; 3 "Chapter N of 3"; 3 Machinery; 3 Cast headings; 109,342 bytes of lessons | n. No source identified on the pages |
| `stalin-red-tsar` (1, chapter 14) | Deleted in `e3d6838` | n | At `7b4351c`: 4 numbered headings; 1 "Chapter N of 1"; Machinery and Cast headings | n. The kicker names the book "Stalin: The Court of the Red Tsar"; no text is on hand, so it flips to y only if the book text is supplied |
| `amway-tools-cult` (7 of 12 chapters) | Deleted in `d42aca7` (last live `9cc8514`) | n on hand; the old index names YouTube id `P9nA3pqSaf8` (Sean Munger) | At `9cc8514`: 55 numbered headings; 7 "Chapter N of 12"; 6 files with "confirmed against" or "verified against" narration; 7 tables | y. The video id makes the source re-fetchable |
| `watergate-geographic-history` (8, chapters 5 to 12 of 12) | Deleted in `1a1e4d8` (last live `be11360`) | n on hand; old pages link YouTube id `GUmLe8YtIck` (Sean Munger) | At `be11360`: 48 numbered headings; 8 "Chapter N of 12"; 8 Cast headings; 1 trailing Corrections | y. Re-fetchable by video id; chapters 1 to 4 were never covered, so a rebuild can finish it |
| `putin-rise-to-power` (12, chapters 7 to 18 of 18) | Deleted in `f31abdf` and `0067f88` (last live `859b841`) | n | At `859b841`: 85 numbered headings; 12 "Chapter N of 18"; 12 Cast headings; 10 Machinery; 5 trailing Corrections | n. Pages cite a video by timestamp (for example 55:00 to 1:04:57) but no id or URL was found; flips to y once the video is identified. Largest deleted course (330,363 bytes of lessons) |
| `orchestral-instruments` | Never published | n. Empty scaffold (`assets`, `learning-records`, `reference`, no files) in the workspace; `git log -- orchestral-instruments` in the site repo is empty | Nothing to check | n. Nothing exists to rebuild; a new course if wanted |
| `answers/verdict-is-the-eiffel-tower-in-paris.html` | Reverted (`34a19d2` reverts `9804fbb`) | n. The page embeds its own evidence; no course sources | Not a course. The page carried a date line under the title (`2026-09-30`) | n. Outside course mode |
| `answers/recommend-deep-cut-19th-century-symphonies-berwald-farrenc-beach.html` | Reverted (`c83ada7` reverts `abe9bd3`) | n. No course sources | Not checked against course rules | n. Outside course mode |
| `worktree-locking` | Deleted in `1edcb7a` | n | Only two asset files (`assets/quiz.js`, `assets/teach.css`) were removed; no pages | n. A workspace remnant, not a course |

Deleted-course rows count headings that exist, not whether their entries are minor mentions; the Cast and Machinery counts there are heading counts only.

## Page-level violations (site, not lesson)

- The root `index.html` at `105c42e` labels the course table column "Book / Video" (line 43). Directive s changes it to "Topic".
- The same page carries a date stamp line: "Published from the local course workspaces · 2026-09-30 12:42" (line 41).
- Course index pages list chapters as bare "ch1", "ch2" links (checked in `russia-military-morale-crisis/index.html`, `afghanistan-turning-against-taliban/index.html`, and `ark-nova/index.html`) rather than chapter names. Directive d says the chapter header is the chapter name alone; the index labels are the same problem in another place.

## How the courses disappeared

- `e3d6838` ("Publish courses 2026-09-29 06:58") removed 61 files across six courses (control-story, fascism-american-discourse, historians-on-trump, political-spectrum, soviet-afghan-war, stalin-red-tsar) while adding or rewriting the Afghanistan and Russia pages. The commit message gives no reason.
- `claude/skills/deep-research/references/course/publishing.md` line 12 says the publish script mirrors `~/Dev/deep-research/*` HTML and assets to the site copy. The most likely reading is that a course whose workspace is gone from `deep-research` drops off the site on the next publish. That fits the six-course deletion and the shape of the private repo: its first commit `3a4500e` (2026-09-29) holds only Afghanistan and Russia, and `35b0de6` (HEAD) holds those two plus Ark Nova. This is inference, not confirmed (see Unverified).
- `d42aca7` (Amway) has the same form as `e3d6838`, a "Publish teaching docs" commit that removes files, so it belongs with the inferred-prune group, not the deliberate one.
- Three deletions carry an explicit message: `1a1e4d8` ("Remove Watergate geographic history teach"), `f31abdf` ("Delete putin-rise-to-power directory"), and `0067f88` ("Remove putin-rise-to-power topic (20 files) + index row").
- The two reverts are 34a19d2 and c83ada7, made at 10:56 on 2026-09-30, about an hour after their publishes (`9804fbb` at 09:45, `abe9bd3` at 09:46). The live warfronts verdict page is `105c42e`.

## Recommendation

1. Rebuild the three live courses first: sources are on hand, they are the only courses visitors can see, and together they hold all of the violation types.
2. Rebuild Amway (`P9nA3pqSaf8`) and Watergate (`GUmLe8YtIck`) from their video ids. For the other seven, the captain decides whether to identify or supply sources; Fascism (its footnotes name the works it drew on) and Putin (its chapters carry video timestamps) are the closest to ready.
3. Recover deleted content from git rather than re-deriving it: `git show <last-live-sha>:<path>` returns the full page, for example `git show 7b4351c:fascism-american-discourse/lessons/0001-origins-1914-1932.html`.
4. Leave the two reverted answer pages and `worktree-locking` out of the vNext rebuild.
5. Put a guard in the publish step before rebuilding: a course must not vanish from the site because its workspace folder is missing, at least without a printed warning. The current behaviour is inferred only.

## Method and limits

- Live checks were `rg` counts over each course's `lessons/` folder (and the single SVG in Afghanistan lesson 5). Deleted-course checks used `git grep` at the last-live commit, so they cover `lessons/` only.
- "Numbered headings" counts `<h2>` elements starting with a digit and a period. Every live lesson uses 1 (Summary), 3 (Narrative), 4 (Machinery), plus 2 (Cast) when present, so lessons without a Cast section skip number 2.
- "Verification tags" counts bold `confirmed`, `unverified`, `corrected`, `partially correct` phrases. Directive k says explanations should not narrate verification; the tag count is a proxy, not a per-sentence review.
- The sup-plus-link count uses the paragraph-level pattern: a `<sup>` containing a link. "Repeat a URL" means the same href also appears as an ordinary link in the same paragraph.
- "Generic or unnamed groups" in Cast tables means rows named "Unnamed ...", "Wounded returnees", or "Returning veterans". The other 15 rows are named people introduced as "cited for" or "cited on" something, which is also the minor-mention pattern directive n excludes, but that call is a judgement.

## Unverified

- The single-event diagram colour check. Issue #57 lists it, but no rule text defines "single-event". The only diagram in the live courses is the SVG in `afghanistan-turning-against-taliban/lessons/05-ch5-armed-opposition-rivals.html`, which colours edges by relationship type (green resistance pressure, crimson jihadist rivalry, purple leadership split) with a legend.
- The citation-form rule. The sup-plus-link counts show where the current pattern occurs, not which citation variant applies.
- Teacher-voice violations are only partly measured. Exact hits: 14 of 14 Russia Machinery sections open with "The chapter works", and 6 of 8 Ark Nova summaries use second person. Whether the Afghanistan and Russia "The video argues" summaries count as teacher voice is a judgement no grep answers.
- Whether the `e3d6838` deletions were intentional. The commit has no message body, no deep-research history exists before 2026-09-29, and the publish script's pruning behaviour is not read here; `publishing.md` states mirroring but not deletion.
- Why the two answer pages were reverted. The revert commits have no explanation; they may have been test publishes.
- Whether the deleted courses' raw sources exist anywhere else (other machines, Drive, old backups). Searched: one `fd` over `C:\Users\Lance` (excluding `AppData` and `node_modules`) for directories named after the nine slugs, which found none. Not searched: `AppData`, other machines, Drive, backups, and the pre-2026-09-29 workspace root (the old site index says "local teaching workspaces", and that path is unknown).
- The source videos or books for `control-story`, `historians-on-trump`, `political-spectrum`, `soviet-afghan-war`, `stalin-red-tsar`, and `putin-rise-to-power`. A `git grep` at each last-live commit for YouTube ids, "Video:" lines, and author names found ids only for Amway and Watergate. The Watergate pages name Sean Munger; the Putin pages cite timestamps but no id. Only the pages were searched, not the deleted `reference/` transcripts.
- Violation counts for deleted courses are at the last-live commit and cover lessons only; reference pages (glossary, cast map, timeline) were not audited for any course.
- Cast-table entries for the deleted courses were not read, so how many of their rows are minor mentions is unknown. Only the Russia live tables were classified (8 of 23 rows generic or unnamed groups; the rest named people introduced as "cited for" something), and that split is a judgement under directive n.

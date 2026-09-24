# Notes — preferences, method, reading position

## Reader state
- Reading **Simon Sebag Montefiore, *Stalin: The Court of the Red Tsar*** (Hachette UK, 2010; epub) **in order**. Position at workspace creation: **ch.14 read** (covers late January → May 1935).
- Queue: **lesson 02 = ch.15 "The Tsar Rides the Metro"**.

## User preferences (rules governing this workspace)
- Terse chat; substantial teaching content lives in workspace HTML files and is linked, not pasted (global `<teach_content_discipline>`).
- **Spoiler rule** (global `<book_explanations_no_spoilers>`): never reveal future events — no character fates, no deaths, no foreshadowing, no forward references, *even ones the book's own text teases*. Stay inside the reader's timeline; use only what the book states by that point.
- Auto-open updated files (Start-Process, default handler).
- Explanations authored as HTML (`lessons/`, `reference/`); `.md` only for admin (MISSION / NOTES / RESOURCES / learning-records).
- **Font default (2026-09-17):** `"Sitka Text", Constantia, Charter, Georgia, serif` — set in `assets/lesson.css`, mirrored in the other workspaces and pinned in the global rules.

## Method — getting one chapter out of the epub
1. Locate the book: `Get-ChildItem 'C:\Users\Lance\Downloads'` matching "court of the Red Tsar", `.epub`.
2. Extract (no plugin needed — epub is a zip): `tar -xf <epub> -C <dir>`. Layout: `OEBPS/partNNNN.xhtml` (90 chapter files) plus `toc.ncx`, `content.opf` at the root.
3. **Map chapter → file from `toc.ncx`**, not by arithmetic: find the `<navLabel><text>N <title></text>` node and take its `<content src>`. Part dividers shift the numbering (ch.7 = part0018, but ch.8 = part0020, because part0019 is the Part Two divider page).
4. Read that single file: a chapter is exactly one `partNNNN.xhtml` (verified: ch.14 = `part0027.xhtml`; ch.15 = `part0028.xhtml`).
5. **Boundary check:** the next chapter's heading is the first content line of the next file (ch.15's heading opens part0028) — if it is missing, the chapter continues into the next file.
6. Working extract at `%LOCALAPPDATA%\Temp\opencode\stalin-epub\` during a session; regenerate with step 2 if gone.

## Workspace quirks
- The book's own **Source Notes** (epub part0080) and **Select Bibliography** (part0081) are the first check for any claim; RESOURCES is built from them.
- The epub has no page numbers — cite chapter numbers, never pages.
- Character names drift (Sergo / Ordzhonikidze; Klim / Voroshilov; Kolya / "Blackberry" / Yezhov): the glossary is canonical and lessons must use it.

## Queue & status
- 01 done (2026-09-17): ch.14 lesson + cast glossary + reading-position record.
- 02 queued: ch.15 "The Tsar Rides the Metro" (Kaganovich Metro opening; same cast).

## Page-spec update (2026-09-20)
Brought the lesson and the three reference pages to the revised page spec. The lesson gained the surtitle (Chapter 14 of 58; the 58 count comes from the Library of Congress table of contents for the book) with a slim meta line, lost the scope-boundary box, the "First appears" column, all three quizzes, the method box, the primary-source/next-steps section, the Anchors line, the teacher box, and the quiz.js script tag; the footer now carries only the glossary link plus the short identity line. The only rewording was "without moral boundaries" to "with no moral restraint" (the old phrase tripped the checker's boundary narration rule); long paragraphs were split, not rewritten, and every fact, quote, date, and cast anchor id is unchanged. The glossary was retitled "Glossary — as of chapter 14", and all three reference pages traded their Links dumps for slim lesson-footer navs (no course-home link: this workspace has no local index.html). The workspace lesson.css was replaced with the skill's canonical copy (which adds the .surtitle rule and drops quiz styles), and the stale assets/quiz.js was deleted. check_lesson.py passes on the lesson with exit 0.

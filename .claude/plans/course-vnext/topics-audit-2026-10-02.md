# Site topics audit — conformance with pre-redesign deep-research/teach conventions

Date: 2026-10-02 · Scope: all 6 course topics + `answers/` + root index in `bearmancer.github.io` · Method: conventions from the installed `deep-research` skill + `course-vnext` layout; mechanical audit script (`audit_topics.py`, this repo's `_ledger/.../work/` scratch) plus manual spot reads. Read-only; no edits made.

## 1. Conforming

- All 6 courses (afghanistan, ark-nova, russia, saudi, wifi, + index rows): doctype, viewport, `lesson.css`, `course-index.js` + `shell.js` before `</body>`, single `h1` per page, no `<sup>`, no Sources/Bibliography headings, no YouTube links, no bracketed timestamps, no kicker/surtitle in lessons, no "Chapter N of M".
- Filenames all match `NN-chK-*.html`; each course index has `index-rows` + `index-extras`; every lesson is linked from its index; no "here"-style links; no let's/we/I meta voice in body text (one quoted exception inside a blockquote).
- Root index: single merged table (commit `36969c7`), correct links.

## 2. Gaps found

- **G1 — `answers/rules-ark-nova.html`: double H1.** Lines 43 and 45 both render an H1 ("Ark Nova"); template H1 + body H1 duplication. Fix: drop the body copy (or the template copy), keeping the shared answer layout intact.
- **G2 — `saudi-military-paradox` chapter 7 is a Pakistan chapter.** File `lessons/07-ch7-the-identity-tangle.html` (H1 "The Identity Tangle: Peoples of Pakistan and Its Neighbours"; sections: Two Pakistans / Bengal / Urdu-speakers / Kashmir / Durand Line; ~1,800 words) sits inside the Saudi course and is listed in its index row (`index.html:50`). This looks like stray content (possibly written for a planned Pakistan topic). Needs a course-owner decision: replace with a Saudi-relevant chapter, or move the text to a future Pakistan topic.
- **G3 — `russia-military-morale-crisis`: committed working artifact.** `reference/transcripts/full-attempt/transparrot_page.html` is tracked in git (a transcript-parser working file, not a convention `reference/` page). Proposed: remove from repo (keep local copy under gitignored `work/` if still wanted).
- **G4 — `orchestral-instruments/`: empty directory** (no index, no lessons, not listed anywhere). Proposed: remove, or scaffold as a real topic later.
- **G5 — asset drift.** Every topic's `assets/` copies differ from the root feed: `course-index.js` differs per topic by design (contains the lesson list) and `lesson.css` splits into two cohorts (afghanistan/russia/saudi/wifi share one hash; ark-nova another; none match root `assets/lesson.css`). If the root feed is canonical, a republish pass would sync copies; if copies are frozen-at-publish, nothing to do.

## 3. Open policy item (verify with owner)

- **Reference pages carry verification narration.** Timelines/glossaries/cast maps systematically use sourcing caveats: afghanistan timeline ×10, afghan glossary ×4, russia glossary ×10, russia cast-map ×2, russia timeline ×3, saudi timeline ×8 (pattern "Verified: the record confirmed…"). Lessons themselves are clean. If the current conventions ban verification narration everywhere, these pages need a re-voice pass per topic; if the caveats are an intended feature of reference pages, no action.

## 4. Proposed refactor (awaiting approval)

1. G1 fix — tiny edit, one page.
2. G2 decision — (a) commission a Saudi chapter rewrite (sourcing + writing, deep-research style), or (b) park: unlist ch7 + keep file for a future Pakistan topic.
3. G3 removal — one `git rm`.
4. G4 removal — one `rmdir` (empty dir; git doesn't track empty dirs anyway).
5. G5 asset sync — optional mechanical republish tab (only if root feed is canonical).
6. Section 3 policy — either keep as-is or plan re-voice passes.

Nothing else was found that blocks adherence; the topics are otherwise consistent with the pre-redesign conventions.

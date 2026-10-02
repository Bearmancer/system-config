# Site topics audit: open items

Scope: course topics, `answers/` and the root index in `bearmancer.github.io`. Audited 2026-10-02 against the `deep-research` skill conventions and the `course-vnext` layout; open items re-checked 2026-10-03.

## Open

- **G2: `saudi-military-paradox` chapter 7 is a Pakistan chapter.** `lessons/07-ch7-the-identity-tangle.html` (H1 "The Identity Tangle: Peoples of Pakistan and Its Neighbours", about 1,800 words) is listed in the Saudi course index (`index.html:50`). Needs a course-owner decision: commission a Saudi chapter, or unlist it and keep the file for a future Pakistan topic.
- **G5: asset drift.** Each topic's `assets/lesson.css` differs from the root `assets/lesson.css`: afghanistan, russia, saudi and wifi share one hash, ark-nova another. `course-index.js` differs per topic by design. If the root feed is canonical, a republish pass syncs the copies; if copies are frozen at publish, nothing to do.
- **Verification narration in reference pages.** Timelines, glossaries and cast maps carry sourcing caveats ("Verified: the record confirmed…"): afghanistan timeline ×10, afghan glossary ×4, russia glossary ×10, russia cast-map ×2, russia timeline ×3, saudi timeline ×8. Lessons are clean. If current conventions ban verification narration everywhere, each topic needs a re-voice pass; if the caveats are intended on reference pages, no action.

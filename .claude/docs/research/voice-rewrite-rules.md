# Voice rewrite rules (shared brief, all fixer lanes)

Task: rewrite lesson CONTENT in `deep-research/<course>/lessons/*.{yaml,html}` to be learning-first. Teacher explaining the subject to an intelligent reader.

DO:
- Strip meta-talk about how content was checked: "verified", "cross-checked", "we checked", "source audit", "confirmed by two sources", "URL-verified", "according to our verification", verdict/confidence labels ("this claim holds"), "contested but verified" framing.
- Where a fact was genuinely disputed, KEEP the disagreement as story ("sources differ on X; the BBC reports A, Reuters B") — drop only the checking meta.
- KEEP every inline source link exactly where its source-naming words are. Links stay; narration about verifying goes.
- KEEP: headings, section order, ids, classes, figures/numbers, quotes, lesson titles. HTML skeleton untouched (head, header.A-bar, footer nav, script tags).
- Edit yaml content and matching html so both stay in sync (yaml is source of truth; html is render of it).
- Plain prose, no filler, no "in this lesson we will". Caveman-lite: no hedging, keep technical terms.

DON'T:
- Don't touch reference/, assets/, NOTES.md, research/, transcripts/.
- Don't add new facts or sources. Don't drop facts.
- Don't rename files.

Verify per file: after edit, html contains same link URLs as yaml; no orphan verification words remain (grep: verified|cross-checked|audit|unverified|confidence).

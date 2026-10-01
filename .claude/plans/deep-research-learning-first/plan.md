# deep-research: learning-first restructure plan

Status: superseded 2026-10-01. Captain narrowed the goal to tone only; the SKILL.md Voice rule and opt-in verification landed instead. P0-P6 will not run.

Read-only architect pass. Skill under `C:/Users/Lance/.claude/skills/deep-research/`. Two other agents edit it now: re-read line numbers before applying. Measurements taken 2026-09-30.

## 1. Current-state audit

### Frontmatter description (SKILL.md:3), verbatim opening
- "One-stop research engine + web-data fleet router. Consult before any scrape, search, crawl or extract call: server pick, bot-block chain, credit failover."
- Then "Input shape picks mode": question/claim -> verdict page FIRST; long source or topic to learn -> course SECOND; classical -> picks THIRD.
- Learning words in the description: "topic to learn", "explain chapter N", "course/notes/treatise". The word "learn" appears once in about 140 words. No "understand", "teach me", "study", "walk me through", "how does X work".

### Top-level SKILL.md sections (139 lines, about 1800 words)
- Preamble (1-10), Workflow (12-21), Reader profile (23-28), Terminal answer format (30-35), Fast path: every web call (37-53), Mode router (55-73), Verdict mode (75-79), Research rules (81-91), Tier ladder (93-98), Passes (100-106), Source handling (108-113), Burn guards (115-117), URL audit (119-126), Key rotation (128-139).

### Measured split (SKILL.md body lines)
- Fetch/scrape infrastructure: Fast path 17 + Burn guards 3 + Key rotation 12 = 32 lines (23%). With URL audit 8 (tooling, cross-skill) = 40 (29%). Plus the "plain fetch" router row and description sentence 1.
- Fact-check/verification machinery: Verdict 5 + Research rules 11 + Tier ladder 6 + Passes 7 + Source handling 6 = 35 lines (25%).
- Learning-specific text: zero body sections. `rg -ci "learn|teach|understand|course" SKILL.md` = 7 hits: description, router rows 61-63, line 69 pointer, line 73. Only ONE row states learning intent ("Topic to learn, no source", line 62).
- All learning material lives outside SKILL.md: `references/modes/course.md` 46 lines + `references/course/*` 508 lines = 554 lines. `references/fleet.md` = 104 lines. SKILL.md is about 0% learning while the reference tree is about 75% learning; the entry file misdescribes the skill.

### Router table (SKILL.md:59-67)
- Row order: course (named source) > course (topic) > course (existing workspace) > recommend > verdict > fetch > ask. Router order is already learning-first; the description and the Fast path section contradict it (description order verdict > course > recommend; fleet text sits above the router at line 37).

### Where learning intent is buried, contradicted, or weakly triggered
- Buried: no purpose line. Skill never says the aim is understanding. Course rules are 2 hops deep (`modes/course.md` -> `course/*.md`).
- Contradicted (a): description says "fact-check" -> verdict; router row 1 (SKILL.md:61) says named source "any verb incl. 'fact-check'" -> course. Same word, two modes.
- Contradicted (b): description sentence 1 and Fast path (37) say "consult before ANY scrape/search": the skill fires on plumbing, and every learning run reads 17 lines of chain text before the router.
- Contradicted (c): Workflow step 2 default "rigorous research (Tier 1...)" and step 3 "Research level: pick tier 0/1/2" apply to every mode; a course ask gets a research-depth frame, not a learner-depth one.
- Contradicted (d): `course.md` page standard 2 bans quizzes, reader questions, next-steps, "method box, teacher box". Defensible as slim-page style, but no comprehension element exists anywhere; `learning-records/` is created (course.md:28) and never defined in SKILL.md. Content-heavy, comprehension-light.
- Weak triggers: no phrase for "help me understand X", "I want to learn X", "explain X to me", "walk me through", "study guide", "what should I know about X". Undertriggers on pure-topic learning, overtriggers on scraping. Collides with OMC `research` and `mattpocock-skills:research`.
- No verb for learning in the router labels: "verdict", "recommend", "fast path" are all verbs/nouns of checking or fetching; the learning mode is the noun "course".
- README.md table order is verdict first, fast path last; same bias as the description.

## 2. Target information architecture

### Purpose line (SKILL.md, directly under H1)
- "Primary purpose: help the user learn and understand a topic, source or claim, through a verified per-chapter course. Fact-checking, source fetching and classical picks support that purpose."

### Mode names (verbs, learning first)
1. `learn` (was course): named source, topic to learn, continue workspace. Loads `references/modes/course.md`.
2. `check` (was verdict): question, claim, claim list, URL list; cited verdict page. Also the verification pass inside `learn` step 6.
3. `recommend` (unchanged): classical picks.
4. `fetch` (was Fast path): plain fetch/scrape, no research ask.
- Keep file names (`modes/course.md`, `course/`) to avoid churn in `publishing.md`, `publish_teach.py`, evals. Only labels in SKILL.md, README.md, evals change (open decision D2).

### Description text (proposed, about 120 words, learning first)
"Learn and understand a topic, book, article, paper, lecture or video: builds a verified per-chapter GitHub Pages course. Use when the user wants to learn, understand, study, be taught or walked through something ('teach me X', 'help me understand X', 'explain chapter N', 'go through <source> chapter by chapter', video URL + 'explain', 'make a course/notes/treatise', 'continue the course'). Also checks facts instead of recalling them (dates, figures, names, attributions: 'is it true', 'how true is it that X', 'did X happen') into a cited verdict page, gives verified classical picks (deep cuts, Soviet symphonies, new concerto), and routes web scrape/search/crawl calls (server pick, bot-block chain, key rotation), even without naming this skill."
- Triggers kept: explain chapter N, chapter by chapter, course/notes/treatise, continue a course workspace, fact-check/is it true, classical deep cuts, scrape/search/crawl/extract, key rotation.
- Triggers added: learn, understand, study, teach me, help me understand, walk me through.
- Fleet trigger kept but demoted to the last clause (decision D1).

### SKILL.md section order (target about 105 lines, from 139)
1. H1 + purpose line + caveman lite line + host-neutral fan-out probe (existing 6-10).
2. Mode router (moved up from 55): four modes, learn first; one tie-break stated once for "fact-check" (named source + verify-only intent -> check; otherwise learn).
3. Workflow (existing 12-21); "Research level" reworded to "Depth": learn = course depth, check = Tier 0/1/2.
4. Learn mode (NEW section, about 10 lines, no new file): aim = comprehension over coverage; syllabus approval before build for topic-only asks; prerequisite-first order inside a chapter; source's own account kept, corrections folded in; done = each chapter stands with earlier ones and reads clean; pointer to `references/modes/course.md`.
5. Check mode (existing Verdict mode 75-79) followed by "Verification rules" = Research rules, Tier ladder, Passes, Source handling (81-113 unchanged text, relabelled as shared by check and learn step 6).
6. Reader profile + Terminal answer format (23-35, content unchanged, moved below modes).
7. URL audit (kept in SKILL.md; cross-skill rule, 8 lines, inbound pointers rely on it).
8. Fetch (3 lines): pick server row in `references/fleet.md`; MCP -> CLI -> POST; blocked -> chain in fleet.md; credit/auth failure -> "Key rotation" in fleet.md.
- Removed from SKILL.md: Fast path chain (17 lines), Burn guards (3), Key rotation (12) -> `references/fleet.md`.

### Material moving to references/
- `references/fleet.md` gains, in order: existing server table (1-30); `## Bot-block chain` (from SKILL.md 37-53); `## Burn guards` (115-117); `## Key rotation` (128-139), merged with existing `## Keys and ops` (line 70) so nothing repeats. Grows about 104 -> 135 lines. No new file, no stub. fleet.md stays one hop from SKILL.md, so the rules stay reachable.
- fleet.md:83 "OmO: see SKILL.md Key rotation" -> "see Key rotation below".
- Learning material stays put.

### Fleet-router and key-rotation reachability
- SKILL.md `## Fetch` contains the strings "Key rotation" and `references/fleet.md`, so `rg "Key rotation" SKILL.md` still hits and the chain is one hop away.

## 3. File-by-file change list (skill root `C:/Users/Lance/.claude/skills/deep-research/`)
- `SKILL.md`: rewrite description; add purpose line; reorder per section 2; add Learn mode; rename Verdict->Check, Fast path->Fetch; cut chain/Burn/Key rotation bodies; router tie-break. Caveman lite kept; state current fact only, no "was/now" narration.
- `references/fleet.md`: receive chain, burn guards, key rotation; fix line 83; keep error-code table.
- `references/modes/course.md`: retitle "Learn mode (course)"; lines 24 and 30 "SKILL.md passes" -> "SKILL.md Verification rules". No other change.
- `references/course/publishing.md:30`: 'SKILL.md "Verdict mode" step 3' -> '"Check mode" step 3'.
- `references/domains/**`: `rg -n -i "verdict|fast path"`; rename any hit (likely none).
- `README.md` (human-read, plain prose): learn first in the table, new mode names, layout block, "Single homes": URL audit in SKILL.md; key failover in references/fleet.md.
- `evals/evals.json`: see section 5.
- `C:/Users/Lance/Dev/system-config/claude/skills/deep-research/**`: backup mirror already differs from live (SKILL.md, README.md, assets, evals, references/course/*). Do NOT hand-sync; let the backup job copy after the live edit (decision D5).

## 4. Inbound-reference updates
Command run: `rg -n "deep-research" C:/Users/Lance/.claude C:/Users/Lance/.config/opencode C:/Users/Lance/Dev/system-config --glob '!**/plugins/**'` (my view truncated at 80 lines; the implementer reruns it excluding `history.jsonl` and `jobs/`).

Must change (section pointer breaks):
- `C:/Users/Lance/.claude/CLAUDE.md:224` `<key_rotation>`: 'rotate per deep-research SKILL.md "Key rotation"' -> 'rotate per deep-research `references/fleet.md` "Key rotation"'. Mirror: `C:/Users/Lance/Dev/system-config/claude/CLAUDE.md:212`. Check `C:/Users/Lance/.config/opencode/AGENTS.md` and `C:/Users/Lance/Dev/system-config/opencode/AGENTS.md` for a twin rule (not in visible output).
- `references/fleet.md:83` (inside skill): local pointer.
- `C:/Users/Lance/.claude/skills/arr-api-reference/SKILL.md:7`: mentions deep-research in a line I could not see whole; read and confirm which section it names.

Unchanged under the default plan (URL audit stays in SKILL.md):
- `C:/Users/Lance/.claude/skills/github-create/SKILL.md:62` and `C:/Users/Lance/Dev/system-config/claude/skills/github-create/SKILL.md:62`: 'deep-research SKILL.md "URL audit"'.
- `C:/Users/Lance/.claude/skills/shell-gotchas/SKILL.md` and `C:/Users/Lance/Dev/system-config/claude/skills/shell-gotchas/SKILL.md:62`: same pointer.
- These change only if the captain picks D3 option b.

No change (path or name only):
- `CLAUDE.md:147`, `:155`; opencode `AGENTS.md:45,53`: course data path `~/Dev/deep-research/<slug>/`.
- `C:/Users/Lance/Dev/system-config/README.md:56,58,60`: `scripts/switch_api_key.py` path and repo clone; scripts do not move.
- `settings.json:158` (live + `system-config/claude/settings.json:158`): "learning-course content pipeline" wording; optional refresh.
- `system-config/docs/adr/0003-file-key-rotation.md`, `docs/standards/architecture.md`, `.claude/plans/deep-research/review.md`, `plans/treatise-merge/**`: historical or path-only; edit only if they quote "SKILL.md Key rotation".

## 5. Eval changes (`evals/evals.json`, 4 evals, ids 0-3, fields id/prompt/expected_output/files)
- Evals 0, 1, 2 (course): behaviour unchanged, prompts stay. Reword `expected_output` only where it says "course mode"/"Verdict" -> "learn mode"; add "no research-tier question asked".
- Eval 3 (Napoleon): "Verdict mode with no cast list" -> "Check mode with no cast list". Reword required.
- Add 3 evals covering real gaps: (4) "help me understand the Thirty Years' War" -> learn mode, syllabus put to user via AskUserQuestion, nothing built before approval; (5) "grab this page <url>" -> fetch only, no publish, no intake; (6) "Soviet symphonies from early 20th century" -> recommend page (untested today). Optional (7): named source + "fact-check" tie-break.
- Fixtures (`geom-fixture.html`, `scripts/fixtures/**`) unaffected.
- Run skill-creator description optimization: 10 should-trigger (6 learning phrasings, 2 check, 2 fetch) and 10 should-not (OMC research, code questions, API docs lookup).

## 6. Risks
- CLAUDE.md `<key_rotation>` not updated in both live and mirror: agents on credit failure land on a missing section. Mitigation: one pass plus `rg "Key rotation"` after.
- Fleet trigger demotion undertriggers on scrape calls; skill-map.md:157 records the earlier decision to fire on every web call. Mitigation: D1.
- Overlap with OMC `research` and `mattpocock-skills:research` widens with "understand/learn". Mitigation: anchor on topic/source + course nouns; tune by description eval.
- Concurrent editors: two agents edit the skill now. Apply only after they finish; re-read first.
- Mirror drift: live and `system-config/claude/skills/deep-research` differ already; a blind sync could overwrite newer live edits.
- Learn mode section adds context on every run; cap at 10 lines.
- Quiz/reader-question ban conflicts with a learning-first purpose; lifting it touches `check_lesson.py` and `lesson_rules.py` (D4).
- Mode labels differ from file names (`course.md` = learn); document in README.

## 7. Acceptance checks
- `rg -ci "learn|understand|teach|study" SKILL.md` >= 8; description leads with learning; "web-data fleet router" appears only in the last clause.
- SKILL.md <= about 110 lines; no `## Fast path`, `## Burn guards`, `## Key rotation` in SKILL.md; `rg -n "^## (Bot-block chain|Burn guards|Key rotation)" references/fleet.md` returns 3.
- Every inbound pointer in section 4 resolves to an existing heading (check each with `rg -n "^#+ <heading>"`).
- `rg -n "Verdict mode|Fast path" -g '!evals/**'` in the skill dir returns zero stale references.
- Every reference file is still named in SKILL.md (one-hop rule, README.md).
- `uv run scripts/check_urls.py` passes on new URLs; `jaq . evals/evals.json` parses; `scripts/fixtures/run_gate.py` and stencil tests still pass (scripts untouched).
- Description eval: >= 9/10 should-trigger, <= 1/10 false trigger.
- No "no longer/previously/now" narration in edited AI-consumed files.

## 8. Open decisions for the captain
- D1 fleet trigger in the description: (a) keep as last clause [recommended]; (b) drop it and rely on CLAUDE.md `key_rotation` + a one-line web-call rule; (c) split the fleet router into its own small skill.
- D2 mode rename depth: (a) labels only, keep file names [recommended]; (b) rename `modes/course.md` -> `learn.md` and update publishing.md, evals, README; (c) keep "course" and only add a purpose line.
- D3 key-rotation home: (a) `references/fleet.md` [recommended]; (b) also move URL audit there and repoint github-create and shell-gotchas; (c) leave both in SKILL.md and only reorder.
- D4 learning checks: (a) keep the quiz/reader-question ban [recommended, no script change]; (b) allow an optional "check your understanding" block in lesson schema plus gate update; (c) put comprehension checks in `learning-records/` only.
- D5 mirror sync: (a) backup job syncs after live edit [recommended]; (b) edit both copies by hand; (c) diff-reconcile first, then sync.

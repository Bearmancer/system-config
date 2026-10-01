---
name: deep-research
description: "Use when the user asks to research, explain, teach or study something, or to check facts: 'teach me X', 'help me understand X', 'explain chapter N', 'go through <book/article/paper/lecture/video> chapter by chapter', make a course/notes/treatise, continue a course workspace. Long source or topic -> per-chapter GitHub Pages course; question, claim or topic ('is it true that X', 'how true is it that X', 'did X happen') -> answer in cited prose, no per-claim table; explicit fact-check-only request ('fact-check this', 'only fact check', 'verify these claims') -> per-claim verdict page; board-game rules ('how do I play X', 'rules for X') -> one rules page; classical works wanted (deep cuts, Soviet symphonies, bored of Beethoven, new concerto/overture) -> verified picks page. Facts are always verified, not recalled (dates, figures, names, chronology, attributions, discography, durations). Consult before any scrape, search, crawl or extract call (server pick, bot-block chain, credit failover), even without naming this skill."
---

# Deep research

Caveman lite for agent-internal text only: subagent prompts, worker reports, notes files, terminal summary; no filler or pleasantries, technical terms kept. Reader-facing prose (lesson body, summary, answer/verdict/rules pages) never uses caveman style; Voice governs it. Applies on every host.

Host-neutral. Fan-out probe: subagent launcher present -> launch `researcher` if defined, else the host's general subagent; one self-contained worker per chapter/axis (prompt names deliverable, scope, verify step, stop condition, output schema); no launcher, or subagent lacks web tools -> run inline.

## Workflow

Every run, stages in order:

1. Classify: pick mode via "Mode router". Router covers every input shape.
2. Intake: Ask only on real ambiguity (scope, source or output that the request leaves open and a wrong guess would waste the run): one AskUserQuestion batch, up to 4 questions, recommended option first. Otherwise no questions. Defaults: rigorous research (Tier 1, contested claims Tier 2), output published to Bearmancer (stage 5). Quick work (plain fetch, single-claim check) never asks. After asking, stop and wait for answers. Host with async question tool (OmO: answer arrives as next user message): end the turn after asking.
3. Research level: pick tier 0/1/2 ("Tier ladder"); state it in one line.
4. Execute: the mode's steps.
5. Publish, no asking, every mode: GitHub Pages (bearmancer.github.io) via `references/course/publishing.md` (course: workspace publish; verdict, recommend: "Single answer page", one page each). Terminal shows short answer + live link.
6. Gaps: workflow needs something missing (mechanism, script, tool, config) -> open GitHub issue on Bearmancer/system-config; no workaround.

## Reader profile

- Reader is in India. Default scope global, never US/West by default.
- Region-varying fact: give global picture, include India alongside. India = one included lens, not the frame. TB statistics: global burden + India figures, not US data.
- Prices only when topic already involves cost: in ₹, original currency beside it if source differs. No pricing section otherwise.
- No other India rules: no spelling/unit/date rules, no forced Indian examples.

## Terminal answer format

Terminal answer of a published run: bottom line (1-3 lines) + live link. Other self-contained terminal answers (e.g. gap report):
- Short heading per part; one-line bottom line first; then grouped sections.
- Blank line between sections; bold key number or verdict per group; sources as short final list.
- Never one flat bullet list without headings and spacing.

## Fast path: every web call

1. Pick server by capability: `references/fleet.md`. Name row used. Route MCP first, then vendor CLI, then POST script.
2. Bot-blocked (401/403/429/503, challenge page, empty body): walk chain in order, stop at first fetch holding target content. Credit/auth failure on a step: walk accounts of that server ("Key rotation") before leaving it. Blocked: next step.
   1. Tavily `tavily_extract`.
   2. Firecrawl `firecrawl_scrape` `proxy: "auto"`, `maxAge: 0`.
   3. Exa `web_fetch_exa` (cached copy); `SOURCE_NOT_AVAILABLE` -> next.
   4. ScrapeGraph `scrape` `stealth: true` (+5 credits).
   5. Apify tool `apify--rag-web-browser` (Actor ID `apify/rag-web-browser`), or site Actor via `search-actors` + `call-actor`.
   6. AgentQL `extract-web-data`.
   7. Firefox DevTools MCP, or Playwright MCP `browser_navigate` -> `browser_snapshot`.
   8. Bright Data Web Unlocker: MCP `scrape_as_markdown`, then CLI `brightdata scrape`; 502 `reject_block` -> retry once.
   9. Browserbase (paid tier for CAPTCHA).
   Keep internal log `URL | status | method` per attempt. All steps and accounts exhausted: URL blocked, never guess content; flag or drop the claim it carried.
3. Credit/quota/auth failure: "Key rotation" below; error codes per service: `references/fleet.md`.

Plain fetch, no research asked: stop after fast path.

## Mode router

One skill, every research ask. Match first row that fits.

| Input shape | Example | Mode | Load |
|---|---|---|---|
| Explicit fact-check-only ask, any input: claims, URL, named source | "fact-check this", "only fact check", "verify these claims" | verdict; published (Workflow stage 5) | "Verdict mode" below |
| Board-game rules ask | "how do I play <game>", "rules for <game>", "teach me <board game>" | boardgame; Tier 0; published (Workflow stage 5) | "Board-game mode" below |
| Named source: URL, book, article, paper, lecture, video; any verb except an explicit fact-check-only ask | "<youtube url> - explain", "go through The Prince" | course | `references/modes/course.md` |
| Topic to learn, no source | "teach me the Thirty Years' War" | course; syllabus researched, user approves before build | `references/modes/course.md` |
| Existing course workspace | "continue the Prince course" | course | `references/modes/course.md` |
| Classical works wanted | "Soviet symphonies from early 20th century" | recommend; published (Workflow stage 5) | `references/domains/music/classical/recommend.md` |
| Question, claim, claim list, URL list, no fact-check-only ask | "How true is it Putin is fucked?", "is it true that X" | answer: cited prose, no claim table; published (Workflow stage 5) | "Answer mode" below |
| Plain fetch/scrape, no research ask | "grab this page" | fast path only | none |
| Fits no row above | mixed or unclear ask | AskUserQuestion: which mode | none |

Course mode step files, read when course.md step names them: `references/course/workflow.md`, `lesson-schema.md`, `page-design.md`, `diagram-spec.md`, `publishing.md`, `references/course/sources/youtube.md`, `text-sources.md`.

Reference depth: every reference file is listed here, one hop from this file. A reference file never sends to another file for content it needs; it names the file only as a cross-check.

Domain: before first search read `references/domains/<domain>/sources.md` + `exclusions.md`. Domains: `general` (non-music), `music/classical`, `music/popular`. Music domains also read `references/domains/music/rules.md` first. Domain source order replaces default preference order; domain bans always apply.

## Voice

All modes except explicit fact-check-only Verdict mode:
- Write as knowledgeable teacher to intelligent reader: explain subject so it is understood.
- Weave citations into explanation (inline links on source-naming words); checking folds into narrative.
- Sources disagree or claim corrected: say so as part of story, explain why.
- Register: flowing explanatory prose, sentence length varied; connectives show how ideas relate (because, which meant, so, yet); paragraphs build an argument step by step.
- Claims carry calibrated confidence, stated plainly where evidence is firm and qualified where it is thin. No stacked emphatic one-liners, no rhetorical punch lines, no bold for emphasis in prose.
- No report language: no verdict/confidence framing ("claim holds", "confirmed", "verdict"), no meta framing ("let's", "this lesson shows", "key takeaway").

## Answer mode

Default for any question, claim or topic. Facts are verified internally with the passes below; output is a cited explanation per Voice, not a verification report.

1. Operationalize internally: turn question into checkable sub-claims, one per axis. Vague or loaded wording ("fucked") becomes measurable axes; the answer names how it read the question in one plain sentence. Done when every axis has a binary observable.
2. Pick domain; run passes. Done when every sub-claim has a verdict or pass cap hit.
3. Compose cited prose per Voice: open with the direct answer in plain sentences (no confidence label), then explain in short headed sections with inline hyperlinks on source-naming words. Sub-claims and axes stay internal, never shown as a list. Contested points told as the story of the disagreement, sources named; unverified points read as the source's own account or as open. No per-claim verdict table, verdict groups or claim ledger. Publish per Workflow stage 5 with `--kind answer`.

## Board-game mode

Board-game rules ask. One ADD-friendly rules page per game, `--kind rules`, Tier 0.

1. Sources in order: publisher rulebook, FAQ, errata; then BGG files and forums. Public pages and BGG XML API only; never log in, never handle cookies.
2. Page order: theme; goal and how you win; turn structure; actions; ONE easiest strategy; easiest scoring path; player-count changes for the stated count only (default 4, else max).
3. Cut setup and end-game scoring unless the strategy needs them.
4. ADD-friendly: bullets for actions and turn steps, pointer lists over walls, sentences under ~25 words; explanations between them stay calm Voice prose.
5. Voice applies. Citations = hyperlinks on source-naming words; no Sources heading.

## Verdict mode

Runs only when the user explicitly asks for a fact-check only ("fact-check this", "only fact check", "verify these claims"). A question, claim or "is it true" alone is Answer mode.

1. Operationalize: turn question into checkable sub-claims, one per axis. Vague or loaded wording ("fucked") becomes measurable axes (e.g. war outcome, economy, regime stability, succession); state axes chosen in one line. Done when every axis has a binary observable.
2. Pick domain; run passes (below). Done when every sub-claim has a verdict or pass cap hit.
3. Compose: bottom line first (1-3 lines: answer + confidence + what would change it), then claims in three groups: **Verified** (full or partial, each marked which), **Unverified** (no evidence either way), **False**; then exhausted-resources block if a rerun happened. No cast list: fact-check pages carry none. Contested axes show both sides with sources; no synthesis beyond evidence. Publish per Workflow stage 5.

## Research rules: always on

1. Goal first: one success criterion per research axis, each with binary observable, plus "stop when X" line.
2. Notes file: append-only, sections `## Plan`, `## Now`, `## Findings`. Course: workspace NOTES.md. Other modes: scratch dir. After compaction re-read whole file, resume at `## Now`.
3. Batch independent searches, fetches, passes in one round. Publish, push, delete: one at a time, observe each.
4. Pass prompt names deliverable, scope, verify step, stop condition. Split passes by source territory.
5. Waiting on Pages build or long job: harness monitor or end turn. No sleep/poll loops.
6. Defect met mid-run (dead link, failed gate, wrong claim): fix same run.
7. Done = evidence: every claim carries URL + quote (verdict mode lists them per claim; otherwise inline links); publish done only after live-bytes check.
8. Claim about a specific site/tool behavior needs a fetch/render/test in this run, else mark it untested. Todo/step closes only with its evidence.
9. After each result ask "answerable with evidence now?" Yes: answer. Two exploration rounds, no new facts: stop exploring, act.

## Tier ladder

- Tier 0 cheap: cached search + highlights, score > 0.7, dedupe canonical URL, wiki paired with second source.
- Tier 1 grounded: search then extract chosen URLs, `maxAge: 0` on stale only, complete markdown, query-reranked.
- User asks "most comprehensive" / "thorough" / "exhaustive": Tier 2.
- Tier 2 contested: 2+ independent domains + primary source + counter-search + `observed_at`/`valid_at`; code-verify behaviour claims; unresolved or refuted claims stay out of the prose synthesis (verdict mode: annex).

## Passes

- Default 2 parallel passes; each gets claim list, source order, output shape. Each claim searched by one pass only.
- Worker output per claim, internal: `claim -> group (verified full / verified partial / unverified / false) -> URL -> quote`.
- Loop until every claim resolves; stop after 5 passes, rest marked unverified. No witness = unverified.
- Rerun on claims already searched: open with exhausted-resources block (every domain, source, tool per claim); new pass targets only sources outside it. Verdict mode keeps block beside the claim groups.
- 3+ source territories, or unresolved by pass 3: one worker per axis.

## Source handling

- Apparatus first: source's own description, bibliography, footnotes; then independent sources.
- Default order: primaries -> records -> press -> scholarship -> wikis. Distributor-run wiki = second source beside a primary.
- Label advocacy sources as advocacy.
- Attribution: "as quoted in the source", "attributed to X, primary not located".

## Burn guards

Map before crawl, explicit limit. No `raw_content` at scale. No summary request for large N unused. Pin agent effort, bound arrays. Block media + fonts.

## URL audit: single home for all skills

Every URL emitted to user or written to file (citations, links, issue/PR bodies, lessons). Exempt: placeholders (`<owner>`, `XXXX`, `/example`), localhost/private IP, MCP endpoints, URLs inside shell commands; script skips these itself.

1. Run `uv run <skill>/scripts/check_urls.py <url>...` or `-f <file>`. Only final `200 OK` passes.
2. `BLOCKED` or `JS?`: re-check via fast-path chain; page must load and hold cited claim.
3. `BROKEN` (4xx/5xx, soft-404, deep link redirected to root): find correct URL, re-audit; else drop link, mark `[link unverified]`.
4. Audit log stays internal; never print a URL table. Failure only: unverifiable claim flagged or dropped.

## Key rotation: single home

Account pools live in `~/.secrets/.env`. Never read that file by any means, not even for variable names. `scripts/switch_api_key.py` is its only reader; it prints account names + sha256 fingerprints only.

Trigger: credit/quota/payment/auth failure per `references/fleet.md` table (e.g. Firecrawl 402, ScrapeGraph `insufficient_credits`, key 401 after working). Plain rate limit (429): retry once first.

1. Run `uv run <skill>/scripts/switch_api_key.py --service <name> --next`. It writes the active key to `~/.config/opencode/secrets/<name>` and to the user env var. OpenCode: config watcher reconnects only that MCP server in about 1 s, no restart (verified: system-config `.claude/docs/research/secrets-subdir-reload.md`).
2. Relay its output line verbatim (already masked). Its watcher-reconnect wording holds on OpenCode only.
3. Retry the failed call on the same server. Repeat `--next` per failure until the output returns to the first account: pool exhausted, go to next chain step. Output `pool empty for <svc>: move to next chain step`: go to next chain step, tell user in one line.
4. OmO host: `~/.omo/agent/mcp.json` reads env vars from OmO's parent process at server spawn; rotated key applies only after OmO restarts from a new terminal. Tell user; continue chain on other servers meanwhile.

Controls: `--list`, `--service all --list`, `--set <ACCOUNT>`, `--next --dry-run`, `--materialize`. Service list and env vars: `references/fleet.md`.

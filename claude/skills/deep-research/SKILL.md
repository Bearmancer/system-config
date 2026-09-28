---
name: deep-research
description: "Web research engine + web-data fleet router. Consult before any scrape, search, crawl or extract call: server pick, bot-block chain, credit failover. Input shape picks mode: topic or long source (book, article, paper, lecture notes, video) -> per-chapter GitHub Pages course with approved syllabus; claim list or URL list -> cited chat verdicts; classical recommendation (deep cuts, bored of Beethoven/Mozart, new symphony/concerto/overture) -> verified picks. Use whenever facts must be checked not recalled (dates, figures, names, chronology, attributions, discography, durations), or user asks to research, fact-check, explain chapter N, go through a source chapter by chapter, make a course/notes/treatise, or continue a course workspace, even without naming this skill."
---

# Deep research

Harness-agnostic: OpenCode first, Claude Code works too. Subagent = runtime's own (Claude Task tool, slim `@librarian`/`@fixer`); subagent lacks web tools: run pass inline.

## Fast path: every web call

1. Pick server by capability: `references/fleet.md`. Name row used.
2. Bot-blocked (401/403/429/503, challenge page, empty body): escalate in order, stop at first fetch holding target content:
   1. `firecrawl_scrape` `proxy: "auto"`, `maxAge: 0`.
   2. ScrapeGraph scrape `stealth: true` (+5 credits).
   3. Firefox DevTools MCP, or `@playwright/cli` (`goto` -> `snapshot` -> `find`): real-browser fingerprint.
   4. Bright Data Web Unlocker (`brightdata` MCP; 5k free req/month).
   All four fail: report URL blocked, never guess content.
3. Credit/quota failure: "Key failover" below.

Plain fetch, no research asked: stop after fast path.

## Mode router

One skill, every research ask. Match first row that fits.

| Input shape | Example | Mode | Load |
|---|---|---|---|
| Named source: URL, book, article, paper, lecture, video; any verb incl. "fact-check" | "<youtube url> - explain", "go through The Prince" | course | `references/modes/course.md` |
| Topic to learn, no source | "teach me the Thirty Years' War" | course; syllabus researched, user approves before build | `references/modes/course.md` |
| Classical works wanted | "Soviet symphonies from early 20th century" | recommend | `references/domains/music/classical/recommend.md` |
| Question, claim, claim list, URL list | "How true is it Putin is fucked?" | verdict | "Verdict mode" below |
| Plain fetch/scrape, no research ask | "grab this page" | fast path only | none |

## Verdict mode

1. Operationalize: turn question into checkable sub-claims, one per axis. Vague or loaded wording ("fucked") becomes measurable axes (e.g. war outcome, economy, regime stability, succession); state axes chosen in one line. Done when every axis has a binary observable.
2. Pick domain; run passes (below). Done when every sub-claim has a verdict or pass cap hit.
3. Reply: bottom line first (1-3 lines: answer + confidence + what would change it), then verdict table, then `Unverified` annex, then exhausted-resources block if a rerun happened. Contested axes show both sides with sources; no synthesis beyond evidence.

Course mode step files, read when course.md step names them: `references/course/workflow.md`, `lesson-schema.md`, `page-design.md`, `diagram-spec.md`, `publishing.md`, `references/course/sources/youtube.md`, `text-sources.md`.

Reference depth: every reference file is listed here, one hop from this file. A reference file never sends to another file for content it needs; it names the file only as a cross-check.

Domain: before first search read `references/domains/<domain>/sources.md` + `exclusions.md`. Domains: `general` (non-music), `music/classical`, `music/popular`. Music domains also read `references/domains/music/rules.md` first. Domain source order replaces default preference order; domain bans always apply.

## Research rules: always on

1. Goal first: one success criterion per research axis, each with binary observable, plus "stop when X" line.
2. Notes file: append-only, sections `## Plan`, `## Now`, `## Findings`. Course: workspace NOTES.md. Other modes: scratch dir. After compaction re-read whole file, resume at `## Now`.
3. Batch independent searches, fetches, passes in one round. Publish, push, delete: one at a time, observe each.
4. Pass prompt names deliverable, scope, verify step, stop condition. Split passes by source territory.
5. Waiting on Pages build or long job: harness monitor or end turn. No sleep/poll loops.
6. Defect met mid-run (dead link, failed gate, wrong claim): fix same run.
7. Done = evidence: every verdict carries URL + quote; publish done only after live-bytes check.
8. After each result ask "answerable with evidence now?" Yes: answer. Two exploration rounds, no new facts: stop exploring, act.

## Tier ladder

- Tier 0 cheap: cached search + highlights, score > 0.7, dedupe canonical URL, wiki paired with second source.
- Tier 1 grounded: search then extract chosen URLs, `maxAge: 0` on stale only, full markdown, query-reranked.
- Tier 2 contested: 2+ independent domains + primary source + counter-search + `observed_at`/`valid_at`; code-verify behaviour claims; unresolved or refuted claims go to annex, never synthesis.

## Passes

- Default 2 parallel passes; each gets claim list, source order, output shape. Each claim searched by one pass only.
- Output per claim: `claim -> verdict (confirmed / partially correct / wrong / unfindable) -> URL -> quote`.
- Loop until every claim resolves; stop after 5 passes, rest marked unverified. No witness = unverified.
- Rerun on claims already searched: open with exhausted-resources block (every domain, source, tool per claim); new pass targets only sources outside it. Keep block beside verdict table.
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

1. Run `python <skill>/scripts/check_urls.py <url>...` or `-f <file>`. Only final `200 OK` passes.
2. `BLOCKED` or `JS?`: re-check via fast-path bot-block chain; page must load and hold cited claim.
3. `BROKEN` (4xx/5xx, soft-404, deep link redirected to root): find correct URL, re-audit; else drop link, mark `[link unverified]`.
4. Report per URL: `URL | status | method | pass`.

## Key failover: single home

Account pools live in `~/.secrets/.env`. Never read that file by any means, not even for variable names. `scripts/switch_api_key.py` is its only reader; it prints account names + sha256 fingerprints only.

Trigger: credit/quota/payment/auth failure (Tavily usage limit, Firecrawl 402, Exa credits exhausted, key 401s after working). Plain rate limit: retry once first.

1. Run `python <skill>/scripts/switch_api_key.py --service <name> --next`.
2. Relay its output line verbatim (already masked).
3. Tell user: restart OpenCode; MCP servers read env at startup only.
4. HARD STOP. No retry on old key, no further tool calls this session.

Controls: `--list`, `--service all --list`, `--set <ACCOUNT>`, `--next --dry-run`. Service list, env vars, Exa rotation no-op: `references/fleet.md`.

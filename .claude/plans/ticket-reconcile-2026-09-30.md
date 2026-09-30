# Ticket reconcile and launch closeout (2026-09-30)

Status: approved 2026-09-30
Mode: ralplan consensus, SHORT. Planner pass, iteration 3 (Architect A1-A3 and Critic C1-C6 of iteration 2 resolved).
Scope: Bearmancer/system-config issues #2, #20, #33, #37-#45, new follow-up issues N1-N4, and the launch closeout. Bearmancer/deep-research PR #1.
This plan is #33 step 6 ("ralplan pass: update #2 map, #20 and this ticket with what steps 1-5 settled").
Published copy (after gate G2): https://github.com/Bearmancer/system-config/blob/master/.claude/plans/ticket-reconcile-2026-09-30.md

## Context (verified on the tracker 2026-09-30)

- **Map #2 is CLOSED** (closed 2026-09-29T04:06:46Z, label `navigator:map`). Its last navigator comment says the map "stays as the logbook". Its done criterion (the four #20 drills) is met. Navigator rule: Decisions lines are written only for CLOSED tickets.
- #3-#20 are all closed. #20 closed 2026-09-29T17:24:26Z (`gh issue view 20 --json closedAt`). Its closing comment records the slim fallback live swap proven against a mock 429 provider: 1 request reached the mock, and the fixer replied `DRILL-OK` on `alibaba-token-plan/deepseek-v4.1-flash`.
- #33 is open. It was filed after #2 closed and carries a `Map: #2 | Vessel: deep-research` header. Today it has no native sub-issues: `gh issue view 33 --json subIssues,subIssuesSummary` returns `"subIssues":{"nodes":[],"totalCount":0}`. Its body does not mention Topgrade or the tailnet (`rg -i 'topgrade|tailnet|tailscale'` over the body finds nothing).
- #37-#43 are open, one per POST-only gap. Each body cites the matrix §4 (PR #36) and the same script contract: PEP 723, a key from `~/.config/opencode/secrets/<svc>`, JSON on stdout, and a non-zero exit carrying the vendor error code. Their parent link is body text only (#38 line 1: `Parent: #33 (step 3). Source: ...`); `issue_dependencies_summary` on #37 shows 0 blocked_by and 0 blocking.
- #45 is open. It is the Pages publish path for verdict and recommend. Its parent is body text only (`Parent: #33 (step 8, ...)`); no native parent and no blocked_by.
- #45's authority: the captain decision in the #33 comment of 2026-09-29T13:44:46Z, item 8.5: "Always push to GitHub Pages (bearmancer.github.io), in **every mode** (verdict, recommend and course), without asking." This is the captain's own signed wording, so it is treated as sufficient; no re-sign is asked.
- Merged PRs: #35 (drill, MCP tool catalog, topgrade/tailnet research), #36 (MCP/CLI/POST matrix), #44 (README reinstall row for the vendor CLIs), and deep-research #1 (`.gitignore` for env, key and secrets files).
- The skill edit for #33 steps 4, 7 and 8 has no PR. It is mirrored in backup commit `e630ec3`. Current live lines: SKILL.md:20 (publish stage, names `Bearmancer/system-config#45`), SKILL.md:41 (`tavily_extract`), SKILL.md:45 (`apify--rag-web-browser`), SKILL.md:46 and :49 ("OmO sidecar: disabled"), fleet.md:54 and :66 (`smartcrawler_initiate`).
- Two plan files are **untracked** today (`git status --short`: `?? .claude/plans/deep-research/` and `?? .claude/plans/ticket-reconcile-2026-09-30.md`). One is the review record `.claude/plans/deep-research/review.md` (round 1, 2026-09-29: FAIL on both axes, 11 findings; round 2, 2026-09-30: PASS on both axes); the other is this plan. Both are cited as evidence, so both are committed at gate G2 before any tracker comment links them.
- Git path in system-config: the branch is `master`, and the daily backup commits (`e630ec3`, `b30643b`, `5e7702e`, `d1b7afd`) go straight to `origin/master` without a PR. Plan and record docs follow the same direct-push path.
- #33's acceptance text still says "Verified CLIs installed and in `install.ps1`". PR #44 records the captain's decision to put the CLIs in the README instead, because install.ps1 only registers scheduled tasks and runs elevated.
- `docs/adr/0001-adopt-shipyard-harness.md` exists. The #2 note "`docs/adr/` is not laid yet" is stale.
- Loose files in `~/.config/opencode/`: `opencode.json.next` (4902 B, 2026-09-29 10:28) and `magic-context.jsonc.MOVED_READPLEASE` (816 B, 2026-09-29 13:56).
- `references/domains/music/classical/recommend.md:8` is step 2, "Scope: unclear ask = orchestral, post-1750, non-chamber, non-vocal". It says nothing about intake, which SKILL.md:17 requires first.

### Native link mechanism (gh CLI 2.101.0)

Primary route, verified with the installed `gh version 2.101.0 (2026-09-15)`:
- `gh issue edit --help`: `--add-sub-issue number` ("Add sub-issues by number or URL"), with the example `gh issue edit 100 --add-sub-issue 123,124`. Also `--remove-sub-issue`, `--parent`, `--remove-parent`, `--add-blocked-by`, `--remove-blocked-by`.
- `gh issue create --help`: `--parent number` ("Add the new issue as a sub-issue of the specified parent number or URL").
- `gh issue view --help`, JSON fields include `parent`, `subIssues`, `subIssuesSummary`, `blockedBy` and `blocking`.
- GitHub docs, adding sub-issues: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/adding-sub-issues

Documented equivalent only (not used): REST `POST /repos/{owner}/{repo}/issues/{n}/sub_issues` with the integer `sub_issue_id`, and `GET .../sub_issues`. Source: https://docs.github.com/en/rest/issues/sub-issues

## RALPLAN-DR summary

### Principles
1. Minimum ceremony. Reuse the tracker's native mechanism before inventing a convention.
2. The tracker is the source of truth. Every close carries evidence (a PR, a commit, or a comment with a live result), and every linked doc is a committed blob, not a local path.
3. Signed destinations are not silently amended. New scope is not folded into a closed map as a Decision.
4. Frontier legibility. Every open ticket states what it waits on, with native links where an issue dependency exists.
5. No workaround for a missing mechanism. Gaps become issues (SKILL.md:21).

### Decision drivers (top 3)
1. A signed, met map (#2) must not be reopened or re-signed for work beyond its destination.
2. Follow-ups must stay discoverable as a frontier, ideally as one census.
3. Low overhead. This is a solo captain, and execution runs on Sonnet.

### Options for structuring the follow-ups

| Option | Pros | Cons |
| --- | --- | --- |
| A. Standalone issues with a `Map: #2 \| Vessel:` header; #2 stays closed | Follows the #33 precedent. No signature. Each issue closes on its own. | No census: the frontier is a text search. Parent links stay body text, which GitHub does not track. |
| B. Reopen #2 and add a vessel D with ticket rows | One census. | Amends a signed, met destination. The map's done criterion becomes false. |
| C. New map issue (`navigator:map`) for post-launch follow-ups | Clean census and a new destination. | Needs a W1/W2 captain signature and a navigator pass: heavy for 7 small scripts plus 4 chores. |
| D. Keep #33 open as an umbrella | Children already name #33. | #33's acceptance is satisfiable; an umbrella that never closes hides its own done state. |
| **E. Native sub-issues under #33 for work split out of #33 (children keep the `Map: #2` header); other follow-ups stay standalone under A; #33 closes on its own acceptance** | Native census for #33's own splits via GitHub's sub-issue list and progress summary, without reopening #2 or signing a new map. No body-text `Parent:` drift. Cheap: one `gh issue edit 33 --add-sub-issue` call. | The census hangs off a closed issue, so #2 carries a pointer that names both queries. Whether GitHub permits closing a parent with open sub-issues is not verified from docs; the close step checks it live and stops if refused. |

Chosen: **E**. Only work that #33's body actually scoped becomes a #33 sub-issue: #37-#43 (step 3), #45 (step 8), N3 (step 7) and N4 (step 8). N1 (Topgrade) and N2 (tailnet) come from the PR #35 research, not from #33, so they are standalone issues with the `Map: #2` header (option A for them). The full frontier is the union of the two queries in the #2 pointer line. E dominates A on driver 2 for #33's splits at equal cost on driver 3. B is invalidated by driver 1. C stays the escalation path (see ADR consequences) but fails driver 3 today. D fails principle 2; E differs from D because #33 closes on its own acceptance and the sub-issue list is a census, not a gate.

## 0. Captain decisions (one AskUserQuestion call, before any gate)

Exactly one AskUserQuestion call with these four questions. Nothing in sections 1-5 runs until it is answered.

1. `~/.config/opencode/opencode.json.next` (staged, not loaded by OpenCode, drifts from the live `opencode.jsonc`): delete / keep as reference / inspect first.
2. `~/.config/opencode/magic-context.jsonc.MOVED_READPLEASE` (816 B; the name signals a pending manual action): read it and act / delete / keep.
3. ADRs 0002-0004 (two distinct instruction files with no import; `{file:}` key rotation; daily-only backup with one-time squash): write them in the sediment pass / leave them as candidates.
4. #33 acceptance amendment ("CLIs in the README, not install.ps1"): edit the #33 acceptance line to match PR #44 / quote the PR #44 decision in the close comment only / do not close #33 yet. **The #33 close is gated on this answer.**

The #45 destination extension is not asked: the 2026-09-29T13:44:46Z #33 comment is the captain's own wording and is sufficient. It is never written as a Decisions line on #2.

**If item 4 is "do not close #33 yet":** skip step 4 and the #33 line of step 5, and keep #33 open. The acceptance lines for the #33 close and for the #33 line on #2 are marked not applicable, #33 joins the expected open list, and the #2 pointer line reads "sub-issues of #33" instead of "sub-issues of closed #33". Everything else runs.

## 1. Close now (conditional on gates)

### #33: close after four gates pass
Evidence per step, for the close comment:
- Step 1-2 (matrix, CLIs): PR #36 (matrix with source URLs; the Unverified section is kept), PR #44 (README reinstall row, CLIs verified with `--version`). The install.ps1 wording is handled per the §0 item 4 answer.
- Step 3 (child issues): #37-#43, one per POST-only row in matrix §4, now native sub-issues of #33.
- Step 4 (fold into skill): backup commit `e630ec3` (SKILL.md, fleet.md). Config gaps decided: fleet.md "keep pins" (Exa 4, Apify 3); Context7 and gh_grep are loaded via slim, so no server definition is needed.
- Step 5 (mimo): the #33 comment of 2026-09-29T17:27:51Z records `opencode models` listing the model and the live `MIMO-OK`.
- Step 7 (chain audit): PR #35 `mcp-tool-catalog.md`. Tool names are fixed in `e630ec3` (SKILL.md:41 `tavily_extract`). The Tavily hosted spelling is split into N3.
- Step 8 (strict workflow): SKILL.md:17-21. Verdict and recommend publishing is split into #45 (authority: the #33 comment of 2026-09-29T13:44:46Z). The recommend.md intake wording is split into N4.
- Step 6: this plan, linked as https://github.com/Bearmancer/system-config/blob/master/.claude/plans/ticket-reconcile-2026-09-30.md, plus the comments in the actions below.
- Review record: https://github.com/Bearmancer/system-config/blob/master/.claude/plans/deep-research/review.md
- Also cite: deep-research PR #1 (the LOW `.gitignore` follow-up from the #2 handoffs).

Gates before closing:
1. **G1, skill tests and skill-edit check.** Scope: the pytest suite covers `scripts/` (including `switch_api_key.py`) only; it does not check SKILL.md or fleet.md. So G1 has two parts:
   - `uv run --with pytest pytest C:\Users\Lance\.claude\skills\deep-research\scripts\tests` passes.
   - `rg` assertions on the skill edit, run from `C:\Users\Lance\.claude\skills\deep-research`, one file per call so a hit in one file cannot mask a miss in the other:
     - present (each exits 0): `rg -q 'tavily_extract' SKILL.md`, `rg -q 'apify--rag-web-browser' SKILL.md`, `rg -q 'smartcrawler_initiate' references/fleet.md`, `rg -q 'system-config#45' SKILL.md`;
     - absent (each exits 1, checked on both files together since any hit fails): `rg -q 'tavily-extract' SKILL.md references/fleet.md`, `rg -q 'crawl_start' SKILL.md references/fleet.md`, `rg -q '@playwright/cli' SKILL.md references/fleet.md`, `rg -q 'OmO sidecar: disabled' SKILL.md references/fleet.md` (the sidecar was removed in #51).
   An Opus review PASS is not a test result.
2. **G2, plan docs committed and pushed.** In `C:\Users\Lance\Dev\system-config` on `master`: commit `.claude/plans/deep-research/review.md` and `.claude/plans/ticket-reconcile-2026-09-30.md` together in one commit and `git push origin master` directly (the same path as the daily backup commits; no PR, since these are plan and record docs). Checks, each for both paths:
   - `git ls-files --error-unmatch .claude/plans/deep-research/review.md .claude/plans/ticket-reconcile-2026-09-30.md` exits 0;
   - `git log origin/master -1 --format=%h -- .claude/plans/deep-research/review.md` and `git log origin/master -1 --format=%h -- .claude/plans/ticket-reconcile-2026-09-30.md` each print the G2 commit.
   No tracker comment (the #20 pointer or the #33 close) is posted before G2 passes. Tracker comments link the `blob/master` URLs above, never local paths.
3. **G3, split confirmed.** N3 and N4 exist, are native sub-issues of #33, and are linked in the close comment, so the Tavily pin and the intake wording do not vanish.
4. **G4, acceptance amendment answered.** §0 item 4 has an answer other than "do not close #33 yet", and the close follows it.

### #20: already closed
Add one pointer comment only (after G2): "Reconciled in the #33 step 6 ralplan pass: https://github.com/Bearmancer/system-config/blob/master/.claude/plans/ticket-reconcile-2026-09-30.md". Do not reopen it.

### Nothing else closes now
#37-#45 have unmet done-when criteria (a live call, or a live page).

## 2. Stay open, with what each one waits on

No native blocked_by links are planned: none of these depends on another issue.

| Issue | Link | Waits on |
| --- | --- | --- |
| #37 Exa POST /answer | sub-issue of #33 | none (frontier) |
| #38 Exa agent stop/cancel | sub-issue of #33 | none (frontier) |
| #39 Exa /batches (low) | sub-issue of #33 | none (frontier) |
| #40 Firecrawl batch scrape | sub-issue of #33 | none (frontier) |
| #41 Bright Data async Unlocker | sub-issue of #33 | none (frontier) |
| #42 Browserbase agent runs | sub-issue of #33 | none (frontier) |
| #43 ScrapeGraph crawl management | sub-issue of #33 | none (frontier) |
| #45 Pages publish for verdict/recommend | sub-issue of #33 | none (frontier). Reuses `scripts/publish_teach.py` and `scripts/verify_live.py` where they fit. |
| N1 Topgrade transcript | standalone, `Map: #2` header | the captain's elevated `install.ps1` run (HITL, not an issue) |
| N2 Tailnet grant | standalone, `Map: #2` header | an owner admin-console action (HITL, not an issue) |
| N3 Tavily tool spelling pin | sub-issue of #33 | none (frontier) |
| N4 recommend.md intake wording | sub-issue of #33 | none (frontier) |

#37-#43 stay independent plain scripts; no shared helper is built up front. One note goes on #33 (the parent), not on each child: "Extract a shared module only when a 3rd script would duplicate more than half of an existing one (sibling_duplication_check)."

Body edits: remove the `Parent: #33 (...)` text from #37-#43 and #45 once the native link exists, keeping their `Source:` text.

## 3. New issues to create

Each body starts with `Type: task | Mode: <mode> | Vessel: <vessel> | Map: #2`, following the #33 header. No `Parent:` or `blockedBy:` text in any body.

- N1 and N2: `gh issue create -R Bearmancer/system-config` with no `--parent` (standalone).
- N3 and N4: `gh issue create -R Bearmancer/system-config --parent 33`, which creates each as a native sub-issue of #33.

- **N1. "Topgrade task: capture the console with Start-Transcript, then handle the failing step"** (HITL, vessel B). Body: wrap the task command in `Start-Transcript -Append -UseMinimalHeader` in `Install-TopgradeTask` (SystemConfig.psm1:179), drop the redundant `--no-retry`, and re-register via an elevated `install.ps1`. After a run names the failing step, add it to `[misc] ignore_failures` or `disable` in `topgrade.toml`, or fix it by that step's own key. Done when: the failing step is named from topgrade's step summary, and the next scheduled run exits 0. Primary capture: the transcript file contains the step summary. Fallback, because transcript capture under Task Scheduler is Unverified (`.claude/docs/research/topgrade-and-tailnet.md:60`): if the transcript lacks the summary, run `topgrade --yes` once interactively in an elevated pwsh and read the summary from the console (or from the task window, which stays open on failure at the `Read-Host` in the research's argument sketch, line 24). `--log-filter` is not a fallback: it only sets console tracing verbosity, and topgrade has no log-file option (same doc, line 15). Source: same doc, Q1.
- **N2. "Tailnet: grant tcp:443 on lance to the owner only; optional OPENCODE_SERVER_PASSWORD pin"** (HITL, owner action, vessel B). Body: `/api/*` already returns 401 without credentials. Add a grant limiting `tcp:443` to the owner's user or a tag, and confirm the policy is no longer the default allow-all. Optionally pin the password with `opencode service set env OPENCODE_SERVER_PASSWORD <value>` (the value never goes in the repo or chat). Done when: another tailnet device gets refused, and the owner device still reaches the service. Source: same doc, Q2(c).
- **N3. "deep-research: pin the Tavily hosted MCP tool spelling (tavily_extract vs tavily-extract)"** (AFK, vessel C). Body: the hosted server returned 401 unauthenticated, so the spelling is unpinned (review.md round 2 LOW note). A check to try, not a fact: the #20 block-chain drill session called Tavily extract through the live MCP, so its recorded tool call may show the real name. Done when: the name is cited from a primary source or a recorded live call, and `rg -n 'tavily.extract' SKILL.md references/fleet.md` shows only the pinned spelling.
- **N4. "deep-research: recommend.md step 2 scope default must not read as skipping intake"** (AFK, vessel C). Body: recommend.md:8 sets the default scope for an unclear ask. Add one clause saying the default applies only after SKILL.md Workflow stage 2 (intake) leaves scope unanswered. Done when: `rg -n 'Scope: unclear ask.*intake|intake.*Scope: unclear ask' references/domains/music/classical/recommend.md` hits the scope line, and the skill pytest suite passes. Source: a LOW reviewer note from the #33 skill-edit review.

## 4. Map #2 lines to append

The body edit on closed #2 keeps its state closed. Append under "## Decisions so far" closed-ticket lines only, plus one pointer:

```
- [Acceptance drills](https://github.com/Bearmancer/system-config/issues/20): restore, drift, block-chain and remote/tasks drills PASS; slim foreground fallback live swap proven with a mock 429 provider (1 request, then DRILL-OK on the fallback).
- [MCP vs CLI vs POST](https://github.com/Bearmancer/system-config/issues/33): matrix verified with sources (PR #36); vendor CLIs in the README reinstall table, not install.ps1 (PR #44); mimo-v2.6-flash re-enabled and kept; every deep-research run goes classify, intake, research level, execute, publish, gaps.
- Post-map follow-ups: sub-issues of closed #33, plus open issues with the `Map: #2` header (`gh issue view 33 -R Bearmancer/system-config --json subIssues`; `gh issue list -R Bearmancer/system-config --search '"Map: #2"' --state open`).
```

The search is approximate, not an exact header match: live-tested 2026-09-30 with `--state all`, it returns #2-#20 and #33 (issues that mention map #2), and not #37-#43 (no header). With `--state open` after this plan, it should return N1-N4 (and #33 if kept open); the executor records the actual result in the completion report.

The #33 line is appended only after #33 closes (step 4 below). No lines for #37, #45 or any open ticket. A census that hangs off a closed parent is expected: #33 closes on its own acceptance, and its sub-issue list stays readable after the close.

Also replace the stale note "Deferred sediment: `docs/adr/` is not laid yet." with the current fact, worded per the §0 item 3 answer: either "`docs/adr/` holds ADR-0001 to ADR-0004." or "`docs/adr/` holds ADR-0001; candidate ADRs: two distinct instruction files (no import), `{file:}` key rotation, daily-only backup with one-time squash."

## 5. Execution steps (after approval)

0. **Captain call.** Ask §0 as one AskUserQuestion call with four questions. Record the answers in the #33 close comment (or, under "do not close #33 yet", in a #33 comment).
1. **Gates G1 and G2.** Run the pytest suite and the `rg` assertions. Commit both plan docs in one commit and push directly to `origin/master`; run the G2 checks. On any failure, stop and report; post nothing to the tracker.
2. **File N1-N4** with the bodies above: N1 and N2 standalone, N3 and N4 with `--parent 33`. Record their numbers.
3. **Native links and body edits.** `gh issue edit 33 -R Bearmancer/system-config --add-sub-issue 37,38,39,40,41,42,43,45`. Then remove the `Parent: #33 (...)` text from #37-#43 and #45 (`gh issue edit <n> --body-file`, keeping `Source:`). Add the sibling_duplication_check note to #33. Post the #20 pointer comment.
4. **Close #33** with the evidence comment from §1, following the §0 item 4 answer (G3, G4). If GitHub refuses the close because of open sub-issues, stop and report. Skipped under "do not close #33 yet".
5. **Edit map #2.** Append the #20 line and the pointer line, and fix the ADR note. Append the #33 line only if step 4 closed #33.

Acceptance (lines marked * are not applicable under "do not close #33 yet"):
- `gh issue view 33 -R Bearmancer/system-config --json subIssues --jq '.subIssues.totalCount'` is 10, and `--jq '[.subIssues.nodes[].number] | sort'` equals #37-#43, #45, N3 and N4. The totalCount check guards against a truncated node list; the paginated REST equivalent is `gh api --paginate repos/Bearmancer/system-config/issues/33/sub_issues --jq '.[].number'`.
- `gh issue view <N1|N2> --json parent --jq .parent` is null for both.
- For each of #37-#43, #45 and N1-N4, `gh issue view <n> --json blockedBy --jq '.blockedBy | length'` is 0.
- `gh issue view <n> --json body` for #37-#43 and #45 contains no `Parent:` line; N1-N4 bodies contain no `Parent:` or `blockedBy:` line, and each starts with the `Map: #2` header.
- \* #33 is closed, with a comment containing every evidence link above, including the `blob/master` URLs of review.md and this plan.
- `gh issue list -R Bearmancer/system-config --state open` equals #37-#43, #45 and N1-N4 (plus #33 under "do not close #33 yet").
- #2 body contains the #20 line and the pointer line, and no line for #37 or #45; its state is still CLOSED.
- \* #2 body contains the #33 line.
- `git log origin/master -1 --format=%h -- .claude/plans/ticket-reconcile-2026-09-30.md` prints the G2 commit, and the #20 pointer and #33 comments link blob URLs, not local paths.

## 6. Remaining launch closeout steps

1. **Verify (separate verifier lane, Sonnet; no self-approval).** Scope: system-config PRs #21-#44, deep-research PR #1, backup commit `e630ec3`, and the G2 commit. Check that each closed ticket's done-when has evidence on the tracker. Also re-run the drift check (`backup-agents.ps1` dry comparison against live config).
2. **Sediment pass (C5, with the `agent-doc-discipline` skill, mandatory).** Move lessons into slots:
   - `run --agent` ignores the agent's model (slim-fallback-drill.md), into the deep-research or OpenCode notes;
   - Tavily reports a bot block as empty content plus `Failed to fetch url` (already in fleet.md; confirm);
   - OpenCode v2 per-model `disabled` (the whitelist is dead);
   - ADRs 0002-0004 only if §0 item 3 says write them.
3. **Purge (`auto_purge`).** Enumerate with `fd -u`: rollback files `opencode.jsonc.bak-models` and `oh-my-opencode-slim.jsonc.bak-chain` (existence not assumed), the throwaway mock-429 drill directory, the local tag `pre-squash`, launch `.omc/state`, and the two loose OpenCode files per the §0 answers. Ask per finding, then purge only approved paths and write a manifest.
4. **Completion report**, posted as a final comment on #2: tickets closed, PRs, drills, the open frontier (#33's sub-issue list plus the `Map: #2` search), and purged paths.
5. **Launch mode cancel** once the report is posted and the verifier lane passes.

## ADR: follow-up structure after the map is met

- **Decision:** keep map #2 closed as the logbook, with Decisions lines for closed tickets only and one pointer line. Work split out of #33 (#37-#43, #45, N3, N4) becomes native sub-issues of #33 via `gh issue edit 33 --add-sub-issue` and `gh issue create --parent 33`; follow-ups from outside #33 (N1, N2) are standalone issues with the `Map: #2` header. Close #33 on its evidence after gates G1-G4. #37-#43 stay independent plain scripts until a 3rd would duplicate more than half of an existing one.
- **Drivers:** the signed destination is met and must not be amended silently; the frontier needs a census; overhead stays minimal for a solo captain.
- **Alternatives considered:** A, standalone issues with a header only (used for N1 and N2; for #33's splits it gives no census and keeps body-text parents); B, reopen #2 with a vessel D (invalidated: amends a met, signed destination); C, a new map (viable, but needs a W1/W2 signature and a navigator pass for small work); D, #33 as a permanent umbrella (fails the evidence-based close rule).
- **Why chosen:** E gives a native census for #33's own splits with one gh CLI call, needs no new convention or signature, keeps #33's parent links truthful to its body, and lets #33 close on its own acceptance.
- **Consequences:** the frontier is #33's sub-issue list plus the `Map: #2` search, both named in the #2 pointer line; a census on a closed parent is expected. Body-text `Parent:`/`blockedBy:` lines are retired in favour of native links. #45's destination extension rests on the #33 comment of 2026-09-29T13:44:46Z, not on a #2 Decisions line. Plan and record docs cited on the tracker are committed and pushed to master first and linked by blob URL. If follow-ups grow past about 12, or gain a shared destination, switch to option C.
- **Follow-ups:** N1-N4; the §0 answers (two loose OpenCode files, ADRs 0002-0004, #33 amendment); a shared module for #37-#43 only when the duplication trigger fires.

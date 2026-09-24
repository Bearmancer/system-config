# haven-psmux - Work Plan

## TL;DR (For humans)
<!-- Filled after the detailed plan below was written, so it summarizes the REAL plan. -->
<!-- Plain English for a non-engineer: NO file paths, NO todo numbers, NO wave/agent/tool names. -->

**What you'll get:** Two finished GitHub posting skills plus a fully evidenced feature request and code proposal asking the Haven app to support psmux session restore on Windows computers.

**Why this approach:** Every public claim is traced back to a verified copy of the code before anything is posted, and the request follows the exact shape of a similar change the Haven team already accepted.

**What it will NOT do:** It will not touch existing tmux support, redesign anything, post anything without your explicit go-ahead, or quote a single line that was not read from the verified code copy.

**Effort:** Medium
**Risk:** Medium - the Haven team gates new issue posts, so there is a fallback path if direct posting is denied.
**Decisions to sanity-check:** psmux means the psmux open-source project for Windows multiplexing (your call, locked); trying the issue post first with a code-only fallback; keeping both skills self-contained rather than sharing text.

Your next move: dual high-accuracy review runs before handoff, then start work in a worker session. Full execution detail follows below.

---

> TL;DR (machine): Medium effort, Medium risk (upstream filing gates); skills tail + recon + bodies + gated filing; Metis-pass-1 repairs folded in.

## Scope
### Must have
- C1 skill-patch tail, delta-only: PR skill version 0.1.0->0.1.1, PR triage `gh auth status` preflight, feature-triage fork conditional on no-fork-yet (feature skill stays v0.1.1: triage fix counts as a no-bump patch). All other Oracle items already verified on disk (PR 134 lines, feature 137 lines v0.1.1).
- C2 Haven recon: temp clone + `codegraph init`, exact `SessionManager.kt` registry lines, `docs/features/terminal.md` + picker-path confirmation or fallback, #611/#615 state+URLs, recorded negative-search evidence, exact Gradle test commands, psmux/psmux CLI-surface verification or documented fallback.
- Code + tests on the recon checkout: PSMUX registry entry plus new coverage, suite green, exit codes recorded.
- C3 bodies: issue-body.md + pr-body.md to the fixed github-create-feature bar with zero TO-FILL (`rg` gate).
- C4 filing: non-mutating restriction probe, Branch A (issue + PR + link comment) or Branch B (PR-only citing #611/#615) per decision predicate, failure-path edits, independent re-audit.
- Dual high-accuracy review (momus + independent oracle) before handoff.
### Must NOT have (guardrails, anti-slop, scope boundaries)
- No product-code edits during planning; no `gh issue create` / `gh pr create` / `git push` until the worker's authorize gate passes.
- No trial `gh issue create` as a probe; restriction probe is `gh api` read-only only.
- No fabricated `file:line`, URLs, test output, or SHAs anywhere; every quote carries its codegraph/gh receipt.
- No tmux-path changes, no registry redesign, no second multiplexer; psmux entry only (escape hatch: pause worker, update draft plus plan, explicit owner re-approval before any redesign).
- No citation of psmux upstream until recon verification passes.
- No `--fill`, no heredoc bodies, no plain `--force` (only `--force-with-lease` post-review).

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: tests-after for Haven change (new coverage for the PSMUX registry entry + full `:core:ssh` module suite green + pre/post gap-demo lines) | none-executable for skill markdown (structural gates: task-row grammar, headers verbatim, <500 lines, version labels exact, full re-read diff). Sole human-step exception: the todo-16 authorize gate (explicit go-ahead plus APPROVED token); everything else agent-executed.
- Exact Gradle task names are a C2 deliverable (todo 10) and gate C4; worker runs `git log --oneline -10` on Haven checkout to mimic commit style before any fork-branch commit.
- Evidence: one .omo/evidence/haven-psmux/task-<N>.txt per todo holding the command outputs for its scenarios (single-txt rule; named deliverables — issue-body.md, pr-body.md, task-16-pre.txt — exempt; no separate wave-notes file).

## Execution strategy
### Parallel execution waves
> Target 5-8 todos per wave. Fewer than 3 (except the final) means you under-split.
- Wave 1 (todos 1-4): C1 tail. Todo 1 verify-only first; todos 2-3 patch; todo 4 is the C1 acceptance gate. Sequential within wave (same two files).
- Wave 2 (todos 5-11): C2 recon. Todo 5 (clone+index) first; 6-11 parallelize after 5 (independent extractions).
- Wave 3 (todos 12-15): code plus tests (12, needs 6,7,10,11), restriction probe (13, independent, parallel), bodies (14 needs 6,7,8,9,10,11,12; 15 needs 12,14).
- Wave 4 (todos 16-19): C4 filing. Strictly sequential (issue -> push/PR -> failure-path -> re-audit). Blocked until todos 10 (test commands), 13 (predicate), 14, 15 are recorded.
- Final wave F1-F4 runs in parallel after ALL todos; ALL must APPROVE.

### Dependency matrix
| Todo | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1 | - | 2,3 | - |
| 2 | 1 | 4 | 3 |
| 3 | 1 | 4 | 2 |
| 4 | 2,3 | 5 | - |
| 5 | 4 | 6-11 | - |
| 6 | 5 | 12,14 | 7,8,9,10,11 |
| 7 | 5 | 12,14 | 6,8,9,10,11 |
| 8 | 5 | 14,17 | 6,7,9,10,11 |
| 9 | 5 | 14 | 6,7,8,10,11 |
| 10 | 5 | 12,14,16,17 | 6,7,8,9,11 |
| 11 | 5 | 12,14 | 6,7,8,9,10 |
| 12 | 6,7,10,11 | 14,15 | 13 |
| 13 | - | 16 | 12,14,15 |
| 14 | 6,7,8,9,10,11,12 | 15 | 13 |
| 15 | 12,14 | 17 | 13 |
| 16 | 10,13,14,15 | 17 | - |
| 17 | 8,10,15,16 | 18 | - |
| 18 | 17 | 19 | - |
| 19 | 18 | F1-F4 | - |

### Token registry (sanctioned placeholders — no others permitted)
| token | resolved by | resolution command |
| --- | --- | --- |
| <fork-user> | todo 13 | `gh api user --jq .login` recorded in task-13.txt |
| <issue-n> | todo 16 | `gh issue create` output URL/number propagated into pr-body.md |
| <pr-n> | todo 17 | `gh pr create` output number used in the link comment |
| "<short, names the capability>" | todo 14 | fixed title string recorded in task-14.txt, reused in 15-17 |
| checkout path | todo 5 | absolute temp path recorded in task-5.txt, reused by 6,7,10,12,17,F3 |
| registry file | todo 6 | registry file path recorded in task-6.txt, reused by todo 17 scoped add |
| test files | todo 12 | test file paths recorded in task-12.txt, reused by todo 17 scoped add |
| comment id | todo 17 | comment ID recorded in task-17.txt, reused by todo 18 delete |

## Todos
> Implementation + Test = ONE todo. Never separate.
<!-- Batches appended post-approval; Metis pre-pass (15 gaps) plus Metis loop-pass-1 (15 findings) folded in. -->
- [x] 1. Verify-only re-read of both skills against the verified baseline
  What to do / Must NOT do: Re-read both SKILL.md fully; prove which of the 3 tail items are still absent via targeted search. Do not rewrite anything in this todo.
  Parallelization: Wave 1 | Blocked by: - | Blocks: 2,3
  References: C:\Users\Lance\.claude\skills\github-create-pr\SKILL.md (expect 134 lines, v0.1.0), C:\Users\Lance\.claude\skills\github-create-feature\SKILL.md (expect 137 lines, v0.1.1), .omo/drafts/haven-psmux.md Findings.
  Acceptance criteria: .omo/evidence/haven-psmux/task-1.txt lists for each tail item (PR version bump, PR auth preflight, conditional fork) PRESENT or ABSENT with the exact search hit.
  QA scenarios: happy — `rg -n "gh auth status" C:\Users\Lance\.claude\skills\github-create-pr\SKILL.md` empty (absent as expected); failure — hit present means already landed, drop that sub-item and record why. Evidence .omo/evidence/haven-psmux/task-1.txt.
  Commit: N | baseline is read-only verification (workspace is not a git repo, so no diff-stat; search output is the receipt).
- [x] 2. PR skill patch: version 0.1.1 plus auth preflight
  What to do / Must NOT do: Set frontmatter version 0.1.1; add `gh auth status` as first line of the triage fence. Touch nothing else, no prose, stay under 500 lines.
  Parallelization: Wave 1 | Blocked by: 1 | Blocks: 4
  References: C:\Users\Lance\.claude\skills\github-create-pr\SKILL.md triage block, todo 1 ABSENT list.
  Acceptance criteria: `rg -n "version: 0.1.1"` hits frontmatter; `rg -n "gh auth status"` hits triage fence; `(Get-Content C:\Users\Lance\.claude\skills\github-create-pr\SKILL.md).Count` under 500; step-0 block intact proven by `rg -n "mktemp" C:\Users\Lance\.claude\skills\github-create-pr\SKILL.md` plus `rg -n "codegraph init" C:\Users\Lance\.claude\skills\github-create-pr\SKILL.md` (marker anchors, never numeric ranges).
  QA scenarios: happy — all checks green, Evidence .omo/evidence/haven-psmux/task-2.txt; failure — any pre-existing block disturbed means revert that hunk and redo once, then escalate. Evidence .omo/evidence/haven-psmux/task-2.txt.
  Commit: N | workspace is not a git repo; receipt is the evidence file plus re-read.
- [x] 3. Feature triage: conditionalize the fork command
  What to do / Must NOT do: Replace the unconditional `gh repo fork` fence lines with probe-first wording (check viewerPermission/isFork, fork only when no fork yet). Touch nothing else.
  Parallelization: Wave 1 | Blocked by: 1 | Blocks: 4
  References: C:\Users\Lance\.claude\skills\github-create-feature\SKILL.md triage fence, C:\Users\Lance\.claude\skills\github-create-pr\SKILL.md fork row as the shape to mirror.
  Acceptance criteria: `rg -n "gh repo fork"` co-occurs with a when-no-fork condition; no unconditional fork instruction remains.
  QA scenarios: happy — conditional wording present, Evidence .omo/evidence/haven-psmux/task-3.txt; failure — unconditional form survives means edit missed, redo. Evidence .omo/evidence/haven-psmux/task-3.txt.
  Commit: N | same non-git receipt rule as todo 2.
- [x] 4. C1 acceptance gate
  What to do / Must NOT do: Run `gh --version`, line counts of both files, checklist search (version labels exact, auth preflight present, conditional fork present, step-0 intact, zero TO-FILL), full re-read of changed hunks. Gate only, no edits.
  Parallelization: Wave 1 | Blocked by: 2,3 | Blocks: 5
  References: C:\Users\Lance\.claude\skills\github-create-pr\SKILL.md, C:\Users\Lance\.claude\skills\github-create-feature\SKILL.md, todos 1-3 evidence.
  Acceptance criteria: .omo/evidence/haven-psmux/task-4.txt shows every check GREEN; any RED blocks Wave 2.
  QA scenarios: happy — all green; failure — any RED returns to the owning todo with the failing line. Evidence .omo/evidence/haven-psmux/task-4.txt.
  Commit: N | gate produces evidence only.
- [x] 5. Temp clone plus codegraph index of Haven upstream
  What to do / Must NOT do: Create temp dir at `$env:TEMP\haven-upstream` (outside the workspace), `git clone https://github.com/GlassHaven/Haven.git` into it (full history: todo 10 needs `git log --oneline -10` for style mimicry), run `codegraph init` there, probe-query one symbol to prove the index answers. Must NOT clone into C:\Users\Lance working dirs; temp only. Record the absolute checkout path in the evidence file. Must NOT clean the temp dir until F3 passes. Re-init loops capped at 2 cycles, then escalate with evidence.
  Parallelization: Wave 2 | Blocked by: 4 | Blocks: 6,7,8,9,10,11
  References: fixed PR skill step 0 (clone-to-temp mandate), .omo/drafts/haven-psmux.md C2 row.
  Acceptance criteria: clone dir exists at the pinned temp path, `codegraph explore "SessionManager registry"` (run with cwd at the checkout) returns SessionManager symbols, absolute path plus base SHA (`git rev-parse HEAD` with cwd at the checkout) recorded; log saved to .omo/evidence/haven-psmux/task-5.txt.
  QA scenarios: happy — probe answers; failure — stale/empty index means `codegraph init` again, max 2 cycles, then escalate with evidence. Evidence .omo/evidence/haven-psmux/task-5.txt.
  Commit: N | temp scratch, never committed.
- [x] 6. Extract SessionManager registry lines
  What to do / Must NOT do: Via codegraph on the todo-5 checkout, record the exact file:line of the TMUX registry entry plus the full registry block verbatim. Quote bytes only, never memory. No cross-checking against issue threads here (that belongs to todo 14).
  Parallelization: Wave 2 | Blocked by: 5 | Blocks: 12,14
  References: todo-5 checkout path from task-5.txt.
  Acceptance criteria: .omo/evidence/haven-psmux/task-6.txt holds exact file:line plus verbatim block matching codegraph output bytes.
  QA scenarios: happy — lines resolve; failure — symbols missing means re-init and re-query `codegraph explore "SessionManager registry"` with cwd at the checkout, max 2 cycles, then escalate, never guess. Evidence .omo/evidence/haven-psmux/task-6.txt.
  Commit: N | evidence only.
- [x] 7. Confirm docs plus picker paths
  What to do / Must NOT do: Record exact lines for the tmux mention in docs/features/terminal.md and the picker path (setChosenSessionName/finishConnect in ConnectionsViewModel.kt) from the todo-5 checkout; if either is absent, record the explicit fallback path instead of forcing it.
  Parallelization: Wave 2 | Blocked by: 5 | Blocks: 12,14
  References: todo-5 checkout, librarian path list (paths verified, lines unknown).
  Acceptance criteria: .omo/evidence/haven-psmux/task-7.txt holds line refs or an explicit fallback statement per path, and opens with an OUTCOME marker line, either `OUTCOME: VERIFIED` or `OUTCOME: FALLBACK:` with a reason (`rg -n "^OUTCOME:"` non-empty).
  QA scenarios: happy — refs resolve; failure — path absent means fallback recorded and draft adjusted, never fabricated. Evidence .omo/evidence/haven-psmux/task-7.txt.
  Commit: N | evidence only.
- [x] 8. Fetch precedent #611 plus #615 state
  What to do / Must NOT do: `gh issue view 611 --repo GlassHaven/Haven --json state,stateReason,closedAt,labels,title,url` and `gh pr view 615 --repo GlassHaven/Haven --json state,baseRefName,headRefName,url,title`; record state, URL, one-line relevance each.
  Parallelization: Wave 2 | Blocked by: 5 | Blocks: 14,17
  References: librarian precedent note, fixed feature skill triage table.
  Acceptance criteria: .omo/evidence/haven-psmux/task-8.txt holds both states plus URLs.
  QA scenarios: happy — both resolve; failure — numbers invalid means re-search by capability words and record corrected refs (todo 16 Branch B reuses this corrected path). Evidence .omo/evidence/haven-psmux/task-8.txt.
  Commit: N | evidence only.
- [x] 9. Record negative-search evidence for psmux
  What to do / Must NOT do: Run the exact search commands (`gh search issues --repo GlassHaven/Haven psmux` and the prs variant — no --state flag, default covers both states — plus `gh issue list --repo GlassHaven/Haven --search "psmux" --state all --limit 10` fallback) and paste command lines with outputs.
  Parallelization: Wave 2 | Blocked by: 5 | Blocks: 14
  References: librarian zero-hit claim (to reproduce, not to trust).
  Acceptance criteria: .omo/evidence/haven-psmux/task-9.txt holds commands plus outputs (empty expected).
  QA scenarios: happy — empty as claimed; failure — a hit appears means triage re-opens (comment vs new issue per table), plan does not proceed blind. Evidence .omo/evidence/haven-psmux/task-9.txt.
  Commit: N | evidence only.
- [x] 10. Resolve exact test commands plus commit style
  What to do / Must NOT do: From the todo-5 checkout enumerate the runnable unit-test invocation for the ssh module plus the full-build command (10-minute timeout each, smallest module scope first); run `git log --oneline -10` on the checkout to mimic Haven commit style. Record all three verbatim.
  Parallelization: Wave 2 | Blocked by: 5 | Blocks: 12,14,16,17
  References: todo-5 checkout, fixed PR skill test-evidence rule.
  Acceptance criteria: .omo/evidence/haven-psmux/task-10.txt holds copy-pasteable test commands plus the log sample, and opens with an `OUTCOME: VERIFIED` marker (`rg -n "^OUTCOME: VERIFIED"` non-empty); C4 stays blocked until this file exists.
  QA scenarios: happy — commands enumerated; failure — task names ambiguous means list candidates and pick by smallest module scope, recorded. Evidence .omo/evidence/haven-psmux/task-10.txt.
  Commit: N | evidence only.
- [x] 11. Verify psmux upstream CLI surface or record fallback
  What to do / Must NOT do: Fetch psmux/psmux README for the list/attach CLI surface usable over SSH (parity table, max 8 rows); check for a named Windows SSH target for the live demo; if none exists record the documented fallback (what counts as verify versus blocked) plus the maintainer-question template line for the issue body.
  Parallelization: Wave 2 | Blocked by: 5 | Blocks: 12,14
  References: https://github.com/psmux/psmux (owner-confirmed identity), draft psmux-citation assumption.
  Acceptance criteria: .omo/evidence/haven-psmux/task-11.txt holds either the verification table or the explicit blocked-fallback statement, opens with an OUTCOME marker line, either `OUTCOME: VERIFIED` or `OUTCOME: FALLBACK:` with a reason (`rg -n "^OUTCOME:"` non-empty); upstream is cited nowhere until this passes.
  QA scenarios: happy — surface verified; failure — unverifiable means fallback statement plus issue-body question, never a silent cite. Evidence .omo/evidence/haven-psmux/task-11.txt.
  Commit: N | evidence only.
- [x] 12. Author the PSMUX registry change plus tests on the recon checkout
  What to do / Must NOT do: On the todo-5 checkout, add the PSMUX registry entry mirroring the todo-6 TMUX shape plus new test coverage; run the todo-10 test commands (10-minute timeout); record exit codes plus suite tail. Max 2 fix cycles, then escalate to owner with evidence (re-gate, never silent widening). No commits here; no drive-by refactors.
  Parallelization: Wave 3 | Blocked by: 6,7,10,11 | Blocks: 14,15
  References: todos 6,7,10,11 evidence; todo-5 checkout path.
  Acceptance criteria: .omo/evidence/haven-psmux/task-12.txt holds the diff stat, exit codes (0 required), suite tail lines, pre/post gap-demo lines, and cycle count.
  QA scenarios: happy — green on first or second cycle; failure — still red after 2 cycles means escalate with evidence, worker stops this todo. Evidence .omo/evidence/haven-psmux/task-12.txt.
  Commit: N | commits happen on the fork branch at todo 17.
- [x] 13. Read-only restriction probe plus branch predicate
  What to do / Must NOT do: Run `gh auth status`, `gh api user --jq .login` (records <fork-user>), `gh api repos/GlassHaven/Haven --jq '{has_issues: .has_issues, visibility: .visibility}'`, and a fork-existence probe (`gh repo view <fork-user>/Haven --json isFork` — missing repo means no fork yet); record the Branch A / Branch B predicate and its inputs. Predicate rule: `has_issues:false` in the probe output means `OUTCOME: BRANCH-B` now; otherwise `OUTCOME: BRANCH-A` with the runtime denial at todo 16 as the only remaining B trigger. Must NOT run any create, push, or fork command in this todo.
  Parallelization: Wave 3 | Blocked by: - | Blocks: 16
  References: probe precedent (has_issues:true, zero psmux hits), draft issue-restriction assumption.
  Acceptance criteria: .omo/evidence/haven-psmux/task-13.txt records predicate (A: attempt issue; B: PR-only citing #611/#615) with reasons, and opens with an OUTCOME marker line, either `OUTCOME: BRANCH-A` or `OUTCOME: BRANCH-B:` with a reason (`rg -n "^OUTCOME: BRANCH-"` non-empty).
  QA scenarios: happy — predicate recorded; failure — probe inconclusive means default to A-with-fallback and say so. Evidence .omo/evidence/haven-psmux/task-13.txt.
  Commit: N | probe produces evidence only.
- [x] 14. Write issue-body.md to the feature bar
  What to do / Must NOT do: Write .omo/evidence/haven-psmux/issue-body.md with all 9 sections (Problem, Proposal, Non-goals, Acceptance checklist, Prior art with #611/#615, Gap evidence with codegraph receipts, Env-context verbatim, Counter-scenarios, PR status), plus one drafted title line recorded verbatim in task-14.txt and reused exactly in todos 15-17. Every quote carries its receipt. No TO-FILL left.
  Parallelization: Wave 3 | Blocked by: 6,7,8,9,10,12 | Blocks: 15
  References: todos 6-12 evidence (env lines draw on todos 8 and 10), C:\Users\Lance\.claude\skills\github-create-feature\SKILL.md Procedure step 3, draft Scope IN.
  Acceptance criteria: `rg -n "TO-FILL|TBD|TO-CONFIRM" .omo/evidence/haven-psmux/issue-body.md` returns empty AND all 9 sections present; output saved to .omo/evidence/haven-psmux/task-14.txt.
  QA scenarios: happy — rg empty, checklist complete; failure — any token present means RED, resolve from cited evidence, never delete the requirement. Evidence .omo/evidence/haven-psmux/task-14.txt plus issue-body.md.
  Commit: N | unfiled draft; filing is todo 16.
- [x] 15. Write pr-body.md to the PR bar
  What to do / Must NOT do: Write .omo/evidence/haven-psmux/pr-body.md (mechanism, linked-issue token <issue-n>, repro steps, expect-vs-actual, test evidence per todo-10 commands with exit codes from todo 12, env with base SHA, evidence quotes, scope map, counters). <issue-n> is the single allowed token until todo 16 resolves it.
  Parallelization: Wave 3 | Blocked by: 12,14 | Blocks: 17
  References: todo 14 body, todos 10 and 12 test evidence, C:\Users\Lance\.claude\skills\github-create-pr\SKILL.md Procedure step 3.
  Acceptance criteria: `rg -n "TO-FILL|TBD|TO-CONFIRM" .omo/evidence/haven-psmux/pr-body.md` returns empty (only <issue-n> permitted); output saved to .omo/evidence/haven-psmux/task-15.txt.
  QA scenarios: happy — gate passes; failure — any other token means RED, resolve from evidence. Evidence .omo/evidence/haven-psmux/task-15.txt plus pr-body.md.
  Commit: N | unfiled draft; filing is todo 17.
- [x] 16. Branch A: file the issue (authorize-gated)
  What to do / Must NOT do: Write .omo/evidence/haven-psmux/task-16-pre.txt (draft title, one-line capability, APPROVED token) and get explicit go-ahead first — forbid all of todos 16-17 without it. If task-13.txt shows `OUTCOME: BRANCH-B`, skip `gh issue create` and go straight to the pr-body rewrite below. Otherwise run `gh issue create --repo GlassHaven/Haven --title "<short, names the capability>" --body-file .omo/evidence/haven-psmux/issue-body.md`; capture URL and number, propagate the number into pr-body.md. On denial, capture the denial output, switch to Branch B with a written record, and rewrite pr-body.md for Branch B before todo 17: delete the `<issue-n>` line, insert `Related #611`, `Related #615` (or the corrected refs from task-8.txt when todo 8 re-searched), plus the standalone rationale. Never retry blindly.
  Parallelization: Wave 4 | Blocked by: 10,13,14,15 | Blocks: 17
  References: todo 14 body, todo 13 predicate, fixed feature skill authorize rule.
  Acceptance criteria: .omo/evidence/haven-psmux/task-16.txt holds the pre-approval reference plus either the issue URL/number or the denial output plus the branch-switch record.
  QA scenarios: happy — issue live, number propagated; failure — denial means Branch B path with rationale in the PR body, never silent. Evidence .omo/evidence/haven-psmux/task-16.txt.
  Commit: N | the public post is the record.
- [x] 17. Fork, push, create PR, link comment
  What to do / Must NOT do: On the todo-5 checkout: `git checkout -b feat/psmux-session-manager`; review `git status --porcelain`, then commit only the todo-12 files (scoped add of the registry file from task-6.txt plus the test files from task-12.txt, then commit with the message style recorded in task-10.txt); record `git status` plus `git diff --stat` in task-17.txt. Fork only when todo 13 shows no fork yet (`gh repo fork GlassHaven/Haven --clone=false`), then `git remote add fork https://github.com/<fork-user>/Haven.git` (<fork-user> from task-13.txt), push `git push -u fork feat/psmux-session-manager`, then `gh pr create --repo GlassHaven/Haven --base main --head <fork-user>:feat/psmux-session-manager --title "<short, names the capability>" --body-file .omo/evidence/haven-psmux/pr-body.md` (A: `Closes #<issue-n>`; B: the precedent refs from task-8.txt plus standalone rationale), then the link comment on the issue (A only): `gh issue comment <issue-n> --repo GlassHaven/Haven --body "PR attached: #<pr-n>"` (<issue-n> from todo 16, <pr-n> from the create output). Bodies from files only, never --fill or heredoc. Never push direct to upstream base.
  Parallelization: Wave 4 | Blocked by: 8,10,15,16 | Blocks: 18
  References: todos 10,13,15,16 evidence, fixed PR skill Procedure step 4 plus never-push-base rule.
  Acceptance criteria: .omo/evidence/haven-psmux/task-17.txt holds branch name, commit SHA, PR URL, pushed SHA, and comment ID (A) or PR URL plus #611 refs (B).
  QA scenarios: happy — `gh pr view` re-read matches the filed body; failure — any step fails means todo 18 owns recovery, never a second PR. Evidence .omo/evidence/haven-psmux/task-17.txt.
  Commit: Y on the fork branch per change, Haven style mimicked from todo-10 log | e.g. feat(ssh): add psmux session manager entry.
- [x] 18. Failure-path recovery plus clean-state confirm
  What to do / Must NOT do: If todo 17 had any failure, settle it the skill way (on A: `gh issue edit` with the issue number from task-16.txt and a corrected body file setting PR status blocked; on B: rationale recorded); wrong comments are removed via `gh api -X DELETE repos/GlassHaven/Haven/issues/comments/` plus the comment ID recorded in task-17.txt (issue and PR review comments share this API), never a stacked correction comment. Then re-read every live post and confirm clean state. Max 2 edit/delete cycles, then escalate to owner.
  Parallelization: Wave 4 | Blocked by: 17 | Blocks: 19
  References: todo 17 evidence, fixed skills Corrections sections.
  Acceptance criteria: .omo/evidence/haven-psmux/task-18.txt holds re-read outputs showing the settled state.
  QA scenarios: happy — clean; failure — residual wrong content past 2 cycles means escalate, stop, ask. Evidence .omo/evidence/haven-psmux/task-18.txt.
  Commit: Y on the fork branch only if recovery changed code | otherwise N.
- [x] 19. Independent re-audit of all posts
  What to do / Must NOT do: Hand post URLs, comment IDs, and SHAs to a fresh agent instructed to re-read each from GitHub and flag anything unverified, mis-stated, or contradictory; fix or delete every flagged item. Never self-certify. Re-run limited to the affected filing todo; no new scope.
  Parallelization: Wave 4 | Blocked by: 18 | Blocks: F1-F4
  References: todos 16-18 evidence, fixed skills re-audit sections.
  Acceptance criteria: .omo/evidence/haven-psmux/task-19.txt is a re-audit report with zero open flags.
  QA scenarios: happy — zero flags; failure — any flag means fix/delete plus targeted re-run of the affected todo, max 2 flag-fix re-runs, then escalate to owner with evidence and stop. Evidence .omo/evidence/haven-psmux/task-19.txt.
  Commit: Y on the fork branch only if the audit changed code | otherwise N.

## Final verification wave
> Runs in parallel after ALL todos. Each check writes its own evidence file (.omo/evidence/haven-psmux/task-F<n>.txt). ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.
- [x] F1. Plan compliance audit — every todo 1-19 has its evidence .txt at the recorded path with the acceptance output inside (named deliverables exempt: issue-body.md, pr-body.md, task-16-pre.txt); dependency order honored (16 gated on 10,13,14,15 with 8 transitively via 14; 19 before F-wave); Branch A/B artifacts match the todo-13 predicate or a recorded switch; task-16-pre.txt APPROVED present (sole sanctioned human step); plan sha256 via `Get-FileHash .omo/plans/haven-psmux.md` recorded in task-F1.txt and compared against .omo/evidence/haven-psmux/review-launch.txt (planner-written digest at review launch); dual review receipts (momus + independent oracle APPROVE lines with sha, planner-owned pre-handoff step) recorded in .omo/drafts/haven-psmux.md. Evidence .omo/evidence/haven-psmux/task-F1.txt.
- [x] F2. Code quality review — skill diffs minimal and additive; bodies match the bar templates section-for-section (9 issue sections verified); placeholder tokens limited to the Token registry set, all resolved (only <issue-n> may predate todo 16); title string identical across task-14.txt, bodies, task-16.txt, task-17.txt (`rg` equality); Branch B path asserts both precedent refs from task-8.txt present. Evidence .omo/evidence/haven-psmux/task-F2.txt.
- [x] F3. Real manual QA — live posts re-read via `gh issue view` (Branch A only) / `gh pr view` and quoted lines re-queried via codegraph on the persisted todo-5 checkout (temp dir intact per no-cleanup rule); quoted bytes match in all three places (post, evidence, checkout). Evidence .omo/evidence/haven-psmux/task-F3.txt.
- [x] F4. Scope fidelity — Must-NOT-haves intact: no tmux-path changes, no second manager, no registry redesign (or a recorded re-gate), no fabricated lines, no trial filing, no plain --force. Evidence .omo/evidence/haven-psmux/task-F4.txt.

## Commit strategy
- Skill files live in a non-git workspace: no commits possible; change receipts are the evidence files plus full re-reads (todos 1-4).
- Haven fork branch: one atomic commit per verified increment, Haven style mimicked from the todo-10 `git log` sample; message shape `feat(ssh): ...` unless the log sample dictates otherwise. Never one end-of-run omnibus.

## Success criteria
- C1: both skills at bar with tail complete, evidence green, versions exact (PR 0.1.1, feature 0.1.1).
- C2: every cited line resolves to codegraph/gh bytes; negative search reproducible from recorded commands.
- Code+tests: exit codes 0 recorded; suite tail captured.
- C3: rg gates empty; bodies filed from files only.
- C4: issue URL (A) or recorded denial plus rationale (B); PR URL plus SHA; link comment (A); re-audit zero flags.
- Dual review receipts recorded (momus + independent oracle approvals on the final sha256); live-plan validation matches the approved digest.

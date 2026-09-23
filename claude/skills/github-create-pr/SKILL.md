---
name: github-create-pr
description: This skill should be used when opening or filing a GitHub PR against a third-party repo — "open a PR upstream", "file a fix PR", "push my fix to a fork and open a PR", "fork and PR" — or after root-causing a bug in a third-party dependency/plugin/CLI where the fix belongs upstream. PR equals working fix plus fork path in hand. Symptom-only or fix-not-yet-made → github-create-issue. New feature, no bug → github-create-feature. Enforces upstream triage first (open PR vs new PR vs issue-only), then fork/base/head check, then the same diagnostic-depth bar as github-create-issue (exact file:line, quoted source, repro, environment, counter-scenarios tried, test output) before filing via `gh` CLI alone.
version: 0.1.1
---

PR get ignore or close when diff no proof carry. Skill lock depth at: reviewer must check claim self from PR body alone, run nothing else. Skill refuse file below this bar.

## Reference bar — depth only, plus diff

Calibrate depth to: https://github.com/code-yeongyu/oh-my-openagent/issues/6167 — match its depth, then add diff section from Procedure step 3 below. Exemplar already in file; no other URL invent.

## Upstream triage — do first, always

Fetch PR state AND linked-issue state AND fork state before pick update vs new PR vs issue-only:

```bash
gh auth status
gh pr list --repo <owner>/<repo> --head <push-user>:<branch> --state all --limit 10
gh pr view <n> --repo <owner>/<repo> --json state,baseRefName,headRefName,url,title
gh issue view <n> --repo <owner>/<repo> --json state,stateReason,closedAt,labels
gh api repos/<owner>/<repo>/issues/<n>/timeline --jq '.[] | select(.event=="closed" or .event=="cross-referenced") | {event:.event, actor:(.actor.login // null), at:.created_at}'
git status --short --branch
git log origin/<base>..HEAD --oneline
gh repo view <owner>/<repo> --json isFork,parent
gh repo view <owner>/<repo> --json viewerPermission --jq .viewerPermission
```

Probe `viewerPermission` first: `ADMIN`/`MAINTAIN`/`WRITE` → own branch allowed; `READ`/`TRIAGE`/`none` → fork path mandatory. Pick triage row on probe result, never on guess.

| situation                                                                                                    | action                                                                                                                                                              |
| ------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| open PR, same head, same mechanism                                                                           | update that PR; never duplicate                                                                                                                                     |
| merged PR, same diff, bug still reproduces                                                                   | regression → new branch, new PR citing old PR + old issue                                                                                                           |
| closed unmerged PR by human, same mechanism                                                                  | refile only with materially stronger case (new repro, narrower diff, new test)                                                                                      |
| stale-closed linked issue (`not_planned`, stale-bot or human) but mechanism still reproduces on current base | treat like closed unmerged: refile PR only with fresh repro on current base + cite old issue/PR; state why close reason wrong                                       |
| no push rights, no fork yet                                                                                  | `gh repo fork <owner>/<repo> --clone=false`, then `git remote add <fork-remote> git@github.com:<fork-user>/<repo>.git`, push to fork, `--head <fork-user>:<branch>` |
| push rights (`WRITE`+)                                                                                       | own branch on upstream, `--head <branch>`; still never push direct to base                                                                                          |
| maintainer prefers issue-only (CONTRIBUTING says so)                                                         | file issue via github-create-issue, skip PR, state why in draft                                                                                                     |
| base moved ahead                                                                                             | rebase on `origin/<base>`, retest, then file                                                                                                                        |

Read timeline, never label alone. Stale-bot `not_planned` on linked issue mean nothing about PR merit.

## Procedure

0. **Clone upstream to temp, index, quote file:line.** Never trust local checkout for mechanism claim:
   ```bash
   TMP=$(mktemp -d)
   git clone --depth 1 https://github.com/<owner>/<repo>.git "$TMP/upstream"
   codegraph init "$TMP/upstream"
   ```
   Run codegraph query there for responsible symbol/file before any mechanism claim. Quote `file:line` from codegraph output. Local working tree used for diff only, never for mechanism proof.

1. **Upstream triage first, then search.** Before draft anything:
   ```bash
   gh pr list --repo <owner>/<repo> --search "<mechanism words>" --state all --limit 15
   gh issue list --repo <owner>/<repo> --search "<mechanism words>" --state all --limit 15
   ```
   Search by **mechanism**, not symptom. Write in draft which PR/issue found and why chosen action follow from triage.

2. **No PR on symptom alone.** Root-cause first: read actual source (not doc, not guess) at file:line responsible. Quote it. State mechanism — what code do, why wrong for this env/input, what divergent value actually be. Diff must map 1:1 to mechanism; no drive-by refactors, no formatting churn.

3. **Match reference bar structure** when draft PR body:
   - Fix describe: mechanism, not just symptom
   - Linked issue: `Fixes #<n>` or `Related #<n>` on own line
   - Repro step: numbered, concrete, replayable (pre-fix fail → post-fix pass)
   - Expect vs actual: separate line, before and after values
   - Test evidence: exact command + verbatim output, fence block (at least one failing-before or passing-after line)
   - Env/doctor output: verbatim, fence block
   - Evidence: exact quote source (`file:line`), exact command output, side-by-side divergent values — never summary of logs
   - Scope: file list, why each file in, what left out
   - Mechanism understood → name responsible function/file, what correct fix be. Reviewers verify named hypothesis far faster than vague "fix stuff"

4. **Push + file with `gh` CLI alone** — see "gh CLI only" below for why.
   ```bash
   git push -u <fork-remote> <branch>
   gh pr create --repo <owner>/<repo> --base <base> --head <fork-user>:<branch> --title "<short, names the mechanism>" --body-file <path-to-body.md>
   ```
   `<fork-remote>` = remote add after fork: `git remote add <fork-remote> git@github.com:<fork-user>/<repo>.git`. Never push direct to upstream base (`origin/<base>`); fork remote or own feature branch only. Write body to file first. Never heredoc-inline body — heredoc mangle on Windows shell. Never `gh pr create --fill`; template above mandatory.

5. **Confirm authorize before file.** Push to fork + public PR = visible, hard-reverse action. State draft title + base/head + one-line mechanism, get explicit go-ahead before `git push` + `gh pr create` — unless user already give blanket authorize for this specific repo/session.

## Counter-scenarios — try them, then say so

Presume you tried them — then actually try them. Before filing, attempt at least one control that could disprove own fix, report outcome either way:

- Base updated + retest (fix still apply on fresh `origin/<base>`).
- Minimal vs full diff (prove each hunk needed; drop hunks that change nothing).
- Flag/config on vs off (isolate fix from setting).
- Same repro through second, independent tool path (isolate core from plugin).
- Repro pre-fix fail captured (stash fix, rerun repro, show fail line; unstash, show pass line).

Write outcome under **Counter-scenarios tried**, include any that fail to reproduce or favour other explain. Claim carry own falsify attempt trust far more.

## Environment block — software-maximalist, no hardware

See `github-create-issue`'s `references/shared-conventions.md` for which of the three skills fires on an ambiguous request, plus the Environment block, Corrections, Independent re-audit, and gh-CLI-only sections — identical across all three github-create-* skills.

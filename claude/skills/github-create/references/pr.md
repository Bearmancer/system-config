# Filing a PR

Shared mechanics (triage timeline command, triage principle, search-first, root-cause-first, body-to-file, fork-remote, indexed checkout) are in `SKILL.md` — this file has only the PR-specific triage table, procedure deltas, and counter-scenarios.

## Upstream triage — do first, always

```bash
gh auth status
gh pr list --repo <owner>/<repo> --head <push-user>:<branch> --state all --limit 10
gh pr view <n> --repo <owner>/<repo> --json state,baseRefName,headRefName,url,title
gh issue view <n> --repo <owner>/<repo> --json state,stateReason,closedAt,labels
gh api repos/<owner>/<repo>/issues/<n>/timeline --jq '.[] | select(.event=="closed" or .event=="cross-referenced") | {event:.event, actor:(.actor.login // null), at:.created_at}'
git status --short --branch
git log origin/<base>..HEAD --oneline
gh repo view <owner>/<repo> --json isFork,parent,viewerPermission
```

Probe `viewerPermission` first: `ADMIN`/`MAINTAIN`/`WRITE` → own branch allowed; `READ`/`TRIAGE`/`none` → fork path mandatory. Pick the triage row on probe result, never on guess.

| situation | action |
| --------- | ------ |
| open PR, same head, same mechanism | update that PR; never duplicate |
| merged PR, same diff, bug still reproduces | regression → new branch, new PR citing old PR + old issue |
| closed unmerged PR by human, same mechanism | refile only with materially stronger case (new repro, narrower diff, new test) |
| stale-closed linked issue (`not_planned`, stale-bot or human) but mechanism still reproduces on current base | refile PR with fresh repro on current base + cite old issue/PR; state why the close reason was wrong |
| no push rights, no fork yet | `gh repo fork <owner>/<repo> --clone=false`, add fork remote (see `SKILL.md`), push to fork, `--head <fork-user>:<branch>` |
| push rights (`WRITE`+) | own branch on upstream, `--head <branch>`; still never push direct to base |
| maintainer prefers issue-only (CONTRIBUTING says so) | file issue only (`references/issue.md`), skip PR, state why in draft |
| base moved ahead | rebase on `origin/<base>`, retest, then file |

Note this table's stale-closed row is looser than the issue table's "truly declined" row: a PR with a fresh repro on current base can still refile even against a human `not_planned` close, because the diff itself is the stronger case.

## Procedure

0. Indexed checkout, read-only proof (shared mechanics, `--depth 1` variant) — quote `file:line` from there; local working tree is for diff only.
1. Upstream triage first (table above), then search by mechanism:
   ```bash
   gh pr list --repo <owner>/<repo> --search "<mechanism words>" --state all --limit 15
   gh issue list --repo <owner>/<repo> --search "<mechanism words>" --state all --limit 15
   ```
2. Root-cause per shared mechanics. Diff must map 1:1 to mechanism; no drive-by refactors, no formatting churn.
3. Draft body matching the reference bar:
   - Fix describe: mechanism, not just symptom
   - Linked issue: `Fixes #<n>` or `Related #<n>` on its own line
   - Repro step: numbered, concrete, replayable (pre-fix fail → post-fix pass)
   - Expect vs actual: separate line, before and after values
   - Test evidence: exact command + verbatim output, fence block (at least one failing-before or passing-after line)
   - Env/doctor output: verbatim, fence block
   - Evidence: exact quote source (`file:line`), exact command output, side-by-side divergent values — never a summary of logs
   - Scope: file list, why each file is in, what's left out
   - Mechanism understood → name the responsible function/file and what the correct fix needs
4. Push + file:
   ```bash
   git push -u <fork-remote> <branch>
   gh pr create --repo <owner>/<repo> --base <base> --head <fork-user>:<branch> --title "<short, names the mechanism>" --body-file <path-to-body.md>
   ```
5. Confirm before filing (see `SKILL.md` — push to fork + public PR both count), then run the commands.

## Counter-scenarios for a PR

- Base updated + retest (fix still apply on fresh `origin/<base>`).
- Minimal vs full diff (prove each hunk needed; drop hunks that change nothing).
- Flag/config on vs off (isolate fix from setting).
- Same repro through second, independent tool path (isolate core from plugin).
- Repro pre-fix fail captured (stash fix, rerun repro, show fail line; unstash, show pass line).

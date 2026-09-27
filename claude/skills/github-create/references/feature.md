# Filing a feature (issue + PR together)

Default: issue + PR together. Issue-only needs a stated reason.

Shared mechanics (triage timeline command, triage principle, search-first, root-cause-first, body-to-file, fork-remote, indexed checkout) are in `SKILL.md` — this file has only the feature-specific triage table, procedure deltas, and counter-scenarios.

## Triage — do first, always

```bash
gh auth status
gh issue list --repo <owner>/<repo> --search "<capability words>" --state all --limit 15
gh pr list --repo <owner>/<repo> --search "<capability words>" --state all --limit 15
gh issue view <n> --repo <owner>/<repo> --json state,stateReason,closedAt,labels
gh api repos/<owner>/<repo>/issues/<n>/timeline --jq '.[] | select(.event=="closed" or .event=="cross-referenced") | {event:.event, actor:(.actor.login // null), at:.created_at}'
gh repo view <owner>/<repo> --json isFork,parent,viewerPermission
git status --short --branch
```

Fork/add-remote only when no fork yet exists (see `SKILL.md` for the fork-remote definition). Never push to `origin` on an upstream checkout.

| state | reason | closing actor | action |
| ----- | ------ | -------------- | ------ |
| open issue/PR, same capability | — | — | comment with new evidence or adopt that thread; never duplicate |
| closed | not_planned | `github-actions[bot]` | stale-bot close, not a rejection → file NEW issue citing old number, then PR |
| closed | completed | human/bot | shipped; if a gap remains → new issue citing old, scoped to remainder, then PR |
| closed | not_planned | human | truly declined; refile only with materially stronger case (new impact, new users, narrower scope, working PR attached) |
| CONTRIBUTING says proposal-only | — | — | issue-only, state why, skip PR |

## Procedure

0. Indexed checkout that becomes the working tree (shared mechanics, full-clone variant — no `--depth 1`, since this checkout gets branched, built, and pushed from). Quote gap source and change hunks from it only; stale index → `codegraph init` again before quoting.
1. Triage first (table above), then search by **capability**, not title words — a closed thread with the same capability decides comment vs new issue.
2. Prove the gap, not the wish: read actual source at file:line where the capability is missing or blocked. Quote it. State mechanism — what the code does today, why it's insufficient for this use, what the divergent behavior actually is. Show a minimal gap demo (repro or before-behavior output, verbatim).
3. Draft issue body matching the reference bar:
   - Problem: who's blocked, what job fails, impact size
   - Proposal: proposed behavior, concrete, scoped
   - Non-goals: what's explicitly out, to bound review
   - Acceptance criteria: checklist, each verifiable (`- [ ] ...`)
   - Prior art: 2+ links (other tool, docs, related issue) with one-line note each
   - Gap evidence: exact quote source (`file:line`), exact demo output, never a summary
   - Env-context: verbatim where gap observed, fence block
   - Unless-impossible note: if a PR cannot attach, state the exact blocker under **PR status**
4. Attach the PR in the same pass unless impossible. Build, test, push first, then issue create, then PR create, then comment link:
   - Linked issue: `Closes #<n>` (only when the PR fully satisfies acceptance) or `Related #<n>`
   - Change describe: mechanism, file list, what's left out
   - Test evidence: exact command + verbatim output (new test name visible)
   - Expect vs actual: separate line, before and after values
   - Scope: each hunk maps to one acceptance item; no drive-by refactors
   ```bash
   git push -u <fork-remote> <branch>
   gh issue create --repo <owner>/<repo> --title "<short, names the capability>" --body-file <issue-body.md>
   gh pr create --repo <owner>/<repo> --base <base> --head <fork-user>:<branch> --title "<short, names the capability>" --body-file <pr-body.md>
   gh issue comment <issue-n> --repo <owner>/<repo> --body "PR attached: #<pr-n>"
   ```
   Failed push or failed PR create → `gh issue edit <issue-n> --repo <owner>/<repo> --body-file <file>` set **PR status: blocked by <reason>** in the same pass, never silent.
   Impossible means only: no push/fork rights obtainable, change spans private code, maintainer demands proposal-only, or diff exceeds reviewable scope and cannot narrow. Then issue-only with **PR status: blocked by <reason>** — never silent.
5. Confirm before filing (see `SKILL.md` — public issue + push + public PR all count), then run the commands.

## Counter-scenarios for a feature

- Issue half: existing workaround tried (config/flag/script) and why it fails; same gap through second tool path; narrower scope considered and why kept/dropped.
- PR half: base updated + retest; flag off/on (prove new behavior gated right); empty-state + populated-state; minimal vs full diff (prove each hunk needed).
- Pre-change behavior captured verbatim (stash or base checkout show old output; unstash show new output).

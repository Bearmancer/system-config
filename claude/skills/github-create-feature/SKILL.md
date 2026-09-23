---
name: github-create-feature
description: This skill should be used when requesting plus building a feature on a third-party repo — "request this feature upstream", "propose and implement feature", "file feature with PR", "add capability upstream" — or when a capability gap needs both a tracked proposal and working code. Feature equals new capability needing proposal plus code. Proposal-only without code belongs to github-create-issue; fix or change under existing issue belongs to github-create-pr. See also siblings github-create-issue, github-create-pr. Enforces duplicate search by capability first, then files a feature-request issue, then attaches a PR implementing it in the same pass — unless impossible (no push/fork rights, private-only change, maintainer wants proposal-only). Holds both posts to the github-create-issue diagnostic bar (exact file:line, quoted source, repro/gap demo, environment, counter-scenarios tried) before filing via `gh` CLI alone.
version: 0.1.1
---

Feature post get ignore when wish alone, no gap proof show. Skill lock depth at: reviewer must check gap + scope + acceptance self from issue alone, and mechanism + tests self from PR alone. Skill refuse file below this bar. Default: issue + PR together. Issue-only need stated reason.

## Reference bar

Calibrate depth only from issue half: https://github.com/code-yeongyu/oh-my-openagent/issues/6167 — match its depth, not its bug shape. Feature issue use Problem/Proposal/Acceptance structure per Procedure step 3 below, not bug repro shape. PR half add diff + tests. Structure to match: Procedure steps 3–4 below.

Sibling route: proposal-only without code → github-create-issue; fix or change under existing issue → github-create-pr.

## Triage — do first, always

Fetch duplicate state AND closing actor AND fork state before pick comment vs new issue vs issue+PR:

```bash
gh auth status
gh issue list --repo <owner>/<repo> --search "<capability words>" --state all --limit 15
gh pr list --repo <owner>/<repo> --search "<capability words>" --state all --limit 15
gh issue view <n> --repo <owner>/<repo> --json state,stateReason,closedAt,labels
gh api repos/<owner>/<repo>/issues/<n>/timeline --jq '.[] | select(.event=="closed" or .event=="cross-referenced") | {event:.event, actor:(.actor.login // null), at:.created_at}'
gh repo view <owner>/<repo> --json isFork,parent
gh repo view <owner>/<repo> --json viewerPermission --jq .viewerPermission
# only when no fork yet: gh repo fork <owner>/<repo> --clone=false
# only when forked new: git remote add <fork-remote> https://github.com/<fork-user>/<repo>.git
git status --short --branch
```

`<fork-remote>` = local remote name point at your fork (e.g. `fork`); `<fork-user>` = your GitHub user own the fork. Define both before any push. Never push to `origin` on upstream checkout.

| state | reason | closing actor | action |
| ----- | ------ | ------------- | ------ |
| open issue/PR, same capability | — | — | comment with new evidence or adopt that thread; never duplicate |
| closed | not_planned | `github-actions[bot]` | **stale-bot close, NOT rejection** → file NEW issue citing old number, then PR |
| closed | completed | human/bot | shipped; if gap remain → new issue citing old, scoped to remainder, then PR |
| closed | not_planned | human | truly declined; refile only with materially stronger case (new impact, new users, narrower scope, working PR attached) |
| CONTRIBUTING says proposal-only | — | — | issue-only, state why, skip PR |

`not_planned` stamp by bot mean nothing — read timeline, never label alone. **Comment on stale-closed thread be dead letter.**

## Procedure

0. **Indexed checkout for PR half.** All file:line quotes come from indexed checkout, never memory:
    ```bash
    git clone https://github.com/<owner>/<repo>.git $(mktemp -d)/<repo>
    codegraph init
    ```
    Quote gap source and change hunks from this checkout only. Stale index (moved lines, missing symbols) → `codegraph init` again before quote.

1. **Triage first, then search.** Before draft anything:
   ```bash
   gh issue list --repo <owner>/<repo> --search "<capability words>" --state all --limit 15
   gh pr list --repo <owner>/<repo> --search "<capability words>" --state all --limit 15
   ```
   Search by **capability**, not title words — closed thread with same capability decide comment vs new issue. Write in draft which thread found and why chosen action follow from triage.

2. **No file on wish alone.** Prove gap first: read actual source (not doc, not guess) at file:line where capability missing or blocked. Quote it. State mechanism — what code do today, why insufficient for this use, what divergent behavior actually be. Show gap demo: minimal repro or before-behavior output, verbatim.

3. **Match reference bar structure** when draft issue body:
   - Problem: who blocked, what job fail, impact size
   - Proposal: proposed behavior, concrete, scoped
   - Non-goals: what explicitly out, to bound review
   - Acceptance criteria: checklist, each verifiable (`- [ ] ...`)
   - Prior art: 2+ links (other tool, docs, related issue) with one-line note each
   - Gap evidence: exact quote source (`file:line`), exact demo output, never summary
   - Env-context: verbatim where gap observed, fence block
   - Unless-impossible note: if PR cannot attach, state exact blocker under **PR status**

4. **Attach PR in same pass unless impossible.** Build plus test plus push first, then issue create, then PR create, then comment link. Branch, build narrowly, test, push to `<fork-remote>`, then file issue, then PR body match reference bar:
    - Linked issue: `Closes #<n>` or `Related #<n>` (use `Closes` only when PR fully satisfy acceptance)
    - Change describe: mechanism, file list, what left out
    - Test evidence: exact command + verbatim output (new test name visible)
    - Expect vs actual: separate line, before and after values
    - Scope: each hunk map to one acceptance item; no drive-by refactors
    ```bash
    git push -u <fork-remote> <branch>
    gh issue create --repo <owner>/<repo> --title "<short, names the capability>" --body-file <issue-body.md>
    gh pr create --repo <owner>/<repo> --base <base> --head <fork-user>:<branch> --title "<short, names the capability>" --body-file <pr-body.md>
    gh issue comment <issue-n> --repo <owner>/<repo> --body "PR attached: #<pr-n>"
    ```
    Write bodies to files first. Never heredoc-inline — heredoc mangle on Windows shell. Never `--fill`.
    Failed push or failed PR create → `gh issue edit <issue-n> --repo <owner>/<repo> --body-file <file>` set **PR status: blocked by <reason>** same pass, never silent.
    Impossible mean only: no push/fork rights obtainable, change span private code, maintainer demand proposal-only, or diff exceed reviewable scope and cannot narrow. Then issue-only with **PR status: blocked by <reason>** — never silent.

5. **Confirm authorize before file.** Public issue + push + public PR = visible, hard-reverse actions. State draft titles + base/head + one-line capability, get explicit go-ahead before run `gh issue create` + push + `gh pr create` — unless user already give blanket authorize for this specific repo/session.

## Counter-scenarios — try them, then say so

Presume you tried them — then actually try them. Before filing, attempt at least one control per half, report outcome either way:

- Issue half: existing workaround tried (config/flag/script) and why fail; same gap through second tool path; narrower scope considered and why kept/dropped.
- PR half: base updated + retest; flag off/on (prove new behavior gated right); empty-state + populated-state; minimal vs full diff (prove each hunk needed).
- Pre-change behavior captured verbatim (stash or base checkout show old output; unstash show new output).

Write outcome under **Counter-scenarios tried** in each body, include any that fail to reproduce or favour other explain. Claim carry own falsify attempt trust far more.

## Environment block — software-maximalist, no hardware

See `github-create-issue`'s `references/shared-conventions.md` for which of the three skills fires on an ambiguous request, plus the Environment block, Corrections, Independent re-audit, and gh-CLI-only sections — identical across all three github-create-* skills.

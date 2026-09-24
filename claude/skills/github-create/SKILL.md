---
name: github-create
description: This skill should be used when filing, opening, or requesting anything on GitHub against a third-party repo — an issue ("file an issue", "report this bug upstream", "create a repo issue"), a PR ("open a PR upstream", "file a fix PR", "fork and PR"), or a feature ("request this feature upstream", "propose and implement feature", "add capability upstream") — or after root-causing a bug in a third-party dependency/plugin/CLI that needs tracking or fixing upstream. Routes internally by what's in hand — symptom with no fix → issue; fix in hand with fork/base/head resolvable → PR; capability that doesn't exist yet → feature (files the issue, then attaches an implementing PR in the same pass). Enforces triage first (closure/upstream/duplicate state decides comment vs new post), then a fixed diagnostic-depth bar (exact file:line, quoted source, repro, environment, counter-scenarios tried) before filing via `gh` CLI alone.
version: 0.2.0
---

Bug report, PR, or feature post get ignore or bounce back when claim carry no proof. Skill lock depth at: reviewer must check every claim against source/diff/demo alone, run nothing else. Skill refuse file below this bar.

## Which shape fires

A request names a symptom with no fix in hand → **Filing an issue**.
A request carries a fix for an existing bug, fork/base/head already resolvable → **Filing a PR**.
A request asks for a capability that doesn't exist yet → **Filing a feature** (files the feature-request issue, then attaches an implementing PR in the same pass).
A request could read as more than one of the above → **Filing an issue**: cheapest, most reversible, and every fix or feature still starts from a filed issue.

## Reference bar

Calibrate depth to https://github.com/code-yeongyu/oh-my-openagent/issues/6167 for every shape below — issue and PR match its depth directly; feature matches its depth for the issue half only (Problem/Proposal/Acceptance structure, not bug-repro shape), then adds diff + tests for the PR half. No other calibration URL invent.

## Confirm before filing

Filing anything on GitHub is visible and hard to reverse (can't unpublish a community discussion). Before running any create/push command below, state the draft title(s) + one-line summary (plus base/head for a PR) and get explicit go-ahead — unless the user already gave blanket authorization for this specific repo/session.

## Counter-scenarios — try them, then say so

Presume you tried them, then actually try them. Before filing any shape, attempt at least one control that could disprove your own claim, and write the outcome under **Counter-scenarios tried** — including anything that fails to reproduce or favors another explanation. A claim that carries its own falsification attempt is trusted far more. Per-shape controls are listed in each section below.

## Environment block — software-maximalist, no hardware

Software fact only. Never CPU/GPU/RAM/model, never hostname/username/tokens.

- OS: caption, version, build, architecture — **verify, never guess** (Win10 and Win11 both report `Windows 10.0.x`; build `19045` = Win10 22H2, `22000+` = Win11)
- App: opencode version; plugin names + versions
- Runtime/deps: node, npm/pnpm/bun, python, dotnet — whatever repro touch
- Base SHA: `git rev-parse origin/<base>` short SHA in body (PR context only)
- Every binary repro name, with its version
- Config excerpt (relevant keys, verbatim)
- **Logs + tests — always.** At least one verbatim test/repro line show divergent value pre-fix and post-fix, plus file path
- `gh --version`; `git --version`

Collect on Windows with CIM one-liner (faster than built-in `systeminfo`):

```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,OSArchitecture
node --version; npm --version; bun --version
gh --version; git --version
<tool> --version
```

## Corrections: edit, don't stack

- Own issue/PR body wrong → `gh issue edit <n> --repo <owner>/<repo> --body-file <file>` / `gh pr edit <n> --repo <owner>/<repo> --body-file <file>`
- Title wrong → `gh pr edit <n> --repo <owner>/<repo> --title "<new>"` (PR context)
- Bad comment → `gh api -X DELETE repos/<owner>/<repo>/issues/comments/<comment_id>`
- New commits after review → push same branch, update PR, comment link on issue; never open second PR (PR context)
- Post-review rebase → `git push --force-with-lease <fork-remote> <branch>`; never plain `--force` (PR context)
- Never post a "correction" comment that supersedes an earlier wrong one — delete the earlier one instead.
- Environment mistake is the most common correction: verify before posting; if one slips through, edit or delete — never append.

## Independent re-audit

After filing, hand the full list of posts (issue number + PR number + comment IDs + pushed SHAs as applicable) to a fresh agent with instructions to **independently** re-read each post from GitHub, check every claim against the machine and source, and flag anything unverified, mis-stated, or contradicted. Fix or delete flagged items. Never self-certify.

## gh CLI only — no GitHub plugin/MCP needed

Use `gh` via Bash for all of this. No reach for a GitHub plugin/MCP server unless the user has one enabled and asks specifically. Issue search, issue create, issue comment, PR create, PR edit, fork — all single `gh` subcommands, plain-text or `--json` output. No multi-step orchestration, no auth flow beyond `gh auth status`, a wrapper adds nothing on top. A GitHub plugin/MCP server adds dependency and permission surface for zero behavior gain on this task shape.

### gh CLI extras worth knowing here

- `--json` with no field list prints every available field for that command — use it once to discover a field before guessing its name.
- `--jq '<expr>'` filters `--json` output inline; skip piping to a separate `jq`/`jaq` process.
- Checking one file in the target repo without a clone: `gh repo read-file <path> --repo <owner>/<repo> --jq .` for JSON metadata, or plain `gh repo read-file <path> --repo <owner>/<repo>` for raw content — faster than a clone when the issue-filing procedure only needs one file's current content, not a full mechanism trace.
- Cross-repo or qualifier-rich duplicate search: `gh search issues|prs repo:<owner>/<repo> is:open <mechanism words>` (bare tokens, GitHub's search index, full `is:`/`author:`/`label:` syntax) — reach for this over `gh issue/pr list --search "<quoted string>"` when the search needs qualifiers beyond one repo, or `--search-type semantic` when the request is phrased in natural language rather than exact terms.
- Formal issue/PR linking beyond a body-text `Closes #<n>`: `gh issue edit <n> --repo <owner>/<repo> --add-sub-issue <child-n>` or `--parent <n>` for a real sub-issue hierarchy; `--add-blocked-by`/`--add-blocking <n>` for a blocking relationship GitHub renders natively.
- Repro screenshot or clip: `--attach <path>` on `issue create`, `issue comment`, `pr create`, or `pr comment` — repeatable for multiple files, `#alt text` after the path — instead of describing a visual in prose.
- Anything `--json` doesn't expose: `gh api repos/<owner>/<repo>/pulls/<n>/comments` for PR review-thread comments (`--comments` on `pr view` shows issue-level comments only), or `gh api graphql -f query='...'` for arbitrary GraphQL.

---

## Filing an issue

### Closure triage — do first, always

Fetch closure state AND closing actor before picking comment vs new issue:

```bash
gh issue view <n> --repo <owner>/<repo> --json state,stateReason,closedAt,labels
gh api repos/<owner>/<repo>/issues/<n>/timeline --jq '.[] | select(.event=="closed") | {actor:.actor.login, at:.created_at}'
```

| state  | reason      | closing actor         | action                                                                                                                                               |
| ------ | ----------- | --------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| open   | —           | —                     | comment with new evidence; never refile                                                                                                              |
| closed | not_planned | `github-actions[bot]` | **stale-bot close, NOT a rejection** — bot text says "if the issue is still relevant please open a new one" → file a NEW issue citing the old number |
| closed | completed   | human/bot             | fix was claimed; if it still reproduces → regression → file a NEW issue citing the old number                                                        |
| closed | not_planned | human                 | truly declined; refile only with a materially stronger case (new impact, new mechanism, or one-line-fix argument)                                    |

`not_planned` stamp by bot mean nothing, just GitHub default for stale close — read timeline, never label alone. **Comment on stale-closed thread be dead letter.**

### Procedure

1. **Closure triage first, then search.** Before draft anything:
   ```bash
   gh issue list --repo <owner>/<repo> --search "<mechanism words>" --state all --limit 15
   ```
   Search by **mechanism**, not symptom — closed issue with same mechanism decide comment vs new issue. Write in draft which issue found and why chosen action follow from triage.

2. **No file on symptom alone.** Root-cause first: read actual source (not doc, not guess) at file:line responsible. Quote it. State mechanism — what code do, why wrong for this env/input, what divergent value actually be.

3. **Match reference bar structure** when draft issue body:
   - Bug describe: mechanism, not just symptom
   - Repro step: numbered, concrete, replayable
   - Expect vs actual: separate line
   - Env/doctor output: verbatim, fence block
   - Evidence: exact quote source (`file:line`), exact command output,
     side-by-side divergent values — never summary of logs
   - Mechanism understood → name responsible function/file, what correct fix be
     needs. Reviewers verify named hypothesis far faster than vague
     "something's wrong here"

4. **File with `gh` CLI alone**:
   ```bash
   gh issue create --repo <owner>/<repo> --title "<short, names the mechanism>" --body-file <path-to-body.md>
   ```
   Write body to file first. Never heredoc-inline body — heredoc mangle on Windows shell.

5. **Confirm before filing** (see above), then run the command.

### Counter-scenarios for an issue

- A/B suspected variable (set config value to distinguishable one, restart, re-read log — e.g. `agents.explore.model = <unique-id>`, then check created session's `model.id`).
- Warm vs cold start (server's first request often return nothing).
- Marker-present vs marker-free directory (root-gated servers).
- Identical bytes under different extension/format (isolate routing from parsing).
- Same file through second, independent tool path (isolate core from plugin).

## Filing a PR

### Upstream triage — do first, always

Fetch PR state AND linked-issue state AND fork state before pick update vs new PR vs issue-only:

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

Probe `viewerPermission` first: `ADMIN`/`MAINTAIN`/`WRITE` → own branch allowed; `READ`/`TRIAGE`/`none` → fork path mandatory. Pick triage row on probe result, never on guess.

| situation | action |
| --------- | ------ |
| open PR, same head, same mechanism | update that PR; never duplicate |
| merged PR, same diff, bug still reproduces | regression → new branch, new PR citing old PR + old issue |
| closed unmerged PR by human, same mechanism | refile only with materially stronger case (new repro, narrower diff, new test) |
| stale-closed linked issue (`not_planned`, stale-bot or human) but mechanism still reproduces on current base | treat like closed unmerged: refile PR only with fresh repro on current base + cite old issue/PR; state why close reason wrong |
| no push rights, no fork yet | `gh repo fork <owner>/<repo> --clone=false`, then `git remote add <fork-remote> git@github.com:<fork-user>/<repo>.git`, push to fork, `--head <fork-user>:<branch>` |
| push rights (`WRITE`+) | own branch on upstream, `--head <branch>`; still never push direct to base |
| maintainer prefers issue-only (CONTRIBUTING says so) | file issue only (see Filing an issue), skip PR, state why in draft |
| base moved ahead | rebase on `origin/<base>`, retest, then file |

Read timeline, never label alone. Stale-bot `not_planned` on linked issue mean nothing about PR merit.

### Procedure

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

4. **Push + file with `gh` CLI alone**:
   ```bash
   git push -u <fork-remote> <branch>
   gh pr create --repo <owner>/<repo> --base <base> --head <fork-user>:<branch> --title "<short, names the mechanism>" --body-file <path-to-body.md>
   ```
   `<fork-remote>` = remote add after fork: `git remote add <fork-remote> git@github.com:<fork-user>/<repo>.git`. Never push direct to upstream base (`origin/<base>`); fork remote or own feature branch only. Write body to file first. Never heredoc-inline body — heredoc mangle on Windows shell. Never `gh pr create --fill`; template above mandatory.

5. **Confirm before filing** (see above — push to fork + public PR both count), then run the commands.

### Counter-scenarios for a PR

- Base updated + retest (fix still apply on fresh `origin/<base>`).
- Minimal vs full diff (prove each hunk needed; drop hunks that change nothing).
- Flag/config on vs off (isolate fix from setting).
- Same repro through second, independent tool path (isolate core from plugin).
- Repro pre-fix fail captured (stash fix, rerun repro, show fail line; unstash, show pass line).

## Filing a feature (issue + PR together)

Default: issue + PR together. Issue-only needs a stated reason.

### Triage — do first, always

Fetch duplicate state AND closing actor AND fork state before pick comment vs new issue vs issue+PR:

```bash
gh auth status
gh issue list --repo <owner>/<repo> --search "<capability words>" --state all --limit 15
gh pr list --repo <owner>/<repo> --search "<capability words>" --state all --limit 15
gh issue view <n> --repo <owner>/<repo> --json state,stateReason,closedAt,labels
gh api repos/<owner>/<repo>/issues/<n>/timeline --jq '.[] | select(.event=="closed" or .event=="cross-referenced") | {event:.event, actor:(.actor.login // null), at:.created_at}'
gh repo view <owner>/<repo> --json isFork,parent,viewerPermission
git status --short --branch
# only when no fork yet:
gh repo fork <owner>/<repo> --clone=false
git remote add <fork-remote> https://github.com/<fork-user>/<repo>.git
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

### Procedure

0. **Indexed checkout for PR half.** All file:line quotes come from indexed checkout, never memory:
    ```bash
    D=$(mktemp -d)/<repo>
    git clone https://github.com/<owner>/<repo>.git "$D"
    codegraph init "$D"
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

5. **Confirm before filing** (see above — public issue + push + public PR all count), then run the commands.

### Counter-scenarios for a feature

- Issue half: existing workaround tried (config/flag/script) and why fail; same gap through second tool path; narrower scope considered and why kept/dropped.
- PR half: base updated + retest; flag off/on (prove new behavior gated right); empty-state + populated-state; minimal vs full diff (prove each hunk needed).
- Pre-change behavior captured verbatim (stash or base checkout show old output; unstash show new output).

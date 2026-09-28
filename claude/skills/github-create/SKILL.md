---
name: github-create
description: This skill should be used when filing, opening, or requesting anything on GitHub against a third-party repo — an issue ("file an issue", "report this bug upstream", "create a repo issue"), a PR ("open a PR upstream", "file a fix PR", "fork and PR"), or a feature ("request this feature upstream", "propose and implement feature", "add capability upstream") — or after root-causing a bug in a third-party dependency/plugin/CLI that needs tracking or fixing upstream. Routes internally by what's in hand — symptom with no fix → issue; fix in hand with fork/base/head resolvable → PR; capability that doesn't exist yet → feature (files the issue, then attaches an implementing PR in the same pass). Enforces triage first (closure/upstream/duplicate state decides comment vs new post), then a fixed diagnostic-depth bar (exact file:line, quoted source, repro, environment, counter-scenarios tried) before filing via `gh` CLI alone.
version: 0.3.0
---

Bug report, PR, or feature post get ignore or bounce back when claim carry no proof. Reviewer check every claim against source/diff/demo alone. Refuse file below bar.

## Which shape fires

A request names a symptom with no fix in hand → **Filing an issue** (`references/issue.md`).
A request carries a fix for an existing bug, fork/base/head already resolvable → **Filing a PR** (`references/pr.md`).
A request asks for a capability that doesn't exist yet → **Filing a feature** (`references/feature.md`) — files the feature-request issue, then attaches an implementing PR in the same pass.
A request could read as more than one of the above → **Filing an issue**: cheapest, most reversible, and every fix or feature still starts from a filed issue.

## Reference bar

Calibrate depth to https://github.com/code-yeongyu/oh-my-openagent/issues/6167 for every shape — issue and PR match its depth directly; feature matches its depth for the issue half only (Problem/Proposal/Acceptance structure, not bug-repro shape), then adds diff + tests for the PR half. No other calibration URL invent.

## Confirm before filing

Filing anything on GitHub is visible and hard to reverse (can't unpublish a community discussion). Before running any create/push command, state the draft title(s) + one-line summary (plus base/head for a PR) and get explicit go-ahead — unless the user already gave blanket authorization for this specific repo/session.

## Counter-scenarios — try them, then say so

Presume you tried them, then actually try them. Before filing any shape, attempt at least one control that could disprove your own claim, and write the outcome under **Counter-scenarios tried** — including anything that fails to reproduce or favors another explanation. A claim that carries its own falsification attempt is trusted far more. Per-shape controls are in each reference file.

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

## URL audit

Every URL in a body or comment (links, prior art, docs) passes `deep-research` SKILL.md "URL audit" before posting. Placeholder `<owner>/<repo>` URLs exempt.

## Independent re-audit

After filing, hand the full list of posts (issue number + PR number + comment IDs + pushed SHAs as applicable) to a fresh agent with instructions to **independently** re-read each post from GitHub, check every claim against the machine and source, and flag anything unverified, mis-stated, or contradicted. Fix or delete flagged items. Never self-certify.

## gh CLI only — no plugin/MCP

Use `gh` via Bash for everything below; no GitHub plugin/MCP unless the user has one enabled and asks specifically.

For general `gh` mechanics — `--json`/`--jq`, pagination, search vs list, sub-issue/blocking flags, `--attach`, `gh api` fallback for review-thread comments and GraphQL — see the `gh` skill. Don't re-derive those here.

github-create-specific extras the `gh` skill doesn't cover:
- One file, no mechanism trace needed → `gh repo read-file <path> --repo <owner>/<repo>` instead of a clone.
- Visual repro → `--attach <path>` on the create/comment command instead of describing it in prose.

## Shared mechanics (used by every shape)

**Triage timeline command** — always pull this before deciding comment vs new post vs update:
```bash
gh api repos/<owner>/<repo>/issues/<n>/timeline --jq '.[] | select(.event=="closed" or .event=="cross-referenced") | {event:.event, actor:(.actor.login // null), at:.created_at}'
```

**Triage principle**: a bot-applied `not_planned` stamp means nothing — it's GitHub's default stale-close, not a rejection. Read the timeline, never the label alone. A comment on a stale-closed thread is a dead letter — file a new post citing the old number instead.

**Search before drafting**: search by mechanism/capability, not by symptom/title words — a closed thread with the same underlying mechanism decides comment vs new post. Write in the draft which thread was found and why the chosen action follows from triage.

**Root-cause first**: never file on symptom/wish alone. Read actual source (not docs, not guesses) at the responsible file:line. Quote it. State mechanism — what the code does, why it's wrong (or insufficient) for this env/input, what the divergent value actually is.

**Body files, never heredoc**: write issue/PR bodies to a file first; heredoc-inline mangles on Windows shell. Never `gh pr create --fill` — the reference-bar template is mandatory.

**Fork remote**: `<fork-remote>` = local git remote name added after `gh repo fork <owner>/<repo> --clone=false`, pointing at your fork (SSH or HTTPS clone URL, either works) — `git remote add <fork-remote> <your-fork-clone-url>`. `<fork-user>` = your GitHub user. Define both before any push; never push directly to the upstream base/origin.

**Indexed checkout for mechanism claims**: clone to a temp dir and `codegraph init` it; quote `file:line` from that index, never from memory.
```bash
TMP=$(mktemp -d)
git clone [--depth 1] https://github.com/<owner>/<repo>.git "$TMP/<repo>"
codegraph init "$TMP/<repo>"
```
Use `--depth 1` when the clone is read-only proof (issue, PR mechanism check — local working tree stays for diff/push only). Omit it when the clone itself becomes the working tree you'll branch/build/push from (feature PR half). Stale index (moved lines, missing symbols) → `codegraph init` again before quoting.

## Filing procedures

Each reference file below holds that shape's closure/triage table, step-by-step procedure, and counter-scenario controls — the shared mechanics above are assumed, not repeated.

- **Issue** → `references/issue.md`
- **PR** → `references/pr.md`
- **Feature** (issue + PR together) → `references/feature.md`

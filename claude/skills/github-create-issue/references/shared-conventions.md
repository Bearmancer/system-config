# Shared Conventions: github-create-issue, github-create-pr, github-create-feature

These four sections are shared verbatim across the three github-create-* skills.

## Which skill fires

A request names a symptom with no fix in hand → `github-create-issue`.
A request carries a fix for an existing bug, fork/base/head already resolvable → `github-create-pr`.
A request asks for a capability that doesn't exist yet → `github-create-feature` (files the feature-request issue, then attaches an implementing PR in the same pass).
A request could read as more than one of the above → `github-create-issue`: cheapest, most reversible, and every fix or feature still starts from a filed issue.

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
- Never post "correction" comment that supersede earlier wrong one — delete earlier one instead.
- Environment mistake be most common correction: verify before post; if one slip through, edit or delete — never append.

## Independent re-audit

After file, hand full list of post (issue number + PR number + comment IDs + pushed SHAs as applicable) to fresh agent with instruct to **independently** re-read each post from GitHub, check every claim against machine and source, flag anything unverified, mis-stated, or contradict. Fix or delete flagged item. Never self-certify.

## gh CLI only — no GitHub plugin/MCP needed

Use `gh` via Bash for all this. No reach for GitHub plugin/MCP server unless user have one enable and ask specific.

**Why plain `gh` enough here:** issue search, issue create, issue comment, PR create, PR edit, fork — all single `gh` subcommand, plain-text or `--json` output. No multi-step orchestrate, no auth flow beyond `gh auth status`, wrapper add nothing on top. A GitHub plugin/MCP server adds dependency and permission surface for zero behavior gain on this task shape.

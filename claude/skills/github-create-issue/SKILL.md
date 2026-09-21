---
name: github-create-issue
description: This skill should be used when opening or filing a GitHub issue — "file an issue", "open a GitHub issue", "report this bug upstream", "create a repo issue" — or after root-causing a bug in a third-party dependency/plugin/CLI that needs tracking upstream on GitHub. Enforces closure triage first (open → comment; stale-bot / regression closure → new issue), then a duplicate search, then a fixed diagnostic-depth bar (exact file:line, quoted source, reproduction, environment, counter-scenarios tried, error text) before filing via `gh` CLI alone.
version: 0.1.0
---

Bug report get ignore or bounce back when claim symptom, no proof show. Skill lock depth at: reviewer must check claim self, run nothing else. Skill refuse file below this bar.

## Reference bar

Calibrate issue: https://github.com/code-yeongyu/oh-my-openagent/issues/6167

That issue show target depth. Have, in order:

1. Prereq checklist (search duplicate, check latest version, check docs)
2. One sentence bug describe, name exact mechanism (not just symptom)
3. Numbered repro step, concrete enough replay word-for-word
4. Expect vs actual behavior, state separate
5. Tool/doctor output paste verbatim
6. Error log / probe output show actual divergent value side by side
   (e.g. `file:///c:/...` vs `file:///C:/...`), not paraphrase

## Closure triage — do first, always

Fetch closure state AND closing actor before pick comment vs new issue:

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

## Procedure

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

4. **File with `gh` CLI alone** — see "gh CLI only" below for why.
   ```bash
   gh issue create --repo <owner>/<repo> --title "<short, names the mechanism>" --body-file <path-to-body.md>
   ```
   Write body to file first. Never heredoc-inline body — heredoc mangle on Windows shell.

5. **Confirm authorize before file.** File public issue = visible, hard-reverse action (can no unpublish community discuss). State draft title + one-line summary, get explicit go-ahead before run `gh issue create` — unless user already give blanket authorize for this specific repo/session.

## Counter-scenarios — try them, then say so

Presume you tried them — then actually try them. Before filing, attempt at least one control that could disprove own mechanism, report outcome either way:

- A/B suspected variable (set config value to distinguishable one, restart, re-read log — e.g. `agents.explore.model = <unique-id>`, then check created session's `model.id`).
- Warm vs cold start (server's first request often return nothing).
- Marker-present vs marker-free directory (root-gated servers).
- Identical bytes under different extension/format (isolate routing from parsing).
- Same file through second, independent tool path (isolate core from plugin).

Write outcome under **Counter-scenarios tried**, include any that fail to reproduce or favour other explain. Claim carry own falsify attempt trust far more.

## Environment block — software-maximalist, no hardware

Software fact only. Never CPU/GPU/RAM/model, never hostname/username/tokens.

- OS: caption, version, build, architecture — **verify, never guess** (Win10 and Win11 both report `Windows 10.0.x`; build `19045` = Win10 22H2, `22000+` = Win11)
- App: opencode version; plugin names + versions
- Runtime/deps: node, npm/pnpm/bun, python, dotnet — whatever repro touch
- Every binary repro name, with its version
- Config excerpt (relevant keys, verbatim)
- **Logs — always.** At least one verbatim log line show divergent value, plus log file path

Collect on Windows with CIM one-liner (faster than built-in `systeminfo`):

```powershell
Get-CimInstance Win32_OperatingSystem | Select-Object Caption,Version,BuildNumber,OSArchitecture
node --version; npm --version; bun --version
<tool> --version
```

## Corrections: edit, don't stack

- Own issue body wrong → `gh issue edit <n> --repo <owner>/<repo> --body-file <file>`
- Bad comment → `gh api -X DELETE repos/<owner>/<repo>/issues/comments/<comment_id>`
- Never post "correction" comment that supersede earlier wrong one — delete earlier one instead.
- Environment mistake be most common correction: verify before post; if one slip through, edit or delete — never append.

## Independent re-audit

After file, hand full list of post (issue numbers + comment IDs) to fresh agent with instruct to **independently** re-read each post from GitHub, check every claim against machine and source, flag anything unverified, mis-stated, or contradict. Fix or delete flagged item. Never self-certify.

## Orchestration

Drafting session orchestrate: closure triage, duplicate search, and body draft belong to one worker that can run `gh`; **independent re-audit** go to separate subagent handed only post list (issue numbers + comment ids) and instruct to re-check every claim from GitHub — never back to session that write posts. One context must not both author and certify same issue.

## gh CLI only — no GitHub plugin/MCP needed

Use `gh` via Bash for all this. No reach for GitHub plugin/MCP server unless user have one enable and ask specific.

**Why plain `gh` enough here:** issue search, issue create, issue comment, PR/issue read — all single `gh` subcommand, plain-text or `--json` output. No multi-step orchestrate, no auth flow beyond `gh auth status`, wrapper add nothing on top.

**When GitHub plugin/MCP actually help instead:**

- Structured JSON schema validate at tool layer (fewer malformed
  `--json`/`--jq` mistake) when chain many GitHub call in one task
- Cross-cut workflow touch GitHub _and_ other system in one
  tool-call graph (e.g., agent framework wire issue create into a
  bigger pipeline)
- Sandbox/restrict env where shell out to `gh` block
  by policy but MCP tool call allowlist

None apply here for file one well-evidence issue — that a `gh` one-liner, plugin add dependency and permission surface for zero behavior gain here.

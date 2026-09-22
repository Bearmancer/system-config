---
name: github-create-issue
description: This skill should be used when opening or filing a GitHub issue — "file an issue", "open a GitHub issue", "report this bug upstream", "create a repo issue" — or after root-causing a bug in a third-party dependency/plugin/CLI that needs tracking upstream on GitHub. Enforces closure triage first (open → comment; stale-bot / regression closure → new issue), then a duplicate search, then a fixed diagnostic-depth bar (exact file:line, quoted source, reproduction, environment, counter-scenarios tried, error text) before filing via `gh` CLI alone.
version: 0.1.0
---

Bug report get ignore or bounce back when claim symptom, no proof show. Skill lock depth at: reviewer must check claim self, run nothing else. Skill refuse file below this bar.

## Reference bar

Calibrate issue: https://github.com/code-yeongyu/oh-my-openagent/issues/6167 — match its depth. Structure to match: Procedure step 3 below.

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

See `references/shared-conventions.md` for which of the three skills fires on an ambiguous request, plus the Environment block, Corrections, Independent re-audit, and gh-CLI-only sections — identical across all three github-create-* skills.

# Filing an issue

Shared mechanics (triage timeline command, triage principle, search-first, root-cause-first, body-to-file, fork-remote, indexed checkout) are in `SKILL.md` — this file has only the issue-specific triage table, procedure deltas, and counter-scenarios.

## Closure triage — do first, always

```bash
gh issue view <n> --repo <owner>/<repo> --json state,stateReason,closedAt,labels
gh api repos/<owner>/<repo>/issues/<n>/timeline --jq '.[] | select(.event=="closed" or .event=="cross-referenced") | {event:.event, actor:(.actor.login // null), at:.created_at}'
```

| state  | reason      | closing actor         | action                                                                                                     |
| ------ | ----------- | ---------------------- | ------------------------------------------------------------------------------------------------------------ |
| open   | —           | —                      | comment with new evidence; never refile                                                                     |
| closed | not_planned | `github-actions[bot]`  | stale-bot close, not a rejection → file a NEW issue citing the old number                                    |
| closed | completed   | human/bot              | fix was claimed; if it still reproduces → regression → file a NEW issue citing the old number                |
| closed | not_planned | human                  | truly declined; refile only with a materially stronger case (new impact, new mechanism, or one-line-fix argument) |

## Procedure

1. Closure triage first (table above), then search by mechanism:
   ```bash
   gh issue list --repo <owner>/<repo> --search "<mechanism words>" --state all --limit 15
   ```
2. Root-cause per shared mechanics — no filing on symptom alone.
3. Draft body matching the reference bar:
   - Bug describe: mechanism, not just symptom
   - Repro step: numbered, concrete, replayable
   - Expect vs actual: separate line
   - Env/doctor output: verbatim, fence block
   - Evidence: exact quote source (`file:line`), exact command output, side-by-side divergent values — never a summary of logs
   - Mechanism understood → name the responsible function/file and what the correct fix needs
4. File:
   ```bash
   gh issue create --repo <owner>/<repo> --title "<short, names the mechanism>" --body-file <path-to-body.md>
   ```
5. Confirm before filing (see `SKILL.md`), then run the command.

## Counter-scenarios for an issue

- A/B suspected variable (set config value to distinguishable one, restart, re-read log — e.g. `agents.explore.model = <unique-id>`, then check created session's `model.id`).
- Warm vs cold start (server's first request often return nothing).
- Marker-present vs marker-free directory (root-gated servers).
- Identical bytes under different extension/format (isolate routing from parsing).
- Same file through second, independent tool path (isolate core from plugin).

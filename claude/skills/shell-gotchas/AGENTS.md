# shell-gotchas — agent notes

Single-file skill. `SKILL.md` is the source of truth; no build, tests, or manifests here.

- Do not rename the skill or its trigger description. Invocation depends on it.
- Keep bullets repo-agnostic: name the shell behavior, not one repo's paths. Put repo-specific proof in the bullet, not the rule.
- Verify by running the real command (`sd`, `jaq`, `pwsh`), never by simulating it. Quoting bugs only show live.
- Quoting layers (PowerShell single-quoted = literal; harness JSON-decodes once): write patterns with single `\s` plus plain `"`. If a pattern keeps missing, stop re-escaping and move logic to a `.ps1` in temp, invoked as `pwsh -NoProfile -File "path/to/s.ps1"`.
- `jaq` parses strict JSON only; this box has no `jq`. JSONC trailing commas kill it — strip or skip.
- Stay in-process for file writes (`Get-Content -LiteralPath -Raw`, dotnet `WriteAllText` or `Set-Content -NoNewline`). Bash `>` redirect risks line-ending damage.
- Do not add docs, examples dirs, or tests here unless asked.

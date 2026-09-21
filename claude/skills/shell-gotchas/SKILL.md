---
name: shell-gotchas
description: This skill should be used when writing or debugging shell commands in either PowerShell (.ps1, profile functions, pwsh one-liners) or the Bash tool (git-bash on Windows), especially on a parsing error, silent-empty variable, unexpected read-only-variable error, a zip/archive command producing wrong internal structure, a `cd` that seems to not persist, cloning a repo for research/verification, a missing JSON tool, or hand-building a JSON payload with Windows paths. Also applies whenever authoring new PowerShell or Bash-tool code.
version: 0.3.0
---

Known shell foot-guns, verified in this environment. Check this list
before debugging a shell error from scratch.

## PowerShell

- `$Host` is a read-only built-in automatic variable — never use as a
  param/var name (`Cannot overwrite variable Host`). Rename, e.g.
  `$ApiHost`.
- `"$var?query=..."` in a double-quoted string fails interpolation — `?`
  breaks variable-name parsing, resolves silently empty. Use
  `"${var}?query=..."` (braces) or `"$($var)?query=..."` (subexpression;
  also covers member access like `"$($r.Status)?x=1"`) whenever a variable
  is immediately followed by `?`.
- `Compress-Archive -Path $files.FullName` where `$files` is a flat
  array of individual file paths (e.g. from `Get-ChildItem -Recurse
  -File`) flattens directory structure — all files land at zip root.
  Pass top-level `Get-ChildItem $dir` items instead (not recursively
  flattened) to preserve subtree structure.
- `Get-Volume -FileSystemLabel "X"` can return nothing despite the
  volume being mounted (WMI cache staleness). Use `Get-CimInstance
  Win32_LogicalDisk | Where-Object VolumeName -eq "X"` instead.
- NTFS case-only rename (`tv` → `TV`) can no-op on a single
  `Rename-Item` call. Force via two-step rename through a temp name:
  ```powershell
  Rename-Item -Path $path -NewName "$leaf.__tmp__"
  Rename-Item -Path "$path.__tmp__" -NewName $newCasedName
  ```
- `"#${n}: $_"` — colon immediately after a variable in a double-quoted
  string is parsed as a PS scope/drive separator (`$n:_` → read-only
  drive variable, silently empty). Always brace the var:
  `"#${n}: $r"` or `"#$($n): $r"`. Same trap hits any char that is a
  legal scope/drive prefix (letters, underscore).
- `jq`/`jaq` cannot sit in the middle of a PowerShell pipeline:
  `... | jq .id` throws `InvalidOperation: Cannot run a document in the
  middle of a pipeline`. Native executables that read stdin only work at
  the end of a pipeline or as a standalone command. Use
  `ConvertFrom-Json` for in-pipeline JSON extraction:
  `(gh issue view N --json id | ConvertFrom-Json).id`.
- Building a string that must contain literal double quotes (e.g. a
  `-File "path with spaces"` arg passed as one flag value) —
  double-quoted PowerShell strings interpret `` ` ``/`$`/nested quotes,
  forcing escapes like `` `"..`" `` or doubled `""..""`. Wrap the outer
  string in single quotes instead — single-quoted strings are literal,
  so inner `"..."` needs no escaping at all: `'--params=-NoProfile -File
  "C:\path with spaces\script.ps1"'`. Only use
  double-quoted-with-escapes when the value itself needs variable
  interpolation.

## Bash tool (git-bash on Windows)

- Bash tool cwd does not persist a `cd` across calls the way a real
  terminal does — each call can reset to the tool's default dir. Do not
  rely on a prior `cd`; use `git -C <dir> <cmd>` (or an absolute path
  per-command) instead of `cd dir && cmd`.
- Clone-to-temp for research/verification: see CLAUDE.md's "Research
  clones stay in temp" rule.
- Use `jaq` for JSON on this box — same CLI/filter syntax as `jq`,
  stricter parsing that catches bad escapes. Both `jaq` and `jq` reject
  trailing commas; see JSON parsers below for comma-tolerant paths.
- When building a JSON string payload by hand inside a single-quoted
  bash `echo`, backslashes pass through literally, so a Windows path
  (`C:\Users\...`) lands as invalid JSON escapes (`\U`, `\L`, ...).
  Either double every backslash (`C:\\\\Users...`) or use forward
  slashes in the test payload — JSON parsers accept both.
- **This also bites heredocs, and the doubling math is worse than plain
  bash.** The Bash tool's `command` parameter is itself JSON-decoded by
  the harness before bash ever sees it — one layer of backslash-halving
  happens before your string reaches the shell at all. A quoted heredoc
  (`<<'EOF'`) then passes bytes through literally with no further
  processing, so what looks like `C:\\Users` (2 backslashes) in the
  command you write can arrive in the file as `C:\Users` (1) once the
  harness layer has already eaten one level. Cheapest fix: forward
  slashes in the test JSON, always — sidesteps the whole
  stacked-escaping problem instead of counting backslash layers.
- Prefer extracting one JSON field with `sed -n 's/.*"key" *:
  *"\([^"]*\)".*/\1/p'` over pulling in a JSON-parser dependency
  (`jaq`/`jq`) for a single-field grab.
- Piping a real command's stdout through bash's `>` file redirect
  (git-bash on Windows) can introduce line-ending artifacts a downstream
  tool doesn't see when the same data stays in-process —
  `Invoke-Formatter` threw `Cannot determine line endings as the text
  probably contain mixed line endings` only on bash-redirected
  round-trips, never when chained entirely inside one `pwsh` session
  (`$text | Invoke-Formatter | Invoke-Formatter`, byte-identical).
  Reproduce line-ending bugs in-process first before blaming the
  formatter/tool.

## Third-party process spawners with their own JSON "command" field (dprint exec, etc.)

- A tool that reads a shell command out of a JSON config value (dprint's
  `exec` plugin, similar patterns elsewhere) does its own tokenizing of
  that string into argv — it is NOT bash, NOT cmd.exe, and its
  quote/backslash handling is an unknown third dialect. Don't assume it
  follows POSIX shell rules, PowerShell rules, or the Windows
  `CommandLineToArgvW`/MSVC-runtime backslash-quote rule (`2n`
  backslashes+quote = `n` backslashes, toggle quote mode; `2n+1` =
  literal quote). Confirmed here: embedding `\"..name -join \"..\"..\"`
  (meant as an escaped inner double-quote) inside dprint's `"command"`
  string split on the _wrong_ quote and got silently re-joined wrong
  when `pwsh -Command` re-concatenated the fragments — no error until
  PowerShell tried to parse the mangled result.
- **Fix, not workaround: eliminate the nested quoting entirely.** Put
  the real logic in its own script file and give the JSON `"command"`
  field a trivial invocation with no embedded quotes of its own: `pwsh
  -NoProfile -File "C:\path\to\script.ps1" "{{file_path}}"` — the only
  quoting left is around plain paths, which every dialect handles the
  same way.
- If a stdin-based formatter script instead needs the _file path_, check
  the plugin's templating (dprint: `{{file_path}}`) and actually use it
  as an argument — forgetting to pass it produces a script that silently
  runs against no/empty input, which for dprint surfaces as `"the
  formatted text was empty. Perhaps dprint-plugin-exec has been
  misconfigured?"`, not an obvious "missing argument" error.
- Read from the real file (`Get-Content -LiteralPath $Path -Raw`)
  instead of stdin (`[Console]::In.ReadToEnd()`) when both are available
  — the file read handles line-ending detection correctly, the stdin
  read is what hit the mixed-line-endings bug above.
- Verify the _actual_ invocation, not a manual re-simulation of it.
  Testing a hand-built shell command that mimics what you think the tool
  does can pass while the tool's real invocation still fails (or the
  reverse) — the dprint fix above only got proven correct by running
  real `dprint fmt`, twice, after every escaping theory checked out in
  isolated bash tests but still broke live.

## Quoting layers, strict parsers, in-process writes

- Single-quoted PS is literal: single `\s` + plain `"`, never `\\s` / `\"`.
- Repeated escaping misses → script file: `Write` .ps1 with literal pattern, invoke `pwsh -NoProfile -File "C:/path/s.ps1"`.
- Strict JSON parsers reject trailing commas: `jaq`, `jq`, `ConvertFrom-Json`. Tolerant path is pwsh plus dotnet: `[System.Text.Json]` with `AllowTrailingCommas` and `JsonCommentHandling.Skip`, mutate via `JsonNode` — no regex surgery.
- No `json5`/`commentjson` Python libs, no `gojq`/`yq`/`dasel` on box. Fallback stays `sd`-strip of `,\s*}` / `,\s*]` → `jaq`.
- Bash `>` redirect risks line endings. Stay in-process: `Get-Content -LiteralPath $P -Raw` → `[System.IO.File]::WriteAllText` (or `Set-Content -NoNewline`).
- `rg -c` on zero matches prints nothing, exit 1. Reads as crash, means success. Confirm via `Read`/`grep` tool.
- Read `$LASTEXITCODE` after native CLIs: parse/count failures surface there, not stdout.
- `gh api` sub-issue endpoint (`/issues/{n}/sub_issues`) requires the
  integer database ID, not the GraphQL node ID. `gh issue view N --json
  id` returns the base64 node ID (`I_kwDO...`), which the REST endpoint
  rejects with HTTP 422 "not of type integer". Get the integer via:
  `gh api repos/{owner}/{repo}/issues/{n} --jq .id`. Use `-F
  "sub_issue_id=$id"` (not `-f`) so `gh` sends it as a number, not a
  quoted string.
- Never `-replace` with a bool pattern (`$T.Contains(x)` coerces to `"True"`, deletes every `true` in memory).
- Python `re` replacement: raw-string `\"` writes literal backslashes. Use plain `"` in replacement.
- Check indent via `repr()` before whitespace-sensitive edits.

## Orchestration

This skill is knowledge, not a workflow: it loads into whatever session or subagent needs it. When a host session orchestrates, the real reproduction and the fix verification belong to the worker actually running the commands — never re-simulate a command by hand in the orchestrator; quoting bugs only show live. Long or repetitive verification loops (a repro matrix across shells, repeated round-trips) go to a spawned subagent with the exact commands and expected outputs.

## Reference

- Quoting matrix (`ref/quoting-matrix.md`): measured arg-transmission results for tricky payloads across pwsh7/pwsh5/cmd/python/bash/dotnet. Reach for it when passing quotes, backslashes, or shell metachars across a runtime boundary.

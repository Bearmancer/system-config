---
name: shell-gotchas
description: This skill should be used when writing or debugging shell commands in either PowerShell (.ps1, profile functions, pwsh one-liners) or the Bash tool (git-bash on Windows), especially on a parsing error, silent-empty variable, unexpected read-only-variable error, a zip/archive command producing wrong internal structure, a `cd` that seems to not persist, cloning a repo for research/verification, a missing JSON tool, or hand-building a JSON payload with Windows paths. Also applies whenever authoring new PowerShell or Bash-tool code.
version: 0.3.0
---

Known shell foot-guns, verified in this environment. Check this list before debugging a shell error from scratch.

## PowerShell

- `$Host` = read-only auto var. Never use as param/var name (`Cannot overwrite variable Host`). Rename: `$ApiHost`.
- Double-quoted string: var followed by `?` or a scope-prefix char (letter/`_`, e.g. `:`) breaks interpolation, resolves silently empty. `"$var?query=..."` → empty; `"#$n: $_"` → `$n:_` parsed as drive var, empty. Fix: brace `${var}` or subexpression `$($var)` — `"${var}?query=..."`, `"$($r.Status)?x=1"`, `"#${n}: $r"`, `"#$($n): $r"`.
- `Compress-Archive -Path $files.FullName` with `$files` a flat array from `Get-ChildItem -Recurse -File` flattens dirs — all files land at zip root. Pass top-level `Get-ChildItem $dir` items instead to preserve subtree.
- `Get-Volume -FileSystemLabel "X"` can return nothing on a mounted volume (WMI cache stale). Use `Get-CimInstance Win32_LogicalDisk | Where-Object VolumeName -eq "X"`.
- NTFS case-only rename (`tv`→`TV`) can no-op in one `Rename-Item` call. Two-step via temp name:
  ```powershell
  Rename-Item -Path $path -NewName "$leaf.__tmp__"
  Rename-Item -Path "$path.__tmp__" -NewName $newCasedName
  ```
- Mutating fields piped through `Where-Object` doesn't persist — pipeline output is a copy. `($items | Where-Object {...}).value = "x"` hits the copy, fails silent. Use `foreach ($i in $items) { if (<cond>) { $i.value = "x" } }`.
- Building a string with literal double quotes (e.g. `-File "path with spaces"` as one flag value): double-quoted PS strings need escapes (`` `" `` or `""`). Wrap the outer string single-quoted instead — literal, no escaping needed: `'--params=-NoProfile -File "C:\path with spaces\script.ps1"'`. Use double-quote+escape only when the value needs interpolation.
- Never `-replace` with a bool pattern (`$T.Contains(x)` coerces to `"True"`, deletes every `true` in memory).
- Read `$LASTEXITCODE` after native CLIs — parse/count failures surface there, not stdout.

## Bash tool (git-bash on Windows)

- Bash tool cwd doesn't persist a `cd` across calls — each call may reset to the tool's default dir. Use `git -C <dir> <cmd>` or an absolute path per-command, not `cd dir && cmd`.
- Cloning a repo for research/verification: temp files, incl. clone repos, go through `mktemp` — see CLAUDE.md `<ai_artifacts>`.
- Bash `>` redirect of a command's stdout (git-bash) can add line-ending artifacts: `Invoke-Formatter` threw `Cannot determine line endings as the text probably contain mixed line endings` only on bash-redirected round-trips, never chained inside one `pwsh` session (`$text | Invoke-Formatter`). Reproduce in-process before blaming the tool.
- `rg -c` on zero matches prints nothing, exit 1 — reads as crash, means success. Confirm via `Read`/`grep` tool.
- Double-quoted Windows path ending `\` (`ls "C:\dir\"`): trailing `\"` escapes the quote → `unexpected EOF while looking for matching '"'`. Drop trailing slash or use forward slashes.
- Foreground `sleep N && cat <task output>` blocked by harness. Background task notifies on exit; waiting on a condition → Monitor.

## JSON tools

- Use `jaq` for JSON here — same CLI/filter syntax as `jq`, stricter parsing catches bad escapes.
- `jaq`/`jq`/`ConvertFrom-Json` all reject trailing commas. Tolerant path: pwsh + dotnet `[System.Text.Json]` with `AllowTrailingCommas`+`JsonCommentHandling.Skip`, mutate via `JsonNode` — no regex surgery. No `json5`/`commentjson` Python libs on box, no `gojq`/`yq`/`dasel` either. Fallback: `sd`-strip `,\s*}` / `,\s*]` → `jaq`.
- `jq`/`jaq` can't sit mid-PowerShell-pipeline: `... | jq .id` throws `InvalidOperation: Cannot run a document in the middle of a pipeline` — native stdin executables only work at pipeline end or standalone. Use `ConvertFrom-Json` for in-pipeline JSON extraction: `(gh issue view N --json id | ConvertFrom-Json).id`.
- Hand-building JSON in a single-quoted bash `echo` with a Windows path (`C:\Users\...`): backslashes pass through literally → invalid escapes (`\U`, `\L`, ...). Fix: forward slashes, or double every backslash (`C:\\Users...`) — JSON parsers accept both.
- Same bug hits heredocs, doubling math worse: the Bash tool's `command` param is JSON-decoded by the harness before bash sees it (one backslash-halving layer already spent), then a quoted heredoc (`<<'EOF'`) passes bytes through literally. What you write as `C:\\Users` (2 backslashes) can land as `C:\Users` (1) in the file. Fix: forward slashes always — sidesteps counting escaping layers.

## gh CLI

- `gh api` sub-issue endpoint (`/issues/{n}/sub_issues`) needs the integer database ID, not the GraphQL node ID. `gh issue view N --json id` returns the node ID (`I_kwDO...`) → REST rejects with HTTP 422 "not of type integer". Get the int: `gh api repos/{owner}/{repo}/issues/{n} --jq .id`. Use `-F "sub_issue_id=$id"` (not `-f`) so it's sent as a number.

## Python

- `re` replacement with a raw-string `\"` writes literal backslashes — use plain `"` in the replacement string.
- Check indent via `repr()` before whitespace-sensitive edits.

## Third-party process spawners with own JSON "command" field (dprint exec, etc.)

- A tool reading a shell command out of a JSON config value (dprint's `exec` plugin, similar elsewhere) does its own argv tokenizing: not bash, not cmd.exe, an unknown third dialect. An escaped inner double-quote (`\"..name -join \"..\"..\"`) inside dprint's `"command"` string splits on the wrong quote; `pwsh -Command` re-concatenates the fragments wrong, no error until PowerShell parses the mangled result.
- Fix, not workaround: eliminate nested quoting entirely. Put the real logic in its own script file, give the JSON `"command"` field a trivial invocation with no embedded quotes: `pwsh -NoProfile -File "C:\path\to\script.ps1" "{{file_path}}"` — the only quoting left is around plain paths.
- Forgetting to pass the templated file path (dprint: `{{file_path}}`) runs the script against empty input, which dprint surfaces as `"the formatted text was empty. Perhaps dprint-plugin-exec has been misconfigured?"`, not an obvious missing-argument error.
- Read from the real file (`Get-Content -LiteralPath $Path -Raw`) instead of stdin (`[Console]::In.ReadToEnd()`) when both are available — the file read handles line-ending detection correctly; the stdin read is what hit the mixed-line-endings bug above.
- Verify the actual invocation, not a manual re-simulation of it — a hand-built command mimicking what the tool does can pass while the real invocation still fails (or the reverse). Confirm by running the real command (e.g. `dprint fmt`, twice).

## Reference

- Quoting matrix (`ref/quoting-matrix.md`): measured arg-transmission results for tricky payloads across pwsh7/pwsh5/cmd/python/bash/dotnet. Reach for it when passing quotes, backslashes, or shell metachars across a runtime boundary.
- URL audit: any URL emitted passes `deep-research` SKILL.md "URL audit" before it reaches the user.

# `{file:}` MCP key hot-reload on OpenCode v2.0.18

Ticket: Bearmancer/system-config #3 (R1). Tested 2026-09-29 on the installed binary `opencode v2.0.18` (Windows).

## Question

When an MCP server's key is injected with `{file:path}` inside `mcp.servers.<name>.environment` in `opencode.json`, and only the key file changes (`opencode.json` itself is untouched):

1. Does the MCP server reconnect with the new key automatically, and does that depend on whether the file sits in a watched path?
2. Does `opencode reload` make it reconnect?
3. How are a trailing newline and a missing file handled?

## Answer (short)

- A key file inside a config-watched path (project `.opencode/**`, or the global config dir) reconnects only the affected server within about 1 s, with no reload command.
- A key file outside those paths (for example `./secrets/key`) is not picked up automatically. It is picked up by `opencode reload`, or by any other reload that happens for another reason.
- `opencode reload` restarts every MCP server in that location, including unchanged ones, with freshly read `{file:}` values.
- Trailing newlines, CRLF and surrounding whitespace are trimmed.
- A missing file makes config loading fail. At startup the location returns HTTP 500 and no MCP server starts. `opencode reload` with the file missing kills the running MCP servers and does not restart them.

## Test setup

- Isolated server: `opencode serve --hostname 127.0.0.1 --port 47811` started from `tmp/r1/proj`, with `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME`, `XDG_STATE_HOME` and `OPENCODE_TEST_HOME` all pointing under `tmp/r1`. The real service and the real `~/.config/opencode` were not used.
- A second isolated server on port 47812 (`proj2`) was used for the missing-file-at-startup case.
- `tmp/r1/proj/opencode.json` defines three local stdio MCP servers. Each runs `tmp/r1/mcp-server.js`, a small Node JSON-RPC stdio server with one tool `getkey`. On every spawn it appends `spawn pid=... TESTKEY=<value>` to `tmp/r1/mcp.log`, and it logs `exit` on shutdown.
  - `kf_unwatched`: `TESTKEY = {file:./secrets/key}`. The file is `proj/secrets/key`, not in a watch target.
  - `kf_projdir`: `TESTKEY = {file:./.opencode/key}`. The file is in the project `.opencode` directory.
  - `kf_global`: `TESTKEY = {file:<abs>/xdg/config/opencode/key}`. The file is in the global config dir.
- Evidence is the timestamped `mcp.log` (spawn and exit lines carrying the env value seen by the child process) and `serve.log` (server debug log). `opencode api --server ... mcp.list` was used to read server status.
- The tool call itself was not driven through a model. No API exists to call an MCP tool without a session (see Unverified). The value the tool would return is the `TESTKEY` value the child received at spawn, which is what `mcp.log` records.

## Evidence

Times below are UTC from `mcp.log`. Log lines are in `C:\Users\Lance\.claude\jobs\da241933\tmp\r1\mcp.log`.

### 1. Watched vs unwatched, no reload

| Test | Action (only this file changed) | Result within about 10 s |
|---|---|---|
| A2, unwatched | write `proj/secrets/key` at 03:51:08 | No spawn or exit. `pre-reload new lines: 0` |
| A3, unwatched | write `proj/secrets/key` at 03:52:03 | No spawn or exit. `pre-reload new lines: 0` |
| B, project dir | write `proj/.opencode/key` at 03:51:32 | 03:51:32.947 `kf_projdir exit`, 03:51:33.150 `kf_projdir spawn TESTKEY="v4-projdir"`. Only that server restarted |
| C, global dir | write `xdg/config/opencode/key` at 03:51:44 | 03:51:44.942 `kf_global exit`, 03:51:45.160 `kf_global spawn TESTKEY="v5-global"`. Only that server restarted |

- The first run (all three files written together, 03:50:34) restarted all three servers, including `kf_unwatched`. That is the piggyback effect described in claim 3 below. Only the isolated single-file runs above show the true per-path behavior.
- Source explanation. The config watcher subscribes to: the global config directory, project `.opencode` directories that exist, the direct config files, the claude/agents sources and any explicit file (`packages/core/src/config/watch.ts:8-38`). A key file elsewhere is not a watch target.
- On a watch event the reload is debounced 100 ms and re-runs `load()` (`packages/core/src/config.ts:284-289`). `load()` re-reads every `{file:}` through `ConfigVariable.substitute` (`packages/core/src/config.ts:136-139`, `packages/core/src/config/variable.ts:36-84`).
- `reload()` compares the substituted result with the previous one (`isDeepStrictEqual`, `config.ts:273`). If it differs, it publishes `Event.Updated`. The MCP service then compares each server's resolved config and replaces only servers whose config changed (`packages/core/src/mcp/index.ts:524-560`). That is why B and C restarted a single server.

### 2. `opencode reload`

- A2 continued: at 03:51:18 `opencode reload --server http://127.0.0.1:47811` printed `Configuration reloaded`.
  - 03:51:18.844 `kf_global exit`, 03:51:18.988 `kf_projdir exit`, 03:51:19.135 `kf_unwatched exit`.
  - 03:51:19.917 `kf_unwatched spawn TESTKEY="v3-unwatched"` (the new value), 03:51:19.932 `kf_projdir spawn`, 03:51:19.946 `kf_global spawn`.
- So `reload` picks up the unwatched change, and it also restarts the two servers whose config did not change.
- Source: `opencode reload` calls `client.location.reload` (`packages/cli/src/commands/handlers/reload.ts:17-21`), which reaches `LocationServiceMap.reload` (`packages/server/src/handlers/location.ts:22`, `packages/core/src/location-service-map.ts:20-35`). That function invalidates and rebuilds all location services.
- G (03:55:09 to 03:55:10) shows the same full restart of all three servers, with values `v6-unwatched`, `v8-projdir`, `v5-global`.

### 3. Piggyback: an unwatched change is applied by any later reload

- A3 wrote `proj/secrets/key` at 03:52:03 and nothing restarted by 03:52:13.
- At about 03:52:14 the watched file `proj/.opencode/key` was deleted. `serve.log` shows a `config.updated` event at 03:52:14.151, and `mcp.log` shows `kf_unwatched exit` at 03:52:14.214 and `kf_unwatched spawn TESTKEY="v6-unwatched"` at 03:52:14.498. The unwatched server picked up its own new value because a reload for another reason re-read every `{file:}`.
- Consequence: an unwatched key file is not reliably stale forever, but the refresh time is not deterministic.

### 4. Trailing newline and whitespace

- Files were written as `v1-unwatched\n`, `v1-projdir\n`, `v1-global` (no newline). Values seen by the servers: `"v1-unwatched"`, `"v1-projdir"`, `"v1-global"`, all without newlines (03:49:08 spawn lines).
- A3 wrote `v6-unwatched\r\n  \n` (CRLF plus trailing spaces and a blank line). The server received `"v6-unwatched"` (03:52:14.498 spawn line).
- Source: `fileContent.trim()` then `JSON.stringify(...).slice(1, -1)` (`packages/core/src/config/variable.ts:79`).

### 5. Missing file

- Startup, missing file (port 47812, `proj2` references `./secrets/nokey`): `opencode api mcp.list` returned `HTTP 500 Internal Server Error`. The server log shows `ConfigInvalidError` from `Config.load`. No `kf_missing` spawn line exists in `mcp.log`.
- Runtime, file deleted while the server is running (03:52:14): the watcher triggers a reload that fails. `serve.log` lines 713 and 714 (03:52:14.988 and 03:52:15.091): `failed to reload config ... ConfigInvalidError ... NotFound ... proj\.opencode\key`. Running MCP servers were not stopped by the watcher-triggered failure.
- Restoring the file (D, 03:52:49) recovered: 03:52:49.445 `kf_projdir exit`, 03:52:49.658 `kf_projdir spawn TESTKEY="v7-projdir"`.
- `opencode reload` while the file is missing (E, 03:54:12): the CLI printed a stack trace ending in `cli.reload`. `mcp.log`: 03:54:12.309 `kf_projdir exit`, 03:54:12.625 `kf_unwatched exit`, 03:54:12.857 `kf_global exit`, and no spawns follow. `mcp.list` returned `HTTP 500`.
- Recovery after that failed reload: restoring the file at 03:54:41 did not restart anything. The next request (`mcp.list`) rebuilt the location and spawned all three servers at 03:54:54 (`v6-unwatched`, `v8-projdir`, `v5-global`). A further `opencode reload` (G) restarted them again.
- Source: a missing file raises `InvalidError` (`variable.ts:59-77`). Direct files load with `Effect.orDie` (`config.ts:194-198`), so the whole config load dies rather than only that one MCP server.

### 6. Other properties of the substitution (from source)

- `{env:}` and `{file:}` are substituted textually on the whole file before JSON parsing, so they work in `url`, `headers` and `environment` alike (`variable.ts:27-34`).
- A `{file:` on a line whose trimmed prefix starts with `//` is skipped (`variable.ts:48-54`).
- `~/` is expanded to the home directory. A relative path resolves against the config file's directory (`variable.ts:56-58`).
- `{env:X}` with X unset becomes an empty string with no error (`variable.ts:28-31`).

## Practical guidance

- To get automatic key rotation, put the key file under the global config dir (`~/.config/opencode/`) or a project `.opencode/` directory. Do not commit real keys there.
- For a key file elsewhere (for example `~/.secrets/x`), run `opencode reload` after changing it. Expect every MCP server in that location to restart.
- Never delete or rename a referenced key file while OpenCode is running or before `opencode reload`. A missing file takes down all MCP servers for that location until the next request after the file is restored.

## Unverified

- No model-driven tool call was made. The tool value is inferred from the `TESTKEY` env recorded at each spawn. There is no API in `packages/server/src/handlers/mcp.ts` to call an MCP tool without a session.
- Source line numbers come from the OpenCode `v2` branch head (commit `ca084b2`, 2026-09-28). The empirical runs used the installed `opencode v2.0.18`. The two agreed on every observed behavior. Whether the tag `v2.0.18` differs in the cited files was not checked.
- The exact trigger of the 03:52:14 reload (item 3 above) is inferred from timestamps. The `config.updated` event at 14.151 precedes the failed-reload errors at 14.988 by about 0.8 s, which was not explained.
- The file-deletion case for a watched file was tested once. It was not tested for an unwatched file.
- Only the Windows watcher backend was exercised (`backend=windows` and `backend=node` in `serve.log`). Behavior on other platforms is untested.
- Whether the real running service (`opencode serve --service`) behaves identically was not tested by design.
- The tests used relative paths from a project config and one absolute path in the global config. A `{file:~/...}` path outside any watched root was not run separately, though it is covered by the same code path as `./secrets/key`.

## Safety and cleanup notes

- No file under `~/.config/opencode` or `~/.secrets` was edited. The real `opencode service` was not stopped or restarted.
- One command, `opencode debug config`, was run once without `--server` while the isolated environment variables were set. It hung, and its two processes (PIDs 1836 and 5808) were terminated. It may have contacted or started a background service. Only PIDs recorded above were killed.
- Both isolated servers (ports 47811 and 47812), their tee process, their launcher shells and the MCP child processes were stopped at the end. `tmp/r1` still holds the test files and logs (job tmp, deleted with the job). Nothing was committed.

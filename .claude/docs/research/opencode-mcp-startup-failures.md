# OpenCode MCP startup failures and OmO auth after senpi#2346 (#67)

Date: 2026-09-30. Read-only investigation of the local machine, the installed OpenCode 2.0.20 source at tag `v2.0.20`, the OpenCode v2 docs and senpi tag `v2026.9.29-5`. Times are UTC (`Z`); the machine's local time is UTC+5:30. Refs #67.

## Question restated

Issue #67 asks why OpenCode's remote MCP servers fail when it starts, and what the native fix is. The captain reported 9 failures on the 2026-09-30 start; the log run `0bd085ad` lists 7 (`getaddrinfo ENOTFOUND`). The earlier run `563b5459` (2026-09-29) had stdio servers fail with "Request timed out" and `aws-mcp` fail with "Invalid request parameters". The debug log flag did not reach the log. The ticket asks for the root cause, the two failures beyond the seven, whether OpenCode has a native retry, reconnect or timeout setting, and the correct way to enable debug logging.

A second, separate question in the ticket comment is whether OmO (senpi) still fails to authenticate after senpi#2346: is the installed runtime at or after merge commit 3b7f871, do any deep-research remote servers reach OmO through a skill-carried declaration, and does every keyed stdio server in `~/.omo/agent/mcp.json` carry an explicit `env` block.

The two causes are reported separately below. They share no code path: OpenCode's failures are DNS errors in the OpenCode server process; OmO's failures were dropped Authorization headers.

## Short answers

- Part A cause: the operating system's DNS resolver intermittently stops answering for about 12 seconds. It hit OpenCode during two MCP start bursts and also hit unrelated programs on this machine at other times. The evidence does not point to a service-start-at-logon race or a proxy, and the probes I ran show no resolver difference between Node and standalone Bun (the Bun embedded in `opencode.exe` was not tested). OpenCode 2.0.20 has no retry or reconnect setting for a failed MCP server; it tries once per location.
- The two extra failures: the OpenCode log holds exactly seven MCP failures in run `0bd085ad` (six in the second incident, run `d4ebd344`), and all 16 servers in the first run have one recorded outcome, so no OpenCode MCP failure is missing. The OmO logs do hold more failures on the same date (section A5): three auth failures at 23:35Z on 2026-09-29, then four connect timeouts and one catalog-refresh failure at the 00:05Z OmO start on 2026-09-30. Those are the best candidates for the captain's extra count, but the mapping to "9" is unproven.
- Part B: OmO is on a build that contains the fix, the deep-research skill's remote declaration was live and broke auth on 2026-09-29, and every keyed stdio server has an `env` block. The skill sidecar no longer exists. No OmO run since the fix has been observed connecting to the remote servers, so the fix is supported by config, docs and source, not by a fresh run.

## Part A: OpenCode startup failures

### A1. What the log shows

Run `0bd085ad` is `opencode serve --service` (OpenCode 2.0.19), started 07:29:51Z:

```
opencode.log:69216  07:29:51.605Z run=0bd085ad message="cli starting" version=2.0.19 args="[\"serve\",\"--service\"]"
```

Sixteen MCP servers exist in this run: the 14 in `opencode.jsonc` lines 109 to 287 plus `context7` and `gh_grep`, which the `oh-my-opencode-slim` plugin registers (its log says `mcps":2` and `[v2] mcp servers registered {"count":2}`). No server has `disabled` set, so all 16 are attempted. Nine connected first, at 07:31:46 to 07:32:19, and seven failed together:

```
opencode.log:69355  07:31:54.052Z WARN run=0bd085ad message="mcp http request failed" errors="[{\"type\":\"TypeError\",\"message\":\"getaddrinfo ENOTFOUND learn.microsoft.com\",\"code\":\"ENOTFOUND\",\"errno\":4}]" durationMs=11270 ... server=microsoft-learn
opencode.log:69356  07:31:54.060Z WARN run=0bd085ad message="mcp connect failed" server=microsoft-learn status.status=failed status.error="getaddrinfo ENOTFOUND learn.microsoft.com"
```

The other six (`context7`, `tavily`, `browserbase`, `firecrawl`, `gh_grep`, `apify`) fail in the same 40 milliseconds (lines 69357 to 69368). Their `durationMs` values are 11285 to 11310. Sixteen servers equal nine connected plus seven failed, with none unaccounted for.

The second incident is run `d4ebd344`, started 07:37:08Z after an upgrade to 2.0.20. It failed again, with six servers this time (`tavily` connected):

```
07:38:03.398Z WARN run=d4ebd344 message="mcp http request failed" ... "getaddrinfo ENOTFOUND mcp.apify.com" ... durationMs=11711 ... server=apify
```

The six failures are `apify`, `microsoft-learn`, `browserbase`, `gh_grep`, `firecrawl` and `context7`, with `durationMs` 11711 to 11961. At 07:38:03 four servers had connected (`exa`, `tavily`, `playwright`, `github`), six had failed and six were still starting.

### A2. Cause: the OS resolver timed out; the launch order did not matter

An error `ENOTFOUND` that takes 11 to 12 seconds is a resolver timeout, not an instant "no such name". A fast miss looks different: in my probe, forcing IPv6 lookups (`family: 6`) returned `ENOTFOUND` in 3 to 50 ms because this machine has no IPv6 default route.

The Windows DNS client logged the matching event during the first burst, in the System log:

```
30-09-2026 13:01:53  Microsoft-Windows-DNS-Client 1014  Name resolution for the name learn.microsoft.com timed out after none of the configured DNS servers responded.
```

13:01:53 local is 07:31:53Z, one second before the seven `ENOTFOUND` lines. The same event id 1014 recurs for unrelated names and programs (`api.anthropic.com`, `claude.ai`, `rs-ny.rustdesk.com`, `api.github.com`, `mcp.brightdata.com` on 2026-09-20, and others), so the outages are machine-wide and not specific to OpenCode. No event 1014 was logged for the second burst at 13:08:03 local (see Unverified).

The mid-session failures point the same way. Run `563b5459` logged `ENOTFOUND` and `models.dev` timeouts hours after it started, when no client had just attached. I converted each System-log event 1014 from local time (UTC+5:30) and matched it to the nearest OpenCode network error (`Failed to fetch models.dev` with `TimeoutError`, or `mcp http request failed` with `ENOTFOUND`). This is same-minute correlation, not proof of one cause:

| Event 1014 (UTC) | Name that timed out | Nearest OpenCode network error |
|---|---|---|
| 2026-09-29 17:05:07 | `api.github.com` | none within 2 minutes |
| 2026-09-29 18:01:26 | `claude.ai` | 22 s later `models.dev` TimeoutError (18:01:47); 52 s and 66 s later `ENOTFOUND mcp.apify.com` |
| 2026-09-29 18:11:58 and 18:12:05 | `rs-ny.rustdesk.com`, `claude.ai` | none within 2 minutes |
| 2026-09-29 23:26:36 | `api.anthropic.com` | none within 2 minutes |
| 2026-09-29 23:39:46 | `claude.ai` | 38 s later `ENOTFOUND mcp.browserbase.com` (23:40:24), then `mcp.apify.com` at 23:40:38 |
| 2026-09-29 23:50:14 and 23:50:18 | `rs-ny.rustdesk.com`, `api.anthropic.com` | 51 to 55 s earlier `models.dev` TimeoutError (23:49:23) |
| 2026-09-30 07:31:53 | `learn.microsoft.com` | 1 s later the seven `ENOTFOUND` lines |

Five of the nine event-1014 timestamps have an OpenCode network error within about a minute; four have none. The `models.dev` fetch is a plain HTTPS request from the same server process and fails with a timeout, not a DNS-specific error, so it may reflect general connectivity loss and not DNS alone.

Things I tested and ruled out, each read-only:

- Logon race. The scheduled task `OpenCode service` runs `pwsh -NoProfile -Command "opencode service start"` at logon (`SystemConfig.psm1:194-196`; registered state: trigger `MSFT_TaskLogonTrigger`, no delay, `RunOnlyIfNetworkAvailable: False`, `LastRunTime 30-09-2026 12:27:57`, result 0). The service that task started (run `5d1d3f4b`, 06:57:47Z) logged no MCP connect or failure at all; OpenCode connects MCP servers lazily when a client opens a location. The failing service `0bd085ad` was spawned at 07:29:51Z by a terminal client (`run=a220a0aa`, args `[]`, 07:29:37Z) and the DNS failure came at 07:31:42 to 07:31:54Z, over an hour after logon. Run `d4ebd344` was likewise spawned by a client after the version upgrade. So the scheduled task's start order is not the trigger, and adding a task delay would not have prevented either incident.
- Per-process resolver. From this machine, Node v24.19.0 and Bun 1.4.2 `dns.lookup` resolved all eight remote hosts (`mcp.tavily.com`, `mcp.exa.ai`, `learn.microsoft.com`, `mcp.apify.com`, `mcp.browserbase.com`, `mcp.context7.com`, `mcp.firecrawl.dev`, `mcp.grep.app`) in 25 to 139 ms, and the OS resolver via `Resolve-DnsName` did the same in 6 to 389 ms. Two cold bursts of eight unrelated hostnames, one per runtime, also resolved (one name returned a fast `ENOTFOUND` in 60 ms, a genuine miss). So eight-way concurrency alone did not trigger the failure in these probes, and Node and Bun behaved the same. These probes ran after both incidents, so they show the fault is intermittent, not permanent, and they cannot show what the resolver did during the incidents. The Bun tested is the standalone `~/.bun/bin/bun`, not necessarily the runtime embedded in `opencode.exe`, and I could not read the service process's own environment.
- Proxy, hosts file, VPN client settings. There are no proxy variables at process, user or machine scope (`NODE_USE_SYSTEM_CA` and three `OPENCODE_*` variables are the only relevant names); WinHTTP reports "Direct access"; the IE proxy is off; the hosts file has no active lines.
- IPv6. `tailscale netcheck` reports "IPv6: no, but OS has support", and there is no `::/0` route. The only non-link-local IPv6 address is on the Tailscale interface. AAAA answers therefore cannot be used, but IPv4 answers resolve, so IPv6 is not the failure.

The DNS layer on this machine has one notable feature. Tailscale's "Use Tailscale DNS" is on, and the Windows name-resolution policy table has a catch-all rule for the whole namespace:

```
Namespace   : .
NameServers : {100.100.100.100, fd7a:115c:a1e0::53}
```

The adapters list `100.100.100.100` (Tailscale) and `192.168.0.1` (Wi-Fi router). `tailscale dns status` shows MagicDNS forwarding to `8.8.8.8`, `8.8.4.4`, `1.1.1.1` and IPv6 resolvers, and says: "Run 'tailscale set --accept-dns=false' to revert to your system default DNS resolver." Queries sent directly to `100.100.100.100`, `192.168.0.1` and `8.8.8.8` each answered in 6 to 21 ms at probe time. Which hop went silent during the two incidents cannot be told from local evidence.

### A3. OpenCode has no native retry or reconnect setting

The v2 docs page for MCP servers (https://opencode.ai/v2/docs/mcp-servers) documents only three timeouts, set under `mcp.timeout` or per server: `startup` 30 seconds ("Transport connection and server initialization"), `catalog` 30 seconds and `execution` 12 hours. It documents no retry, backoff or reconnect key. The source agrees (tag `v2.0.20`):

- `packages/core/src/mcp/index.ts:537-546`: "Initial connections stay asynchronous", one `startServer` per server, forked once when a location is created.
- `index.ts:459-463`: a failed attempt sets `status: "failed"` and logs `mcp connect failed`; nothing schedules another attempt.
- The only reconnect paths are an expired MCP session (`index.ts:330`, "mcp session expired, reconnecting") and an OAuth credential switch (`index.ts:566-585`). Neither applies to a DNS error.
- `index.ts:83` and `:440` serialize remote loads per URL, so different hosts connect in parallel.
- `packages/core/src/mcp/client.ts:32-34` sets the defaults and `:167` applies `startup` to `client.connect`.

A DNS error is returned by the request in about 11 seconds, well under the 30 second `startup` timeout, so raising `startup` does not help the seven `ENOTFOUND` failures. There is no native setting that retries them. What did recover them in both incidents was creating a fresh connection set: in run `0bd085ad` all seven servers connected with new connection ids at 07:32:23 to 07:32:30Z, and in run `d4ebd344` the six failed ones plus a second `exa` connected at 07:43:39 to 07:43:43Z. Each recovery followed a burst of `configuration normalization diagnostic` lines, which is the config-reload signature. The captain's earlier belief that "no reconnect afterwards" happens is therefore only true within one location; a reload reconnects. The CLI has an `opencode reload` subcommand ("Reload configuration") and the v2 docs say `/mcps` in the TUI can "view, connect, disconnect, or authenticate servers".

### A4. The stdio "Request timed out" failures (run 563b5459)

At 23:24:42 to 23:24:43Z (directory `system-config`) and 23:25:02Z (directory `C:\Users\Lance`) `aws-mcp`, `sequential-thinking`, `codegraph` and `playwright` failed with `status.error="Request timed out"`, for example:

```
opencode.log:64443  23:24:42.760Z WARN run=563b5459 message="mcp connect failed" server=sequential-thinking status.status=failed status.error="Request timed out"
```

`opencode.jsonc` gives those three servers only `catalog` and `execution` timeouts (lines 215-218, 270-273, 281-284); `startup` is unset, so the 30 second default applies (`client.ts:32`). The servers that set `"startup": 120000` (`agentql`, `scrapegraph`, `firefox-devtools`, `brightdata`) did not time out. The failures appeared about 37 seconds after sibling servers connected in the same location, which matches a 30 second startup limit (an inference; see Unverified). In run `0bd085ad` the same three connected 4 to 7 seconds after their location started, and in run `563b5459`'s first start at 17:26 within 14 seconds, so they are slow only under load. `aws-mcp`'s later `Invalid request parameters` (23:59:23Z) is the removed server from PR #51 and is moot.

### A5. The two failures beyond seven, and the counts

The OpenCode log has no MCP failure beyond the seven, so the two extra failures are not OpenCode MCP connections from that start. The ticket says the count might sit in the OmO logs, and it does: the OmO logs hold further failures on 2026-09-30. I aggregated every warning and error in `~/.omo/agent/logs/mcp/*.log` from 2026-09-29T17:00Z to the end of 2026-09-30 and dropped the repeated `MCP server <unknown> has 0 exposed tools` warnings (see Unverified). What remains, in UTC:

| Time | Server | Entry |
|---|---|---|
| 09-29 23:35:01 | `apify`, `exa`, `tavily` | `failed during connect ... Streamable HTTP error: Error POSTing to endpoint`; apify's body is `invalid_token` (3 failures, the skill-declared remote servers with no Authorization header, section B2) |
| 09-30 00:05:05 | `codegraph` | `Failed to refresh MCP catalog cache` (1) |
| 09-30 00:05:19 to 00:05:22 | `agentql`, `sequential-thinking`, `playwright`, `brightdata` | `failed during connect: ... timed out during connect after 15000ms diagnostic rerun timed out after 5000ms` (4) |
| 09-30 03:06:56 | `firefox-devtools` | `Failed to refresh MCP catalog cache` (1) |

The single OmO start at 00:05Z (05:35 local) has five failures, not nine or seven plus two. The three evening failures plus the five plus the 03:06Z catalog failure add up to nine, and that sum is the only way I found to reach nine from failure lines. Whether it is the captain's number is unproven. The OmO start at 00:05Z is 05:35 local on 2026-09-30, so it also fits "the 2026-09-30 start" by local date. The four 15 second timeouts are consistent with the same slow-stdio-start pattern as A4: `~/.omo/agent/mcp.json` now sets `connectTimeoutMs: 120000` on six stdio servers, but that key was added in repo commit `4faf316` (2026-09-30 08:48 +0530, PR #51, which is 03:18Z); the live file was last modified at 03:06Z. Both are after the 00:05Z timeouts, and no OmO connect timeout is logged after that.

The counts in OpenCode itself:

- Nine servers had connected when the first wave ended (`brightdata`, the ninth, at 07:32:19.882Z). Nine is a count of successes, and it is the only nine in `opencode.log`.
- Six servers were connected at 07:31:55.197Z (`agentql`, `sequential-thinking`, `github`, `playwright`, `codegraph`, `exa`), and the second burst has six failures. Either could be the captain's "6"; which one the UI displays is not knowable here.
- "Enabled": none of the 14 configured servers sets `disabled` (v2 uses `disabled`, not `enabled`; the docs say "Use `disabled`, not an `enabled` field"), so 14 configured plus 2 from the plugin equals 16 enabled. `opencode mcp list` run from `C:\Users\Lance` after both incidents prints 16 lines, all `✓ ... connected`: `agentql`, `apify`, `brightdata`, `browserbase`, `codegraph`, `context7`, `exa`, `firecrawl`, `firefox-devtools`, `gh_grep`, `github`, `microsoft-learn`, `playwright`, `scrapegraph`, `sequential-thinking`, `tavily`. So the current service does not reproduce a count of 6, and no source I have gives 6 enabled.
- Other error-level lines in the OpenCode window: `run=bc06b7cb` at 07:31:34.751Z, `cli process failed ... Invalid value for flag --log-level: "DEBUG"` (the debug attempt); and `run=fadb205f` at 07:32:09 to 07:32:16Z, five `unhandled rejection ... EPERM: operation not permitted, rename '...session.json.<pid>.<uuid>.tmp' -> '...\.local\state\opencode\session.json'`. These are not MCP failures, but they are the only other errors near the burst. Two `InterruptError` lines at 07:30:19Z (`/api/event` 200 and `/api/integration` 499) are a client disconnect, not failures.

### A6. Debug logging

The flag is `--log-level` with lowercase values. The log shows the captain's two attempts:

```
07:31:34.719Z run=bc06b7cb args="[\"--log-level=DEBUG\"]"
07:31:34.751Z ERROR run=bc06b7cb ... Invalid value for flag --log-level: "DEBUG". Expected: "all" | "trace" | "debug" | "info" | "warn" | "warning" | "error" | "fatal" | "none"
07:31:39.507Z run=fadb205f args="[\"--log-level=debug\"]"
```

The lowercase form worked, but only for the terminal client: run `fadb205f` has 174 `level=DEBUG` lines and `b0336b3d` has 76, all `role=cli` (none is `role=server`), and the server run `0bd085ad` has none. The background service is always spawned as the fixed command `opencode serve --service` (`packages/client/src/effect/service.ts:67-73`), so a flag given to the client does not reach it. `opencode --help` states "--print-logs Print logs to stderr (server logs require --standalone)". The v2 troubleshooting page (https://opencode.ai/v2/docs/troubleshooting) documents only reading `opencode.log`, not a level setting. Separately, the source, and only the source, reads an environment variable: `packages/util/src/observability/logging.ts:164-172` maps `OPENCODE_LOG_LEVEL` (any case, `DEBUG|INFO|WARN|ERROR`) and `:160` prints to stderr when `OPENCODE_PRINT_LOGS=1`. Neither variable appears in the v2 docs I read, so they are undocumented behavior.

### A7. Recommended native fixes

1. Debug logs for the server: run a foreground server with `opencode --standalone --log-level debug --print-logs`, the only route the CLI help documents. For the always-on background service there is no documented level setting. The undocumented option is `opencode service set env OPENCODE_LOG_LEVEL debug`: the `service set` help names an `env` key and `service-config.ts:14-24` lists `env` as a persisted service key, but the variable itself is source-only. I did not run it because `service set` stops the service, and I did not verify that the daemon inherits the value (see Unverified). If that route is not acceptable, there is no native route for service-level debug logging.
2. Stdio timeouts: set `startup` once instead of per server. The v2 docs example is `"mcp": { "timeout": { "startup": 120000 }, "servers": { ... } }`; a per-server `timeout` object overrides matching defaults. This targets `codegraph`, `playwright`, `sequential-thinking` and `github`, which have no `startup`.
3. DNS: there is no OpenCode setting. The cause is in the OS and Tailscale layer. The native diagnostic is Tailscale's own setting `tailscale set --accept-dns=false`, which removes the catch-all resolver rule and uses the router; the cost is that MagicDNS names stop working, and this was not tested. Capturing the DNS Client event log during a burst would show which server stops answering.
4. Recovery after a failed start: `/mcps` (connect) or `opencode reload`; there is no native automatic retry, so none can be configured.
5. The scheduled task needs no change for this issue, because neither incident came from its logon start.

## Part B: OmO auth after senpi#2346

Upstream: https://github.com/code-yeongyu/senpi/issues/2345, fixed by https://github.com/code-yeongyu/senpi/pull/2346.

### B1. Is the installed runtime at or after merge commit 3b7f871? Yes.

`omo --version` prints `omo 5.1.4 (engine: senpi 2026.9.29-5)`. PR #2346 merged on 2026-09-29T06:13:44Z as `3b7f8710ec5b2c1700205c9af87109b776ebbcf6`. The GitHub compare of that commit against tag `v2026.9.29-5` (`a893419c201f4e19676309704ffc0ff7fb282599`, published 2026-09-29T20:04:11Z) reports `ahead_by 212, behind_by 0`, so the tag contains the merge. Independent evidence that the runtime already ran the fix at 23:35Z: OmO's own log line for the skill matches the message at `packages/coding-agent/src/core/extensions/builtin/mcp/skill-server.ts:101` word for word.

### B2. Does a deep-research remote server reach OmO through a skill-carried declaration? It did on 2026-09-29; it does not today.

`~/.omo/agent/logs/mcp/skills.log` records the sidecar path and the dropped auth:

```
23:35:00.821Z warning  Skill 'deep-research' MCP server 'tavily': bearerTokenEnv 'TAVILY_API_KEY' is ignored and no Authorization header is sent, because a skill-declared remote server must not send a parent environment variable to a server the skill chose; declare the server in your own mcp.json instead, where bearerTokenEnv keeps working.
```

The same warning appears for `firecrawl`, `exa`, `apify` and `browserbase` (23:35:00.822 to .826Z). One second later `apify.log` shows the consequence: `23:35:01.909Z ... Error POSTing to endpoint: {"error":"invalid_token","error_description":"Missing or invalid access token. Pass an Apify API token in the Authorization: Bearer ..."}`. The code is `skill-server.ts:98-104`: for a remote server with `bearerTokenEnv`, the field is dropped and `auth: false` is set. At 00:03:39Z on 2026-09-30 the same sidecar, `C:\Users\Lance\.claude\skills\deep-research\mcp.json`, was reported for six servers with "collides with the global config; system config wins", so from then the global file was used.

Today no sidecar exists: the deep-research skill directory has no `mcp.json`; `fd` finds only `~/.omo/agent/mcp.json` across `~/.claude/skills`, `~/.agents`, `~/.omo/agent` and `~/.config/opencode/skills`; none of the 624 plugin `SKILL.md` files has an `mcp.json` beside it or an `mcp:` front matter block; and `references/fleet.md:3` says "No skill sidecar `mcp.json`". The remote servers now come from `~/.omo/agent/mcp.json` lines 3 to 22 with `bearerTokenEnv`, which the senpi docs say keeps working when declared there (`docs/mcp.md:259-263`, https://github.com/code-yeongyu/senpi/blob/v2026.9.29-5/packages/coding-agent/docs/mcp.md).

### B3. Does every keyed stdio server carry an explicit env block? Yes.

In `~/.omo/agent/mcp.json`: `agentql` (line 27, `AGENTQL_API_KEY`), `scrapegraph` (line 35, `SGAI_API_KEY` from `${SCRAPEGRAPH_API_KEY}`), `brightdata` (line 55, `API_TOKEN` from `${BRIGHTDATA_API_KEY}`) and `github` (line 60, `GITHUB_PERSONAL_ACCESS_TOKEN`) each have an `env` block. `codegraph`, `firefox-devtools`, `playwright` and `sequential-thinking` have none and use no key. The docs say a stdio child sees only `HOME`, `LOGNAME`, `PATH`, `SHELL`, `TERM`, `USER` (on Windows the system path and profile variables) plus `env` (`docs/mcp.md:49-54`), so a keyed server without `env` would have no key. The `${VAR}` values expand from OmO's parent environment; the variable names `AGENTQL_API_KEY`, `SCRAPEGRAPH_API_KEY`, `BRIGHTDATA_API_KEY` and `GITHUB_PERSONAL_ACCESS_TOKEN`, and the five remote key names (`EXA_API_KEY`, `TAVILY_API_KEY`, `FIRECRAWL_API_KEY`, `APIFY_TOKEN`, `BROWSERBASE_API_KEY`), exist at user scope. Only names were checked, never values, and `~/.secrets/.env` was not read.

Verdict: config, docs and source support the fix, but no OmO run since it has been observed authenticating to the remote servers. The remote-server OmO logs have no line later than 00:05Z on 2026-09-30, and `~/.omo/agent/mcp.json` was last edited at 03:06Z, so the current file has never been exercised in a logged OmO start. The only OmO auth failures on record (23:35:01Z) predate the collision report at 00:03:39Z that put the global file in charge; no later auth failure is logged, but OmO logs warnings and errors only, so that absence is weak evidence. A fresh OmO start followed by one call to each remote server would settle it.

The change to make, if any, is only to keep the remote servers in `~/.omo/agent/mcp.json`. There is no native way to make a skill-declared remote server send an env-derived token; the docs state it is refused by design.

## Sources

- OpenCode v2 MCP docs: https://opencode.ai/v2/docs/mcp-servers
- OpenCode v2 troubleshooting: https://opencode.ai/v2/docs/troubleshooting
- OpenCode v1 MCP docs (numeric `timeout`, contrast only): https://opencode.ai/docs/mcp-servers/
- OpenCode source at `v2.0.20`: https://github.com/anomalyco/opencode/blob/v2.0.20/packages/core/src/mcp/index.ts, https://github.com/anomalyco/opencode/blob/v2.0.20/packages/core/src/mcp/client.ts, https://github.com/anomalyco/opencode/blob/v2.0.20/packages/schema/src/mcp.ts, https://github.com/anomalyco/opencode/blob/v2.0.20/packages/cli/src/services/service-config.ts, https://github.com/anomalyco/opencode/blob/v2.0.20/packages/client/src/effect/service.ts, https://github.com/anomalyco/opencode/blob/v2.0.20/packages/client/src/pty-handoff.ts, https://github.com/anomalyco/opencode/blob/v2.0.20/packages/util/src/observability/logging.ts
- senpi: https://github.com/code-yeongyu/senpi/issues/2345, https://github.com/code-yeongyu/senpi/pull/2346, https://github.com/code-yeongyu/senpi/releases/tag/v2026.9.29-5, https://github.com/code-yeongyu/senpi/blob/v2026.9.29-5/packages/coding-agent/src/core/extensions/builtin/mcp/skill-server.ts

All fifteen URLs returned HTTP 200 from `check_urls.py` on 2026-09-30. Local evidence: `~/.local/share/opencode/log/opencode.log`, `~/.config/opencode/opencode.jsonc` (the file is `.jsonc`; no `opencode.json` exists), `SystemConfig.psm1`, `~/.omo/agent/mcp.json`, `~/.omo/agent/logs/mcp/*.log`, the Windows System event log and the read-only PowerShell and CLI probes described above.

## Unverified

- What the OpenCode UI counts as "9 failures" and "6 enabled". The log arithmetic gives 9 connected and 7 failed in run `0bd085ad`, and 6 failed in run `d4ebd344`; the mapping to the UI is a guess.
- Which DNS hop stopped answering (Tailscale `100.100.100.100`, the router `192.168.0.1`, or an upstream resolver). Only one event 1014 exists for the first burst and none for the second, so the second burst's cause is inferred from the same 11 to 12 second signature.
- Why `exa` (both bursts) and `tavily` (second burst) resolved while the others failed. A warm DNS cache from other programs is a plausible explanation and was not tested.
- That 11 to 12 seconds equals the Windows resolver's full timeout schedule. I did not source the schedule.
- What triggered the reconnect waves at 07:32:23Z and 07:43:39Z. The correlation is with config-reload log bursts; I did not identify the trigger, and I did not test whether `opencode reload` or `/mcps` connect recovers a failed server.
- Why the logon-started service `5d1d3f4b` was replaced by `0bd085ad` at 07:29:51Z. It shared the version 2.0.19, so a version mismatch is not the reason.
- That the roughly 37 second gap in run `563b5459` reflects the 30 second `startup` default. Startup begin times are not logged.
- That `opencode service set env OPENCODE_LOG_LEVEL debug` reaches the daemon. `pty-handoff.ts:78-87` merges the service `env`, but I did not read the spawn call that applies it, and `service set` stops the service, which I was told not to do. Whether `--log-level` on `opencode service start` propagates was not tested; the fixed spawn arguments at `service.ts:68` suggest it does not.
- That `tailscale set --accept-dns=false` stops the failures. Its output is quoted from `tailscale dns status`; the change was not applied.
- Whether antivirus, Windows Defender network inspection or the two client starts (one per incident) had any part in the resolver silence. Not examined.
- Whether the API keys behind the environment variables are valid. Only the names were checked.
- Whether `firefox-devtools` or `playwright` need environment variables beyond the MCP SDK allowlist. They have no `env` block and no failure was seen in the OmO logs.
- The remaining OmO logs were searched for auth-failure patterns only; the one `invalid_token` hit is the only one found.
- What the OmO warning `MCP server <unknown> has 0 exposed tools after includeTools/excludeTools filters` means. It repeats on every server, including ones that later connected (33 times for `brightdata`, 22 for `agentql`), and its last entry for each remote server is at 00:05Z. I did not find its source, and I did not test whether it hides a real problem.
- Whether the OmO "9 failures" is the sum I built (3 at 23:35Z, 1 at 00:05:05Z, 4 at 00:05:19 to :22Z, 1 at 03:06:56Z). It is the only path to nine from failure lines that I found, not a confirmed match.
- The 25 OmO `mcp.session_start` errors with "stale extension generation after reload" (00:06Z to 05:32Z in `service.log`) were not counted as MCP failures; if the captain's count includes them the total is higher.
- Whether the OmO remote servers work now. No OmO run after the last edit of `mcp.json` (03:06Z) was observed; the OmO verdict rests on config, docs and source.

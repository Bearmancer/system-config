# Topgrade failure and tailnet exposure of OpenCode

Date: 2026-09-29. Machine: Windows 10 Pro, topgrade 17.12.2, opencode v2.0.19, tailscale 1.102.4. Read-only research; no config, task or service changes were made.

## Questions

Q1. The Scheduled Task "Topgrade" (daily 10:00, `topgrade --yes --no-retry`, registered by `Install-TopgradeTask` in `SystemConfig.psm1`) last ran 2026-09-29 10:00:30 with LastTaskResult=1. Which step failed, what do topgrade's docs say about logs, summary and config, and what is the proper native fix?

Q2. The OpenCode service at 127.0.0.1:49374 is exposed by `tailscale serve --bg 49374` at https://lance.tail2e6179.ts.net (tailnet only). GET on the root returned 200 without credentials. (a) Does OpenCode server auth protect the API routes anyway? (b) Which native Tailscale mechanisms restrict Serve access? (c) Recommendation.

## Q1 findings

- Live task action: `pwsh.exe -NoProfile -Command "topgrade --yes --no-retry; if ($LASTEXITCODE) { Read-Host 'topgrade FAILED'; exit 1 }"` (source: `Export-ScheduledTask -TaskName Topgrade`; `SystemConfig.psm1` lines 175-181). It launches pwsh directly, not wt.exe. The 10:00 run used pwsh.exe (Task Scheduler event 129).
- Event 201 at 11:03:26 reported return code 2147942401 (0x80070001), which is exit 1, the task's own `exit 1` after `Read-Host`. So topgrade reported at least one failed step. Topgrade returns `StepFailed` when any summary step failed (https://github.com/topgrade-rs/topgrade/blob/main/src/main.rs). The 1h03m duration is the `Read-Host` wait, not topgrade's runtime.
- Topgrade has no log-file option; only `--log-filter` / `log_filters` for console tracing verbosity (https://github.com/topgrade-rs/topgrade/blob/main/src/config.rs). The step summary prints only to the console and was lost when the window closed.
- Config lives at `C:\Users\Lance\AppData\Roaming\topgrade.toml` (README "Configuration Path"). Active keys: `[misc] ignore_failures = ["dotnet"]`, `assume_yes = true`, `ask_retry = false`, `auto_retry = 1`.
- `--no-retry` is a hidden legacy alias of `--no-ask-retry`, redundant with `ask_retry = false`. `--yes` is redundant with `assume_yes = true`.
- A dry run (`--dry-run` spawns no processes, per `src/execution_context.rs`) listed the steps: winget, rustup, .NET, Cargo, VS Code Insiders extensions, pip3, TLDR, npm, gcloud, gh extensions, Claude Code, Claude Code Plugins, Skills, uv, Bun, Yazi. Windows update and Microsoft Store were skipped only because of the dry run's "dumb terminal".
- Tool-owned logs show winget (`DiagOutputDir\WinGet-2026-09-29-10-00-*.log`: "Leaf command succeeded") and gcloud (`%APPDATA%\gcloud\logs\2026.09.29\`) succeeded. None of the other steps leaves a per-run log.
- **The failed step cannot be named from the available evidence.**

### Proposed native fix

1. Capture the console with `Start-Transcript` (https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.host/start-transcript?view=powershell-7.5). Task argument sketch for `Install-TopgradeTask`: `-NoProfile -Command "Start-Transcript -Path $env:LOCALAPPDATA\topgrade-task.log -Append -UseMinimalHeader; topgrade --yes; $rc = $LASTEXITCODE; Stop-Transcript; if ($rc) { Read-Host 'topgrade FAILED'; exit 1 }"`.
2. Once the transcript names the step, handle it in `topgrade.toml`: add it to `[misc] ignore_failures`, add it to `[misc] disable`, or fix it with that step's own section key (source: `topgrade --config-reference`).
3. Drop the redundant `--no-retry`. Optionally set `notify_end = "on_failure"`.

## Q2 findings

### (a) The OpenCode API is protected

Probe results (status codes only, no bodies read):

| Route | Status | Content-Type | Bytes |
| --- | --- | --- | --- |
| `/`, any non-API path including a nonexistent one | 200 | text/html | 5986 |
| `/api/info`, `/api/session`, `/api/provider`, `/api/event`, `/openapi.json` | 401 | application/json | 64 |

- The same split holds via the tailnet: `/` returns 200 and `/api/session` returns 401. Every non-API path returns one identical HTML app shell, so the root 200 is not an API hole. The v2 `/api/*` routes are listed with `UnauthorizedError` 401 at https://opencode.ai/v2/docs/api.
- The documented mechanism is `OPENCODE_SERVER_PASSWORD` (HTTP basic auth; username `opencode` by default): https://opencode.ai/docs/server/. Third-party reports say v2 always enables auth and generates a random password when the variable is unset (https://github.com/joryirving/home-ops/pull/10468, https://github.com/openchamber/openchamber/issues/3984).
- `opencode service set env <NAME> <value>` passes environment variables to the service (https://opencode.ai/v2/docs/cli/commands/). `opencode service get hostname` returns `127.0.0.1`.

### (b) Tailscale mechanisms

- Serve is tailnet-only; `tailscale funnel status` shows no funnel.
- "Access control rules apply to Serve just like any other service" (https://tailscale.com/kb/1312/serve). Grants are deny-by-default with `ip` such as `tcp:443` (https://tailscale.com/kb/1324/grants). But the default tailnet policy allows all devices until it is edited (https://tailscale.com/kb/1018/acls).
- Identity headers and `--accept-app-caps` need a backend that consumes them. OpenCode doesn't, so they add no enforcement here.

### (c) Recommendation

1. Keep OpenCode's server auth. The API returns 401 without credentials both locally and via the tailnet.
2. Optionally pin a stable password with `opencode service set env OPENCODE_SERVER_PASSWORD <value>` (owner action; the value never goes in the repo or chat).
3. Add a tailnet grant limiting `tcp:443` on `lance` to the owner's own user or a tag, and confirm the policy is no longer the default allow-all (owner action, admin console).
4. Keep Funnel off and the service bound to 127.0.0.1 (both already true).

## Unverified

- Which topgrade step failed on 2026-09-29.
- Whether the Windows update and Microsoft Store steps run in the task's real console.
- Whether `Start-Transcript` captures topgrade's native output under Task Scheduler with `InteractiveToken`.
- Whether the service uses an env-pinned or a random per-start password. `service.json` and the state directory are off-limits and were not read.
- OpenCode v2 auth details rest on third-party issues; the official v2 server page returned 404.
- That a valid credential returns 200 on `/api/*` (no authentication was attempted).
- The current tailnet policy file content.

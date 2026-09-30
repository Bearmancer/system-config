# system-config

Runs this machine's daily jobs and backs up its AI agent config. One private repo, three Windows Scheduled Tasks.

## Repo boundaries

| Repo | Owns | Knows nothing about |
|---|---|---|
| `Toolbox` (`Dev\Toolbox`) | CLI commands; its `.env`, `state/toolbox.db`, `state/logs`; DB backup to Azure blob and dashboard redeploy inside `toolbox sync lastfm` / `toolbox sync youtube` | Scheduling, tasks, system-config |
| `system-config` (this repo, private) | The three scheduled tasks, `install.ps1`, `run-sync.ps1`, `backup-agents.ps1`, agent config backup, foobar2000 mirror | Toolbox internals. It only calls `toolbox sync lastfm` and `toolbox sync youtube` from PATH |
| `bearmancer.github.io` | Built HTML of learning courses, published by the `learning-course` skill | Course sources (transient, not backed up anywhere) |

`toolbox` on PATH resolves to `C:\Users\Lance\Dev\Toolbox\artifacts\publish\src\App\release\toolbox.exe`. This repo never builds or publishes Toolbox and never reads its `.env`.

## Scheduled tasks

- **Daily sync** (09:00): `run-sync.ps1` — lastfm sync, youtube sync, agent config backup, foobar2000 mirror, then checks the OpenCode service and starts it if it is down.
- **Topgrade** (10:00): `topgrade --yes --no-retry`.
- **OpenCode service** (at logon): `opencode service start`.

All three registered by `install.ps1` (run once, elevated, by hand — this repo's scripts never register scheduled tasks themselves).

## Agent config backup (`claude/`, `opencode/`, `omo/`, `agents/`)

`backup-agents.ps1` mirrors whitelisted local config into this repo via `robocopy`, then commits and pushes if anything changed.

| Repo folder | Local home | Mode |
|---|---|---|
| `claude/` (CLAUDE.md, keybindings.json, settings.json) | `~/.claude/` | files |
| `claude/skills/` | `~/.claude/skills/` | `/MIR /XJ /XD synced *-workspace __pycache__ .pytest_cache` |
| `claude/agents/`, `claude/commands/` | `~/.claude/agents`, `~/.claude/commands` | `/MIR` |
| `opencode/` (AGENTS.md, opencode.jsonc, oh-my-opencode-slim.jsonc, tui.json) | `~/.config/opencode/` | files |
| `opencode/agents/`, `opencode/commands/` | `~/.config/opencode/...` | `/MIR` |
| `omo/` (mcp.json, settings.json) | `~/.omo/agent/` | files (settings.json credential-guarded) |
| `agents/.skill-lock.json` | `~/.agents/.skill-lock.json` | files |
| `powershell/` | `$PROFILE` directory's profile file(s) + dot-sourced files | files |

Excluded on purpose: plugin caches, sessions, credentials, `secrets/`, `auth.json`, `service.json`, `~/.omo/teach`, `ulw-research`, `notepads`, `cache`, `codegraph`. `claude/settings.json` and `omo/settings.json` are dropped from a backup if it appears to hold a credential.

A whitelisted source that is absent is removed from its mirror path; nothing else in the repo is touched.

Sync direction is one-way: local machine → repo. Restore is a manual reverse copy — nothing here writes back to `~/.claude`, `~/.config/opencode`, or `~/.omo` automatically.

## Reinstall, not backup

Plugins, skills and secrets are not backed up as files. Each is restored by one step:

| Item | Restore step |
|---|---|
| Claude plugins | `claude plugin install <plugin>@<marketplace>` for each entry in `enabledPlugins` of the restored `claude/settings.json` |
| `.skill-lock.json` | Copy `agents/.skill-lock.json` back to `~/.agents/.skill-lock.json` |
| Slim skills (vendored oh-my-opencode-slim bundle) | OpenCode installs the `oh-my-opencode-slim` npm plugin listed (unpinned) in the restored `opencode.jsonc`; the researcher-subagent delegation was verified against `2.2.25` (`.claude/docs/research/researcher-subagent-mcp.md`) |
| OpenCode credentials (`auth.json`, `mcp-auth.json` in `~/.local/share/opencode`) | `opencode auth login` for providers, `opencode mcp auth` for OAuth MCP servers (both verified in `--help`) |
| OmO credentials (`~/.omo/agent/auth.json`) | Log in again in the app; `omo --help` lists no login command. Check afterwards with `omo auth check --provider <name>` |
| Secret pools (`~/.secrets/.env`) | Manual, from the password manager or an offline copy. Never backed up |
| Secrets | `uv run ~/.claude/skills/deep-research/scripts/switch_api_key.py --service all --materialize`, from the key pools in `~/.secrets/.env` |
| MCP key env vars (read by `omo/mcp.json`) | `switch_api_key.py --service <name> --set <ACCOUNT>` per service writes the secrets file and the user env var; set `GITHUB_PERSONAL_ACCESS_TOKEN` by hand. Restart OmO from a new terminal afterwards |
| Vendor CLIs (deep-research) | `uv tool install tavily-cli; npm install -g firecrawl-cli apify-cli @brightdata/cli just-scrape browse` (verified with each `--version`; sources in `.claude/docs/research/mcp-cli-post-matrix.md`) |
| Repos | `gh repo clone <owner>/<repo>`, e.g. `gh repo clone Bearmancer/deep-research ~/Dev/deep-research` |
| Scheduled Tasks | `install.ps1`, elevated |
| `service.json` | `opencode service set hostname 127.0.0.1` |
| Tailscale serve | `tailscale serve --bg 49374` |

## foobar2000 mirror

One-way `rclone sync` of `%APPDATA%\foobar2000-v2` to the `gdrive` remote's `foobar2000-v2` folder. rclone keeps no version history of its own on the remote side — Google Drive's own 30-day file versions are the only history.

## Setup

Run `install.ps1` elevated. It registers the three tasks and creates the `gdrive` rclone remote if missing (a browser opens once for Google sign-in).

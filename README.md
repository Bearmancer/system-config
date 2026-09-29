# system-config

Runs this machine's daily jobs and backs up its AI agent config. One private repo, two Windows Scheduled Tasks.

## Repo boundaries

| Repo | Owns | Knows nothing about |
|---|---|---|
| `Toolbox` (`Dev\Toolbox`) | CLI commands; its `.env`, `state/toolbox.db`, `state/logs`; DB backup to Azure blob and dashboard redeploy inside `toolbox sync lastfm` / `toolbox sync youtube` | Scheduling, tasks, system-config |
| `system-config` (this repo, private) | Both scheduled tasks, `install.ps1`, `run-sync.ps1`, `backup-agents.ps1`, agent config backup, foobar2000 mirror | Toolbox internals. It only calls `toolbox sync lastfm` and `toolbox sync youtube` from PATH |
| `bearmancer.github.io` | Built HTML of learning courses, published by the `learning-course` skill | Course sources (transient, not backed up anywhere) |

`toolbox` on PATH resolves to `C:\Users\Lance\Dev\Toolbox\artifacts\publish\src\App\release\toolbox.exe`. This repo never builds or publishes Toolbox and never reads its `.env`.

## Scheduled tasks

- **Daily sync** (09:00): `run-sync.ps1` — lastfm sync, youtube sync, agent config backup, foobar2000 mirror.
- **Topgrade** (10:00): `topgrade --yes --no-retry`.

Both registered by `install.ps1` (run once, elevated, by hand — this repo's scripts never register scheduled tasks themselves).

## Agent config backup (`claude/`, `opencode/`, `omo/`, `agents/`)

`backup-agents.ps1` mirrors whitelisted local config into this repo via `robocopy`, then commits and pushes if anything changed.

| Repo folder | Local home | Mode |
|---|---|---|
| `claude/` (CLAUDE.md, keybindings.json, settings.json) | `~/.claude/` | files |
| `claude/skills/` | `~/.claude/skills/` | `/MIR /XJ /XD synced *-workspace` |
| `claude/agents/`, `claude/commands/` | `~/.claude/agents`, `~/.claude/commands` | `/MIR` |
| `opencode/` (AGENTS.md, opencode.json, tui.json) | `~/.config/opencode/` | files |
| `opencode/agents/`, `opencode/commands/` | `~/.config/opencode/...` | `/MIR` |
| `omo/settings.json` | `~/.omo/agent/settings.json` | files (credential-guarded) |
| `agents/.skill-lock.json` | `~/.agents/.skill-lock.json` | files |
| `powershell/` | `$PROFILE` directory's profile file(s) + dot-sourced files | files |

Excluded on purpose: plugin caches, sessions, credentials, `secrets/`, `auth.json`, `service.json`, `~/.omo/teach`, `ulw-research`, `notepads`, `cache`, `codegraph`. `claude/settings.json` and `omo/settings.json` are dropped from a backup if it appears to hold a credential.

Sync direction is one-way: local machine → repo. Restore is a manual reverse copy — nothing here writes back to `~/.claude`, `~/.config/opencode`, or `~/.omo` automatically.

## foobar2000 mirror

One-way `rclone sync` of `%APPDATA%\foobar2000-v2` to the `gdrive` remote's `foobar2000-v2` folder. rclone keeps no version history of its own on the remote side — Google Drive's own 30-day file versions are the only history.

## Setup

Run `install.ps1` elevated. It registers the tasks and creates the `gdrive` rclone remote if missing (a browser opens once for Google sign-in).

# system-config

Runs this machine's daily jobs and backs up its AI agent config. One private repo, two Windows Scheduled Tasks.

## Repo boundaries

| Repo | Owns | Knows nothing about |
|---|---|---|
| `Toolbox` (`Dev\Toolbox`) | CLI commands; its `.env`, `state/toolbox.db`, `state/logs`; DB backup to Azure blob and dashboard redeploy inside `toolbox sync lastfm` / `toolbox sync youtube` | Scheduling, tasks, system-config |
| `system-config` (this repo, private) | Both scheduled tasks, `install.ps1`, `run-sync.ps1`, `backup-agents.ps1`, agent config backup, foobar2000 mirror, the Claude hook | Toolbox internals. It only calls `toolbox sync lastfm` and `toolbox sync youtube` from PATH |
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
| `opencode/` (AGENTS.md, opencode.jsonc, tui.json) | `~/.config/opencode/` | files |
| `opencode/agents/`, `opencode/commands/`, `opencode/skills/` | `~/.config/opencode/...` | `/MIR` |
| `omo/omo.jsonc` | `~/.omo/omo.jsonc` | files |
| `omo/scripts/`, `omo/plans/` | `~/.omo/scripts`, `~/.omo/plans` | `/MIR` |
| `agents/.skill-lock.json` | `~/.agents/.skill-lock.json` | files |
| `agents/skills/` | `~/.agents/skills/` | `/MIR /XJ` |
| `powershell/` | `$PROFILE` directory's profile file(s) + dot-sourced files | files |

Excluded on purpose: plugin caches, sessions, credentials, `~/.omo/teach`, `ulw-research`, `notepads`, `cache`, `codegraph`. `settings.json` is dropped from a backup if it appears to hold a credential.

Sync direction is one-way: local machine → repo. Restore is a manual reverse copy — nothing here writes back to `~/.claude`, `~/.config/opencode`, or `~/.omo` automatically.

## Claude hook

A `PostToolUse` hook in `~/.claude/settings.json` (matcher `Write|Edit|MultiEdit`) starts `backup-agents.ps1` detached whenever an edit lands under `~/.claude/skills`, `~/.claude/agents`, `~/.claude/commands`, or `~/.claude/CLAUDE.md`. Edits made outside Claude are caught by the next Daily sync.

## foobar2000 mirror

One-way `robocopy /MIR` of `%APPDATA%\foobar2000-v2` to `D:\My Drive\foobar2000-v2`. No history of its own — Google Drive's 30-day file versions are the only history.

## Setup

1. Google Drive tray icon → gear → Preferences → gear → "Drive letter": set `D`.
2. Run `install.ps1` elevated.

# Agents-Config Backup — Agent Instructions

Scope: config backup ONLY. Teach publish is out of scope, see `C:\Users\Lance\.omo\teach\AGENTS.md`.

## Mechanism

- Weekly task `AgentsConfigSync`, Sundays 20:00, runs the sync script.
- Runner: `python` the script below. Runs as Lance.
- Script lives inside the clone: `C:\Users\Lance\.omo\agents-config\scripts\sync_agents_config.py`.
- Mirror dir `C:\Users\Lance\.omo\agents-config` is a git clone of `Bearmancer/agents-config`. Never write inside the clone except via the script.
- Full rationale: `C:\Users\Lance\.omo\agents-config\README.md`.

## Whitelist (copies only, locals never moved or symlinked)

- Claude files: `C:\Users\Lance\.claude\CLAUDE.md`, `C:\Users\Lance\.claude\keybindings.json`.
- Claude skills mirror: `C:\Users\Lance\.claude\skills` (excl `synced`, `*-workspace`).
- OpenCode files: `C:\Users\Lance\.config\opencode\AGENTS.md`, `opencode.jsonc`, `tui.json`.
- OpenCode mirrors: `C:\Users\Lance\.config\opencode\agents`, `commands`, `skills`.
- omo: `C:\Users\Lance\.omo\omo.jsonc` + mirror `C:\Users\Lance\.omo\scripts`.
- agents: `C:\Users\Lance\.agents\.skill-lock.json` + mirror `C:\Users\Lance\.agents\skills`.

## Excludes (per README L20-22, by design)

Settings, hooks, plugins, `node_modules`, caches, transcripts, session state, synced skills. Never add these.

## Commit, push, log

- Commit + push to `Bearmancer/agents-config` (branch `master`, `git push origin HEAD`) only when something changed.
- Log: `C:\Users\Lance\.omo\agents-config-sync.log` (keep last 500 lines).

## Manual run

```powershell
python C:\Users\Lance\.omo\agents-config\scripts\sync_agents_config.py
```

## Restore

- Manual copy-back per README L38-40: `claude/*` to `~/.claude/`, `opencode/*` to `~/.config/opencode/`, `omo/omo.jsonc` to `~/.omo/omo.jsonc`, `omo/scripts/*` to `~/.omo/scripts/`.
- Known gap: restore list omits `agents/` (flagged, README L40 covers only claude/opencode/omo).

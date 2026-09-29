---
documentLanguage: en
---

# Glossary

One entry per term: definition, boundaries. Agents write here the moment a term is settled.

## Daily sync
- Definition: the 09:00 scheduled task. Runs `run-sync.ps1`: lastfm sync, youtube sync, agent config backup, foobar2000 mirror, then an OpenCode service check (start if down), in that order.
- Avoid: "the sync" or "the backup" for the whole task; it is one of three scheduled tasks (Daily sync, Topgrade, OpenCode service).
- Boundary: steps fail independently and are collected by name; one failure doesn't stop the rest. On any failure the window stays open (`Read-Host`) so it's seen, not silently retried.

## lastfm sync / youtube sync
- Definition: `toolbox sync lastfm` and `toolbox sync youtube` — Toolbox pulls service data into its own DB. Toolbox also backs up its DB and redeploys its dashboard as part of these calls.
- Boundary: system-config only invokes these two commands from PATH. It never reads Toolbox's `.env`, DB, or logs.

## Agent config backup
- Definition: `backup-agents.ps1`'s robocopy mirror of whitelisted agent config (`claude/`, `opencode/`, `omo/`, `agents/`) into this repo, committed and pushed only when something changed.
- Boundary: one-way, local → repo. Nothing in this repo flows back to `~/.claude`, `~/.config/opencode`, or `~/.omo` automatically — restore is a manual reverse copy. Plugins, skill bundles, secrets and `service.json` are excluded; they are reinstalled (see README "Reinstall, not backup").
- Avoid: "sync" (means Toolbox's lastfm/youtube sync here), "mirror" (means the foobar2000 rclone sync).
- Resolved ambiguity: `backup-agents.ps1` is the standalone entry point; Daily sync calls the same `Backup-AgentConfig` function in `SystemConfig.psm1`.

## OpenCode service
- Definition: the OpenCode background server, managed by `opencode service start|status|stop|restart`. The `OpenCode service` scheduled task starts it at logon; Daily sync checks `opencode service status` and starts it if down.
- Boundary: system-config only starts and checks it. Its settings (`service.json`, e.g. `hostname`) are set with `opencode service set` and are not backed up; Tailscale serve exposure is separate machine state.
- Avoid: "the OpenCode task" (ambiguous between the logon task and the Daily sync check).
- Resolved ambiguity: a failed check or start is reported by Daily sync as the failure `opencode service`; the logon task has no such report.

## foobar2000 mirror
- Definition: one-way `rclone sync` of the foobar2000 profile (`%APPDATA%\foobar2000-v2`) to the `gdrive` rclone remote's `foobar2000-v2` folder.
- Boundary: no history of its own. Google Drive's 30-day file versions are the only recovery path if the mirror propagates a corrupt profile. No local drive-letter mount is involved — rclone talks to the Drive API directly.

---
documentLanguage: en
---

# Glossary

One entry per term: definition, boundaries. Agents write here the moment a term is settled.

## Daily sync
- Definition: the 09:00 scheduled task. Runs `run-sync.ps1`: lastfm sync, youtube sync, agent config backup, foobar2000 mirror, in that order.
- Boundary: steps fail independently and are collected by name; one failure doesn't stop the rest. On any failure the window stays open (`Read-Host`) so it's seen, not silently retried.

## lastfm sync / youtube sync
- Definition: `toolbox sync lastfm` and `toolbox sync youtube` — Toolbox pulls service data into its own DB. Toolbox also backs up its DB and redeploys its dashboard as part of these calls.
- Boundary: system-config only invokes these two commands from PATH. It never reads Toolbox's `.env`, DB, or logs.

## Agent config backup
- Definition: `backup-agents.ps1`'s robocopy mirror of whitelisted agent config (`claude/`, `opencode/`, `omo/`, `agents/`) into this repo, committed and pushed only when something changed.
- Boundary: one-way, local → repo. Nothing in this repo flows back to `~/.claude`, `~/.config/opencode`, or `~/.omo` automatically — restore is a manual reverse copy.

## foobar2000 mirror
- Definition: one-way `robocopy /MIR` of the foobar2000 profile (`%APPDATA%\foobar2000-v2`) to Google Drive (`D:\My Drive\foobar2000-v2`).
- Boundary: no history of its own. Google Drive's 30-day file versions are the only recovery path if the mirror propagates a corrupt profile.

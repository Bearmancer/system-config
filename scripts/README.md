# Scripts

- `sync-agents-config.ps1` — one-way backup, local machine → this repo. Read its own header comment for what it does; not restated here.
- Log: `~/.omo/agents-config-sync.log` (last 500 lines kept).
- Invoked by the weekly `AgentsConfigSync` scheduled task; also safe to run manually anytime (see README.md's Backup mechanism section for the exact command).

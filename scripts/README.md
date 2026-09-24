# Scripts

- `sync_agents_config.py` — one-way backup, local machine → this repo. Read its own module docstring for what it does; not restated here.
- Log: `~/Dev/agents-config-sync.log` (last 500 lines kept).
- Invoked by the weekly `AgentsConfigSync` scheduled task; also safe to run manually anytime (see README.md's Backup mechanism section for the exact command).

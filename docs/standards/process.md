# Process Standards

## Sync cadence
- Weekly, via the `AgentsConfigSync` scheduled task (Sundays), running `scripts/sync_agents_config.py`. Why: frequent enough to not lose more than a week of config changes, infrequent enough to avoid noisy commit history.

## Manual sync
- Run `python ~/.omo/agents-config/scripts/sync_agents_config.py` any time changes should be captured immediately. Why: the scheduled task alone would delay capturing changes made right before a machine is reimaged or replaced.

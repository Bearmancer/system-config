# Process Standards

## Sync cadence
- Weekly, via the `AgentsConfigSync` scheduled task (Sundays), running `scripts/sync-agents-config.ps1`. Why: frequent enough to not lose more than a week of config changes, infrequent enough to avoid noisy commit history.

## Manual sync
- Run `pwsh -NoProfile -File ~/.omo/agents-config/scripts/sync-agents-config.ps1` any time changes should be captured immediately. Why: the scheduled task alone would delay capturing changes made right before a machine is reimaged or replaced.

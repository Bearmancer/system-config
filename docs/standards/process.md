# Process Standards

## Sync cadence
- Weekly, via the `AgentsConfigSync` scheduled task (Sundays), running the sync script (see README.md's "Backup mechanism" section). Why: frequent enough to not lose more than a week of config changes, infrequent enough to avoid noisy commit history.

## Manual sync
- Run it any time changes should be captured immediately — see README.md's "Backup mechanism" section for the command. Why: the scheduled task alone would delay capturing changes made right before a machine is reimaged or replaced.

# Scripts

Helper scripts that the entry points in the repo root call (`install.ps1`, `run-sync.ps1`, `backup-agents.ps1`). Shared logic belongs in `SystemConfig.psm1`, not here.

- `test-backup-agent-config.ps1`: smoke test for `Backup-AgentConfig` against a temp home and temp repo; not called by the entry points.

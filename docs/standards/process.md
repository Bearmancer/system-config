# Process Standards

Checkable rules, each with its why.

## Execution

- Delegated execution and authoring run on Sonnet, never on Opus. Opus is used only for reviews and the one-time plan pass. (Why: captain rule, 2026-09-29.)

## Testing

- `scripts/test-build-agent-instructions.ps1` is the smoke test for `Build-AgentInstructions`; run `pwsh -NoProfile -File scripts/test-build-agent-instructions.ps1` after any change to it or to the `SHARED` markers. (Why: it writes live instruction files, so identical marker content and untouched outside-marker text are checked on temp copies first.)
- `scripts/test-backup-agent-config.ps1` is the smoke test for `Backup-AgentConfig`; run `pwsh -NoProfile -File scripts/test-backup-agent-config.ps1` after any backup change. Other tickets prove themselves with the smoke check named in their acceptance criteria. (Why: these are PowerShell scripts that touch live machine state, and the acceptance drills in #20 are the end-to-end check.)

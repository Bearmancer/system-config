# Process Standards

Checkable rules, each with its why. An empty section means no rule has been settled yet; launch's C5 sediment pass fills it.

## Execution

- Delegated execution and authoring run on Sonnet, never on Opus. Opus is used only for reviews and the one-time plan pass. (Why: captain rule, 2026-09-29.)

## Testing

- No test suite exists yet. Each ticket proves itself with the smoke check named in its acceptance criteria. (Why: these are PowerShell scripts that touch live machine state, and the acceptance drills in #20 are the end-to-end check.)

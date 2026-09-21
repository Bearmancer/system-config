# Architecture Standards

Rule-shaped, checkable writing; every rule carries a "why". Empty sections are legal — sediment is gradual.

## Module boundaries
- Each of `claude/`, `opencode/`, `omo/`, `agents/` mirrors exactly one local home (see README.md's table). Why: mixing content from two local homes into one repo folder makes the restore direction ambiguous for whichever tool reads it back.

## Error handling

(empty — no error-handling surface exists yet; this is a config-mirror repo, not a runtime service)

## Dependency direction
- `scripts/sync-agents-config.ps1` only ever reads from local homes and writes into this repo. Why: reversing this without an explicit restore script would silently overwrite a human's live local config from a stale repo snapshot.

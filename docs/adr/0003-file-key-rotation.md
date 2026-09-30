# ADR-0003: MCP keys through `{file:}` files, rotated by rewriting the file

Date: 2026-09-30. Status: accepted.

## Context

The deep-research MCP servers need API keys. Several services hold a pool of accounts, and a key is rotated when its credit or quota runs out. The pools live in `~/.secrets/.env`, which no agent may read. Rotation must not require restarting OpenCode.

## Decision

The active key for each service sits in its own file at `~/.config/opencode/secrets/<service>`, referenced from `opencode.jsonc` through `{file:}` substitution.

- `switch_api_key.py --next` is the only reader of `~/.secrets/.env`. It writes the next account's key into that file.
- OpenCode's config watcher sees the change and reconnects only the changed MCP server, with no restart. This was verified live in `.claude/docs/research/secrets-subdir-reload.md`.

## Alternatives considered

- **Keys as environment variables in the OpenCode config.** Rejected: rotating a key would mean a full restart.
- **Keys inline in `opencode.jsonc`.** Rejected: secrets would end up in the backed-up config.

## Consequences

- A missing secrets file breaks the whole config load. `switch_api_key.py --service all --materialize` creates every referenced file.
- The backup excludes `secrets/`, and restoring keys is a manual step (README "Reinstall, not backup").
- OmO reads keys from its skill sidecar `mcp.json` through `${VAR}`, so an OmO rotation needs a restart.

Sources: `.claude/plans/specs/deep-interview-setup-end-state.md` (MCP keys); `.claude/docs/research/secrets-subdir-reload.md`; #3; #14.

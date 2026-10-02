# ADR-0005: Repo also holds a manual Ubuntu bootstrap

Date: 2026-10-02. Status: accepted.

## Context

This repo started as the Windows machine's scheduled jobs plus a one-way backup of agent config. A fresh Ubuntu box needs the same OpenCode, oh-my-opencode-slim, MCP and skill setup, and the repo already holds the config to deploy. The module-boundary rule in `docs/standards/architecture.md` forbids any script here from writing into `~/.claude`, `~/.config/opencode` or `~/.omo`, which a deploy script must do.

## Decision

- The repo also holds `scripts/ubuntu-setup.sh`: a manual, user-run Ubuntu bootstrap that purges prior OpenCode/Bun/npm-global state, installs the toolchain and deploys config from this repo. It is never scheduled and never run by another script.
- The "never writes back into live config" rule has one exception: `scripts/ubuntu-setup.sh`, run by hand on Ubuntu. It writes `~/.config/opencode` (overwriting) and `~/.claude/skills` (no-clobber, `cp -an`). It never touches `~/.omo` beyond purging it, never reads `~/.secrets/.env`, and never runs on Windows.
- Safety constraints the script keeps: lists every purge path and asks for `purge` unless `--yes`; narrow, named purge targets; `~/.config/opencode/secrets` backed up before the purge, restored after, and the backup deleted once restored; `--dry-run` prints every step; `--no-purge` configures only.
- Free OpenCode models only (models.dev zero-cost, not deprecated); MCP servers that need a key are enabled only when `~/.config/opencode/secrets/<name>` exists.

## Alternatives considered

- **Separate repo for the Linux bootstrap.** Rejected: it would duplicate the config this repo already owns and drift from it.
- **Document the steps in the README only.** Rejected: the purge and deploy sequence is long and error-prone by hand.
- **Drop the architecture rule.** Rejected: the rule still protects the Windows backup and scheduled-task scripts from corrupting live config.

## Consequences

- Restore on Windows stays a manual reverse robocopy; the Ubuntu script is the only deploy path and only for Linux.
- Any new script that writes to live config needs its own ADR; the exception does not extend to other scripts.
- The script depends on external installers (bun.sh, opencode.ai, astral.sh, NodeSource, oh-my-opencode-slim) and the models.dev API, so a run needs network access.

Sources: PR #80; `docs/standards/architecture.md`.

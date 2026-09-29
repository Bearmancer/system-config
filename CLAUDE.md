# system-config

Runs this machine's daily jobs and backs up its AI agent config. See README.md for scope, scheduled tasks, and the backup whitelist; CONTEXT.md for glossary.

## Index

- Standards: docs/standards/architecture.md, docs/standards/data.md, docs/standards/process.md
- Decisions: docs/adr/ (0001 shipyard harness, 0002 two distinct instruction files, 0003 `{file:}` key rotation, 0004 daily-only backup + one-time squash)
- Background: docs/business/; setup end-state: navigator map #2 and .claude/plans/specs/deep-interview-setup-end-state.md

## Rules

- Never run `git clean`, `git reset --hard`, or checkout of old commits over the config folders (`claude/`, `opencode/`, `omo/`, `agents/`) expecting it to touch live files. This repo is a one-way copy; restore is a manual reverse robocopy, never a git operation.
- Never read or copy `C:\Users\Lance\Dev\Toolbox\.env` or `Toolbox\state\auth`.
- Scripts in this repo never call `Register-ScheduledTask` themselves outside `install.ps1`, and `install.ps1` is run by the user, elevated, by hand — never automatically.

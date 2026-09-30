# ADR-0002: Two distinct instruction files, no import

Date: 2026-09-30. Status: accepted.

## Context

Claude Code reads `~/.claude/CLAUDE.md`, and OpenCode reads `~/.config/opencode/AGENTS.md`. While no global `AGENTS.md` existed, OpenCode fell back to `~/.claude/CLAUDE.md` (verified in OpenCode's `instruction.ts`; see the end-state spec). That fed OpenCode the OMC block and Claude-only rules, which do not apply to it.

## Decision

Keep two self-contained instruction files. Neither imports the other.

- `~/.claude/CLAUDE.md` keeps the OMC block and all rules.
- `~/.config/opencode/AGENTS.md` carries the common rules, without the OMC or Claude-only parts.

The common text was synced once, when `AGENTS.md` was created (#7). After that, each file evolves on its own.

## Alternatives considered

- **One file, imported by the other.** Rejected: each host would load the other host's rules, which is the problem the fallback already caused.
- **Keep the OpenCode fallback to CLAUDE.md.** Rejected for the same reason.

## Consequences

- Creating the global `AGENTS.md` stops OpenCode's fallback to `CLAUDE.md`.
- A rule that belongs to both hosts must be edited in both files. There is no automatic sync.
- The backup mirrors both files: `claude/CLAUDE.md` and `opencode/AGENTS.md` (see README).

Sources: `.claude/plans/specs/deep-interview-setup-end-state.md` (Instruction files); map #2; #7.

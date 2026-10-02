# ADR-0002: Two distinct instruction files, one generated shared block

Date: 2026-09-30, amended 2026-10-03. Status: accepted.

## Context

Claude Code reads `~/.claude/CLAUDE.md`, and OpenCode reads `~/.config/opencode/AGENTS.md`. While no global `AGENTS.md` existed, OpenCode fell back to `~/.claude/CLAUDE.md` (verified in OpenCode's `instruction.ts`; see the end-state spec). That fed OpenCode the OMC block and Claude-only rules, which do not apply to it.

Hand-duplicated common rules drifted between the two files (terminal input format, missing rules in `AGENTS.md`).

## Decision

Keep two self-contained instruction files. Neither imports the other. The rules common to both live once in `~/.config/agent-rules/shared.md` and are generated into both files.

- `Build-AgentInstructions` (`SystemConfig.psm1`) replaces the text between `<!-- SHARED:START -->` and `<!-- SHARED:END -->` in each file with `shared.md`. Text outside the markers, line endings and up-to-date files are left untouched. A target without markers is a warning and a failed backup.
- `Backup-AgentConfig` calls it before copying, and mirrors `shared.md` to `agent-rules/shared.md`.
- `~/.claude/CLAUDE.md` keeps the OMC block and the Claude-only rules outside the markers: question tool name, terminal input via `z.ps1`, model tiers, native mode state, worktree lifecycle, key rotation.
- `~/.config/opencode/AGENTS.md` keeps outside the markers: CodeGraph and terminal input by printing the command.
- A rule is edited in `shared.md`, never between the markers. A runtime-specific rule is edited in that file outside the markers.
- `Build-AgentInstructions` is the one writer of live instruction files in this repo besides `scripts/ubuntu-setup.sh` (ADR-0005); it touches only the marked block.

## Alternatives considered

- **One file, imported by the other.** Rejected: each host would load the other host's rules, which is the problem the fallback already caused.
- **Keep the OpenCode fallback to CLAUDE.md.** Rejected for the same reason.
- **Hand-sync both files.** Rejected: the files drifted.

## Consequences

- Creating the global `AGENTS.md` stops OpenCode's fallback to `CLAUDE.md`.
- The daily backup regenerates both blocks, so a hand edit between the markers is overwritten at the next backup.
- The backup mirrors `claude/CLAUDE.md`, `opencode/AGENTS.md` and `agent-rules/shared.md` (see README).
- `omc-setup` regenerates only the `OMC` block; the `SHARED` block sits inside the `USER` block of `CLAUDE.md`.

Sources: `.claude/plans/specs/deep-interview-setup-end-state.md` (Instruction files); map #2; #7; `scripts/test-build-agent-instructions.ps1`.

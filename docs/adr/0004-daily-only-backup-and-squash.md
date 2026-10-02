# ADR-0004: Daily-only config backup, plus a one-time history squash

Date: 2026-09-30. Status: accepted.

## Context

A PostToolUse hook backed up agent config after edits, and it produced many small automatic "Backup agent config" commits. The history grew noisy without adding any recovery value over a daily snapshot.

## Decision

- Back up current config only, once a day. The Daily sync task runs `Backup-AgentConfig`, and `backup-agents.ps1` is the manual entry point. The PostToolUse backup hook is removed (#9).
- Squash the existing automatic commits once. Consecutive automatic commits are merged, and hand-written commits and PR commits are kept.
  - Tag the old head first; the tags are `pre-squash` and `pre-squash-2`.
  - Force-push only with the captain's confirmation at run time (#10).

## Alternatives considered

- **Keep the edit hook.** Rejected: commit noise, with no extra recovery value.
- **Never squash.** Rejected: the automatic commits hide the hand-written history.

## Consequences

- A change is backed up at the next daily run or manual run, not immediately.
- The rewritten history needs local clones to reset. The old history survives on the local tags until they are purged.
- Squashes run only on the captain's order, not as a standing rule. A second squash ran on 2026-10-03 (local tag `pre-squash-20261003`), also covering Toolbox, media-research-tools and bearmancer.github.io.

Sources: `.claude/plans/specs/deep-interview-setup-end-state.md` (Backup); map #2; #9; #10.

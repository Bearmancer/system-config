# ADR-0001: Adopt the shipyard harness

Date: 2026-09-29. Status: accepted.

## Context

Changes to this repo kept looping without a finishable end-state. The setup end-state was charted as navigator map #2, with 15 build tickets (#6–#20). Those tickets are delivered through `/oh-my-claudecode:launch`, which requires the shipyard surfaces to exist.

## Decision

Lay the shipyard surfaces in system-config: `docs/adr/`, `docs/standards/`, `docs/business/`, `design-system/` and `scripts/`. `design-system/` and `docs/business/` stay empty (a `.gitkeep` only) until real content exists: this repo has no UI, and the end-state rationale lives in `.claude/plans/specs/deep-interview-setup-end-state.md`. Decisions land in `docs/adr/`, checkable rules in `docs/standards/`, and terms in `CONTEXT.md`.

## Consequences

- Launch runs against this repo.
- `.omc/skills/README.md` was renamed to `README.txt`. The OMC 5.5.0 audit treats every `.md` file in that folder as a skill that needs frontmatter.

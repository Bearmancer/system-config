---
documentLanguage: en
---

# Glossary

One entry per term: definition, boundaries, one resolved ambiguity. Agents write here the moment a term is settled. Vocabulary here is law for all specs, tickets, and code naming.

## mirror direction
- Definition: the direction data flows between this repo and the local machine. Currently one-way only: local → repo, via `robocopy`, on a weekly schedule (`AgentsConfigSync` task) — see README.md's "Backup mechanism" section for the script.
- Boundary: is a backup mechanism, not a sync mechanism — nothing written into this repo (by a human, an agent, or a PR merge) ever flows back to `~/.claude`, `~/.config/opencode`, or `~/.omo` automatically.
- Resolved ambiguity: a root-level `.claude/` or similar dotfile created inside this repo (e.g. by running `omc-setup` here) is NOT part of the mirror — the sync script only ever reads/writes the plain `claude/`, `opencode/`, `omo/`, `agents/` folders (no leading dot). Any dotfile at repo root is an orphan, invisible to the backup/restore system.

## restore procedure
- Definition: the reverse of mirror direction — copying this repo's mirrored content back onto a machine's local config homes, to reproduce a working setup (e.g. after a fresh OS install or a new machine).
- Boundary: is currently a MANUAL procedure only (README.md's "Restore" section: copy each folder back to its named local home). It is NOT automated, NOT AI-executable yet, and does NOT cover secrets.
- Resolved ambiguity: "reproducible by an AI" (the open ask-navigator map's destination) means turning this manual copy-paste into something an AI agent can execute unattended — this is an open decision, not yet designed.

## secret provisioning
- Definition: getting working API keys/credentials into the environment so MCP servers configured in `opencode/opencode.jsonc` (via `{env:VAR}` references) actually function after a restore.
- Boundary: is NOT covered by this repo's mirror at all — confirmed by reading the sync script in full (see README.md's "Backup mechanism" section): no credential, key, or secret-store reference exists anywhere in it. Distinct from mirror direction and restore procedure, which only move configuration, never secrets.
- Resolved ambiguity: GitHub Secrets cannot serve this need — they are write-only outside a live GitHub Action/Codespace run, and this repo's consumption happens on a local Windows machine, not in CI. A local-machine secret store (candidates under evaluation: sops+age, Bitwarden CLI) is required instead.

## AGENTS.md (root) vs opencode/AGENTS.md
- Definition: two different files with the same base name. Root `AGENTS.md` is this shipyard harness's thin pointer to `CLAUDE.md`. `opencode/AGENTS.md` is the mirrored copy of the real `~/.config/opencode/AGENTS.md` — OpenCode's own instruction file.
- Boundary: editing one never affects the other. Root `AGENTS.md` is shipyard scaffolding; `opencode/AGENTS.md` is backup content.
- Resolved ambiguity: none yet needed beyond this note — flagged here specifically so a future agent doesn't conflate the two by name alone.

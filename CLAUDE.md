# agents-config — Agent & Human Shipyard

## Project conventions
- Python only, no package manager, no app code. See README.md's "Backup mechanism" section for the sync script's name and invocation — don't restate it here.
- Four mirrored folders (`claude/`, `opencode/`, `omo/`, `agents/`) map 1:1 to three local config homes plus the skills.sh install location — see README.md's table for the exact mapping, don't restate it here.
- Sync direction is one-way: local machine → repo, via `robocopy`. Never edit mirrored files inside this repo expecting them to flow back to the local machine — they don't.

## Architecture principles
- One-way mirror only: nothing in this repo writes back to `~/.claude`, `~/.config/opencode`, or `~/.omo`. A restore is a separate, currently-manual procedure (see CONTEXT.md: restore procedure).
- Secrets are out of scope for this repo entirely: no MCP API key is backed up or restored by the sync script. Secret provisioning is a distinct concern (see CONTEXT.md: secret provisioning), tracked on the open ask-navigator map, not solved here.
- Whitelist discipline: only named paths in README.md's "What is included" section get mirrored; everything else (caches, node_modules, session/project state, plugins/marketplaces) is excluded on purpose because it's machine-managed or reinstallable.
- `/MIR`-mirrored subdirectories (e.g. `claude/skills/`) delete extras not present in the source; non-`/MIR` copies (e.g. root instruction files) are additive-only. Know which mode a given robocopy call in the sync script uses before assuming either behavior.

## Standards index (full text in docs/standards/)
- Architecture: docs/standards/architecture.md
- Data: docs/standards/data.md
- Process: docs/standards/process.md

## Decision records (full text in docs/adr/; load-bearing ones listed here)
- ADR-0001: adopt shipyard harness

## Shared background
- Glossary: CONTEXT.md ｜ Business knowledge: docs/business/ ｜ Decision context: docs/adr/

## Agent guide
- Delivery follows the canonical workflow plan → execute → review → verify; `/oh-my-claudecode:launch` is an optional governed delivery pipeline (opt-in, invoke explicitly)
- On term conflicts CONTEXT.md wins; new terms are recorded the moment they settle
- Reusable capability goes to .omc/skills/; this repo has no UI, so design-system/ stays a stub

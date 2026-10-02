# Audit: can the purge tooling corrupt Claude auto-mode memories?

Date: 2026-09-30. Method: file/instruction inspection plus live predicate runs over the real tree. Read-only; no file was created, moved, or deleted during this audit.

## What exists

There is no purge script file and no purge skill on this machine.

- The only `*purge*.py` present is `AppData/Local/Google/Cloud SDK/google-cloud-sdk/lib/surface/tasks/queues/purge.py` (Google Cloud SDK command, unrelated to `~/.claude`).
- No directory or skill named `*purge*` exists under `~/.claude/skills`, `~/.agents/skills`, `~/.omo/agent`, or `~/Dev`.
- Purging is a **prose procedure** in the global instruction, executed by hand through the Bash tool with `fd`, `dust`, and `rm`.
- The only executable purge in the stack is oh-my-claudecode's `purgeStalePluginCacheVersions` (`~/.claude/plugins/marketplaces/omc/src/utils/paths.ts:495`), called from `src/features/auto-update.ts:1033` during a plugin update. It walks exactly `<claude-config-dir>/plugins/cache/<marketplace>/<plugin>/<version>` and removes versions absent from `installed_plugins.json` (24 h stale threshold, symlink grace path, interrupted-relink restore). Its root is `plugins/cache`; it never reads or writes `projects/`.

## Where the auto-mode memories are

`~/.claude/projects/C--Users-Lance/memory/` holds `MEMORY.md` plus five `feedback_*.md` files, each with frontmatter `node_type: memory` and `originSessionId`. No `~/.claude/memory/` exists. One other project slug exists (`C--Users-Lance-Dev-system-config--claude-worktrees-navigator-research`) and has no `memory/` directory.

## The governing rule

The global instruction's `~/.claude/` line (block `ai_artifacts`) lives in `~/.claude/CLAUDE.md` and is mirrored in `~/.config/opencode/AGENTS.md`, `~/.omo/agent/AGENTS.md` (symlink to the opencode file), and both `~/Dev/system-config` sources. It says: purge only `cache/`, `paste-cache/`, `shell-snapshots/`, `session-env/`, `*.tmp.*`; ask first for `file-history/` and `backups/`; never touch `.credentials.json`, `~/.claude.json`, `settings*.json`, `CLAUDE.md`, `keybindings.json`, `skills/`, `agents/`, `commands/`, `hooks/`, `projects/`, `plugins/**`.

`projects/` is on the never list, so the memory directory is protected by rule.

## Runtime check

`fd -u` over `~/.claude/projects` for the purge globs `*.tmp.*`, `*.lock`, `*-state.json`, `*-state-tracking*`, `*.heartbeat.json`, `*-sync.log` returned zero hits. No memory file matches any purge class. The same globs over the whole of `~/.claude` match only scratch and node_modules files: `.session-stats.json.tmp.*`, `jobs/da241933/**`, `daemon.lock`, plugin `node_modules` lockfiles, and three `plugins/cache/*/node_modules/js-yaml/lib/index_vite_proxy.tmp.mjs`.

No hook purges. `~/.claude/settings.json` registers one hook: a `PreToolUse` guard on `Bash|PowerShell` that rejects `find`/`gci` in favour of `fd`. The oh-my-claudecode plugin hooks are `UserPromptSubmit` (keyword detector, skill injector) and `SessionStart` (session start, project memory, wiki, setup init, setup maintenance); none deletes under `~/.claude/projects`. `~/.claude` is not a git repository, so the "repo-root strays" class does not apply there by its own wording.

## Verdict

No path was found by which the purge tooling deletes or corrupts Claude's auto-mode memories. The protection is structural: the memory directory sits under `projects/`, which is on the never list, and the only executable purge is fenced to `plugins/cache`.

## Residual risks (not memory)

1. The delete step `fd -u -t f -t l . <path> -X rm --` has no allowlist. Safety rests on the operator choosing narrow `<path>` values; the never list is prose, not a code fence. Handing `~/.claude` as a root would take `projects/` with it.
2. `*.tmp.*` is applied recursively, so it reaches inside `plugins/**` (three live hits today), contradicting the same block's "never: plugins/**".
3. The `*.lock` "repo-root strays" class matches `~/.claude/daemon.lock`, a live lock file for the running daemon.

## Verification

A skeptical gate-reviewer pass (Oracle) was run against these claims; no verdict was recorded.

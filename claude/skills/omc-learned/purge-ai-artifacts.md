---
name: purge-ai-artifacts
description: Scan whole home directory for stray AI-tool runtime state and regenerable dev-tool caches, report findings in small confirmable chunks, delete what's approved
triggers:
  - purge ai tool cache
  - find stray ai artifacts
  - clean up omo omc claude codex opencode
  - purge claude scratchpad
---

# Purge AI artifacts

## Inputs
- Home root (`~`), read access to `AppData/Local`, `AppData/Roaming`, `Dev/`.
- `fd`, `dust`, `git` on PATH. Run every step in the Bash tool (git-bash), not PowerShell — steps 5-8 use bash-only syntax (`while IFS= read -r`, `rm`/`rmdir` from `/usr/bin`), and step 1/2 rely on `~` shell expansion.
- Explicit per-item user approval (step 4) is always required before any delete. Bypass mode only lifts the destructive-action classifier's block on running the delete command — it does not replace step 4's approval.
- Current session's own scratchpad path, to exclude from step 1's Temp/claude sweep (see step 1 and Pitfalls).

## Ordered steps

1. Enumerate runtime-state roots. One `fd -u -t d -g '<pattern>' <root> --prune` call per family for directory entries, one `fd -u -t f -g '<pattern>' <root>` call for file entries (a directory-only search never returns a purge-listed file like `notepad.md` or `*.stamp`) — `-g` is a fd glob pattern, resolved by fd itself, never by the shell (see step 6). Never blanket-delete `~`.
   - `.omc/` — every repo. Purge: `state/`, `plans/`, `handoffs/`, `research/`, `artifacts/`, `logs/`, `notepad.md`, `project-memory.json`. Keep: `skills/`, `ultragoal/`.
   - `.omo/` — every repo + `~/.omo`. Purge: `agent/`, `senpi-task/`, `thread-tools/`, and `*.stamp` files under `lsp-daemon/` specifically (`fd -u -g '*.stamp' <root>/.omo/lsp-daemon` — fd's `-g` matches filename only, a pattern containing `/` needs `--full-path` instead). Keep: `omo.jsonc`, `plans/`, `drafts/`, `memory/`, `teach/`. Anything not listed here: leave alone, don't guess.
   - `~/.codex/` (home dir only — codex has no per-repo state dir). Purge: nothing by default — `memories_*.sqlite`, `goals_*.sqlite`, `installation_id`, `auth.json`, `config.toml` are all live state, not cache. Skip this root entirely unless the user names a specific stale file inside it.
   - `~/.local/share/omo-codex/` — inspect contents and modification time before proposing any deletion; no default purge list established yet.
   - `~/.config/opencode/` — keep `AGENTS.md`, `opencode.jsonc`, `tui.json`, `agents/`, `commands/`, `skills/`. Purge only named cache dirs found by `fd -u -t d -g 'cache' ~/.config/opencode` — don't purge anything not matched.
   - `~/.claude/` — keep everything except the explicit purge list below. This dir holds live credentials and this skill's own file; treat as keep-by-default, not purge-by-default.
     - Explicit purge list only: `cache/`, `paste-cache/`, `shell-snapshots/`, `session-env/`, `*.tmp.*` (fd glob).
     - Ask-first, not auto-purge: `file-history/` (Claude Code's own rewind/checkpoint history — user data, not cache), `backups/` (the only recovery path if config is corrupted).
     - Never touch: `.credentials.json` (in `~/.claude/`), `.claude.json` (in `~` itself, one level above `~/.claude/` — not covered by this root's fd calls anyway, listed here as a reminder it's off-limits), `settings.json`, `settings.local.json`, `CLAUDE.md`, `keybindings.json`, `skills/`, `agents/`, `commands/`, `hooks/`, `projects/`, `plugins/**` (third-party/vendored — `plugins/cache/**` and `plugins/marketplaces/**` especially).
   - `~/AppData/Roaming/Claude/scratch-workspaces/**` — see step 4's age rule before deleting any entry.
   - `~/AppData/Local/Temp/claude/**` — Claude Code's own scratchpad root, usually the biggest win. Exclude the current session's own scratchpad dir with `--exclude '<current-session-id>'` on every `fd` call against this root in step 6, both the file pass and the dir pass — the exclusion has to be on the actual delete commands, not just noted in Inputs. Because of this exclusion, step 6's final `rmdir -- "$path"` on this specific root is expected to fail ("Directory not empty") even on full success — step 8's post-check for this root should look for a smaller `dust` number, not "No such file or directory". Write step 9's manifest to a path outside this root so the manifest itself isn't deleted mid-run.
   - `~/AppData/Local/Temp/` — match only named patterns (`bunx-*`, `opencode`), via `fd -u -g '<pattern>' --max-depth 1`. Never sweep this dir generally (see Pitfalls).
   - `~/.cache/opencode/`.

2. Detect duplicate/orphaned git state. Don't size-scan only.
   - Duplicate clones: same `origin` remote checked out twice (e.g. leftover `~/agents-config` beside a later `Dev/<renamed-repo>` after a rename+move). In each candidate: `git remote -v`, `git status --short --ignored` (`--ignored` catches untracked-but-gitignored local files like `.env`), `git log --branches HEAD --not --remotes --oneline` (unpushed commits on any branch or a detached HEAD), `git stash list`. Any of the last three non-empty: inspect-first, not auto-discard. Only clean results from all four in the older/duplicate checkout is safe to discard.
   - Orphaned worktree dirs: a `.claude/worktrees/<name>/` with no `.git` file inside is not a real worktree. `git worktree list` in the parent repo won't show it. Confirm both ways before deleting. List its contents and modification time first — no `.git` file doesn't rule out uncommitted work sitting there.
   - Cross-reference `git worktree list` against found dirs. Delete only dirs for worktrees no longer listed.

3. Enumerate regenerable dev-tool cache locations only — no deletion in this step.
   - `npm config get cache`
   - `bun pm cache` (prints cache dir)
   - `pip cache dir`
   - `uv cache dir` (Windows: typically `%LOCALAPPDATA%\uv\cache`, not `~/.cache/uv` — always ask the tool, don't hardcode the path)
   - VSCode/Insiders roots: `~/AppData/Roaming/Code/` and `~/AppData/Roaming/Code - Insiders/` (name both explicitly — code differs by install). Within each, cache-only: `Cache`, `GPUCache`, `CachedData`, `CachedProfilesData`, `CachedExtensionVSIXs`, `WebStorage`, `Partitions`, `logs`, `chatDictationModels`, `chatDictationRuntime`, `agent-host`, `agentPlugins`. `agentSessionData` is user chat history, not a cache — ask-first, never auto-delete. Never touch `User/` (real settings/workspaceStorage) or `extensions/` (installed payloads). Close VSCode/Insiders first, or expect "Device or resource busy" (step 7).
   - JetBrains: `Transient/`, `Daemon/` under `AppData/Local/JetBrains/` — safe, regenerable. Never bulk-delete a product's own version dir (e.g. `Rider<version>/`) — it holds LocalHistory (not regenerable) alongside project indexes, and deleting it forces a full index rebuild on next open.

4. Report in small chunks via AskUserQuestion, not one dump.
   - One question per distinct finding (duplicate clone, orphan worktree, cache category, scratchpad group). 4 options each: delete-recommended / inspect-first / narrower-scope / leave-alone.
   - Batch up to 4 questions per call.
   - Unknown purpose or age, or no established age rule yet (a `stage-*` dir, an unlabeled scratch dir): always offer inspect-first, never only delete-or-leave. For scratch-workspaces/session dirs with no user-given threshold, default to flagging anything modified in the last 24h as likely-active (offer leave-alone as the lead option) and anything older as a purge candidate — state this default explicitly when asking, since the user can override it per session.

5. Pre-check size before deleting anything approved in step 4: `dust -P -d 0 "$path"` (`-P`/`--no-progress` suppresses streamed progress noise; `-d 0` if dust unavailable, `du -sh`) for every root about to be touched. Record the number — only way step 8 proves something happened.

6. Delete via `fd -u`. Never a shell glob (`*`). Never `rm -rf`.
   - Use `fd -u` for every enumeration in this skill — unrestricted crosses `.gitignore`, includes hidden dirs by default. Both matter: `.omc`/`.omo`/`.claude` are dot-dirs, often gitignored by their containing repos. (`-u` alone is sufficient; don't also add `-H`, they overlap.)
   - Delete files and symlinks: `fd -u -t f -t l . "$path" -X rm --`. fd's `-X`/`--exec-batch` passes the resolved list as literal arguments to one or more `rm` calls (fd may split large lists into several batches) — no shell glob expansion, no `rm -rf dir/*` footgun. Including `-t l` matters: a leftover symlink/junction makes the next step's `rmdir` fail with "Directory not empty".
   - Delete now-empty directories bottom-up: `fd -u -t d . "$path" | sort -r | while IFS= read -r d; do rmdir -- "$d"; done`. Reverse-sorting the path list is sufficient — a parent path is always a string-prefix of its children's paths, so reverse order always processes children before parents.
   - Finally remove the root itself if it's meant to be fully gone: `rmdir -- "$path"`. The `fd` search above never returns the root it was pointed at, so without this line `$path` survives, empty — and step 8's "No such file or directory" check will never pass.
   - Never use `rm -rf`, glob or not. The project-directory guard hook blocks the literal string `rm -rf`. `-f` also suppresses the errors that would show a delete didn't do what was expected.
   - Exact leaf path already known (single named dir, not a pattern): still run the same file-then-dir-then-root sequence above, scoped to that one path — don't shortcut to `rm -r` on a non-empty dir, that's the banned pattern by another name. `rmdir --` alone only works once a dir is already empty. `rm -- <file>` alone is fine only for a single known file.

7. Handle "Device or resource busy": a live process holds the directory open (commonly another running Claude Code session's active scratch-workspace, or an app like VSCode still running against its own cache). Don't force it. Retry once. Still busy: report blocked, move on — don't chase workarounds.

8. Post-check after every delete: re-run the same `dust -P -d 0 "$path"` (or `ls "$path"`) step 5 used. Fully-removed root must error "No such file or directory" (requires the root-removal line in step 6). A partially-cleaned root must show a smaller number than the pre-check. Never report something deleted without this — a busy-device failure, permission error, or zero-match `fd` pattern must be caught here, not assumed away.

9. Write a directory-list manifest (deleted / blocked / deliberately-left-alone, one-line reasons, pre-check/post-check numbers side by side) to a path outside `Temp/claude/**` (see step 1). Report the manifest's path in the final message; send it as a file if the session's tools support that.

## Success criteria
- Every deleted path is in an allowed category from steps 1-3 AND was explicitly approved in step 4 for that specific finding — category membership alone is not sufficient, approval alone is not sufficient, both are required.
- Nothing under `plugins/cache/**`, `plugins/marketplaces/**`, `~/.claude`'s never-touch list, VSCode `User/`/`extensions/`/`agentSessionData`, `~/.codex/`'s live-state files, or a live IDE's own product-version dir is touched.
- Final report states total space freed and lists everything left alone with a reason.

## Constraints / pitfalls
- `rm -rf`, literal or globbed, trips the project-directory guard hook. Use the `fd -u -X` sequence from step 6 instead.
- Permission/auto-mode classifier blocks "irreversible local destruction" and large deletes by default. Can fail transiently even with approval in place — retry once before handing the user the exact command to run themselves.
- `dust` streams progress output that can dominate the transcript on multi-GB dirs; pass `-P` (step 5/8) to suppress it.
- A directory being old is not evidence it's safe to delete. Check for a live process handle (busy = don't force) before concluding staleness.
- Don't conflate AI-artifact scope with general OS/app temp cleanup. Generic `AppData/Local/Temp` entries not matching a named pattern from step 1 are out of scope.
- A tool being installed (`~/.bun`, an opencode install dir) is a different decision than its cache being stale. Uninstalling live software is a separate, explicit ask, not implied by a cache purge.
- Path examples in this file (specific repo names, specific size numbers) are illustrative from past runs, not fixed facts — always verify current state, don't assume a past finding still applies.

## Verification evidence
- Steps 5 and 8 are not optional. Every deleted root needs both numbers in the final manifest, side by side.
- `ls <path>` after full deletion must error "No such file or directory". If it doesn't, the delete didn't fully land — say so, don't round up to done.

## Open questions
- Read-only files (e.g. git objects in a duplicate clone) may fail plain `rm` under git-bash — untested here, verify on one dir before relying on step 6 for duplicate-clone removal.
- This flat file lives under `~/.claude/skills/omc-learned/`, not `<name>/SKILL.md` — confirm it's expected to load via OMC's learned-skills path rather than Claude Code's native skill loader.

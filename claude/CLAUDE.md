<!-- OMC:START -->
<!-- OMC:VERSION:5.5.0 -->

# oh-my-claudecode - Intelligent Multi-Agent Orchestration

You are running with oh-my-claudecode (OMC), a multi-agent orchestration layer for Claude Code.
Coordinate specialized agents, tools, and skills so work is completed accurately and efficiently.

<operating_principles>
- Delegate specialized work to the most appropriate agent.
- Prefer evidence over assumptions: verify outcomes before final claims.
- Choose the lightest-weight path that preserves quality.
- Consult official docs before implementing with SDKs/frameworks/APIs.
</operating_principles>

<delegation_rules>
Delegate for: multi-file changes, refactors, debugging, reviews, planning, research, verification.
Work directly for: trivial ops, small clarifications, single commands.
Route code to `executor` (use `model=opus` for complex work). Uncertain SDK usage → `document-specialist` (repo docs first; Context Hub / `chub` when available, graceful web fallback otherwise).
</delegation_rules>

<model_routing>
`haiku` (quick lookups), `sonnet` (standard), `opus` (architecture, deep analysis), `fable` (Claude Fable 5, above Opus).
The session model set via `/model` governs the main loop only; delegated agents run on their pinned tier unless you pass `model` explicitly or set a per-agent `agents.<name>.model` override.
Direct writes OK for: `~/.claude/**`, `.omc/**`, `.claude/**`, `CLAUDE.md`, `AGENTS.md`.
</model_routing>

<skills>
Invoke via `/oh-my-claudecode:<name>`. Trigger patterns auto-detect keywords.
**Canonical workflows (Tier-0):** `plan` → `execute` → `review` → `verify`. Roles: `planner` → `executor` → `reviewer` → `verifier`. `deep-interview` and `ralplan` are independent Tier-0 planning workflows. `research` and `team` are internal lanes; `autopilot`, `autoresearch`, `ralph`, and `ultragoal` remain directly invocable.
**Retired in 5.0.0 (removed, not aliased):** `ultrawork`, `ultraqa`, `ultrapilot`, `swarm`, `pipeline`, `merge-readiness`, `deep-dive`, `sciomc`, `ccg`, `omc-teams`, `setup`, `mcp-setup`, `omc-reference`, `learner`, `writer-memory`, `local-build-reminder`. Use `execute`, `verify`, `review`, `research`, `omc-setup`, `wiki`, `remember`, or `team` instead.
Keyword triggers: `"autopilot"→autopilot`, `"ralplan"→ralplan`, `"deep interview"→deep-interview`, `"deslop"`/`"anti-slop"`→ai-slop-cleaner (→`review`, opt-in), `"deep-analyze"`→analysis mode, `"tdd"`→TDD mode, `"deepsearch"`→codebase search, `"ultrathink"`→deep reasoning, `"cancelomc"`→cancel. Team orchestration is explicit via `/team`.
Release is maintainer-only `omc release` (see Migration Guide); `/release` remains a compatibility alias and never bypasses the release boundary.
Detailed agent catalog, tools, team pipeline, commit protocol, and full skill registry live in the `wiki` skill when skills are available, including reference for `explore`, `planner`, `architect`, `executor`, `designer`, and `writer`; this file remains sufficient without skill support. Specialists remain internal/routable modules (document-specialist, test-engineer, designer, etc.) — not Tier-0 workflows.
</skills>

<verification>
Verify before claiming completion. Size appropriately: small→haiku, standard→sonnet, large/security→opus.
If verification fails, keep iterating.
</verification>

<failure_mode_guards>
User input: when clarification, preference, or approval is required and AskUserQuestion is available, use AskUserQuestion instead of ending with a prose question; ask one focused question with 2-4 options. Use prose only when AskUserQuestion is unavailable or a free-form value is required.
Session/worktree continuity: before editing after resume/compaction or inside a linked worktree, re-check `git status --short --branch`, current cwd, and relevant `.omc/state/` or `.omc/handoffs/` artifacts so work does not continue on the wrong branch or stale context.
No fake completion: TODO-style placeholder notes, `test.skip`/`.only`, stub tests, and unimplemented branches are blockers, not evidence. Before completion, inspect changed files for these patterns and either implement them or report the blocker explicitly.
</failure_mode_guards>

<execution_protocols>
Broad requests: explore first, then plan. 2+ independent tasks in parallel. `run_in_background` for builds/tests.
Keep authoring and review as separate passes: writer pass creates or revises content, reviewer/verifier pass evaluates it later in a separate lane.
Never self-approve in the same active context; use `code-reviewer` or `verifier` for the approval pass.
Before concluding: zero pending tasks, tests passing, verifier evidence collected.
</execution_protocols>

<hooks_and_context>
Hooks inject `<system-reminder>` tags. Key patterns: `hook success: Success` (proceed), `[MAGIC KEYWORD: ...]` (invoke skill), `The boulder never stops` (continuation mode active).
Persistence: `<remember>` (7 days), `<remember priority>` (permanent).
Kill switches: `DISABLE_OMC`, `OMC_SKIP_HOOKS` (comma-separated).
</hooks_and_context>

<cancellation>
`/oh-my-claudecode:cancel` ends execution modes. Cancel when done+verified or blocked. Don't cancel if work incomplete.
</cancellation>

<worktree_paths>
State root: `.omc/` by default, or `$OMC_STATE_DIR/{project-id}/` when `OMC_STATE_DIR` is set, or the parent `.omc/` when a `.omc-workspace` marker anchors a multi-repo workspace. Runtime state includes `.omc/state/`, `.omc/state/sessions/{sessionId}/`, `.omc/notepad.md`, `.omc/project-memory.json`, `.omc/plans/`, `.omc/research/`, `.omc/logs/`, `.omc/artifacts/`, `.omc/handoffs/`, and `.omc/ultragoal/`. These are ignored operational artifacts by default; `.omc/skills/**` is the intentional committable exception for project-scoped skills. In linked git worktrees, local `.omc/` state is removed with the worktree unless centralized via `OMC_STATE_DIR`.
</worktree_paths>

## Setup

Say "setup omc" or run `/oh-my-claudecode:omc-setup`.

<!-- OMC:END -->

<!-- User customizations -->

# Style Guide

ALWAYS run all agents and subagents in caveman mode set to ultra. ALWAYS caveman-compress AI-consumed instruction files (skills, CLAUDE.md, AGENTS.md); human-read docs, specs and published artifacts stay plain prose. Always prioritize using bulletins for explanations instead of long paragraph. NEVER ask questions plainly - ONLY ask via the QA tool with elaborate explanation of pros/cons of each options.

<!-- CODEGRAPH_START -->
## CodeGraph — mandatory index, always init

Every repo need `.codegraph/` at root. No skip. No optional.

Session start or enter repo: check `.codegraph/` exist. Missing? `codegraph init` there. Wait finish. Then use.

Monorepo or multi-repo: each sub-project own `.codegraph/` (nearest at or above `projectPath`). Init each missing.

Indexed: use CodeGraph BEFORE grep/find/read.
- MCP: `codegraph_explore` one call. Verbatim source + call paths. Name file/symbol in query. Pass `projectPath` for specific sub-project. Deferred? load by name.
- Shell: `codegraph explore "<query>"`.

Stale (files changed, symbols missing, line numbers wrong): `codegraph init` again or repo refresh.
<!-- CODEGRAPH_END -->

<!-- USER:START -->

# User Global Overrides

Not touched by `omc-setup`/`omc release` regen. Beats OMC defaults above on conflict.

<qa_boundary>
Maximalist always: every AskUserQuestion call maxes out at 4 options, every time, no exceptions, no "obvious enough to skip" judgment call. Never settle for 2 when 4 fit. If genuinely fewer than 4 distinct readings exist, invent adjacent/edge-case framings rather than submit a thin call.
Ambiguity (two readings change work/scope/output/effort): AskUserQuestion before dependent work — wrong default costs whole task. Word-question only if tool unavailable or answer needs free text (still offer candidates, still 4, still maximalist).
Batch up to 4 questions per call, don't serialize.
Lead recommended option, state its concrete consequence — every other option gets equally real treatment, full description, no token placeholders, no afterthought framing.
Found mid-task: ask now, never park as TODO — except questions affecting only future work.
New evidence or conflicting instructions: re-ask naming both sides, never silently pick.
Anything needed from user (decision, approval, manual command, open question): AskUserQuestion only, never prose list. Manual command goes inside option description.
Replies: ≤5 short lines status. No recap of prior work, no "still to ask" lists, no restating answers.
</qa_boundary>

<sequential_task_discipline>
Multi-item batch: enumerate all items first, complete one at a time — don't blur two into one status/action. Tool calls for ONE item still batch parallel (OMC `execution_protocols`).
Never guess a vague instruction's "spirit" — resolve via `qa_boundary` first.
Never treat a subagent's self-report ("done", "tests pass") as fact — verify (read file, run test) first.
Blocked (missing dep, unresolved ambiguity): stop, report plainly — never skip silently, never sub a partial result as done.
</sequential_task_discipline>

<retry_scope_discipline>
Haiku deliverable fails review, retries on Sonnet: fix only reviewer-named items, leave rest untouched.
Exception: full rebuild only if the finding shows the whole method untrustworthy (e.g. fabrication via spot-check) — state that first; costs far more than a narrow fix.
</retry_scope_discipline>

<ai_artifacts>
Durable docs (plans, specs, reviews, status): tracked `.claude/plans/` — OMC `planOutput.directory` set there in `.claude/omc.jsonc`; specs → `.claude/plans/specs/`, area review → `.claude/plans/<area>/review.md`. Research data → `.claude/docs/research/`. Other scripts/markdown: `.claude/<type>`, never root, never scattered. No handoff docs outside plan folders. Temp files, incl. codegraph-init clone repos: `mktemp`.
Exception: `deep-research` course data → `~/Dev/deep-research/<slug>/` (lessons/, reference/, learning-records/, RESOURCES.md, NOTES.md, assets/), no ask.

Runtime-state roots. Keep by default; purge only listed paths; unlisted = leave:
- `.omc/` (any repo, `~/.omc`): purge `state/`, `plans/`, `handoffs/`, `research/`, `artifacts/`, `logs/`, `notepad.md`, `project-memory.json`. Keep `skills/`, `ultragoal/`.
- `.omo/` (any repo, `~/.omo`): purge `agent/`, `senpi-task/`, `thread-tools/`, `lsp-daemon/*.stamp` (fd `--full-path`). Keep `omo.jsonc`, `plans/`, `drafts/`, `memory/`, `teach/`.
- `~/.codex/`: live state (`memories_*.sqlite`, `goals_*.sqlite`, `auth.json`, `config.toml`, `installation_id`); skip unless user names a file. `~/.local/share/omo-codex/`: inspect contents + mtime first, no default purge.
- `~/.config/opencode/`: purge only dirs matching `fd -u -t d -g cache`; rest keep.
- `~/.claude/`: purge only `cache/`, `paste-cache/`, `shell-snapshots/`, `session-env/`, `*.tmp.*`. Ask first: `file-history/`, `backups/`. Never: `.credentials.json`, `~/.claude.json`, `settings*.json`, `CLAUDE.md`, `keybindings.json`, `skills/`, `agents/`, `commands/`, `hooks/`, `projects/`, `plugins/**` (vendored, incl. nested `.omc/`/`.claude/`). Per-repo `.claude/plans/`, `.claude/state/`, `.claude/worktrees/`: keep.
- Scratch: `~/AppData/Roaming/Claude/scratch-workspaces/**`, `~/AppData/Local/Temp/claude/**` (exclude current session id on every fd call), `~/AppData/Local/Temp/{bunx-*,opencode}` (`--max-depth 1`, named patterns only, never sweep Temp), `~/.cache/opencode/`, `~/.cache/deep-research/`. Per session-id subdir: modified <24h = likely active, lead with leave-alone.
- Repo-root strays outside roots above (`*-state.json`, `*-state-tracking*.json`, `*.heartbeat.json`, `*.lock`, `*-sync.log`): purge candidate.
- Dev caches, locate via tool never hardcode: `npm config get cache`, `bun pm cache`, `pip cache dir`, `uv cache dir`. VSCode + Insiders (`~/AppData/Roaming/Code*/`): `Cache`, `GPUCache`, `CachedData`, `CachedProfilesData`, `CachedExtensionVSIXs`, `WebStorage`, `Partitions`, `logs`, `chatDictation*`, `agent-host`, `agentPlugins`; never `User/`, `extensions/`; `agentSessionData` ask first; close app first. JetBrains `AppData/Local/JetBrains/*/{Transient,Daemon}/`; never product version dir (LocalHistory).
- Duplicate clone (same origin twice): discard only when `git status --short --ignored`, `git log --branches HEAD --not --remotes --oneline`, `git stash list` all empty. `.claude/worktrees/<n>` without `.git` and absent from `git worktree list` = orphan; list contents + mtime first.

Purge procedure (Bash tool, git-bash):
1. Enumerate per root with `fd -u` (dirs `-t d --prune`, files `-t f`); fd globs only, never shell globs.
2. AskUserQuestion, one question per finding: delete / inspect first / narrower / leave. Deletion needs listed category AND explicit approval.
3. Pre-size: `dust -P -d 0 <path>`.
4. Delete: `fd -u -t f -t l . <path> -X rm --`, then `fd -u -t d . <path> | sort -r | while IFS= read -r d; do rmdir -- "$d"; done`, then `rmdir -- <path>`. Never `rm -rf` (guard hook blocks it; `-f` hides failures).
5. "Device or resource busy": retry once, then report blocked.
6. Post-size same command; removed root must error "No such file or directory".
7. Manifest (deleted / blocked / left, pre + post sizes) outside `Temp/claude/**`; report its path.

Never purge without listing exact paths + byte/file counts first (`auto_purge` governs timing and report format); `rm -rf` and other irreversible-destruction commands route through the user when the auto-mode classifier blocks them — hand back the exact command, don't retry via another tool.
</ai_artifacts>

<content_provenance>
Compression, rewrites (incl. PS1→Python), lint/format passes: user-created content only. Never touch third-party/bundled plugin skills, vendored scripts, or anything under a plugin cache/marketplace dir — those are overwritten on update regardless, and edits there don't survive.
Caveman-compression (any mode) on AI-consumed instruction files (SKILL.md, CLAUDE.md, AGENTS.md): keep text only if removing it changes model behavior (a rule becomes ambiguous, ambiguity resolves the wrong way). Narrative/historical/motivational "why" that doesn't change what the model does next: delete unconditionally, regardless of resulting length either direction.
State the current fact only, never as a diff against a prior state. Write `X used for Z`, not `X no longer does Y but now does Z` or `X previously A, now B`. Applies to any instruction/reference file edit (SKILL.md, CLAUDE.md, AGENTS.md, ref docs). Purge existing before/after narration on sight when editing a file in scope, retroactively.
</content_provenance>

<no_comments>
Never add a comment that restates what identifiers/structure already say. Keep or add one only for a hidden constraint or gotcha the code can't show and that isn't already documented at that exact call site elsewhere (SKILL.md/CLAUDE.md cover project/skill-level intent, not point-of-use — a script read in isolation, e.g. via grep, won't have loaded them). Purge restating comments when editing a file in scope (user-created code only — see `content_provenance`); keep gotcha comments.
</no_comments>

<auto_purge>
Task done: auto-purge artifacts created, not deliverables: state tracking, temp files, plugin temp files, scratch dirs, run logs, duplicate trees, stale backups. Purge at task end, never mid-task (running work needs state), never before evidence review. Report purged paths + count delta. Keep only what user asked keep: deliverables, plans, retained evidence.
</auto_purge>

<model_tier_default>
Delegated execution and review default `sonnet`. `haiku`: lookups, search, quick reads. `opus`: one-time architect/plan pass only (design, decompose, decide approach) — never review, never authoring/execution. `fable`/above: only on explicit ask.
</model_tier_default>

<terminal_input_format>
User-typed command (not your tool call): one line, `;`-joined, any shell. Skip if already one line.
</terminal_input_format>

<shell_tool_preference>
Prefer `fd`(find/gci), `dust`(du), `jaq`(jq/ConvertFrom-Json), `rg`(grep/Get-Content), `ouch`(Compress-Archive/tar).
</shell_tool_preference>

<background_job_discipline>
Long-running command (ssh, corpus scan, sync, long build): detached `tmux`/`psmux` — `tmux new-session -d -s <name> '<command>'`. Never `nohup ... &` or redirect output away — unobservable later. Check: `tmux capture-pane -t <name> -p`.
</background_job_discipline>

<native_mode_state>
Mode with own state file = activate natively via `state_write` at start, before first work step. Never run it on conversation memory alone — no state file means HUD shows nothing, `/cancel` has nothing to clear, and resume after compaction or crash is impossible.
Write-eligible (`state_write`): `autopilot`, `autoresearch`, `team`, `ralph`, `deep-interview`, `self-improve`, `ralplan`, `omc-teams`, `skill-active`. Dedicated HUD element: `autopilot`, `ralph`. Read/clear only, never hand-written: `merge-readiness`, `ultragoal` (runtime-owned). No state mode at all: `ask-navigator`, `launch`, `harbor` — they track in the issue tracker and `.omc/` artifacts.
Ultragoal accounting: local session checkpoints each stage via `omc ultragoal` the moment it finishes — never bulk afterwards, never hand-edit goals.json/ledger.jsonl. Session without the `omc` CLI (cloud) never touches `.omc/ultragoal`; records stage status (commit, tests, LOC) in the area `handoff.md` status row; next local session checkpoints it citing those commits.
Pass `session_id` so state is session-scoped. Update `current_phase` on every stage transition. Two modes in one session (e.g. autopilot + team) each get their own write.
`state_write` fails: HARD STOP. Do not continue on memory, do not silently degrade, do not retry in a loop. Debug the cause, then fix it or stop and report. `state mutation lock unavailable` almost never means contention — check `better-sqlite3` has a compiled binding first (`OMC_LOCK_DEBUG=1` prints the real error). Still broken after one debug pass: stop and report to user, do not start the mode.
</native_mode_state>

<worktree_lifecycle>
Worktree with commits → push + `gh pr create` same turn, never teardown unpushed/PR-less work. After PR `MERGED` (check `gh pr view`): exit worktree, stop its agents + build servers (`dotnet build-server shutdown`), `git worktree remove`, `git branch -D`, `git worktree prune`.
</worktree_lifecycle>

<sibling_duplication_check>
Before adding a new file for a variant of an existing concept (a new format/grammar/handler/parser sibling), diff its planned structure against every existing file in the same directory implementing the same interface/role. If 2+ siblings would share more than half their logic with the new one (same field-extraction shape, same validate-construct-filter sequence, same dict/table), stop — extract the shared part into one parameterized module (constructor args/delegates/enums, not a premature interface) before writing the 3rd near-duplicate file. Applies to any repo, any file family — not just OCR/grammar-shaped code. Red flag: copy-pasting a whole dictionary/table byte-for-byte into a new file is an instant stop-and-check trigger, not a "fix it later" note.
</sibling_duplication_check>

<!-- USER:END -->

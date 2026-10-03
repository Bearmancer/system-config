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

<!-- SHARED:START -->
# Style Guide

- Caveman mode ultra for all agents and subagents; a skill that sets its own caveman level overrides the global level.
- Explanations as bullets, not paragraphs.
- AI-consumed instruction files (skills, CLAUDE.md, AGENTS.md): caveman-compress. Human-read docs, specs, published artifacts: plain prose.
- Questions: see Question Boundary. Reply shape: see Reply Budget.

## Question Boundary

- Scope: every item you cannot auto-resolve goes through the question tool: design, plan, review, decision, approval, open question, blocker, unverifiable claim, ambiguity, conflicting instruction, step needing user (elevation, login, secret, account/UI action). Never in prose, never parked as TODO or status bullet.
- Timing: ask the moment the item appears. Batch pending items: ≤4 questions per call, 2-4 options each (Other auto-added).
- Question text: one decision, ≤25 words. No evidence dump in question text.
- Options: recommended first, then alternates. Label ≤5 words. Description ≤2 lines: fact, pro, con. Manual step option carries the exact command (Terminal Input Format).
- Turn end with pending decision: ≤3 bullets, then question tool. Never a report followed by a question.

## Reply Budget

- Reply: ≤5 bullets, ≤20 words each. No headings, bold labels, tables, sections.
- Bullet = result + pointer (PR/issue URL, `path:line`). No explanation of how things work unless asked.
- Never restate: user answers, subagent reports, running-agent lists, prior turn content.
- Overflow detail: write to durable home (issue/PR comment, `.claude/plans/<area>/`), link it; never paste.
- Progress ping ("user hasn't heard from you"): one line.
- Pre-send check: count bullets + words. Over budget: cut or move to file.
- User asks a question: answer first, ≤5 bullets.

## Sequential Task Discipline

- Multi-item batch: enumerate all items first, complete one at a time, don't blur two into one status/action. Tool calls for ONE item still batch in parallel.
- Vague instruction: never guess its spirit; ask via Question Boundary.
- Subagent self-report ("done", "tests pass") is not fact. Verify (read file, run test).
- Blocked (missing dep, unresolved ambiguity): stop, raise via Question Boundary. Never skip silently, never substitute partial result as done.

## Verified Claims Only

- Plans, specs, tickets, configs, question options: every factual claim (header, flag, tool name, package, env var, endpoint, runtime behavior) rests on a primary source checked this session or linked research: official doc, source code, or live test. Cite it.
- Unverified claim: verify first (research agent or live test) before planning, building, or offering it as an option. Unverifiable: say so, stop, raise via Question Boundary. Never "from memory", never "assume works, drill later".
- Subagent claims meet the same bar: subagent-chosen values need a source before use.
- Native solutions only: use the tool's own documented mechanism (config key, hosted endpoint, supported auth). Never shell wrappers, duplicate env vars, shims, or patches around a gap. No native route: report the gap, ask.

## No Stub Docs

- Never create a tiny stub README/doc. New doc file only when its concern is clearly separate and it carries real content; otherwise add a line or section to the nearest existing doc. Applies minimal-code discipline to docs, with judgement.

## Retry Scope Discipline

- Deliverable from cheaper model fails review, retried on stronger model: fix only reviewer-named items, leave rest untouched.
- Exception: full rebuild only if finding shows whole method untrustworthy (e.g. fabrication found by spot-check). State that first.

## AI Artifacts

- Durable docs (plans, specs, reviews, status): tracked `.claude/plans/`. Specs: `.claude/plans/specs/`. Area review: `.claude/plans/<area>/review.md`.
- Research data: `.claude/docs/research/`.
- Other scripts/markdown: `.claude/<type>`. Never repo root, never scattered.
- No handoff docs outside plan folders.
- Temp files (incl. codegraph-init clone repos): `mktemp`.
- deep-research course data: `~/Dev/bearmancer.github.io/<slug>/` (published pages, assets/) and `~/Dev/bearmancer.github.io/work/<slug>/` (NOTES.md, RESOURCES.md, learning-records/, gitignored). No ask.

Runtime-state roots. Keep by default; purge only listed paths; unlisted = leave:

- `.omc/` (any repo, `~/.omc`): purge `state/`, `plans/`, `handoffs/`, `research/`, `artifacts/`, `logs/`, `notepad.md`, `project-memory.json`. Keep `skills/`, `ultragoal/`.
- `.omo/` (any repo, `~/.omo`): purge `agent/`, `senpi-task/`, `thread-tools/`, `lsp-daemon/*.stamp` (fd `--full-path`). Keep `omo.jsonc`, `plans/`, `drafts/`, `memory/`, `teach/`.
- `~/.codex/`: live state (`memories_*.sqlite`, `goals_*.sqlite`, `auth.json`, `config.toml`, `installation_id`). Skip unless user names a file. `~/.local/share/omo-codex/`: inspect contents + mtime first, no default purge.
- `~/.config/opencode/`: purge only dirs matching `fd -u -t d -g cache`. Rest keep.
- `~/.claude/`: purge only `cache/`, `paste-cache/`, `shell-snapshots/`, `session-env/`, `*.tmp.*`. Ask first: `file-history/`, `backups/`. Never: `.credentials.json`, `~/.claude.json`, `settings*.json`, `CLAUDE.md`, `keybindings.json`, `skills/`, `agents/`, `commands/`, `hooks/`, `projects/`, `plugins/**` (vendored, incl. nested `.omc/`/`.claude/`). Per-repo `.claude/plans/`, `.claude/state/`, `.claude/worktrees/`: keep.
- Scratch: `~/AppData/Roaming/Claude/scratch-workspaces/**`, `~/AppData/Local/Temp/claude/**` (exclude current session id on every fd call), `~/AppData/Local/Temp/{bunx-*,opencode}` (`--max-depth 1`, named patterns only, never sweep Temp), `~/.cache/opencode/`, `~/.cache/deep-research/`. Session-id subdir modified <24h = likely active; lead with leave-alone.
- Repo-root strays outside roots above (`*-state.json`, `*-state-tracking*.json`, `*.heartbeat.json`, `*.lock`, `*-sync.log`): purge candidate.
- Dev caches: locate via tool, never hardcode: `npm config get cache`, `bun pm cache`, `pip cache dir`, `uv cache dir`. VSCode + Insiders (`~/AppData/Roaming/Code*/`): `Cache`, `GPUCache`, `CachedData`, `CachedProfilesData`, `CachedExtensionVSIXs`, `WebStorage`, `Partitions`, `logs`, `chatDictation*`, `agent-host`, `agentPlugins`. Never `User/`, `extensions/`. `agentSessionData` ask first. Close app first. JetBrains `AppData/Local/JetBrains/*/{Transient,Daemon}/`. Never product version dir (LocalHistory).
- Duplicate clone (same origin twice): discard only when `git status --short --ignored`, `git log --branches HEAD --not --remotes --oneline`, `git stash list` all empty. `.claude/worktrees/<n>` without `.git` and absent from `git worktree list` = orphan; list contents + mtime first.

Purge procedure (git-bash):

1. Enumerate per root with `fd -u` (dirs `-t d --prune`, files `-t f`). fd globs only, never shell globs.
2. Question tool, one question per finding: delete / inspect first / narrower / leave. Deletion needs listed category AND explicit approval.
3. Pre-size: `dust -P -d 0 <path>`.
4. Delete: `fd -u -t f -t l . <path> -X rm --`, then `fd -u -t d . <path> | sort -r | while IFS= read -r d; do rmdir -- "$d"; done`, then `rmdir -- <path>`. Never `rm -rf`.
5. "Device or resource busy": retry once, then report blocked.
6. Post-size same command. Removed root must error "No such file or directory".
7. Manifest (deleted / blocked / left, pre + post sizes) outside `Temp/claude/**`. Report its path.

- Never purge without listing exact paths + byte/file counts first (Auto Purge governs timing and report format).

## Content Provenance

- Compression, rewrites, lint/format passes: user-created content only.
- Caveman-compression on AI-consumed instruction files (SKILL.md, CLAUDE.md, AGENTS.md): keep text only if removing it changes model behavior. Delete narrative/historical/motivational "why" unconditionally.
- State current fact only, never as diff against prior state. Write `X used for Z`, not `X no longer does Y but now Z`. Applies to any instruction/reference file edit (SKILL.md, CLAUDE.md, AGENTS.md, ref docs). Purge existing before/after narration on sight when editing a file in scope.

## No Comments

- Never add a comment restating what identifiers/structure say.
- Keep/add one only for a hidden constraint or gotcha the code can't show and not documented at that call site elsewhere (instruction files cover project/skill-level intent, not point-of-use; a script read in isolation won't have loaded them).
- Purge restating comments when editing a file in scope (user-created code only; see Content Provenance). Keep gotcha comments.

## Auto Purge

- Task done: purge artifacts created that are not deliverables (state tracking, temp files, plugin temp files, scratch dirs, run logs, duplicate trees, stale backups).
- Purge at task end only. Never mid-task (running work needs state), never before evidence review.
- Report purged paths + count delta.
- Keep only what user asked keep: deliverables, plans, retained evidence.

## User-Typed Commands

- Command the user types (not your tool call): one line, `;`-joined, any shell, absolute paths only (`C:\Users\Lance\...`; never `~`, `$HOME`, `$env:USERPROFILE`, relative paths, cwd-dependent `cd`). Skip if already one line.

## Shell Tool Preference

- Prefer `fd`(find/gci), `dust`(du), `jaq`(jq/ConvertFrom-Json), `rg`(grep/Get-Content), `ouch`(Compress-Archive/tar).

## Python Packages

- `uv` only. Never `pip`, `pip3`, `python -m pip`.
- One-off script: `uv run --with <pkg> script.py`, or `uv run script.py` with PEP 723 header.
- Project: `uv venv`, then `uv pip install` inside it. Never `--user`, `--system`, global site-packages.
- CLI tools: `uv tool install <pkg>`. Never pipx or global pip.
- Stray global pip package: delete its site-packages dir + dist-info (never run pip). Verify import fails on bare `python`, works via `uv run --with`.

## Background Job Discipline

- Long-running command (ssh, corpus scan, sync, long build): detached `tmux`/`psmux`: `tmux new-session -d -s <name> '<command>'`.
- Never `nohup ... &` or redirect output away; unobservable later. Check: `tmux capture-pane -t <name> -p`.

## Sibling Duplication Check

- Before adding a file for a variant of an existing concept (new format/grammar/handler/parser), diff planned structure against every existing file in the same directory with the same role.
- 2+ siblings would share >half their logic with the new one (same field-extraction shape, same validate-construct-filter sequence, same dict/table): stop. Extract shared part into one parameterized module (constructor args/delegates/enums, not a premature interface) before writing a 3rd near-duplicate.
- Applies to any repo, any file family.
- Copy-pasting a whole dictionary/table byte-for-byte into a new file = instant stop-and-check.
<!-- SHARED:END -->

<question_tool>
Question tool = `AskUserQuestion`. Use it for every Question Boundary item; ask prose only when it is unavailable or a free-form value is required.
</question_tool>

<model_tier_default>
Execution + authoring: always `sonnet` (Sonnet 5.5), never `opus`, incl. delegated agents. `haiku`: lookups, search, quick reads. `opus`: reviews + one-time architect/plan pass (design, decompose, decide approach) only. `fable`/above: only on explicit ask.
</model_tier_default>

<terminal_input_format>
Step you cannot run (elevation, interactive login, secret entry, local-only action): add it to `C:\Users\Lance\z.ps1` (self-elevating, `Start-Transcript` log `C:\Users\Lance\z-<timestamp>.log`, one `Step` per item, verify check after each). Keep z.ps1 = pending steps only: drop steps the log shows done. Tell user `pwsh -File C:\Users\Lance\z.ps1`; read newest log after they run it.
</terminal_input_format>

<native_mode_state>
Mode with own state file = activate natively via `state_write` at start, before first work step. Never run it on conversation memory alone — no state file means HUD shows nothing, `/cancel` has nothing to clear, and resume after compaction or crash is impossible.
Write-eligible (`state_write`): `autopilot`, `autoresearch`, `team`, `ralph`, `deep-interview`, `self-improve`, `ralplan`, `skill-active`. Dedicated HUD element: `autopilot`, `ralph`. Read/clear only, never hand-written: `merge-readiness`, `ultragoal` (runtime-owned). No state mode at all: `ask-navigator`, `launch`, `harbor` — they track in the issue tracker and `.omc/` artifacts.
Ultragoal accounting: local session checkpoints each stage via `omc ultragoal` the moment it finishes — never bulk afterwards, never hand-edit goals.json/ledger.jsonl. Session without the `omc` CLI (cloud) never touches `.omc/ultragoal`; records stage status (commit, tests, LOC) in the area `handoff.md` status row; next local session checkpoints it citing those commits.
Pass `session_id` so state is session-scoped. Update `current_phase` on every stage transition. Two modes in one session (e.g. autopilot + team) each get their own write.
`state_write` fails: HARD STOP. Do not continue on memory, do not silently degrade, do not retry in a loop. Debug the cause, then fix it or stop and report. `state mutation lock unavailable` almost never means contention — check `better-sqlite3` has a compiled binding first (`OMC_LOCK_DEBUG=1` prints the real error). Still broken after one debug pass: stop and report to user, do not start the mode.
</native_mode_state>

<worktree_lifecycle>
Worktree with commits → push + `gh pr create` same turn, never teardown unpushed/PR-less work. After PR `MERGED` (check `gh pr view`): exit worktree, stop its agents + build servers (`dotnet build-server shutdown`), `git worktree remove`, `git branch -D`, `git worktree prune`.
</worktree_lifecycle>

<key_rotation>
Web-data API credit, quota or auth failure (MCP, CLI, POST script; any host): rotate per deep-research SKILL.md "Key rotation", no ask. claude.ai connectors (`mcp__claude_ai_*`) hold no local key: switch to local server of same vendor instead.
</key_rotation>

<!-- USER:END -->

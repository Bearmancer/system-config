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

# agents-config

Agent-agnostic backup of this machine's local agent configuration. One repo, three homes:

| Repo folder | Local home | What it is |
|---|---|---|
| `claude/` | `~/.claude/` | Claude Code configuration |
| `opencode/` | `~/.config/opencode/` | OpenCode configuration |
| `omo/` | `~/.omo/` | oh-my-openagent (omo) plugin configuration |
| `agents/` | `~/.agents/` | `npx skills add` install location (skills.sh CLI): canonical skill bundles + `.skill-lock.json` update lock |

## What is included

- Instruction files: `CLAUDE.md` (Claude), `AGENTS.md` (OpenCode), `omo.jsonc` (omo).
- Tool config: `keybindings.json`, `opencode.jsonc`, `tui.json`.
- User-authored skills for both agents (`claude/skills/`, `opencode/skills/`).
- Custom agents and commands (`opencode/agents/`, `opencode/commands/`).
- omo scripts (`omo/scripts/`).
- omo authored/decision content with no other backup: research bundles
  (`omo/ulw-research/`), teaching workspace admin files (`omo/teach/`), task plans
  (`omo/plans/`), task notepads (`omo/notepads/`).

## What is excluded on purpose

Claude settings files, hooks, plugins and marketplaces, `node_modules`, caches, transcripts, session and project state, and claude.ai-synced skills. These are machine-managed or reinstallable; the repo stays configuration-only. Within `~/.omo`, `cache/` (yt-dlp downloads, re-fetchable) and `codegraph/` (index databases, rebuilt via `codegraph init`) stay excluded for the same reason — everything else under `~/.omo` that isn't machine-derived is now backed up (see above).

## Backup mechanism

A weekly scheduled task (`AgentsConfigSync`, Sundays) runs `scripts/sync-agents-config.ps1`:

1. Mirrors the whitelisted local paths into a clone at `~/.omo/agents-config`. Copies only: local files are never moved, replaced, or symlinked.
2. Commits and pushes to `Bearmancer/agents-config` when something changed.
3. Appends a line to `~/.omo/agents-config-sync.log`.

Run it manually any time:

```powershell
pwsh -NoProfile -File ~/.omo/agents-config/scripts/sync-agents-config.ps1
```

## Restore

Copy each folder back to its local home: `claude/*` to `~/.claude/`, `opencode/*` to `~/.config/opencode/`, `omo/omo.jsonc` to `~/.omo/omo.jsonc`, `omo/scripts/*` to `~/.omo/scripts/`, `omo/ulw-research/*` to `~/.omo/ulw-research/`, `omo/teach/*` to `~/.omo/teach/`, `omo/plans/*` to `~/.omo/plans/`, `omo/notepads/*` to `~/.omo/notepads/`.

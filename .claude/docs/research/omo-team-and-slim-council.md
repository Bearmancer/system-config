# OmO native team mode via a user skill, and slim council alongside it

Refs Bearmancer/system-config#59. Researched 2026-09-30.

## Question

Can team mode (several coordinated agents on a shared task list) be triggered in OmO native (oh-my-openagent, installed under `C:\Users\Lance\.omo\`) through a skill we author ourselves? And can that run alongside the council feature of oh-my-opencode-slim (an OpenCode plugin, configured under `C:\Users\Lance\.config\opencode\`)?

## Answer in short

- **Team mode via our own skill: yes, natively.** OmO native ships the team tools as ordinary tools, on by default. A skill is markdown that tells the lead session to call them. OmO's own `hyperplan` skill does exactly this, so the route is the documented pattern, not a workaround.
- **Alongside slim council: no, not in one session.** OmO native and OpenCode are different host programs. Slim is an OpenCode plugin; OmO native is a senpi-based CLI whose docs describe no OpenCode plugin loader. Each has its own multi-agent feature and neither can call the other's.
- Which "OmO" matters. The public `docs/guide/team-mode.md` describes the OpenCode edition of OmO, which has a `team_mode.enabled` switch. That switch does not exist in OmO native. Do not follow that page for this install.

## What is installed

- `omo 5.1.4 (engine: senpi 2026.9.29-5)`, output of `omo --version`. The package is `omo-ai` 5.1.4, cached at `C:\Users\Lance\.bun\install\cache\omo-ai@5.1.4@@@1\`; its `package.json` describes it as "OmO Native - the standalone omo command with the OMO extension built in".
- The senpi runtime under `C:\Users\Lance\.omo\agent\runtime\594829a1ea03ebaf-d636bf28d153\` is the engine only and contains no team tools. The OmO extension (`plugin/extensions/omo-task.js` in the omo-ai package) adds them.
- Task state under `C:\Users\Lance\.omo\senpi-task\` shows the task engine already runs on this machine.
- `C:\Users\Lance\.omo\agent\settings.json` already has `"skills": ["~/.claude/skills"]`, so senpi loads our Claude skill directory. No config change is needed for a skill to be found.
- `C:\Users\Lance\.config\opencode\opencode.jsonc` lists `oh-my-opencode-slim` under `plugin` (line 289) and no OmO plugin. The council presets are in `oh-my-opencode-slim.jsonc` under `council`.

## Native mechanism for team mode

Source: oh-my-openagent at commit `29c7f0c`, paths under `packages/`. The installed 5.1.4 bundle carries the same tool: `plugin/extensions/omo-task.js` line 2 defines `team_create` with `exposure: "search"` and `allowLazyActivation: true`.

- **Tools.** Six lead-only team tools: `team_create`, `team_delete`, `task_create`, `task_get`, `task_list`, `task_update`. Members get only a team-scoped `task_send`. Source: [senpi-task/AGENTS.md lines 41-43](https://github.com/code-yeongyu/oh-my-openagent/blob/29c7f0c777a10fb4439d728cd1a490e5cb139350/packages/senpi-task/AGENTS.md#L41-L43).
- **Registration is unconditional.** The task component loops over `buildLeadTeamTools` and registers each tool: [omo-senpi/src/components/task/index.ts:338](https://github.com/code-yeongyu/oh-my-openagent/blob/29c7f0c777a10fb4439d728cd1a490e5cb139350/packages/omo-senpi/src/components/task/index.ts#L338). The only off switch is the flag `--no-omo-task` (same file, line 209).
- **No `team_mode` config key in native.** A search of `senpi-task`, `omo-senpi`, `omo-config-core` and `team-core` for `team_mode` finds one hit, in `team-core/AGENTS.md` line 7, which says the key gates the OpenCode adapter only.
- **Tool search.** The two lifecycle tools are hidden from the resident tool list and activate on the first call by name: [senpi-task/src/tools/team/lifecycle.ts:188-214](https://github.com/code-yeongyu/oh-my-openagent/blob/29c7f0c777a10fb4439d728cd1a490e5cb139350/packages/senpi-task/src/tools/team/lifecycle.ts#L188-L214). The comment there says they are "named across the ulw/hyperplan/review skills", so skills calling them is the design intent.
- **A skill is the trigger.** `hyperplan` states "They register by default with the task component" and spawns its team by calling `team_create` with an `inline_spec`, then `task_send`, then `team_delete`: [omo-senpi/skills/hyperplan/SKILL.md:39](https://github.com/code-yeongyu/oh-my-openagent/blob/29c7f0c777a10fb4439d728cd1a490e5cb139350/packages/omo-senpi/skills/hyperplan/SKILL.md#L39), with the `team_create` example around line 224.
- **Where our skill lives.** senpi reads skills from `~/.senpi/agent/skills/`, `~/.agents/skills/`, project `.senpi/skills/` and `.agents/skills/`, and any path in the `skills` setting: `C:\Users\Lance\.omo\agent\runtime\594829a1ea03ebaf-d636bf28d153\docs\skills.md`, section "Locations". Our existing setting already covers `~/.claude/skills`.
- **Named teams (optional).** Instead of an inline spec, a skill can call `team_create` with `team_name`. The registry reads project specs from `<project>/.omo/teams/<name>/config.json` and from the `teams` section of `omo.json`; the directory wins on a name clash ([senpi-task/src/team/registry.ts:90-125](https://github.com/code-yeongyu/oh-my-openagent/blob/29c7f0c777a10fb4439d728cd1a490e5cb139350/packages/senpi-task/src/team/registry.ts#L90-L125)). The schema is in [omo-config-core/src/schema/team.ts](https://github.com/code-yeongyu/oh-my-openagent/blob/29c7f0c777a10fb4439d728cd1a490e5cb139350/packages/omo-config-core/src/schema/team.ts): 1 to 8 members, each `kind: "category"` (needs `prompt`) or `kind: "subagent_type"`, name matching `^[a-z0-9-]+$`.
- **Member limits.** Read-only curated agents (`explore`, `librarian`, `plan-consultant`, `plan-reviewer`) and the three ulw reviewer agents are rejected as members; delegate to those with the `task` tool instead ([member-validator.ts:45-59](https://github.com/code-yeongyu/oh-my-openagent/blob/29c7f0c777a10fb4439d728cd1a490e5cb139350/packages/senpi-task/src/team/member-validator.ts#L45-L59)).
- **Lead only.** Only the top-level session can lead; a child cannot call `team_create` (senpi-task/AGENTS.md line 43 and `hyperplan/SKILL.md` prerequisite 2). A team skill must run in the main session, not inside a `task` child.
- **Shared task list.** Provided by `task_create`, `task_get`, `task_list`, `task_update`. Messages travel through durable mailboxes with injected delivery (senpi-task/AGENTS.md, section "TEAM DELIVERY MODEL").

## Alongside slim council

- Slim describes itself as "A lightweight agent orchestration plugin for OpenCode" (`AGENTS.md` line 7 at commit `aa1bc37`, package version 3.0.1), and its `package.json` keywords include `opencode-plugin`.
- Council is a slim agent. `@council` dispatches `councillor-<name>` subagents in parallel through OpenCode's own delegation tool (`task()` on v1, `subagent()` on v2), per [docs/council.md](https://github.com/alvinunreal/oh-my-opencode-slim/blob/aa1bc37f654fddca7080cbc0f56be78415e5f917/docs/council.md) "How it works". It exists only when `config.council` exists (same file, "Troubleshooting").
- Slim has no team or shared-task-list feature. A search of slim `src`, `docs` and `README.md` for `team_create`, `shared task list` and `task_create` returns nothing.
- The two are separate hosts. OmO native runs on senpi (`omo --version` reports the senpi engine). Senpi loads its own extensions and packages, and the docs in the runtime folder describe no OpenCode plugin loader. So slim's `@council` is not reachable from an OmO native session, and OmO's `team_*` tools are not reachable from OpenCode running slim.
- Nothing conflicts on disk. OmO native state is `~/.omo/`; slim is configured in `~/.config/opencode/`. Using both means running two programs, one per task.
- OmO's closest native equivalent of council is the `hyperplan` skill: five adversarial category members debating through `team_create` and `task_send`. It is a comparable idea, not the slim council.

## Answers

1. Trigger team mode in OmO native through our own skill: **yes.** Write a SKILL.md in a directory senpi already scans (for example `~/.claude/skills/<name>/`). It instructs the lead to call `team_create` with an `inline_spec`, coordinate with `task_send` and the `task_*` list tools, and finish with `team_delete`. No config key, flag, or shim is needed. Use `hyperplan/SKILL.md` as the model.
2. Run that alongside slim council in one session: **no native route.** They belong to different hosts. Use each in its own program.

## Unverified

- **No live run.** I did not start a team in the installed `omo`. "Tools present and callable in this install" rests on the 5.1.4 bundle text and the source at `29c7f0c`, not on an observed `team_create` call. I did not diff the source commit against the 5.1.4 release.
- **Inline spec rules.** The named-spec schema requires `leadAgentId` when a team has several members. I did not check whether the inline `team_create` path applies or fills in that rule.
- **Skill discovery.** The `skills` setting is present and the docs say it works, but I did not confirm that a new skill in `~/.claude/skills` appears in `/skill:` on this machine.
- **Slim plus OmO's OpenCode edition.** OmO also ships an OpenCode plugin edition with `team_mode.enabled` (public `docs/guide/team-mode.md`). Whether that plugin and slim can load together in one OpenCode was not tested and is not covered above.
- **No OpenCode plugin support in senpi** is inferred from silence in the runtime `docs/*.md`, not from a stated exclusion.
- **Model routing.** Which models team members would use with the opencode-go and qwen-token-plan setup was not examined.

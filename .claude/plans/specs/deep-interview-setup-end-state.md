# Deep Interview Spec: Personal Setup End-State

## Metadata
- Interview ID: di-setup-end-state
- Rounds: 7 frontier rounds (plus Round 0 topology)
- Type: brownfield
- Generated: 2026-09-29
- Threshold: 0.03 (source: captain override mid-session; default 0.2)
- Status: PASSED — destination (W1) signed by captain 2026-09-29
- Map home: GitHub issues, Bearmancer/system-config, label `navigator:map`
- documentLanguage: en
- Guiding principle: minimum complexity (minimal-code-discipline), no performance loss, check how others solve it before proposing.

## Destination (signed W1)

system-config is the single documented, daily-backed-up home for everything authored on this machine: two distinct instruction files (`~/.claude/CLAUDE.md`, `~/.config/opencode/AGENTS.md`), authored skills in `~/.claude/skills` (OmO reads it via one setting), current Claude / OpenCode v2 / OmO settings, and Scheduled Tasks as code (Daily sync with an OpenCode service check, Topgrade, OpenCode service at logon, reachable over Tailscale only). Vendored skills, plugins and secrets are reinstall-only; git history is one commit a day after a one-time squash. `~/Dev` is flat real repos with no links. deep-research runs on bare OpenCode, OpenCode+slim (the current primary, but removable) and OmO. It fans out to a native researcher subagent, walks every account of every server in the 9-step block chain before reporting a block, rotates keys via `{file:}` with hot reload, keeps sources in private Bearmancer/deep-research and publishes HTML to bearmancer.github.io. Done when the restore drill, drift check, block-chain drill and remote/tasks check all pass.

## Topology

| Component | Items | Status |
|---|---|---|
| A. Estate map | a skill structure, f Claude vs OpenCode, i repo storage, j no links, k schema | active, covered |
| B. Backup + schedule | b skill backup, c daily sync, d task creation, e task backup | active, covered |
| C. deep-research | g no ulw-research, h github.io output, l harness-agnostic | active, covered |

## Decisions

### A. Estate
- No separate manifest. Fix the README backup table (remove stale rows: `opencode/AGENTS.md`, `opencode.jsonc`, `~/.omo/omo.jsonc`, `~/.omo/scripts`, `~/.omo/plans`) and add a "Reinstall, not backup" section: plugins, `.skill-lock.json`, slim-bundled skills, secrets, repos, Scheduled Tasks, `service.json`.
- Instruction files: two distinct, self-contained files. `~/.claude/CLAUDE.md` keeps the OMC block and all rules. New `~/.config/opencode/AGENTS.md` gets the common rules without OMC/Claude-only parts. One-time sync of common text now; afterwards each evolves independently. No import. (Creating global AGENTS.md stops OpenCode's fallback to `~/.claude/CLAUDE.md` — verified in `instruction.ts`.)
- Skills: authored skills live only in `~/.claude/skills`. OmO reads them via `"skills": ["~/.claude/skills"]` in `~/.omo/agent/settings.json`. Vendored skills (`~/.agents/skills` caveman x20, `~/.config/opencode/skills` slim x8 — byte-identical to slim 2.2.25 bundle) are not backed up; lock file + plugin list only.
- Repos: flat `~/Dev/<name>`, real dirs, each cloned from its own remote. No symlinks/junctions. Delete all `.codegraph` dirs now (incl. dangling junction `media-research-tools/bowie-discography/.codegraph` -> missing `~/.omo/codegraph`). Keep the mandatory CodeGraph rule (re-init in-repo on next visit).
- Purge stale/dead: ulw-research leftovers (`~/.omo/plans/agents-config-restructure.md`, `~/.omo/drafts/agents-config-restructure.md`), stale repo copies.

### B. Backup + schedule
- Keep robocopy local-to-repo mirror (`backup-agents.ps1`). Backup only current config: Claude (`CLAUDE.md`, `settings.json`, `keybindings.json`, `skills/` minus `synced`, agents, commands), OpenCode v2 (`opencode.json`, `tui.json`, `AGENTS.md`, agents, commands; exclude `secrets/`), OmO (`~/.omo/agent/settings.json` with credential guard; never `auth.json`), PowerShell profile.
- Daily only. Remove the PostToolUse backup hook (`hooks/claude-backup-trigger.ps1` + settings entry). No immediate commits.
- One-time history squash: merge consecutive auto "Backup agent config" commits until a group exceeds ~50 changed lines; keep hand-written commits; local tag `pre-squash` first; push once with `--force-with-lease` (captain approved).
- Scheduled Tasks exist only as code in `SystemConfig.psm1`, registered by `install.ps1` (run elevated by hand). Repo is the backup; no XML export.
- Daily sync keeps: `toolbox sync lastfm`, `toolbox sync youtube`, agent config backup, foobar2000 rclone mirror, fail-visible `Read-Host`; add OpenCode service status check + restart. Topgrade task unchanged.
- New task "OpenCode service": at logon, `opencode service start` (not 24/7). Tailscale-only access: `opencode service set hostname 127.0.0.1` + `tailscale serve --bg 49374`. `service.json` never backed up.

### C. deep-research
- Skill source stays in `~/.claude/skills/deep-research`, backed up by system-config. No ulw-research dependency (already zero refs in skill).
- Course sources: `~/Dev/deep-research` becomes private repo Bearmancer/deep-research; publish step commits+pushes sources, then mirrors HTML+assets to public bearmancer.github.io (published HTML cannot reconstruct transcripts/NOTES/RESOURCES/learning-records).
- Hosts: bare OpenCode v2, OpenCode + oh-my-opencode-slim (current primary, removable layer), OmO 5.0.1 (omo-native). No host-specific tool names in SKILL.md.
- Fan-out: capability probe — if a subagent launcher exists, one worker per chapter with self-contained prompt + output schema; else inline. Define native `researcher` subagent in `opencode.json` `agents` (built-in `general`/`explore` stay disabled).
- MCP keys: pools stay in `~/.secrets/.env`. Active key per service at `~/.config/opencode/secrets/<svc>`, referenced via `{file:}` (watched dir, hot reload, only changed MCP reconnects). `switch_api_key.py --next` writes the file and creates every referenced file (missing file breaks config load). Backup excludes `secrets/`. Sidesteps bug #50882.
- OmO MCPs: skill-bundled `mcp.json` sidecar (`${VAR}`; OmO rotation needs restart).
- Block chain (walk every account of a server before moving on; report "blocked" only after full log `URL | status | method`):
  1. Tavily extract (basic, then advanced)
  2. Firecrawl `proxy:"auto"`, `maxAge:0`
  3. Exa `web_fetch_exa` (cached copy; `SOURCE_NOT_AVAILABLE` = next)
  4. ScrapeGraph stealth
  5. Apify `web-fetch` / site Actor (`?tools=` narrowed)
  6. AgentQL (`disabled: true` by default)
  7. Firefox DevTools / `@playwright/cli`
  8. Bright Data Web Unlocker (local `npx @brightdata/mcp`; retry on `x-brd-error: reject_block`)
  9. Browserbase (`disabled: true` by default; paid tier for CAPTCHA)
  - Dappier not wired (data marketplace, cannot unblock). v2 uses `disabled: true`, not `enabled: false`.

## Acceptance Criteria
- [ ] Restore drill: following README restore + reinstall list on a fresh folder brings back every authored file; OpenCode, Claude and OmO start with the same skills and rules.
- [ ] Drift check: every README backup row exists locally and in repo; no stale files; one commit/day; no links under `~/Dev`; no `.codegraph` junctions.
- [ ] Block-chain drill: deep-research on a known bot-protected URL on bare OpenCode, slim and OmO; log shows chain walked in order, one key rotation with no restart, correct verdict.
- [ ] Remote + tasks check: after reboot + logon, OpenCode service up, reachable only via tailnet HTTPS, not LAN IP; all three Scheduled Tasks defined in code and registered.

## Open unknowns (research tickets)
- Live test: `{file:}` key change under `~/.config/opencode/secrets/` hot-reloads one MCP (source says yes; `{file:}` absent from v2 MCP docs).
- `researcher` subagent reaches MCPs under bare v2 and slim (Code Mode `execute`; slim maps `bash: deny` to `execute` deny).
- Browserbase header auth (else key stays in URL); Firecrawl remote Bearer; ScrapeGraph MCP stealth arg name; out-of-credit codes for Bright Data, AgentQL, Apify, ScrapeGraph.

## Key sources
- OpenCode rules/skills/config/MCP docs: https://opencode.ai/docs/rules/, https://opencode.ai/docs/skills/, https://opencode.ai/v2/docs/mcp-servers/, https://opencode.ai/v2/docs/cli/commands/
- OpenCode source (v2 @ca084b2): `packages/core/src/config/variable.ts`, `config.ts`, `config/watch.ts`, `mcp/index.ts`, `session/instruction.ts`
- Claude Code memory docs: https://code.claude.com/docs/en/memory
- Issues: anomalyco/opencode #51341, #50882, #51637
- Chain ordering: https://danielmiessler.com/blog/progressive-web-scraping-four-tier-system
- Dotfile managers: https://www.chezmoi.io/comparison-table/

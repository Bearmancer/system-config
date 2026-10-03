# Inventory 2026-10-03

State of all repos in `C:\Users\Lance\Dev` and live agent config after the 2026-10-03 purge, history squash, Markdown audit and consolidation assessment.

## Repos

| Repo | Branch | Synced with GitHub | Commits |
| --- | --- | --- | --- |
| Toolbox | master | yes | 594 |
| bearmancer.github.io | main | yes | 22 |
| media-research-tools | master | yes | 14 |
| sdet-roadmap | master | yes | 9 |
| system-config | master | yes | 49 |

Old heads before the squash: local tags `pre-squash-20261003`.

## Purged

Recorded in `backlog-2026-10-01.md` ("Purged 2026-10-02", "Purged 2026-10-03").

## Consolidation candidates

1. Site assets: `shell.js` has 7 identical copies (hub, 5 courses, skill source); `publish_teach.py:92,463` and `stamp_lesson.py:130` copy it per course. Four courses (wifi, afghanistan, russia, saudi) carry an older Tufte-theme `lesson.css`; the hub and skill carry the current theme. Target: one `assets/` at the site root. Effort M. Needs a theme decision.
2. Instruction rules: about 100 lines of `~/.claude/CLAUDE.md` overrides are hand-synced into `~/.config/opencode/AGENTS.md`. Target: one source file and a generate step in the backup script. Effort M. Needs an ADR-0002 amendment.
3. sdet-roadmap: `assessment/engine/agent-assessment-content.md` (2637 lines) duplicates the 100 bank questions with no generator. `validate_assessment.py:922` reads a nonexistent `agents/` dir, so the sync check never runs. Target: fix the path, generate the file from the bank. Effort M.
4. deep-research and ledgerlab skills claim the same triggers while ledgerlab is a draft. Key rotation (`keystate.py` vs `switch_api_key.py`, `_post_common.py`) and the fetch ladder (`registry.yaml` vs `fleet.md`, `keys-errors.md`) overlap. Target: registry as single source at cutover (handoff §11). Effort L.
5. Toolbox CLAUDE.md files repeat the RequiredEnv rule (6 files) and the Serilog rule (5 files); root rules 10, 11, 15 repeat global rules. Target: one home in Core, pointers elsewhere. Effort S.
6. bowie-discography: `docs/bowie-yearly-scraper-draft.md` is superseded by `bowie-yearly-scraper.md`. Effort S.
7. `caveman-explore` and `caveman-learn` in `~/.claude/skills` are symlinks to `~/.agents/skills` copies byte-identical to the caveman plugin 3.0.0; plugin 2.7.0 is also still cached. Effort S.
8. system-config research: `secrets-subdir-reload.md` extends `file-key-hot-reload.md`. Effort S.

Rejected: stt runners already share `common.py`; `fleet.md` is already an index over `scrapers/*`; the MCP research docs answer different questions; Toolbox per-folder CLAUDE.md files stay scoped by area.

## Unfinished work

- bowie-discography `docs/bowie-yearly-scraper.md:138-453`: 37 todos and F1-F4 unchecked; no `config.py`, `identity.py` or `sites/`; `release_sweep.py:27-32` expected values are stubs. Still wanted.
- ledgerlab: handlers, shell and layouts, fixture runs, surface probe and URL audit port not built (`handoff.md:212-219`, README). Still wanted; OmO removal waits on activation.
- sdet-roadmap `validate_assessment.py:922`: sync check never runs. Still wanted.
- `backlog-2026-10-01.md`: treatise-merge sign-off pending; Afghanistan NOTES quotes pending; upstream issues wait on maintainers.
- `ticket-reconcile-2026-09-30.md:67`: `magic-context.jsonc.MOVED_READPLEASE` decision; plan executed.
- bearmancer.github.io `.slim/deepwork/kim-verify-and-topics.md`: ignored scratch.

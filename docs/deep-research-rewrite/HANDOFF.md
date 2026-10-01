# Handoff: deep-research rewrite (working name `ledgerlab`)

Status: design agreed through grill-with-docs; nothing built, nothing committed to any repo.

## Read first (do not duplicate here)
- `docs/deep-research-rewrite/GLOSSARY.md`: all terms (claim, ledger, status, round, surface, wave, gate, mode, layout, fixture, ...).
- `docs/deep-research-rewrite/adr/0001-0024` (0005 corrected: one layout per lesson, no judge): decisions and rejected alternatives.
- `layouts.html` (published atlas): https://claude.ai/artifact/5VdRcdc4UN5gmkziqDbmub
- Existing system: `system-config/claude/skills/deep-research/`, `system-config/.claude/docs/research/mcp-tool-catalog.md`, `mcp-cli-post-matrix.md`, `fleet.md`.

## Target
- Skill source in `system-config/claude/skills/<name>/` only after it exists live (backup `/MIR` deletes repo-only skills). Draft staged in `docs/deep-research-rewrite/ledgerlab/`. Installed under `.claude`. Python + YAML ledger. Output lands in `bearmancer.github.io`.
- Old skill and old courses stay live until a fixture regenerates its domain.

## Migration, one domain at a time
Order: rules (Ark Nova) -> verify (Russia morale) -> learn (Saudi). Rules first: smallest source set, already a pilot.

For each domain, before building, ask the user these intake questions (deferred to execution by design):
- **Rules / Ark Nova:** which expansions are in scope; local rulebook PDF paths; include solo and BGG designer posts? What counts as the publisher account?
- **Verify / Russia morale:** which input is the test (transcript, claim list, article)? Which claims are known-wrong, to seed? Output tone for the untrue/interpretive page.
- **Learn / Saudi military:** scope boundary the user expects; which existing chapters carry over; known contested topics; preferred language level.
- All: freshness expectation (refresh is on request only); any domain-specific surfaces to add (e.g. BGG, Places video packs).

## New test per domain
1. Regenerate unattended from the same input; no intake questions at run time.
2. Every claim has one of 4 statuses; appendix lists sources covered and failed-to-grab.
3. Seed one false claim; the run must catch it, mark `untrue`, and block the push.
4. Diff against the old course: every old claim is either retained, reclassified, or listed as dropped with reason.

## Open or unsettled
- Voice: user rejected the old agent's "phrasing style itself" but did not say what about it. At build time, ask for 2-3 before/after samples, then write the rule (ADR 0014).
- Q39: user asked for unlimited reproduction of source text on the public page; not adopted. Paraphrase + cite stands (ADR 0010).
- opencode.jsonc lists qwen3.7-plus; user states qwen-3.8-flash. User updates config.
- Vision support of muse-1.3, mimo, qwen unknown; two-family visual read may not be possible.
- Brave, Dappier, Crawl4AI not wired yet.
- Verifier and extractor model families: pick concrete models at build time.
- Built as a draft in `ledgerlab/` (see its README): registry, ledger schema and checker, attempt log, mode inference, key memory and lock, driver skeleton, role prompts. 67 tests pass.
- Not started: agent handlers, shell and layout components, `tools/list` probe, URL audit port, skill-creator eval set, fixture runs.
- Design considered settled by the user on 2026-10-01. Leaves (rules, verify, site) decided in ADRs 0022-0024; no OmO (ADR 0021).

## Suggested skills for the next agent
- `grilling` + `domain-modeling` to finish open items and keep GLOSSARY/ADRs current.
- `/skill-creator` to build the skill; the 3 fixtures are the eval prompts.
- `tdd` for the Python scripts (ledger build, surface inventory, URL audit, rotation check).
- `research` for any source-gathering legwork.
- `handoff` again at the end of the build.

## Constraints from the repo
- system-config CLAUDE.md: config folders are a one-way copy; never git clean/reset them; never read Toolbox `.env` or `state/auth`.
- No shadow-library surfaces (ADR 0010).

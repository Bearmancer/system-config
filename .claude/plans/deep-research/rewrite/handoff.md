# Handoff: deep-research rewrite (`ledgerlab`)

Written 2026-10-01 from a cloud session; split and corrected 2026-10-02. Audience: the next agent (or the user) working **on the user's own machine**, where OpenCode, the MCP fleet, API keys and the models exist. Everything here is work the cloud session could not do or could not verify, plus the migration order and per-domain tests.

Related, do not duplicate here: `README.md` (index), `GLOSSARY.md`, `adr/0001-0024` (rewrite-design ADRs, numbered separately from `docs/adr/`), `layouts.html` (layout atlas; published copy https://claude.ai/artifact/5VdRcdc4UN5gmkziqDbmub), and the draft code in Bearmancer/deep-research `ledgerlab/` (its README lists what is built).

Existing system to read: `claude/skills/deep-research/`, `.claude/docs/research/mcp-tool-catalog.md`, `mcp-cli-post-matrix.md`, `fleet.md`.

Decisions recorded 2026-10-02 (user, final):
- Full rewrite supersedes the learning-first "tone only" plan (`.claude/plans/deep-research-learning-first/plan.md`).
- Visual-read fallback: while only one vision model family is available, `true` needs one visual read plus text corroboration (ADR 0012, enforced in `ledger.py`).
- OmO removal waits until ledgerlab is live (ADR 0021 stands; section 4.3).
- Independence (ADR 0019): script floor of two distinct publishers; the verifier's rationale sits on the evidence entry.
- AgentQL and Browserbase stay `wired: true`; live `omo/mcp.json` and `opencode/opencode.jsonc` configure both.
- The skill is not activated: nothing is copied to `~/.claude/skills`.

---

## 0. Status snapshot

| Area | State |
|---|---|
| Design | Settled by the user. 24 ADRs. No open grilling. |
| Draft code | Built and tested: registry, ledger schemas and checker (including the attempt-log audit and the visual-read family rule), attempt log, mode inference, key memory with OS-level rotation lock, generation counter and unknown-failure counter, driver skeleton with `render` phase, role prompts, layout picker. 86 pytest tests pass: `uv run --with pytest --with pyyaml --with jsonschema pytest ledgerlab/tests --basetemp <empty temp dir>` from the deep-research repo root. |
| Agent handlers | **Not built.** The driver fails honestly at the first missing handler (`ingest`). |
| Site shell and 12 layout components | **Not built.** |
| Fixture runs (rules, verify, learn) | **Not run.** Need local host, keys, models. |
| Voice rule | **Pending.** Needs user samples. |
| Activation | **Not done** (user decision). `ledgerlab/` is staged in the deep-research repo. |
| Cutover | **Not started.** Old `deep-research` skill and old repo stay live until all three fixtures pass. |

## 1. Hard constraints (obey these first)

From `system-config/CLAUDE.md` and the session:
- Never run `git clean`, `git reset --hard`, or check out old commits over `claude/`, `opencode/`, `omo/`, `agents/`. This repo is a one-way copy of live config. Restore is a manual reverse robocopy.
- Never read or copy `C:\Users\Lance\Dev\Toolbox\.env` or `Toolbox\state\auth`.
- Scripts never call `Register-ScheduledTask` outside `install.ps1`. `install.ps1` is run by the user, elevated, by hand.
- Only `switch_api_key.py` reads `~/.secrets/.env`. Agents never read it. Never print, log or commit a key. Ledger and key state hold **fingerprints only**.
- BGG: public pages and XML API only. Never log in, never handle cookies. Files behind login: the user supplies local PDFs.
- No shadow libraries (Anna's Archive, LibGen, Z-Library) as surfaces, ever (ADR 0010). No paywall-circumvention services.
- Published pages paraphrase and cite. Quotes are 25 words or fewer, attributed. Raw fetched text stays in gitignored `work/`.
- No questions to the user at run start. The one allowed stop: a whole key pool exhausted, via `NEEDS_YOU.md`.
- Do not assume oh-my-opencode (OmO) or the slim plugin (ADR 0021). Plain OpenCode only.
- The daily backup (`SystemConfig.psm1:60`) mirrors `~/.claude/skills` into repo `claude/skills/` with `/MIR`. A skill that exists only in the repo is deleted at the next backup. Install live first; never add `claude/skills/ledgerlab/` by hand.

## 2. Local prerequisites

1. OpenCode v2.x running; `opencode --version`. Background service on 127.0.0.1 (port was 49374 on 2026-09-29).
2. Python 3.11+, `uv`, `git`, `pdftotext`, `tesseract` (OCR), `yt-dlp`, Playwright (or the Firefox DevTools MCP). Check each: `<tool> --version`.
3. CLIs already installed per fleet notes: `tvly`, `firecrawl`, `apify`, `brightdata`, `just-scrape`, `browse`.
4. Key pools in `~/.secrets/.env` (8-9 keys per pooled service). Active keys materialised under `~/.config/opencode/secrets/<pool>`. If any file is missing the OpenCode config fails to load: `uv run <skill>/scripts/switch_api_key.py --service all --materialize`.
5. A clone of `Bearmancer/bearmancer.github.io` (the site, public, Pages on `main`). Old source repo: `Bearmancer/deep-research` (to be archived last).
6. `pip install pytest pyyaml jsonschema` in the interpreter the driver will use.

## 3. Activation steps (do in order)

1. Pull the deep-research branch with `ledgerlab/`. Run the draft tests (command in section 0; expect 86 pass).
2. Only when the user says so: copy `ledgerlab/` to `~/.claude/skills/ledgerlab` (live). The next backup mirrors it into `claude/skills/ledgerlab`. Scripts run as `uv run --directory ~/.claude/skills/ledgerlab --with pyyaml --with jsonschema python -m scripts.<module>`.
3. Confirm OpenCode sees the skill (new session, ask it to list skills). Skill frontmatter is `name: ledgerlab`.
4. Do **not** delete or edit `deep-research` yet.
5. `ledgerlab/` in the deep-research repo is staging. Remove it there in the cutover PR, so archiving that repo (section 8) strands nothing.

## 4. Config changes on the local machine

Edit live config, then let the backup mirror it. Do not hand-edit repo copies of `opencode/` or `omo/` expecting them to apply.

1. **Model ids.** `opencode.jsonc` allows only: `muse-spark-1.3-contributor`, `deepseek-v4.1-flash`, `qwen3.7-plus`, `mimo-v2.6-flash` (providers.opencode-go), and lists `qwen3.8-flash` as `disabled: true`. ADR 0013 names qwen-3.8-flash for the verifier. `opencode models` printed nothing on the authoring host (v2.0.21, 2026-10-02, also with `--standalone`), so no id could be verified; `registry/roles.yaml` marks every role `id_status: unverified`. On a host where `opencode models` lists models: confirm all four ids, enable the qwen 3.8 flash id in the config (or change the verifier), then set `id_status: verified`.
2. **Vision/audio capability.** Test each model with one image and one short audio/video clip. Record results in `roles.yaml` notes. Until a second vision family is confirmed, visual-read claims use the ADR 0012 fallback (one visual read plus text corroboration). `ledger.py` maps `read_by` to a family through `roles.yaml`; add any new reader model there.
3. **Remove OmO** (user asked to ditch it; ADR 0021). Deferred until ledgerlab is live: the old skill still depends on the sidecar. Checklist, ask before deleting:
   - `oh-my-opencode-slim` in `opencode.jsonc` plugin list; `opencode/oh-my-opencode-slim.jsonc`; `omo/` folder (`mcp.json`, `settings.json`); README and CLAUDE.md references; backup whitelist entries for `omo/`; `dprint.json` include of `omo/**`.
   - Context7 and gh_grep come from the slim plugin. Re-add natively to `opencode.jsonc` only if wanted.
   - Skill sidecar `mcp.json` assumptions in `deep-research/references/fleet.md` die with OmO.
   - Verify OpenCode still starts: `opencode mcp list` shows servers connected; `opencode api mcp.list`.
4. **Wire the unwired MCPs** (ADR 0016 wants maximal coverage): Brave and Dappier already have pool entries in `switch_api_key.py` (`SERVICE_MAP`) but are not in `MATERIALIZE_SERVICES`. Add Brave, Dappier (and Crawl4AI, keyless) to `opencode.jsonc` with `{file:}` key substitution (ADR 0003), add to `MATERIALIZE_SERVICES`, run `--materialize`, then flip `wired: true` in `registry/registry.yaml` and regenerate `references/routing.md` (`python -m scripts.gen_routing_table` from `ledgerlab/`; the drift test fails otherwise). Verify the real MCP tool names for each; the registry guesses (`brave_web_search`, `dappier`, `crawl4ai`).
5. **`opencode run` flags.** Verified against `opencode run --help` (v2.0.21): `--model provider/model#variant` and `--format default|json` exist, so `OpencodeRunner.command` is valid. Still open: how to pass a per-step system prompt (`--agent <name>` selects an agent defined in config), how to make the extractor tool-less (ADR 0009), and whether unattended steps need `--auto` (auto-approves permissions not explicitly denied).
6. **Update the system-config docs index** (CLAUDE.md "Index", README tables) after cutover, not before.

## 5. Probes to run and record

Write results to `ledgerlab/registry/` in the deep-research repo or a research note under `.claude/docs/research/` (existing convention: `mcp-tool-catalog.md`).

1. **Surface inventory (`tools/list`).** OpenCode has no native tool-listing route. Send MCP `tools/list` directly to each server (method documented in `.claude/docs/research/mcp-tool-catalog.md`). Keyed servers (agentql, apify, brightdata, exa, tavily) refuse without a key; run with the active key from the secrets file **inside the probe script only**, never echo it. Output: JSON per server of tool names. Compare against `registry.yaml` `routes.mcp` lists; fix mismatches (known: ScrapeGraph MCP 1.0.1 lacks `crawl_start`/monitor tools; Tavily extract spelling `tavily_extract` vs `tavily-extract`).
2. **Error-code verification.** Registry `unverified` lists (Tavily bad_key/out_of_credit/rate_limit; AgentQL out_of_credit/blocked/rate_limit; Browserbase all; Apify blocked; ScrapeGraph blocked; Brightdata rate_limit). As real failures occur, record codes and move the class out of `unverified`. Until then unknown errors follow ADR 0017 (retry once, log `unknown`, rotate only after 2 different URLs fail alike).
3. **Vendor reset windows.** Registry has `reset: unknown` everywhere (=> probe after 24 h). Look up each vendor's quota reset (monthly vs rolling) and set `monthly` where true.
4. **Key fingerprints without reading `.env`.** `keystate.py` needs the fingerprints of every pooled key. Add a `--fingerprints` flag to `switch_api_key.py` (it already has `get_fingerprint`) that prints `pool<TAB>fingerprint<TAB>account-label` only. The driver calls that; nothing else touches `.env`.
5. **Rotation reconnect latency.** After `switch_api_key.py --next`, measure how long OpenCode's watcher takes to reconnect the changed server (ADR 0003 verified it works, not how long). Use it to set the retry delay after a rotation lock release.

## 6. Build tasks (ordered, with acceptance)

Existing tested modules to build on (package `ledgerlab/scripts/`): `registry.py`, `ledger.py`, `ledger_check.py`, `log_attempt.py`, `infer_mode.py`, `keystate.py`, `driver.py` (phases, suspend/resume, `run_wave`, `OpencodeRunner`), `cli.py`. Add tests for everything new; follow `tdd` skill. Keep the seeded-bad-claim test green.

### B1. Surface inventory script
`scripts/inventory.py`: probes each registry server, writes `work/inventory.json`, reports servers that are wired but unreachable or missing tools. Acceptance: unreachable server flagged; mismatched tool names reported; no key in output.

### B2. Key rotation integration
Wire `keystate` around real rotation. An agent reads `KeyState.generation(pool)` before using a key. On a credit-out error (via `registry.classify_error`) it calls `keystate.rotate_once(state_path, pool, seen_generation, rotate)`; `rotate` runs `switch_api_key.py --service <pool> --next` and marks the old fingerprint exhausted. `rotate_once` re-reads the generation after taking the lock, so one exhaustion event causes one rotation; agents that get `False` wait for the reconnect and retry once. For an error class `unknown`, call `KeyState.note_unknown_failure(pool, signature, url)`; it returns True once the same failure has hit 2 distinct URLs, which means rotate. When `keystate.pool_exhausted` is true raise `driver.PoolExhausted(pool)`. Acceptance: simulated 9-key pool exhausts, driver suspends with `NEEDS_YOU.md`; resume after reset window probes once.

### B3. Phase handlers (the core)
Each handler is a function `(Driver) -> PhaseResult`, re-entrant, reads and writes only the topic dir (`_ledger/<topic>/`), `work/` and `run.yaml`. Agent steps go through `OpencodeRunner` with role prompts from `references/roles.md`.

| Phase | Does | Output | Acceptance |
|---|---|---|---|
| infer_mode | exists | mode + reason | done |
| ingest | fetch input via the fetch ladder (registry order); yt-dlp transcript or deepseek media read for video/audio; pdftotext then OCR + vision for image-only PDFs | raw text in `work/`; sources.yaml rows (status read/failed with reason) | every fetch attempt logged; failed sources listed with reason; no raw text outside `work/` |
| discover (learn, rules) | waves (default 8, `run_wave`) of discovery agents; extractor turns source text into claims; loop until saturation (2 waves, no new concept cluster); misconception searches add `origin: misconception` claims | claims.yaml rows `open`; concept clusters | stops by saturation; claims atomic; hashes valid |
| extract (verify mode) | extractor splits the user's input into factual claims, attributes by locator, counts skipped opinions/predictions | claims.yaml `open`, `origin: extracted-from-input` | skipped count in run record |
| verify | per claim Ralph loop, max 5 rounds; round N uses the paradigm from `registry.round_order[N-1]`, query variant rotates (supporting, opposing, primary, other-language); every attempt through `log_attempt`; evidence = source + locator + <=25-word quote + stance; independence rationale by the verifier agent | claim ends true/untrue/interpretive/not-found | `ledger_check` clean (`--publish`); rotation audit clean; failed-to-grab sources enumerated per wave |
| write (learn, rules) | course map by concept clusters ordered by prerequisite; author writes only from verified claims; sentences carry claim ids; debate blocks, errata box; one layout picked by `references/layouts.md` | lesson source with claim anchors | every sentence maps to claims; layout recorded in header |
| conformance | extractor re-splits final prose; `ledger.prose_claims_missing` and `ledger.check_sentences` | pass/fail list | any claim absent from ledger fails the gate |
| layout | pick one layout from claim shape (`references/layouts.md`); record it in the lesson header | layout choice | one layout per lesson, no judge (ADR 0005) |
| render | build the page once into the shared shell. Verify mode renders claim cards (ADR 0023) | HTML | no overflow at phone width; both themes |
| gates | verifier (other family, fresh context) re-checks **every claim, all statuses**; `ledger_check --publish` (schema, status invariants, rotation order and repeats, rounds and paradigms against `attempts.jsonl`); URL audit (port `check_urls.py`); render/schema check; appendix present (sources read + failed) | `GateFailed` with problems, or pass | seeded bad claim blocks |
| publish | work on `draft/<topic>-<run>`; fast-forward main only on pass; regenerate home index; verify pages `noindex` and unlisted; pull --rebase under a publish lock | pushed commit | main never contains a failed run |
| live_check | after Pages build, fetch live bytes, compare; mismatch auto-reverts the merge | pass or revert | reuse the idea in `verify_live.py` |

Resume behaviour (ADR 0006/0020): re-run keeps `true`/`untrue`, re-opens `not-found`, adds only new claims; never auto-stale; refresh on request.

### B4. Shared site shell and layout components
- Start from existing `assets/lesson.css`, `shell.js`, `course-index.js` (topic and chapter selects, font and size picker) on `bearmancer.github.io`; add theme toggle.
- Implement the 12 layouts as components (concept, glossary, Q&A, table-first, decision tree, steps, timeline, claim cards, layered wrapper, cause-effect, cheat sheet, diagram). Reference render: `layouts.html`. Direct explanation only; no narrative.
- Home index generated from topic dirs at publish time: Courses (learn) and Rules. Verify pages are not listed; they carry `<meta name="robots" content="noindex">`.
- Every page ends with the appendix: sources read, sources failed to grab (separate lists).
- Acceptance: phone width has no horizontal page scroll; both themes legible; keyboard focus visible.

### B5. Port or retire old gates
Review each old script; decide keep, port, or drop (see section 7). `check_lesson.py` encodes old lesson rules (Voice, no ledger) that conflict with the new design; do not reuse unchanged.

### B6. Site repo layout (`bearmancer.github.io`)
- Built pages at published paths (URLs stay stable). Per topic `_ledger/<topic>/` with `claims.yaml`, `sources.yaml`, `attempts.jsonl`, `runs/<run_id>/` (run.yaml, RUN_RECORD.yaml, REPORT.md or NEEDS_YOU.md). `.nojekyll` already exists so underscore dirs are served; the ledger is public by design (ADR 0024).
- Add `work/` to `.gitignore`. Existing `.gitignore` has `.omc/` and slim-worktree lines; the slim lines are OmO leftovers, remove when OmO is removed.
- Gotcha from `learning-records/0001`: `core.autocrlf=true` caused a 1-byte CR delta between local and live `course-index.js`. Compare live bytes after stripping CR, or set `.gitattributes`.

### B7. Evals with `/skill-creator`
The three fixtures are the eval prompts. Create `evals/evals.json` (schema in skill-creator `references/schemas.md`). Assertions: unattended run; every claim has a status; appendix lists covered and failed; seeded false claim blocked. Baseline = no skill. `/skill-creator` is user-invoked.

## 7. Old skill reuse inventory (`system-config/claude/skills/deep-research/`)

| Item | Verdict | Note |
|---|---|---|
| `scripts/switch_api_key.py` | keep, extend | add `--fingerprints`; sole `.env` reader |
| `scripts/_post_common.py` + POST scripts (`exa_answer`, `exa_agent_run`, `exa_batches`, `firecrawl_batch_scrape`, `brightdata_unlocker`, `browserbase_agent_run`, `scrapegraph_crawl`) | keep | already registered as `route: post` in the registry; contract: JSON out, error JSON on stderr, exit 1; refuse redirects |
| `scripts/check_urls.py` | port | URL audit gate; flags OK/BROKEN/JS?/BLOCKED; exit 1 if any not OK. BGG returns 403 to bots: verify by a second fetcher |
| `scripts/verify_live.py` | adapt | live-bytes check; currently tied to lesson gate |
| `scripts/fetch_video.py`, `slice_chapter.py`, `extract_chapters.py` | keep for ingest | transcript and chapter handling; yt-dlp 429 seen on Russia course (`subs.en.vtt` never fetched) |
| `scripts/publish_teach.py`, `stamp_lesson.py` | review | tied to old lesson format; mine for publish and Pages-build polling logic |
| `scripts/check_lesson.py`, `lesson_rules.py`, `check_map_geometry.py`, `layout_diagram.py` | drop or rewrite | old lesson rules and map geometry; reuse diagram idea only if still wanted |
| `assets/lesson.css`, `shell.js`, `lesson.stencil.html` | seed for shell | restyle for the 12 layouts |
| `references/fleet.md` | superseded | content moved into `registry.yaml`; delete the hand table after cutover |
| `references/course/*`, `modes/course.md` | read for lessons learned | do not port Voice rule; ADR 0014 replaces it |
| `evals/` | replace | new fixtures |
| SKILL.md Voice, Tier ladder, Passes, Verdict mode | replaced | by ADRs 0008, 0014, 0019, 0023 |
| Carry over: caveman-lite for agent-internal text; reader profile (India-aware, INR only when cost is the topic); fetch/bot-block order idea; "no sleep/poll loops" | keep | |

## 8. Fixture runs and migration

Order: **rules (Ark Nova) -> verify (Russia morale) -> learn (Saudi military)**. One domain fully done before the next.

### Intake questions to ask the user at execution time (deferred by design)
- **Rules / Ark Nova:** expansions in scope (Marine Worlds rulebook is image-only, 8 pages, no text layer); paths to local PDFs (base: `Arche_Nova_Rules_EN_Low_2022_01.pdf`, 20 pages; expansion: `ark-nova-marine-worlds-rules.pdf`); include solo and BGG designer posts?; which BGG/forum accounts count as designer/publisher.
- **Verify / Russia morale:** which input is the test (the existing course's source video/transcript, an article, or a claim list)? Which claims are known false to seed? Output tone for the unlisted page.
- **Learn / Saudi military:** scope boundary; which of the 9 existing chapters carry over (ch1-9 exist; ch7 Pakistan identity tangle; ch8-9 Gulf verdicts); contested topics; language level.
- **All:** freshness expectation (refresh only on request); extra domain-specific surfaces (BGG, Places video packs).

### Per-domain test (all four must pass)
1. Regenerate unattended from the same input; zero questions at run time.
2. Every claim has one of the 4 statuses; appendix lists sources covered and failed-to-grab; wave logs exist.
3. Seed one false claim; the run catches it, marks it `untrue`, blocks the push.
4. Diff against the old course: every old claim is retained, reclassified, or listed as dropped with a reason.

### Domain-specific notes
- **Ark Nova (rules):** authority order rulebook > publisher page > FAQ > errata (supersedes; check version date) > designer/publisher posts; player forum = `interpretive`. Existing evidence to mine: `deep-research/ark-nova/research/bgg-official-findings.md`, `bgg-forum-findings.md`, `base-visual-read.md`, `marine-worlds-visual-read.md`; source list in `.claude/docs/research/boardgame-sources-and-bgg-access.md`. Known gotchas: rulebook strength numbers, table rows and icon glyphs do not survive PDF text extraction (drop or mark unverified); BGG returns 403 to automated fetches (Cloudflare); BGG file downloads need login (user supplies PDFs). Rules page scope: essentials only, plus one "easiest strategy" section whose claims are `interpretive` (ADR 0022). Default player count 4 else max. Cut setup and endgame scoring unless the strategy needs them (the live Ark Nova course later included them; the rules page stays short).
- **Russia morale (verify):** old course has 14 chapters; transcript `subs.en.vtt` was never fetched (429). Verify page: untrue and interpretive cards only, `noindex`, unlisted, at `answers/verify-<slug>-<date>.html`. Header counts: checked, true (not listed), untrue, interpretive, not-found; skipped opinions/predictions counted.
- **Saudi (learn):** richest ledger-shaped content. Old unresolved items: `NOTES.md` pending list is stale; fact-check ledger at `~/.claude/docs/research/saudi-military/NOTES.md` (axis 1 of several done). Gulf verdicts folded into ch8-9 already.

### Cutover (only after all three pass)
1. Remove `ledgerlab/` from `Bearmancer/deep-research` (the skill now lives under `~/.claude/skills`), then archive that repo (GitHub archive, read-only; do not delete). Its NOTES, RESOURCES, learning-records stay readable.
2. Rename or remove the live `deep-research` skill; the new skill takes its triggers. Update the `claude/skills/` mirror via the normal backup.
3. Delete hand-maintained `fleet.md` table; keep the generated routing table.
4. Update `system-config/CLAUDE.md` index, README, CONTEXT.md glossary (add terms: claim, ledger, status, round, surface, paradigm, wave, gate, fixture), and add a pointer from `docs/adr/` to the rewrite ADRs in `.claude/plans/deep-research/rewrite/adr/`.
5. Close or update trackers: system-config map #55 (course vNext) and #56 (board-game mode) per `.claude/plans/backlog-2026-10-01.md`.

## 9. Voice rule: collection protocol

Status: pending (`ledgerlab/references/voice.md` in the deep-research repo). The user rejected the old agent's "phrasing style itself" and wants flowing, explanatory, easy-to-understand prose, even if slightly longer, not narrative.
1. Ask the user for 2-3 before/after samples (a paragraph from an existing course they dislike, and how they would phrase it).
2. Pull two or three paragraphs from live courses as candidates if they cannot supply samples; show old-style vs proposed.
3. Write the rule in `voice.md` with the samples as examples; add a lint (banned phrases, sentence length) only if the user agrees.
4. Carry over: no report language, inline-link citations on source-naming words, India-aware global scope.

## 10. Open or unverified items

- Per-step system prompt and tool-less extractor in `opencode run` (section 4.5).
- All four model ids (`opencode models` returned nothing); vision and audio capability; qwen 3.7 vs 3.8.
- Errata box: the glossary and `roles.md` put `untrue` claims in an errata box, but ADR 0019 allows only `true` (plain) and `interpretive` (debate) sentences, and `ledger.check_sentences` follows ADR 0019. Decide whether errata sentences need an ADR and their own check.
- POST routes in `registry.yaml` name `uv run scripts/<x>.py` files that live in the old `deep-research` skill; port them into `ledgerlab/` or point the routes at the old path before relying on them.
- ADR 0024 says archive `deep-research` after the fixtures; `ledgerlab/` is staged inside it (section 3).
- Registry tool names for Brave, Dappier, Crawl4AI; Tavily `tavily_extract` spelling; ScrapeGraph missing tools.
- Vendor reset windows; unverified error cells.
- Context7 and gh_grep dropped with OmO; re-add natively if wanted.
- Layout component list is final (12) but each needs real rendering tests.
- The 25-word quote cap and noindex-only exposure for verify pages are design choices the user accepted; the repo is public, so noindex reduces discovery only.
- Q39: the user asked for unlimited reproduction of source text on the public site. Not adopted; paraphrase + cite stands (ADR 0010). Revisit only with the user.
- Check whether the live `deep-research` skill's `references/` still reference OmO sidecars; clean at cutover.

## 11. Risks and gotchas

- No cap means a run can be long and costly; the stops are saturation, 5 rounds per claim, whole-pool key exhaustion, per-agent timeouts. Watch the first fixture run live.
- A key swap mid-call fails parallel agents: always take the rotation lock.
- A timed-out worker thread cannot be killed from `run_wave`. A task still running at the batch deadline is marked failed and not re-run beside the original; the wave returns without waiting for it. The `OpencodeRunner` subprocess timeout is the real kill switch.
- One active key per MCP is shared by every parallel agent.
- Prompt injection: only the tool-less extractor sees raw pages. If OpenCode cannot disable tools per step, find another way (separate agent definition) before any unattended run.
- YAML pitfall: bare `true`/`false` parse as booleans. `ledger.load_claims` normalises; always write via `ledger.dump_claims` (quotes the status).
- `ledger_check` returns early on schema errors by design.
- Backup `/MIR` deletes repo-only skills (section 1).
- Rotation locks are OS file locks released when the holder dies; do not add stale-lock takeover.
- Auto-merge to main on gate pass plus auto-revert on a failed live check: test the revert path on a throwaway branch before the first real publish.
- Public ledger exposes URLs, locators and short quotes; fine by decision, but re-check before publishing anything sensitive.

## 12. Definition of done

- [ ] Section 3 activation complete; draft tests green live.
- [ ] Config reconciled (model ids verified, OmO removed after ledgerlab is live, Brave/Dappier/Crawl4AI wired or dropped).
- [ ] Probes recorded (inventory, error codes, reset windows, fingerprints, reconnect latency, vision).
- [ ] Handlers B3 built with tests; driver runs a fixture end to end.
- [ ] Shell and 12 layouts built; index generator; noindex for verify.
- [ ] Voice rule written from the user's samples.
- [ ] All three fixtures pass the 4-step test, including the seeded false claim.
- [ ] `/skill-creator` evals exist and pass.
- [ ] Cutover steps done; old repo archived.

## 13. Suggested skills and order of operations

- `/skill-creator` (user-invoked) for B7. `tdd` for B1-B3 scripts. `grilling` + `domain-modeling` for any new decision; update `GLOSSARY.md` and add ADRs numbered 0025+. `research` for probe write-ups. `code-review` before merging. `handoff` when pausing.
- Suggested order: sections 3, 4, 5 -> B1, B2 -> B3 ingest/discover/verify on the rules fixture -> B3 write/gates/publish -> B4 -> rules fixture pass -> verify fixture -> learn fixture -> cutover.

## 14. Command cheat sheet

```
# tests (deep-research repo root)
uv run --with pytest --with pyyaml --with jsonschema pytest ledgerlab/tests --basetemp <empty temp dir>
# scripts run from ledgerlab/ as the `scripts` package
cd ledgerlab
# regenerate routing table after any registry edit (drift test enforces it)
uv run --with pyyaml --with jsonschema python -m scripts.gen_routing_table
# ledger gate on a topic dir
uv run --with pyyaml --with jsonschema python -m scripts.ledger_check <site>/_ledger/<topic> --publish
# start / resume a run
uv run --with pyyaml --with jsonschema python -m scripts.cli start --site-root <site> --topic <slug> "<prompt>"
uv run --with pyyaml --with jsonschema python -m scripts.cli resume <site>/_ledger/<topic>/runs/<run_id>
# log one attempt
uv run --with pyyaml --with jsonschema python -m scripts.log_attempt --file attempts.jsonl --claim c1 --round 1 --surface tavily.search --route mcp --url <u> --status ok
# keys (only this script reads ~/.secrets/.env)
uv run <skill>/scripts/switch_api_key.py --service all --list
uv run <skill>/scripts/switch_api_key.py --service all --materialize
# MCP status
opencode mcp list ; opencode api mcp.list
```

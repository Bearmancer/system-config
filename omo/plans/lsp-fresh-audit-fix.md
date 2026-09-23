# lsp-fresh-audit-fix - Work Plan

## TL;DR (For humans)

<!-- Fill this LAST, after the detailed plan below is written, so it summarizes the REAL plan. -->
<!-- Plain English for a non-engineer: NO file paths, NO todo numbers, NO wave/agent/tool names. -->

**What you'll get:** A recorded before-and-after check of missing language tools, then the missing pieces installed following the Fresh editor's official list, plus a clear demo that strict JSON and relaxed JSONC behave differently.

**Why this approach:** We snapshot failures first with the same checks we repeat after, so proof is apples-to-apples; and we follow Fresh's own server list instead of guessing, keeping the current Biome setup intact.

**What it will NOT do:** It won't edit your code, won't add project config files unless a real split demands it, and won't install anything beyond the agreed Fresh set.

**Effort:** Medium
**Risk:** Low - installs are user-level binaries plus evidence files; driver is npm/pip executable availability on Windows.
**Decisions to sanity-check:** Full python stack (all four side by side with documented order); Fresh-official markdown and JSON servers; Biome stays default in OpenCode.

Your next move: say start work now, or run a high-accuracy review first. Full execution detail follows below.

---

> TL;DR (machine): Medium effort, Low risk, Fresh-spec LSP audit-fix with PRE/POST proof + JSONC demo.

## Scope

### Must have

- PRE audit capture: OpenCode lsp_status, host Get-Command map, PSES logs, config-absence proof, all saved to evidence dir
- Fresh-spec installs: marksman, vscode-langservers-extracted, yaml-language-server, pyright, ty, ruff; verify csharp-ls + basedpyright-langserver already present
- POST confirm: re-run exact PRE queries, diff PRE vs POST, pass = missing now present + verify OK
- JSON-vs-JSONC distinct proof: paired fixtures run in Fresh terms (vscode server strict vs jsonc) and OpenCode terms (biome routing), both evidenced
- Purpose notes: ty-vs-basedpyright paragraph each + why both; ruff check-vs-format vs ruff server paragraph; with source URLs

### Must NOT have (guardrails, anti-slop, scope boundaries)

- No product code edits; installs are user-level executables only
- No new project lsp.json unless PRE/POST diff proves a routing split is required; allowlist only .opencode/lsp.json, .omo/lsp.json; approver is user
- No unrelated LSP servers; no replacing biome default with vscode-json-ls without POST proof; no pylsp install (Fresh default stays excluded by user scope)
- No invented Fresh spec; every Fresh claim cites config.rs line or docs/features/lsp.md

## Verification strategy

> Zero human intervention - all verification is agent-executed.

- Test decision: none (install/config plan, no prod code) + agent-executed QA per todo (happy + failure, exact tool + invocation, evidence path)
- Evidence: .omo/evidence/lsp-fresh-audit-fix/task-<N>-<slug>.<ext> (outside ulw-loop flat evidence dir; if inside ulw-loop use attemptDir from 'omo ulw-loop status --json')
- PRE/POST rule: every PRE command re-runs verbatim POST; diff saved; threshold: PRE documents failure (missing binary / FAIL status), POST shows present + OK or diagnostics answer

## Execution strategy

### Parallel execution waves

- Wave 1: Todo 1 (PRE audit) alone — everything depends on its snapshots
- Wave 2: Todos 2-6 (marksman, json-ls, yaml, python stack, csharp verify) in parallel — independent binaries
- Wave 3: Todos 7-8 (fixture proof, POST confirm + notes) in parallel after Wave 2 — need installed binaries

### Dependency matrix

| Todo            | Depends on | Blocks | Can parallelize with                                |
| --------------- | ---------- | ------ | --------------------------------------------------- |
| 1 PRE audit     | none       | 2-8    | none                                                |
| 2 marksman      | 1          | 7-8    | 3,4,5,6                                             |
| 3 json-ls       | 1          | 7-8    | 2,4,5,6                                             |
| 4 yaml          | 1          | 8      | 2,3,5,6                                             |
| 5 python stack  | 1          | 8      | 2,3,4,6                                             |
| 6 csharp verify | 1          | 8      | 2,3,4,5                                             |
| 7 fixture proof | 2,3        | 8      | 8* (*shares fixtures dir, run 7 first if collision) |
| 8 POST confirm  | 2-7        | F1-F4  | 7                                                   |

## Todos

> Implementation + Test = ONE todo. Never separate.

<!-- APPEND TASK BATCHES BELOW THIS LINE WITH edit/apply_patch - never rewrite the headers above. -->

-
  1. [x] PRE audit capture (failure baseline)
         What to do / Must NOT do: Run lsp_status MCP, Get-Command map for marksman/vscode-json-language-server/basedpyright-langserver/ty/ruff/yaml-language-server/csharp-ls, head of .omo/lsp-pses.log/StartEditorServices-*.log + .omo/lsp-pses-session.json, prove .opencode/lsp.json/.omo/lsp.json/.codex/lsp-client.json absent, save all stdout to evidence. Must NOT install anything in this todo.
         Parallelization: Wave 1 | Blocked by: none | Blocks: 2-8
         References (executor has NO interview context - be exhaustive): .omo/drafts/lsp-fresh-audit-fix.md (Findings/Decisions); .omo/lsp-pses.log/StartEditorServices-20688.log; .omo/lsp-pses-session.json:1; lsp-setup SKILL.md workflow §4 + scripts/verify-lsp.ts:102-115; Fresh config.rs#L5636-L5673 + #L5784-L5800 + docs/features/lsp.md (expected set)
         Acceptance criteria (agent-executable): evidence dir holds lsp_status output showing yaml-ls missing + no markdown entry, Get-Command table showing vscode-json/basedpyright/csharp present and marksman/ty/ruff/yaml absent, log excerpt, three config-absence proofs
         QA scenarios (name the exact tool + invocation): happy — `lsp_status` via MCP returns 42 configured; failure — `Get-Content .omo/lsp-pses.log/StartEditorServices-20688.log -Head 40` on missing log proves path wrong, record which file substituted. Evidence .omo/evidence/lsp-fresh-audit-fix/task-1-pre-audit.md
         Commit: N
-
  2. [x] Install marksman (Fresh markdown server)
         What to do / Must NOT do: Install marksman per Fresh spec (winget/choco or cargo install marksman per host), confirm `marksman server` starts. Must NOT write project lsp.json; user-level binary only.
         Parallelization: Wave 2 | Blocked by: 1 | Blocks: 7-8
         References (executor has NO interview context - be exhaustive): https://github.com/sinelaw/fresh/blob/1c8688e477d85c5cffb18cf4fd1a752182df5103/crates/fresh-editor/src/config.rs#L5784-L5800; https://github.com/sinelaw/fresh/blob/master/docs/features/lsp.md; https://github.com/artempyanykh/marksman; https://github.com/sinelaw/fresh/issues/2549; .omo/drafts/lsp-fresh-audit-fix.md
         Acceptance criteria (agent-executable): `Get-Command marksman` resolves; `marksman --version` exit 0; version string saved to evidence
         QA scenarios (name the exact tool + invocation): happy — `marksman --version` prints version; failure — `marksman server --help` unknown-arg output captured, proves arg surface. Evidence .omo/evidence/lsp-fresh-audit-fix/task-2-marksman.md
         Commit: N
-
  3. [x] Install vscode-langservers-extracted (Fresh json + jsonc server)
         What to do / Must NOT do: `npm install -g vscode-langservers-extracted`, confirm `vscode-json-language-server --stdio` exists. Fresh uses same binary for json and jsonc ids — document, do not invent separate jsonc binary. Must NOT replace biome default in OpenCode.
         Parallelization: Wave 2 | Blocked by: 1 | Blocks: 7-8
         References (executor has NO interview context - be exhaustive): https://github.com/sinelaw/fresh/blob/1c8688e477d85c5cffb18cf4fd1a752182df5103/crates/fresh-editor/src/config.rs#L5636-L5673; https://github.com/microsoft/vscode/blob/main/extensions/json-language-features/server/README.md; https://code.visualstudio.com/docs/languages/json; .omo/drafts/lsp-fresh-audit-fix.md
         Acceptance criteria (agent-executable): `Get-Command vscode-json-language-server` resolves; package version from `npm ls -g vscode-langservers-extracted` saved
         QA scenarios (name the exact tool + invocation): happy — binary on PATH; failure — `vscode-json-language-server --help` documents --stdio vs --node-ipc, capture output. Evidence .omo/evidence/lsp-fresh-audit-fix/task-3-jsonls.md
         Commit: N
-
  4. [x] Install yaml-language-server + verify
         What to do / Must NOT do: `npm install -g yaml-language-server`, run verify-lsp or MCP diagnostics on a sample .yaml. Must NOT touch unrelated npm globals.
         Parallelization: Wave 2 | Blocked by: 1 | Blocks: 8
         References (executor has NO interview context - be exhaustive): lsp-setup references/yaml/README.md:3-5; https://github.com/redhat-developer/yaml-language-server; lsp-setup scripts/verify-lsp.ts:102-115; .omo/drafts/lsp-fresh-audit-fix.md
         Acceptance criteria (agent-executable): `Get-Command yaml-language-server` resolves; diagnostics roundtrip on sample yaml returns (OK or problem list, not 'not installed')
         QA scenarios (name the exact tool + invocation): happy — `yaml-language-server --stdio --help` or version exit 0; failure — diagnostics on nonexistent file returns clean error, captured. Evidence .omo/evidence/lsp-fresh-audit-fix/task-4-yaml.md
         Commit: N
-
  5. [x] Install python full stack (pyright + ty + ruff) with routing table
         What to do / Must NOT do: Verify basedpyright-langserver present; `pip install pyright ty ruff` (or uv tool), confirm `pyright-langserver --stdio`, `ty server`, `ruff server` all resolve; write routing table (basedpyright = production Pyright-compatible checker today; ty = Astral Rust future, types only; ruff server = lint+format per keystroke alongside a type server) into evidence. Explicitly note Fresh default pylsp excluded per user scope. Must NOT enable all four simultaneously in any editor without priority order — document order, do not reconfigure editors.
         Parallelization: Wave 2 | Blocked by: 1 | Blocks: 8
         References (executor has NO interview context - be exhaustive): lsp-setup references/python/README.md:3-5,42-47; https://docs.basedpyright.com/latest/; https://docs.astral.sh/ty/ + https://docs.astral.sh/ty/features/language-server/; https://docs.astral.sh/ruff/ + https://docs.astral.sh/ruff/editors/ + migration https://github.com/astral-sh/ruff/blob/main/docs/editors/migration.md; Fresh docs https://github.com/sinelaw/fresh/blob/master/docs/features/lsp.md; .omo/drafts/lsp-fresh-audit-fix.md
         Acceptance criteria (agent-executable): all three new binaries resolve + basedpyright still resolves; `ruff --version`, `ty --version` outputs saved; routing table file exists in evidence
         QA scenarios (name the exact tool + invocation): happy — `ruff check --help` + `ruff format --help` both exit 0 proving dual role; failure — `ty server --help` on wrong flag captured. Evidence .omo/evidence/lsp-fresh-audit-fix/task-5-python.md
         Commit: N
-
  6. [x] Verify csharp-ls present + diagnostics roundtrip
         What to do / Must NOT do: Confirm csharp-ls.exe resolves, run diagnostics on a sample .cs (MCP diagnostics or verify-lsp). No install expected — prove present. Must NOT install dotnet SDK unless binary missing (it is present).
         Parallelization: Wave 2 | Blocked by: 1 | Blocks: 8
         References (executor has NO interview context - be exhaustive): lsp-setup references/csharp/README.md:3-5,41-43; https://github.com/razzmatazz/csharp-language-server; .omo/drafts/lsp-fresh-audit-fix.md; Get-Command result 2026-09-22 (csharp-ls.exe present)
         Acceptance criteria (agent-executable): `Get-Command csharp-ls` resolves; diagnostics roundtrip answers (OK or problem list, not 'not installed'); binary-name mapping table (OpenCode id csharp = exe csharp-ls) saved
         QA scenarios (name the exact tool + invocation): happy — diagnostics on sample .cs returns; failure — diagnostics on missing path returns clean error, captured. Evidence .omo/evidence/lsp-fresh-audit-fix/task-6-csharp.md
         Commit: N
-
  7. [x] JSON-vs-JSONC distinct fixture proof (dual terms)
         What to do / Must NOT do: Create paired fixtures (.json strict with comment = must error; .jsonc same content = must pass) in evidence work dir; run through vscode-json-ls semantics (document strict vs jsonc tolerance) and OpenCode biome routing (extension .json vs .jsonc, parser flags allowComments/allowTrailingCommas); save both outputs. Teardown fixtures if outside evidence dir. Must NOT leave fixtures in repo root.
         Parallelization: Wave 3 | Blocked by: 2,3 | Blocks: 8
         References (executor has NO interview context - be exhaustive): https://github.com/microsoft/vscode/blob/main/extensions/json-language-features/server/README.md; https://code.visualstudio.com/docs/languages/json; https://biomejs.dev/internals/language-support/; Fresh config.rs#L5636-L5673; lsp-setup scripts/detect-lsp.ts:85; .omo/drafts/lsp-fresh-audit-fix.md
         Acceptance criteria (agent-executable): fixture A (.json + //comment) errors; fixture B (.jsonc identical) passes with comments ignored; both results saved with exact commands quoted
         QA scenarios (name the exact tool + invocation): happy — strict errors + jsonc passes; failure — trailing-comma variant: jsonc warns-or-passes while json errors, captured as second pair. Evidence .omo/evidence/lsp-fresh-audit-fix/task-7-jsonc-proof.md
         Commit: N
-
  8. [x] POST same-query confirm + purpose notes
         What to do / Must NOT do: Re-run Todo 1 exact commands verbatim; diff PRE vs POST; write ty-vs-basedpyright + ruff-server-vs-format notes with URLs into evidence; declare project lsp.json needed/not-needed against split trigger. Must NOT claim done unless every missing binary now resolves.
         Parallelization: Wave 3 | Blocked by: 2-7 | Blocks: F1-F4
         References (executor has NO interview context - be exhaustive): Todo 1 evidence; https://docs.astral.sh/ty/; https://docs.basedpyright.com/latest/; https://docs.astral.sh/ruff/editors/; .omo/drafts/lsp-fresh-audit-fix.md Scope OUT allowlist
         Acceptance criteria (agent-executable): POST Get-Command shows marksman/yaml-language-server/pyright/ty/ruff now present; lsp_status re-run saved; PRE/POST diff file exists; notes file exists
         QA scenarios (name the exact tool + invocation): happy — diff shows only additions (no regressions); failure — any still-missing binary listed as blocker with install error quoted, not silently skipped. Evidence .omo/evidence/lsp-fresh-audit-fix/task-8-post-confirm.md
         Commit: N

## Final verification wave

> Runs in parallel after ALL todos. ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.

- [x] F1. Plan compliance audit
      Every Todo 1-8 evidence file exists; PRE commands re-ran verbatim POST; no todo skipped; diff saved.
- [x] F2. Code quality review
      No product files touched; no repo-root fixtures left; no project lsp.json written unless split trigger proven with user approval.
- [x] F3. Real manual QA
      Binaries actually execute (marksman --version, yaml --help, ruff check/format --help, ty --version); fixture proof ran for real (strict errors, jsonc passes); outputs quoted, not self-reported.
- [x] F4. Scope fidelity
      Only Fresh-spec set installed; biome default untouched; pylsp excluded as scoped; purpose notes present with URLs; extra work listed or none.

## Commit strategy

No commits (environment installs + evidence only, no repo code). If evidence dir policy requires commit, one commit: `docs(lsp): fresh-spec audit baseline and post-confirm evidence`. Mimic `git log --oneline -20` before composing.

## Success criteria

- PRE failure documented (missing marksman/ty/ruff/yaml + absent configs) and POST proves all resolve via same queries
- Fresh routing honored (marksman markdown; vscode-json-ls json+jsonc split ids) with OpenCode biome routing documented, not replaced
- Python routing table + ty/basedpyright + ruff-server/format notes exist with source URLs
- Worker needed zero interview; every todo had references + executable acceptance + happy/failure QA

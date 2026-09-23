# Topgrade Autonomy — no prompts + auto log triage

> User ask: Fix topgrade failures requiring (a) manual `no` press i.e. not autonomous, (b) manual log reading to isolate proper fixes.
> Goal: `toolbox maintenance topgrade` runs fully unattended. Zero prompts. Fail step maps to root fix automatically.

## Facts

- Topgrade 17.12.0 at `C:\Users\Lance\.cargo\bin\topgrade.exe`. Config `C:\Users\Lance\AppData\Roaming\topgrade.toml`.
- Current: `ignore_failures=["dotnet"]`, `assume_yes` commented, `ask_retry` default true = manual retry prompt.
- Zero topgrade refs in `Dev/Toolbox`. No wrapper, no parser.
- Reusable: `create-scheduled-task/run-sync.ps1` + `install-scheduler.ps1` + `state/logs/scheduler/sync-*.log`.

## Autonomy decision

- Config file over CLI flags. One source of truth.
- Set `[misc]`: `assume_yes = true`, `ask_retry = false`, `auto_retry = 1`. Keep `ignore_failures = ["dotnet"]`. No legacy `no_retry`.
- `disable` stays user-owned, parser suggests entry, human confirms.

## Design

- New `Services.Maintenance`: `TopgradeRunner` (spawn, exit code) → `TopgradeParser` (pure, FAILED markers) → `TopgradeFixMapper` (pure dict step→hint).
- Telemetry: `ServiceName.Maintenance` → `state/logs/maintenance.jsonl`. Scheduler transcript `state/logs/scheduler/topgrade-*.log`.
- CLI: `toolbox maintenance topgrade [--config]` thin → ErrorOr → 0/1. One line per failed step + fix.
- Scheduler: `create-scheduled-task/run-topgrade.ps1` mirrors `run-sync.ps1` + weekly task.

## TODOs

-
  1. [x] Add `ServiceName.Maintenance` + slug + Errors.Maintenance factories — verify by build ok, slug maintenance
-
  2. [x] Implement `TopgradeParser` pure + xunit theory — verify by red-green, 0 skips
-
  3. [x] Implement `TopgradeFixMapper` pure + xunit theory — verify by each fail maps to hint
-
  4. [x] Implement `TopgradeRunner` spawn + exit-code + timeout/cancel — verify by mocked tests, cancel never Error
-
  5. [x] Wire `maintenance topgrade` Spectre command thin — verify by CLI 0/1, Title Case output
-
  6. [x] Add `run-topgrade.ps1` + scheduler registration — verify by dry-run log + prune
-
  7. [x] Set `assume_yes=true, ask_retry=false, auto_retry=1` in topgrade.toml + e2e unattended — verify by zero prompts, fail maps to fix

## Waves

- Wave 1: T1 || T6-draft
- Wave 2: T2 || T3 (deps T1)
- Wave 3: T4 → T5 (deps T2+T3)
- Wave 4: T6 finalize + T7 (deps T5)

## Final Verification Wave

- [x] F1. Goal/constraint check — unattended, triage lines present
- [x] F2. Quality — ErrorOr, zero comments, const paths, Title Case
- [x] F3. Security — no secrets, safe spawn, timeout
- [x] F4. QA — live run artifact + cleanup receipt

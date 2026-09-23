# ulw-research outputs — pointer index

Read this before touching any file under `.omo/ulw-research/`, `.omo/plans/`, `.omo/notepads/`.

## Stamp bundles: `C:\Users\Lance\.omo\ulw-research\<stamp>\`

Treat each `<stamp>` dir as one sealed bundle. Example: `20260915-073104` (9 files).
Read in this order: SYNTHESIS first, report.html second, rest only as needed.

- `SYNTHESIS.md` — trust this as the cited record: verdict table + resolved contradictions. Differs from `report.html` by being record over presentation.
- `claim-graph.md` — trust this as the sole allowlist for assertions (supported | partial | refuted | unresolved). Differs from SYNTHESIS by gating every claim, not delivering the verdict.
- `observation-manifest.md` — trust this as the evidence ledger (O-ids, source, fetch status, quotes). Differs from claim-graph by recording what was seen, not what is true.
- `intent-diff.md` — trust this as the intent-closure check (expected vs observed per intent row). Differs from observation-manifest by judging ask-satisfaction, not logging sources.
- `expansion-log.md` — trust this as the run history (waves, member axes, format gate). Differs from verification-economics by recording what ran, not what verification cost.
- `verification-economics.md` — trust this as the verification ledger (risk vs error cost vs path chosen, defer decisions, counter-searches). Differs from expansion-log by justifying verification spend, not narrating waves.
- `report.html` — hand this to humans as the readable deliverable. Differs from SYNTHESIS by presentation over record; never cite it as evidence.
- Deliverable files (`*.pdf`, `*.docx`, etc.) — ship these as asked-for formats. Example bundle carries `Soltissimo-1-Link-Hunt.pdf` + `Soltissimo-1-Link-Hunt.docx`. Differ from `report.html` by being frozen hand-offs, not the browsable report.

## Plans: `C:\Users\Lance\.omo\plans\`

- Name one plan per task: `<slug>.md`. Example: `terminal-toolchain-office-research.md`.
- Follow the convention sections in order: TL;DR, Scope (IN/OUT), Verification strategy, Execution strategy (waves), Todos, Final verification wave, Commit strategy, Success criteria, Todo details (references / acceptance / QA / evidence / commit).
- Feed workers from Todo details only — never paraphrase acceptance or QA steps.

## Notepads: `C:\Users\Lance\.omo\notepads\`

- Scope notepads per task dir. Example: `notepads/terminal-toolchain-office-research/` carries `learnings.md`, `problems.md`, `issues.md`, `decisions.md`.
- Write learnings, problems, issues, decisions there during work; never duplicate bundle evidence into them.

## Skill note

- `ulw-research` is harness-native. No skill file exists on disk — do not search for one.

## Research feeds implementation

- Consume a stamp bundle as cited evidence: quote SYNTHESIS verdicts + claim-graph ids + observation-manifest O-ids into the plan's Todo details references.
- Start implementation from the plan file, not from raw bundle files. Workers execute Todos; bundle files stay read-only evidence.

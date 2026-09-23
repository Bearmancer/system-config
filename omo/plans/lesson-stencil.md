# Plan: lesson stencil — fixed-shape template + stamp (feasibility & adoption)

## Verdict

**PARTIAL YES.** A stencil + stamp tool structurally precludes every _shape_ bug
class (missing/misordered footer, missing Sources block, legacy-section
regressions) and precludes orphan anchors + dangling index hrefs **iff** stamp
and publisher derive their row ids from one shared contract. It cannot preclude
content-truth errors or worker non-delivery — those keep gate + disk-verify
defenses. Adopt as structure owner; keep `check_lesson.py` as backstop.

## Bug-class coverage

| Class                                             | Precluded? | Mechanism / residual defense                                                |
| ------------------------------------------------- | ---------- | --------------------------------------------------------------------------- |
| Missing or misordered footer nav                  | Yes        | Template owns the footer; writer never touches it                           |
| Dangling `../../index.html` / `../index.html#chK` | Yes*       | Stamp derives both from filename; *publisher must share the row-id function |
| Orphan `chK` anchors (anchor without lesson)      | Yes*       | Same single-writer contract both sides; contract test pins parity           |
| Missing per-chapter Sources block                 | Yes        | Unconditional slot; empty list = stamp hard fail                            |
| Open Threads / fact-check-box regressions         | Yes        | No such blocks exist in the template                                        |
| Banned-phrase smuggle inside free narrative       | No         | Gate phrase scan stays                                                      |
| Content truth (verdicts, citations, facts)        | No         | Verification fan-out + review stays                                         |
| Worker non-delivery (no diff, TEMP writes)        | No         | Stamp contract: repo path only + diff stat + mtime + gate exit 0 in report  |

## Architecture

- **Skill-owned**: `learning-course/assets/lesson.stencil.html` — fixed order
  (kicker, H1, surtitle, meta, cast, essentials, narrative, machinery, Sources,
  footer Home/Prev/Next-or-Index/Glossary), no legacy blocks, slot markers.
- **Workspace-owned**: `lessons/<slug>.yaml` per lesson — scalars (kicker,
  title, chapter_n, chapter_m, timerange, lesson_nn), lists (cast, essentials,
  skippables, sources[label,url,note]), exactly two restricted-HTML fragments
  (narrative, machinery); everything else plain text, stamp escapes.
- **Skill-owned**: `scripts/stamp_lesson.py` — stdlib only. YAML + stencil →
  lesson HTML; derives chK from filename, assembles footer nav + Sources,
  pre-checks max-twice, fails closed, writes repo path only, prints diff stat +
  mtime. TDD against golden + corrupt fixtures (from Task 2b).
- **Shared contract**: stamp and `publish-teach.ps1` use the same row-id regex
  (`-ch0*(\d+)` else `^(\d+)` → `chK` / `lesson-NN`); a contract test pins both.

## Migration options

| Option                   | Scope                                                               | Cost       | Risk                                                | Existing wave-3 footer work   |
| ------------------------ | ------------------------------------------------------------------- | ---------- | --------------------------------------------------- | ----------------------------- |
| A forward-only           | New lessons stamped                                                 | Lowest     | Two shapes coexist, old drift continues             | Keep                          |
| B on-touch (recommended) | New stamped + restamp each lesson when edited; 3-lesson pilot first | Low-medium | Bounded churn, converges over time                  | Keep; overwrite only on touch |
| C full backfill          | Reverse-extract 31 YAMLs, restamp everything                        | Highest    | Regression in shipped pages; per-lesson review load | Supersede                     |

Do not commit to C until the 3-lesson pilot yields a per-lesson number.

## Waves

- **W1 (done, inline)** — Shape contract frozen:
  `learning-course/references/stencil-contract.md` (owner table, row-id
  contract, publisher parity test spec).
- **W2 (done, inline)** — 2a: `learning-course/assets/lesson.stencil.html`.
  2b: `learning-course/references/lesson-schema.md` (schema + golden + 10
  corrupt variants).
- **W3 (done, inline)** — `scripts/stamp_lesson.py` (stdlib-only, fails closed,
  repo-path-only writes, diff stat). Suite: `run_stencil_tests.py` 12/12 —
  stamped golden passes the gate, all 11 corrupt variants fail with their rule
  tags (RED 0/12 → GREEN 12/12).
- **W4 (done, inline)** — Round-trip wired: stencil suite runs the gate on the
  stamped golden; `run_parity_test.py` pins the shared row-id pattern
  `(?i)-ch0*(\d+)` in BOTH `stamp_lesson.py` and `publish-teach.ps1` and
  asserts identical ids across fixtures — drift alarm.
- **W5 (next)** — 3-lesson pilot (one new-model, one legacy, one mixed/stub):
  reverse-extract YAML, stamp, diff review, gate exit 0, anchor probe, record
  minutes → go/no-go number for option C.
- **W6 (done, inline)** — Docs: `workflow.md` gains “The stencil (stamp-only
  lesson writing)” (paths, stamp usage, writer rule, migration B recorded);
  `SKILL.md` Step 5 + scripts list updated.

- **W1 (ultrabrain)** — Freeze shape contract: map every gate rule + spec
  section + publisher regex to template/content/gate owner; pin row-id function.
  QA: contract table complete, regex quoted exact.
- **W2 (deep ∥ deep)** — 2a: draft `lesson.stencil.html` per contract.
  2b: YAML schema + golden example + corrupt-variant list.
  QA: slot names match schema; banned blocks absent by grep.
- **W3 (deep + programming)** — stamp_lesson.py TDD: golden stamps gate-clean;
  each corrupt variant fails distinctly; repo-path-only writes.
- **W4 (deep + programming)** — Gate self-test: stamp round-trip in
  `run_gate.py`; stamped golden MUST pass; corrupt MUST fail with expected
  reason; stamped real-footer fixture committed (fixture-vs-reality drift
  impossible: a fixture IS stamp output).
- **W5 (deep + programming)** — 3-lesson pilot (one new-model, one legacy, one
  mixed/stub): diff review, gate exit 0, index anchor probe, record minutes →
  go/no-go number for Option C.
- **W6 (writing)** — Docs: stencil paths, stamp usage, stamp-only writer rule
  (repo path + diff stat + mtime + gate exit in every report), row-id contract,
  recorded D1–D3 decisions.

## Decisions pending (user)

- **D1 content format**: YAML (recommended) vs markdown-frontmatter vs JSON.
- **D2 template engine**: stdlib placeholders (recommended) vs Jinja dependency.
- **D3 migration scope**: A vs B (recommended) vs C + wave-3 disposition.

## Risks

- Publisher regex drift reopens dangling/orphan class → contract test.
- Over-constrained stencil blocks legitimate variation → pilot must include an
  edge lesson; slots for both narrative styles.
- Reverse-extract errors under C → per-lesson diff review mandatory.
- Worker non-delivery persists structurally → stamp-only writer rule + lead
  disk-verify (path + diff stat + mtime), per standing rules.

## Effort

6 tasks, mostly sequential; ~2–4 focused sessions to W6. Option C adds
per-lesson extraction cost, measured in W5 before any commitment.

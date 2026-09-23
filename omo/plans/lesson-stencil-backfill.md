# lesson-stencil-backfill - Work Plan

## TL;DR (For humans)

**What you'll get:** all 33 shipped lesson pages regenerated from fixed-shape YAML through the stamp tool, each diff-reviewed, so footers, Sources blocks, and anchors can no longer drift.

**Why this approach:** pages that already have YAML get restamped first (cheap, proves the pipeline); the 11 YAML-less pages get reverse-extracted then stamped; per-lesson diff review stays mandatory throughout.

**What it will NOT do:** it will not change lesson content or verdicts, will not touch the publisher, will not invent missing lessons for the empty topic, and will not commit to anything beyond the stamped pages.

**Effort:** Large
**Risk:** Medium - reverse-extraction can misread legacy pages; per-lesson diff review is the guard.
**Decisions to sanity-check:** D1 YAML, D2 stdlib, D3 C full backfill with pilot-gate waiver (all owner-locked, ledger-recorded).

Your next move: worker executes waves in order. Full execution detail follows below.

---

> TL;DR (machine): Large effort, Medium risk; 33 lessons restamp-verified; owner decisions D1 YAML / D2 stdlib / D3 C recorded.

## Scope

### Must have

- W0: stamp suite 12/12 green, parity test green, Python+YAML ready.
- W1: 22 YAML-present lessons restamped + diff-reviewed (control-story 13, historians-on-trump 8, political-spectrum 1).
- W2: 11 YAML-missing lessons reverse-extracted to YAML then stamped + diff-reviewed (amway-tools-cult 7, soviet-afghan-war 3, stalin-red-tsar 1).
- W3: gate exit 0 on all 33 stamped pages + index anchor probe + row-id parity re-check.
- Per-lesson diff review mandatory; record minutes per topic for the Option C cost number.

### Must NOT have (guardrails, anti-slop, scope boundaries)

- No content/verdict changes; stamp output shape only. Any content delta found in diff review is reported, never silently kept.
- No publisher changes (`publish_teach.py` vs plan's `publish-teach.ps1` name mismatch is recorded, not fixed here).
- No koscot lesson creation (empty topic, nothing to backfill).
- No edits to the canonical skill except through the skill's own workflow; workspace stencil copies left as-is unless the plan says otherwise.
- No commit of anything except stamped lesson HTML + their YAML (per repo commit rules).

## Verification strategy

> Zero human intervention - all verification is agent-executed.

- Test decision: tests-after for reverse-extraction (golden + corrupt fixtures exist); gate exit 0 per lesson is the executable acceptance.
- Evidence: .omo/evidence/lesson-stencil-backfill/task-<N>.txt per todo (diff stats, gate exits, minutes).
- Anchor probe: every stamped page's chK anchors resolve from the index (probe command + output pasted).

## Execution strategy

### Parallel execution waves

- Wave 0 (todos 1-2): setup verify. Sequential (shared toolchain).
- Wave 1 (todos 3-5): YAML-present restamp, one todo per topic. Parallel (disjoint dirs).
- Wave 2 (todos 6-8): YAML-missing extract+stamp, one todo per topic. Parallel (disjoint dirs). Blocked on Wave 0 only.
- Wave 3 (todos 9-10): full gate + anchor probe + parity. Sequential after Waves 1-2.
- Final wave F1-F4 in parallel after ALL todos; ALL must APPROVE.

### Dependency matrix

| Todo | Depends on | Blocks | Can parallelize with |
| ---- | ---------- | ------ | -------------------- |
| 1    | -          | 2      | -                    |
| 2    | 1          | 3-8    | -                    |
| 3    | 2          | 9      | 4,5,6,7,8            |
| 4    | 2          | 9      | 3,5,6,7,8            |
| 5    | 2          | 9      | 3,4,6,7,8            |
| 6    | 2          | 9      | 3,4,5,7,8            |
| 7    | 2          | 9      | 3,4,5,6,8            |
| 8    | 2          | 9      | 3,4,5,6,7            |
| 9    | 3-8        | 10     | -                    |
| 10   | 9          | F1-F4  | -                    |

### Token registry (sanctioned placeholders — no others permitted)

| token        | resolved by     | resolution                                                            |
| ------------ | --------------- | --------------------------------------------------------------------- |
| <topic>      | each topic todo | literal topic dir name under C:\Users\Lance\.omo\teach                |
| teach root   | recon           | C:\Users\Lance\.omo\teach                                             |
| stamp script | recon           | C:\Users\Lance\.claude\skills\learning-course\scripts\stamp_lesson.py |

## Todos

> Implementation + Test = ONE todo. Never separate.

-
  1. [x] Verify stamp toolchain green before any lesson work
         What to do / Must NOT do: Run run_stencil_tests.py (expect 12/12) + run_parity_test.py (expect pass) + `python --version` and YAML import check. Record outputs. Touch nothing else.
         Parallelization: Wave 0 | Blocked by: - | Blocks: 2
         References: C:\Users\Lance\.claude\skills\learning-course\scripts\fixtures\stencil\run_stencil_tests.py, run_parity_test.py, C:\Users\Lance\.omo\teach (root).
         Acceptance criteria: .omo/evidence/lesson-stencil-backfill/task-1.txt holds 12/12 line, parity pass line, python version; any RED blocks all waves.
         QA scenarios: happy — all green; failure — RED means fix toolchain first, never proceed to lessons. Evidence .omo/evidence/lesson-stencil-backfill/task-1.txt.
         Commit: N | evidence only.
-
  2. [x] Freeze the per-lesson work procedure from the skill workflow
         What to do / Must NOT do: Read workflow.md + stencil-contract.md + lesson-schema.md; record the exact per-lesson step order (extract→stamp→diff→gate→probe→minutes) into task-2.txt as the checklist todos 3-8 execute. No lesson work yet.
         Parallelization: Wave 0 | Blocked by: 1 | Blocks: 3-8
         References: C:\Users\Lance\.claude\skills\learning-course\references\workflow.md, stencil-contract.md, lesson-schema.md.
         Acceptance criteria: task-2.txt holds the numbered checklist todos 3-8 will follow verbatim.
         QA scenarios: happy — checklist complete; failure — ambiguous step means re-read, never guess. Evidence .omo/evidence/lesson-stencil-backfill/task-2.txt.
         Commit: N | evidence only.
-
  3. [ ] Restamp control-story (13 YAML-present lessons) + diff review
         What to do / Must NOT do: Restamp all 13 lessons from their existing YAML via stamp_lesson.py; diff each stamped page against shipped bytes; gate exit 0 each; anchor probe; record minutes. Content deltas reported, never silently kept.
         Parallelization: Wave 1 | Blocked by: 2 | Blocks: 9
         References: C:\Users\Lance\.omo\teach\control-story\lessons\, stamp script, task-2 checklist.
         Acceptance criteria: task-3.txt holds per-lesson diff stats, 13 gate exits 0, probe outputs, total minutes.
         QA scenarios: happy — all green; failure — any gate RED or content delta means report + hold that lesson, continue the rest. Evidence .omo/evidence/lesson-stencil-backfill/task-3.txt.
         Commit: Y per reviewed lesson batch, repo style | stamp(control-story): restamp 13 lessons from YAML.
-
  4. [ ] Restamp historians-on-trump (8 YAML-present lessons) + diff review
         What to do / Must NOT do: Same procedure as todo 3 for all 8 lessons.
         Parallelization: Wave 1 | Blocked by: 2 | Blocks: 9
         References: C:\Users\Lance\.omo\teach\historians-on-trump\lessons\, stamp script, task-2 checklist.
         Acceptance criteria: task-4.txt holds per-lesson diff stats, 8 gate exits 0, probe outputs, total minutes.
         QA scenarios: happy — all green; failure — report + hold that lesson. Evidence .omo/evidence/lesson-stencil-backfill/task-4.txt.
         Commit: Y per reviewed lesson batch | stamp(historians-on-trump): restamp 8 lessons from YAML.
-
  5. [ ] Restamp political-spectrum (1 YAML-present lesson) + diff review
         What to do / Must NOT do: Same procedure as todo 3 for the single lesson.
         Parallelization: Wave 1 | Blocked by: 2 | Blocks: 9
         References: C:\Users\Lance\.omo\teach\political-spectrum\lessons\, stamp script, task-2 checklist.
         Acceptance criteria: task-5.txt holds diff stat, gate exit 0, probe output, minutes.
         QA scenarios: happy — green; failure — report + hold. Evidence .omo/evidence/lesson-stencil-backfill/task-5.txt.
         Commit: Y | stamp(political-spectrum): restamp 1 lesson from YAML.
-
  6. [ ] Reverse-extract + stamp amway-tools-cult (7 YAML-missing lessons) + diff review
         What to do / Must NOT do: Reverse-extract each of the 7 shipped pages to YAML per lesson-schema.md (scalars, lists, exactly two restricted-HTML fragments, everything else plain text, stamp escapes); stamp; diff review; gate exit 0; anchor probe; record minutes.
         Parallelization: Wave 2 | Blocked by: 2 | Blocks: 9
         References: C:\Users\Lance\.omo\teach\amway-tools-cult\lessons\, lesson-schema.md golden example, stamp script, task-2 checklist.
         Acceptance criteria: task-6.txt holds 7 YAML paths, per-lesson diff stats, 7 gate exits 0, probe outputs, total minutes.
         QA scenarios: happy — all green; failure — extraction doubt means hold that lesson with the exact ambiguity recorded, never force. Evidence .omo/evidence/lesson-stencil-backfill/task-6.txt.
         Commit: Y per reviewed lesson batch | stamp(amway-tools-cult): extract + restamp 7 lessons.
-
  7. [ ] Reverse-extract + stamp soviet-afghan-war (3 YAML-missing lessons) + diff review
         What to do / Must NOT do: Same procedure as todo 6 for all 3 lessons.
         Parallelization: Wave 2 | Blocked by: 2 | Blocks: 9
         References: C:\Users\Lance\.omo\teach\soviet-afghan-war\lessons\, lesson-schema.md, stamp script, task-2 checklist.
         Acceptance criteria: task-7.txt holds 3 YAML paths, per-lesson diff stats, 3 gate exits 0, probe outputs, total minutes.
         QA scenarios: happy — all green; failure — hold with ambiguity recorded. Evidence .omo/evidence/lesson-stencil-backfill/task-7.txt.
         Commit: Y per reviewed lesson batch | stamp(soviet-afghan-war): extract + restamp 3 lessons.
-
  8. [ ] Reverse-extract + stamp stalin-red-tsar (1 YAML-missing lesson) + diff review
         What to do / Must NOT do: Same procedure as todo 6 for the single lesson.
         Parallelization: Wave 2 | Blocked by: 2 | Blocks: 9
         References: C:\Users\Lance\.omo\teach\stalin-red-tsar\lessons\, lesson-schema.md, stamp script, task-2 checklist.
         Acceptance criteria: task-8.txt holds YAML path, diff stat, gate exit 0, probe output, minutes.
         QA scenarios: happy — green; failure — hold with ambiguity recorded. Evidence .omo/evidence/lesson-stencil-backfill/task-8.txt.
         Commit: Y | stamp(stalin-red-tsar): extract + restamp 1 lesson.
-
  9. [ ] Full gate sweep + index anchor probe + parity re-check across all 33
         What to do / Must NOT do: Run the gate over every stamped page (exit 0 each), probe every chK anchor from the index, re-run the row-id parity test; record per-topic rollup plus the Option C per-lesson cost number from todos 3-8 minutes.
         Parallelization: Wave 3 | Blocked by: 3-8 | Blocks: 10
         References: gate runner, parity test, todos 3-8 evidence.
         Acceptance criteria: task-9.txt holds 33 gate exits, probe results, parity pass, cost number.
         QA scenarios: happy — all green; failure — failing page returns to its topic todo with the gate output. Evidence .omo/evidence/lesson-stencil-backfill/task-9.txt.
         Commit: N | verification only.
-
  10. [ ] Held-lesson disposition + backfill closeout report
          What to do / Must NOT do: For every lesson held in todos 3-8 (if none, state explicitly), record its ambiguity and the owner decision needed; write the closeout report (per-topic minutes, total, gate tally, held list) to task-10.txt.
          Parallelization: Wave 3 | Blocked by: 9 | Blocks: F1-F4
          References: todos 3-9 evidence.
          Acceptance criteria: task-10.txt holds the held list (or explicit none) plus closeout rollup.
          QA scenarios: happy — rollup complete; failure — unaccounted lesson means recount. Evidence .omo/evidence/lesson-stencil-backfill/task-10.txt.
          Commit: N | report only.

## Final verification wave

> Runs in parallel after ALL todos. Each check writes its own evidence file (.omo/evidence/lesson-stencil-backfill/task-F<n>.txt). ALL must APPROVE. Surface results and wait for the user's explicit okay before declaring complete.

- [ ] F1. Plan compliance audit — every todo 1-10 has its evidence file with acceptance output; dependency order honored; held lessons all accounted in todo 10.
- [ ] F2. Content fidelity — spot-check stamped pages against shipped bytes: shape-only deltas (footer, Sources, anchors); zero content/verdict changes; held list matches actual holds.
- [ ] F3. Gate + parity re-run — gate suite and row-id parity re-run green on demand, outputs pasted.
- [ ] F4. Scope fidelity — Must-NOT-haves intact: no publisher changes, no koscot creation, no content edits, no skill edits.

## Commit strategy

- One atomic commit per reviewed lesson batch, repo style (`stamp(<topic>): ...`); never one end-of-run omnibus. Mimic existing log shape before composing.

## Success criteria

- 33/33 lessons stamped, gate exit 0 each, anchors resolve, parity green.
- Per-lesson diff reviews complete; held lessons listed with owner decisions pending.
- Option C per-lesson cost number recorded from real minutes.

# agents-config-restructure - Work Plan

## TL;DR (For humans)

**What you'll get:** Clean agents-config repo with unified skills-first schema, caveman ultra mode active, grill-me auto-loaded for ulw workflows, teaching content publishing to GitHub Pages via modified learning-course skill.

**Why this approach:** Minimal disruption to omo native paths while achieving your goals: no external skill bloat, stress-tested planning via grill-me, ultra-compressed communication always on.

**What it will NOT do:** Change omo's runtime behavior (where it writes plans/research/teach). Only modify user-owned skills to output differently.

**Effort:** Medium
**Risk:** Low - all changes are to user-owned files, omo native paths untouched
**Decisions:** Unified skills/ dir, remove all external skills.sh backup, grill before research

## Scope

### Affected user and ideal state

**Affected user:** Lance (you)

**Ideal state:**

- IS-1: agents-config repo contains ONLY user-defined skills (no external skills.sh catalog)
- IS-2: Single unified skills/ dir at repo root (no claude/skills/ vs opencode/skills/ duplication)
- IS-3: Caveman ultra mode global always-on (installed in ~/.omo/agent/skills/)
- IS-4: Grill-me auto-loaded when invoking ulw-plan/ulw-research/ulw
- IS-5: learning-course Step 6 invokes ulw-research with grill-me (stress-test brief first)
- IS-6: Teaching content publishes to Bearmancer GitHub Pages (skill output change, not path change)
- IS-7: Finished AND out-of-scope plans/notepads removed from repo backup (omo/plans/ and omo/notepads/ end empty)
- IS-8: "Questions ONLY via QA tool" rule enforced globally

### Must have

- Unified skills/ dir with user-authored skills only
- Caveman installed to ~/.omo/agent/skills/
- Grill family installed to ~/.omo/agent/skills/
- learning-course SKILL.md modified (Step 6 → ulw-research + grill-me)
- Memory rules saved (QA tool only, grill auto-load, caveman ultra)
- Finished plans/notepads deleted from repo

### Must NOT have

- Changes to omo native paths (plans/, drafts/, ulw-research/, notepads/)
- External skills.sh catalog in backup
- Duplicate skills across harness-specific dirs
- Questions output as text (always QA tool)

## Verification strategy

- Test decision: tests-after for skill modifications (structural gates: skill loads, discovery picks it up)
- Evidence: skill file exists at target path, `ls ~/.omo/agent/skills/` shows installed skills
- Manual verify: invoke ulw-plan, confirm grill-me loads; invoke caveman, confirm ultra mode

## Execution strategy

### Parallel execution waves

- Wave 1 (todos 1-3): Install skills to ~/.omo/agent/skills/ (caveman, grill family)
- Wave 2 (todos 4-6): Restructure repo (unified skills/, remove external, delete finished plans/notepads)
- Wave 3 (todos 7-8): Modify learning-course SKILL.md (Step 6 → ulw-research + grill-me)
- Wave 4 (todos 9-10): Update project rules (CLAUDE.md/AGENTS.md)
- Final wave F1-F3: Verify installations, repo structure, skill behavior

### Dependency matrix

| Todo | Depends on | Blocks |
| ---- | ---------- | ------ |
| 1    | -          | 4,5    |
| 2    | -          | 4,5    |
| 3    | 1,2        | 5      |
| 4    | 1,2,3      | 7      |
| 5    | 1,2,3      | 7      |
| 6    | -          | 7      |

      (todo 6 deletes all 5 plans + 3 notepads; omo/plans/ and omo/notepads/ end empty)

| 7 | 4,5,6 | 9 |
| 8 | - | 9 |
| 9 | 7,8,11 | F1-F3 |
| 10 | - | F1-F3 |
| 11 | - | 9 |

> CRITICAL ORDERING: todo 5 (delete agents/skills/) MUST run AFTER todos 1-2 (install caveman + grill family FROM agents/skills/). Deleting first destroys the source.

### Reversibility of destructive steps

| Step | Destroys                       | Recovery                                              |
| ---- | ------------------------------ | ----------------------------------------------------- |
| 4    | opencode/skills/ (21 external) | `git checkout -- opencode/skills` or `npx skills add` |
| 5    | agents/skills/ (170+ external) | `git checkout -- agents/skills` or `npx skills add`   |
| 6    | 3 plans + 3 notepads           | `git checkout -- omo/plans omo/notepads`              |
| 8    | 2 deprecated skills            | `git checkout -- claude/skills`                       |

All destructive work happens on a git-tracked tree; the pre-change commit is the restore point. Take one commit before Wave 2 and record its SHA in the run log.

## Todos

- [ ] 1. Install caveman to ~/.omo/agent/skills/caveman/
      What to do: Create ~/.omo/agent/skills/ (VERIFIED MISSING on disk) then copy agents/skills/caveman/ into it.
      References: C:/Users/Lance/agents-config/agents/skills/caveman/SKILL.md (VERIFIED EXISTS)
      Acceptance: File exists at ~/.omo/agent/skills/caveman/SKILL.md
      QA: `ls ~/.omo/agent/skills/caveman/` shows SKILL.md
      Commit: N (runtime install, not repo change)
      Recommended task executor category: quick

- [ ] 2. Install grill family to ~/.omo/agent/skills/
      What to do: Copy grill-me, grill-with-docs, grilling, domain-modeling from agents/skills/ to ~/.omo/agent/skills/
      References: C:/Users/Lance/agents-config/agents/skills/grill-me/, grill-with-docs/, grilling/, domain-modeling/
      Acceptance: All four dirs exist at ~/.omo/agent/skills/ with SKILL.md
      QA: `ls ~/.omo/agent/skills/` shows grill-me, grill-with-docs, grilling, domain-modeling
      Commit: N
      Recommended task executor category: quick

- [ ] 3. Verify skill discovery
      What to do: Confirm omo loads skills from ~/.omo/agent/skills/. Facts: OMO_CODING_AGENT_DIR=C:/Users/Lance/.omo/agent; ~/.omo/agent/skills/ did not exist before todo 1.
      References: memory fact "Global user-skills root: ~/.omo/agent/skills/<skill-name>/SKILL.md"; OMO_CODING_AGENT_DIR value
      Acceptance: caveman appears in a fresh agent turn's available-skills list, OR a written statement of the exact discovery mechanism
      QA: run a fresh agent turn and grep its skills list for `caveman`; capture the list or the mechanism note
      Commit: N
      Recommended task executor category: unspecified-low

- [ ] 4. Create unified skills/ dir in repo
      What to do: Create skills/ at repo root. Move the 6 user-authored skills from claude/skills/ into it: arr-api-reference, deep-cut-classical, gh, github-create, learning-course, shell-gotchas.
      VERIFIED FACT: claude/skills/ holds exactly 8 dirs — the 6 above plus rigorous-research and web-data-apis (deprecated; todo 8 deletes them).
      VERIFIED FACT: opencode/skills/ holds NO user-authored skills — all 21 entries (answers, bx, bx-search, cavecrew, caveman*, gh, images-search, llm-context, local-*, news-search, spellcheck, suggest, videos-search, web-search) are externally installed. Do NOT merge them; delete the whole dir (its `gh` duplicate is already kept from claude/skills/).
      References: C:/Users/Lance/agents-config/claude/skills/, opencode/skills/
      Acceptance: skills/ dir exists with exactly 6 user-authored skills; opencode/skills/ removed
      QA: `ls skills/` shows exactly 6; `test -d opencode/skills` returns false
      Commit: Y
      Recommended task executor category: quick

- [ ] 5. Remove external skills from agents/skills/ [BLOCKED BY TODOS 1-3]
      What to do: Delete entire agents/skills/ directory (170+ external skills.sh skills). They can be reinstalled via npx skills add when needed.
      PRE-CONDITION: todos 1-2 done and verified — caveman + grill family sources live INSIDE agents/skills/ and are destroyed if this runs first.
      References: C:/Users/Lance/agents-config/agents/skills/
      Acceptance: agents/skills/ removed; ~/.omo/agent/skills/ still holds all 5 installed skills
      QA: `test -d agents/skills/` returns false AND `ls ~/.omo/agent/skills/` shows 5 skills
      Commit: Y
      Recommended task executor category: quick

- [ ] 6. Delete all 5 plans and 3 notepads (omo/plans/ and omo/notepads/ end empty)
      What to do: Delete these 5 plan files and 3 notepad dirs:
      PLANS (3 finished): omo/plans/topgrade-autonomy.md, omo/plans/mcp-wireup-firecrawl-tavily-mslearn.md, omo/plans/haven-psmux.md
      PLANS (2 removed from scope by user decision): omo/plans/mcp-startup-optimization.md ("Ignore MCP startup"), omo/plans/lesson-stencil.md ("Ignore W5 entirely purge it")
      NOTEPADS: omo/notepads/topgrade-autonomy/, omo/notepads/mcp-wireup-firecrawl-tavily-mslearn/, omo/notepads/lsp-fresh-audit-fix/
      DO NOT touch omo/ulw-research/ or omo/teach/ (omo native paths stay as-is per constraint 2).
      References: audit findings (3 finished, verified [x]); user decisions "Ignore MCP startup" + "Ignore W5 entirely purge it"; direct answer "Delete both files"
      Acceptance: omo/plans/ is EMPTY and omo/notepads/ is EMPTY
      QA: `ls omo/plans/` prints nothing AND `ls omo/notepads/` prints nothing
      Commit: Y
      Recommended task executor category: quick

- [ ] 7. Modify learning-course Step 6 + purge its rigorous-research/web-data-apis deps
      What to do: Edit skills/learning-course/SKILL.md (post-todo-4 path). THREE edits, not one:
      (a) Step 6: replace the rigorous-research fan-out with a ulw-research invocation: `task({load_skills: ['ulw-research', 'grill-me'], prompt: 'Grill this research brief first, then run exhaustive research on these claims: [list]...'})`; output lands in `<workspace>/research/chNN/`.
      (b) "## API key failover — pointer only" section (near the end, points at web-data-apis's switch_api_key.py): rewrite to state rotation is handled inside ulw-research, or delete the section.
      (c) Bundled-resources / prose mentions of `rigorous-research`: remove every one, else todo 8 breaks a dangling reference.
      References: skills/learning-course/SKILL.md (Step 6, "API key failover" section, Bundled resources list)
      Acceptance: `rg -n "rigorous-research|web-data-apis" skills/learning-course/SKILL.md` returns ZERO hits; `rg -n "ulw-research" skills/learning-course/SKILL.md` hits Step 6
      QA: rg for the deprecated names comes back empty AND the ulw-research hit is present
      Commit: Y
      Recommended task executor category: unspecified-high

- [ ] 8. Deprecate rigorous-research and web-data-apis
      What to do: Delete claude/skills/rigorous-research/ and claude/skills/web-data-apis/ — todo 4 did NOT move them, so they still sit under claude/skills/. Delete from there.
      References: C:/Users/Lance/agents-config/claude/skills/ (VERIFIED: 8 dirs; todo 4 moves 6, leaving these 2)
      Acceptance: both dirs removed
      QA: `test -d claude/skills/rigorous-research` returns false AND `test -d claude/skills/web-data-apis` returns false
      Commit: Y
      Recommended task executor category: quick

- [ ] 11. Confirm IS-6 (GitHub Pages publish) needs no change
      What to do: Verify learning-course Step 8 already publishes to Bearmancer GitHub Pages via publish_teach.py. If yes, record IS-6 as satisfied by existing behavior and stop — do NOT redirect omo's native teach path (explicit user decision: "only alter our skill output"). If Step 8 does not already target GitHub Pages, append the missing publish step.
      References: skills/learning-course/SKILL.md Step 8; omo/teach/AGENTS.md publish contract
      Acceptance: a written finding: either "IS-6 already satisfied at Step 8" or the appended step text
      QA: quote the Step 8 publish line in the finding
      Commit: N
      Recommended task executor category: quick

- [ ] 9. Update CLAUDE.md and AGENTS.md with new rules
      What to do: Add to project rules: (1) "NEVER output questions as text. ONLY use ask_user_question tool." (2) "When invoking ulw-plan/ulw-research/ulw, auto-load grill-me with docs." (3) "Caveman ultra mode global always-on."
      References: Memory boundaries.md, facts/2026-09.md
      Acceptance: Rules present in CLAUDE.md and AGENTS.md
      QA: `rg "ask_user_question" CLAUDE.md` hits
      Commit: Y
      Recommended task executor category: quick

- [ ] 10. Update README.md with new schema
      What to do: Edit repo README.md to reflect unified skills-first schema. Remove references to claude/skills/, opencode/skills/, agents/skills/. Document new skills/ dir.
      References: Current README.md
      Acceptance: README reflects new structure
      QA: `rg "skills/" README.md` shows unified dir
      Commit: Y
      Recommended task executor category: quick

## Final verification wave

- [ ] F1. Verify skill installations
      What to do: `ls ~/.omo/agent/skills/` shows caveman, grill-me, grill-with-docs, grilling, domain-modeling
      Evidence: ls output
      Recommended task executor category: unspecified-high

- [ ] F2. Verify repo structure
      What to do: `ls skills/` shows 6 user-authored skills. `test -d agents/skills/` fails. `ls omo/plans/` shows only unfinished plans.
      Evidence: ls outputs
      Recommended task executor category: unspecified-high

- [ ] F3. Verify skill behavior
      What to do: Invoke ulw-plan or ulw-research, confirm grill-me loads. Check learning-course Step 6 text.
      Evidence: Skill invocation output, rg hits
      Recommended task executor category: unspecified-high

## Commit strategy

- One commit per wave: (1) install skills (not committed, runtime), (2) restructure repo, (3) modify learning-course, (4) update rules
- Conventional commits: feat(skills): unified schema, chore: remove external skills, docs: update README

## Success criteria

- C1: ~/.omo/agent/skills/ contains caveman + grill family (5 skills)
- C2: Repo has unified skills/ dir with 6 user-authored skills
- C3: agents/skills/ removed (no external backup)
- C4: omo/plans/ and omo/notepads/ both empty (5 plans + 3 notepads deleted, incl. the 2 scope-removed plans)
- C5: learning-course Step 6 invokes ulw-research + grill-me
- C6: Project rules include QA tool, grill auto-load, caveman ultra
- C7: README reflects new schema
- C8: IS-6 resolved — learning-course Step 8 publish target confirmed (already GitHub Pages) or the missing step appended (todo 11)

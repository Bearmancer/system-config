# Why OmO "invoked" ulw-research without its scaffolding (2026-09-30)

Refs system-config#58 (map #55).

## Question

In the user's most recent OmO run asking about OMC features (2026-09-30), why and how was `ulw-research` invoked, and why was its usual scaffolding (todo/plan structure) missing?

## Answer in short

- `ulw-research` was never invoked as a skill in that run. The model only opened its `SKILL.md` with the ordinary `read` tool, once, at 04:24:51Z. There was no skill expansion, no pointer message, no `ULW-RESEARCH MODE ENABLED!` line, no team, and no `.omo/ulw-research/` directory.
- No keyword hook fired. The prompt never contained `ulw`; the run was started by the `deep-research` skill.
- The model chose the read itself while surveying OmO. It read "OMO" as the omo-ai/senpi plugin and was hunting for "goal methods". Its answer then listed `ulw-research` as an OMO-senpi skill, and the user corrected it: "im aaking omc alone not omo".
- The scaffolding the user expected belongs to the skill's own workflow. That workflow only runs after a model follows the skill, and here nothing followed it.
- Todo scaffolding did appear in the first two turns (forced init, then a model-made init). It is absent from the later OMC-only follow-up turns. The first-turn todo hook fires once per session and the model made no further `todo` calls.

Times are UTC as logged; local time (IST) is +5:30.

## Which run

- Session file: `C:\Users\Lance\.omo\agent\sessions\--C--Users-Lance--\2026-09-30T03-17-56-315Z_01a0f051-9fda-78d8-8c7c-9db98697c6d8.jsonl`. Line 2 gives the model: `opencode-go/muse-spark-1.3-contributor`.
- Line 80 (04:22:02Z), user turn: `The user explicitly invoked the "deep-research" skill ...` then `<user-request>Explain OMO separation of concerns - ... b. what is diff of autopilot vs launch vs execute vs dry dock ...`.
- Line 155 (04:39:09Z): `im aaking omc alone not omo`. Lines 176 to 199: follow-ups on OMC `launch`, `harbor`, `drydock`. Lines 209 and 213 (05:26 to 05:27Z): an OMC PR/issue approach and 20+ todos.
- Rejected candidates: session `01a0f0cc` (deep-research on newspaper sites) and `01a0f0f0` (purge audit; zero `ulw` matches, OMC only as audit subject).

## Evidence: ulw-research was read, not invoked

Line numbers are JSONL lines in the session file above.

- Line 93 (04:23:37Z): a grep for `autopilot|dry.?dock|ulw-execute|ulw-plan` over `node_modules/omo-ai/plugin`, plus a listing of its `skills` tree.
- Line 95 (04:23:37Z): five parallel `read` calls on `ulw-plan`, `ulw-execute`, `ultrawork`, `mass-ulw`, `ulw-loop` `SKILL.md`.
- Line 115 (04:24:51Z), the only touch: `CALL read {"path": "C:\\Users\\Lance\\node_modules\\omo-ai\\plugin\\skills\\ulw-research\\SKILL.md"}`, batched with reads of `.agents\skills\gh`, `github-create` and `.omo\agent\AGENTS.md`. Its thinking text: "Checking available skills and their locations to locate the github-create and gh skill sources."
- Line 118: the tool result, frontmatter `name: ulw-research`, truncated at 388 of 429 lines.
- Line 147 (04:27:24Z), final answer: `ulw-research (team-first saturation with claim graph and debate)` listed under "OMO-senpi skills".
- Custom-message census of the whole session (`grep -o '"customType":"..."'` counted): 0 `skill-pointer`, 0 `ultrawork:directive`, 1 `senpi.todo-first-turn`, 7 `senpi.todo-state`. An invocation would leave a pointer `custom_message` or a user turn starting `The user explicitly invoked the "ulw-research"`; neither exists.
- Filesystem: `C:\Users\Lance\.omo` holds `agent cache drafts lsp-daemon memory plans senpi-task teach thread-tools`. There is no `ulw-research` directory and `plans` is empty. The skill's own step creates it: `mkdir -p .omo/ulw-research/$(date +%Y%m%d-%H%M%S)` (text of `ulw-research/SKILL.md`, seen at line 118).
- The memory recall sidecar for this session (`C:\Users\Lance\.omo\memory\agents\lance-80b35f83\runtime\recall\sidecars\MDFhMGYwNTEtOWZkYS03OGQ4LThjN2MtOWRiOTg2OTdjNmQ4\2026-09-30T04-23-09-287Z_01a0f08d-54e7-7b01-be43-fcffa3a8a068.jsonl`, lines 9 and 11) answered `No nudge` both times, so it did not steer the model to the skill.

## Trigger code: what would fire, and why it did not

1. Keyword pointer hook, `C:\Users\Lance\node_modules\omo-ai\plugin\extensions\omo.js`, line 2 (minified, so column offsets):
   - Col 1196466, table entry: `{skillName:"ulw-research",customType:"omo-ulw-research:skill-pointer",pattern:new RegExp(String.raw`\b(?:ulw|${Mne})[\s-]*research\b`,"i"),...,instruction:"orchestrate team-first maximum-saturation research",companions:[jne]}`. `Mne` matches `mass-ulw|ulw-mass|mulw|meth`; the `Nne` table starts at col 1195046.
   - Just after it, handler `Rne()` ("skill-pointers") tests each pattern against the text of an interactive `input` event (code fences, inline code and existing pointer blocks blanked first by `Tne`). It then sends a hidden `custom_message` built by `Dne()`: `This message mentions ulw-research. If the user of this session is asking to run ulw-research, read the ulw-research skill at ... with the read tool and follow it ...`.
   - It is a pointer only. It tells the model to read the skill; it does not expand the skill.
   - Not fired here: the user text `Explain OMO separation of concerns ...` and the `deep-research` token contain no `ulw ... research`, and `deep-research` does not match `\b(?:ulw|...)[\s-]*research\b`. The census above shows no `omo-ulw-research:skill-pointer` message.
2. Explicit skill expansion, `C:\Users\Lance\.omo\agent\runtime\594829a1ea03ebaf-d636bf28d153\dist\bundle\chunks\chunk-63QHOG5A.js`:
   - Line 2587, `_expandSkillCommand`: parses skill tokens (`parseSkillInvocationTokens`, known skill names only), reads the skill file, calls `formatSkillInvocationPrompt` (defined line 2571; template on line 2559), which writes `The user explicitly invoked the "<name>" skill. Follow the instructions in <skill-instruction> as binding ...`.
   - This produced line 80 for `deep-research`. It never produced one for `ulw-research` in this session.
3. First-turn todo hook, same chunk, line 2237: `FIRST_TURN_CUSTOM_TYPE="senpi.todo-first-turn"`, reminder text `This is the first request of the session. Before continuing, call the todo tool with op "init" ...`. `shouldArmFirstTurn` is on the same line. `session-worker.js` line 3784 holds `withForcedTodoChoice`, which forces `tool_choice` to `todo` when the model API supports it. This is why a `todo` init shows up on the first turn of a session.
4. Tip text only: `chunk-2POUJCWM.js` line 2, col 17617, `Trigger "ulw-research" for a saturating, citation-backed investigation ...`. It is UI tip copy, not a trigger.

## Why the model read it anyway

- Line 80 asked about "OMO" (typed OMO, meant OMC per line 155). With `.omo/plans` empty, the model searched `omo-ai/plugin` (line 93) and read the whole `ulw-*` family as "goal methods" (lines 95 and 115).
- No log line records a decision to run the skill. The read is a discovery read, batched with unrelated files.
- The skill's own Activation text says a bare question is not activation and to only "mention that `ulw-research` is available" (line 118). The model behaved accordingly.

## Scaffolding: expected versus seen

Expected had the skill run (its text, line 118): first reply line `ULW-RESEARCH MODE ENABLED!`, an `<analysis>` block, `.omo/ulw-research/<ts>/brief.md`, `team_create` with axis owners and a skeptic, a claim graph, a deliverable interview.

Seen in this session:

- None of those. No `team_create` call appears.
- Todo, first turn: `logs/session.log` line 92, `{"ts":"2026-09-30T04:22:02.888Z","level":"info","event":"todo_first_turn","mode":"forced"}`; session line 82, `CALL todo {"op":"init",...}` with 6 items; line 83 `senpi.todo-state`; closed at lines 138 to 145.
- Todo, correction turn: line 156 (04:39:22Z), a second `todo init` with 3 items, closed at lines 165 to 169.
- No todo in the later OMC turns: lines 176 to 199 (04:41 to 04:44Z) and 209 to 214 (05:26 to 05:27Z). `logs/session.log` records `todo_owed_backstop_suppressed` with reason `no-open-tasks` at 04:27:24, 04:40:16, 04:42:19 and 05:27:38, and `non-interactive` at 04:42:15. The backstop stays silent when no tasks are open, and the first-turn reminder covers the first request only.

## Comparison with earlier runs

No local session ever ran the full ulw-research scaffolding. Across all sessions in `--C--Users-Lance--` there is no `team_create` tool call, and the `mkdir -p .omo/ulw-research` string appears only inside the skill text that was read.

- Sep 27 `2026-09-27T06-40-13-516Z_01a0e197-becc-722c-958e-6b635e9436c8.jsonl` (07:15Z, user text contained `ulw-research`): the pointer hook fired. Line 172 `omo-ultrawork:directive`, line 173 `omo-ulw-research:skill-pointer` (text quoted above), line 174 `omo-ultimate-browsing:skill-pointer`, line 177 first reply line `ULTRAWORK MODE ENABLED!`. The model then made a partial read (line 183, `ulw-research/SKILL.md offset 1 limit 100`) and answered from analysis (line 186). No `ULW-RESEARCH MODE ENABLED!`, no team, no brief. Differences from Sep 30: the hook fired, an ultrawork banner appeared, and an `ultimate-browsing` companion pointer appeared.
- Sep 27 `2026-09-27T06-17-48-714Z_01a0e183-39a9-7b36-bdf3-3552b7400175.jsonl` (06:35Z): line 71 is a real skill expansion, `The user explicitly invoked the "ulw-research" skill`, with `<user-request> Yeah this is abject recurrent fialure - rethink entire methodology`. Line 72 answers in prose and writes a memory note; no banner, no brief, no team. The skill body was injected and still not followed. The self-note at line 96 records `invoked ultrawork/mass-ulw/review-work/ulw-research protocols without confirming the ask`.
- Todo scaffolding on first turns: `logs/session.log` lines 2 and 22 (Sep 27), 86 and 92 (Sep 29 to 30) are `todo_first_turn` with `mode:"forced"`; line 104 (05:34:11Z, a different session) is `mode:"reminder-only"`.
- Conclusion: wherever a todo/plan structure appeared, it came from the first-turn todo hook, not from ulw-research. The ulw-research-specific structure (banner, brief, team) has no local example of appearing. The closest cases are runs where the pointer fired or the skill body was injected and the model still did not follow it. A Sep 20 bundle `omo/ulw-research/20260920-042352/REPORT.md` is listed in `01a0e197` line 85, but `C:\Users\Lance\agents-config\omo\ulw-research` does not exist on this machine now, so it could not be inspected.

## Unverified

- Why the model read `ulw-research` at line 115: inferred from its one-line thinking and the batch it sat in. No log states the decision.
- Whether the Sep 27 `01a0e183` line 71 expansion came from `$ulw-research`, `/skill:ulw-research` or plain text: only the already-expanded block is stored.
- Whether `C:\Users\Lance\node_modules\omo-ai\plugin\extensions\omo.js` is loaded by runtime `594829a1ea03ebaf-d636bf28d153`. The string `skill-pointer` is absent from that runtime's `dist`, and the plugin lives outside `.omo\agent\runtime\`. The pointer messages in the Sep 27 sessions match this file's strings, which is indirect evidence only.
- What the user meant by "missing scaffolding". This note maps it to the ulw-research artifacts and to the todo list; the user did not specify.
- The exact rule that produced no todo init in the 05:26 and 05:27Z turns: only the `no-open-tasks` backstop reason and the first-request wording of the reminder are recorded. `shouldArmFirstTurn` was not read beyond its signature.
- `C:\Users\Lance\.local\share\opencode\log\` and `storage\` were listed, not searched; they belong to the older `oh-my-opencode-slim` plugin. `OmO-debug.log` (all lines) and `logs/session.log` were read; neither holds a skill-invocation line for this run.

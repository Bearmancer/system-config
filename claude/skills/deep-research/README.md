# deep-research: how this skill is built

A human-facing guide. Agents load `SKILL.md`, not this file.

## One skill for every research ask

| You say | What happens |
|---|---|
| "How true is it Putin is fucked?", "is it true that X" | **Answer mode.** The question is split into measurable axes and each is checked with sources internally. The reply is cited explanatory prose that opens with the direct answer, with no per-claim table. |
| "Fact-check this", "only fact check", "verify these claims" | **Verdict mode**, only on an explicit fact-check-only request. The reply opens with a bottom line and then the claims grouped as verified (full or partial), unverified, and false. |
| "<video url> - explain", or naming a book, article or paper | **Course mode.** The source is fetched and split into chapters, each chapter becomes a verified treatise page, and the course is published to GitHub Pages. |
| "Teach me the Thirty Years' War" | **Course mode, topic variant.** A chapter list is researched first and you approve it before anything is built. |
| "Soviet symphonies from early 20th century" | **Recommend mode** (classical only). Returns verified deep-cut picks with timings, skipping the ban list. |
| "How do I play Ark Nova, 4 players" | **Board-game mode.** Quick tier. Reads the publisher rulebook, FAQ and errata first, then BGG files and forums (public pages only, no login). Publishes one short rules page: theme, goal, turn, actions, one easy strategy, easiest scoring path, and the stated player count. |
| "Grab this page" | **Fast path.** Picks the right scraper, climbs the bot-block chain if needed, and stops. |

## Layout

```
deep-research/
  SKILL.md              router + rules every mode needs (loaded on trigger)
  README.md             this file (never loaded by agents)
  references/
    fleet.md            routing: need -> vendor, capability map, bot-block chain, POST scripts
    scrapers/           one file per vendor (MCP tools, CLI, REST presets), browser.md, keys-errors.md
    modes/course.md     course steps 0-9 and page standards
    course/             course detail: workflow, page design, schema, diagrams, publishing, source adapters
    domains/
      general/          non-music source order + bans
      music/
        rules.md        shared by every genre: streaming ban, discography method, timing rules
        classical/      sources, exclusions (ban list), recommend (pick format)
        popular/        sources, exclusions
  scripts/              run, not read: fetch, slice, stamp, gate, publish, URL audit, key rotation, vendor REST presets (vendor_request.py + exa/firecrawl/brightdata/browserbase/scrapegraph scripts)
  assets/               page shell: lesson.css, stencil, shell.js
  evals/                test prompts and fixtures
```

## How one skill holds a big, complex structure

A skill can carry a lot of material because it loads in layers:

1. **Description**: about 100 words, always in context. Its only job is to make the skill trigger.
2. **SKILL.md**: loaded when the skill triggers. It holds the router and the rules every mode shares.
3. **Reference files**: read only when a step needs them. Course mode never loads the classical ban list, and a quick fact-check never loads the course page rules.
4. **Scripts**: executed, never read into context, so they cost nothing no matter how long they are.

A single "dump" skill with everything in SKILL.md would load every branch on every run. Attention spreads thin and rules get skipped.

## Pointer hops

A **hop** is one "go read file X" instruction the agent has to follow.

- 0 hops: text inside SKILL.md.
- 1 hop: SKILL.md names `references/fleet.md`, and the agent reads it.
- 2 hops: that file names another file, and the agent has to follow again.

Each hop is a decision the model can skip, or half-do. Anthropic's skill guide warns that Claude may only preview files reached through nested references (for example with `head -100`), and it asks for references kept one level deep from SKILL.md (platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices, "Avoid deeply nested references").

What counts is **hops, not folder depth**. `references/domains/music/classical/exclusions.md` sits 4 folders down but is 1 hop away, because SKILL.md names it directly. The rules this skill follows:

- Every reference file is named in SKILL.md, so it is one hop away.
- A reference file may mention another file only as a cross-check. It never depends on it for content.
- Folders nest only where siblings share material. `music/rules.md` sits above `classical/` and `popular/` because both use it. Otherwise the tree stays flat.

## Why not wrapper skills

A wrapper skill ("classical-recs, which loads deep-research") adds a hop *between skills*. Loading a second skill is the model's choice, like any hop. Anthropic's skill-creator notes that Claude tends to undertrigger skills, so every extra skill in a chain is one more chance to skip. Wrappers are worth it only when each skill triggers on its own from different phrases. Here the four old skills shared triggers and rules, so they merged into this one.

No published source ranks wrappers against nesting. That ranking is inferred from the two documented facts above.

## Single homes

Each shared rule lives in one place, and other skills point to it:

- The URL audit and API key failover live in `SKILL.md`. github-create, shell-gotchas and arr-api-reference point here.
- The streaming ban lives in `references/domains/music/rules.md`.
- Temp clones, codegraph and question discipline live in `~/.claude/CLAUDE.md`.

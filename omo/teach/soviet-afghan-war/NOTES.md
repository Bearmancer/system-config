# Notes — course map, authoring contract, palette, and status

## User preferences & observed workflow (carried over from the other teach workspaces)

- Chat terse; **substantial teaching content lives in workspace HTML**, never in chat replies. Chat carries status and pointers only.
- Explanations authored as **HTML** (`lessons/*.html`, `reference/*.html`), never as `.md`. Markdown only for admin (MISSION / NOTES / RESOURCES / learning-records).
- Every chapter gets a **full treatise**, never a summary. Course is walked sequentially; a chapter may lean on the ones before it.
- **Optionality (anti-OCD):** every chapter carries a "what matters / what you can skip" block; NOTES marks chapters essential vs skippable; chat states plainly when a standard step was skipped.
- **Method transparency:** the user asks _how_ something was found, so every chapter carries a method box and every date/figure carries its provenance.
- **Source skepticism:** documented fact and contested reading stay visibly separate; nothing is smoothed.
- **Auto-open:** after writing or updating a page, open it (`Start-Process`, default handler).
- **Publishing:** teaching HTML publishes to https://bearmancer.github.io/ via `~/.omo/scripts/publish-teach.ps1`.

## Course map (no source to slice — this course's own structure, decided at build time)

Because the user asked one integrated question rather than supplying a chaptered source, the course is built around the three parts of that question. Boundaries are periods, not source chapters.

| # | Lesson file                            | Title                                                                                                           | Period                   | Essential?                                                |
| - | -------------------------------------- | --------------------------------------------------------------------------------------------------------------- | ------------------------ | --------------------------------------------------------- |
| 1 | `lessons/01-ch1-road-to-invasion.html` | The neighbour: how the Soviet-Afghan connection was built, and how the December 1979 decision was actually made | 1919 — Dec 1979          | **yes** — this is the "suddenly" the user is asking about |
| 2 | `lessons/02-ch2-ten-years.html`        | The ten years, part one: why Moscow could not win                                                               | Dec 1979 — 1985          | **yes**                                                   |
| 3 | `lessons/03-ch3-exit.html`             | The ten years, part two: why leaving took four more years, and what the withdrawal left behind                  | 1985 — Feb 1989 (+ coda) | **yes** — answers "why ten years"                         |

All three are essential for this mission; there is no skippable chapter. If the course grows later, extensions in the obvious direction are: the PDPA and the 1978 Saur revolution as its own chapter; the mujahideen parties and the Pakistan pipeline as its own chapter; the Soviet home front and the "Afgantsy". None of those are written yet and none should be pre-built.

## Authoring contract (every lesson)

Section order (numbered `<h2>` — the checker requires `<h2>N. …` for any numbered heading):

1. What this chapter does — the chapter's argument in one paragraph.
2. **Cast block** + **chapter-scoped relationship subgraph** (SVG) — see below.
3. **What matters — and what you can skip**.
4. The narrative — with blockquotes for primary-source quotations (translate Russian/Persian quotations; quote the English translation and name the edition).
5. The machinery — the structural mechanism the chapter establishes.
6. **The record** — the fact-check box: claim → documented / contested / unfindable, each with source + short quote. Contested readings are the replacement for "source says / record shows" in this course.
7. Open threads — what the period itself leaves unresolved at the boundary.
8. Retrieval check — exactly 3 quizzes.
9. Method box — how boundaries, dates and checks were derived.
10. Primary documents & next steps; footer.

A **boundary box** near the top must literally contain the phrase `covers chapter N only` — the gate script looks for it.

### Quiz contract (enforced by `scripts/check_lesson.py`)

```html
<div class="quiz">
  <p class="quiz-q">Question text.</p>
  <button class="quiz-option" data-correct="false">option text</button>
  <button class="quiz-option" data-correct="false">option text</button>
  <button class="quiz-option" data-correct="true">option text</button>
  <p class="quiz-explanation" hidden>Shown after the first click.</p>
</div>
```

Every option in one quiz must have **exactly the same word count**; exactly one option carries `data-correct="true"`; at least 3 quizzes, at least 3 options each. No formatting tells.

### Links and assets

Each lesson links `../assets/lesson.css`, `../assets/quiz.js`, and (once they exist) `../reference/glossary.html`, `../reference/cast-map.html`, `../reference/timeline.html`, plus `../index.html`. The gate fails on any dangling link, so a lesson that ships before the reference pages exist must either wait for them or link only to what exists. **All three reference pages are built in the same pass as the lessons**, so link all of them.

## Palette — workspace-stable, do not change meanings

Rule: colour is the **only** line difference (all edges solid, ~2.2 px, colour-matched arrowhead, never dashed/dotted, never varied by thickness). One colour = one concern. These meanings hold across every chapter subgraph and the cumulative cast map.

| Key     | Colour    | Meaning                                                                 | Arrowhead id |
| ------- | --------- | ----------------------------------------------------------------------- | ------------ |
| armed   | `#b3261e` | Armed force — who is fighting whom                                      | `ah-armed`   |
| command | `#1a7f37` | Command and control — orders, appointments, direct subordination        | `ah-command` |
| supply  | `#1f5fa8` | Patronage and supply — money, arms, training, sanctuary                 | `ah-supply`  |
| faction | `#7a3fa0` | Party faction or ideological alignment                                  | `ah-faction` |
| treaty  | `#c07a00` | Diplomacy and agreement — treaties, accords, recognition                | `ah-treaty`  |
| covert  | `#0e7c7b` | Intelligence and covert action                                          | `ah-covert`  |
| kinship | `#6b4a1f` | Kinship, clan and personal loyalty                                      | `ah-kinship` |
| rivalry | `#6f6a60` | Rivalry or opposition short of war — purges, feuds, political hostility | `ah-rivalry` |

Node conventions: person = white fill `#ffffff`; organisation (PDPA, KGB, ISI, CIA, Politburo…) = cream `#f2efe4`; unknown identity = pale grey `#eceae2`. Border solid, `#c8c2b4` for group frames. Node label = name + one line of role, with `(chN)` for the chapter of introduction.

Chapter subgraph canvas ≈ 700–950 wide; the cumulative map ≈ `viewBox="0 0 1140 860"`. Both get `figure.map` wrapping and the `figure.map svg` CSS from `references/diagram-spec.md`.

## Canonical cast table (authoritative — all three lessons and the cast map must agree with this)

A person's `(chN)` tag and their cast row's third column must both match this table. Anything not in this table is not a node.

| Person          | First appears | Notes                                       |
| --------------- | ------------- | ------------------------------------------- |
| L. Brezhnev     | ch1           | General Secretary                           |
| Yu. Andropov    | ch1           | KGB chairman, later General Secretary (ch2) |
| D. Ustinov      | ch1           | Defence Minister                            |
| A. Gromyko      | ch1           | Foreign Minister                            |
| A. Kosygin      | ch1           | Premier; led the March 1979 refusal         |
| M. Daoud Khan   | ch1           | President 1973–78                           |
| N. M. Taraki    | ch1           | Khalq head of state                         |
| H. Amin         | ch1           | Ruler from Sep 1979                         |
| B. Karmal       | ch1           | Parcham; installed Dec 1979                 |
| J. Carter       | ch1           | Signed the 3 July 1979 finding              |
| Z. Brzezinski   | ch1           | US National Security Adviser                |
| Ismail Khan     | ch1           | Herat commander, March 1979                 |
| K. Chernenko    | ch2           | General Secretary 1984–85                   |
| M. Gorbachev    | ch2           | General Secretary from March 1985           |
| M. Zia-ul-Haq   | ch2           | Pakistan's ruler — **not** on stage in ch1  |
| R. Reagan       | ch2           | US President from 1981                      |
| A. S. Massoud   | ch2           | Panjshir commander                          |
| G. Hekmatyar    | ch2           | Hezb-e Islami                               |
| B. Rabbani      | ch2           | Jamiat-e Islami                             |
| Abdul Haq       | ch2           | Kabul and east commander                    |
| E. Shevardnadze | ch3           | Foreign minister from 1985                  |
| S. Akhromeyev   | ch3           | Chief of the General Staff                  |
| V. Varennikov   | ch3           | Operational group, Kabul                    |
| B. Gromov       | ch3           | 40th Army from 1987                         |
| M. Najibullah   | ch3           | Kabul ruler from 1986                       |
| J. Haqqani      | ch3           | Khost front commander                       |
| D. Cordovez     | ch3           | UN mediator                                 |

Organisation nodes (not cast rows; tag = the chapter whose subgraph first draws them): Politburo (ch2), 40th Army (ch2), Afghan Army / DRA forces (ch2), ISI (ch2), CIA (ch2).

**Verified absent.** W. Casey was briefly added to the cast map on the strength of a build agent's report, then removed: a grep across all three chapters returns **zero** mentions of him. He is not a player in this course, and the map is not allowed to promise ties the chapters never draw. **Rule for the future: before any name becomes a node, grep the three chapters for it.** The same grep confirms every other node is substantiated — Antonov/Varennikov 2 mentions in ch3, Gromov 8, Najibullah 21, Ismail Khan 3 in ch1, Abdul Haq 1 in ch2, Haqqani 3 in ch3.

**No duplicate relations.** The Soviet aid relationship is drawn once, Brezhnev to Taraki. A second, identically-labelled supply edge from Andropov to Taraki was removed: two edges with the same label joining the same pair is a claim drawn twice, not two claims.

## SVG rules beyond the shipped checker

`check_map_geometry.py` tests edges-through-boxes, box overlaps, merged arrowheads, and labels against boxes and lines. It does **not** test label-vs-label overprinting, labels clipped by the canvas, isolated nodes, or edges whose endpoints float in space unattached to any box. All four of those shipped defects in this workspace.

Run the extra probe on every SVG visual, alongside the shipped checker:

```
python "$HOME\.omo\scripts\check_svg_extra.py" <file.html>
```

It must print `OK` and exit 0. Rules it enforces, now binding here:

1. **No isolated nodes.** Every node in a diagram has at least one edge attached. If a cast member has no relation worth drawing, they belong in the cast table and the roster, not as a floating box.
2. **No dangling terminals.** Every edge endpoint sits on a node's border.
3. **No label collisions and no clipped labels.** Two labels never overlap; every label fits inside the viewBox.
4. **Edge endpoints must name the pair the chapter asserts.** A label is a claim about the two nodes it joins.

## Timeline seed (dates to verify, not to trust)

1919 Anglo-Afghan Treaty of Rawalpindi · 1921 Soviet-Afghan friendship treaty · 1929 Nadir Shah · 1955–56 Soviet arms/economic credits after Pakistan joins SEATO/CENTO · 1965 PDPA founded · 17 Jul 1973 Daoud coup · 27–28 Apr 1978 Saur revolution · Mar 1979 Herat mutiny · 14 Sep 1979 Taraki killed · 12–24 Dec 1979 Politburo decisions and the treaty request · 24–27 Dec 1979 airlift, Storm-333, Amin killed, Karmal installed · Jan 1980 Carter Doctrine, UN General Assembly resolution, Olympic boycott · 1982 Geneva proximity talks begin · 1985 Gorbachev; mujahideen seven-party alliance · 25 Feb 1986 "bleeding wound" · 4 May 1986 Najibullah replaces Karmal · Sep 1986 Stingers arrive · 14 Apr 1988 Geneva Accords signed · 15 May 1988 withdrawal begins · 15 Feb 1989 Gromov crosses the Friendship Bridge last · 1989 Soviet casualty total ~14,453 (verify).

## Verification recipe (this course's replacement for the source fan-out)

No creator-supplied claims exist to check. Instead:

1. Every date, figure, name and quotation that reaches a lesson is attributed to a listed source (document, archive, memoir, scholarship, or named press report).
2. Wiki sources are never sole support; where only a wiki-grade source exists, the entry is written down as contested or unfindable.
3. Contested claims (e.g. whether the US "induced" the invasion; whether the December decision was defensive; casualty totals) get both readings, attributed to whoever holds them.
4. Unfindable items go to `RESOURCES.md` **Gaps** and stay visible in the lesson.
5. Source chain for searches: Firecrawl → Tavily → Exa, escalating only when the previous returns empty or thin; Firefox DevTools MCP as the fallback for JS-heavy or login-walled pages.

## Gates (run on every changed artifact)

- `python "C:\Users\Lance\.claude\skills\learning-course\scripts\check_lesson.py" <lesson...>` → exit 0 (3+ quizzes, equal option word counts, exactly one correct, boundary wording `covers chapter N only`, fact-check wording, all links and assets resolve, no dangling section references).
- `python "C:\Users\Lance\.claude\skills\learning-course\scripts\check_map_geometry.py" <file.html>` → exit 0 for the cumulative cast map **and** every per-chapter subgraph.
- Screenshot pass on any changed visual (Edge headless, `--window-size="1500,2400"`), then look at the PNG.

### Cast-block delta rule (enforced — the chapters drifted on this without it)

Each cast row carries `id="cast-<slug>"` on the `<tr>`. The third column is **always** `first appears chN`:

- **Introduced in this chapter** → plain text `first appears chN`, full role line.
- **Introduced in an earlier chapter** → a link to that chapter's own row, `href="chK-<slug>.html#cast-<slug>"`, link text `first appears chK`, and only a one-line role line ("unchanged" or the role change). **Never** link a cast row to the reference cast map, and never leave the third column as just "returning".
- The `(chN)` tag on the same person's node in every diagram must agree with this column.

## Queue & status

- **2026-09-18 — workspace created.** Scaffold (MISSION, NOTES, RESOURCES, assets, course home) written. Three chapters built in parallel: ch1 (1919–Dec 1979), ch2 (Dec 1979–1985), ch3 (1985–Feb 1989 + coda). All three pass `check_lesson.py` and `check_map_geometry.py` exit 0.
- **Defect register (found in the screenshot pass — the mechanical gates cannot see any of these):**

  | #  | File           | Defect                                                                                                                                                                                                                                                                                                                   |
  | -- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
  | 1  | ch1 subgraph   | Green edge labelled "small-group decision" is drawn Andropov → Ustinov, which is not a relation the chapter asserts. It should run from the decision group to **Brezhnev** (the 8 December persuasion), relabelled.                                                                                                      |
  | 2  | ch1 subgraph   | The teal "shelters Karmal" edge starts at (425,110) — not on any node boundary, so it dangles in empty space. Must start on a node edge.                                                                                                                                                                                 |
  | 3  | ch1 subgraph   | Brezhnev, Kosygin, Daoud and (after fix 1) Ustinov end up with **no** edge. Every person in the cast block needs at least one honest relation drawn, or should not be in the diagram.                                                                                                                                    |
  | 4  | ch1 cast block | Third column holds a historical entry point ("September 1979, embracing Taraki in Moscow") instead of `first appears ch1`. Either relabel the column honestly or make it conform to the delta rule — and it must not contradict the diagram's `(ch1)` tags.                                                              |
  | 5  | ch2 subgraph   | Two labels overprint at the same coordinates: "commands" (318,240) and "Panjshir offensives" (320,240) — they render as one garbled string.                                                                                                                                                                              |
  | 6  | ch2 cast block | `href="01-ch1-road-to-invasion.html#cast-zia"` and `...#cast-carter` are **dangling** — chapter 1's cast block introduces neither Zia nor Carter. Fix by making chapter 1 introduce Carter (he is genuinely on stage in ch1 via the 3 July 1979 finding) and chapter 2 introduce Zia, or by retagging both in chapter 2. |
  | 7  | ch3 subgraph   | Two labels overprint: "siege by proxy" (250,300 anchor start) and "Geneva guarantee" (400,296 anchor end) — their glyph boxes overlap.                                                                                                                                                                                   |
  | 8  | ch3 subgraph   | Shevardnadze has no edge, though the chapter gives him the Geneva track as his active relation.                                                                                                                                                                                                                          |
  | 9  | ch3 cast block | Every row's third column is the bare word "returning", and every row links to `../reference/cast-map.html#cast-…` instead of back to the chapter that introduced the person. Violates the delta rule above.                                                                                                              |
  | 10 | ch3 subgraph   | `(ch2)` tags on Akhromeyev, Gromov and Najibullah do not match chapter 2's cast block, which introduces none of them. Retag to the chapter that actually introduces them.                                                                                                                                                |

- **Defect register — all ten cleared on 2026-09-18.** ch1's subgraph was rebuilt to twelve honest edges (every cast member now has at least one), ch2's and ch3's overprinted label pairs were separated, ch3's dangling Typhoon endpoint was attached and Shevardnadze given his Geneva edge, ch3's cast block was rewritten to the delta rule, ch2's Zia row and dangling anchors were corrected, and chapter 1 gained Carter and Ismail Khan as cast rows. The cast map was rebuilt: 32 nodes, every node wired, no dangling endpoints, `(chN)` tags aligned to the canonical table, the Andropov → Ustinov mis-relation corrected to the decision group persuading Brezhnev, and one duplicate supply edge removed.
- **Reference pages built:** `reference/timeline.html` (85 entries, four eras, each entry tagged with a kind and marked documented or contested), `reference/glossary.html` (five sections, 92 entries), `reference/cast-map.html` (32 nodes, full legend, roster, and a "context that is deliberately not drawn" section).
- **Gate status:** `check_lesson.py` exit 0 on all three chapters; `check_map_geometry.py` exit 0 on all four visuals; `check_svg_extra.py` OK on all four (0 label collisions, 0 clipped labels, 0 isolated nodes, 0 dangling terminals).
- **Next:** publish via `~/.omo/scripts/publish-teach.ps1` and probe the live URLs. If the course is extended, the natural chapters are the PDPA and the Saur revolution, the Pakistan pipeline and the mujahideen parties, and the Soviet home front.
- **2026-09-20 — all three lessons rebuilt to the revised page spec.** Head order is now kicker → H1 → surtitle (`Chapter N of 3 · period`) → meta line (`Lesson NN · Cast map · Glossary`); the surtitle carries the page's only timestamps. Cast tables are two columns (`Name | Role this chapter`); the "First appears" column and every "first appears" phrase are gone, and returning rows end in an absolute "(chapter N)" reference. Deleted outright: boundary boxes, both quiz sections with all quiz blocks and quiz.js script tags, both "ask your teacher" boxes, both method sections, and the "Primary documents and next steps" sections (their external URLs were folded into the record boxes as hyperlinks on the cited sources). Figcaptions now state colours with no links. Footers are course home + previous/next lesson + glossary with a `Workspace: soviet-afghan-war · Lesson NN · chapter N of 3` identity line. Long wrapper paragraphs were split to 1–3 sentences; all blockquotes, facts, dates, names, numbers, quotes, corrections, H2 numbering, SVG art, and cast anchor ids are unchanged. `assets/lesson.css` was replaced with the skill's canonical copy (surtitle rule, no quiz styles) and stale `assets/quiz.js` was deleted.
- **Link-budget decision (checker constraint).** The checker caps every link target at two uses per page (fragments stripped), so only one in-context hyperlink per lesson file is possible alongside the required footer prev/next link. The first returning cast row per target file keeps the full hyperlink (ch2 Brezhnev → ch1; ch3 Gorbachev → ch2; ch3 Karmal → ch1); the remaining returning rows carry a plain-text "(chapter N)" reference to the same anchors, which all still exist. If the checker ever counts fragments as distinct targets, restore hyperlinks to every returning row.
- **Gate status:** `check_lesson.py` exit 0 on all three lessons; `rg -i "quiz|teacher|boundar|first appears"` over lessons and CSS returns nothing; cross-lesson anchors verified (no dangling `#cast-…` targets). No new facts, no invented URLs (every hyperlink reuses a URL from RESOURCES.md or the old primary-documents sections), no chapter renumbering. Reference pages, index.html, transcripts, and learning-records untouched; no publish, no auto-open per instructions.

### Known gap in the geometry checker

`check_map_geometry.py` checks labels against boxes and against lines, but **not labels against each other**. Two labels can be drawn at the same point and the gate still exits 0 — which is exactly what happened in ch2 and ch3 (defects 5 and 7). The screenshot pass is the only gate that catches this class, so it is not optional for any changed visual. Worth adding a label-vs-label test to the checker if the user wants it.

## Environment quirks worth remembering

- The publish script derives the site label from `MISSION.md`'s first `#` heading, one row per workspace, linking to that workspace's `index.html`. Hand-authored `index.html` at the workspace root is used as the course home and suppresses the generated one — do **not** create `reference/index.html`, or it may be picked instead.
- Windows host: `pwsh` for scripts, `Start-Process` to open files. Python checkers are invoked with `python`.

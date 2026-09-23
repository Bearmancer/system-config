# Learning record 0001 — a course built from the record, and what the gates missed

**Status:** initial build complete, 2026-09-18.

## What was built and why

The user asked a question rather than supplying a source: *"Explain how Soviet is connected to Afghanistan, or why they warred for ten years, because it seems confusing how Russia suddenly decided Afghanistan."* There was no video and no book, so the `learning-course` pipeline ran without its usual spine. The replacement was a three-chapter course built directly from the documentary record — `soviet-afghan-war/` — with the user's own framing as the structure: chapter 1 answers the "suddenly" (1919 to Storm-333), chapter 2 the first half of the ten years (why Moscow could not win), chapter 3 the second half (why leaving took four more years).

Because there is no creator, there is no "what the source says / what the record shows" split. The discipline that replaced it, and which the user should hold future chapters to, is **documented fact versus contested reading**, kept apart in every chapter's fact-check box, with every load-bearing date and figure carrying its provenance.

## What the evidence says about the gates

All three chapters passed `check_lesson.py` and `check_map_geometry.py` on exit 0 while still containing defects that a reader would call obvious:

- two labels drawn at identical coordinates in ch2 and ch3, rendering as one garbled string;
- three nodes in ch1 with no edge at all, and an edge endpoint floating in empty space;
- on the cumulative map, **ten** isolated nodes, two dangling edges, one invented player (W. Casey, whom no chapter names), and a wrong relation carried over from ch1 (Andropov → Ustinov, standing for a decision the chapter attributes to the group's persuasion of Brezhnev).

The mechanical gates were not wrong; they were incomplete. `check_map_geometry.py` tests labels against boxes and against lines, but never labels against each other, never edges against the canvas bounds, never whether a node has any edge, and never whether an edge endpoint actually lands on a box. A throwaway probe (`check_svg_extra.py`, now kept at `~/.omo/scripts/`) added those four tests and found **all** of the above in one pass, on files that had just exited 0.

Implication for future sessions: when a gate exits 0, that means the gate's own defect classes are absent — nothing more. The screenshot pass is not decoration; it is the only thing that caught the garbled labels, and the probe exists because even the screenshot pass is easy to do carelessly.

## What the evidence says about sub-agent reports

Two reports were materially wrong about their own output. One claimed "both gates exit 0 with zero geometry warnings" on a chapter whose diagram had three label-on-line warnings and three isolated nodes. Another claimed to have "de-collided 4 label pairs" and that "legend and roster render cleanly" on a map that measured ten isolated nodes and two dangling edges. A third reported that a file had not been touched by it while the file had in fact changed under it during the run — and a sub-agent's *narrative* report listed cast members (Casey) that its own saved file did not contain.

Working rule confirmed: verify from the artifact, by running the gate yourself, and never let a claim into a reference page on a agent's say-so. The Casey node existed solely because one report asserted a cast member that a grep disproves.

## Working preferences reconfirmed

- Substantial teaching content goes into workspace HTML, never into chat; chat carries status and pointers.
- The user's colour rule is a hard rule: colour is the only line difference, and one colour means one concern workspace-wide. The palette chosen here is command / supply / armed / treaty / covert / faction / kinship / rivalry, and it held across all four diagrams.
- Optionality is expected at every level, including the level of process: this session reported plainly that no correction log exists, because there was no machine text to correct.

# Rules mode decisions

- Authority order for `true`: publisher rulebook, publisher rules/product page, publisher or designer FAQ, official errata (supersedes the printed rulebook; check version date), designer or publisher forum posts. Player-to-player posts are `interpretive`.
- A claim's effective rule follows the highest-precedence source. Superseded rulebook text is kept as contradicting evidence with the note "superseded by <errata, date>".
- Authoritative accounts per game (designer, publisher staff) are derived from the BGG credits and the publisher site, stored in the registry, and tagged `authority: designer` on sources.
- BGG: public pages and XML API only; never log in or handle cookies. Files behind login: the user supplies local PDFs; the driver accepts file paths as input.
- No-text-layer PDFs: local OCR plus vision reads under the visual-read rule (ADR 0012).
- Layouts for rules: concept page, table-first, decision tree, cheat sheet, picked by the agent from claim shape (ADR 0005).
- Default player count when unstated: 4, else the maximum (carried over).
- Strategy: every rules page carries one "easiest strategy" section (user choice). Its claims are `interpretive` with attributed sources and are labelled as such, never `true`.
- Scope: essentials only. Setup and endgame scoring are cut unless the strategy section needs them (carried over from the old board-game mode). Note: the live Ark Nova course later included them; the rules page stays short by design.

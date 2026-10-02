# Ticket reconcile and launch closeout (2026-09-30)

Status: executed. Map #2, #33, #37-#43, #45 and the follow-up issues #46, #48, #49 are closed.
Scope: Bearmancer/system-config map #2 and #33 with its splits. This plan is #33 step 6.

## ADR: follow-up structure after the map is met

- **Decision:** keep map #2 closed as the logbook, with Decisions lines for closed tickets only and one pointer line. Work split out of #33 becomes native sub-issues of #33 (`gh issue edit 33 --add-sub-issue`, `gh issue create --parent 33`). Follow-ups from outside #33 are standalone issues with the `Map: #2` header. Close #33 on its own evidence. Scripts for the POST-only gaps (#37-#43) stay independent until a 3rd would duplicate more than half of an existing one.
- **Drivers:** the signed destination is met and must not be amended silently; the frontier needs a census; overhead stays minimal for a solo captain.
- **Alternatives considered:**
  - Standalone issues with a header only: no census, parent links stay body text.
  - Reopen #2 with a vessel D: amends a met, signed destination.
  - A new map: needs a signature and a navigator pass for small work.
  - #33 as a permanent umbrella: fails the evidence-based close rule.
- **Consequences:** the frontier is #33's sub-issue list plus the `Map: #2` search, both named in the #2 pointer line; a census on a closed parent is expected. Body-text `Parent:`/`blockedBy:` lines give way to native links. Plan and record docs cited on the tracker are committed to master first and linked by blob URL. If follow-ups grow past about 12, or gain a shared destination, switch to a new map.

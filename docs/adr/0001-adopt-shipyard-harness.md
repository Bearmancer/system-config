# ADR-0001: Adopt Shipyard Harness

## Decision
Adopt the shipyard documentation harness (CLAUDE.md, CONTEXT.md, docs/adr/, docs/standards/, docs/business/) for this repo.

## Drivers
- No CONTEXT.md or docs/adr/ existed before this ADR — knowledge about what this repo actually is (a one-way config mirror, not application code) lived only in README.md prose and an open ask-navigator map, not in a form a fresh agent session could act on by reading alone.
- An open ask-navigator map ("make agents-config reproducible by an AI, including Bitwarden-based secret recovery") needs stable vocabulary (mirror direction, restore procedure, secret provisioning) to build tickets on.

## Alternatives considered
- Leave README.md as the sole documentation surface: rejected — README already conflates "what this repo is" with "how to restore it" and has no glossary or decision-record structure for the restore/secrets work still to come.

## Why chosen
Matches this session's existing use of the shipyard harness (ask-navigator, drydock) rather than inventing a lighter-weight ad hoc doc structure for this one repo.

## Consequences
- CONTEXT.md becomes authoritative for the three new terms; future specs/tickets about restore or secrets must use them consistently.
- docs/standards/ and docs/business/ start empty except for structural stubs — sediment is expected to be gradual via the open ask-navigator map's tickets, not filled speculatively now.

## Follow-ups
- ask-navigator's open map should land its resolved decisions (restore mechanism, Bitwarden item-naming convention) as new ADRs and CONTEXT.md entries as they settle, not as edits to this ADR.

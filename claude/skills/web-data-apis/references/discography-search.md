# Discography search — entry → trace → verify

Genre-agnostic; any music task points here. Classical-only rules (ban list, priority order, full timing rules) live in `deep-cut-classical`.

"Find every recording of X" / "duration of Y" = research task: find candidates, trace each to its original session, cross-check from a second angle, then call it complete.

## Sources

- Cite: MusicBrainz, Discogs, Presto Classical, label websites, print/label liner notes.
- **Music streaming services: ignore entirely** on music research. Canonical list (single home; other skills point here):
  - Services: Spotify, Apple Music, Apple Classical, Amazon Music, YouTube Music, Tidal, Deezer, Qobuz, Idagio, Primephonic, Naxos Music Library, SoundCloud, Pandora, any other streaming platform.
  - Domains: `spotify.com`, `music.apple.com`, `classical.music.apple.com`, `music.amazon.*`, `music.youtube.com`, `tidal.com`, `deezer.com`, `qobuz.com`, `idagio.com`, `naxosmusiclibrary.com`, `soundcloud.com`, `pandora.com`.
  - Pass the domain list as `excludeDomains` (or tool equivalent) on every search. Search result still lands on one: discard unread. Never fetch, scrape, cite, quote, or link them.
  - Never mention them in output: no listen pointers, no "available on X", no streaming track totals. Fact whose only witness is a streaming service: `[unverified — dropped]`.
  - Not in scope: YouTube (`youtube.com`, `youtu.be`) — allowed as a listen pointer only, never a fact or timing source. Non-music tasks unaffected.

## 1. Entry points

MusicBrainz (structured, MBID-citable, release/recording/work relations) and Discogs (pressing variants, marketplace-verified catalog numbers). Query from 2+ angles before treating a result set as complete:

- Composer/work + performer or conductor
- Performer/conductor + label
- Catalog number, if known
- Work title alone, filtered by era/orchestra

## 2. Trace each candidate to its session

Reissues, box sets, and digital-era repackagings repress old sessions under new catalog numbers, covers, or remasters. Per candidate:

- Identify the original session (venue, dates if known, orchestra) — not the sleeve date.
- Repress of a known session? Say so: "all other listings are represses of [session]" is a finding.
- MusicBrainz/Discogs disagree or thin: fill from Presto Classical, then the label's own site as tie-breaker (authoritative for its own catalog; check last).

## 3. Verify before "complete"

- State any date / catalog / session conflict in one line.
- "N recordings exist" only after each of N traces to a distinct session.
- State research depth reached (one query / one source / full multi-angle sweep).

## Durations

Two independent sources, movement-sum cross-check, complete-vs-cut flag, named range when recordings differ. Worked rules: `deep-cut-classical` SKILL.md "Timing verification" — applies to any genre.

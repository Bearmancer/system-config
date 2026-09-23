# Web Research Exclusion List

Scope: all Tavily / Exa / Brave / Firecrawl web-data searches in this workspace unless explicitly overridden per-query.

## Explicitly excluded domains

- `qobuz.com` — added 2026-09-21 per user request. Reason: streaming-duplicate noise in discography work (Ormandy Swan Lake). Apply as `exclude_domains: ["qobuz.com"]` (Tavily) / `excludeDomains: ["qobuz.com"]` (Exa/Firecrawl).
  - Includes `www.qobuz.com`, `open.qobuz.com` (subdomain match).
- `music.apple.com` — added 2026-09-21. Apple Music streaming duplicates. Subdomains: `music.apple.com`.
- `open.spotify.com`, `spotify.com` — added 2026-09-21. Spotify streaming duplicates.
- `tidal.com` — added 2026-09-21 (user wrote "tudal"). Includes `www.tidal.com`, `listen.tidal.com`.
- `deezer.com` — added 2026-09-21. Includes `www.deezer.com`.
- `music.amazon.com`, `amazon.com` (music pages only, filter path `/music`) — added 2026-09-21. Amazon Music streaming duplicates. Apply domain `music.amazon.com`; for Tavily also add `amazon.com` only when query is discography-scoped.
- `music.youtube.com`, `youtube.com`, `youtu.be` — added 2026-09-21. YouTube / YouTube Music uploads, track-split videos, no session authority.

Priority sources (allowlist order): `musicbrainz.org` first, then `discogs.com`, then `naxos.com`, `archive.org`, `45cat.com`, `allmusic.com`.

## Rules

- Excluded domains never appear in synthesized tables as primary evidence. If a claim exists only on an excluded domain, mark claim unverified, do not cite it.
- To override for a single query, state `override exclusion: qobuz.com for <reason>` in that call only. Permanent removal requires editing this file.
- New exclusions append below with date + reason. Never delete entries, only supersede with note.

## History

- 2026-09-21: created. `qobuz.com` excluded.
- 2026-09-21: added streaming block: `music.apple.com`, `spotify.com`/`open.spotify.com`, `tidal.com`, `deezer.com`, `music.amazon.com` (+amazon music pages), `music.youtube.com`/`youtube.com`/`youtu.be`. Priority: MusicBrainz then Discogs.

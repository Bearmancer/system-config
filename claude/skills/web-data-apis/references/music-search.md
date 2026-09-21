# Music search — source priority

House rules for looking up music metadata: releases, credits, catalog numbers, dates, pressing variants, discography detail. Applies whenever a task needs to identify or verify a recording, release, or work — not just classical (`deep-cut-classical` layers its own additional sources on top of this for that use case).

## Banned sources — streaming services

Never cite a streaming service as a source for metadata, credits, dates, or catalog facts. They're playback platforms, not discographic authorities — their metadata is licensor-supplied, inconsistently normalized, and not independently verifiable.

| Service         | Why banned                                             |
| --------------- | ----------------------------------------------------- |
| Spotify         | playback platform, not a discographic authority       |
| Apple Music     | same                                                   |
| Apple Classical | same, classical-specific branding doesn't change this |
| Amazon Music    | same                                                   |
| Tidal           | same                                                   |
| Deezer          | same                                                   |
| Qobuz           | same — including its hi-res/classical-leaning catalog  |

A streaming service link is fine to hand the user as a listen-to pointer. It is never a citation for a fact.

## Source priority (search/verify in this order)

1. **MusicBrainz** — open metadata database. Canonical release data, credits, dates, catalog numbers, relationships between releases/recordings/works. First stop: it's structured, cross-referenced, and citable by MBID.
2. **Discogs** — discography and release detail. Best for pressing variants, physical-release specifics, credits Discogs contributors have logged, and marketplace-verified catalog numbers MusicBrainz doesn't have.
3. **Presto Classical** — classical-specific retailer. Strong for classical catalog/release data, label crossovers, and new-release detail before it reaches the aggregators above.
4. **Label website** — check last. A label is authoritative for its own catalog, but check it after the three above: labels' own sites are often slower to update, less consistently structured, and harder to cross-reference against other releases than MusicBrainz/Discogs/Presto.

If sources conflict, prefer the more structured/citable one (MusicBrainz > Discogs > Presto > label) and state the conflict in one line rather than silently picking.

---
name: arr-api-reference
description: This skill should be used when the user asks to "wire Sonarr to SABnzbd", "add a Radarr root folder via API", "connect Prowlarr to Sonarr/Radarr", "set SABnzbd category paths", "map Prowlarr download client categories", "add a path to an Emby library", "query Sonarr/Radarr/Prowlarr/SABnzbd/Emby/Bazarr API", "find Emby/Sonarr/Radarr/Prowlarr/SABnzbd/Bazarr logs or config location", "where does Emby store its config/logs", "Emby troubleshooting" (process name, port, autostart mechanism), "wire Bazarr to Sonarr/Radarr", "trigger Bazarr subtitle search", or otherwise configure, locate, or automate the Sonarr/Radarr/Prowlarr/SABnzbd/Emby/Bazarr media stack via their HTTP APIs or on-disk locations instead of their web UIs.
version: 0.3.0
---

Configure Sonarr/Radarr/Prowlarr/SABnzbd/Emby (plus Bazarr) through their HTTP APIs or on-disk locations — no UI click needed. General HTTP/API debugging, PowerShell foot-guns, and web research route to `shell-gotchas` and `deep-research` instead.

## Core pattern: schema-then-submit

Sonarr, Radarr, Prowlarr same mutation pattern for anything pluggable (download clients, applications, indexers, notifications):

1. `GET .../schema` — give back one template object per implementation
   (e.g. `Sabnzbd`, `QBittorrent`, `Radarr`), each with `fields` array
   of `{name, value, ...}` objects
2. Filter to implementation need, mutate relevant fields' `.value` in
   place
3. `POST`/`PUT` whole object back (not just changed field) — API want
   full resource

See [[shell-gotchas]] for general PowerShell foot-gun (`$var?query=`
interpolation, NTFS case-only rename, `Where-Object`-pipeline field
mutation) — also apply when script against these APIs.

`references/api-reference.md` — single home for exact endpoint, auth
header/param, request body, category code table
(Movies/TV/Music/XXX/Books/etc.), and per-app quirk for Sonarr,
Radarr, Prowlarr, SABnzbd, Emby, Bazarr.

## Category wiring — the thing that actually connects the stack

4 app only work as pipeline if every app agree on same category
**string** for given content type (e.g. `tv`, `movies`). No shared
namespace enforce this — convention only, must verify by hand:

- SABnzbd category name (`[[categories]]` section) — SAB force-lowercase
  category id regardless of what's sent; `dir` path casing kept as sent.
  Keep category names lowercase everywhere (detail: `references/api-reference.md`).
- Sonarr download-client field `tvCategory` must match that SAB category
  name
- Radarr download-client field `movieCategory` must match that SAB
  category name
- Prowlarr download-client `categories` array (separate from `fields`)
  map Prowlarr numeric category code to client category string:
  `[{clientCategory: "tv", categories: [5000,5010,...]}]`. Un-mapped
  category fall through to client default `category` field value.

Mismatch anywhere in chain fail silent — download finish, just land
wrong (or default) category/folder, no error show anywhere. Always
verify end-to-end with real (or old) job, not just re-read config back.
`python scripts/verify_category_wiring.py` cross-checks the whole
chain in one call (SAB category list vs Sonarr/Radarr download-client
category vs Prowlarr mapping) — run it after any category or
download-client edit, don't just hand-read four configs.

Staging dir mirror by protocol, not by app: `C:\Media\Usenet\TV`
(SABnzbd) and `C:\Media\Torrent\TV` (qBittorrent) both feed same
`C:\Media\Library\TV` final import target. Same pattern for
Movies/Music/XXX/Books/General under each protocol root.

## Emby — separate app, separate id system, easy to get burned

Emby not part of Sonarr/Radarr/Prowlarr/SABnzbd category-string pipeline
above — last hop, shows finished library to human. Two gotchas: no API
key on disk (mint in Dashboard, or trade credentials for a token), and
add-library-path needs the `Guid` field, not `name`/`ItemId` (`name=`
throws HTTP 500). Full detail, worked example, auth options,
process/port/config/log paths: `references/api-reference.md` Emby
section.

## Renaming category folders after the fact

NTFS path lookup case-insensitive; display-casing-only rename of
directory (`tv` → `TV`) no invalidate open file handle inside, safe do
live even mid-download.

## Routing: stack-state vs triage vs backup

- Bind/firewall/autostart config (read before touching service config): `references/stack-state.md`.
- Stack looks broken right now (down/stuck/zombie/stale-queue): `references/triage.md`.
- Before editing any live config here again: run `python "$HOME\.claude\skills\arr-api-reference\scripts\backup_arr_stack.py"`.

## Verifying, not assuming

After any config mutation, re-`GET` check the real value come back —
many API accept write then quiet-normalize or reject part of it (see
SABnzbd category-casing above; Prowlarr PUT-dedupe gotcha in
`references/api-reference.md`, already handled by `merge_arr_fields`
in the scripts below).

To find why one finished download land somewhere not expect, query
app history/queue for that job `category` field first — category set
at grab time, no change back if mapping fix after. Job in wrong spot
almost always come before fix, no contradict fix.

## Scripts — use these instead of re-deriving the API calls

Import `scripts/arr_scripts.py` for everything except backup/verify
(those two run standalone) — don't hand-roll schema-then-submit dance
again, already handles dedupe/mutation gotcha above.

| Function (in `arr_scripts.py`) | Purpose / gotcha handled |
| --- | --- |
| `add_arr_download_client` | Wire download client (e.g. SABnzbd) into Sonarr/Radarr from its schema template. |
| `set_prowlarr_category_map` | Set/replace Prowlarr category→client-category mapping in one call, dedupe-safe. |
| `set_sab_category_dir` / `remove_sab_category` | SABnzbd category dir — correct `set_config` shape, not the tempting-but-broken `set_cat`. |
| `set_qbt_category_dir` | qBittorrent category save path (`editCategory`). Own store, unrelated to SAB/Sonarr/Radarr category — category existing doesn't mean `savePath` points anywhere real; verify with `GET /api/v2/torrents/categories`. |
| `find_arr_job` | Look up SABnzbd history entry by name substring — first move when a download lands somewhere unexpected. |
| `add_emby_library_path` | Add path to existing Emby library by name (resolves name→`Guid` internally, caller never touches the id gotcha). |

- **`scripts/verify_category_wiring.py`** — standalone, imports only
  `arr_scripts` (same dir). Cross-checks SAB category list against
  Sonarr/Radarr download-client category and Prowlarr's mapping, prints
  every mismatch, exits 1 if any found. Run after any category or
  download-client edit — the check prose alone can't enforce (see
  "Category wiring" above).
- **`scripts/backup_arr_stack.py`** — imports `arr_scripts` for
  key/base-URL helpers only. `backup_arr_stack()` triggers backup on
  all 4 apps, zips qBittorrent's config dir (no backup API exists for
  it), renames each `<name> - <yyyy-MM-dd>.zip`, starts Google Drive if
  unmounted, drops all 5 in `Computer\Configs` — that folder must
  already exist, never auto-created. Run by full path, no `$PROFILE`
  alias: `python "$HOME\.claude\skills\arr-api-reference\scripts\backup_arr_stack.py"`.
  Partial-fail mode: a down app's backup fails loud per-app but the
  others still write (seen: SAB `mode=config` refuse + null-path
  `Copy-Item` error while Sonarr/Prowlarr zip fine; Radarr zip re-dated
  with old content). Check each timestamp after run, don't trust "no
  red text".

## Bazarr — subtitle manager, separate API quirks

Bazarr connect to Sonarr + Radarr to manage subtitle, separate auth
and form-encoded (not JSON) POST body. Full endpoint detail, wiring
script, and gotchas: `references/api-reference.md`. Autostart
mechanism: `references/stack-state.md`.

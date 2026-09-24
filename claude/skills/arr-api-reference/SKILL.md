---
name: arr-api-reference
description: This skill should be used when the user asks to "wire Sonarr to SABnzbd", "add a Radarr root folder via API", "connect Prowlarr to Sonarr/Radarr", "set SABnzbd category paths", "map Prowlarr download client categories", "add a path to an Emby library", "query Sonarr/Radarr/Prowlarr/SABnzbd/Emby/Bazarr API", "find Emby/Sonarr/Radarr/Prowlarr/SABnzbd/Bazarr logs or config location", "where does Emby store its config/logs", "Emby troubleshooting" (process name, port, autostart mechanism), "wire Bazarr to Sonarr/Radarr", "trigger Bazarr subtitle search", or otherwise configure, locate, or automate the Sonarr/Radarr/Prowlarr/SABnzbd/Emby/Bazarr media stack via their HTTP APIs or on-disk locations instead of their web UIs.
version: 0.3.0
---

Configure Sonarr/Radarr/Prowlarr/SABnzbd/Emby (plus Bazarr) through their HTTP APIs or on-disk locations — no UI click needed. General HTTP/API debugging, PowerShell foot-guns, and web research route to `shell-gotchas` and `rigorous-research`/`web-data-apis` instead.

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

- SABnzbd category name (`[[categories]]` section) — **SABnzbd
  force lowercase category id no matter what you send.** Only
  category's `dir` (destination path) keep casing you send. Plan
  around it: keep category name lowercase everywhere, style path
  however want.
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
above — it last hop, thing that show finished library to human. Own
auth, own id quirk:

- **No API key on disk.** Unlike other four app, Emby no write static
  key to any config file. Make one in Dashboard → Advanced → API
  Keys, or trade username/password for session token via `POST
  /Users/AuthenticateByName`. Don't hunt `system.xml` for it — not
  there.
- **Add path to existing library needs `id` (the `Guid` field), not `name` or `ItemId`** — sending `name=` throws `System.FormatException: Unrecognized Guid format` HTTP 500. Full trace + field detail: `references/api-reference.md`.
- **Auth take two way:** query param `?api_key=<key>` or header
  `X-Emby-Token: <key>` — both work same, no preference.

```powershell
$key = "<api key>"
$libs = Invoke-RestMethod "http://localhost:8096/Library/VirtualFolders?api_key=$key"
$target = $libs | Where-Object Name -eq "Home videos & photos"
Invoke-RestMethod -Method Post "http://localhost:8096/Library/VirtualFolders/Paths?id=$($target.Guid)&path=C:\Media\Library\XXX&refreshLibrary=true&api_key=$key"
```

Process name `EmbyServer` (+ tray helper `embytray`), default port
`8096`, config dir `%AppData%\Emby-Server\programdata\config\` (no
secret there), log at
`%AppData%\Emby-Server\programdata\logs\embyserver.txt` — check log
tail for real .NET exception when call 500, don't just guess from HTTP
body alone.

## Renaming category folders after the fact

NTFS path lookup case-insensitive; display-casing-only rename of
directory (`tv` → `TV`) no invalidate open file handle inside, safe do
live even mid-download. Single `Rename-Item` sometimes no-op on
case-only change — see [[shell-gotchas]] for two-step
temp-name workaround.

## Autostart and bind state

Current wildcard-bind/firewall config, per-app autostart mechanism, and Bazarr's Windows Service registration: `references/stack-state.md` — read before touching service config.

Before edit any live config here again: run `python "$HOME\.claude\skills\arr-api-reference\scripts\backup_arr_stack.py"`.

Live down/stuck/zombie-process/stale-queue diagnostic runbooks: `references/triage.md` — read there when the stack looks broken right now.

## Verifying, not assuming

After any config mutation, re-`GET` check the real value come back —
many API accept write then quiet-normalize or reject part of it (see
SABnzbd category-casing above, and Prowlarr category-mapping field
duplicate on naive `PUT` — dedupe `fields` by `name` before resend if
re-`PUT`-ing already-fetch resource).

To find why one finished download land somewhere not expect, query
app history/queue for that job `category` field first — category set
at grab time, no change back if mapping fix after. Job in wrong spot
almost always come before fix, no contradict fix.

## Scripts — use these instead of re-deriving the API calls

Two file. Import `scripts/arr_scripts.py` for everything except
automated backup — don't hand-roll schema-then-submit dance again,
already handle include dedupe/mutation gotcha above:

- **`add_arr_download_client`** — wire download client (e.g. SABnzbd)
  into Sonarr or Radarr from its schema template.
- **`set_prowlarr_category_map`** — set/replace Prowlarr
  category→client-category mapping in one call, dedupe-safe.
- **`set_sab_category_dir`** / **`remove_sab_category`** — SABnzbd category
  dir (correct `set_config` shape, not tempting-but-broken `set_cat`).
- **`set_qbt_category_dir`** — qBittorrent category save path
  (`editCategory`). qBittorrent category own store, unrelated to
  SAB/Sonarr/Radarr category — category exist there no mean its
  `savePath` point anywhere real; verify with `GET
  /api/v2/torrents/categories`.
- **`find_arr_job`** — look up SABnzbd history entry by name substring —
  first move when download land somewhere not expect.
- **`add_emby_library_path`** — add path to existing Emby library by name
  (resolve name → `Guid` inside, caller never touch id gotcha
  above).

- **`scripts/verify_category_wiring.py`** — standalone, no import
  anything else need except `arr_scripts` (same dir). Cross-check SAB
  category list against Sonarr/Radarr download-client category and
  Prowlarr's mapping, print every mismatch, exit 1 if any found. Run
  after any category or download-client edit — this is the check
  prose alone can't enforce (see "Category wiring" section above).

- **`scripts/backup_arr_stack.py`** — standalone, no import
  anything else need. `backup_arr_stack()` trigger backup on all 4 app
  - zip qBittorrent config dir (no backup API exist for it), rename
    each `<name> - <yyyy-MM-dd>.zip`, starts Google Drive if unmounted,
    drops all 5 in `Computer\Configs`. That folder must already exist —
    never auto-created. Run directly by full path — no `$PROFILE`
    alias: `python "$HOME\.claude\skills\arr-api-reference\scripts\backup_arr_stack.py"`.
  - Partial-fail mode: down app backup fail loud per app but other
    still write (seen: SAB `mode=config` refuse + null-path
    `Copy-Item` error while Sonarr/Prowlarr zip fine; Radarr zip
    re-date with old content). Check each timestamp after run, don't
    trust "no red text".

## Bazarr — subtitle manager, separate API quirks

Bazarr connect to Sonarr + Radarr to manage subtitle, separate auth
and form-encoded (not JSON) POST body. Full endpoint detail, wiring
script, and gotchas: `references/api-reference.md`. Autostart
mechanism: `references/stack-state.md`.

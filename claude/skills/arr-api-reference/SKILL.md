---
name: arr-api-reference
description: This skill should be used when the user asks to "wire Sonarr to SABnzbd", "add a Radarr root folder via API", "connect Prowlarr to Sonarr/Radarr", "set SABnzbd category paths", "map Prowlarr download client categories", "add a path to an Emby library", "query Sonarr/Radarr/Prowlarr/SABnzbd/Emby/Bazarr API", "find Emby/Sonarr/Radarr/Prowlarr/SABnzbd/Bazarr logs or config location", "where does Emby store its config/logs", "Emby troubleshooting" (process name, port, autostart mechanism), "wire Bazarr to Sonarr/Radarr", "trigger Bazarr subtitle search", or otherwise configure, locate, or automate the Sonarr/Radarr/Prowlarr/SABnzbd/Emby/Bazarr media stack via their HTTP APIs or on-disk locations instead of their web UIs.
version: 0.3.0
---

Configure Sonarr/Radarr/Prowlarr/SABnzbd/Emby all through HTTP APIs — no UI click need. All five have full REST/JSON-RPC-style APIs. Skill write down verified request shapes, auth, gotchas found while drive from PowerShell.

## Core pattern: schema-then-submit

Sonarr, Radarr, Prowlarr same mutation pattern for anything pluggable (download clients, applications, indexers, notifications):

1. `GET .../schema` — give back one template object per implementation
   (e.g. `Sabnzbd`, `QBittorrent`, `Radarr`), each with `fields` array
   of `{name, value, ...}` objects
2. Filter to implementation need, mutate relevant fields' `.value` in
   place
3. `POST`/`PUT` whole object back (not just changed field) — API want
   full resource

**PowerShell gotcha:** mutate fields with `foreach` loop, not
`Where-Object` pipeline assign. `($obj.fields | Where-Object
{...}).value = "x"` hit pipeline copy, fail silent; `foreach ($f in
$obj.fields) { if ($f.name -eq "x") { $f.value = "y" } }` mutate in
place, correct way.

See [[shell-gotchas]] for general PowerShell foot-gun (`$var?query=`
interpolation, NTFS case-only rename) — also apply when script against
these APIs.

Read `references/api-reference.md` for exact endpoint, auth shape,
field name per app.

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
- **Two id field per library, only one work.** `GET
  /Library/VirtualFolders` give back each library with both `ItemId`
  (short decimal string, e.g. `"45267"`) and `Guid` (32-char hex, no
  dash, e.g. `"de1bd066d4ed4e20a426feafdfc10c5f"`). Only `Guid` real
  item id Emby innards can read.
- **Add path to existing library need `id`, not `name`.** `POST
  /Library/VirtualFolders/Paths?id=<Guid>&path=<path>` correct way.
  Send `name=<library name>` instead (look like should work, other
  Emby-adjacent tool accept name-based lookup) throw
  `System.FormatException: Unrecognized Guid format` HTTP 500 —
  handler always call `GetItemById` on whatever given, no name
  fallback. Body content no matter; pure query-string call.
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

## Boot-time bind race (Sonarr/Radarr/Prowlarr/SABnzbd)

All 4 app `host`/`BindAddress` used be hardcode to this machine
Tailscale IP (`100.86.121.94`). At boot, Windows start each Automatic
service before `tailscaled` finish reconnect and re-assign that
IP — bind fail with `SocketException 10049` (WSAEADDRNOTAVAIL, not
port-in-use), service die. `sc.exe config <Name> depend= Tailscale`
only wait for Tailscale _service_ report Running, not for IP actually
exist — not enough alone.

Fixed 2026-08-29: `BindAddress`/`host` change to wildcard (`*` for
Sonarr/Radarr/Prowlarr config.xml, `0.0.0.0` for SABnzbd's
`sabnzbd.ini`) — app now bind instant no matter Tailscale timing, also
work on `localhost` this machine (no work before). Reachability lock
down instead by Windows Firewall: existing
`NzbDrone`/`SABnzbd`/`SABnzbd-console` inbound rule scope
`RemoteAddress = 100.64.0.0/10` (Tailscale CGNAT range, match SAB own
`local_ranges` setting) — default-deny handle rest, no need explicit
block rule. `depend=Tailscale` + `sc.exe failure ...
actions= restart/30000/restart/60000/restart/120000` keep as harmless
extra safety on top.

SABnzbd itself have no Windows Service via installer by default — it
ship one native (pywin32 `ServiceFramework` in `SABnzbd.py`, verb
`install|update|remove|start|stop|restart`), but install command
wrong-detect non-interactive/session-0 shell, refuse
(`StartServiceCtrlDispatcher` error) — work around with `sc.exe create`
direct plus write `-f <inifile>` command line into
`HKLM\SYSTEM\CurrentControlSet\services\SABnzbd\CommandLine`
(REG_MULTI_SZ) same way installer `set_serv_parms` would do.

qBittorrent have no headless/service mode (GUI-only Qt binary, no
`-nox` build this machine) — can't run as Session-0 service like other
four. On purpose manual-start (user decide 2026-08-29), same as Emby —
don't wrap either as service/task unless ask again.

### Current inventory (verified 2026-08-29, post-fix)

| App         | Autostart mechanism                                                                                       | Account                     | Bind                    | Firewall                                                         |
| ----------- | --------------------------------------------------------------------------------------------------------- | --------------------------- | ----------------------- | ---------------------------------------------------------------- |
| Sonarr      | native Windows Service, Auto                                                                              | `NT AUTHORITY\LocalService` | `*` (config.xml)        | `NzbDrone` rule, `RemoteAddress=100.64.0.0/10`                   |
| Radarr      | native Windows Service, Auto                                                                              | `NT AUTHORITY\LocalService` | `*` (config.xml)        | `NzbDrone` rule, `RemoteAddress=100.64.0.0/10`                   |
| Prowlarr    | native Windows Service, Auto                                                                              | `NT AUTHORITY\LocalService` | `*` (config.xml)        | `NzbDrone` rule, `RemoteAddress=100.64.0.0/10`                   |
| SABnzbd     | native Windows Service, Auto (`sc create`, not installer)                                                 | `LocalSystem`               | `0.0.0.0` (sabnzbd.ini) | `SABnzbd`/`SABnzbd-console` rules, `RemoteAddress=100.64.0.0/10` |
| qBittorrent | manual only, no service/task                                                                              | —                           | n/a                     | n/a                                                              |
| Emby        | login Startup-folder shortcut (`%AppData%\Microsoft\Windows\Start Menu\Programs\Startup\Emby Server.lnk`) | current user                | n/a                     | n/a                                                              |

No arr-related Scheduled Task. Servy (`C:\Program Files\Servy`) manage
only `ClaudeRemoteControl` — unrelated, not use for any above.

Before edit any live config here again: run `backup-arr`.

## Before hitting any app's API

Confirm app really running first (`Get-Process <App>`). Down app give
misleading "connection refused" — worse, call made while down can leave
false "API key missing" entry in _its own_ health log once back up,
since log just record request that arrive with no key attach (app not
there to catch one, not real config problem). Don't chase that log
entry like it live thing.

**Stuck/zombie process look "running" but serve nothing.**
`Get-Process` show exe no mean it listen —
Sonarr/Radarr/Prowlarr `SingleInstancePolicy` self-kill fresh
launch if see another instance already hold lock, but older
instance itself can be zombie (crash past HTTP listener, mutex still
hold). Symptom: process exist, `Get-NetTCPConnection -OwningProcess
<pid>` give back nothing, `curl` get connection-refused. Fix:
`Stop-Process -Id <pid> -Force`, relaunch.

**SABnzbd duplicate-process outage (seen 2026-09-19).** Two
`SABnzbd.exe` at once (one boot-time, one late-night manual launch),
both bare cmdline `"C:\Program Files\SABnzbd\SABnzbd.exe"`, neither
listen on 8080, log tail 3 day old. Meanwhile `sc.exe query` show
all four service `STOPPED` while Sonarr/Prowlarr orphan process
still serve API fine — SCM state and process table disagree, trust
`Get-NetTCPConnection -State Listen` for port 8989/7878/9696/8080,
not service state. Fix: `Stop-Process -Id <both> -Force`,
`sc.exe start SABnzbd`, verify single PID listen `0.0.0.0:8080`
before touch anything else. Sonarr-side client config need zero
change after — outage was process, not setting.

## "All download clients are unavailable due to failures" triage

Health error almost always mean client app down, not client config
wrong. Order: (1) confirm listener (`Get-NetTCPConnection -State
Listen` for 8080), (2) read Sonarr log tail for exact cause —
SAB-down look like `DownloadClientUnavailableException: Unable to
connect to SABnzbd, No connection could be made because the target
machine actively refused it. (100.86.121.94:8080)` under
`DownloadMonitoringService|Unable to retrieve queue and history
items from SABnzbd`, (3) fix process (see zombie section above),
(4) `POST /api/v3/downloadclient/testall` — expect
`[{id, isValid: True, validationFailures: []}]`, then re-`GET
/api/v3/health` and confirm download-client error gone with no
config edit.

Stale queue entries with `status: downloadClientUnavailable` persist
after client recover (they reference grab-time state). Don't hand-
`POST /api/v3/queue/grab` with `{ids}` — it 405. Instead queue a
`SeriesSearch`: `POST /api/v3/command`
`{"name":"SeriesSearch","seriesId":<id>}` → `queued`, wait ~90s,
then `GET /queue` group by `status` and SAB `mode=queue` show
`Downloading` jobs. Verified 2026-09-19: 11 stale → 1
`downloading`, SAB `jobs=2 status=Downloading`.

Pause live SAB-side: Sonarr queue `status: paused` mirror SAB job
status, so resume in SAB, not Sonarr:
`mode=queue&name=resume&value=<nzo_id>&output=json&apikey=...` →
`{"status":true}`, re-query queue confirm job `Downloading`.
Find `nzo_id` per job from same `mode=queue` response (`.queue.slots[].nzo_id`).
Duplicate-pause pattern (seen 2026-09-19): 8 Sonarr paused entries
same release map to only 2 real SAB job (1 `Downloading`, 1
`Paused`) — rest stale tracked ref to `nzo_id` lost in restart.
Resume real one, stale ref drop on re-poll by itself, don't chase
them.

## Allowed Hosts (Sonarr General setting)

Empty `allowedHosts` raise `AllowedHostsCheck` warning in
`/api/v3/health`. Set via same host resource as login (id always
`1`): `GET /api/v3/config/host`, change only `allowedHosts`,
`PUT` whole object to `/api/v3/config/host/1` with `password`
untouched (hash-compare rule same as username change above).
Verified value this machine (2026-09-19):
`localhost,127.0.0.1,100.86.121.94,lance,lance.tail2e6179.ts.net`
(hostname + MagicDNS from `tailscale status`, SAB `host_whitelist`
tail domain `*.tail2e6179.ts.net` confirm suffix). After PUT,
re-`GET` show value back, `GET /health` empty, and probe health
through Tailscale IP (`http://100.86.121.94:8989/api/v3/health`)
to prove not lock out before close.

## Login username/password (WebUI, not API key)

Separate from `ApiKey` in config.xml. Sonarr/Radarr/Prowlarr keep this
in internal SQLite `Users` table, not config.xml — expose via `GET/PUT
/api/v3/config/host` (`/api/v1` for Prowlarr), field
`username`/`password`/`passwordConfirmation`.

- **Sonarr/Radarr/Prowlarr force-lowercase username server-side**
  no matter what you send (`user.Username =
  username.ToLowerInvariant()` in `UserService.Upsert`) — send
  `"Lance"` quiet-store `"lance"`. qBittorrent's `web_ui_username`
  preference no lowercase — case you send is case it keep.
- **Change username without touch password:** `GET
  /api/v3/config/host` first, change only `username` in object come
  back, `PUT` whole thing back with `password` untouched (still the
  hash `GET` gave). Backend compare `resource.Password` to stored hash
  byte-for-byte; equal mean "unchanged," skip re-hash. Send plaintext
  password there instead, double-hash it, break login.
- **qBittorrent:** `POST /api/v2/app/setPreferences` with body
  `json={"web_ui_username":"<name>"}` (URL-encoded).
- **SABnzbd:** WebUI username/password live under `[misc]` in
  `sabnzbd.ini`, separate from `[[servers]]` block — those per-provider
  Usenet account login, not local app credential; never mix up two.
- **Emby:** no username/password to rotate through this pipeline —
  auth is per-user-account through own `/Users` system, unrelated to
  arr-stack login idea.

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

- **`scripts/backup_arr_stack.py`** — standalone, no import
  anything else need. `backup_arr_stack()` trigger backup on all 4 app
  - zip qBittorrent config dir (no backup API exist for it), rename
    each `<name> - <yyyy-MM-dd>.zip`, starts Google Drive if unmounted,
    drops all 5 in `Computer\Configs`. That folder must already exist —
    never auto-created. Was wired into `$PROFILE` as `backup-arr` via
    dot-source (PowerShell mechanism, now gone — script is Python).
    Update `$PROFILE`'s `backup-arr` function to shell out instead:
    `python "$HOME\.claude\skills\arr-api-reference\scripts\backup_arr_stack.py"`.
  - Partial-fail mode: down app backup fail loud per app but other
    still write (seen: SAB `mode=config` refuse + null-path
    `Copy-Item` error while Sonarr/Prowlarr zip fine; Radarr zip
    re-date with old content). Check each timestamp after run, don't
    trust "no red text".

## Orchestration

Live-stack work mostly read-only and easy go wrong quiet-like. When host session orchestrate, spawn worker to run API call and catch raw response — keep orchestrator out of request loop. Verify pass (category chain really end where should?) is own subagent task with exact GETs to run and expect field to quote. Never fake a call by hand: run the real one, or say plain you did not.

## Finishing an edit to this skill

`~/.claude/skills/arr-api-reference/` is source of truth. The `agents-config` repo mirror it: after edit, run the sync script (`agents-config` repo's README.md, "Backup mechanism" section) to commit and push change. Before touch live app config, run `backup-arr`.

## Bazarr — subtitle manager, separate API quirks

Bazarr connect to Sonarr + Radarr to manage subtitle. Port `6767`,
config at `C:\ProgramData\Bazarr\config\config.yaml`, API key in
`general.apikey` field of that file. Auth: header `X-API-KEY: <key>`
OR query `?apikey=<key>` OR form field `apikey`.

**`/system/settings` hide from swagger on purpose** — it exist
but give back `null` from swagger path list. Only `GET` and `POST`
register; `PUT`/`PATCH` give 405.

**Big gotcha: POST body must be `application/x-www-form-urlencoded`
(form), not JSON.** Handler read `request.form` — send JSON body
get quiet-ignore, setting no save. Earlier try with
`ConvertTo-Json` body all fail for this reason.

Field name pattern: `settings-<section>-<key>` (partial update OK —
only key you give get write).

### Wire Bazarr → Sonarr + Radarr

```powershell
$h = @{"X-API-KEY"="<bazarr-apikey>"}
$b = @{
    "settings-general-use_sonarr" = "true"
    "settings-sonarr-ip"          = "127.0.0.1"
    "settings-sonarr-port"        = "8989"
    "settings-sonarr-base_url"    = "/"
    "settings-sonarr-ssl"         = "false"
    "settings-sonarr-apikey"      = "<sonarr-apikey>"
    "settings-general-use_radarr" = "true"
    "settings-radarr-ip"          = "127.0.0.1"
    "settings-radarr-port"        = "7878"
    "settings-radarr-base_url"    = "/"
    "settings-radarr-ssl"         = "false"
    "settings-radarr-apikey"      = "<radarr-apikey>"
}
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:6767/api/system/settings" -Headers $h -Body $b -ContentType "application/x-www-form-urlencoded"
# expect 204 No Content; 406 + message on validation fail
# verify:
$v = Invoke-RestMethod -Headers $h "http://127.0.0.1:6767/api/system/settings"
"use_sonarr: $($v.general.use_sonarr), key set: $($v.sonarr.apikey.Length -gt 0)"
"use_radarr: $($v.general.use_radarr), key set: $($v.radarr.apikey.Length -gt 0)"
```

No restart need — `save_settings()` call `sonarr_signalr_client.restart()`
and `radarr_signalr_client.restart()` inside. Full service restart
only at `POST /api/system?action=restart` (also hide from swagger).

Bazarr **not** connect to Prowlarr or Emby — those not
Bazarr integration target. Prowlarr feed Sonarr/Radarr (download
source); Emby is playback front-end. Bazarr only talk
Sonarr + Radarr for library metadata.

### Inventory addition (verified 2026-09-06)

| App    | Port | Config                                     | Auth                      |
| ------ | ---- | ------------------------------------------ | ------------------------- |
| Bazarr | 6767 | `C:\ProgramData\Bazarr\config\config.yaml` | `X-API-KEY` or `?apikey=` |

Bazarr autostart mechanism: TBD (not yet confirm as service/task).

## Additional Resources

- **`references/api-reference.md`** — exact endpoint, auth
  header/param, request body, category code table
  (Movies/TV/Music/XXX/Books/etc.), per-app quirk for Sonarr, Radarr,
  Prowlarr, SABnzbd, Emby.

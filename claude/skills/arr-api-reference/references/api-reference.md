# Arr-stack + Emby API reference

All endpoints verified working real instances. Auth key each app own config file — read it, don't hardcode.

## Auth key locations

| App      | Config file                                                                                 | Key path           |
| -------- | ------------------------------------------------------------------------------------------- | ------------------ |
| Sonarr   | `<AppData>\Sonarr\config.xml`                                                               | `<Config><ApiKey>` |
| Radarr   | `<AppData>\Radarr\config.xml`                                                               | `<Config><ApiKey>` |
| Prowlarr | `<AppData>\Prowlarr\config.xml`                                                             | `<Config><ApiKey>` |
| SABnzbd  | `<UserAppData>\Local\sabnzbd\sabnzbd.ini`                                                   | `[misc] api_key =` |
| Emby     | none on disk — mint in Dashboard → Advanced → API Keys, or `POST /Users/AuthenticateByName` | n/a                |

PowerShell one-liner XML-based ones:

```powershell
$key = ([xml](Get-Content "C:\ProgramData\Sonarr\config.xml")).Config.ApiKey
```

## Host config (login, launch-browser, etc.)

`GET`/`PUT /api/v3/config/host` (`/api/v1` for Prowlarr) — id always `1`. Covers `bindAddress`, `port`, `authenticationMethod`, `username`/`password`/`passwordConfirmation`, `launchBrowser`, more. `launchBrowser: true` opens browser tab each startup — set `false` stop that. See skill "Login username/password" section, safe username-change pattern (don't touch `password` unless actually changing it).

`allowedHosts` (same resource): comma-separated `localhost,127.0.0.1,100.86.121.94,lance,lance.tail2e6179.ts.net` verified 2026-09-19 — `PUT` whole object to `/config/host/1`, re-`GET` confirm, probe `/health` via Tailscale IP to prove no lockout.

## Sonarr / Radarr (v3 API — identical shape, different port/base path)

Auth: header `X-Api-Key: <key>`. Base: `http://<host>:<port>/api/v3`.

| Action                                                               | Endpoint                       | Body                                                                                                                                                                  |
| -------------------------------------------------------------------- | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| List root folders                                                    | `GET /rootfolder`              | —                                                                                                                                                                     |
| Add root folder                                                      | `POST /rootfolder`             | `{"path": "C:\\Media\\Library\\TV"}`                                                                                                                                  |
| Remove root folder                                                   | `DELETE /rootfolder/{id}`      | —                                                                                                                                                                     |
| List download clients                                                | `GET /downloadclient`          | —                                                                                                                                                                     |
| Get download client templates                                        | `GET /downloadclient/schema`   | —                                                                                                                                                                     |
| Add download client                                                  | `POST /downloadclient`         | full object from schema, mutated (see below)                                                                                                                          |
| Test all download clients                                            | `POST /downloadclient/testall` | empty body — returns `[{id, isValid, validationFailures}]`; re-`GET /health` after, download-client error should clear with no config edit if outage was process-side |
| Trigger backup                                                       | `POST /command`                | `{"name": "Backup"}`                                                                                                                                                  |
| Re-search one series (clear stale `downloadClientUnavailable` queue) | `POST /command`                | `{"name": "SeriesSearch", "seriesId": <id>}` → `queued`; `POST /queue/grab` with `{ids}` 405s, use this instead                                                       |

Download client add — filter schema to implementation, set fields, POST whole thing:

```powershell
$schemas = Invoke-RestMethod -Uri "$base/downloadclient/schema" -Headers $headers
$sab = $schemas | Where-Object { $_.implementation -eq "Sabnzbd" }
foreach ($f in $sab.fields) {
    if ($f.name -eq "host") { $f.value = "100.86.121.94" }
    if ($f.name -eq "port") { $f.value = 8080 }
    if ($f.name -eq "apiKey") { $f | Add-Member -NotePropertyName value -NotePropertyValue $sabKey -Force }
    if ($f.name -eq "tvCategory") { $f.value = "tv" }       # movieCategory for Radarr
}
$body = @{
    enable = $true; protocol = $sab.protocol; priority = 1; name = "SABnzbd"
    fields = $sab.fields; implementationName = $sab.implementationName
    implementation = $sab.implementation; configContract = $sab.configContract
    infoLink = $sab.infoLink; tags = @()
} | ConvertTo-Json -Depth 8
Invoke-RestMethod -Uri "$base/downloadclient" -Headers $headers -Method Post -Body $body -ContentType "application/json"
```

Note: `apiKey` field no `value` in schema template (secret field) — need `Add-Member -Force`, not direct assign.

**Validation errors informative.** 400 on `/rootfolder` returns `[{propertyName, errorMessage, attemptedValue}]`; e.g. `"Path already configured as a root folder"` means exists already, check state not retry blind.

**Post-restart race.** Right after start/restart, `GET` may return empty though DB has row (cache warm-up lag, few secs observed). One empty GET right after restart not proof fail — wait ~5s, recheck.

**Windowless exe.** Both ship `<App>.exe` (windowless) and `<App>.Console.exe` (visible console). Use non-`.Console` variant for anything unwatched.

## Prowlarr (v1 API)

Auth: header `X-Api-Key: <key>`. Base: `http://<host>:<port>/api/v1`.

| Action                                               | Endpoint                   | Body                                                                    |
| ---------------------------------------------------- | -------------------------- | ----------------------------------------------------------------------- |
| List applications (pushes indexers to Sonarr/Radarr) | `GET /applications`        | —                                                                       |
| Get application templates                            | `GET /applications/schema` | —                                                                       |
| Add application                                      | `POST /applications`       | full object from schema, mutated (same pattern as downloadclient above) |
| List download clients                                | `GET /downloadclient`      | —                                                                       |
| Get one download client                              | `GET /downloadclient/{id}` | —                                                                       |
| Update download client                               | `PUT /downloadclient/{id}` | full object, `.fields` **and** `.categories`                            |
| Force indexer→app sync (skip schedule)               | `POST /command`            | `{"name": "ApplicationIndexerSync"}`                                    |
| Trigger backup                                       | `POST /command`            | `{"name": "Backup"}`                                                    |

Applications add uses `configContract: "SonarrSettings"` / `"RadarrSettings"`, fields `prowlarrUrl`, `baseUrl`, `apiKey`, `syncCategories` (array Prowlarr category codes, table below), `syncLevel: "fullSync"`.

Download client **category mapping** (separate top-level field from `.fields`, easy miss):

```powershell
$client.categories = @(
    @{ clientCategory = "tv"; categories = @(5000,5010,5020,5030,5040,5045,5050,5060,5070,5080,5090) },
    @{ clientCategory = "movies"; categories = @(2000,2010,2020,2030,2040,2045,2050,2060,2070,2080,2090) }
)
```

Anything not listed routes to client's default `category` field (set via `.fields`, `name -eq "category"`).

**PUT dedupe gotcha.** Re-`PUT`-ing object fetched from `GET .../{id}` can duplicate field in `.fields` (observed: `category` field twice, diff values, after `PUT`). Before resubmit already-fetched-and-previously-PUT object, dedupe:

```powershell
$deduped = @{}
foreach ($f in $client.fields) { $deduped[$f.name] = $f }
$client.fields = @($deduped.Values)
```

### Prowlarr category codes (indexer categories, used in `syncCategories` and download-client `.categories` mapping)

| Range     | Meaning                                                         |
| --------- | --------------------------------------------------------------- |
| 1000-1180 | Console                                                         |
| 2000-2090 | Movies (2000 base, 2040 HD, 2045 UHD, 2050 BluRay, 2080 WEB-DL) |
| 3000-3060 | Audio/Music                                                     |
| 4000-4070 | PC                                                              |
| 5000-5090 | TV (5000 base, 5040 HD, 5045 UHD, 5070 Anime)                   |
| 6000-6090 | XXX                                                             |
| 7000-7060 | Books                                                           |
| 8000-8020 | Other                                                           |

## Emby

Auth: query param `api_key=<key>` or header `X-Emby-Token: <key>` — either works. Base: `http://<host>:<port>` (no `/api` prefix, no version segment).

| Action                       | Endpoint                                                                       | Body                               |
| ---------------------------- | ------------------------------------------------------------------------------ | ---------------------------------- |
| List libraries               | `GET /Library/VirtualFolders`                                                  | —                                  |
| Add path to existing library | `POST /Library/VirtualFolders/Paths?id=<Guid>&path=<path>&refreshLibrary=true` | none — pure query string           |
| Mint token from credentials  | `POST /Users/AuthenticateByName`                                               | `{"Username": "...", "Pw": "..."}` |

`GET /Library/VirtualFolders` response per library: `Name`, `Locations` (array of paths), `CollectionType`, `ItemId` (decimal string, cosmetic only), `Guid` (32-hex no dashes — real id).

**The id gotcha.** `Library/VirtualFolders/Paths` calls `LibraryManager.GetItemById` on whatever id passed — no name-based lookup server-side. Sending `name=<library name>` (several third-party scripts + intuitive API shape suggest should work) throws:

```
System.FormatException: Unrecognized Guid format.
   at System.Guid.GuidResult.SetFailure(ParseFailure failureKind)
   ...at Emby.Api.Library.LibraryStructureService.Post(AddMediaPath request)
```

HTTP 500, no other hint in body. Fix: resolve library by `Name` from `GET /Library/VirtualFolders` first, pass its `Guid` as `id`. `ItemId` (decimal one) also fails same way — not Guid either.

Process name `EmbyServer` (+ `embytray` notification-area helper), default port `8096`. Config dir `%AppData%\Emby-Server\programdata\config\system.xml` (server settings, no secrets). Logs: `%AppData%\Emby-Server\programdata\logs\embyserver.txt` — on any 500, tail this before re-guessing request shape; full .NET stack trace with exact failing call sits right there.

## SABnzbd

Auth: **query-string** `apikey=<key>` param, not header. Base: `http://<host>:<port>/api`.

| Action                 | URL params                                                                                                                                                        |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Get config (a section) | `mode=get_config&section=<misc\|categories>&apikey=...&output=json` → body is `{"config": {"categories": [...]}}` (nested under `config`, not bare array)         |
| Set a misc key         | `mode=set_config&section=misc&keyword=<download_dir\|complete_dir\|dirscan_dir\|...>&value=<val>&apikey=...&output=json`                                          |
| Set a category's dir   | `mode=set_config&section=categories&keyword=<catname>&dir=<path>&apikey=...&output=json`                                                                          |
| Delete a category      | `mode=del_config&section=categories&keyword=<catname>&apikey=...&output=json`                                                                                     |
| List job history       | `mode=history&limit=<N>&apikey=...&output=json` → `.history.slots[]` has `name`, `category`, `status`, `storage` (final path), `path` (temp path), `fail_message` |

**Wrong-but-tempting endpoint.** `mode=set_cat` doesn't update existing category's dir reliably — use `mode=set_config&section=categories&keyword=<name>&dir=<path>` instead.

**Category names force-lowercased.** Sending `keyword=TV` creates/updates category whose stored `name` is `tv` — `dir` value casing kept exact as sent, identifier itself not. Title-Case category identifiers not possible in SABnzbd; only folder paths stylable — keep every app's category-string references (Sonarr `tvCategory`, Radarr `movieCategory`, Prowlarr `clientCategory`) lowercase matching reality, independent of destination folders' casing.

**"Rename" a category** = delete old keyword then set_config new one; no in-place rename endpoint.

**PowerShell string-interpolation gotcha.** `"$sabBase?mode=..."` resolves `$sabBase` empty since `?` not valid variable-name-terminator char at that spot — write `"${sabBase}?mode=..."` instead.

**Wildcard/default category.** Literal `*` fallback for anything with no explicit category; URL-encode as `%2A` when used as `keyword` value in query string.

## Logs, process, and live queue status

| App      | Log files                                                                                                                | Process name(s)                                           | Default port |
| -------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------- | ------------ |
| Sonarr   | `C:\ProgramData\Sonarr\logs\sonarr.*.txt` (main), `sonarr.debug.*.txt`                                                   | `Sonarr`                                                  | 8989         |
| Radarr   | `C:\ProgramData\Radarr\logs\radarr*.txt`                                                                                 | `Radarr` (windowless) / `Radarr.Console` (visible window) | 7878         |
| Prowlarr | `C:\ProgramData\Prowlarr\logs\prowlarr*.txt`                                                                             | `Prowlarr`                                                | 9696         |
| SABnzbd  | `<sabnzbd config dir>\logs\sabnzbd.log` (dir varies by install — this instance: `C:\Users\Lance\AppData\Local\sabnzbd\`) | `SABnzbd`                                                 | 8080         |
| Emby     | `%AppData%\Emby-Server\programdata\logs\embyserver.txt`                                                                  | `EmbyServer`, `embytray`                                  | 8096         |

All three *arr apps log to rolling numbered files (`.0.txt`, `.1.txt`, ...) — highest number or no-suffix file most recent; `*.debug.*` files verbose, only useful when `LogLevel` in `config.xml` set to `debug` (all three observed already running `debug` this setup).

Tail newest lines without opening file:

```powershell
Get-Content "C:\ProgramData\Sonarr\logs\sonarr.txt" -Tail 50
```

**Live queue (currently downloading/importing), not just history:**

- Sonarr/Radarr: `GET /api/v3/queue` — items mid-import/mid-download with `status`, `trackedDownloadStatus`, `errorMessage`
- SABnzbd: `mode=queue&apikey=...&output=json` — active NZBs with `percentage`, `timeleft`, `cat`
- Prowlarr: no queue of own (dispatches only) — check *arr app or SABnzbd queue instead

**Process management (Windows):**

```powershell
Get-Process Sonarr,Radarr,Prowlarr,SABnzbd -ErrorAction SilentlyContinue
Stop-Process -Name Radarr -Force   # match actual running name — Radarr vs Radarr.Console
```

Config-file edits (`config.xml`, `sabnzbd.ini`) made while app running get overwritten next write/exit — stop process first, edit, restart. API-driven changes (everything above) need no restart or stop.

# Dated incident/config records

Historical fixes and verified-state snapshots for the arr stack. Read when
debugging autostart, boot-time bind failures, or stale-queue symptoms —
not needed for normal API usage.

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

| App      | Autostart mechanism                                        | Account                     | Bind                    | Firewall                                                         |
| -------- | ----------------------------------------------------------- | ---------------------------- | ------------------------ | ------------------------------------------------------------------ |
| Sonarr   | native Windows Service, Auto                               | `NT AUTHORITY\LocalService` | `*` (config.xml)        | `NzbDrone` rule, `RemoteAddress=100.64.0.0/10`                   |
| Radarr   | native Windows Service, Auto                               | `NT AUTHORITY\LocalService` | `*` (config.xml)        | `NzbDrone` rule, `RemoteAddress=100.64.0.0/10`                   |
| Prowlarr | native Windows Service, Auto                               | `NT AUTHORITY\LocalService` | `*` (config.xml)        | `NzbDrone` rule, `RemoteAddress=100.64.0.0/10`                   |
| SABnzbd  | native Windows Service, Auto (`sc create`, not installer)  | `LocalSystem`               | `0.0.0.0` (sabnzbd.ini) | `SABnzbd`/`SABnzbd-console` rules, `RemoteAddress=100.64.0.0/10` |

qBittorrent: manual start only, no service/task — user decision 2026-08-29, don't wrap as service/task unless asked again. No network bind/firewall entry (not a listening service the way the four above are).
Emby: login Startup-folder shortcut (`%AppData%\Microsoft\Windows\Start Menu\Programs\Startup\Emby Server.lnk`), runs as current user. Same — no bind/firewall entry.

No arr-related Scheduled Task. Servy (`C:\Program Files\Servy`) manage
only `ClaudeRemoteControl` — unrelated, not use for any above.

SABnzbd duplicate-process outage and stale-queue recovery playbooks
stay in the main SKILL.md's triage sections — those are active
runbooks, not historical records.

## Bazarr autostart (open)

Bazarr autostart mechanism: TBD (not yet confirm as service/task).

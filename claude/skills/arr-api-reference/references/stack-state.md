# Stack state — current autostart, bind, and firewall config

Current state only. Read before touching service config.

## Bind and firewall

Sonarr/Radarr/Prowlarr/SABnzbd bind to wildcard (`*` in `config.xml` for Sonarr/Radarr/Prowlarr, `0.0.0.0` in `sabnzbd.ini` for SABnzbd) — needed because a Tailscale-IP bind fails at boot with `SocketException 10049` before `tailscaled` reassigns the IP. Reachability is locked down by Windows Firewall instead: `NzbDrone`/`SABnzbd`/`SABnzbd-console` inbound rules scope `RemoteAddress = 100.64.0.0/10` (Tailscale CGNAT range, matches SAB's own `local_ranges` setting).

SABnzbd has no Windows Service via its installer by default. It ships one native (pywin32 `ServiceFramework` in `SABnzbd.py`, verb `install|update|remove|start|stop|restart`), but the install command mis-detects a non-interactive/session-0 shell and refuses (`StartServiceCtrlDispatcher` error). Workaround: `sc.exe create` directly, plus write `-f <inifile>` into `HKLM\SYSTEM\CurrentControlSet\services\SABnzbd\CommandLine` (`REG_MULTI_SZ`), the same way the installer's `set_serv_parms` would.

## Autostart inventory

| App        | Autostart mechanism                                        | Account                     | Bind                    | Firewall                                                         |
| ---------- | ----------------------------------------------------------- | ---------------------------- | ------------------------ | ------------------------------------------------------------------ |
| Sonarr     | native Windows Service, Auto                               | `NT AUTHORITY\LocalService` | `*` (config.xml)        | `NzbDrone` rule, `RemoteAddress=100.64.0.0/10`                   |
| Radarr     | native Windows Service, Auto                               | `NT AUTHORITY\LocalService` | `*` (config.xml)        | `NzbDrone` rule, `RemoteAddress=100.64.0.0/10`                   |
| Prowlarr   | native Windows Service, Auto                               | `NT AUTHORITY\LocalService` | `*` (config.xml)        | `NzbDrone` rule, `RemoteAddress=100.64.0.0/10`                   |
| SABnzbd    | native Windows Service, Auto (`sc create`, not installer)  | `LocalSystem`               | `0.0.0.0` (sabnzbd.ini) | `SABnzbd`/`SABnzbd-console` rules, `RemoteAddress=100.64.0.0/10` |
| Bazarr     | native Windows Service (`Bazarr`)                           | —                            | —                        | —                                                                    |
| qBittorrent | manual start only, by decision — no service/task           | —                            | no listening service     | none                                                                 |
| Emby       | login Startup-folder shortcut (`%AppData%\Microsoft\Windows\Start Menu\Programs\Startup\Emby Server.lnk`), runs as current user | current user | —            | none                                                                 |

No arr-related Scheduled Task. Servy (`C:\Program Files\Servy`) manages only `ClaudeRemoteControl` — unrelated.

Live down/stuck/zombie-process/stale-queue diagnostic runbooks live in `triage.md`, not here.

#!/usr/bin/env python3
from __future__ import annotations

import shutil
import subprocess
import time
import zipfile
from datetime import datetime
from pathlib import Path

import requests

from arr_scripts import ArrApp, HOST, get_arr_api_key, get_sab_api_key

GOOGLE_DRIVE_FS_EXE = Path(r"C:\Program Files\Google\Drive File Stream\130.0.2.0\GoogleDriveFS.exe")


def backup_arr_stack() -> list[Path]:
    configs = Path(r"D:\My Drive\Computer\Configs")

    if not configs.exists():
        subprocess.Popen([str(GOOGLE_DRIVE_FS_EXE)])
        for _ in range(20):
            time.sleep(1)
            if configs.exists():
                break
    if not configs.exists():
        raise FileNotFoundError(f"Path not found, not creating it: {configs}")

    date = datetime.now().strftime("%Y-%m-%d")

    ports: dict[ArrApp, int] = {"Sonarr": 8989, "Radarr": 7878, "Prowlarr": 9696}
    for app, port in ports.items():
        key = get_arr_api_key(app)
        ver = "v1" if app == "Prowlarr" else "v3"
        resp = requests.post(
            f"http://{HOST}:{port}/api/{ver}/command",
            headers={"X-Api-Key": key},
            json={"name": "Backup"},
        )
        resp.raise_for_status()
        time.sleep(3)
        backups_dir = Path(rf"C:\ProgramData\{app}\Backups\manual")
        zips = sorted(backups_dir.glob("*.zip"), key=lambda p: p.stat().st_mtime, reverse=True)
        shutil.copy2(zips[0], configs / f"{app} - {date}.zip")

    sab_key = get_sab_api_key()
    resp = requests.get(f"http://{HOST}:8080/api?mode=config&name=create_backup&apikey={sab_key}&output=json")
    resp.raise_for_status()
    sab_backup_path = Path(resp.json()["value"]["message"])
    shutil.copy2(sab_backup_path, configs / f"SABnzbd - {date}.zip")

    qbt_dir = Path.home() / "AppData" / "Roaming" / "qBittorrent"
    qbt_zip = configs / f"qBittorrent - {date}.zip"
    with zipfile.ZipFile(qbt_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for item in qbt_dir.iterdir():
            if item.name == "lockfile":
                continue
            if item.is_file():
                zf.write(item, item.relative_to(qbt_dir))
            else:
                for sub in item.rglob("*"):
                    if sub.is_file():
                        zf.write(sub, sub.relative_to(qbt_dir))

    return sorted(configs.glob(f"* - {date}.zip"))


def main() -> None:
    for f in backup_arr_stack():
        print(f)


if __name__ == "__main__":
    main()

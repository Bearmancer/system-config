#!/usr/bin/env python3
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Literal

import requests

ArrApp = Literal["Sonarr", "Radarr", "Prowlarr"]
DownloadClientApp = Literal["Sonarr", "Radarr"]

HOST = "100.86.121.94"
ARR_PORTS: dict[str, int] = {"Sonarr": 8989, "Radarr": 7878, "Prowlarr": 9696}
ARR_API_VER: dict[str, str] = {"Sonarr": "v3", "Radarr": "v3", "Prowlarr": "v1"}
SAB_URL = f"http://{HOST}:8080/api"


def get_arr_api_key(app: ArrApp) -> str:
    tree = ET.parse(Path(rf"C:\ProgramData\{app}\config.xml"))
    api_key = tree.getroot().find("ApiKey")
    return api_key.text if api_key is not None and api_key.text is not None else ""


def get_sab_api_key() -> str:
    ini_path = Path.home() / "AppData" / "Local" / "sabnzbd" / "sabnzbd.ini"
    pattern = re.compile(r"^api_key\s*=\s*(.+)", re.IGNORECASE)
    for line in ini_path.read_text().splitlines():
        m = pattern.match(line)
        if m:
            return m.group(1).strip()
    raise ValueError(f"api_key not found in {ini_path}")


def arr_base_and_headers(app: ArrApp) -> tuple[str, dict[str, str]]:
    base = f"http://{HOST}:{ARR_PORTS[app]}/api/{ARR_API_VER[app]}"
    return base, {"X-Api-Key": get_arr_api_key(app)}


def sab_api(**params: Any) -> Any:
    params.setdefault("apikey", get_sab_api_key())
    params.setdefault("output", "json")
    resp = requests.get(SAB_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def merge_arr_fields(fields: list[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: dict[str, dict[str, Any]] = {}
    for f in fields:
        deduped[f["name"]] = f
    return list(deduped.values())


def set_arr_field_value(fields: list[dict[str, Any]], name: str, value: Any) -> None:
    for f in fields:
        if f["name"] == name:
            f["value"] = value


def add_arr_download_client(
    app: DownloadClientApp,
    implementation: str,
    dc_host: str,
    dc_port: int,
    api_key: str,
    category_value: str,
) -> Any:
    category_field = {"Sonarr": "tvCategory", "Radarr": "movieCategory"}[app]
    base, headers = arr_base_and_headers(app)

    resp = requests.get(f"{base}/downloadclient/schema", headers=headers, timeout=10)
    resp.raise_for_status()
    tmpl = next(
        (
            t
            for t in resp.json()
            if t["implementation"].casefold() == implementation.casefold()
        ),
        None,
    )
    if tmpl is None:
        raise ValueError(
            f"No download client implementation named '{implementation}' in {app}'s schema."
        )

    set_arr_field_value(tmpl["fields"], "host", dc_host)
    set_arr_field_value(tmpl["fields"], "port", dc_port)
    set_arr_field_value(tmpl["fields"], "apiKey", api_key)
    set_arr_field_value(tmpl["fields"], category_field, category_value)

    body = {
        "enable": True,
        "protocol": tmpl["protocol"],
        "priority": 1,
        "name": implementation,
        "fields": tmpl["fields"],
        "implementationName": tmpl["implementationName"],
        "implementation": tmpl["implementation"],
        "configContract": tmpl["configContract"],
        "infoLink": tmpl["infoLink"],
        "tags": [],
    }

    resp = requests.post(f"{base}/downloadclient", headers=headers, json=body, timeout=10)
    resp.raise_for_status()
    return resp.json()


def set_prowlarr_category_map(
    client_id: int, mapping: dict[str, Any], default_category: str | None = None
) -> Any:
    base, headers = arr_base_and_headers("Prowlarr")

    resp = requests.get(f"{base}/downloadclient/{client_id}", headers=headers, timeout=10)
    resp.raise_for_status()
    client = resp.json()
    client["fields"] = merge_arr_fields(client["fields"])

    if default_category:
        set_arr_field_value(client["fields"], "category", default_category)

    client["categories"] = [
        {"clientCategory": k, "categories": v} for k, v in mapping.items()
    ]

    resp = requests.put(
        f"{base}/downloadclient/{client_id}", headers=headers, json=client, timeout=10
    )
    resp.raise_for_status()
    return resp.json()


def set_sab_category_dir(category: str, dir_: str) -> Any:
    return sab_api(mode="set_config", section="categories", keyword=category, dir=dir_)


def remove_sab_category(category: str) -> Any:
    return sab_api(mode="del_config", section="categories", keyword=category)


def set_qbt_category_dir(category: str, dir_: str) -> None:
    resp = requests.post(
        f"http://{HOST}:8088/api/v2/torrents/editCategory",
        data={"category": category, "savePath": dir_},
        timeout=10,
    )
    resp.raise_for_status()


def find_arr_job(name_match: str) -> list[dict[str, Any]]:
    hist = sab_api(mode="history", limit=200)
    pattern = re.compile(re.escape(name_match), re.IGNORECASE)
    return [
        {
            "name": slot["name"],
            "category": slot["category"],
            "status": slot["status"],
            "storage": slot["storage"],
            "path": slot["path"],
            "fail_message": slot["fail_message"],
        }
        for slot in hist["history"]["slots"]
        if pattern.search(slot["name"])
    ]


def add_emby_library_path(
    library_name: str, path: str, api_key: str, emby_base: str = "http://localhost:8096"
) -> Any:
    headers = {"X-Emby-Token": api_key}
    resp = requests.get(f"{emby_base}/Library/VirtualFolders", headers=headers, timeout=10)
    resp.raise_for_status()
    libs = resp.json()
    target = next(
        (lib for lib in libs if lib["Name"].casefold() == library_name.casefold()), None
    )
    if target is None:
        raise ValueError(f"No Emby library named '{library_name}'.")

    resp = requests.post(
        f"{emby_base}/Library/VirtualFolders/Paths",
        params={"id": target["Guid"], "path": path, "refreshLibrary": "true"},
        headers=headers,
        timeout=10,
    )
    resp.raise_for_status()
    if resp.text:
        try:
            return resp.json()
        except ValueError:
            return resp.text
    return None

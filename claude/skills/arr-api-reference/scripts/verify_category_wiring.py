#!/usr/bin/env python3
"""Cross-check category-string wiring across Sonarr/Radarr/Prowlarr/SABnzbd.

Usage: python verify_category_wiring.py
Exit code 0 = all wired correctly, 1 = mismatch found (see stdout).
"""
from __future__ import annotations

import sys

import requests

from arr_scripts import arr_base_and_headers, sab_api


def get_sab_categories() -> set[str]:
    cats = sab_api(mode="get_config", section="categories")["config"]["categories"]
    return {c["name"] for c in cats if c["name"] != "*"}


def get_arr_download_client_categories(app: str, category_field: str) -> dict[str, str]:
    """Returns {download_client_name: category_value}."""
    base, headers = arr_base_and_headers(app)
    resp = requests.get(f"{base}/downloadclient", headers=headers, timeout=10)
    resp.raise_for_status()
    out: dict[str, str] = {}
    for client in resp.json():
        for field in client["fields"]:
            if field["name"] == category_field and field.get("value"):
                out[client["name"]] = field["value"]
    return out


def get_prowlarr_client_categories() -> dict[str, list[str]]:
    """Returns {download_client_name: [clientCategory, ...]}."""
    base, headers = arr_base_and_headers("Prowlarr")
    resp = requests.get(f"{base}/downloadclient", headers=headers, timeout=10)
    resp.raise_for_status()
    out: dict[str, list[str]] = {}
    for client in resp.json():
        mapped = [c["clientCategory"] for c in client.get("categories", [])]
        if mapped:
            out[client["name"]] = mapped
    return out


def main() -> int:
    problems: list[str] = []

    sab_cats = get_sab_categories()
    sonarr_cats = get_arr_download_client_categories("Sonarr", "tvCategory")
    radarr_cats = get_arr_download_client_categories("Radarr", "movieCategory")
    prowlarr_cats = get_prowlarr_client_categories()

    arr_cats: dict[str, str] = {**sonarr_cats, **radarr_cats}

    for client_name, category in arr_cats.items():
        if category not in sab_cats:
            problems.append(
                f"'{client_name}' download-client category '{category}' "
                f"has no matching SABnzbd category (SAB has: {sorted(sab_cats)})"
            )

    prowlarr_all_mapped = {c for cats in prowlarr_cats.values() for c in cats}
    for category in arr_cats.values():
        if category not in prowlarr_all_mapped:
            problems.append(
                f"category '{category}' used by an arr download-client has no "
                f"Prowlarr clientCategory mapping — matched jobs fall through to "
                f"Prowlarr's default client category instead"
            )

    if problems:
        print(f"Category wiring mismatch ({len(problems)}):")
        for p in problems:
            print(f"  - {p}")
        return 1

    print(f"Category wiring OK. SAB categories: {sorted(sab_cats)}")
    print(f"Sonarr: {sonarr_cats}")
    print(f"Radarr: {radarr_cats}")
    print(f"Prowlarr mapped: {prowlarr_cats}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

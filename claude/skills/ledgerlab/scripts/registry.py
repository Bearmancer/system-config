"""Load and validate the routing registry; classify vendor errors; list surfaces by paradigm."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT / "registry" / "registry.yaml"
ROLES_PATH = ROOT / "registry" / "roles.yaml"
ROUTE_KINDS = ("mcp", "cli", "post", "http", "local")
LADDERS = ("discovery", "fetch")
ERROR_CLASSES = ("bad_key", "out_of_credit", "blocked", "rate_limit")


class RegistryError(ValueError):
    pass


@dataclass(frozen=True)
class Surface:
    id: str
    server: str
    capability: str
    paradigm: str
    ladder: str
    cost: str
    routes: dict[str, list[str]]
    wired: bool
    pool: str | None


def load(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    validate(data)
    return data


def surfaces(reg: dict[str, Any]) -> dict[str, Surface]:
    out: dict[str, Surface] = {}
    for sname, server in reg["servers"].items():
        for cname, cap in server["capabilities"].items():
            sid = f"{sname}.{cname}"
            out[sid] = Surface(
                id=sid,
                server=sname,
                capability=cname,
                paradigm=cap["paradigm"],
                ladder=cap["ladder"],
                cost=cap["cost"],
                routes=cap["routes"],
                wired=bool(server.get("wired", False)),
                pool=server.get("pool"),
            )
    return out


def discovery_surfaces(reg: dict[str, Any], paradigm: str, wired_only: bool = True) -> list[Surface]:
    return [
        s
        for s in surfaces(reg).values()
        if s.ladder == "discovery" and s.paradigm == paradigm and (s.wired or not wired_only)
    ]


def round_paradigms(reg: dict[str, Any], round_no: int) -> list[str]:
    order = reg["round_order"]
    if not 1 <= round_no <= len(order):
        raise RegistryError(f"round {round_no} outside 1..{len(order)}")
    return list(order[round_no - 1])


def validate(reg: dict[str, Any]) -> None:
    problems: list[str] = []
    paradigms = set(reg.get("paradigms", []))
    if reg.get("schema") != 1:
        problems.append("schema must be 1")
    for i, group in enumerate(reg.get("round_order", []), 1):
        for p in group:
            if p not in paradigms:
                problems.append(f"round_order[{i}] unknown paradigm {p}")
    if len(reg.get("round_order", [])) != reg.get("max_rounds"):
        problems.append("round_order length must equal max_rounds")
    sids: set[str] = set()
    for sname, server in reg.get("servers", {}).items():
        if server.get("keyed") and not server.get("pool"):
            problems.append(f"{sname}: keyed server needs a pool")
        for cname, cap in server.get("capabilities", {}).items():
            sid = f"{sname}.{cname}"
            sids.add(sid)
            if cap.get("paradigm") not in paradigms:
                problems.append(f"{sid}: unknown paradigm {cap.get('paradigm')}")
            if cap.get("ladder") not in LADDERS:
                problems.append(f"{sid}: ladder must be one of {LADDERS}")
            routes = cap.get("routes") or {}
            if not routes:
                problems.append(f"{sid}: no routes")
            for kind in routes:
                if kind not in ROUTE_KINDS:
                    problems.append(f"{sid}: unknown route kind {kind}")
        for cls in (server.get("errors") or {}):
            if cls not in ERROR_CLASSES:
                problems.append(f"{sname}: unknown error class {cls}")
        for cls in server.get("unverified", []):
            if cls not in ERROR_CLASSES:
                problems.append(f"{sname}: unknown unverified class {cls}")
    for sid in reg.get("fetch_ladder", []):
        if sid not in sids:
            problems.append(f"fetch_ladder: unknown surface {sid}")
    for i, rnd in enumerate(reg.get("round_order", []), 1):
        if not any(
            cap["paradigm"] in rnd and cap["ladder"] == "discovery" and server.get("wired")
            for server in reg["servers"].values()
            for cap in server["capabilities"].values()
        ):
            problems.append(f"round {i} {rnd} has no wired discovery surface")
    if problems:
        raise RegistryError("; ".join(problems))


def classify_error(reg: dict[str, Any], server: str, status: object = None, code: object = None) -> str:
    """Return bad_key, out_of_credit, blocked, rate_limit or unknown.

    Matches the status number or the vendor code (case-insensitive substring) against the server's table.
    A class listed in `unverified` never matches, so unknown failures are retried once and logged
    instead of burning a key (ADR 0017).
    """
    srv = reg["servers"].get(server)
    if srv is None:
        raise RegistryError(f"unknown server {server}")
    needles = {str(x).lower() for x in (status, code) if x not in (None, "", "-")}
    for cls in ERROR_CLASSES:
        if cls in srv.get("unverified", []):
            continue
        for pattern in (srv.get("errors") or {}).get(cls, []):
            p = str(pattern).lower()
            if any(p == n or p in n for n in needles):
                return cls
    return "unknown"


def load_roles(path: Path = ROLES_PATH) -> dict[str, dict[str, str]]:
    """Load model roles; reject any checking role that shares a family with the author (ADR 0013)."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    roles = data["roles"]
    author_family = roles["author"]["family"]
    for name in data["checking_roles"]:
        if roles[name]["family"] == author_family:
            raise RegistryError(f"role {name} shares family {author_family} with the author")
    return roles


def model_families(roles: dict[str, dict[str, str]]) -> dict[str, str]:
    """Map every model id (without a `#variant` suffix) and role name to its model family."""
    out: dict[str, str] = {}
    for name, role in roles.items():
        out[name] = role["family"]
        out[role["model"].split("#")[0]] = role["family"]
    return out


def family_of(families: dict[str, str], read_by: str) -> str | None:
    return families.get(read_by.split("#")[0])

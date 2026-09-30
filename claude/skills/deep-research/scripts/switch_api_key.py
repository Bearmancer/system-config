#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ctypes
import hashlib
import os
import re
import sys
import tempfile
import winreg
from dataclasses import dataclass
from pathlib import Path

SERVICE_CHOICES = [
    "tavily",
    "exa",
    "firecrawl",
    "dappier",
    "agentql",
    "scrapegraph",
    "context7",
    "brave",
    "apify",
    "brightdata",
    "browserbase",
    "all",
]


@dataclass(frozen=True)
class ServiceInfo:
    env_var: str
    pool_pattern: str


SERVICE_MAP: dict[str, ServiceInfo] = {
    "tavily": ServiceInfo("TAVILY_API_KEY", r"^(?P<acct>[A-Z0-9]+)_TAVILY_API_KEY$"),
    "exa": ServiceInfo("EXA_API_KEY", r"^(?P<acct>[A-Z0-9]+)_EXA_API_KEY$"),
    "firecrawl": ServiceInfo(
        "FIRECRAWL_API_KEY", r"^(?P<acct>[A-Z0-9]+)_(FIRECRAWL|FIRECRAWLER)_API_KEY$"
    ),
    "dappier": ServiceInfo("DAPPIER_API_KEY", r"^(?P<acct>[A-Z0-9]+)_DAPPIER_API_KEY$"),
    "agentql": ServiceInfo("AGENTQL_API_KEY", r"^(?P<acct>[A-Z0-9]+)_AGENTQL_API_KEY$"),
    "scrapegraph": ServiceInfo(
        "SCRAPEGRAPH_API_KEY",
        r"^(?P<acct>[A-Z0-9]+)_(SCRAPEGRAPH|SCRAPEGRAPHAI)_API_KEY$",
    ),
    "context7": ServiceInfo(
        "CONTEXT7_API_KEY", r"^(?P<acct>[A-Z0-9]+)_CONTEXT7_API_KEY$"
    ),
    "brave": ServiceInfo("BRAVE_API_KEY", r"^(?P<acct>[A-Z0-9]+)_BRAVE_API_KEY$"),
    "apify": ServiceInfo("APIFY_TOKEN", r"^(?P<acct>[A-Z0-9]+)_APIFY_TOKEN$"),
    "brightdata": ServiceInfo(
        "BRIGHTDATA_API_KEY", r"^(?P<acct>[A-Z0-9]+)_BRIGHTDATA_API_KEY$"
    ),
    "browserbase": ServiceInfo(
        "BROWSERBASE_API_KEY", r"^(?P<acct>[A-Z0-9]+)_BROWSERBASE_API_KEY$"
    ),
}


DEFAULT_SECRETS_DIR = Path.home() / ".config" / "opencode" / "secrets"

MATERIALIZE_SERVICES = [
    "agentql",
    "apify",
    "brightdata",
    "browserbase",
    "exa",
    "firecrawl",
    "scrapegraph",
    "tavily",
]


def write_secret(secrets_dir: Path, svc: str, value: str) -> Path:
    secrets_dir.mkdir(parents=True, exist_ok=True)
    target = secrets_dir / svc
    fd, tmp = tempfile.mkstemp(dir=secrets_dir, prefix=f".{svc}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as f:
            f.write(value)
        os.replace(tmp, target)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return target


def materialize_secret(
    dotenv: dict[str, str], svc: str, secrets_dir: Path, dry_run: bool = False
) -> str:
    if (secrets_dir / svc).exists():
        return f"{svc}: exists"
    pool = get_pool(dotenv, svc)
    value = get_active_value(SERVICE_MAP[svc].env_var)
    if not value and pool:
        value = pool[sorted(pool)[0]]
    if not value:
        raise ValueError(f"{svc}: no active key or pool account; file not created")
    if dry_run:
        return f"{svc}: WHATIF create (no write)"
    write_secret(secrets_dir, svc, value)
    return f"{svc}: created"


SECTION_ALIASES = {"scrapegraphai": "scrapegraph"}


class DotEnv(dict):
    sections: dict[str, dict[str, str]]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sections = {}


def _parse_assignment(line: str) -> tuple[str, str] | None:
    if line.startswith("export "):
        line = line[len("export ") :]
    idx = line.find("=")
    if idx < 1:
        return None
    name = line[:idx].strip()
    val = line[idx + 1 :].strip()
    if len(val) >= 2 and (
        (val[0] == '"' and val[-1] == '"') or (val[0] == "'" and val[-1] == "'")
    ):
        val = val[1:-1].strip()
    return (name, val) if name else None


def _section_service(title: str) -> str | None:
    key = re.sub(r"[^a-z0-9]", "", title.lower())
    key = SECTION_ALIASES.get(key, key)
    return key if key in SERVICE_MAP else None


def get_dotenv_map(path: Path) -> DotEnv:
    if not path.exists():
        raise FileNotFoundError(f"env file not found: {path}")
    env_map = DotEnv()
    section: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        if line[0] in "#;":
            heading = re.match(r"^(#+)\s*(.*)$", line)
            if heading and "=" not in heading.group(2):
                if len(heading.group(1)) == 1:
                    section = None
                elif len(heading.group(1)) == 2:
                    section = _section_service(heading.group(2))
            continue
        parsed = _parse_assignment(line)
        if not parsed:
            continue
        name, val = parsed
        env_map[name] = val
        if section:
            env_map.sections.setdefault(section, {})[name] = val
    return env_map


def get_pool(dotenv: dict[str, str], svc: str) -> dict[str, str]:
    pattern = re.compile(SERVICE_MAP[svc].pool_pattern, re.IGNORECASE)
    pool: dict[str, str] = {}
    for k, v in dotenv.items():
        m = pattern.match(k)
        if m:
            acct = m.group("acct")
            if acct and v:
                pool[acct] = v
    for k, v in getattr(dotenv, "sections", {}).get(svc, {}).items():
        m = pattern.match(k)
        acct = m.group("acct") if m else k
        if acct and v:
            pool[acct] = v
    return pool


def get_fingerprint(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:8]


def get_active_account(pool: dict[str, str], active: str | None) -> str | None:
    if not active:
        return None
    for k, v in pool.items():
        if v == active:
            return k
    return None


def _get_user_env_var(name: str) -> str | None:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return str(value)
    except (FileNotFoundError, OSError):
        return None


def _set_user_env_var(name: str, value: str) -> None:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)


def _broadcast_env_change() -> None:
    try:
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        SMTO_ABORTIFHUNG = 2
        result = ctypes.c_ulong()
        ctypes.windll.user32.SendMessageTimeoutW(
            HWND_BROADCAST,
            WM_SETTINGCHANGE,
            0,
            "Environment",
            SMTO_ABORTIFHUNG,
            1000,
            ctypes.byref(result),
        )
    except Exception:
        pass


def get_active_value(env_var: str) -> str | None:
    v = _get_user_env_var(env_var)
    if not v:
        v = os.environ.get(env_var)
    return v


def show_pool_state(dotenv: dict[str, str], svc: str) -> str:
    env_var = SERVICE_MAP[svc].env_var
    pool = get_pool(dotenv, svc)
    active = get_active_value(env_var)
    active_acct = get_active_account(pool, active)
    parts: list[str] = []
    for n in sorted(pool.keys()):
        fp = get_fingerprint(pool[n])
        parts.append(f"{n}({fp})*" if n == active_acct else f"{n}({fp})")
    if active_acct:
        state = f"active={active_acct}"
    elif active:
        state = "active=NOT-IN-POOL"
    else:
        state = "active=UNSET"
    return f"{svc:<11} {state:<22} pool: {' '.join(parts)}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Rotate a masked pool of API keys. The active key is written to "
            "~/.config/opencode/secrets/<service> (read by OpenCode via {file:}) "
            "and to a User-scope environment variable."
        )
    )
    parser.add_argument("--service", required=True, choices=SERVICE_CHOICES)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--set", dest="set_account", default=None)
    parser.add_argument("--next", action="store_true")
    parser.add_argument("--env-path", default=str(Path.home() / ".secrets" / ".env"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--secrets-dir", default=str(DEFAULT_SECRETS_DIR))
    parser.add_argument(
        "--materialize",
        action="store_true",
        help="create every missing secrets file (--service all, or one service)",
    )
    args = parser.parse_args()

    try:
        dotenv = get_dotenv_map(Path(args.env_path))
        secrets_dir = Path(args.secrets_dir)

        if args.materialize:
            targets = MATERIALIZE_SERVICES if args.service == "all" else [args.service]
            failed = False
            for svc in targets:
                try:
                    print(materialize_secret(dotenv, svc, secrets_dir, args.dry_run))
                except ValueError as exc:
                    failed = True
                    print(str(exc), file=sys.stderr)
            sys.exit(1 if failed else 0)

        if args.service == "all":
            if args.set_account or args.next:
                raise ValueError("'-all' supports listing only (no -Set/-Next)")
            for svc in SERVICE_MAP:
                print(show_pool_state(dotenv, svc))
            sys.exit(0)

        if args.list or (not args.set_account and not args.next):
            print(show_pool_state(dotenv, args.service))
            sys.exit(0)

        env_var = SERVICE_MAP[args.service].env_var
        pool = get_pool(dotenv, args.service)
        if not pool:
            raise ValueError(f"pool empty for {args.service}: move to next chain step")
        names = sorted(pool.keys())
        active = get_active_value(env_var)
        active_acct = get_active_account(pool, active)

        target_acct = args.set_account
        if not target_acct:
            if active_acct:
                i = names.index(active_acct)
                target_acct = names[(i + 1) % len(names)]
            else:
                target_acct = names[0]
        if target_acct not in pool:
            raise ValueError(
                f"account '{target_acct}' not in {args.service} pool: {', '.join(names)}"
            )

        target_fp = get_fingerprint(pool[target_acct])
        if not args.dry_run:
            write_secret(secrets_dir, args.service, pool[target_acct])
        if active_acct == target_acct:
            print(f"{args.service}: already active {target_acct}({target_fp})")
            sys.exit(0)

        if args.dry_run:
            print(f"{args.service}: WHATIF -> {target_acct}({target_fp}). (no write)")
        else:
            _set_user_env_var(env_var, pool[target_acct])
            os.environ[env_var] = pool[target_acct]
            _broadcast_env_change()
            if active_acct:
                from_desc = f"{active_acct}({get_fingerprint(pool[active_acct])})"
            else:
                from_desc = "UNSET"
            print(
                f"{args.service}: {from_desc} -> {target_acct}({target_fp}). "
                "Secrets file updated; the OpenCode config watcher reconnects the MCP server."
            )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

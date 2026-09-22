"""Sync local opencode + curated claude config to OCI as whole files. No flags except --dry-run.

Usage:
    python mirror_config_oci.py [--dry-run]

Syncs:
  ~/.config/opencode  ->  oci:~/.config/opencode   (opencode.json adapted Win->Linux;
                          includes AGENTS.md, tui.json, package.json, agents/,
                          commands/, skills/, plugins/)
  ~/.claude/skills, ~/.claude/plugins, ~/.claude/settings.json, ~/.claude/CLAUDE.md
                      ->  oci:~/.claude/            (sessions, transcripts, cache,
                          credentials and all machine state excluded)

Never synced: node_modules, .env, *.bak*, tasks/, logs, machine state.
Remote snapshot tarball is taken before every real run. Stdlib only, needs `ssh oci`.
"""

from __future__ import annotations

import difflib
import json
import re
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REMOTE = "oci"
HOME = Path.home()
LOCAL_OPENCODE = HOME / ".config" / "opencode"
LOCAL_CLAUDE = HOME / ".claude"
REMOTE_OPENCODE = "~/.config/opencode"
REMOTE_CLAUDE = "~/.claude"

OPENCODE_FILES = ["AGENTS.md", "tui.json", "package.json"]
OPENCODE_DIRS = ["agents", "commands", "skills", "plugins"]
CLAUDE_FILES = ["settings.json", "CLAUDE.md"]
CLAUDE_DIRS = ["skills", "plugins"]
EXCLUDE_RES = [
    re.compile(p)
    for p in (
        r"\.bak\.",
        r"\.bak$",
        r"^node_modules",
        r"^\.env$",
        r"last_inuse_sweep$",
        r"catalog-cache",
        r"usage-cache",
        r"\.marketplaces\.json$",
    )
]
EXCLUDE_DIRS = {"cache", "marketplaces", "data", "__pycache__", "node_modules", ".git"}
MAX_BYTES = 50 * 1024 * 1024  # abort if staging bigger than this

LINUX_FIREFOX_PROFILE = "/home/ubuntu/.firefox-devtools-mcp/profile"
LINUX_FIREFOX_BIN = "/usr/bin/firefox"


def strip_jsonc(text: str) -> str:
    out: list[str] = []
    i, n = 0, len(text)
    in_str = False
    while i < n:
        ch = text[i]
        if in_str:
            out.append(ch)
            if ch == "\\" and i + 1 < n:
                out.append(text[i + 1])
                i += 2
                continue
            if ch == '"':
                in_str = False
            i += 1
            continue
        if ch == '"':
            in_str = True
            out.append(ch)
            i += 1
            continue
        if ch == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        out.append(ch)
        i += 1
    return re.sub(r",\s*([}\]])", r"\1", "".join(out))


def adapt_win2linux(cfg: dict[str, Any]) -> dict[str, Any]:
    cfg = json.loads(json.dumps(cfg))
    shell = str(cfg.get("shell", ""))
    if re.match(r"^[A-Za-z]:\\\\", shell) or shell.lower().endswith(".exe"):
        cfg["shell"] = "/bin/bash"
    for section in ("lsp", "mcp"):
        block = cfg.get(section)
        if not isinstance(block, dict):
            continue
        for _name, entry in block.items():
            if not isinstance(entry, dict):
                continue
            cmd = entry.get("command")
            if (
                isinstance(cmd, list)
                and len(cmd) > 2
                and cmd[0] == "cmd"
                and cmd[1] == "/c"
            ):
                entry["command"] = cmd[2:]
    lsp = cfg.get("lsp")
    if isinstance(lsp, dict):
        lsp.pop("powershell", None)  # pwsh absent on OCI
    mcp = cfg.get("mcp")
    if isinstance(mcp, dict) and isinstance(mcp.get("firefox-devtools"), dict):
        ff = mcp["firefox-devtools"]
        if isinstance(ff.get("command"), list):
            fixed: list[str] = []
            skip_next = False
            for tok in ff["command"]:
                if skip_next:
                    skip_next = False
                    continue
                if tok == "--profile-path":
                    fixed += [tok, LINUX_FIREFOX_PROFILE]
                    skip_next = True
                elif tok == "--firefox-path":
                    fixed += [tok, LINUX_FIREFOX_BIN]
                    skip_next = True
                elif re.match(r"^[A-Za-z]:", tok):
                    continue
                else:
                    fixed.append(tok)
            ff["command"] = fixed
    return cfg


def ssh(*args: str, data: bytes | None = None) -> "subprocess.CompletedProcess[bytes]":
    return subprocess.run(["ssh", REMOTE, *args], input=data, capture_output=True)


def excluded(rel: str) -> bool:
    if any(part in EXCLUDE_DIRS for part in rel.split("/")):
        return True
    return any(p.search(rel) for p in EXCLUDE_RES)


def stage_openmode(dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    raw = (LOCAL_OPENCODE / "opencode.jsonc").read_bytes().decode(encoding="utf-8-sig")
    cfg = adapt_win2linux(json.loads(strip_jsonc(raw)))
    (dst / "opencode.json").write_text(
        json.dumps(cfg, indent="\t") + "\n", encoding="utf-8"
    )
    for name in OPENCODE_FILES + OPENCODE_DIRS:
        src = LOCAL_OPENCODE / name
        if not src.exists():
            continue
        if src.is_dir():
            for f in sorted(src.rglob("*")):
                if not f.is_file():
                    continue
                rel = f.relative_to(src).as_posix()
                if excluded(f"{name}/{rel}"):
                    continue
                target = dst / name / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(f.read_bytes())
        elif not excluded(name):
            (dst / name).write_bytes(src.read_bytes())


def stage_claude(dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    for name in CLAUDE_FILES + CLAUDE_DIRS:
        src = LOCAL_CLAUDE / name
        if not src.exists():
            continue
        if src.is_dir():
            for f in sorted(src.rglob("*")):
                if not f.is_file():
                    continue
                rel = f.relative_to(src).as_posix()
                if excluded(f"{name}/{rel}"):
                    continue
                target = dst / name / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(f.read_bytes())
        elif not excluded(name):
            (dst / name).write_bytes(src.read_bytes())


def remote_files(dest: str) -> dict[str, str]:
    p = ssh(f"find {dest} -type f -printf '%P %s\\n' 2>/dev/null | sort")
    if p.returncode != 0:
        raise RuntimeError(f"remote list failed: {p.stderr.decode().strip()}")
    out: dict[str, str] = {}
    for line in p.stdout.decode(errors="replace").splitlines():
        rel, _, size = line.partition(" ")
        out[rel] = size.strip()
    return out


def local_files(dst: Path) -> dict[str, str]:
    return {
        f.relative_to(dst).as_posix(): str(f.stat().st_size)
        for f in dst.rglob("*")
        if f.is_file()
    }


def main() -> int:
    dry_run = "--dry-run" in sys.argv[1:]
    with tempfile.TemporaryDirectory(prefix="oci-sync-") as tmp:
        staging = Path(tmp)
        stage_openmode(staging / "opencode")
        stage_claude(staging / "claude")
        total = sum(f.stat().st_size for f in staging.rglob("*") if f.is_file())
        if total > MAX_BYTES:
            print(
                f"ABORT: staging {total} bytes exceeds {MAX_BYTES} cap.",
                file=sys.stderr,
            )
            return 2
        print(f"staging: {total} bytes")

        for name, dest in (("opencode", REMOTE_OPENCODE), ("claude", REMOTE_CLAUDE)):
            local = local_files(staging / name)
            remote = remote_files(dest)
            new = sorted(set(local) - set(remote))
            gone = sorted(set(remote) - set(local))
            changed = sorted(
                k for k in set(local) & set(remote) if local[k] != remote[k]
            )
            print(
                f"--- {name}: {len(new)} new, {len(changed)} changed, {len(gone)} remote-only"
            )
            for k in new[:20]:
                print(f"  + {k}")
            for k in changed[:20]:
                print(f"  ~ {k} ({remote[k]} -> {local[k]} bytes)")
            for k in gone[:20]:
                print(f"  - remote-only, kept: {k}")

        old = (
            ssh(f"cat {REMOTE_OPENCODE}/opencode.json")
            .stdout.decode(errors="replace")
            .splitlines()
        )
        new_text = (
            (staging / "opencode" / "opencode.json")
            .read_text(encoding="utf-8")
            .splitlines()
        )
        diff = list(
            difflib.unified_diff(
                old,
                new_text,
                fromfile="oci:opencode.json",
                tofile="local:opencode.json",
                lineterm="",
            )
        )
        print(f"--- opencode.json: {len(diff)} diff lines")
        for line in diff[:80]:
            print(line)

        if dry_run:
            print("dry-run done, nothing written.")
            return 0
        if input("Type YES to write to OCI: ").strip() != "YES":
            print("aborted.")
            return 1

        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        snap = ssh(
            f"tar -czf ~/config-sync-{stamp}.tgz {REMOTE_OPENCODE} {REMOTE_CLAUDE} && echo OK"
        )
        if snap.returncode != 0 or b"OK" not in snap.stdout:
            print(f"snapshot FAILED: {snap.stderr.decode().strip()}", file=sys.stderr)
            return 2
        print(f"snapshot: ~/config-sync-{stamp}.tgz")

        for name, dest in (("opencode", REMOTE_OPENCODE), ("claude", REMOTE_CLAUDE)):
            src = staging / name
            with tarfile.open(str(src) + ".tar", "w") as tf:
                tf.add(src, arcname=".")
            tar_bytes = Path(str(src) + ".tar").read_bytes()
            p = ssh(f"mkdir -p {dest} && tar -xf - -C {dest}", data=tar_bytes)
            if p.returncode != 0:
                print(
                    f"transfer {name} FAILED: {p.stderr.decode().strip()}",
                    file=sys.stderr,
                )
                return 2
            print(f"{name}: synced to {REMOTE}:{dest}/")

        v = ssh("opencode mcp list 2>&1 | tail -8")
        print(v.stdout.decode(errors="replace"))
    print("done. Restart opencode on OCI (config loads once at startup).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

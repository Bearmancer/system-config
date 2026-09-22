#!/usr/bin/env python3
"""Weekly backup: mirrors whitelisted local agent config into the repo clone and pushes.

Local files are never modified, moved, or symlinked; the repo receives copies only.
Whitelist and rationale: see README.md. Excludes (plugins, settings, caches) are absent
by design.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_REPO_PATH = Path.home() / ".omo" / "agents-config"
DEFAULT_REMOTE_URL = "https://github.com/Bearmancer/agents-config.git"
LOG_PATH = Path.home() / ".omo" / "agents-config-sync.log"
LOG_MAX_LINES = 500


def write_log(message: str) -> None:
    line = f"{datetime.now():%Y-%m-%d %H:%M:%S} {message}"
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)


def git(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def robocopy(source: Path, destination: Path, extra: list[str]) -> None:
    if not source.exists():
        write_log(f"skip: source missing {source}")
        return
    args = ["robocopy", str(source), str(destination), *extra, "/NFL", "/NDL", "/NJH", "/NJS", "/R:1", "/W:1"]
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode >= 8:
        raise RuntimeError(
            f"robocopy failed with exit {result.returncode} for {source} -> {destination}: {result.stdout}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-path", type=Path, default=DEFAULT_REPO_PATH)
    parser.add_argument("--remote-url", default=DEFAULT_REMOTE_URL)
    args = parser.parse_args()

    repo_path: Path = args.repo_path
    remote_url: str = args.remote_url

    if not (repo_path / ".git").exists():
        write_log(f"clone missing; cloning {remote_url} -> {repo_path}")
        git("clone", remote_url, str(repo_path))

    c = Path.home() / ".claude"
    o = Path.home() / ".config" / "opencode"
    m = Path.home() / ".omo"
    a = Path.home() / ".agents"

    # synced/ and *-workspace excluded: plugin cache + skill-creator eval output, not source material
    robocopy(c, repo_path / "claude", ["CLAUDE.md", "keybindings.json"])
    robocopy(c / "skills", repo_path / "claude" / "skills", ["/MIR", "/XJ", "/XD", "synced", "*-workspace"])

    robocopy(o, repo_path / "opencode", ["AGENTS.md", "opencode.jsonc", "tui.json"])
    robocopy(o / "agents", repo_path / "opencode" / "agents", ["/MIR"])
    robocopy(o / "commands", repo_path / "opencode" / "commands", ["/MIR"])
    robocopy(o / "skills", repo_path / "opencode" / "skills", ["/MIR"])

    robocopy(m, repo_path / "omo", ["omo.jsonc"])
    robocopy(m / "scripts", repo_path / "omo" / "scripts", ["/MIR"])

    # cache/ and codegraph/ excluded: regenerable via yt-dlp / codegraph init, not source material
    robocopy(m / "ulw-research", repo_path / "omo" / "ulw-research", ["/MIR"])
    robocopy(m / "teach", repo_path / "omo" / "teach", ["/MIR"])
    robocopy(m / "plans", repo_path / "omo" / "plans", ["/MIR"])
    robocopy(m / "notepads", repo_path / "omo" / "notepads", ["/MIR"])

    # /XJ skips junction/symlink-linked skills (plugin installs): reinstallable, not backups
    robocopy(a, repo_path / "agents", [".skill-lock.json"])
    robocopy(a / "skills", repo_path / "agents" / "skills", ["/MIR", "/XJ"])

    git("add", "-A", cwd=repo_path)

    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=repo_path)
    if diff.returncode != 0:
        stamp = f"{datetime.now():%Y-%m-%d %H:%M}"
        git(
            "-c", "user.name=Bearmancer",
            "-c", "user.email=lordlance@outlook.in",
            "commit", "-m", f"Sync agent config {stamp}",
            cwd=repo_path,
        )
        git("push", "origin", "HEAD", cwd=repo_path)
        write_log(f"pushed sync commit {stamp}")
    else:
        write_log("no changes")

    if LOG_PATH.exists():
        lines = LOG_PATH.read_text(encoding="utf-8").splitlines()
        if len(lines) > LOG_MAX_LINES:
            LOG_PATH.write_text("\n".join(lines[-LOG_MAX_LINES:]) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except subprocess.CalledProcessError as e:
        write_log(f"{' '.join(e.cmd)} failed (exit {e.returncode}): {e.stderr}")
        sys.exit(1)

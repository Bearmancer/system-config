#!/usr/bin/env python3
"""Weekly backup: mirrors whitelisted local agent config into the repo clone and pushes.

Local files are never modified, moved, or symlinked; the repo receives copies only.
Whitelist and rationale: see README.md. Excludes (plugins, settings, caches) are absent
by design.
"""
from __future__ import annotations

import argparse
import fnmatch
import shutil
import stat
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


def copy_files(source: Path, destination: Path, names: list[str]) -> None:
    """Additive copy of named files only (matches prior non-/MIR robocopy calls)."""
    if not source.exists():
        return
    destination.mkdir(parents=True, exist_ok=True)
    for name in names:
        src_file = source / name
        if src_file.exists():
            shutil.copy2(src_file, destination / name)


def is_reparse_point(entry: Path) -> bool:
    """True for symlinks AND NTFS junctions/mount points (os.path.islink misses junctions)."""
    attrs = getattr(entry.lstat(), "st_file_attributes", None)
    if attrs is None:
        return entry.is_symlink()
    return bool(attrs & stat.FILE_ATTRIBUTE_REPARSE_POINT)


def mirror_dir(
    source: Path,
    destination: Path,
    exclude_dirs: frozenset[str] = frozenset(),
    exclude_globs: tuple[str, ...] = (),
    skip_junctions: bool = False,
) -> None:
    """Recursive mirror: destination ends up identical to source (matches robocopy /MIR)."""
    if not source.exists():
        return
    destination.mkdir(parents=True, exist_ok=True)

    def excluded(name: str) -> bool:
        return name in exclude_dirs or any(fnmatch.fnmatch(name, g) for g in exclude_globs)

    kept_names = set()
    for entry in source.iterdir():
        if excluded(entry.name):
            continue
        if skip_junctions and is_reparse_point(entry):
            continue
        kept_names.add(entry.name)
        dst_entry = destination / entry.name
        if entry.is_dir():
            mirror_dir(entry, dst_entry, exclude_dirs, exclude_globs, skip_junctions)
        else:
            shutil.copy2(entry, dst_entry)

    for entry in destination.iterdir():
        if entry.name in kept_names:
            continue
        if entry.is_dir():
            shutil.rmtree(entry)
        else:
            entry.unlink()


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
    copy_files(c, repo_path / "claude", ["CLAUDE.md", "keybindings.json"])
    mirror_dir(c / "skills", repo_path / "claude" / "skills", exclude_dirs=frozenset({"synced"}), exclude_globs=("*-workspace",), skip_junctions=True)

    copy_files(o, repo_path / "opencode", ["AGENTS.md", "opencode.jsonc", "tui.json"])
    mirror_dir(o / "agents", repo_path / "opencode" / "agents")
    mirror_dir(o / "commands", repo_path / "opencode" / "commands")
    mirror_dir(o / "skills", repo_path / "opencode" / "skills")

    copy_files(m, repo_path / "omo", ["omo.jsonc"])
    mirror_dir(m / "scripts", repo_path / "omo" / "scripts")

    # cache/ and codegraph/ excluded: regenerable via yt-dlp / codegraph init, not source material
    mirror_dir(m / "ulw-research", repo_path / "omo" / "ulw-research")
    mirror_dir(m / "teach", repo_path / "omo" / "teach")
    mirror_dir(m / "plans", repo_path / "omo" / "plans")
    mirror_dir(m / "notepads", repo_path / "omo" / "notepads")

    # skip_junctions skips junction/symlink-linked skills (plugin installs): reinstallable, not backups
    copy_files(a, repo_path / "agents", [".skill-lock.json"])
    mirror_dir(a / "skills", repo_path / "agents" / "skills", skip_junctions=True)

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

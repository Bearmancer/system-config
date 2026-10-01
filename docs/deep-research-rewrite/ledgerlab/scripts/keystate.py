"""Exhausted-key memory and rotation lock (ADR 0017).

State file (JSON) stores key fingerprints only, never keys:
{pool: {fingerprint: {"exhausted_at": ISO, "reset": "monthly"|"unknown"}}}.
A key is skipped until its reset window passes; an unknown window means probe again after 24 h.
`pool_exhausted` is true when every key in the pool is still inside its window (the early-terminate trigger).
`rotation_lock` makes one agent rotate while others wait, then retry once.
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

UNKNOWN_WINDOW = timedelta(hours=24)


def fingerprint(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:12]


def _parse(ts: str) -> datetime:
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def _stamp(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def reset_at(exhausted_at: datetime, reset: str) -> datetime:
    if reset == "monthly":
        year, month = (exhausted_at.year + 1, 1) if exhausted_at.month == 12 else (exhausted_at.year, exhausted_at.month + 1)
        return exhausted_at.replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
    return exhausted_at + UNKNOWN_WINDOW


class KeyState:
    def __init__(self, path: Path):
        self.path = path
        self.data: dict[str, dict[str, dict[str, str]]] = {}
        if path.exists():
            self.data = json.loads(path.read_text(encoding="utf-8"))

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=1, sort_keys=True), encoding="utf-8")
        os.replace(tmp, self.path)

    def mark_exhausted(self, pool: str, fp: str, now: datetime | None = None, reset: str = "unknown") -> None:
        now = now or datetime.now(timezone.utc)
        self.data.setdefault(pool, {})[fp] = {"exhausted_at": _stamp(now), "reset": reset}
        self.save()

    def is_available(self, pool: str, fp: str, now: datetime | None = None) -> bool:
        """True if the key was never exhausted or its reset window has passed (probe once on resume)."""
        entry = self.data.get(pool, {}).get(fp)
        if entry is None:
            return True
        now = now or datetime.now(timezone.utc)
        return now >= reset_at(_parse(entry["exhausted_at"]), entry.get("reset", "unknown"))

    def available(self, pool: str, fps: list[str], now: datetime | None = None) -> list[str]:
        return [fp for fp in fps if self.is_available(pool, fp, now)]

    def pool_exhausted(self, pool: str, fps: list[str], now: datetime | None = None) -> bool:
        return bool(fps) and not self.available(pool, fps, now)

    def clear(self, pool: str, fp: str) -> None:
        self.data.get(pool, {}).pop(fp, None)
        self.save()


class LockTimeout(TimeoutError):
    pass


@contextlib.contextmanager
def rotation_lock(lock_dir: Path, pool: str, timeout: float = 60.0, stale_after: float = 120.0, poll: float = 0.05) -> Iterator[None]:
    """Exclusive per-pool lock. The first agent to hit credit-out holds it while rotating."""
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock = lock_dir / f"{pool}.lock"
    deadline = time.monotonic() + timeout
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            break
        except FileExistsError:
            with contextlib.suppress(FileNotFoundError):
                if time.time() - lock.stat().st_mtime > stale_after:
                    lock.unlink()
                    continue
            if time.monotonic() >= deadline:
                raise LockTimeout(f"rotation lock for {pool} busy")
            time.sleep(poll)
    try:
        yield
    finally:
        with contextlib.suppress(FileNotFoundError):
            lock.unlink()

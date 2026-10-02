"""Exhausted-key memory, rotation lock, and unknown-failure counter (ADR 0017).

State file (JSON) stores fingerprints only, never keys:
{"keys": {pool: {fingerprint: {"exhausted_at": ISO, "reset": "monthly"|"unknown"}}},
 "generation": {pool: int}, "unknown": {pool: {signature: [url fingerprints]}}}.

- A key is skipped until its reset window passes; an unknown window means probe again after 24 h.
  `pool_exhausted` is true when every key in the pool is still inside its window (the early-terminate trigger).
- `generation` counts completed rotations per pool. An agent reads it before using a key; on credit-out it calls
  `rotate_once` with that value, so one exhaustion event causes one rotation: later agents find the generation moved
  and just retry with the new key.
- Locks are OS file locks (msvcrt / fcntl). They die with the holding process, so there is no stale-lock takeover.
- Every read and write of the state file happens under one state lock, so concurrent agents never see a half-written file.
- `note_unknown_failure` implements "rotate only after the same unknown failure hits 2 different URLs".
"""
from __future__ import annotations

import contextlib
import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Callable, Iterator

if os.name == "nt":
    import msvcrt
else:
    import fcntl

UNKNOWN_WINDOW = timedelta(hours=24)
UNKNOWN_URLS_TO_ROTATE = 2


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


class LockTimeout(TimeoutError):
    pass


def _try_lock(fd: int) -> None:
    if os.name == "nt":
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
    else:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)


def _unlock(fd: int) -> None:
    if os.name == "nt":
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    else:
        fcntl.flock(fd, fcntl.LOCK_UN)


@contextlib.contextmanager
def file_lock(path: Path, timeout: float = 60.0, poll: float = 0.05) -> Iterator[None]:
    """Exclusive OS lock on `path`, held until the block exits or the process dies. The file is never deleted."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR)
    try:
        deadline = time.monotonic() + timeout
        while True:
            try:
                _try_lock(fd)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise LockTimeout(f"lock {path.name} busy") from None
                time.sleep(poll)
        try:
            yield
        finally:
            _unlock(fd)
    finally:
        os.close(fd)


def _replace(src: Path, dst: Path, attempts: int = 5) -> None:
    """os.replace, retried briefly: Windows refuses while a scanner or reader holds the destination open."""
    for i in range(attempts):
        try:
            os.replace(src, dst)
            return
        except PermissionError:
            if i == attempts - 1:
                raise
            time.sleep(0.02 * (i + 1))


class KeyState:
    def __init__(self, path: Path):
        self.path = path
        self.lock_dir = path.parent / f"{path.stem}.locks"
        self.refresh()

    def _read(self) -> dict[str, dict]:
        data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else {}
        for section in ("keys", "generation", "unknown"):
            data.setdefault(section, {})
        return data

    def _mutate(self, fn: Callable[[dict[str, dict]], object]) -> object:
        """Read-modify-write under the state lock, so concurrent agents never lose each other's updates."""
        with file_lock(self.lock_dir / "state.lock", timeout=10.0):
            self.data = self._read()
            result = fn(self.data)
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(self.data, indent=1, sort_keys=True), encoding="utf-8")
            _replace(tmp, self.path)
            return result

    def refresh(self) -> None:
        """Re-read under the state lock: on Windows a read racing `os.replace` raises PermissionError."""
        with file_lock(self.lock_dir / "state.lock", timeout=10.0):
            self.data = self._read()

    def mark_exhausted(self, pool: str, fp: str, now: datetime | None = None, reset: str = "unknown") -> None:
        stamp = _stamp(now or datetime.now(timezone.utc))

        def mark(d: dict[str, dict]) -> None:
            d["keys"].setdefault(pool, {})[fp] = {"exhausted_at": stamp, "reset": reset}

        self._mutate(mark)

    def is_available(self, pool: str, fp: str, now: datetime | None = None) -> bool:
        """True if the key was never exhausted or its reset window has passed (probe once on resume)."""
        entry = self.data["keys"].get(pool, {}).get(fp)
        if entry is None:
            return True
        now = now or datetime.now(timezone.utc)
        return now >= reset_at(_parse(entry["exhausted_at"]), entry.get("reset", "unknown"))

    def available(self, pool: str, fps: list[str], now: datetime | None = None) -> list[str]:
        return [fp for fp in fps if self.is_available(pool, fp, now)]

    def pool_exhausted(self, pool: str, fps: list[str], now: datetime | None = None) -> bool:
        return bool(fps) and not self.available(pool, fps, now)

    def clear(self, pool: str, fp: str) -> None:
        self._mutate(lambda d: d["keys"].get(pool, {}).pop(fp, None))

    def generation(self, pool: str) -> int:
        return int(self.data["generation"].get(pool, 0))

    def bump_generation(self, pool: str) -> None:
        def bump(d: dict[str, dict]) -> None:
            d["generation"][pool] = int(d["generation"].get(pool, 0)) + 1
            d["unknown"].pop(pool, None)

        self._mutate(bump)

    def note_unknown_failure(self, pool: str, signature: str, url: str) -> bool:
        """Record an unclassified failure. True once the same signature has hit 2 distinct URLs: rotate (ADR 0017)."""
        ufp = fingerprint(url)

        def note(d: dict[str, dict]) -> bool:
            urls = d["unknown"].setdefault(pool, {}).setdefault(signature, [])
            if ufp not in urls:
                urls.append(ufp)
            return len(urls) >= UNKNOWN_URLS_TO_ROTATE

        return bool(self._mutate(note))


@contextlib.contextmanager
def rotation_lock(lock_dir: Path, pool: str, timeout: float = 60.0, poll: float = 0.05) -> Iterator[None]:
    """Exclusive per-pool lock. The agent that hit credit-out holds it while rotating."""
    with file_lock(lock_dir / f"rotate-{pool}.lock", timeout=timeout, poll=poll):
        yield


def rotate_once(
    state_path: Path, pool: str, seen_generation: int, rotate: Callable[[KeyState], None], timeout: float = 60.0
) -> bool:
    """Run `rotate` unless another agent already rotated this pool since `seen_generation` was read.

    Returns True if this call rotated, False if the exhaustion event was already handled (retry once with the
    current key). The generation is re-read after the lock is acquired, so waiters never rotate a second time.
    """
    lock_dir = KeyState(state_path).lock_dir
    with rotation_lock(lock_dir, pool, timeout=timeout):
        state = KeyState(state_path)
        if state.generation(pool) != seen_generation:
            return False
        rotate(state)
        state.bump_generation(pool)
        return True

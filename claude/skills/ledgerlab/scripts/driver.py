"""Run driver: phase state machine with a persisted run.yaml (ADR 0020).

Phases are re-entrant: `resume` re-runs the phase that was in progress. Real phase work (launching OpenCode agents,
publishing) plugs in through `handlers`; this module owns state, suspension, failure reports and wave control.
Exit codes: 0 done, 1 failed, 2 suspended (NEEDS_YOU.md written).
"""
from __future__ import annotations

import concurrent.futures as cf
import subprocess
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Protocol

import yaml

# ADR 0020: learn and rules share one phase list; verify extracts claims from the input and renders claim cards (ADR 0023).
_LEARN_PHASES = ["infer_mode", "ingest", "discover", "verify", "write", "conformance", "layout", "render", "gates", "publish", "live_check"]
PHASES: dict[str, list[str]] = {
    "learn": _LEARN_PHASES,
    "rules": _LEARN_PHASES,
    "verify": ["infer_mode", "ingest", "extract", "verify", "render", "gates", "publish", "live_check"],
}
# infer_mode runs before the mode is known; the full phase list is chosen right after it.
BOOT_PHASES = ["infer_mode"]

DONE, FAILED, SUSPENDED, RUNNING = "done", "failed", "suspended", "running"
EXIT = {DONE: 0, FAILED: 1, SUSPENDED: 2}


class PoolExhausted(Exception):
    """Every key of one MCP pool is exhausted (ADR 0017): stop and ask the user."""

    def __init__(self, pool: str, detail: str = ""):
        super().__init__(f"key pool {pool} exhausted")
        self.pool = pool
        self.detail = detail


class GateFailed(Exception):
    def __init__(self, gate: str, problems: list[str]):
        super().__init__(f"gate {gate} failed")
        self.gate = gate
        self.problems = problems


class RateLimited(Exception):
    pass


@dataclass
class PhaseResult:
    data: dict[str, Any] = field(default_factory=dict)
    mode: str | None = None  # set by infer_mode


@dataclass
class RunState:
    run_id: str
    topic: str
    prompt: str
    mode: str | None = None
    phase: str = "infer_mode"
    status: str = RUNNING
    log: list[dict[str, Any]] = field(default_factory=list)
    needs_user: str | None = None
    failure: dict[str, Any] | None = None
    created_at: str = ""

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.__dict__, sort_keys=False, allow_unicode=True)

    @classmethod
    def from_file(cls, path: Path) -> "RunState":
        return cls(**yaml.safe_load(path.read_text(encoding="utf-8")))


Handler = Callable[["Driver"], PhaseResult | None]


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_run_id(clock: Callable[[], str] = now) -> str:
    return clock().replace(":", "").replace("-", "")


class Driver:
    def __init__(self, run_dir: Path, state: RunState, handlers: dict[str, Handler], clock: Callable[[], str] = now):
        self.run_dir = run_dir
        self.state = state
        self.handlers = handlers
        self.clock = clock

    @classmethod
    def start(cls, run_dir: Path, topic: str, prompt: str, handlers: dict[str, Handler], run_id: str | None = None, clock: Callable[[], str] = now) -> "Driver":
        run_dir.mkdir(parents=True, exist_ok=True)
        state = RunState(run_id=run_id or new_run_id(clock), topic=topic, prompt=prompt, created_at=clock())
        d = cls(run_dir, state, handlers, clock)
        d.save()
        return d

    @classmethod
    def resume(cls, run_dir: Path, handlers: dict[str, Handler], clock: Callable[[], str] = now) -> "Driver":
        state = RunState.from_file(run_dir / "run.yaml")
        if state.status == DONE:
            return cls(run_dir, state, handlers, clock)
        state.status, state.needs_user, state.failure = RUNNING, None, None
        (run_dir / "NEEDS_YOU.md").unlink(missing_ok=True)
        d = cls(run_dir, state, handlers, clock)
        d.save()
        return d

    def save(self) -> None:
        (self.run_dir / "run.yaml").write_text(self.state.to_yaml(), encoding="utf-8")

    def phases(self) -> list[str]:
        return PHASES[self.state.mode] if self.state.mode else BOOT_PHASES

    def run(self) -> int:
        st = self.state
        while st.status == RUNNING:
            phase = st.phase
            handler = self.handlers.get(phase)
            try:
                if handler is None:
                    raise NotImplementedError(f"no handler for phase {phase}")
                result = handler(self) or PhaseResult()
            except PoolExhausted as exc:
                self._suspend(phase, exc)
                break
            except GateFailed as exc:
                self._fail(phase, f"gate {exc.gate} failed", exc.problems)
                break
            except Exception as exc:  # noqa: BLE001 - any handler error must leave a report, not a stack trace
                self._fail(phase, f"{type(exc).__name__}: {exc}", traceback.format_exc().splitlines()[-6:])
                break
            st.log.append({"phase": phase, "at": self.clock(), "data": result.data})
            if phase == "infer_mode":
                if result.mode not in PHASES:
                    self._fail(phase, f"infer_mode returned unknown mode {result.mode!r}", [])
                    break
                st.mode = result.mode
            phases = self.phases()
            idx = phases.index(phase)
            if idx + 1 >= len(phases):
                st.status = DONE
                st.phase = "done"
            else:
                st.phase = phases[idx + 1]
            self.save()
        self.save()
        self.write_record()
        return EXIT[st.status]

    def _suspend(self, phase: str, exc: PoolExhausted) -> None:
        st = self.state
        st.status = SUSPENDED
        st.needs_user = f"Key pool {exc.pool} is exhausted during phase {phase}."
        (self.run_dir / "NEEDS_YOU.md").write_text(
            f"# Run {st.run_id} needs you\n\n"
            f"- Topic: {st.topic}\n- Phase: {phase}\n- Reason: {st.needs_user}\n"
            f"- Detail: {exc.detail or '-'}\n\n"
            "Add keys or wait for the reset window, then resume: re-run the driver on this run directory.\n"
            "State is saved; settled claims are kept.\n",
            encoding="utf-8",
        )

    def _fail(self, phase: str, reason: str, problems: list[Any]) -> None:
        st = self.state
        st.status = FAILED
        st.failure = {"phase": phase, "reason": reason, "problems": [str(p) for p in problems]}
        body = "\n".join(f"- {p}" for p in st.failure["problems"]) or "- (none recorded)"
        (self.run_dir / "REPORT.md").write_text(
            f"# Run {st.run_id} failed\n\n- Topic: {st.topic}\n- Mode: {st.mode}\n- Phase: {phase}\n- Reason: {reason}\n\n## Problems\n\n{body}\n\n"
            "Nothing was published. The draft branch keeps the ledger; re-run to resume.\n",
            encoding="utf-8",
        )

    def write_record(self) -> None:
        st = self.state
        record = {
            "run_id": st.run_id,
            "topic": st.topic,
            "mode": st.mode,
            "status": st.status,
            "phases": [{"phase": e["phase"], "at": e["at"]} for e in st.log],
            "failure": st.failure,
        }
        (self.run_dir / "RUN_RECORD.yaml").write_text(yaml.safe_dump(record, sort_keys=False), encoding="utf-8")


# ---- waves (ADR 0020) -------------------------------------------------------------------------------

@dataclass
class TaskResult:
    ok: bool
    value: Any = None
    error: str | None = None
    attempts: int = 1


def run_wave(
    tasks: dict[str, Any],
    fn: Callable[[Any], Any],
    size: int = 8,
    timeout: float | None = None,
    retries: int = 1,
    max_rate_limit_retries: int = 5,
) -> tuple[dict[str, TaskResult], int]:
    """Run tasks in parallel batches. Halve the batch size on RateLimited. Errors get `retries` retries, then fail.

    `timeout` is one shared wall-clock deadline per batch (every task in a batch starts together). A timed-out task
    is requeued for its retry, but its original future is kept: when the key comes up again, a still-running original
    means failure (a Python thread cannot be killed, and a retry would run a second copy beside it); an original that
    finished meanwhile is used as is (result) or retried (error). The executor is abandoned (`shutdown(wait=False)`)
    so a hung task never blocks the wave. Agent steps must carry their own subprocess timeout (see OpencodeRunner).

    Returns (results, final_size).
    """
    results: dict[str, TaskResult] = {}
    queue = list(tasks)
    tries = {k: 0 for k in tasks}
    rl_tries = {k: 0 for k in tasks}
    timed_out: dict[str, cf.Future] = {}
    while queue:
        batch, queue = queue[:size], queue[size:]
        halve = False
        live = []
        for key in batch:
            orig = timed_out.pop(key, None)
            if orig is None:
                live.append(key)
            elif not orig.done():
                results[key] = TaskResult(False, error=f"timeout after {timeout}s (original still running, not re-run)", attempts=tries[key])
            elif orig.exception() is None:
                results[key] = TaskResult(True, orig.result(), attempts=tries[key])
            else:
                live.append(key)
        batch = live
        if not batch:
            continue
        pool = cf.ThreadPoolExecutor(max_workers=len(batch))
        try:
            futures = {pool.submit(fn, tasks[k]): k for k in batch}
            for key in batch:
                tries[key] += 1
            done, pending = cf.wait(futures, timeout=timeout)
            for fut in done:
                key = futures[fut]
                try:
                    results[key] = TaskResult(True, fut.result(), attempts=tries[key])
                except RateLimited:
                    halve = True
                    rl_tries[key] += 1
                    if rl_tries[key] > max_rate_limit_retries:
                        results[key] = TaskResult(False, error="rate limited", attempts=tries[key])
                    else:
                        queue.append(key)
                except Exception as exc:  # noqa: BLE001
                    if tries[key] <= retries:
                        queue.append(key)
                    else:
                        results[key] = TaskResult(False, error=f"{type(exc).__name__}: {exc}", attempts=tries[key])
            for fut in pending:
                key = futures[fut]
                if tries[key] <= retries:
                    timed_out[key] = fut
                    queue.append(key)
                else:
                    results[key] = TaskResult(False, error=f"timeout after {timeout}s (still running)", attempts=tries[key])
        finally:
            pool.shutdown(wait=False, cancel_futures=True)
        if halve:
            size = max(1, size // 2)
    return results, size


# ---- agent runner -----------------------------------------------------------------------------------

class AgentRunner(Protocol):
    def run(self, role: str, prompt: str) -> str: ...


class OpencodeRunner:
    """Launch one OpenCode agent step. `--model provider/model#variant` and `--format json` match `opencode run --help` (v2.0.21)."""

    def __init__(self, roles: dict[str, dict[str, str]], timeout: float = 900.0, exec_fn: Callable[..., Any] = subprocess.run):
        self.roles = roles
        self.timeout = timeout
        self.exec_fn = exec_fn

    def command(self, role: str, prompt: str) -> list[str]:
        return ["opencode", "run", "--model", self.roles[role]["model"], "--format", "json", prompt]

    def run(self, role: str, prompt: str) -> str:
        proc = self.exec_fn(self.command(role, prompt), capture_output=True, text=True, timeout=self.timeout, check=False)
        if proc.returncode != 0:
            raise RuntimeError(f"opencode run failed ({proc.returncode}): {proc.stderr[:300]}")
        return proc.stdout

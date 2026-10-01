import json
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import driver
import gen_routing_table
import infer_mode
import keystate
import log_attempt
import registry
from driver import Driver, GateFailed, PhaseResult, PoolExhausted, RateLimited


@pytest.fixture(scope="module")
def reg():
    return registry.load()


# ---- infer_mode -------------------------------------------------------------------------------------

@pytest.mark.parametrize(
    "prompt,mode",
    [
        ("Explain the Saudi military paradox", "learn"),
        ("fact-check this video transcript", "verify"),
        ("is it true that Russia lost 90% of its officers", "verify"),
        ("how do I play Ark Nova with 4 players", "rules"),
        ("summarise /home/me/Downloads/Arche_Nova_Rules_EN.pdf", "rules"),
        ("fact-check the Ark Nova rulebook claims", "verify"),
        ("teach me the Thirty Years' War", "learn"),
    ],
)
def test_infer_mode(prompt, mode):
    assert infer_mode.infer_mode(prompt)[0] == mode


def test_pasted_claim_list_is_verify():
    text = "Here is what he said:\n- Russia lost most of its officers in 2022\n- Sanctions had no effect on output\n- The ruble never fell below 100\n"
    assert infer_mode.infer_mode(text)[0] == "verify"


def test_short_list_is_not_verify():
    assert infer_mode.infer_mode("topics:\n- a\n- b\n- c\n")[0] == "learn"


# ---- log_attempt ------------------------------------------------------------------------------------

def _rec(reg, **kw):
    base = dict(claim="c1", round_no=1, surface="tavily.search", route="mcp", url="https://x.org", status="ok")
    base.update(kw)
    return log_attempt.build_record(reg, **base)


def test_log_attempt_fills_paradigm_and_ladder(reg):
    rec = _rec(reg, content=b"hello", now=datetime(2026, 10, 1, tzinfo=timezone.utc))
    assert rec["paradigm"] == "keyword" and rec["ladder"] == "discovery"
    assert rec["content_hash"] and rec["at"] == "2026-10-01T00:00:00Z"


@pytest.mark.parametrize(
    "kw",
    [
        {"surface": "ghost.search"},
        {"surface": "brave.search", "route": "mcp"},  # not wired
        {"route": "post"},  # tavily.search has no post route
        {"round_no": 6},
        {"status": "weird"},
        {"status": "ok", "error_class": "blocked"},
        {"query_variant": "nonsense"},
    ],
)
def test_log_attempt_rejects(reg, kw):
    with pytest.raises(log_attempt.AttemptError):
        _rec(reg, **kw)


def test_log_attempt_cli_appends(tmp_path):
    f = tmp_path / "attempts.jsonl"
    script = Path(log_attempt.__file__)
    args = [sys.executable, str(script), "--file", str(f), "--claim", "c1", "--round", "2", "--surface", "exa.search", "--route", "mcp", "--status", "ok", "--url", "https://x.org"]
    assert subprocess.run(args, capture_output=True).returncode == 0
    assert subprocess.run(args, capture_output=True).returncode == 0
    rows = [json.loads(x) for x in f.read_text().splitlines()]
    assert len(rows) == 2 and rows[0]["paradigm"] == "semantic"
    bad = subprocess.run(args[:-6] + ["--surface", "nope.x", "--route", "mcp", "--status", "ok"], capture_output=True)
    assert bad.returncode == 1


# ---- keystate ---------------------------------------------------------------------------------------

def test_keystate_window_and_pool_exhaustion(tmp_path):
    ks = keystate.KeyState(tmp_path / "ks.json")
    t0 = datetime(2026, 10, 1, 12, tzinfo=timezone.utc)
    fps = [keystate.fingerprint(k) for k in ("k1", "k2")]
    ks.mark_exhausted("firecrawl", fps[0], t0)
    assert ks.available("firecrawl", fps, t0) == [fps[1]]
    assert not ks.pool_exhausted("firecrawl", fps, t0)
    ks.mark_exhausted("firecrawl", fps[1], t0)
    assert ks.pool_exhausted("firecrawl", fps, t0 + timedelta(hours=1))
    assert not ks.pool_exhausted("firecrawl", fps, t0 + timedelta(hours=25))  # unknown window: probe after 24h


def test_keystate_monthly_reset_and_persistence(tmp_path):
    p = tmp_path / "ks.json"
    ks = keystate.KeyState(p)
    t0 = datetime(2026, 12, 20, tzinfo=timezone.utc)
    ks.mark_exhausted("apify", "abc", t0, reset="monthly")
    again = keystate.KeyState(p)
    assert not again.is_available("apify", "abc", datetime(2026, 12, 31, tzinfo=timezone.utc))
    assert again.is_available("apify", "abc", datetime(2027, 1, 1, tzinfo=timezone.utc))
    assert "k1" not in p.read_text()  # fingerprints only


def test_rotation_lock_is_exclusive(tmp_path):
    with keystate.rotation_lock(tmp_path, "exa"):
        with pytest.raises(keystate.LockTimeout):
            with keystate.rotation_lock(tmp_path, "exa", timeout=0.1):
                pass
    with keystate.rotation_lock(tmp_path, "exa", timeout=0.1):
        pass  # released


def test_rotation_lock_breaks_stale_lock(tmp_path):
    lock = tmp_path / "exa.lock"
    lock.write_text("999999")
    old = time.time() - 600
    import os

    os.utime(lock, (old, old))
    with keystate.rotation_lock(tmp_path, "exa", timeout=0.5, stale_after=60):
        pass


# ---- routing table drift ----------------------------------------------------------------------------

def test_routing_md_is_up_to_date(reg):
    assert gen_routing_table.render(reg) == gen_routing_table.OUT.read_text(encoding="utf-8")


# ---- roles ------------------------------------------------------------------------------------------

def test_roles_checkers_differ_from_author():
    roles = driver.load_roles(registry.ROOT / "registry" / "roles.yaml")
    assert roles["author"]["family"] not in {roles[r]["family"] for r in ("extractor", "verifier", "media")}


def test_roles_rejects_same_family(tmp_path):
    p = tmp_path / "roles.yaml"
    p.write_text("schema: 1\nroles:\n  author: {model: a, family: x}\n  verifier: {model: b, family: x}\nchecking_roles: [verifier]\n")
    with pytest.raises(ValueError, match="shares family"):
        driver.load_roles(p)


def test_opencode_runner_command_and_failure():
    roles = {"author": {"model": "p/m"}}

    class P:
        returncode, stdout, stderr = 1, "", "boom"

    r = driver.OpencodeRunner(roles, exec_fn=lambda *a, **k: P())
    assert r.command("author", "hi")[:4] == ["opencode", "run", "--model", "p/m"]
    with pytest.raises(RuntimeError, match="boom"):
        r.run("author", "hi")


# ---- driver -----------------------------------------------------------------------------------------

CLOCK = iter(f"2026-10-01T00:00:{i:02d}Z" for i in range(1, 60))


def clock():
    return next(CLOCK)


def handlers(mode="learn", boom=None):
    h = {}
    for ph in set(driver.PHASES["learn"]) | set(driver.PHASES["verify"]):
        h[ph] = lambda d: PhaseResult()
    h["infer_mode"] = lambda d: PhaseResult(mode=mode)
    h.update(boom or {})
    return h


def test_learn_run_completes_and_writes_record(tmp_path):
    d = Driver.start(tmp_path, "saudi", "explain Saudi military", handlers(), run_id="r1", clock=clock)
    assert d.run() == 0
    assert d.state.status == "done"
    rec = (tmp_path / "RUN_RECORD.yaml").read_text()
    assert "infer_mode" in rec and "live_check" in rec


def test_verify_mode_skips_write_phases(tmp_path):
    seen = []
    h = handlers("verify")
    for ph in driver.PHASES["learn"]:
        h[ph] = (lambda p: lambda d: seen.append(p))(ph)
    h["infer_mode"] = lambda d: PhaseResult(mode="verify")
    Driver.start(tmp_path, "t", "fact-check", h, clock=clock).run()
    assert "write" not in seen and "layout" not in seen and "extract" not in seen  # extract has no learn-handler here
    assert seen[-1] == "live_check"


def test_pool_exhaustion_suspends_then_resume_continues(tmp_path):
    state = {"calls": 0}

    def verify(d):
        state["calls"] += 1
        if state["calls"] == 1:
            raise PoolExhausted("firecrawl", "all 9 keys out of credit")

    h = handlers(boom={"verify": verify})
    d = Driver.start(tmp_path, "t", "p", h, clock=clock)
    assert d.run() == 2
    assert d.state.status == "suspended" and d.state.phase == "verify"
    assert "firecrawl" in (tmp_path / "NEEDS_YOU.md").read_text()
    d2 = Driver.resume(tmp_path, h, clock=clock)
    assert not (tmp_path / "NEEDS_YOU.md").exists()
    assert d2.run() == 0 and state["calls"] == 2  # re-entrant: phase re-ran


def test_gate_failure_writes_report_and_stops(tmp_path):
    def gates(d):
        raise GateFailed("ledger-check", ["c3 true-bar", "c9 open-at-publish"])

    d = Driver.start(tmp_path, "t", "p", handlers(boom={"gates": gates}), clock=clock)
    assert d.run() == 1
    report = (tmp_path / "REPORT.md").read_text()
    assert "c3 true-bar" in report and "Nothing was published" in report
    assert "publish" not in [e["phase"] for e in d.state.log]


def test_unexpected_error_fails_with_report_and_missing_handler_is_reported(tmp_path):
    h = handlers(boom={"ingest": lambda d: 1 / 0})
    assert Driver.start(tmp_path / "a", "t", "p", h, clock=clock).run() == 1
    assert "ZeroDivisionError" in (tmp_path / "a" / "REPORT.md").read_text()
    assert Driver.start(tmp_path / "b", "t", "p", {"infer_mode": lambda d: PhaseResult(mode="learn")}, clock=clock).run() == 1
    assert "no handler for phase ingest" in (tmp_path / "b" / "REPORT.md").read_text()


def test_unknown_mode_fails(tmp_path):
    h = handlers(boom={"infer_mode": lambda d: PhaseResult(mode="poetry")})
    assert Driver.start(tmp_path, "t", "p", h, clock=clock).run() == 1


# ---- waves ------------------------------------------------------------------------------------------

def test_wave_runs_all_tasks():
    res, size = driver.run_wave({f"c{i}": i for i in range(20)}, lambda x: x * 2, size=8)
    assert all(r.ok for r in res.values()) and res["c7"].value == 14 and size == 8


def test_wave_halves_on_rate_limit_and_still_finishes():
    hits = {"n": 0}

    def fn(x):
        hits["n"] += 1
        if hits["n"] == 1:
            raise RateLimited()
        return x

    res, size = driver.run_wave({f"c{i}": i for i in range(8)}, fn, size=8)
    assert all(r.ok for r in res.values()) and size == 4


def test_wave_retries_once_then_fails_and_times_out():
    calls = {"n": 0}

    def flaky(x):
        calls["n"] += 1
        raise RuntimeError("boom")

    res, _ = driver.run_wave({"a": 1}, flaky, size=2, retries=1)
    assert not res["a"].ok and res["a"].attempts == 2 and calls["n"] == 2

    res, _ = driver.run_wave({"a": 1}, lambda x: time.sleep(0.4), size=2, timeout=0.05, retries=1)
    assert not res["a"].ok and "timeout" in res["a"].error


def test_wave_rate_limit_gives_up_eventually():
    def always(x):
        raise RateLimited()

    res, size = driver.run_wave({"a": 1}, always, size=4, max_rate_limit_retries=2)
    assert not res["a"].ok and res["a"].error == "rate limited" and size == 1


# ---- CLI entry --------------------------------------------------------------------------------------

def test_cli_infers_mode_then_reports_missing_handler(tmp_path):
    import ledgerlab

    code = ledgerlab.main(["start", "--site-root", str(tmp_path), "--topic", "ark-nova", "how do I play Ark Nova"])
    assert code == 1  # ingest has no handler yet; honest failure, not a silent pass
    run = next((tmp_path / "_ledger" / "ark-nova" / "runs").iterdir())
    assert "no handler for phase ingest" in (run / "REPORT.md").read_text()
    assert "mode: rules" in (run / "run.yaml").read_text()


def test_gates_handler_blocks_bad_ledger_and_passes_good(tmp_path):
    import ledger
    import ledgerlab

    topic = tmp_path / "t"
    topic.mkdir()
    bad = {"schema": 1, "claims": [{"id": "c1", "text": "X.", "hash": ledger.claim_hash("X."), "status": "true", "origin": "discovered", "rounds": 1, "paradigms_tried": ["keyword"], "evidence": []}]}
    (topic / "claims.yaml").write_text(ledger.dump_claims(bad))
    (topic / "sources.yaml").write_text("schema: 1\nsources: []\n")
    h = ledgerlab.make_handlers(topic)
    d = driver.Driver.start(tmp_path / "run", "t", "p", h)
    with pytest.raises(GateFailed):
        h["gates"](d)
    good = {"schema": 1, "claims": [{"id": "c1", "text": "X.", "hash": ledger.claim_hash("X."), "status": "not-found", "origin": "discovered", "rounds": 5, "paradigms_tried": ["keyword"], "evidence": []}]}
    (topic / "claims.yaml").write_text(ledger.dump_claims(good))
    assert h["gates"](d).data["claims"] == 1

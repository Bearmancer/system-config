"""CLI entry: start or resume a run. Only the phases that need no agent are real so far (infer_mode, gates).

  ledgerlab.py start --site-root <bearmancer.github.io clone> --topic <slug> "<prompt>"
  ledgerlab.py resume <run_dir>

Other phases fail with a clear REPORT.md until agent handlers are wired (see HANDOFF.md, build order step 4-5).
Exit: 0 done, 1 failed, 2 suspended (NEEDS_YOU.md).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import driver
import infer_mode
import ledger


def make_handlers(topic_dir: Path) -> dict[str, driver.Handler]:
    def h_infer(d: driver.Driver) -> driver.PhaseResult:
        mode, reason = infer_mode.infer_mode(d.state.prompt)
        return driver.PhaseResult(data={"reason": reason}, mode=mode)

    def h_gates(d: driver.Driver) -> driver.PhaseResult:
        claims = ledger.load_claims(topic_dir / "claims.yaml")
        sources = ledger.load_sources(topic_dir / "sources.yaml")
        attempts = ledger.load_attempts(topic_dir / "attempts.jsonl")
        errors = [v for v in ledger.check(claims, sources, attempts, publish=True) if v.severity == "error"]
        if errors:
            raise driver.GateFailed("ledger-check", [str(e) for e in errors])
        return driver.PhaseResult(data={"claims": len(claims["claims"])})

    return {"infer_mode": h_infer, "gates": h_gates}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--site-root", type=Path, required=True)
    s.add_argument("--topic", required=True)
    s.add_argument("prompt")
    r = sub.add_parser("resume")
    r.add_argument("run_dir", type=Path)
    args = ap.parse_args(argv)

    if args.cmd == "start":
        topic_dir = args.site_root / "_ledger" / args.topic
        run_id = driver._now().replace(":", "").replace("-", "")
        d = driver.Driver.start(topic_dir / "runs" / run_id, args.topic, args.prompt, make_handlers(topic_dir), run_id=run_id)
    else:
        topic_dir = args.run_dir.parent.parent
        d = driver.Driver.resume(args.run_dir, make_handlers(topic_dir))
    code = d.run()
    print(f"{d.state.run_id}: {d.state.status} (phase {d.state.phase})")
    return code


if __name__ == "__main__":
    raise SystemExit(main())

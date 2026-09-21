#!/usr/bin/env python3

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tokenize
from datetime import datetime
from pathlib import Path

EXCLUDED_PATH_PARTS = {"synced", "node_modules", ".agents"}


def say(message: str) -> None:
    print(message)


def head(message: str) -> None:
    print("")
    print(f"== {message} ==")


def ensure_basedpyright() -> str:
    if shutil.which("basedpyright") is None:
        say("basedpyright missing - installing via uv tool install")
        subprocess.run(["uv", "tool", "install", "basedpyright"])
        if shutil.which("basedpyright") is None:
            say(
                "ERROR: basedpyright still unavailable after install attempt. Run manually: uv tool install basedpyright"
            )
            sys.exit(1)
    result = subprocess.run(
        ["basedpyright", "--version"], capture_output=True, text=True
    )
    return result.stdout.strip()


def strip_py(path: Path) -> None:
    src = path.read_text(encoding="utf-8")
    lines = src.splitlines()
    toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    sig = [t for t in toks if t.type not in (tokenize.NL, tokenize.COMMENT)]
    doc_rows: set[int] = set()
    for i, t in enumerate(sig):
        if t.type != tokenize.STRING:
            continue
        prev = sig[i - 1] if i else None
        nxt = sig[i + 1] if i + 1 < len(sig) else None
        prev_ok = prev is None or prev.type in (
            tokenize.NEWLINE,
            tokenize.INDENT,
            tokenize.DEDENT,
        )
        if prev_ok and nxt is not None and nxt.type == tokenize.NEWLINE:
            after = sig[i + 2] if i + 2 < len(sig) else None
            if after is not None and after.type in (
                tokenize.DEDENT,
                tokenize.ENDMARKER,
            ):
                continue
            for r in range(t.start[0], t.end[0] + 1):
                doc_rows.add(r)
    cuts: dict[int, int] = {}
    for t in toks:
        if t.type == tokenize.COMMENT:
            cuts.setdefault(t.start[0], t.start[1])
    out: list[str] = []
    for idx, line in enumerate(lines, start=1):
        if idx == 1 and line.startswith("#!"):
            out.append(line)
            continue
        if idx in doc_rows:
            continue
        if idx in cuts:
            line = line[: cuts[idx]].rstrip()
        out.append(line)
    text = "\n".join(out)
    while "\n\n\n\n" in text:
        text = text.replace("\n\n\n\n", "\n\n\n")
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")


def get_bp_error_map(paths: list[Path]) -> dict[str, int]:
    existing = [str(p) for p in paths if p.exists()]
    counts: dict[str, int] = {}
    if not existing:
        return counts
    result = subprocess.run(
        ["basedpyright", "--outputjson", *existing], capture_output=True, text=True
    )
    if not result.stdout:
        return counts
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return counts
    for d in data.get("generalDiagnostics", []):
        if d.get("severity") == "error":
            key = Path(d["file"]).name
            counts[key] = counts.get(key, 0) + 1
    return counts


def get_bp_first_message(path: Path) -> str:
    result = subprocess.run(
        ["basedpyright", "--outputjson", str(path)], capture_output=True, text=True
    )
    if not result.stdout:
        return ""
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return ""
    errors = [
        d for d in data.get("generalDiagnostics", []) if d.get("severity") == "error"
    ]
    if errors:
        return errors[0].get("message", "")
    return ""


def is_excluded(path: Path, root: Path) -> bool:
    parts_lower = {p.lower() for p in path.parts}
    return any(excluded in parts_lower for excluded in EXCLUDED_PATH_PARTS)


def safe_unlink(path: Path) -> bool:
    try:
        path.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def safe_rmdir(path: Path) -> bool:
    try:
        path.rmdir()
        return True
    except OSError:
        return False


def find_empty_dirs(roots: list[Path]) -> list[Path]:
    empty: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for d in root.rglob("*"):
            if d.is_dir() and not any(d.iterdir()):
                empty.append(d)
    return sorted(empty, key=lambda p: len(str(p)), reverse=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-comments", action="store_true")
    parser.add_argument("--skip-artifacts", action="store_true")
    parser.add_argument("--include-codegraph-indexes", action="store_true")
    parser.add_argument(
        "--script-roots",
        nargs="*",
        type=Path,
        default=[
            Path.home() / ".claude" / "skills" / "learning-course" / "scripts",
            Path.home() / ".claude" / "skills" / "arr-api-reference" / "scripts",
            Path.home() / ".omo" / "scripts",
            Path.home()
            / ".config"
            / "opencode"
            / "skills"
            / "caveman-compress"
            / "scripts",
        ],
    )
    parser.add_argument(
        "--purge-roots",
        nargs="*",
        type=Path,
        default=[
            Path.home() / ".omo",
            Path.home() / ".claude" / "skills",
            Path.home() / ".config" / "opencode",
        ],
    )
    args = parser.parse_args()

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_dir = Path(os.environ["TEMP"]) / "opencode" / f"purge-backup-{stamp}"
    exit_code = 0

    say(
        f"purge.py  ({'DRY RUN — nothing will change' if args.dry_run else 'live run'})"
    )
    say(f"time: {datetime.now():%Y-%m-%d %H:%M:%S}")

    head("Linter (hard requirement, auto-install)")
    bp_version = ensure_basedpyright()
    say(f"basedpyright {bp_version}")

    head("Discovery")
    cont_dir = Path.home() / ".omo" / "run-continuation"
    conts = [f for f in cont_dir.iterdir() if f.is_file()] if cont_dir.exists() else []
    live = max(conts, key=lambda f: f.stat().st_mtime) if conts else None
    say(
        f"run-continuations : {len(conts)} file(s); keeping newest as live: {live.name if live else '(none)'}"
    )

    pycs: list[Path] = []
    for r in args.purge_roots:
        if r.exists():
            pycs.extend(d for d in r.rglob("__pycache__") if d.is_dir())
    say(f"pycache dirs      : {len(pycs)}")

    tmp_dir = Path(os.environ["TEMP"]) / "opencode"
    tmp_items = list(tmp_dir.iterdir()) if tmp_dir.exists() else []
    say(f"temp scratch      : {len(tmp_items)} item(s) under {tmp_dir}")

    pses_dir = Path.home() / ".omo" / "lsp-pses.log"
    pses_logs = (
        list(pses_dir.glob("StartEditorServices-*.log")) if pses_dir.exists() else []
    )
    say(f"editor-svc logs   : {len(pses_logs)}")

    cg_dir = Path.home() / ".omo" / "codegraph"
    cg_dbs = list(cg_dir.rglob("*.db")) if cg_dir.exists() else []
    cg_size = sum(f.stat().st_size for f in cg_dbs)
    say(
        f"codegraph DBs     : {len(cg_dbs)} file(s), {cg_size / 1024 / 1024:.1f} MB (opt-in: --include-codegraph-indexes)"
    )

    if shutil.which("basedpyright") is None:
        raise RuntimeError(
            "Linter check failed after install attempt - aborting before any strip."
        )

    if not args.skip_comments:
        head("Comment strip")
        targets: list[Path] = []
        for r in args.script_roots:
            if r.exists():
                for f in r.rglob("*.py"):
                    if f.is_file() and not is_excluded(f, r):
                        targets.append(f)
        say(f"script files in scope: {len(targets)} (python {len(targets)})")

        if args.dry_run:
            say(
                "dry run: would strip comments/docstrings from the files above (backup in TEMP, auto-restore on lint failure)"
            )
        else:
            backup_dir.mkdir(parents=True, exist_ok=True)
            for f in targets:
                shutil.copy2(f, backup_dir / f.name)

            for f in targets:
                strip_py(f)
            say(f"stripped: {len(targets)} python")

            head("Lint verify (native reports, auto-restore on failure)")
            bad: list[Path] = []
            notes: list[str] = []

            if targets:
                before_map = get_bp_error_map([backup_dir / f.name for f in targets])
                after_map = get_bp_error_map(targets)
                for f in targets:
                    if after_map.get(f.name, 0) > before_map.get(f.name, 0):
                        bad.append(f)
                notes.append("basedpyright: per-file baseline diff")

            seen: set[Path] = set()
            deduped_bad: list[Path] = []
            for f in bad:
                if f not in seen:
                    seen.add(f)
                    deduped_bad.append(f)
            bad = deduped_bad

            if bad:
                for f in bad:
                    src = backup_dir / f.name
                    shutil.copy2(src, f)
                    detail = get_bp_first_message(f)
                    if not detail:
                        compile_result = subprocess.run(
                            [sys.executable, "-m", "py_compile", str(f)],
                            capture_output=True,
                            text=True,
                        )
                        detail = (
                            (
                                compile_result.stderr or compile_result.stdout
                            ).splitlines()[0]
                            if (compile_result.stderr or compile_result.stdout)
                            else ""
                        )
                    say(f"RESTORED (lint failed): {f} - {detail}")
                say(f"backups kept at: {backup_dir}")
                exit_code = 1
            else:
                for n in notes:
                    say(f"  - {n}")
                say("lint clean: all gates green")
                shutil.rmtree(backup_dir, ignore_errors=True)

    if not args.skip_artifacts:
        head("Artifact purge")
        if args.dry_run:
            say(
                "dry run: would purge run-continuations (keep live), pycache, temp scratch, editor-services logs, empty dirs"
            )
            if args.include_codegraph_indexes:
                say(
                    f"dry run: would purge {cg_size / 1024 / 1024:.1f} MB of codegraph DBs"
                )
        else:
            n = 0
            for c in conts:
                if live is None or c.name != live.name:
                    if safe_unlink(c):
                        n += 1
            say(f"run-continuations purged: {n} (kept {live.name if live else 'none'})")

            n = 0
            for d in pycs:
                shutil.rmtree(d, ignore_errors=True)
                n += 1
            say(f"pycache dirs purged: {n}")

            n = 0
            for item in tmp_items:
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                    n += 1
                elif safe_unlink(item):
                    n += 1
            say(f"temp scratch purged: {n} item(s)")

            n = 0
            for log in pses_logs:
                if safe_unlink(log):
                    n += 1
            say(
                f"editor-services logs purged: {n} (of {len(pses_logs)} found; locked-by-another-process files skipped)"
            )

            n = 0
            for d in find_empty_dirs(args.purge_roots):
                if safe_rmdir(d):
                    n += 1
            say(f"empty dirs purged: {n}")

            if args.include_codegraph_indexes:
                n = 0
                for db in cg_dbs:
                    if safe_unlink(db):
                        n += 1
                say(
                    f"codegraph DBs purged: {n} ({cg_size / 1024 / 1024:.1f} MB) — reindex later with codegraph init"
                )
            else:
                say("codegraph DBs kept (opt-in: --include-codegraph-indexes)")

    head("Done")
    say(f"exit code: {exit_code}")
    say(
        "tips: --dry-run to preview | --skip-comments / --skip-artifacts to scope | --include-codegraph-indexes to reclaim codegraph disk"
    )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())

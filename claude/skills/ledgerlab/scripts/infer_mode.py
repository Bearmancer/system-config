"""Infer the run mode from the prompt (ADR 0007, Q44). Returns (mode, reason). Default learn.

verify: verify / fact-check / debunk / "is it true" words, or a pasted list of claims.
rules: rulebook, "how to play", board-game words, or a rulebook-looking PDF path.
Verify wins over rules: "fact-check the Ark Nova rules" is a verify run.
"""
from __future__ import annotations

import re
import sys

VERIFY_WORDS = re.compile(
    r"\b(verify|fact[- ]?check|debunk|is (it|this|that) (really )?true|true or false|check (these|this|the) claims?|are these (claims )?(true|correct))\b",
    re.I,
)
RULES_WORDS = re.compile(
    r"\b(rulebook|rule ?book|how (do|to) (i|you|we) play|how to play|board ?game|boardgame|bgg|boardgamegeek|errata|player count)\b",
    re.I,
)
RULES_FILE = re.compile(r"[\w./\\-]*(rule|regel|anleitung|manual)[\w./\\ -]*\.pdf", re.I)
LIST_LINE = re.compile(r"^\s*(?:[-*•]|\d{1,3}[.)])\s+\S")


def infer_mode(prompt: str) -> tuple[str, str]:
    m = VERIFY_WORDS.search(prompt)
    if m:
        return "verify", f"verify word: {m.group(0)!r}"
    list_lines = [ln for ln in prompt.splitlines() if LIST_LINE.match(ln)]
    if len(list_lines) >= 3 and any(len(ln.split()) >= 5 for ln in list_lines):
        return "verify", f"pasted claim list ({len(list_lines)} items)"
    m = RULES_WORDS.search(prompt)
    if m:
        return "rules", f"rules word: {m.group(0)!r}"
    m = RULES_FILE.search(prompt)
    if m:
        return "rules", f"rulebook file: {m.group(0)!r}"
    return "learn", "default"


def main(argv: list[str] | None = None) -> int:
    text = " ".join(argv if argv is not None else sys.argv[1:]) or sys.stdin.read()
    mode, reason = infer_mode(text)
    print(f"{mode}\t{reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

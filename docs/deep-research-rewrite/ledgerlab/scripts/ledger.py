"""Claim ledger: load, hash, and enforce status invariants (ADR 0018, 0019).

`check` returns Violation objects; an empty list means the ledger may publish (with publish=True,
any `open` claim is a violation). Rotation rules read attempts.jsonl (ADR 0015).
"""
from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"
STATUSES = ("true", "untrue", "interpretive", "not-found", "open")
MAX_QUOTE_WORDS = 25
MAX_ROUNDS = 5
CREDIBLE_TIERS = ("T1", "T2")


@dataclass(frozen=True)
class Violation:
    rule: str
    claim: str | None
    message: str
    severity: str = "error"

    def __str__(self) -> str:
        where = self.claim or "-"
        return f"[{self.severity}] {self.rule} {where}: {self.message}"


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def claim_hash(text: str) -> str:
    """16-hex content hash of normalised claim text, for cross-topic matching."""
    return hashlib.sha256(normalize_text(text).encode("utf-8")).hexdigest()[:16]


def _load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _normalize_status(claims: dict[str, Any]) -> dict[str, Any]:
    # YAML 1.1 reads bare true/false as booleans; the ledger statuses are strings.
    for c in claims.get("claims", []):
        if c.get("status") is True:
            c["status"] = "true"
        elif c.get("status") is False:
            c["status"] = "untrue"
    return claims


def load_claims(path: Path) -> dict[str, Any]:
    return _normalize_status(_load_yaml(path))


def load_sources(path: Path) -> dict[str, Any]:
    return _load_yaml(path)


def load_attempts(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    return rows


def dump_claims(data: dict[str, Any]) -> str:
    class _Dumper(yaml.SafeDumper):
        pass

    def _str(dumper: yaml.SafeDumper, value: str) -> Any:
        if value in ("true", "false", "null", "yes", "no", "on", "off"):
            return dumper.represent_scalar("tag:yaml.org,2002:str", value, style='"')
        return dumper.represent_scalar("tag:yaml.org,2002:str", value)

    _Dumper.add_representer(str, _str)
    return yaml.dump(data, Dumper=_Dumper, sort_keys=False, allow_unicode=True)


def _schema_errors(schema_name: str, data: dict[str, Any]) -> list[str]:
    schema = json.loads((SCHEMA_DIR / schema_name).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    out = []
    for err in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        loc = "/".join(str(p) for p in err.absolute_path) or "<root>"
        out.append(f"{loc}: {err.message}")
    return out


def _words(text: str) -> int:
    return len(text.split())


def _supporting(claim: dict[str, Any], sources: dict[str, dict[str, Any]], tiers: tuple[str, ...] | None = None):
    return _by_stance(claim, sources, "supports", tiers)


def _contradicting(claim: dict[str, Any], sources: dict[str, dict[str, Any]], tiers: tuple[str, ...] | None = None):
    return _by_stance(claim, sources, "contradicts", tiers)


def _by_stance(claim, sources, stance, tiers):
    out = []
    for ev in claim.get("evidence", []):
        src = sources.get(ev["source"])
        if src is None or src.get("status") != "read":
            continue
        if ev["stance"] != stance:
            continue
        if tiers is not None and src["tier"] not in tiers:
            continue
        out.append((ev, src))
    return out


def _meets_bar(claim: dict[str, Any], pairs: list) -> bool:
    """Truth bar: one T1 source, or two T1/T2 sources from distinct publishers with a recorded independence rationale."""
    if any(src["tier"] == "T1" for _, src in pairs):
        return True
    credible = [(ev, src) for ev, src in pairs if src["tier"] in CREDIBLE_TIERS]
    publishers = {src["publisher"].strip().lower() for _, src in credible}
    has_rationale = bool((claim.get("independence") or {}).get("rationale", "").strip())
    return len(credible) >= 2 and len(publishers) >= 2 and has_rationale


def check(
    claims_doc: dict[str, Any],
    sources_doc: dict[str, Any],
    attempts: list[dict[str, Any]] | None = None,
    publish: bool = False,
    round_order: list[list[str]] | None = None,
) -> list[Violation]:
    v: list[Violation] = []
    for msg in _schema_errors("claims.schema.json", claims_doc):
        v.append(Violation("schema", None, f"claims.yaml {msg}"))
    for msg in _schema_errors("sources.schema.json", sources_doc):
        v.append(Violation("schema", None, f"sources.yaml {msg}"))
    if v:
        return v  # structure is broken; semantic rules would only produce noise

    sources = {s["id"]: s for s in sources_doc["sources"]}
    if len(sources) != len(sources_doc["sources"]):
        v.append(Violation("unique-source-id", None, "duplicate source id"))
    for s in sources.values():
        if s["status"] == "failed" and not s.get("fail_reason"):
            v.append(Violation("failed-source-reason", None, f"{s['id']} failed without fail_reason"))

    ids: set[str] = set()
    for c in claims_doc["claims"]:
        cid = c["id"]
        if cid in ids:
            v.append(Violation("unique-claim-id", cid, "duplicate claim id"))
        ids.add(cid)
        if c["hash"] != claim_hash(c["text"]):
            v.append(Violation("hash", cid, "hash does not match normalised text"))
        if len(set(c["paradigms_tried"])) != len(c["paradigms_tried"]):
            v.append(Violation("paradigms-unique", cid, "paradigms_tried has duplicates"))
        if c["rounds"] > MAX_ROUNDS:
            v.append(Violation("max-rounds", cid, f"{c['rounds']} rounds exceeds {MAX_ROUNDS}"))
        for ev in c["evidence"]:
            if ev["source"] not in sources:
                v.append(Violation("evidence-source", cid, f"unknown source {ev['source']}"))
            elif sources[ev["source"]]["status"] != "read":
                v.append(Violation("evidence-source", cid, f"{ev['source']} was not read"))
            if _words(ev["quote"]) > MAX_QUOTE_WORDS:
                v.append(Violation("quote-length", cid, f"quote over {MAX_QUOTE_WORDS} words"))
        v.extend(_check_status(c, sources, publish))

    if attempts is not None:
        v.extend(check_rotation(attempts, round_order or _default_round_order()))
    return v


def _check_status(c: dict[str, Any], sources: dict[str, dict[str, Any]], publish: bool) -> list[Violation]:
    cid, status = c["id"], c["status"]
    out: list[Violation] = []
    sup = _supporting(c, sources)
    con = _contradicting(c, sources)
    sup_cred = _supporting(c, sources, CREDIBLE_TIERS)
    con_cred = _contradicting(c, sources, CREDIBLE_TIERS)

    if status == "open":
        if publish:
            out.append(Violation("open-at-publish", cid, "claim still open"))
        return out

    if status in ("true", "untrue") and c["rounds"] < 1:
        out.append(Violation("rounds-required", cid, f"{status} needs at least one round"))

    if status == "true":
        if not _meets_bar(c, sup):
            out.append(Violation("true-bar", cid, "needs one T1 source, or two independent T1/T2 sources with a rationale"))
        if con_cred:
            out.append(Violation("true-contradicted", cid, "credible contradicting evidence; status should be interpretive"))
        if "visual-read" in c.get("tags", []):
            reads = {ev.get("read_by") for ev, _ in sup if ev.get("read_by")}
            corroborated = any(ev.get("text_corroboration") for ev, _ in sup)
            if len(reads) < 2 and not corroborated:
                out.append(Violation("visual-read", cid, "needs two independent reads or one text corroboration"))
    elif status == "untrue":
        if not _meets_bar(c, con):
            out.append(Violation("untrue-bar", cid, "contradicting evidence does not meet the truth bar"))
        if sup_cred:
            out.append(Violation("untrue-supported", cid, "credible supporting evidence; status should be interpretive"))
    elif status == "interpretive":
        positions = c.get("positions", [])
        if len(positions) < 2:
            out.append(Violation("interpretive-positions", cid, "needs at least 2 positions"))
        for p in positions:
            if not any(sources.get(s, {}).get("tier") in CREDIBLE_TIERS for s in p["sources"]):
                out.append(Violation("interpretive-source", cid, "each position needs a T1/T2 source"))
            for s in p["sources"]:
                if s not in sources:
                    out.append(Violation("interpretive-source", cid, f"unknown source {s}"))
    elif status == "not-found":
        if c["rounds"] != MAX_ROUNDS:
            out.append(Violation("not-found-rounds", cid, f"not-found needs {MAX_ROUNDS} rounds"))
        if sup_cred or con_cred:
            out.append(Violation("not-found-evidence", cid, "credible evidence exists; pick another status"))
    return out


def _default_round_order() -> list[list[str]]:
    from registry import load

    return load()["round_order"]


def check_rotation(attempts: list[dict[str, Any]], round_order: list[list[str]]) -> list[Violation]:
    """Each discovery round must use only paradigms not used in earlier rounds, and follow round_order (ADR 0015, 0016)."""
    out: list[Violation] = []
    by_claim: dict[str, dict[int, set[str]]] = {}
    for a in attempts:
        if a.get("ladder") != "discovery":
            continue
        by_claim.setdefault(a["claim"], {}).setdefault(int(a["round"]), set()).add(a["paradigm"])
    for cid, rounds in by_claim.items():
        seen: set[str] = set()
        for rno in sorted(rounds):
            used = rounds[rno]
            repeat = used & seen
            if repeat:
                out.append(Violation("rotation-repeat", cid, f"round {rno} reuses paradigm {sorted(repeat)}"))
            if 1 <= rno <= len(round_order):
                stray = used - set(round_order[rno - 1])
                if stray:
                    out.append(Violation("rotation-order", cid, f"round {rno} used {sorted(stray)}, expected {round_order[rno - 1]}", "warn"))
            seen |= used
    return out


def prose_claims_missing(extracted_texts: list[str], claims_doc: dict[str, Any]) -> list[str]:
    """Conformance gate: claims extracted from final prose that are absent from the ledger (by content hash)."""
    known = {c["hash"] for c in claims_doc["claims"]}
    return [t for t in extracted_texts if claim_hash(t) not in known]


def check_sentences(sentences: list[dict[str, Any]], claims_doc: dict[str, Any]) -> list[Violation]:
    """A sentence is publishable only if every mapped claim is true (plain), interpretive (debate) or untrue (errata)."""
    by_id = {c["id"]: c for c in claims_doc["claims"]}
    want = {"plain": "true", "debate": "interpretive", "errata": "untrue"}
    out: list[Violation] = []
    for s in sentences:
        block = s.get("block", "plain")
        if block not in want:
            out.append(Violation("sentence-block", None, f"{s.get('id')}: unknown block {block}"))
            continue
        mapped = s.get("claims", [])
        if not mapped:
            out.append(Violation("sentence-unmapped", None, f"{s.get('id')}: no mapped claim"))
        for cid in mapped:
            c = by_id.get(cid)
            if c is None:
                out.append(Violation("sentence-claim", cid, f"{s.get('id')}: unknown claim"))
            elif c["status"] != want[block]:
                out.append(Violation("sentence-status", cid, f"{s.get('id')}: {block} block needs {want[block]}, claim is {c['status']}"))
    return out

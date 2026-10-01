import copy

import pytest

import ledger


def src(sid, tier="T1", publisher=None, status="read", **kw):
    d = {"id": sid, "url": f"https://example.org/{sid}", "tier": tier, "publisher": publisher or f"pub-{sid}", "status": status}
    d.update(kw)
    return d


def claim(cid, text, status, **kw):
    d = {
        "id": cid,
        "text": text,
        "hash": ledger.claim_hash(text),
        "status": status,
        "origin": "discovered",
        "rounds": 1,
        "paradigms_tried": ["keyword"],
        "evidence": [],
    }
    d.update(kw)
    return d


def ev(source, stance="supports", **kw):
    d = {"source": source, "locator": "p.1", "quote": "short quote", "stance": stance}
    d.update(kw)
    return d


def docs(claims, sources):
    return {"schema": 1, "claims": claims}, {"schema": 1, "sources": sources}


def rules(violations):
    return {v.rule for v in violations if v.severity == "error"}


def test_good_ledger_is_clean():
    c, s = docs(
        [
            claim("c1", "Hand limit is 3.", "true", evidence=[ev("s1")]),
            claim("c2", "Two sources agree.", "true", evidence=[ev("s2"), ev("s3")], independence={"rationale": "different outlets, no shared wire"}),
        ],
        [src("s1"), src("s2", "T2", "Outlet A"), src("s3", "T2", "Outlet B")],
    )
    assert ledger.check(c, s) == []


def test_seeded_bad_claim_is_caught_and_blocks_publish():
    # Acceptance test (Q46): a false claim written as `true` with only T3 support must fail the gate.
    c, s = docs(
        [claim("c1", "The moon is made of cheese.", "true", evidence=[ev("s1")])],
        [src("s1", "T3", "someforum")],
    )
    assert "true-bar" in rules(ledger.check(c, s, publish=True))


def test_true_contradicted_by_credible_source():
    c, s = docs(
        [claim("c1", "X is so.", "true", evidence=[ev("s1"), ev("s2", "contradicts")])],
        [src("s1"), src("s2", "T2", "Other")],
    )
    assert "true-contradicted" in rules(ledger.check(c, s))


def test_two_secondaries_need_distinct_publishers_and_rationale():
    base_sources = [src("s1", "T2", "Same"), src("s2", "T2", "Same")]
    c, s = docs([claim("c1", "X.", "true", evidence=[ev("s1"), ev("s2")], independence={"rationale": "claimed"})], base_sources)
    assert "true-bar" in rules(ledger.check(c, s))
    c, s = docs([claim("c1", "X.", "true", evidence=[ev("s1"), ev("s2")])], [src("s1", "T2", "A"), src("s2", "T2", "B")])
    assert "true-bar" in rules(ledger.check(c, s))


def test_untrue_needs_contradicting_bar_and_no_credible_support():
    c, s = docs([claim("c1", "X.", "untrue", evidence=[ev("s1", "contradicts")])], [src("s1")])
    assert ledger.check(c, s) == []
    c, s = docs([claim("c1", "X.", "untrue", evidence=[ev("s1", "contradicts"), ev("s2")])], [src("s1"), src("s2", "T2", "O")])
    assert "untrue-supported" in rules(ledger.check(c, s))


def test_interpretive_needs_two_sourced_positions():
    pos = [{"text": "A", "sources": ["s1"]}, {"text": "B", "sources": ["s2"]}]
    c, s = docs([claim("c1", "X.", "interpretive", positions=pos)], [src("s1"), src("s2", "T2", "O")])
    assert ledger.check(c, s) == []
    c, s = docs([claim("c1", "X.", "interpretive", positions=pos[:1])], [src("s1")])
    assert "interpretive-positions" in rules(ledger.check(c, s))
    weak = [{"text": "A", "sources": ["s1"]}, {"text": "B", "sources": ["s2"]}]
    c, s = docs([claim("c1", "X.", "interpretive", positions=weak)], [src("s1"), src("s2", "T3", "forum")])
    assert "interpretive-source" in rules(ledger.check(c, s))


def test_not_found_needs_five_rounds_and_no_credible_evidence():
    c, s = docs([claim("c1", "X.", "not-found", rounds=5)], [])
    assert ledger.check(c, s) == []
    c, s = docs([claim("c1", "X.", "not-found", rounds=3)], [])
    assert "not-found-rounds" in rules(ledger.check(c, s))
    c, s = docs([claim("c1", "X.", "not-found", rounds=5, evidence=[ev("s1")])], [src("s1")])
    assert "not-found-evidence" in rules(ledger.check(c, s))


def test_open_blocks_publish_only():
    c, s = docs([claim("c1", "X.", "open", rounds=0)], [])
    assert ledger.check(c, s) == []
    assert "open-at-publish" in rules(ledger.check(c, s, publish=True))


def test_visual_read_needs_two_reads_or_text_corroboration():
    one = [ev("s1", read_by="deepseek")]
    c, s = docs([claim("c1", "X.", "true", evidence=one, tags=["visual-read"])], [src("s1")])
    assert "visual-read" in rules(ledger.check(c, s))
    two = [ev("s1", read_by="deepseek"), ev("s1", read_by="muse")]
    c, s = docs([claim("c1", "X.", "true", evidence=two, tags=["visual-read"])], [src("s1")])
    assert ledger.check(c, s) == []
    corr = [ev("s1", read_by="deepseek", text_corroboration=True)]
    c, s = docs([claim("c1", "X.", "true", evidence=corr, tags=["visual-read"])], [src("s1")])
    assert ledger.check(c, s) == []


def test_quote_length_and_locator_required():
    long_quote = " ".join(["w"] * 26)
    c, s = docs([claim("c1", "X.", "true", evidence=[ev("s1", quote=long_quote)])], [src("s1")])
    assert "quote-length" in rules(ledger.check(c, s))
    bad = ev("s1")
    del bad["locator"]
    c, s = docs([claim("c1", "X.", "true", evidence=[bad])], [src("s1")])
    assert "schema" in rules(ledger.check(c, s))


def test_failed_source_cannot_be_evidence_and_needs_reason():
    c, s = docs([claim("c1", "X.", "true", evidence=[ev("s1")])], [src("s1", status="failed")])
    got = rules(ledger.check(c, s))
    assert {"evidence-source", "failed-source-reason"} <= got


def test_hash_must_match_text():
    c, s = docs([claim("c1", "X.", "open", rounds=0, hash="0" * 16)], [])
    assert "hash" in rules(ledger.check(c, s))


def test_hash_normalisation_ignores_case_and_punctuation():
    assert ledger.claim_hash("Hand limit is 3.") == ledger.claim_hash("hand  LIMIT is 3")


def test_yaml_bare_true_is_normalised(tmp_path):
    p = tmp_path / "claims.yaml"
    p.write_text(
        "schema: 1\nclaims:\n- id: c1\n  text: X\n  hash: '%s'\n  status: true\n  origin: discovered\n  rounds: 1\n  paradigms_tried: [keyword]\n  evidence: []\n" % ledger.claim_hash("X"),
        encoding="utf-8",
    )
    assert ledger.load_claims(p)["claims"][0]["status"] == "true"


def test_dump_quotes_status_strings():
    out = ledger.dump_claims({"schema": 1, "claims": [{"status": "true"}]})
    assert 'status: "true"' in out


def attempt(claim_id, rnd, paradigm, ladder="discovery"):
    return {"claim": claim_id, "round": rnd, "paradigm": paradigm, "ladder": ladder}


ORDER = [["keyword"], ["semantic"], ["answer-agent"], ["scholarly-archive"], ["crawl-map", "browser-unlocker"]]


def test_rotation_ok():
    att = [attempt("c1", 1, "keyword"), attempt("c1", 2, "semantic"), attempt("c1", 5, "crawl-map")]
    assert ledger.check_rotation(att, ORDER) == []


def test_rotation_repeat_is_an_error_and_wrong_order_a_warning():
    att = [attempt("c1", 1, "keyword"), attempt("c1", 2, "keyword")]
    got = ledger.check_rotation(att, ORDER)
    assert {v.rule for v in got if v.severity == "error"} == {"rotation-repeat"}
    assert any(v.rule == "rotation-order" and v.severity == "warn" for v in got)


def test_fetch_attempts_do_not_count_for_rotation():
    att = [attempt("c1", 1, "keyword"), attempt("c1", 2, "keyword", ladder="fetch")]
    assert ledger.check_rotation(att, ORDER) == []


def test_conformance_prose_claims_missing():
    c, _ = docs([claim("c1", "Hand limit is 3.", "true")], [])
    assert ledger.prose_claims_missing(["hand limit is 3", "You always draw four."], c) == ["You always draw four."]


def test_sentence_rules():
    c, _ = docs(
        [claim("c1", "A.", "true"), claim("c2", "B.", "interpretive"), claim("c3", "C.", "untrue")],
        [],
    )
    ok = [
        {"id": "p1", "claims": ["c1"], "block": "plain"},
        {"id": "p2", "claims": ["c2"], "block": "debate"},
        {"id": "p3", "claims": ["c3"], "block": "errata"},
    ]
    assert ledger.check_sentences(ok, c) == []
    bad = [{"id": "p1", "claims": ["c1", "c3"], "block": "plain"}, {"id": "p2", "claims": [], "block": "plain"}]
    assert {v.rule for v in ledger.check_sentences(bad, c)} == {"sentence-status", "sentence-unmapped"}

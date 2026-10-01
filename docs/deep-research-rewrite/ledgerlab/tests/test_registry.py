import copy

import pytest

import registry


@pytest.fixture(scope="module")
def reg():
    return registry.load()


def test_registry_loads_and_validates(reg):
    assert reg["max_rounds"] == 5
    assert len(reg["round_order"]) == 5


def test_every_round_has_a_wired_discovery_surface(reg):
    for rno in range(1, 6):
        found = [s for p in registry.round_paradigms(reg, rno) for s in registry.discovery_surfaces(reg, p)]
        assert found, f"round {rno} has no wired discovery surface"


def test_fetch_ladder_order_starts_cheap_and_wayback_before_heavy(reg):
    ladder = reg["fetch_ladder"]
    assert ladder[0] == "direct.fetch"
    assert ladder.index("wayback.fetch") < ladder.index("scrapegraph.scrape")
    assert ladder.index("exa.fetch") < ladder.index("wayback.fetch")


def test_unwired_servers_are_excluded_from_discovery(reg):
    ids = {s.id for s in registry.discovery_surfaces(reg, "keyword")}
    assert "brave.search" not in ids
    assert "tavily.search" in ids


def test_classify_verified_codes(reg):
    assert registry.classify_error(reg, "firecrawl", 402) == "out_of_credit"
    assert registry.classify_error(reg, "firecrawl", 429) == "rate_limit"
    assert registry.classify_error(reg, "exa", 200, "SOURCE_NOT_AVAILABLE") == "blocked"
    assert registry.classify_error(reg, "brightdata", 502, "client_10020") == "out_of_credit"


def test_unverified_class_never_matches(reg):
    # Tavily credit/key cells are unverified: no rotation on a 402-looking failure (ADR 0017).
    assert registry.classify_error(reg, "tavily", 402) == "unknown"
    assert registry.classify_error(reg, "browserbase", 401) == "unknown"


def test_unknown_server_raises(reg):
    with pytest.raises(registry.RegistryError):
        registry.classify_error(reg, "nope", 500)


def test_validation_catches_bad_fetch_ladder(reg):
    bad = copy.deepcopy(reg)
    bad["fetch_ladder"].append("ghost.fetch")
    with pytest.raises(registry.RegistryError, match="ghost.fetch"):
        registry.validate(bad)


def test_validation_catches_keyed_server_without_pool(reg):
    bad = copy.deepcopy(reg)
    bad["servers"]["tavily"]["pool"] = None
    with pytest.raises(registry.RegistryError, match="needs a pool"):
        registry.validate(bad)

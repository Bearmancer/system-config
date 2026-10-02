# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Generic vendor REST call for hosts with no MCP and no CLI for the vendor. Presets per vendor: references/scrapers/<vendor>.md.

Pools: exa, firecrawl, brightdata, browserbase, scrapegraph, tavily, apify, agentql. The base URL (incl. version prefix) and the auth header are fixed per pool, so the key only ever goes to the vendor host.
--body: JSON literal or @file. --param k=v and --header k=v repeat. Path starts with "/" and is relative to the pool base (firecrawl `/scrape`, scrapegraph `/credits`, apify `/store`).
Usage: uv run vendor_request.py <pool> <METHOD> </path> [--body JSON|@file] [--param k=v]... [--header k=v]...
"""
import argparse

import _post_common as pc


def parse_pairs(items, what):
    out = {}
    for item in items or []:
        key, sep, value = item.partition("=")
        if not sep or not key:
            pc.fail("-", "bad_" + what, f"expected k=v, got {item!r}")
        out[key] = value
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("pool", choices=sorted(pc.VENDORS))
    ap.add_argument("method", choices=["GET", "POST", "PUT", "PATCH", "DELETE"])
    ap.add_argument("path")
    ap.add_argument("--body")
    ap.add_argument("--param", action="append")
    ap.add_argument("--header", action="append")
    args = ap.parse_args(argv)
    body = pc.load_json_arg(args.body) if args.body else None
    pc.run(
        args.pool,
        args.method,
        args.path,
        body,
        params=parse_pairs(args.param, "param") or None,
        headers=parse_pairs(args.header, "header") or None,
    )


if __name__ == "__main__":
    main()

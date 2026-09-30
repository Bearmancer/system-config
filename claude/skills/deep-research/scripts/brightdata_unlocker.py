# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Bright Data async Web Unlocker: start, result.

Docs: https://docs.brightdata.com/products/web-unlocker/send-your-first-request, https://docs.brightdata.com/api-reference/rest-api/unlocker/request, https://docs.brightdata.com/api-reference/rest-api/unlocker/get-results
The zone needs "Asynchronous requests" on in Advanced settings.
start prints {"response_id": ...}. result returns 202 while pending; --wait polls after 20 s, 10 s, then every 5 s.
Error codes arrive in the x-brd-error-code / x-brd-err-code headers and are echoed.
Usage: uv run brightdata_unlocker.py start --zone <zone> <url> | result <response_id> [--wait] [--timeout SECONDS]
"""
import argparse

import _post_common as pc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    start = sub.add_parser("start")
    start.add_argument("--zone", required=True)
    start.add_argument("url")
    result = sub.add_parser("result")
    result.add_argument("response_id")
    result.add_argument("--wait", action="store_true")
    result.add_argument("--timeout", type=int, default=120)
    args = ap.parse_args(argv)
    if args.cmd == "start":
        pc.run("brightdata", "POST", "/unblocker/req", {"url": args.url}, params={"zone": args.zone})
    elif args.wait:
        pc.emit(*pc.poll("brightdata", "/unblocker/get_result", {"response_id": args.response_id}, (20, 10, 5), args.timeout))
    else:
        pc.run("brightdata", "GET", "/unblocker/get_result", params={"response_id": args.response_id})


if __name__ == "__main__":
    main()

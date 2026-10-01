"""Shared plumbing for the POST scripts (exa_*, firecrawl_*, brightdata_*, browserbase_*, scrapegraph_*, vendor_request).

Key: ~/.config/opencode/secrets/<pool>, read here and sent only as the auth header.
Success: JSON payload to stdout, exit 0. HTTP or network error: one JSON line to stderr
{"status", "code", "message"}, exit 1. Vendor code comes from the response, else the status number.
Error shapes: references/scrapers/keys-errors.md.
Redirects are refused so the auth header never leaves the vendor host.
"""
from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, NoReturn

from switch_api_key import DEFAULT_SECRETS_DIR as SECRETS_DIR

UA = "deep-research-post-scripts/1"

# pool -> (base URL, auth header, header value prefix)
VENDORS: dict[str, tuple[str, str, str]] = {
    "exa": ("https://api.exa.ai", "x-api-key", ""),
    "firecrawl": ("https://api.firecrawl.dev/v2", "Authorization", "Bearer "),
    "brightdata": ("https://api.brightdata.com", "Authorization", "Bearer "),
    "browserbase": ("https://api.browserbase.com/v1", "X-BB-API-Key", ""),
    "scrapegraph": ("https://v2-api.scrapegraphai.com/api", "SGAI-APIKEY", ""),
    "tavily": ("https://api.tavily.com", "Authorization", "Bearer "),
    "apify": ("https://api.apify.com/v2", "Authorization", "Bearer "),
    "agentql": ("https://api.agentql.com/v1", "X-API-Key", ""),
}

PATH_OK = re.compile(r"^/[A-Za-z0-9._~%!$'()*+,;=:@/-]*$")
CODE_HEADERS = ("x-brd-error-code", "x-brd-err-code")
MESSAGE_HEADERS = ("x-brd-error", "x-brd-err-msg")


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args: Any, **kw: Any) -> None:
        return None


OPENER = urllib.request.build_opener(_NoRedirect)


def fail(status: int | str, code: str, message: str) -> NoReturn:
    print(json.dumps({"status": status, "code": code, "message": message[:500]}, ensure_ascii=True), file=sys.stderr)
    sys.exit(1)


def load_key(pool: str) -> str:
    path = SECRETS_DIR / pool
    try:
        key = path.read_text(encoding="utf-8").strip()
    except OSError:
        fail("-", "key_unreadable", f"cannot read {path}")
    if not key:
        fail("-", "key_empty", f"{path} is empty")
    if re.search(r"\s", key):
        fail("-", "key_malformed", f"{path} has whitespace")
    return key


def vendor_code(status: int, headers: Any, payload: Any) -> tuple[str, str]:
    """Return (code, message) for an error response."""
    code = next((headers.get(h) for h in CODE_HEADERS if headers.get(h)), None)
    message = ""
    if isinstance(payload, dict):
        err = payload.get("error")
        if isinstance(err, dict):
            code = code or err.get("code") or err.get("type")
            message = err.get("message") or ""
        elif isinstance(err, str):
            message = err
        code = code or payload.get("tag") or payload.get("code")
        message = message or str(payload.get("message") or "")
    elif isinstance(payload, str):
        message = payload
    message = message or next((headers.get(h) for h in MESSAGE_HEADERS if headers.get(h)), "")
    return str(code or status), message


def parse_body(raw: bytes) -> Any:
    text = raw.decode("utf-8", errors="replace")
    if not text.strip():
        return None
    try:
        return json.loads(text)
    except ValueError:
        return text


def call(
    pool: str,
    method: str,
    path: str,
    body: dict | None = None,
    params: dict | None = None,
    headers: dict | None = None,
) -> tuple[int, Any]:
    base, auth_header, prefix = VENDORS[pool]
    if not PATH_OK.match(path) or "//" in path or ".." in path.split("/"):
        fail("-", "bad_path", "path must be /segment/... with URL-safe characters only")
    for k, v in (headers or {}).items():
        if k.lower() in ("host", auth_header.lower()) or re.search(r"[\x00-\x1f\x7f]", f"{k}{v}"):
            fail("-", "bad_header", f"header {k!r} not allowed")
    url = base + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req_headers = {"User-Agent": UA, "Accept": "application/json", auth_header: prefix + load_key(pool)}
    if data is not None:
        req_headers["Content-Type"] = "application/json"
    req_headers.update(headers or {})
    req = urllib.request.Request(url, data=data, method=method, headers=req_headers)
    try:
        with OPENER.open(req, timeout=60) as resp:
            payload = parse_body(resp.read())
            if any(resp.headers.get(h) for h in CODE_HEADERS):
                fail(resp.status, *vendor_code(resp.status, resp.headers, payload))
            return resp.status, payload
    except urllib.error.HTTPError as exc:
        payload = parse_body(exc.read())
        fail(exc.code, *vendor_code(exc.code, exc.headers, payload))
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        fail("-", "network_error", str(getattr(exc, "reason", exc)))


def emit(status: int, payload: Any) -> None:
    if payload is None or isinstance(payload, str):
        payload = {"status": status, "body": payload}
    print(json.dumps(payload, ensure_ascii=True))


def run(pool: str, method: str, path: str, body: dict | None = None, **kw: Any) -> None:
    emit(*call(pool, method, path, body, **kw))


def load_json_arg(value: str) -> Any:
    """JSON literal, or @file to read it from a file."""
    text = value
    if value.startswith("@"):
        try:
            text = Path(value[1:]).read_text(encoding="utf-8")
        except OSError as exc:
            fail("-", "bad_json_file", f"cannot read {value[1:]}: {exc.strerror}")
    try:
        return json.loads(text)
    except ValueError as exc:
        fail("-", "bad_json", f"invalid JSON argument: {exc}")


def add_id_commands(sub: Any, table: dict[str, tuple[str, str]]) -> dict[str, Any]:
    """Register `<name> <id>` subcommands; table maps name -> (HTTP method, path with {id})."""
    parsers = {}
    for name, (method, path) in table.items():
        parsers[name] = sub.add_parser(name)
        parsers[name].add_argument("id")
        parsers[name].set_defaults(method=method, path=path)
    return parsers


def dispatch(pool: str, args: Any, **kw: Any) -> None:
    run(pool, args.method, args.path.format(id=urllib.parse.quote(args.id, safe="")), **kw)


def poll(pool: str, path: str, params: dict, waits: tuple[int, ...], timeout: int) -> tuple[int, Any]:
    """GET until status != 202. `waits` gives the sleeps before each poll; the last one repeats.
    Still 202 after `timeout` seconds: fail with code `timeout`."""
    deadline = time.monotonic() + timeout
    i = 0
    while True:
        time.sleep(waits[min(i, len(waits) - 1)])
        status, payload = call(pool, "GET", path, params=params)
        if status != 202:
            return status, payload
        if time.monotonic() > deadline:
            fail(202, "timeout", f"still pending after {timeout}s")
        i += 1

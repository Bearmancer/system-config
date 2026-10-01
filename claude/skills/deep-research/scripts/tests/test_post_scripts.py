import http.server
import io
import json
import sys
import threading
import urllib.error
from email.message import Message
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import _post_common as pc  # noqa: E402
import brightdata_unlocker  # noqa: E402
import browserbase_agent_run  # noqa: E402
import exa_agent_run  # noqa: E402
import exa_answer  # noqa: E402
import exa_batches  # noqa: E402
import firecrawl_batch_scrape  # noqa: E402
import scrapegraph_crawl  # noqa: E402
import vendor_request  # noqa: E402

FAKE_KEY = "fake-key-1234567890"


class FakeResp:
    def __init__(self, status, body, headers=None):
        self.status = status
        self._body = body if isinstance(body, bytes) else json.dumps(body).encode()
        self.headers = Message()
        for k, v in (headers or {}).items():
            self.headers[k] = v

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


@pytest.fixture
def net(tmp_path, monkeypatch):
    for pool in pc.VENDORS:
        (tmp_path / pool).write_text(FAKE_KEY + "\n", encoding="utf-8")
    monkeypatch.setattr(pc, "SECRETS_DIR", tmp_path)
    monkeypatch.setattr(pc.time, "sleep", lambda s: None)

    class Net:
        sent = []
        replies = []

        def reply(self, status, body, headers=None):
            self.replies.append((status, body, headers or {}))

    n = Net()
    n.sent, n.replies = [], []

    def fake_urlopen(req, timeout=None):
        n.sent.append(req)
        status, body, headers = n.replies.pop(0)
        if status >= 400:
            msg = Message()
            for k, v in headers.items():
                msg[k] = v
            raw = body if isinstance(body, bytes) else json.dumps(body).encode()
            raise urllib.error.HTTPError(req.full_url, status, "err", msg, io.BytesIO(raw))
        return FakeResp(status, body, headers)

    monkeypatch.setattr(pc.OPENER, "open", fake_urlopen)
    return n


def sent_json(req):
    return json.loads(req.data.decode())


CASES = [
    (exa_answer, ["hello"], "POST", "https://api.exa.ai/answer", {"query": "hello"}),
    (exa_answer, ["q", "--model", "exa-fast", "--output-schema", '{"type":"object"}'], "POST",
     "https://api.exa.ai/answer", {"query": "q", "model": "exa-fast", "outputSchema": {"type": "object"}}),
    (exa_agent_run, ["stop", "run_1"], "POST", "https://api.exa.ai/agent/runs/run_1/stop", None),
    (exa_agent_run, ["cancel", "run_1"], "POST", "https://api.exa.ai/agent/runs/run_1/cancel", None),
    (exa_batches, ["start", "--requests", '[{"customId":"a"}]'], "POST", "https://api.exa.ai/batches",
     {"requests": [{"customId": "a"}]}),
    (exa_batches, ["status", "b1"], "GET", "https://api.exa.ai/batches/b1", None),
    (exa_batches, ["cancel", "b1"], "POST", "https://api.exa.ai/batches/b1/cancel", None),
    (firecrawl_batch_scrape, ["start", "https://a.test"], "POST", "https://api.firecrawl.dev/v2/batch/scrape",
     {"urls": ["https://a.test"], "formats": ["markdown"]}),
    (firecrawl_batch_scrape, ["status", "j1"], "GET", "https://api.firecrawl.dev/v2/batch/scrape/j1", None),
    (firecrawl_batch_scrape, ["cancel", "j1"], "DELETE", "https://api.firecrawl.dev/v2/batch/scrape/j1", None),
    (firecrawl_batch_scrape, ["errors", "j1"], "GET", "https://api.firecrawl.dev/v2/batch/scrape/j1/errors", None),
    (brightdata_unlocker, ["start", "--zone", "z1", "https://a.test"], "POST",
     "https://api.brightdata.com/unblocker/req?zone=z1", {"url": "https://a.test"}),
    (brightdata_unlocker, ["result", "r1"], "GET", "https://api.brightdata.com/unblocker/get_result?response_id=r1", None),
    (browserbase_agent_run, ["start", "do it"], "POST", "https://api.browserbase.com/v1/agents/runs", {"task": "do it"}),
    (browserbase_agent_run, ["status", "r9"], "GET", "https://api.browserbase.com/v1/agents/runs/r9", None),
    (scrapegraph_crawl, ["start", "https://a.test", "--max-pages", "1"], "POST",
     "https://v2-api.scrapegraphai.com/api/crawl",
     {"url": "https://a.test", "formats": [{"type": "markdown"}], "maxPages": 1}),
    (scrapegraph_crawl, ["status", "c1"], "GET", "https://v2-api.scrapegraphai.com/api/crawl/c1", None),
    (scrapegraph_crawl, ["stop", "c1"], "POST", "https://v2-api.scrapegraphai.com/api/crawl/c1/stop", None),
    (scrapegraph_crawl, ["resume", "c1"], "POST", "https://v2-api.scrapegraphai.com/api/crawl/c1/resume", None),
    (scrapegraph_crawl, ["delete", "c1"], "DELETE", "https://v2-api.scrapegraphai.com/api/crawl/c1", None),
    (scrapegraph_crawl, ["pages", "c1", "--limit", "5"], "GET",
     "https://v2-api.scrapegraphai.com/api/crawl/c1/pages?limit=5", None),
    (scrapegraph_crawl, ["pages", "c1", "--cursor", "50"], "GET",
     "https://v2-api.scrapegraphai.com/api/crawl/c1/pages?cursor=50", None),
]


CASES += [
    (vendor_request, ["scrapegraph", "GET", "/credits"], "GET", "https://v2-api.scrapegraphai.com/api/credits", None),
    (vendor_request, ["exa", "POST", "/findSimilar", "--body", '{"url":"https://a.test"}'], "POST",
     "https://api.exa.ai/findSimilar", {"url": "https://a.test"}),
    (vendor_request, ["apify", "GET", "/store", "--param", "search=maps", "--param", "limit=3"], "GET",
     "https://api.apify.com/v2/store?search=maps&limit=3", None),
    (vendor_request, ["agentql", "POST", "/query-data", "--body", '{"query":"{ a }","url":"https://a.test"}'], "POST",
     "https://api.agentql.com/v1/query-data", {"query": "{ a }", "url": "https://a.test"}),
    (vendor_request, ["tavily", "POST", "/research", "--body", '{"input":"q"}'], "POST",
     "https://api.tavily.com/research", {"input": "q"}),
]


@pytest.mark.parametrize("mod,argv,method,url,body", CASES)
def test_request_shape(net, capsys, mod, argv, method, url, body):
    net.reply(200, {"ok": True})
    mod.main(argv)
    req = net.sent[0]
    assert (req.get_method(), req.full_url) == (method, url)
    assert (sent_json(req) if req.data else None) == body
    assert json.loads(capsys.readouterr().out) == {"ok": True}


@pytest.mark.parametrize("argv", [["status", "b1"], ["cancel", "b1"], ["start", "--requests", "[]"]])
def test_exa_batches_send_beta_header(net, argv):
    net.reply(200, {})
    exa_batches.main(argv)
    assert net.sent[0].get_header("Exa-beta") == "batches-2026-06-06"


@pytest.mark.parametrize(
    "pool,header,value",
    [
        ("exa", "X-api-key", FAKE_KEY),
        ("firecrawl", "Authorization", f"Bearer {FAKE_KEY}"),
        ("brightdata", "Authorization", f"Bearer {FAKE_KEY}"),
        ("browserbase", "X-bb-api-key", FAKE_KEY),
        ("scrapegraph", "Sgai-apikey", FAKE_KEY),
        ("tavily", "Authorization", f"Bearer {FAKE_KEY}"),
        ("apify", "Authorization", f"Bearer {FAKE_KEY}"),
        ("agentql", "X-api-key", FAKE_KEY),
    ],
)
def test_auth_header_per_vendor(net, pool, header, value):
    net.reply(200, {})
    pc.call(pool, "GET", "/x")
    assert net.sent[0].get_header(header) == value


@pytest.mark.parametrize(
    "status,body,headers,code",
    [
        (402, {"requestId": "r", "error": "no credit", "tag": "INSUFFICIENT_CREDITS"}, {}, "INSUFFICIENT_CREDITS"),
        (404, {"error": {"type": "NOT_FOUND", "code": "RUN_NOT_FOUND", "message": "gone"}}, {}, "RUN_NOT_FOUND"),
        (403, {"error": {"type": "auth_invalid_key", "message": "bad"}}, {}, "auth_invalid_key"),
        (402, {"error": "Payment required"}, {}, "402"),
        (407, b"", {"x-brd-error-code": "client_10020"}, "client_10020"),
        (502, b"boom", {"x-brd-err-code": "reject_block"}, "reject_block"),
    ],
)
def test_http_error_exits_1_with_vendor_code(net, capsys, status, body, headers, code):
    net.reply(status, body, headers)
    with pytest.raises(SystemExit) as exc:
        pc.call("exa", "GET", "/x")
    assert exc.value.code == 1
    err = json.loads(capsys.readouterr().err)
    assert err["status"] == status
    assert err["code"] == code


def test_key_never_reaches_output_on_error(net, capsys):
    net.reply(401, {"error": "bad key"})
    with pytest.raises(SystemExit):
        exa_answer.main(["q"])
    out = capsys.readouterr()
    assert FAKE_KEY not in out.out + out.err


def test_missing_key_file_exits_1_naming_path_only(net, tmp_path, capsys):
    (tmp_path / "exa").unlink()
    with pytest.raises(SystemExit) as exc:
        exa_answer.main(["q"])
    assert exc.value.code == 1
    assert json.loads(capsys.readouterr().err)["code"] == "key_unreadable"
    assert net.sent == []


def test_non_json_202_is_wrapped(net, capsys):
    net.reply(202, b"Request is pending")
    brightdata_unlocker.main(["result", "r1"])
    assert json.loads(capsys.readouterr().out) == {"status": 202, "body": "Request is pending"}


def test_result_wait_polls_until_done(net, capsys):
    net.reply(202, b"Request is pending")
    net.reply(202, b"Request is pending")
    net.reply(200, {"status_code": 200, "body": "ok"})
    brightdata_unlocker.main(["result", "r1", "--wait"])
    assert len(net.sent) == 3
    assert json.loads(capsys.readouterr().out)["status_code"] == 200


def test_poll_timeout_fails_with_code(net, monkeypatch, capsys):
    clock = iter([0, 5, 50, 500])
    monkeypatch.setattr(pc.time, "monotonic", lambda: next(clock))
    for _ in range(3):
        net.reply(202, b"pending")
    with pytest.raises(SystemExit) as exc:
        brightdata_unlocker.main(["result", "r1", "--wait", "--timeout", "30"])
    assert exc.value.code == 1
    err = json.loads(capsys.readouterr().err)
    assert (err["status"], err["code"]) == (202, "timeout")


def test_result_status_code_error_uses_header_code(net, capsys):
    net.reply(200, {"status_code": 502, "headers": {"X-Brd-Error-Code": "reject_block"}, "body": ""})
    with pytest.raises(SystemExit) as exc:
        brightdata_unlocker.main(["result", "r1"])
    assert exc.value.code == 1
    err = json.loads(capsys.readouterr().err)
    assert (err["status"], err["code"]) == (502, "reject_block")


def test_result_status_code_error_without_header_falls_back_to_status(net, capsys):
    net.reply(200, {"status_code": 404, "headers": {}, "body": "not found"})
    with pytest.raises(SystemExit):
        brightdata_unlocker.main(["result", "r1"])
    assert json.loads(capsys.readouterr().err)["code"] == "404"


def test_result_status_code_ok_is_emitted(net, capsys):
    net.reply(200, {"status_code": 200, "headers": {}, "body": "hi"})
    brightdata_unlocker.main(["result", "r1"])
    assert json.loads(capsys.readouterr().out)["body"] == "hi"


def test_direct_2xx_with_error_header_fails(net, capsys):
    net.reply(200, b"", {"x-brd-error-code": "reject_block", "x-brd-error": "blocked"})
    with pytest.raises(SystemExit):
        pc.call("brightdata", "POST", "/request", {})
    err = json.loads(capsys.readouterr().err)
    assert (err["status"], err["code"], err["message"]) == (200, "reject_block", "blocked")


def test_error_message_falls_back_to_err_msg_header(net, capsys):
    net.reply(502, b"", {"x-brd-err-code": "peer_x", "x-brd-err-msg": "peer failed"})
    with pytest.raises(SystemExit):
        pc.call("brightdata", "GET", "/x")
    assert json.loads(capsys.readouterr().err)["message"] == "peer failed"


def test_key_with_inner_whitespace_rejected_without_echo(net, tmp_path, capsys):
    (tmp_path / "exa").write_text("part1 part2", encoding="utf-8")
    with pytest.raises(SystemExit) as exc:
        exa_answer.main(["q"])
    assert exc.value.code == 1
    err = capsys.readouterr().err
    assert json.loads(err)["code"] == "key_malformed"
    assert "part1" not in err and "part2" not in err
    assert net.sent == []


def test_redirect_refused_and_auth_not_forwarded(tmp_path, monkeypatch, capsys):
    seen = []

    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            seen.append((self.path, self.headers.get("x-api-key")))
            if self.path == "/start":
                self.send_response(302)
                self.send_header("Location", "/elsewhere")
                self.end_headers()
            else:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"{}")

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    (tmp_path / "exa").write_text(FAKE_KEY, encoding="utf-8")
    monkeypatch.setattr(pc, "SECRETS_DIR", tmp_path)
    monkeypatch.setitem(pc.VENDORS, "exa", (f"http://127.0.0.1:{srv.server_port}", "x-api-key", ""))
    try:
        with pytest.raises(SystemExit) as exc:
            pc.call("exa", "GET", "/start")
    finally:
        srv.shutdown()
        srv.server_close()
    assert exc.value.code == 1
    assert json.loads(capsys.readouterr().err)["status"] == 302
    assert [path for path, _ in seen] == ["/start"]


def test_json_file_unreadable_exits_1(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        pc.load_json_arg(f"@{tmp_path / 'missing.json'}")
    assert exc.value.code == 1
    assert json.loads(capsys.readouterr().err)["code"] == "bad_json_file"


def test_poll_wait_schedule(net, monkeypatch):
    waits = []
    monkeypatch.setattr(pc.time, "sleep", waits.append)
    for _ in range(4):
        net.reply(202, b"pending")
    net.reply(200, {})
    pc.poll("brightdata", "/p", {}, (20, 10, 5), 10**6)
    assert waits == [20, 10, 5, 5, 5]


def test_ids_are_url_quoted(net):
    net.reply(200, {})
    exa_agent_run.main(["stop", "a/b c"])
    assert net.sent[0].full_url == "https://api.exa.ai/agent/runs/a%2Fb%20c/stop"


def test_json_arg_from_file(tmp_path):
    f = tmp_path / "r.json"
    f.write_text('[{"customId": "x"}]', encoding="utf-8")
    assert pc.load_json_arg(f"@{f}") == [{"customId": "x"}]


def test_bad_json_arg_exits_1(capsys):
    with pytest.raises(SystemExit) as exc:
        pc.load_json_arg("{nope")
    assert exc.value.code == 1


def test_vendor_request_extra_header_sent(net):
    net.reply(200, {})
    vendor_request.main(["exa", "GET", "/batches/b1", "--header", "Exa-Beta=batches-2026-06-06"])
    assert net.sent[0].get_header("Exa-beta") == "batches-2026-06-06"


@pytest.mark.parametrize(
    "argv,code",
    [(["exa", "GET", "search"], "bad_path"), (["exa", "GET", "/x", "--param", "novalue"], "bad_param")],
)
def test_vendor_request_rejects_bad_input_before_network(net, capsys, argv, code):
    with pytest.raises(SystemExit) as exc:
        vendor_request.main(argv)
    assert exc.value.code == 1
    assert json.loads(capsys.readouterr().err)["code"] == code
    assert net.sent == []

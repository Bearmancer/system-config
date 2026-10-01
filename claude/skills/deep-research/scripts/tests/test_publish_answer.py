import argparse
import subprocess
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import publish_teach as pt

BODY = '<h2>Bottom Line</h2><p><strong>Confirmed.</strong> <a href="https://example.org/x">Source</a></p>'


class FakeResp:
    def __init__(self, status, body):
        self.status = status
        self._body = body

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


@pytest.fixture
def env(tmp_path, monkeypatch):
    staging = tmp_path / "site"
    (staging / ".git").mkdir(parents=True)
    body = tmp_path / "body.html"
    body.write_text(BODY, encoding="utf-8")
    calls = []

    def done(stdout="", rc=0):
        return subprocess.CompletedProcess([], rc, stdout=stdout, stderr="")

    def fake_run_checked(args, cwd):
        calls.append(args)
        if args[:3] == ["git", "diff", "--cached"]:
            return done(rc=1)
        if args[:2] == ["git", "remote"]:
            return done("origin")
        if args[:3] == ["gh", "api", "user"]:
            return done("bearmancer")
        return done()

    monkeypatch.setattr(pt, "run_checked", fake_run_checked)
    monkeypatch.setattr(
        pt.subprocess, "run", lambda args, **kw: calls.append(args) or done()
    )
    monkeypatch.setattr(pt.time, "sleep", lambda s: None)

    class Env:
        pass

    e = Env()
    e.calls, e.staging = calls, staging
    e.args = argparse.Namespace(
        page=body,
        kind="verdict",
        title="Is the Eiffel Tower in Paris?",
        repo_name="bearmancer.github.io",
        staging=staging,
        no_push=False,
    )
    e.page = staging / "answers" / "verdict-is-the-eiffel-tower-in-paris.html"
    return e


def live(monkeypatch, replies):
    seen = []

    def fake_urlopen(url, timeout=None):
        seen.append(url)
        reply = replies.pop(0) if len(replies) > 1 else replies[0]
        if isinstance(reply, int):
            raise urllib.error.HTTPError(url, reply, "err", {}, None)
        return FakeResp(*reply)

    monkeypatch.setattr(pt.urllib.request, "urlopen", fake_urlopen)
    return seen


def test_check_answer_body_needs_inline_link():
    with pytest.raises(ValueError, match="inline https link"):
        pt.check_answer_body("<p>no links</p>")


def test_check_answer_body_refuses_sources_heading():
    with pytest.raises(ValueError, match="Sources"):
        pt.check_answer_body(BODY + "<h2>Sources</h2>")


def test_check_answer_body_accepts_cited_body():
    pt.check_answer_body(BODY)


def test_slugify_bounds_and_strips():
    assert pt.slugify("Is the Eiffel Tower in Paris?") == "is-the-eiffel-tower-in-paris"
    assert len(pt.slugify("x" * 200)) == 60


def test_answer_html_layout():
    page = pt.build_answer_html("recommend", "Soviet <Deep> Cuts", BODY, "2026-09-30")
    assert "<title>Soviet &lt;Deep&gt; Cuts</title>" in page
    assert '<p class="kicker">Recommendation</p>' in page
    assert 'href="../assets/lesson.css"' in page
    assert 'src="../assets/shell.js"' in page
    assert BODY in page
    assert 'class="lesson-footer"' in page
    assert page.count('class="A-bar"') == 1


def test_probe_needs_title_bytes(monkeypatch):
    monkeypatch.setattr(pt.time, "sleep", lambda s: None)
    seen = live(monkeypatch, [404, (200, b"stale"), (200, b"<title>T</title>")])
    assert pt.probe("https://x/p.html", "<title>T</title>") == ("200", True)
    assert len(seen) == 3


def test_probe_reports_missing_needle(monkeypatch):
    monkeypatch.setattr(pt.time, "sleep", lambda s: None)
    live(monkeypatch, [(200, b"other")])
    assert pt.probe("https://x/p.html", "T", attempts=3) == ("200", False)


def test_publish_answer_writes_page_index_and_pushes(env, monkeypatch):
    title = "Is the Eiffel Tower in Paris?"
    seen = live(monkeypatch, [(200, f"<title>{title}</title>".encode())])
    assert pt.publish_answer(env.args) is True
    assert "Confirmed." in env.page.read_text(encoding="utf-8")
    index = (env.staging / "index.html").read_text(encoding="utf-8")
    assert (
        '<a href="answers/verdict-is-the-eiffel-tower-in-paris.html">'
        "Is the Eiffel Tower in Paris?</a></td><td>Verdict" in index
    )
    assert (env.staging / "assets" / "lesson.css").is_file()
    assert (env.staging / ".nojekyll").is_file()
    assert ["git", "push", "-u", "origin", "main"] in env.calls
    assert any(c[:2] == ["git", "commit"] and "verdict" in c[3] for c in env.calls)
    assert seen == [
        "https://bearmancer.github.io/answers/verdict-is-the-eiffel-tower-in-paris.html"
    ]


def test_publish_answer_fails_when_live_bytes_lack_title(env, monkeypatch):
    live(monkeypatch, [(200, b"<title>old page</title>")])
    assert pt.publish_answer(env.args) is False


def test_publish_answer_fails_on_http_error(env, monkeypatch):
    live(monkeypatch, [404])
    assert pt.publish_answer(env.args) is False


def test_publish_answer_rejects_uncited_body_before_any_git(env):
    env.args.page.write_text("<p>uncited</p>", encoding="utf-8")
    with pytest.raises(ValueError):
        pt.publish_answer(env.args)
    assert env.calls == []
    assert not env.page.exists()


def test_recommend_kind_row_and_course_rebuild_keeps_answers(env, monkeypatch):
    env.args.kind, env.args.title = "recommend", "Soviet Symphonies"
    live(monkeypatch, [(200, b"<title>Soviet Symphonies</title>")])
    assert pt.publish_answer(env.args) is True
    pt.write_hub(env.staging, pt.course_rows(env.staging))
    index = (env.staging / "index.html").read_text(encoding="utf-8")
    assert "Soviet Symphonies</a></td><td>Recommendation" in index


def test_answer_kind_page_label_hub_row_and_rebuild(env, monkeypatch):
    page = pt.build_answer_html("answer", "Is it true?", BODY, "2026-09-30")
    assert '<p class="kicker">Answer</p>' in page
    env.args.kind, env.args.title = "answer", "Is it true?"
    live(monkeypatch, [(200, b"<title>Is it true?</title>")])
    assert pt.publish_answer(env.args) is True
    assert (env.staging / "answers" / "answer-is-it-true.html").is_file()
    pt.write_hub(env.staging, pt.course_rows(env.staging))
    index = (env.staging / "index.html").read_text(encoding="utf-8")
    assert "Is it true?</a></td><td>Answer" in index


def test_index_without_answers_has_no_answers_table():
    assert "<h2>Answers</h2>" not in pt.build_top_index_html("")


def test_publish_answer_rejects_empty_slug_before_any_write(env):
    env.args.title = "日本語 !!!"
    with pytest.raises(ValueError, match="no ASCII letters/digits"):
        pt.publish_answer(env.args)
    assert env.calls == []
    assert not (env.staging / "answers").exists()
    assert not (env.staging / "index.html").exists()


def test_publish_answer_no_push_writes_page_and_skips_publish(env, monkeypatch, capsys):
    env.args.no_push = True

    def boom(*a, **kw):
        raise AssertionError("publish must not run")

    monkeypatch.setattr(pt, "publish", boom)
    assert pt.publish_answer(env.args) is True
    assert "Confirmed." in env.page.read_text(encoding="utf-8")
    assert (env.staging / "index.html").is_file()
    assert not any(c[:2] in (["git", "push"], ["git", "commit"]) for c in env.calls)
    assert f"== --no-push: answers/{env.page.name}" in capsys.readouterr().out


def test_publish_with_paths_stages_only_those_paths(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    repo.mkdir()
    real = pt.run_checked

    def git(*args):
        return subprocess.run(
            ["git", *args], cwd=repo, capture_output=True, text=True, check=True
        )

    git("init", "-b", "main")
    git("config", "user.email", "t@example.org")
    git("config", "user.name", "t")
    (repo / "keep.html").write_text("k", encoding="utf-8")
    (repo / "stray.txt").write_text("s", encoding="utf-8")

    def fake_run_checked(args, cwd):
        if args[0] == "git" and args[1] != "push":
            return real(args, cwd)
        if args[:2] == ["git", "push"]:
            return subprocess.CompletedProcess([], 0, stdout="", stderr="")
        if args[:2] == ["gh", "api"]:
            return subprocess.CompletedProcess([], 0, stdout="bearmancer", stderr="")
        return subprocess.CompletedProcess([], 0, stdout="", stderr="")

    monkeypatch.setattr(pt, "run_checked", fake_run_checked)
    monkeypatch.setattr(pt, "probe", lambda *a, **kw: ("200", True))
    monkeypatch.setattr(pt.time, "sleep", lambda s: None)
    git("remote", "add", "origin", "https://example.invalid/x.git")
    assert pt.publish(repo, "r", "msg", 1, "keep.html", "k", ["keep.html"]) is True
    assert git("ls-files").stdout.split() == ["keep.html"]
    assert git("status", "--porcelain").stdout.strip() == "?? stray.txt"


def test_rules_kind_page_label_hub_row(env, monkeypatch):
    page = pt.build_answer_html("rules", "Ark Nova", BODY, "2026-10-01")
    assert '<p class="kicker">Rules</p>' in page
    env.args.kind, env.args.title = "rules", "Ark Nova"
    live(monkeypatch, [(200, b"<title>Ark Nova</title>")])
    assert pt.publish_answer(env.args) is True
    assert (env.staging / "answers" / "rules-ark-nova.html").is_file()
    pt.write_hub(env.staging, pt.course_rows(env.staging))
    index = (env.staging / "index.html").read_text(encoding="utf-8")
    assert "Ark Nova</a></td><td>Rules" in index

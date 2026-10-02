import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import publish_teach as pt


def git(cwd, *args):
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout


def make_course(source, name):
    lessons = source / name / "lessons"
    lessons.mkdir(parents=True)
    (lessons / "01-ch1-intro.html").write_text(
        f"<html><title>{name} ch1</title></html>", encoding="utf-8"
    )


@pytest.fixture
def site(tmp_path, monkeypatch):
    staging = tmp_path / "site"
    staging.mkdir()
    git(staging, "init", "-b", "main")
    git(staging, "config", "user.email", "t@example.org")
    git(staging, "config", "user.name", "t")
    source = tmp_path / "src"
    source.mkdir()

    real_run_checked = pt.run_checked

    def fake_run_checked(args, cwd):
        if args[0] == "git" and args[1] != "push":
            return real_run_checked(args, cwd)
        out = "bearmancer" if args[:3] == ["gh", "api", "user"] else "origin"
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")

    monkeypatch.setattr(pt, "run_checked", fake_run_checked)
    monkeypatch.setattr(pt, "push_sources", lambda s: None)
    monkeypatch.setattr(pt, "probe", lambda *a, **k: ("200", True))
    monkeypatch.setattr(
        sys,
        "argv",
        ["publish_teach.py", "--source", str(source), "--staging", str(staging)],
    )
    return source, staging


def test_publishing_one_course_keeps_other_courses(site):
    source, staging = site
    make_course(source, "course-a")
    make_course(source, "course-b")
    pt.main()
    assert "course-b/index.html" in git(staging, "ls-tree", "-r", "--name-only", "HEAD")

    for f in sorted((staging / "course-b").rglob("*"), reverse=True):
        f.rmdir() if f.is_dir() else f.unlink()
    (staging / "course-b").rmdir()
    for f in sorted((source / "course-b").rglob("*"), reverse=True):
        f.rmdir() if f.is_dir() else f.unlink()
    (source / "course-b").rmdir()

    pt.main()
    tracked = git(staging, "ls-tree", "-r", "--name-only", "HEAD")
    assert "course-a/index.html" in tracked
    assert "course-b/index.html" in tracked
    assert "course-b/lessons/01-ch1-intro.html" in tracked


def test_non_course_workspace_is_skipped(site):
    source, staging = site
    make_course(source, "course-a")
    make_course(source, "course-b")
    non_course = source / "boardgames" / "ark-nova"
    non_course.mkdir(parents=True)
    (non_course / "rules.body.html").write_text(
        "<html><title>Ark Nova rules</title></html>", encoding="utf-8"
    )

    pt.main()

    assert not (staging / "boardgames").exists()
    index = (staging / "index.html").read_text(encoding="utf-8")
    assert "boardgames" not in index
    tracked = git(staging, "ls-tree", "-r", "--name-only", "HEAD")
    assert "course-a/index.html" in tracked
    assert "course-b/index.html" in tracked


def test_built_index_pages_pass_the_index_gate(site):
    import check_lesson

    source, staging = site
    make_course(source, "course-a")
    make_course(source, "course-b")
    (source / "course-a" / "assets").mkdir()
    (source / "course-a" / "assets" / "lesson.css").write_text("", encoding="utf-8")
    ref = source / "course-a" / "reference"
    ref.mkdir()
    for name in ("cast-map", "glossary", "timeline"):
        (ref / f"{name}.html").write_text(
            f"<html><title>{name}</title></html>", encoding="utf-8"
        )
    (source / "course-a" / "lessons" / "01-ch1-intro.html").write_text(
        "<html><title>Intro — Course A</title><body><h1>Intro</h1></body></html>",
        encoding="utf-8",
    )
    pt.main()

    home = (staging / "course-a" / "index.html").read_text(encoding="utf-8")
    assert '<li id="ch1"><a href="lessons/01-ch1-intro.html">1 · Intro</a></li>' in home
    assert "Cast roster" not in home
    assert check_lesson.check(str(staging / "course-a" / "index.html")) == []
    assert check_lesson.check(str(staging / "index.html")) == []
    assert "Topic</th>" in (staging / "index.html").read_text(encoding="utf-8")

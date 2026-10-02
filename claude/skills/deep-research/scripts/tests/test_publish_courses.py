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


def make_course(staging, name):
    lessons = staging / name / "lessons"
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

    real_run_checked = pt.run_checked

    def fake_run_checked(args, cwd):
        if args[0] == "git" and args[1] != "push":
            return real_run_checked(args, cwd)
        out = "bearmancer" if args[:3] == ["gh", "api", "user"] else "origin"
        return subprocess.CompletedProcess(args, 0, stdout=out, stderr="")

    monkeypatch.setattr(pt, "run_checked", fake_run_checked)
    monkeypatch.setattr(pt, "probe", lambda *a, **k: ("200", True))
    monkeypatch.setattr(
        sys,
        "argv",
        ["publish_teach.py", "--staging", str(staging)],
    )
    return staging


def test_publishing_a_new_course_keeps_published_courses(site):
    staging = site
    make_course(staging, "course-a")
    pt.main()
    make_course(staging, "course-b")
    pt.main()
    tracked = git(staging, "ls-tree", "-r", "--name-only", "HEAD")
    assert "course-a/index.html" in tracked
    assert "course-b/index.html" in tracked
    assert "course-b/lessons/01-ch1-intro.html" in tracked


def test_work_dir_is_not_published(site):
    staging = site
    make_course(staging, "course-a")
    notes = staging / "work" / "course-a"
    notes.mkdir(parents=True)
    (notes / "NOTES.md").write_text("n", encoding="utf-8")
    pt.main()
    assert "work/" not in git(staging, "ls-tree", "-r", "--name-only", "HEAD")


def test_non_course_workspace_is_skipped(site):
    staging = site
    make_course(staging, "course-a")
    make_course(staging, "course-b")
    non_course = staging / "boardgames" / "ark-nova"
    non_course.mkdir(parents=True)
    (non_course / "rules.body.html").write_text(
        "<html><title>Ark Nova rules</title></html>", encoding="utf-8"
    )

    pt.main()

    index = (staging / "index.html").read_text(encoding="utf-8")
    assert "boardgames" not in index
    tracked = git(staging, "ls-tree", "-r", "--name-only", "HEAD")
    assert "course-a/index.html" in tracked
    assert "course-b/index.html" in tracked


def test_built_index_pages_pass_the_index_gate(site):
    import check_lesson

    staging = site
    make_course(staging, "course-a")
    make_course(staging, "course-b")
    (staging / "course-a" / "assets").mkdir()
    (staging / "course-a" / "assets" / "lesson.css").write_text("", encoding="utf-8")
    ref = staging / "course-a" / "reference"
    ref.mkdir()
    for name in ("cast-map", "glossary", "timeline"):
        (ref / f"{name}.html").write_text(
            f"<html><title>{name}</title></html>", encoding="utf-8"
        )
    (staging / "course-a" / "lessons" / "01-ch1-intro.html").write_text(
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


def test_md_links_flattened_in_place(site):
    staging = site
    make_course(staging, "course-a")
    page = staging / "course-a" / "lessons" / "01-ch1-intro.html"
    page.write_text(
        '<html><title>t</title><a href="../NOTES.md">notes</a></html>',
        encoding="utf-8",
    )
    pt.main()
    assert page.read_text(encoding="utf-8") == "<html><title>t</title>notes</html>"

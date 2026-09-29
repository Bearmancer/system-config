#!/usr/bin/env python3

import argparse
import json
import re
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

MD_LINK_PATTERN = re.compile(r'(?s)<a\s+[^>]*href="[^"]*\.md"[^>]*>(.*?)</a>')
TITLE_PATTERN = re.compile(r"(?s)<title>(.*?)</title>")
CHAPTER_ROW_CH_PATTERN = re.compile(r"(?i)-ch0*(\d+)")
CHAPTER_ROW_LESSON_PATTERN = re.compile(r"^(\d+)")
CHAPTER_NUM_PATTERN = re.compile(r"(?i)ch(?:apter)?\.?\s*0*(\d+)")
LESSON_PATH_PATTERN = re.compile(r"(?i)^[^/]+/lessons/")
REFERENCE_PATH_PATTERN = re.compile(r"(?i)^[^/]+/reference/")

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lesson_rules import bar_scripts, render_bar

ASSETS = Path(__file__).resolve().parent.parent / "assets"
CANONICAL_CSS = ASSETS / "lesson.css"
SHELL_JS = ASSETS / "shell.js"


def title_case(s: str) -> str:
    return re.sub(
        r"[A-Za-z]+(?:'[A-Za-z]+)*",
        lambda m: m.group(0)[0].upper() + m.group(0)[1:],
        s,
    )


def get_chapter_row_id(rel_path: str, fallback_num: int) -> str:
    file_name = Path(rel_path).name
    m = CHAPTER_ROW_CH_PATTERN.search(file_name)
    if m:
        return f"ch{m.group(1)}"
    n = CHAPTER_ROW_LESSON_PATTERN.match(file_name)
    if n:
        return f"lesson-{n.group(1)}"
    return f"lesson-{fallback_num}"


def get_chapter_num(title: str, rel_path: str) -> int:
    m = CHAPTER_NUM_PATTERN.search(f"{title} {rel_path}")
    if m:
        return int(m.group(1))
    return 999999


def remove_empty_dirs(root: Path) -> None:
    while True:
        empty_dirs = [d for d in root.rglob("*") if d.is_dir() and not any(d.iterdir())]
        if not empty_dirs:
            break
        for d in empty_dirs:
            d.rmdir()


def process_workspaces(source: Path, staging: Path) -> list[dict[str, str]]:
    published: list[dict[str, str]] = []
    for ws in sorted(p for p in source.iterdir() if p.is_dir()):
        dest = staging / ws.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.copytree(ws, dest)

        for f in list(dest.rglob("*")):
            if not f.is_file():
                continue
            in_assets = "assets" in [part.lower() for part in f.relative_to(dest).parts]
            if f.suffix.lower() != ".html" and not in_assets:
                f.unlink()

        remove_empty_dirs(dest)

        if any(dest.rglob("*.html")):
            (dest / "assets").mkdir(exist_ok=True)
            shutil.copyfile(SHELL_JS, dest / "assets" / "shell.js")
            feed = dest / "assets" / "course-index.js"
            if not feed.exists():
                feed.write_text("window.COURSE_INDEX = [];\n", encoding="utf-8")

        for html in sorted(dest.rglob("*.html")):
            text = html.read_text(encoding="utf-8")
            new_text = MD_LINK_PATTERN.sub(r"\1", text)
            if new_text != text:
                html.write_text(new_text, encoding="utf-8")
            rel = html.relative_to(staging).as_posix()
            title_match = TITLE_PATTERN.search(text)
            title = title_match.group(1).strip() if title_match else "untitled"
            published.append({"workspace": ws.name, "path": rel, "title": title})

    return published


def build_home_html(ws_title: str, lesson_rows: str, ref_rows: str, bar: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Course home — {ws_title}</title>
<link rel="stylesheet" href="assets/lesson.css">
</head>
<body>
{bar}
  <p class="home-link"><a href="../index.html">Home</a></p>
  <p class="kicker">Course Home</p>
  <h1>{ws_title}</h1>
  <h2>Chapter index</h2>
  <ul>
{lesson_rows}
  </ul>
  <h2>Cast roster · Glossary</h2>
  <ul>
{ref_rows}
  </ul>
{bar_scripts("assets/")}
</body>
</html>"""


def build_top_index_html(rows: str, generated_at: str) -> str:
    bar = render_bar("Index", [])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Index</title>
<link rel="stylesheet" href="assets/lesson.css">
</head>
<body>
{bar}
  <h1>Index</h1>
  <p class="meta">Published from the local course workspaces · {generated_at} · pick a book/video, then its chapters</p>
  <table class="hub-table">
    <tr><th>Book / Video</th><th>Chapters</th></tr>
{rows}
  </table>
{bar_scripts("assets/")}
</body>
</html>"""


def build_hub_rows(
    source: Path, staging: Path, published: list[dict[str, str]]
) -> list[dict[str, object]]:
    for ws in sorted(p for p in source.iterdir() if p.is_dir()):
        ws_pages = [p for p in published if p["workspace"] == ws.name]
        if not ws_pages:
            continue

        dest = staging / ws.name
        ws_title = ws.name.replace("-", " ").title()

        lesson_pages = [p for p in ws_pages if LESSON_PATH_PATTERN.match(p["path"])]
        ref_pages = [p for p in ws_pages if REFERENCE_PATH_PATTERN.match(p["path"])]

        lesson_rows_list: list[str] = []
        for i, p in enumerate(
            sorted(lesson_pages, key=lambda p: get_chapter_num(p["title"], p["path"])),
            start=1,
        ):
            leaf = p["path"].split("/", 1)[1]
            row_id = get_chapter_row_id(p["path"], i)
            lesson_rows_list.append(
                f'    <li id="{row_id}"><a href="{leaf}">{row_id}</a></li>'
            )

        ref_labels = {"cast-map.html": "Cast roster", "glossary.html": "Glossary"}
        ref_rows_list: list[str] = []
        for p in sorted(ref_pages, key=lambda p: p["path"]):
            label = ref_labels.get(Path(p["path"]).name.lower())
            if label is None:
                continue
            leaf = p["path"].split("/", 1)[1]
            ref_rows_list.append(f'    <li><a href="{leaf}">{label}</a></li>')

        home_html = build_home_html(
            ws_title, "\n".join(lesson_rows_list), "\n".join(ref_rows_list)
        )
        (dest / "index.html").write_text(home_html, encoding="utf-8")

    return course_rows(staging)


def course_rows(staging: Path) -> list[dict[str, object]]:
    return [
        {
            "title": d.name.replace("-", " ").title(),
            "chapters": len(list((d / "lessons").glob("*.html"))),
            "link": f"{d.name}/index.html",
        }
        for d in sorted(staging.iterdir())
        if d.is_dir()
        and not d.name.startswith(".")
        and d.name != "assets"
        and (d / "index.html").is_file()
    ]


def run_checked(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def publish(
    staging: Path, repo_name: str, commit_message: str, published_count: int
) -> None:
    if not (staging / ".git").exists():
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=staging,
            capture_output=True,
            text=True,
            check=True,
        )

    subprocess.run(
        ["git", "add", "-A"], cwd=staging, capture_output=True, text=True, check=True
    )

    status = run_checked(["git", "status", "--porcelain"], staging).stdout
    if status.strip():
        subprocess.run(
            ["git", "commit", "-m", commit_message],
            cwd=staging,
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"== committed: {commit_message}")
    else:
        print("== no changes to commit")

    view_result = run_checked(["gh", "repo", "view", repo_name], staging)
    if view_result.returncode != 0:
        print(f"== creating repo {repo_name} (public)")
        create_result = run_checked(
            [
                "gh",
                "repo",
                "create",
                repo_name,
                "--public",
                "--source",
                str(staging),
                "--remote",
                "origin",
                "--push",
            ],
            staging,
        )
        if create_result.returncode != 0:
            raise RuntimeError(
                f"repo create/push failed (exit {create_result.returncode}). Check gh auth (gh auth status) and network, then re-run."
            )
    else:
        remotes = run_checked(["git", "remote"], staging).stdout.split()
        if "origin" not in remotes:
            user = run_checked(
                ["gh", "api", "user", "--jq", ".login"], staging
            ).stdout.strip()
            subprocess.run(
                [
                    "git",
                    "remote",
                    "add",
                    "origin",
                    f"https://github.com/{user}/{repo_name}.git",
                ],
                cwd=staging,
                capture_output=True,
                text=True,
                check=True,
            )
        push_result = run_checked(["git", "push", "-u", "origin", "main"], staging)
        if push_result.returncode != 0:
            raise RuntimeError(
                f"git push failed (exit {push_result.returncode}). Likely non-fast-forward: run "
                f"git -C '{staging}' pull --rebase, resolve, then re-run."
            )

    user = run_checked(["gh", "api", "user", "--jq", ".login"], staging).stdout.strip()

    print("== enabling Pages (ignored if already on)")
    run_checked(
        [
            "gh",
            "api",
            "-X",
            "POST",
            f"repos/{user}/{repo_name}/pages",
            "-f",
            "source[branch]=main",
            "-f",
            "source[path]=/",
        ],
        staging,
    )

    site = f"https://{user}.github.io/"
    print("== done")
    print(f"site: {site}")
    print(f"pages published: {published_count}")

    code = "000"
    for _ in range(8):
        try:
            with urllib.request.urlopen(site, timeout=10) as resp:
                code = str(resp.status)
        except urllib.error.HTTPError as e:
            code = str(e.code)
        except urllib.error.URLError:
            code = "000"
        if code == "200":
            break
        import time

        time.sleep(15)

    if code == "200":
        print(f"== probe: {site} -> 200")
    else:
        print(
            f"WARNING: probe: {site} -> {code} after 2 min. Pages build still running; "
            f"retry curl.exe -s -o NUL -w '%{{http_code}}' {site} before assuming failure."
        )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-name", default="bearmancer.github.io")
    parser.add_argument(
        "--source", type=Path, default=Path.home() / "Dev" / "deep-research"
    )
    parser.add_argument(
        "--staging",
        type=Path,
        default=Path.home() / "Dev" / "bearmancer.github.io",
    )
    parser.add_argument(
        "--commit", default=f"Publish courses {datetime.now():%Y-%m-%d %H:%M}"
    )
    parser.add_argument("--no-push", action="store_true")
    args = parser.parse_args()

    staging: Path = args.staging
    source: Path = args.source

    if (
        not (staging / ".git").exists()
        and run_checked(["gh", "repo", "view", args.repo_name], Path.home()).returncode
        == 0
    ):
        # A fresh `git init` here would later push non-fast-forward against the live site.
        subprocess.run(
            ["gh", "repo", "clone", args.repo_name, str(staging)], check=True
        )
    staging.mkdir(parents=True, exist_ok=True)

    print(f"== staging: {staging}")
    published = process_workspaces(source, staging)

    (staging / ".nojekyll").touch()

    (staging / "assets").mkdir(exist_ok=True)
    shutil.copyfile(CANONICAL_CSS, staging / "assets" / "lesson.css")
    shutil.copyfile(SHELL_JS, staging / "assets" / "shell.js")

    hub_rows = build_hub_rows(source, staging, published)

    feed = [
        {
            "id": Path(str(h["link"])).parent.name,
            "label": title_case(str(h["title"])),
            "href": h["link"],
        }
        for h in hub_rows
    ]
    (staging / "assets" / "course-index.js").write_text(
        "window.COURSE_INDEX = " + json.dumps(feed) + ";\n", encoding="utf-8"
    )

    rows = "\n".join(
        f'    <tr><td><a href="{h["link"]}">{title_case(str(h["title"]))}</a></td><td>{h["chapters"]}</td></tr>'
        for h in sorted(hub_rows, key=lambda h: str(h["title"]))
    )
    top_index = build_top_index_html(rows, f"{datetime.now():%Y-%m-%d %H:%M}")
    (staging / "index.html").write_text(top_index, encoding="utf-8")

    if args.no_push:
        print(
            f"== --no-push: {len(hub_rows)} courses in hub, {len(published)} pages from source"
        )
        return
    publish(staging, args.repo_name, args.commit, len(published))


if __name__ == "__main__":
    main()

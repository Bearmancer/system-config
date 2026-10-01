#!/usr/bin/env python3

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from html import escape
from pathlib import Path

MD_LINK_PATTERN = re.compile(r'(?s)<a\s+[^>]*href="[^"]*\.md"[^>]*>(.*?)</a>')
TITLE_PATTERN = re.compile(r"(?s)<title>(.*?)</title>")
H1_PATTERN = re.compile(r"(?s)<h1[^>]*>(.*?)</h1>")
CHAPTER_ROW_CH_PATTERN = re.compile(r"(?i)-ch0*(\d+)")
CHAPTER_ROW_LESSON_PATTERN = re.compile(r"^(\d+)")
CHAPTER_NUM_PATTERN = re.compile(r"(?i)ch(?:apter)?\.?\s*0*(\d+)")
LESSON_PATH_PATTERN = re.compile(r"(?i)^[^/]+/lessons/")
REFERENCE_PATH_PATTERN = re.compile(r"(?i)^[^/]+/reference/")
SOURCES_HEADING_PATTERN = re.compile(
    r"(?i)<h[1-6][^>]*>[^<]*(sources|references|bibliography)"
)
EXTERNAL_LINK_PATTERN = re.compile(r'(?i)<a\s[^>]*href="https?://')
ANSWER_KINDS = {
    "answer": "Answer",
    "verdict": "Verdict",
    "recommend": "Recommendation",
    "rules": "Rules",
}
ANSWERS_DIR = "answers"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lesson_rules import bar_scripts, chapter_label, render_bar

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
    return f"ch{fallback_num}"


def get_lesson_number(rel_path: str, fallback_num: int) -> int:
    n = CHAPTER_ROW_LESSON_PATTERN.match(Path(rel_path).name)
    return int(n.group(1)) if n else fallback_num


def chapter_name(html: str, title: str) -> str:
    h1 = H1_PATTERN.search(html)
    if h1:
        return " ".join(re.sub(r"<[^>]+>", " ", h1.group(1)).split())
    return title.split(" — ")[0]


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
    for ws in sorted(
        p for p in source.iterdir() if p.is_dir() and not p.name.startswith(".")
    ):
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
<title>{ws_title}</title>
<link rel="stylesheet" href="assets/lesson.css">
</head>
<body>
{bar}
  <h1>{ws_title}</h1>
  <ol class="index-rows">
{lesson_rows}
  </ol>
  <nav class="index-extras">
{ref_rows}
  </nav>
{bar_scripts("assets/")}
</body>
</html>"""


def build_top_index_html(rows: str, answer_rows_html: str = "") -> str:
    bar = render_bar("Index", [], home=True)
    answers = (
        f"""  <h2>Answers</h2>
  <table class="hub-table">
    <tr><th>Page</th><th>Kind</th></tr>
{answer_rows_html}
  </table>
"""
        if answer_rows_html
        else ""
    )
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
  <table class="hub-table">
    <tr><th>Topic</th><th>Chapters</th></tr>
{rows}
  </table>
{answers}{bar_scripts("assets/")}
</body>
</html>"""


def build_hub_rows(
    source: Path, staging: Path, published: list[dict[str, str]]
) -> list[dict[str, object]]:
    for ws in sorted(
        p for p in source.iterdir() if p.is_dir() and not p.name.startswith(".")
    ):
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
            number = get_lesson_number(p["path"], i)
            name = chapter_name(
                (staging / p["path"]).read_text(encoding="utf-8"), p["title"]
            )
            lesson_rows_list.append(
                f'    <li id="{row_id}"><a href="{leaf}">{chapter_label(number, name)}</a></li>'
            )

        ref_labels = {
            "cast-map.html": "Cast",
            "glossary.html": "Glossary",
            "timeline.html": "Timeline",
        }
        ref_rows_list: list[str] = []
        for p in sorted(ref_pages, key=lambda p: p["path"]):
            label = ref_labels.get(Path(p["path"]).name.lower())
            if label is None:
                continue
            leaf = p["path"].split("/", 1)[1]
            ref_rows_list.append(f'    <a href="{leaf}">{label}</a>')

        home_html = build_home_html(
            ws_title,
            "\n".join(lesson_rows_list),
            "\n".join(ref_rows_list),
            render_bar(
                ws_title,
                [],
                current=ws.name,
                base="lessons/",
                home=True,
                topic_feed="../assets/course-index.js",
                topic_base="../",
            ),
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


def slugify(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:60].strip("-")


def check_answer_body(body: str) -> None:
    if not EXTERNAL_LINK_PATTERN.search(body):
        raise ValueError("answer body needs at least one inline https link")
    if SOURCES_HEADING_PATTERN.search(body):
        raise ValueError(
            "answer body has a Sources/References/Bibliography heading; citations stay inline"
        )


def build_answer_html(kind: str, title: str, body: str, date: str) -> str:
    label = ANSWER_KINDS[kind]
    bar = render_bar(label, [("Home", "../index.html")], base="../")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<link rel="stylesheet" href="../assets/lesson.css">
</head>
<body>
{bar}
  <p class="kicker">{label}</p>
  <h1>{escape(title)}</h1>
  <p class="surtitle">{date}</p>
{body}
  <footer class="lesson-footer">
    <nav><a href="../index.html">Home</a></nav>
  </footer>
{bar_scripts("../assets/")}
</body>
</html>"""


def answer_rows(staging: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for f in sorted((staging / ANSWERS_DIR).glob("*.html")):
        title = TITLE_PATTERN.search(f.read_text(encoding="utf-8"))
        rows.append(
            {
                "title": title.group(1).strip() if title else f.stem,
                "kind": ANSWER_KINDS.get(f.stem.split("-", 1)[0], "Answer"),
                "link": f"{ANSWERS_DIR}/{f.name}",
            }
        )
    return rows


def run_checked(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)


def push_sources(source: Path) -> None:
    add = run_checked(["git", "add", "-A"], source)
    if add.returncode != 0:
        raise RuntimeError(f"source git add failed in {source}: {add.stderr.strip()}")
    staged = run_checked(["git", "diff", "--cached", "--quiet"], source)
    if staged.returncode == 1:
        message = f"Update course sources {datetime.now():%Y-%m-%d}"
        commit = run_checked(["git", "commit", "-m", message], source)
        if commit.returncode != 0:
            raise RuntimeError(
                f"source commit failed in {source}: {commit.stderr.strip() or commit.stdout.strip()}"
            )
        print(f"== sources committed: {message}")
    elif staged.returncode != 0:
        raise RuntimeError(
            f"source git diff failed in {source}: {staged.stderr.strip()}"
        )
    push = run_checked(["git", "push"], source)
    if push.returncode != 0:
        raise RuntimeError(
            f"source push failed in {source}; not publishing HTML with unpushed sources: {push.stderr.strip()}"
        )


def probe(
    url: str, needle: str | None = None, attempts: int = 8, delay: int = 15
) -> tuple[str, bool]:
    code, found = "000", needle is None
    for attempt in range(attempts):
        if attempt:
            time.sleep(delay)
        try:
            with urllib.request.urlopen(url, timeout=10) as resp:
                code = str(resp.status)
                if needle is not None:
                    found = needle.encode() in resp.read()
        except urllib.error.HTTPError as e:
            code = str(e.code)
        except urllib.error.URLError:
            code = "000"
        if code == "200" and found:
            break
    return code, found


def publish(
    staging: Path,
    repo_name: str,
    commit_message: str,
    published_count: int,
    probe_rel: str = "",
    needle: str | None = None,
    paths: list[str] | None = None,
) -> bool:
    if not (staging / ".git").exists():
        subprocess.run(
            ["git", "init", "-b", "main"],
            cwd=staging,
            capture_output=True,
            text=True,
            check=True,
        )

    subprocess.run(
        ["git", "add", "--", *paths] if paths else ["git", "add", "-A"],
        cwd=staging,
        capture_output=True,
        text=True,
        check=True,
    )

    if run_checked(["git", "diff", "--cached", "--quiet"], staging).returncode == 1:
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

    target = f"{site}{probe_rel}"
    code, found = probe(target, needle)

    if code == "200":
        print(f"== probe: {target} -> 200")
    else:
        print(
            f"WARNING: probe: {target} -> {code} after 2 min. Pages build still running; "
            f"retry curl.exe -s -o NUL -w '%{{http_code}}' {target} before assuming failure."
        )
    if needle is not None:
        print(f"== live bytes contain page title: {found}")
        print(f"live: {target}")
    return code == "200" and found


def ensure_staging(repo_name: str, staging: Path) -> None:
    if (
        not (staging / ".git").exists()
        and run_checked(["gh", "repo", "view", repo_name], Path.home()).returncode == 0
    ):
        # A fresh `git init` here would later push non-fast-forward against the live site.
        subprocess.run(["gh", "repo", "clone", repo_name, str(staging)], check=True)
    staging.mkdir(parents=True, exist_ok=True)


def sync_shared_assets(staging: Path) -> None:
    (staging / ".nojekyll").touch()
    (staging / "assets").mkdir(exist_ok=True)
    shutil.copyfile(CANONICAL_CSS, staging / "assets" / "lesson.css")
    shutil.copyfile(SHELL_JS, staging / "assets" / "shell.js")


def write_hub(staging: Path, hub_rows: list[dict[str, object]]) -> None:
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
    answers = "\n".join(
        f'    <tr><td><a href="{a["link"]}">{a["title"]}</a></td><td>{a["kind"]}</td></tr>'
        for a in answer_rows(staging)
    )
    top_index = build_top_index_html(rows, answers)
    (staging / "index.html").write_text(top_index, encoding="utf-8")


def publish_answer(args: argparse.Namespace) -> bool:
    body = args.page.read_text(encoding="utf-8")
    check_answer_body(body)
    slug = slugify(args.title)
    if not slug:
        raise ValueError("title has no ASCII letters/digits")
    staging: Path = args.staging
    ensure_staging(args.repo_name, staging)
    sync_shared_assets(staging)
    (staging / ANSWERS_DIR).mkdir(exist_ok=True)
    rel = f"{ANSWERS_DIR}/{args.kind}-{slug}.html"
    (staging / rel).write_text(
        build_answer_html(
            args.kind, args.title, body, f"{datetime.now():%Y-%m-%d}"
        ),
        encoding="utf-8",
    )
    write_hub(staging, course_rows(staging))
    print(f"== staging: {staging}")
    if args.no_push:
        print(f"== --no-push: {rel}")
        return True
    return publish(
        staging,
        args.repo_name,
        f"Publish {args.kind} {slug} {datetime.now():%Y-%m-%d %H:%M}",
        len(answer_rows(staging)),
        rel,
        escape(args.title),
        [rel, "index.html", "assets"],
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
    parser.add_argument("--page", type=Path, help="HTML body fragment of one answer page")
    parser.add_argument("--kind", choices=sorted(ANSWER_KINDS))
    parser.add_argument("--title")
    args = parser.parse_args()

    if args.page:
        if not (args.kind and args.title):
            parser.error("--page needs --kind and --title")
        ok = publish_answer(args)
        sys.exit(0 if ok else 1)

    staging: Path = args.staging
    source: Path = args.source

    ensure_staging(args.repo_name, staging)

    if not args.no_push:
        push_sources(source)

    print(f"== staging: {staging}")
    published = process_workspaces(source, staging)

    sync_shared_assets(staging)

    hub_rows = build_hub_rows(source, staging, published)
    write_hub(staging, hub_rows)

    if args.no_push:
        print(
            f"== --no-push: {len(hub_rows)} courses in hub, {len(published)} pages from source"
        )
        return
    publish(
        staging,
        args.repo_name,
        args.commit,
        len(published),
        paths=sorted({p["workspace"] for p in published})
        + ["index.html", "assets", ".nojekyll"],
    )


if __name__ == "__main__":
    main()

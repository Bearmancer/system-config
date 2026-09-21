#!/usr/bin/env python3

import argparse
import re
import shutil
import subprocess
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

MD_LINK_PATTERN = re.compile(r'(?s)<a\s+[^>]*href="[^"]*\.md"[^>]*>(.*?)</a>')
TITLE_PATTERN = re.compile(r"(?s)<title>(.*?)</title>")
MISSION_H1_PATTERN = re.compile(r"(?m)^#\s+(.+)$")
CHAPTER_ROW_CH_PATTERN = re.compile(r"(?i)-ch0*(\d+)")
CHAPTER_ROW_LESSON_PATTERN = re.compile(r"^(\d+)")
CHAPTER_NUM_PATTERN = re.compile(r"(?i)ch(?:apter)?\.?\s*0*(\d+)")
LESSON_PATH_PATTERN = re.compile(r"(?i)^[^/]+/lessons/")
REFERENCE_PATH_PATTERN = re.compile(r"(?i)^[^/]+/reference/")
COURSE_HOME_TITLE_PATTERN = re.compile(r"(?i)^course home")


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
        dest.mkdir(parents=True, exist_ok=True)
        shutil.copytree(ws, dest, dirs_exist_ok=True)

        for f in list(dest.rglob("*")):
            if not f.is_file():
                continue
            in_assets = "assets" in [part.lower() for part in f.relative_to(dest).parts]
            if f.suffix.lower() != ".html" and not in_assets:
                f.unlink()

        remove_empty_dirs(dest)

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


def build_home_html(ws_title: str, lesson_rows: str, ref_rows: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Course home — {ws_title}</title>
<style>
  html {{ background: #fbfaf7; }}
  body {{ max-width: 46rem; margin: 0 auto; padding: 3.5rem 2.5rem 5rem; color: #201d1a;
         font-family: "Sitka Text", Constantia, Charter, Georgia, serif; font-size: 18px; line-height: 1.62; }}
  h1 {{ font-size: 2rem; font-weight: 600; margin: 0 0 .4rem; }}
  h2 {{ font-size: 1.15rem; margin: 2rem 0 .6rem; }}
  p.kicker {{ font-family: system-ui, sans-serif; font-size: .72rem; letter-spacing: .14em;
             text-transform: uppercase; color: #8a5a2b; margin: 0 0 .6rem; }}
  a {{ color: #8a5a2b; text-decoration: none; border-bottom: 1px solid rgba(138,90,43,.35); }}
  ul {{ padding-left: 1.2rem; }}
  li {{ margin: .3rem 0; }}
</style>
</head>
<body>
  <p class="kicker">Course home</p>
  <h1>{ws_title}</h1>
  <h2>Chapters</h2>
  <ul>
{lesson_rows}
  </ul>
  <h2>Reference</h2>
  <ul>
{ref_rows}
  </ul>
</body>
</html>"""


def build_top_index_html(rows: str, generated_at: str) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Teaching notes — index</title>
<style>
  html {{ background: #fbfaf7; }}
  body {{ max-width: 46rem; margin: 0 auto; padding: 3.5rem 2.5rem 5rem; color: #201d1a;
         font-family: "Sitka Text", Constantia, Charter, Georgia, serif; font-size: 18px; line-height: 1.62; }}
  h1 {{ font-size: 2rem; font-weight: 600; margin: 0 0 .4rem; }}
  p.kicker {{ font-family: system-ui, sans-serif; font-size: .72rem; letter-spacing: .14em;
             text-transform: uppercase; color: #8a5a2b; margin: 0 0 .6rem; }}
  p.meta {{ font-family: system-ui, sans-serif; font-size: .78rem; color: #5a544b; margin: 0 0 2rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: .95rem; }}
  th {{ text-align: left; border-bottom: 1.5px solid #dbd6ca; padding: .4rem .5rem; }}
  td {{ border-bottom: 1px solid #dbd6ca; padding: .4rem .5rem; vertical-align: top; }}
  a {{ color: #8a5a2b; text-decoration: none; border-bottom: 1px solid rgba(138,90,43,.35); }}
  td:last-child {{ white-space: nowrap; color: #5a544b; font-family: system-ui, sans-serif; font-size: .82rem; }}
</style>
</head>
<body>
  <p class="kicker">Teaching notes</p>
  <h1>Explanations &amp; lessons</h1>
  <p class="meta">Published from the local teaching workspaces · {generated_at} · pick a book/video, then its chapters</p>
  <table>
    <tr><th>Book / video</th><th>Chapters</th></tr>
{rows}
  </table>
</body>
</html>"""


def build_hub_rows(source: Path, staging: Path, published: list[dict[str, str]]) -> list[dict[str, object]]:
    hub_rows: list[dict[str, object]] = []
    for ws in sorted(p for p in source.iterdir() if p.is_dir()):
        ws_pages = [p for p in published if p["workspace"] == ws.name]
        if not ws_pages:
            continue

        dest = staging / ws.name
        ws_title = ws.name.replace("-", " ").title()
        mission_path = ws / "MISSION.md"
        if mission_path.exists():
            m = MISSION_H1_PATTERN.search(mission_path.read_text(encoding="utf-8"))
            if m:
                ws_title = m.group(1).strip()

        existing_home = None
        for p in ws_pages:
            if COURSE_HOME_TITLE_PATTERN.match(p["title"]) or Path(p["path"]).name.lower() == "index.html":
                existing_home = p
                break

        lesson_pages = [p for p in ws_pages if LESSON_PATH_PATTERN.match(p["path"])]
        ref_pages = [p for p in ws_pages if REFERENCE_PATH_PATTERN.match(p["path"])]
        chapter_count = len(lesson_pages)

        if existing_home:
            home_rel_from_root = existing_home["path"]
        else:
            lesson_rows_list: list[str] = []
            for i, p in enumerate(sorted(lesson_pages, key=lambda p: get_chapter_num(p["title"], p["path"])), start=1):
                leaf = p["path"].split("/", 1)[1]
                row_id = get_chapter_row_id(p["path"], i)
                lesson_rows_list.append(f'    <li id="{row_id}"><a href="{leaf}">{p["title"]}</a></li>')

            ref_rows_list: list[str] = []
            for p in sorted(ref_pages, key=lambda p: p["path"]):
                leaf = p["path"].split("/", 1)[1]
                ref_rows_list.append(f'    <li><a href="{leaf}">{p["title"]}</a></li>')

            home_html = build_home_html(ws_title, "\n".join(lesson_rows_list), "\n".join(ref_rows_list))
            (dest / "index.html").write_text(home_html, encoding="utf-8")
            home_rel_from_root = f"{ws.name}/index.html"

        hub_rows.append({"title": ws_title, "chapters": chapter_count, "link": home_rel_from_root})

    return hub_rows


def run_checked(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True)


def publish(staging: Path, repo_name: str, commit_message: str, published_count: int) -> None:
    if not (staging / ".git").exists():
        subprocess.run(["git", "init", "-b", "main"], cwd=staging, capture_output=True, text=True, check=True)

    subprocess.run(["git", "add", "-A"], cwd=staging, capture_output=True, text=True, check=True)

    status = run_checked(["git", "status", "--porcelain"], staging).stdout
    if status.strip():
        subprocess.run(["git", "commit", "-m", commit_message], cwd=staging, capture_output=True, text=True, check=True)
        print(f"== committed: {commit_message}")
    else:
        print("== no changes to commit")

    view_result = run_checked(["gh", "repo", "view", repo_name], staging)
    if view_result.returncode != 0:
        print(f"== creating repo {repo_name} (public)")
        create_result = run_checked(
            ["gh", "repo", "create", repo_name, "--public", "--source", str(staging), "--remote", "origin", "--push"],
            staging,
        )
        if create_result.returncode != 0:
            raise RuntimeError(
                f"repo create/push failed (exit {create_result.returncode}). Check gh auth (gh auth status) and network, then re-run."
            )
    else:
        remotes = run_checked(["git", "remote"], staging).stdout.split()
        if "origin" not in remotes:
            user = run_checked(["gh", "api", "user", "--jq", ".login"], staging).stdout.strip()
            subprocess.run(
                ["git", "remote", "add", "origin", f"https://github.com/{user}/{repo_name}.git"],
                cwd=staging, capture_output=True, text=True, check=True,
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
        ["gh", "api", "-X", "POST", f"repos/{user}/{repo_name}/pages", "-f", "source[branch]=main", "-f", "source[path]=/"],
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
    parser.add_argument("--source", type=Path, default=Path.home() / ".omo" / "teach")
    parser.add_argument("--staging", type=Path, default=Path.home() / ".omo" / "pages" / "bearmancer.github.io")
    parser.add_argument("--commit", default=f"Publish teaching docs {datetime.now():%Y-%m-%d %H:%M}")
    args = parser.parse_args()

    staging: Path = args.staging
    source: Path = args.source

    staging.mkdir(parents=True, exist_ok=True)

    print(f"== staging: {staging}")
    for item in staging.iterdir():
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    published = process_workspaces(source, staging)

    (staging / ".nojekyll").touch()

    hub_rows = build_hub_rows(source, staging, published)

    rows = "\n".join(
        f'    <tr><td><a href="{h["link"]}">{h["title"]}</a></td><td>{h["chapters"]}</td></tr>'
        for h in sorted(hub_rows, key=lambda h: str(h["title"]))
    )
    top_index = build_top_index_html(rows, f"{datetime.now():%Y-%m-%d %H:%M}")
    (staging / "index.html").write_text(top_index, encoding="utf-8")

    publish(staging, args.repo_name, args.commit, len(published))


if __name__ == "__main__":
    main()

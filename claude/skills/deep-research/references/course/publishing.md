# Publishing — GitHub Pages

## Primary flow (this machine)

```
python "<skill>/scripts/publish_teach.py"
```

The script:

- reads course dirs (`<slug>/lessons/*.html`) authored in the site working copy (`~/Dev/bearmancer.github.io`),
- converts `.md` links to plain text in those pages,
- refreshes the root index page,
- commits and pushes to `Bearmancer/bearmancer.github.io` (public site: `https://bearmancer.github.io/`),
- prints the page count.

Course flow scope is fixed: **course pages only**. `.md` admin files (NOTES / RESOURCES / learning-records / transcript slices) live in `~/Dev/bearmancer.github.io/work/<slug>/`, gitignored, so they never publish.

## Single answer page (answer, verdict, recommend, rules)

```
python "<skill>/scripts/publish_teach.py" --page <body.html> --kind answer|verdict|recommend|rules --title "<title>"
```

- Body = HTML fragment, no `<html>`/`<head>`. The script wraps it in the shared layout (A-bar, kicker = kind, H1 = title, date, Home footer) with `assets/lesson.css` + `shell.js`.
- Body gate, refuses before any git call: at least one inline `https` `<a href>`; no Sources/References/Bibliography heading (citations are links in the prose, `page-design.md` "Prose rules").
- Writes `answers/<kind>-<slug>.html` in the site working copy, adds a row under "Answers" on the root index (course publishes keep answer rows), commits and pushes the Pages repo only. Same title overwrites its page.
- Probes the page URL (8 x 15 s) for HTTP 200 and the escaped title in the live bytes; prints `live: <url>`. Exit 0 only when both hold; exit 1: wait for the build with the harness monitor, then re-fetch.
- Body content per mode: answer = `SKILL.md` "Answer mode" step 3 (`--kind answer`); verdict (explicit fact-check-only, `--kind verdict`) = `SKILL.md` "Verdict mode" step 3; recommend = `recommend.md` pick blocks; rules (board-game) = `SKILL.md` "Board-game mode" page order.

## Dry run (`--no-push`)

`--no-push` builds course indexes and the root hub in the site working copy and stops before commit; `git status` there shows the file set. A normal run commits and pushes the site repo only; it prints `no changes to commit` when nothing changed, and the page count at the end tells what went out.

## Verify

One command. Never gate a bare download — a lone file false-fails the
dangling-link checks, so live verification reproduces the tree:

```powershell
python <skill>/scripts/verify_live.py ~/Dev/bearmancer.github.io/<slug> https://bearmancer.github.io/<slug>
```

It downloads lessons plus their link targets (assets, reference, index) into a
temp tree, gates every live lesson, asserts no `.md` hrefs survived (the
publisher flattens them), and byte-compares each asset. Exit 0 only when all
of that holds. The publish script already probes the root index (retries
8 x 15 s, warns on lag); per-page 200s are inside the verifier's download
step — any non-200 fails the run.

Gates apply by artifact: any SVG visual that changed (the cast map) also gets the geometry checker on its live copy; the timeline is HTML-flow, so the screenshot pass covers it when it changed. Citations are links inside the lesson HTML, so they publish with the lesson; RESOURCES stays local and never publishes.

Assets come back byte-identical to the local copies (`Get-FileHash` both sides). Pages legitimately differ from local in exactly one way — `.md` links are flattened to plain text — so expect zero `href="*.md"` live, a small size delta, and matching content otherwise; any further difference means investigate before reporting success. A `200` proves a page exists; the downloaded bytes prove the right page went out. Report the live URLs and the gate results in chat.

## Gotchas

- `warning: LF will be replaced by CRLF` in git output is harmless noise.
- A fresh page can 404 for the first ~30 s while Pages rebuilds — retry before assuming failure.
- A published page rendering unstyled points at a missing `assets/lesson.css` — confirm the site root `assets/` has it and re-run publish.
- Pages are authored as HTML directly in the course dir.
- Live pages differ from local **by design**: the `.md` links are flattened. Compare with that expectation (assets identical, pages differing only in flattened links and a small size delta); any other difference is a real problem worth chasing.

## Fallback (script missing / other machine)

1. Clone or use a `<user>.github.io` repo; copy only `*/lessons/*.html`, `*/reference/*.html`, and `*/assets/*` in the same relative layout.
2. `git add` → commit (`Publish courses <date>`) → push.
3. Ensure Pages is enabled on the default branch (repo Settings → Pages); first publish can take a few minutes.
4. Probe URLs as above.

## Report format (chat)

- Short lines: page path + live URL per new page, 200 status, headline corrections (one line each). No queued-next lines, no closing questions.

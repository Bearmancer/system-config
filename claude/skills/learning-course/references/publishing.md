# Publishing — GitHub Pages, teaching pages only

## Primary flow (this machine)

```
python "$HOME\.omo\scripts\publish_teach.py"
```

The script:

- mirrors `~/.omo/teach/*` **HTML + `assets/` only** to the site working copy (`~/.omo/pages/bearmancer.github.io`),
- converts `.md` links to plain text in the published copy (local files are untouched),
- refreshes the root index page,
- commits and pushes to `Bearmancer/bearmancer.github.io` (public site: `https://bearmancer.github.io/`),
- prints the page count.

Scope is fixed: **teaching pages only**. `.md` admin files (NOTES / RESOURCES / learning-records / transcripts) stay local; the mirror step excludes them. The transcript slices live as `.md` inside `reference/transcripts/` and stay out of the published copy the same way.

## Dry run (no flag — preview by hand)

The script ships no `--dry-run` / `-WhatIf` flag: one run mirrors, commits, and pushes. To preview the mirror selection, copy one workspace's HTML + `assets/` into a temp dir first and confirm the file set looks right; the script prints `no changes to commit` when staging matches the last push, and the page count at the end tells what went out.

## Verify

Two steps. Status codes first, then the bytes themselves:

```powershell
Start-Sleep -Seconds 10   # Pages rebuild takes a moment
curl.exe -s -o NUL -w "%{http_code}" https://bearmancer.github.io/<workspace>/lessons/<file>.html
```

Expect `200` for every newly published URL (lesson + each new reference page). The script probes the root index itself (retries 8 x 15 s, warns on lag); per-page probes stay manual. Then download what you published and run the gates against it, confirming the mirror stayed faithful:

```powershell
curl.exe -s -o "$env:TEMP\live\reference\cast-map.html" https://bearmancer.github.io/<workspace>/reference/cast-map.html
python <skill>/scripts/check_map_geometry.py --strict-labels "$env:TEMP\live\reference\cast-map.html"
python <skill>/scripts/check_lesson.py "$env:TEMP\live\lessons\<file>.html"
```

Gates apply by artifact: any SVG visual that changed (the cast map) also gets the geometry checker on its live copy; the timeline is HTML-flow, so the screenshot pass covers it when it changed. Per-chapter Sources blocks ride inside the lesson HTML, so they publish with the lesson; RESOURCES stays local (split-source retained until migration) and never publishes.

Assets come back byte-identical to the local copies (`Get-FileHash` both sides). Pages legitimately differ from local in exactly one way — `.md` links are flattened to plain text — so expect zero `href="*.md"` live, a small size delta, and matching content otherwise; any further difference means investigate before reporting success. A `200` proves a page exists; the downloaded bytes prove the right page went out. Report the live URLs and the gate results in chat.

## Gotchas

- `warning: LF will be replaced by CRLF` in git output is harmless noise.
- A fresh page can 404 for the first ~30 s while Pages rebuilds — retry before assuming failure.
- A published page rendering unstyled points at a missed `assets/` mirror — confirm the workspace has `assets/lesson.css` and re-run.
- The script mirrors HTML + assets only; author page content in HTML.
- Live pages differ from local **by design**: the `.md` links are flattened. Compare with that expectation (assets identical, pages differing only in flattened links and a small size delta); any other difference is a real problem worth chasing.

## Fallback (script missing / other machine)

1. Clone or use a `<user>.github.io` repo; copy only `*/lessons/*.html`, `*/reference/*.html`, and `*/assets/*` in the same relative layout.
2. `git add` → commit (`Publish teaching docs <date>`) → push.
3. Ensure Pages is enabled on the default branch (repo Settings → Pages); first publish can take a few minutes.
4. Probe URLs as above.

## Report format (chat)

- Short lines: page path + live URL per new page, 200 status, headline inline-verdict corrections (one line each). No queued-next lines, no closing questions.

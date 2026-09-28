# Publishing — GitHub Pages, course pages only

## Primary flow (this machine)

```
python "<skill>/scripts/publish_teach.py"
```

The script:

- mirrors `~/Dev/deep-research/*` **HTML + `assets/` only** to the site working copy (`~/Dev/bearmancer.github.io`),
- converts `.md` links to plain text in the published copy (local files are untouched),
- refreshes the root index page,
- commits and pushes to `Bearmancer/bearmancer.github.io` (public site: `https://bearmancer.github.io/`),
- prints the page count.

Scope is fixed: **course pages only**. `.md` admin files (NOTES / RESOURCES / learning-records / transcripts) stay local; the mirror step excludes them. The transcript slices live as `.md` inside `reference/transcripts/` and stay out of the published copy the same way.

## Dry run (no flag — preview by hand)

The script ships no `--dry-run` / `-WhatIf` flag: one run mirrors, commits, and pushes. To preview the mirror selection, copy one workspace's HTML + `assets/` into a temp dir first and confirm the file set looks right; the script prints `no changes to commit` when staging matches the last push, and the page count at the end tells what went out.

## Verify

One command. Never gate a bare download — a lone file false-fails the
dangling-link checks, so live verification mirrors the tree:

```powershell
python <skill>/scripts/verify_live.py <workspace-dir> https://bearmancer.github.io/<workspace>
```

It downloads lessons plus their link targets (assets, reference, index) into a
temp tree, gates every live lesson, asserts no `.md` hrefs survived (the
publisher flattens them), and byte-compares each asset. Exit 0 only when all
of that holds. The publish script already probes the root index (retries
8 x 15 s, warns on lag); per-page 200s are inside the verifier's download
step — any non-200 fails the run.

Gates apply by artifact: any SVG visual that changed (the cast map) also gets the geometry checker on its live copy; the timeline is HTML-flow, so the screenshot pass covers it when it changed. Citations ride inline inside the lesson HTML, so they publish with the lesson; RESOURCES stays local (split-source retained until migration) and never publishes.

Assets come back byte-identical to the local copies (`Get-FileHash` both sides). Pages legitimately differ from local in exactly one way — `.md` links are flattened to plain text — so expect zero `href="*.md"` live, a small size delta, and matching content otherwise; any further difference means investigate before reporting success. A `200` proves a page exists; the downloaded bytes prove the right page went out. Report the live URLs and the gate results in chat.

## Gotchas

- `warning: LF will be replaced by CRLF` in git output is harmless noise.
- A fresh page can 404 for the first ~30 s while Pages rebuilds — retry before assuming failure.
- A published page rendering unstyled points at a missed `assets/` mirror — confirm the workspace has `assets/lesson.css` and re-run.
- The script mirrors HTML + assets only; author page content in HTML.
- Live pages differ from local **by design**: the `.md` links are flattened. Compare with that expectation (assets identical, pages differing only in flattened links and a small size delta); any other difference is a real problem worth chasing.

## Fallback (script missing / other machine)

1. Clone or use a `<user>.github.io` repo; copy only `*/lessons/*.html`, `*/reference/*.html`, and `*/assets/*` in the same relative layout.
2. `git add` → commit (`Publish courses <date>`) → push.
3. Ensure Pages is enabled on the default branch (repo Settings → Pages); first publish can take a few minutes.
4. Probe URLs as above.

## Report format (chat)

- Short lines: page path + live URL per new page, 200 status, headline inline-verdict corrections (one line each). No queued-next lines, no closing questions.

# Agents-Teach Publish — Agent Instructions

Scope: teach publish ONLY. Config backup is out of scope, see `C:\Users\Lance\.omo\scripts\AGENTS.md`. Distinct repo — that separation is why this file exists.

Full behavior: `C:\Users\Lance\.omo\scripts\publish-teach.ps1` (L1-12 header, L31-55 mirror, L182-220 git+probe). Full verify gates: `C:\Users\Lance\.claude\skills\learning-course\references\publishing.md`.

## Trigger

- Run after teach task done, manual agent run only. No scheduled task.
- Never publish mid-task; workspace HTML must be final first.

## Command

```powershell
pwsh -NoProfile -File C:\Users\Lance\.omo\scripts\publish-teach.ps1
```

Requires `gh` authenticated (repo scope) and git identity configured.

## What the script does

- Mirror every workspace under `C:\Users\Lance\.omo\teach` into staging `C:\Users\Lance\.omo\pages\bearmancer.github.io`: HTML + `assets/` only.
- Strip `.md` admin (MISSION / NOTES / RESOURCES / learning-records / transcripts) from staging; locals never touched.
- Flatten `.md` links to plain text in published copies only (script L44-48).
- Write per-workspace `index.html` course home + root hub `index.html` + `.nojekyll`.
- Commit + push to `Bearmancer/bearmancer.github.io` (public). Site: `https://bearmancer.github.io/`. Print page count.

## Failures

- Push/create failures throw loud (script L195, L199). Check output; never report success on throw.
- Non-fast-forward push: run `git -C C:\Users\Lance\.omo\pages\bearmancer.github.io pull --rebase`, resolve, then re-run script.
- `gh repo create` failure: run `gh auth status`, fix auth/network, re-run.

## Verify

- Root index self-probe: script retries 8 x 15 s, warns on lag (L213-219). Warning means Pages build lagging, not failure.
- Per-page 200 probes stay manual: `curl.exe -s -o NUL -w '%{http_code}' https://bearmancer.github.io/<workspace>/lessons/<file>.html`.
- Live-bytes gate: download published copy, run `C:\Users\Lance\.claude\skills\learning-course\scripts\check_lesson.py` and (for cast-map SVG) `check_map_geometry.py --strict-labels`. Assets byte-identical; pages differ only by flattened `.md` links.

## Do not break

- This dir holds content workspaces. Discovery uses `Get-ChildItem -Directory`; keep this file a file, never a directory.
- Never edit workspace content files for publish reasons. Non-HTML outside `assets/` is stripped from staging by design (script L40).

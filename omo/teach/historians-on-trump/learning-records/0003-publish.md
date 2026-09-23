# 0003 — Publish: final gates + Pages push + live verification (2026-09-21)

## Gates (local)

- check_lesson.py exit 0 on all 8 lessons (01-ch1 through 08-ch8).
- check_map_geometry.py --strict-labels exit 0 on cast-map, glossary, timeline (0-defect flow pages, no SVG visuals — screenshot pass N/A).

## Publish

- Dry-run: copied workspace HTML + assets to $env:TEMP\dryrun-hist, confirmed file set (8 lessons, 3 reference, index, assets); removed temp dir after.
- Ran `python $HOME\.omo\scripts\publish_teach.py` → commit "Publish teaching docs 2026-09-21 04:04", pages published: 66. Script self-probed root index 200.
- No content edits, no YAML restamps.

## Live verification

- All 12 URLs probed 200 first pass (no rebuild-lag retry needed): 8 lessons + cast-map + glossary + timeline + workspace index.
- Downloaded live bytes to $env:TEMP\live; re-ran check_lesson.py (8/8 exit 0) and check_map_geometry.py (3/3 exit 0, 0-defect).
- Live pages carry zero `href="*.md"` (flattened by design); size delta small vs local as expected.
- Assets byte-identical: lesson.css SHA256 4F52398652795DA4F057EAF029955AF47DC3B8A0F048F28FAA3A637AF27C7FF3 local = live.

## Auto-open

- Start-Process: lessons/08-ch8-annex-method.html, reference/cast-map.html, reference/glossary.html, reference/timeline.html.

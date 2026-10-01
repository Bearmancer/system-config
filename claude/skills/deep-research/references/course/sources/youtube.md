# Source adapter — YouTube (and other chaptered video)

The course engine is source-agnostic (see `references/modes/course.md`); this adapter covers everything YouTube-specific: fetching, slicing, description mining, caption quirks, and the corrections that auto-captions need. YouTube/transcript slices stay secondary unless user explicitly names video as course source; every chapter needs >= 1 non-YouTube primary.

## Fetch metadata + captions

```
python <skill>/scripts/fetch_video.py "<video-url>"
```

Writes into a **persistent cache** (default `~/.cache/deep-research/video/<id>/`):

- `info.json` — title, duration, **description**, `chapters[]`, url.
- `subs.en.vtt` — English captions (manual if available, else auto-generated).

The cache is persistent on purpose: slicing is metadata-driven and gets re-run constantly, and a persistent cache keeps every re-run a cache hit. When both files are already there the fetch is skipped entirely; `--force` refreshes them. On first use the script also adopts a copy left in the older temp locations, so switching costs no re-download.

Requirements: `yt-dlp` on PATH. The `[youtube] No supported JavaScript runtime` warning is cosmetic — downloads still work. Captions missing means saying so plainly: quotes ground in the transcript, and teaching from title/thumbnail alone counts as fabrication.

## Chapters

`chapters[]` is creator-side metadata. Cross-check it against the description's own chapter list — the two drift, and the description sometimes carries a newer list. The user's deep-link timestamp marks their **watch position**; chapter boundaries come from the source metadata. If the video has no chapter markers, stop and tell the user; ask how they want to segment (a missing chapter list is unusual for their videos and worth surfacing).

## Extract chapters (the default quick path)

```
python <skill>/scripts/extract_chapters.py "<video-url-or-id>" \
  --out <workspace>/reference/transcripts --chapters all --title
```

One command does the whole extraction job, and the ranges stay metadata-derived: they are read out of `info.json`, which is the video's own metadata. So ranges persist across chapters with no recompute — a chapter range that was correct yesterday is still correct today, and a re-run costs a cache hit.

- `--chapters` takes `all` (default), `8`, `8-18`, `3,5,7`, or a title substring (`--chapters sobchak`); `--list` prints the table, `--dry-run` reports without writing. Prefer `--chapters all`; narrow the spec only for a re-run or a targeted pass.
- Files are named the way this workspace already names them: `<slug>-<startHhMmSs>-<endHhMmSs>.md` (e.g. `sobchak-1h04m57s-1h12m03s.md`), so re-running into an existing workspace overwrites in place.
- The boundary check prints per chapter (last cue before the range, first cue after it). Captions lag the visual cut by ~4–6 s, so verify the "first after" cue opens the next chapter and note the lag in the slice header — that note is the honesty of the slice.
- `slice_chapter.py` covers hand-range overrides only: a chapter boundary the metadata gets wrong and a human re-derives by hand. `extract_chapters.py` shares its collapse implementation (one implementation, imported — see the script header), so both paths collapse rolling-caption duplication the same way.

Batch extraction is safe here because the ranges come from metadata; it is _teaching_ that stays one chapter at a time (every chapter still gets its own treatise page).

## Description mining (mandatory)

The description is where creators put their citations, sources, corrections, and chapter lists. Read it every time, before verification:

- Extract every link/source it cites into inline citations (annotated hyperlink to the actual page, no bare URLs — `references/course/page-design.md`) and treat them as the **first** verification targets — what the creator leaned on is the fastest route to the record.
- Watch for errata ("correction:", pinned notes, "edit:"): those override the spoken claim; fold the correction into the sentence beside the quoted wording, linking both claim and erratum on the words naming them.
- Sponsors and advocacy: label them as such inline so the course keeps promotional framing visible as promotion.
- The description's chapter list is also a second witness for `chapters[]`.

## Machine-caption correction (mandatory pass — `references/modes/course.md` Step 3)

Auto-captions garble proper nouns ("Yeager" for Yager, "Sobcheck" for Sobchak), numbers, and technical terms. The pass:

1. Build the candidate list: names/terms from the title, description, chapter titles, prior glossary, and domain knowledge.
2. Fix the evident garbles in the slice; log each in the slice's corrections table as `heard -> corrected -> basis`; canonical spellings go to the glossary.
3. Ambiguous garble: keep the original, flag it inline (e.g. `[unclear: "Sobcheck"?]`) — every guess goes on record with its basis.
4. Quote a caption line in a lesson only after it passes this pass.
5. Numbers (dates, sums, counts) are the highest-risk class: any number that reaches a treatise carries a second witness (the video's own visuals/description, or an outside source) beside it.

The corrections table lives in the slice header, so every future session sees what the machine got wrong and why the canonical form is the canonical form.

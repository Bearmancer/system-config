# NOTES — Watergate: A Geographic History

## Chapter map (from info.json chapters[] + description, cross-checked — match)

| # | Time | Chapter | Essential? | In last-90? |
|---|------|---------|------------|-------------|
| 1 | 00:00–10:44 | The Geographic Story | yes | no |
| 2 | 10:44–22:00 | Watergate | yes | no |
| 3 | 22:00–34:37 | Richard Nixon | yes | no |
| 4 | 34:37–48:24 | Vietnam | yes | partial (41:16 cut = mid-chapter) |
| 5 | 48:24–1:06:33 | The Roots of Watergate | yes | yes |
| 6 | 1:06:33–1:21:41 | The Plumbers | yes | yes |
| 7 | 1:21:41–1:32:07 | The Cover-Up | yes | yes |
| 8 | 1:32:07–1:42:48 | The Tapes | yes | yes |
| 9 | 1:42:48–1:55:01 | The Scandal | yes | yes |
| 10 | 1:55:01–2:01:19 | Resignation | yes | yes |
| 11 | 2:01:19–2:08:47 | The Aftermath | yes | yes |
| 12 | 2:08:47–2:11:16 | Conclusion | skippable | yes |

Last-90 cut: 2:11:16 minus 90 min = 41:16, mid-ch4. Clean-chapter block = ch5–ch12.

## Extraction recipe

```
python C:\Users\Lance\.claude\skills\learning-course\scripts\fetch_video.py "https://youtube.com/watch?v=GUmLe8YtIck"
python scripts/extract_chapters.py "https://www.youtube.com/watch?v=GUmLe8YtIck" --out ~/.omo/teach/watergate-geographic-history/reference/transcripts --chapters all --title
```

Cache: ~/.omo/cache/learning-course/GUmLe8YtIck/ (info.json + subs.en.vtt). Boundary lag ~4-6s captions behind visual cut (see slice headers).

## Corrections log

- 2026-09-20 ch7 The Cover-Up slice: Chinult→Chennault, Halddederman→Haldeman, Erlickman→Ehrlichman, Litty→Liddy, Graph→Graff, Ablinalp→Abplanalp, Biscane→Biscayne, Caracus→Caracas, Jay Edgar→J. Edgar, Vietkong→Viet Cong, consiliatory→conciliatory; unresolvable: Cambodia voice-over unit name before Parrot's Beak. Numbers second-witnessed: Kent State 4 incl. Miller 20, 18:30 gap June 20, Huston Plan to chiefs June 25 1970, smoking gun June 23, Brookings order June 17 1971, Caracas May 13 1958, Lincoln visit May 9 1970. Unverified: Memorial–Watergate 2,000 ft; Oct 1971 Helms excerpt; June 19 hush-money wording; June 17–18 whereabouts contested (memoirs vs Graff). Lesson: lessons/03-ch7-the-cover-up.html, check_lesson OK, geometry OK zero warnings.
- 2026-09-20 ch8 The Tapes slice: adviserss → advisers; aids → aides (people); benal → banal; plate congressional → placate (context: offered transcripts to investigators); Jorski → Jaworski; Archimold Cox → Archibald Cox; white white house → White House. Numbers second-witnessed: first reel Feb 16 1971, run to July 1973, erased stretch eighteen and one half minutes, March cancer reel dated March 21 1973, Butterfield closed July 13 plus public July 16 (taping ends with public disclosure, not the closed session). Lesson: lessons/04-ch8-the-tapes.html, check_lesson OK, geometry OK strict.
- Pending per-slice pass (Step 3). Candidates: Watergate names (Haldeman, Ehrlichman, Mitchell, Dean, Woodward/Bernstein), places (Chennault, Ellsberg).
- Numbers need second witness before treatise.

## Quirks

- Description carries apparatus: Graff, Hughes, Nixon memoirs, Nixon Library primaries. Scholarly gate applies — quote + cite apparatus, targeted checks only.
- Sponsor: Ground News (label advocacy/promo in RESOURCES).

## Queue & status

- 2026-09-20: workspace created, all 12 slices extracted. Position: Lesson 04 ch8 The Tapes done (verified headline: system dates plus gap plus disclosure dates confirmed against Nixon Library and NARA; gap theory taught as interpretation).

- 2026-09-21 stencil migration (skill update): all 8 lessons ch5-12 restamped YAML->HTML via stamp_lesson.py; record-box/open-threads folded to inline verdicts + Sources block. check_lesson 8/8 OK, geometry 8/8 OK (ch6 one label-on-line warning, pre-existing class), remnants scan zero. Pilot (ch5/ch10/ch12) ~1-7 min/lesson first-pass green; Wave-1 (ch6-9/ch11) same. ch6 worker timed out with zero assistant messages but YAML+HTML complete on disk; adopted after idempotent restamp + gates. Published publish_teach.py (66 pages), live 12/12 200, live gates OK, assets hash identical.

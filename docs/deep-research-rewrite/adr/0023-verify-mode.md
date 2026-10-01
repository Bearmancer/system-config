# Verify mode decisions

- Inputs: pasted text, URL, PDF, video or audio. Video/audio via yt-dlp transcript, or direct audio/video read by deepseek-v4.1 (ADR 0013).
- The extractor splits the input into atomic factual claims, attributes each to the speaker or passage by locator (page, paragraph, timestamp), and dedups. Opinions, predictions and value judgments are not claims; the page header reports how many were skipped.
- Every factual claim goes through the full loop; no sampling.
- Output: one page of claim cards for `untrue` and `interpretive` only, each with sources and its locator in the input. Header: counts of claims checked, true (not listed), untrue, interpretive, not-found. `not-found` claims and failed sources appear in the appendix.
- Published at `answers/verify-<slug>-<date>.html`, `noindex`, unlinked from the home index (ADR 0012).

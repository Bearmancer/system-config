# Ledger layout, IDs, open state, quotes

- Files per topic: `claims.yaml`, `sources.yaml` (readable diffs) and `attempts.jsonl` (append-only, from `log_attempt`). Schema versioned (`schema: 1`).
- Claim id sequential (`c042`), stable across edits; separate content hash (normalised text) for cross-topic matching.
- `open` is a working state, not a fifth status. Allowed during a run; any `open` at publish time fails the gate.
- Evidence entry = source id, locator (page, section, paragraph or timestamp; required), quote (25 words or fewer), stance (supports or contradicts). No locator, no evidence.
- Sketch:
  claims: id, text, hash, status, origin (discovered | misconception | extracted-from-input | extracted-from-prose), rounds, paradigms_tried, evidence[], positions[] (interpretive), tags (visual-read), anchors[].
  sources: id, url, tier (T1-T3), publisher, cites, language, retrieved_at, content_hash, raw_path, status (read | failed), fail_reason.

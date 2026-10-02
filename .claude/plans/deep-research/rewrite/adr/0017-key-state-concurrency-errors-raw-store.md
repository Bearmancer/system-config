# Key state, rotation lock, error classes, raw store

- Exhausted keys are remembered: per-key `exhausted_at` (fingerprint, never the key) stored beside the registry; skipped until the vendor's reset window; probed once on resume. Unknown reset window = probe after 24h.
- Rotation lock: the first agent to hit credit-out rotates; others wait for the watcher reconnect, then retry once. One rotation per exhaustion event.
- Unknown error: retry once, log `unknown`; rotate only after the same unknown failure hits 2 different URLs. Registry error cells are promoted to verified as codes are observed.
- Early terminate: when one MCP's whole key pool (8-9 keys) is exhausted, the run saves state, stops, and asks the user.
- Raw fetched content lives in a gitignored `work/` dir per topic. The ledger keeps URL, retrieved_at, content hash, locator and a short quote. Source text is never published.

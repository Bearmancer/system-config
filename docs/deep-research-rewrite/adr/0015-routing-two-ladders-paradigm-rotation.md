# Routing: two ladders, paradigm-first rotation, logged and audited

- Discovery ladder (find sources) rotates per round per claim. Fetch ladder (read a URL) escalates per URL on block, cheap to expensive. Both write to the same coverage record.
- Rotation unit = retrieval paradigm (keyword search, semantic search, answer/agent engines, crawl/map, structured extraction, browser/unlocker, scholarly/archive APIs), then vendor. MCP to CLI to POST fallback inside one server never counts as a new surface.
- Agent calls a `log_attempt` script per attempt (url, surface, paradigm, route, status). The gate audits the log against the ledger and fails any true/not-found claim whose log breaks rotation or round rules.
- Routing table = YAML registry (server, capability, paradigm, cost, MCP/CLI/POST routes, error codes); markdown generated; tool names validated by direct tools/list probe.

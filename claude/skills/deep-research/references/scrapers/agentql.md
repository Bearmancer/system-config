# AgentQL

Pick: query-shaped extraction (`{ products[] { name price(integer) } }`) from a rendered page; chain step 6. No search, crawl, map, research.

- MCP (readme; server exits at start without key): `extract-web-data`.
- CLI: none usable (`agentql-cli` only scaffolds SDK projects).
- POST (base `https://api.agentql.com/v1`, preset `vendor_request.py agentql`): `POST /query-data` `{"query":"{ products[] { product_name product_price(integer) } }","url":U}` (needs `query` or `prompt`, and `url` or `html`). Also `POST /query-document` (files), `POST /tetra/sessions` (remote browser CDP): out of scope.

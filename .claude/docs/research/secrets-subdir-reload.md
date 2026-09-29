# Key rotation through `~/.config/opencode/secrets/` (live test)

Question: when `switch_api_key.py` replaces a key file inside the `secrets/` subdirectory of the global OpenCode config dir, does a running OpenCode v2.0.18 reconnect the MCP server with the new key, without a restart or `opencode reload`? The earlier test (`file-key-hot-reload.md`) covered only a key file directly in the global config dir, and only local stdio servers.

## Setup

- OpenCode v2.0.18, fully isolated: HOME, USERPROFILE, XDG_CONFIG/DATA/CACHE/STATE_HOME and OPENCODE_DB all pointed at a temp dir. The live config and running service were never touched.
- `opencode serve --hostname 127.0.0.1 --port 47831`.
- One remote MCP server pointing at a local Python stub HTTP MCP that logs the `Authorization` header of every request.
- Header: `Authorization: Bearer {file:~/.config/opencode/secrets/stub}` (tilde form, `secrets/` subdirectory).
- Fake keys only. The replacement used `tempfile.mkstemp` in the same dir plus `os.replace`, the same as `write_secret` in `switch_api_key.py`.

## Result: reconnect works

```
[  7.838s] STUB initialize Authorization='Bearer KEY-ONE-fake'
[  7.850s] STUB tools/list Authorization='Bearer KEY-ONE-fake'
[  9.890s] REPLACE secrets/stub with KEY-TWO via tempfile+os.replace
[ 10.175s] STUB initialize Authorization='Bearer KEY-TWO-fake'
[ 10.181s] STUB tools/list Authorization='Bearer KEY-TWO-fake'
[ 10.195s] VERDICT RECONNECT OK: key2 seen 0.30s after replace, no restart
```

The watcher covers the `secrets/` subdirectory. A `{file:~/...}` path in a remote `headers` value is re-resolved, and an atomic rename triggers the reload. Together with `file-key-hot-reload.md` (the `environment` form for local servers), both server shapes in the live config rotate without a restart.

## OmO differs

OmO (senpi) reads `bearerTokenEnv` and stdio env from its own process environment snapshot (senpi `packages/coding-agent/src/core/extensions/builtin/mcp/transport.ts:226`, `:121`). A User-scope env var written by the key script is not seen until OmO restarts, and `/mcp reconnect` re-reads the same snapshot.

## Unverified

- Real remote endpoints (Exa, Tavily, Firecrawl, Apify) were not exercised; the stub stands in for them.
- The timing (0.30 s) is one run on one machine.

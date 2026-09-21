---
name: wiki
description: LLM Wiki — persistent markdown knowledge base that compounds across sessions (Karpathy model)
triggers: ["wiki", "wiki this", "wiki add", "wiki lint", "wiki query"]
---
# Wiki

Persistent, self-maintained markdown knowledge base for project and session knowledge. Inspired by Karpathy's LLM Wiki concept.

## Operations

### Ingest
Process knowledge into wiki pages. One ingest can touch many pages.

```
wiki_ingest({ title: "Auth Architecture", content: "...", tags: ["auth", "architecture"], category: "architecture" })
```

### Query
Search all wiki pages by keywords and tags. Returns matching pages with snippets — YOU (the LLM) make answers with citations from results.

```
wiki_query({ query: "authentication", tags: ["auth"], category: "architecture" })
```

### Lint
Run health checks on wiki. Find orphan pages, stale content, broken cross-references, big pages, and structure contradictions.

```
wiki_lint()
```

### Quick Add
Add one page fast (simpler than ingest).

```
wiki_add({ title: "Page Title", content: "...", tags: ["tag1"], category: "decision" })
```

### List / Read / Delete
```
wiki_list()           # Show all pages (reads index.md)
wiki_read({ page: "auth-architecture" })  # Read specific page
wiki_delete({ page: "outdated-page" })    # Delete a page
```

### Log
See wiki operation history by reading `.omc/wiki/log.md`.

## Categories
Pages sorted by category: `architecture`, `decision`, `pattern`, `debugging`, `environment`, `session-log`

## Storage
- Pages: `.omc/wiki/*.md` (markdown with YAML frontmatter)
- Index: `.omc/wiki/index.md` (auto-kept catalog)
- Log: `.omc/wiki/log.md` (append-only operation history)

## Cross-References
Use `[[page-name]]` wiki-link syntax to link pages together.

## Auto-Capture
When session ends, big discoveries get auto-saved as session-log pages. Set via `wiki.autoCapture` in `.omc-config.json` (on by default).

## Hard Constraints
- NO vector embeddings — query uses keyword + tag match only
- Wiki pages git-ignored by default (`.omc/wiki/` stays local to project)

## Orchestration

Wiki tools run where knowledge born. In orchestrating session, ingest pass for a body of work belongs to worker that own that work — it hold the context being captured — and periodic `wiki_lint()` pass is own subagent task, so health findings stay separate from authoring context. Context that just wrote ten pages is wrong one to certify them.

## Model Routing

- `haiku` — quick lookups, light inspection, narrow docs work
- `sonnet` — standard build, debug, and review
- `opus` — architecture, deep analysis, consensus planning, high-risk review
- `fable` — Claude Fable 5 (above Opus); pass it direct on Task call or pin per agent with `agents.<name>.model`
- Session model chosen with `/model` apply to main loop only. Delegated agents run on their pinned tier unless Task call passes `model` direct or agent overridden via `agents.<name>.model`. To run delegated work on Fable, use one of those two paths; picking Fable in `/model` alone no change delegation.
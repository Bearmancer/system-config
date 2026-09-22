# Learnings — lsp-fresh-audit-fix

Conventions, patterns, and successful approaches discovered during work on this plan.

_Auto-scaffolded by /start-work. Append new entries below - never overwrite._

---

- 2026-09-22 task-6: csharp-ls cold-start needs warmup — first diagnostics call timed out at 3s, retry answered clean. Always retry once before judging.
- 2026-09-22 task-6: razor/roslyn is separate builtin id from csharp; map both, never conflate.

# Model roles across four families

Allowed models per the user (2026-10-01): mimo-v2.6-flash (free), deepseek-v4.1 (audio + video input), muse-1.3 (free), qwen-3.8-flash. system-config `opencode/opencode.jsonc` still lists qwen3.7-plus; it needs updating by the user.

Proposed roles (confirm vision and context limits at build time):
- Author: muse-1.3 (free, default model).
- Extractor (tool-less, high volume): mimo-v2.6-flash (free).
- Verifier (every claim, all statuses): qwen-3.8-flash, other family than author.
- Video/audio ingest and first visual read: deepseek-v4.1. No layout judge.
- Visual-read second read: deepseek-v4.1 plus a second vision-capable family, if one exists. If none exists, the ADR 0012 fallback applies.
Rule: no checking role shares a family with the author.

# shell-gotchas — agent notes

Single-file skill. `SKILL.md` is the source of truth; no build, tests, or manifests here.

- Do not rename the skill or its trigger description. Invocation depends on it.
- Keep bullets repo-agnostic: name the shell behavior, not one repo's paths. Put repo-specific proof in the bullet, not the rule.
- Verify by running the real command, never by simulating it. Quoting bugs only show live.
- Do not add docs, examples dirs, or tests here unless asked.

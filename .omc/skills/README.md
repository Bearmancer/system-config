# Project Skills

Reusable capabilities sedimented by this project: specialized tools, prompt templates, specialized practices.
One skill per file `.omc/skills/<name>.md`, frontmatter must contain a stable ASCII `id` plus name + description +
**non-empty triggers** (loader validation hard requirement: missing or empty means the skill is never loaded):

```markdown
---
id: project-release-check
name: project-release-check
description: Apply this repository's release readiness rules
triggers:
  - "project release check"
---

# Project Release Check

Follow the repository-specific release checklist and report evidence.
```
The literal YAML keys `id`, `name`, `description`, and `triggers` never localize. `id` and other machine-semantic values stay ASCII and stable; the scalar display values for `name`, `description`, and `triggers`, plus Markdown headings and prose, may localize. A non-Latin display name remains loadable because the explicit ASCII `id` is stable.
Bar for admission matches skillify: if it can be Googled in 5 minutes it is not a skill;
write "this project's specific decision discipline", not generic tutorials.

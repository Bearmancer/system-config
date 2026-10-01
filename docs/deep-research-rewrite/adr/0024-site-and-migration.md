# Site shell, URLs, layout of repo, migration

- Shell: reuse existing `assets/lesson.css`, `shell.js`, `course-index.js` (topic and chapter selects, font and size picker) as the base; rebuilt as components for the 12 layouts; theme toggle added.
- Live URLs stay stable. New runs overwrite the same paths when a fixture regenerates a domain.
- Repo `bearmancer.github.io` holds built pages at published paths and, per topic, `_ledger/<topic>/` (claims.yaml, sources.yaml, attempts.jsonl, runs/). `work/` is gitignored. The ledger is public; it holds only URLs, locators and quotes of 25 words or fewer.
- Home index is generated from topic directories at publish time: Courses (learn) and Rules; verify pages are not listed.
- Concurrent runs: one run per topic; different topics may run in parallel; publish is serialized by a lock with `git pull --rebase` before the fast-forward. The index is regenerated, so it never conflicts.
- Old `deep-research` repo is archived (read-only) after all three fixtures migrate. Its NOTES, RESOURCES and learning-records stay readable there.

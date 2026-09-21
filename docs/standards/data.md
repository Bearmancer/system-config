# Data Standards

## What gets backed up
- Whitelist-only: a path is backed up if and only if `scripts/sync_agents_config.py` names it explicitly. Why: config-adjacent directories often contain caches, session transcripts, or reinstallable state that would bloat the repo and leak machine-specific noise if backed up by default.

## What never gets backed up
- Secrets, in any form (API keys, tokens, credentials): confirmed absent from the sync script by direct read. Why: this repo is infrastructure (private today, but not designed as a secret store) — secret provisioning is deliberately a separate concern (see CONTEXT.md: secret provisioning).

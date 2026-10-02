# Data Standards

Checkable rules, each with its why.

## Secrets

- Credential files (`.env`, `auth.json`, `service.json`, key files under `secrets/`) are never mirrored into this repo. Each one is listed under the README's reinstall section instead. (Why: this repo is pushed to GitHub on every backup.)

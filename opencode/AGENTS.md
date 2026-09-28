# Global rules

## Python package management — uv only, never pip
- Never invoke `pip`, `pip3`, or `python -m pip` for install, upgrade, or uninstall. Always use `uv`.
- One-off scripts: `uv run --with <pkg> script.py` (no manual venv, no global installs).
- Project work: `uv venv` in the project, then `uv pip install` inside that venv. Never `--user`, `--system`, or global site-packages.
- Standalone CLIs: `uv tool install <pkg>`, never pipx or pip-global installs.
- Pre-existing pip-installed packages: remove by deleting their site-packages directory/dist-info (never by running pip); verify the import is gone on bare `python` and present via `uv run --with`.

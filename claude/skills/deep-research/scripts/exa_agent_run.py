# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Exa agent run stop and cancel. Create and poll runs with MCP `agent_run`.

Docs: https://exa.ai/docs/exa-spec.yaml (`/agent/runs/{id}/stop`, `/agent/runs/{id}/cancel`)
stop: ends an `ultra` run early, keeps results so far. cancel: drops a queued or running run, no results. Both bill accrued usage.
Usage: uv run exa_agent_run.py stop|cancel <run_id>
"""
import argparse

import _post_common as pc


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    pc.add_id_commands(
        ap.add_subparsers(dest="cmd", required=True),
        {"stop": ("POST", "/agent/runs/{id}/stop"), "cancel": ("POST", "/agent/runs/{id}/cancel")},
    )
    pc.dispatch("exa", ap.parse_args(argv))


if __name__ == "__main__":
    main()

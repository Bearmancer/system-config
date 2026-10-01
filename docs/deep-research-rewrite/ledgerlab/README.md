# ledgerlab (working name)

Draft rewrite of `deep-research`. Design record: `docs/deep-research-rewrite/`. Agents load `SKILL.md`, not this file.

## Where this lives, and why

It sits under `docs/` on purpose. The daily backup mirrors `~/.claude/skills` into `claude/skills/` with `/MIR`, so a skill that exists only in the repo is deleted at the next backup. To activate it, copy this folder to `~/.claude/skills/ledgerlab` on the live machine (the backup then mirrors it back).

## What is built

| Piece | File | Tested |
|---|---|---|
| Routing registry (surfaces, paradigms, rounds, fetch ladder, error codes) | `registry/registry.yaml`, `scripts/registry.py` | yes |
| Generated routing table | `scripts/gen_routing_table.py` -> `references/routing.md` | drift test |
| Ledger schema + invariants + rotation audit + conformance | `schema/`, `scripts/ledger.py`, `scripts/ledger_check.py` | yes, incl. seeded bad claim |
| Attempt log | `scripts/log_attempt.py` | yes |
| Mode inference | `scripts/infer_mode.py` | yes |
| Key memory + rotation lock | `scripts/keystate.py` | yes |
| Driver: phases, run.yaml, suspend/resume, failure report, waves | `scripts/driver.py`, `scripts/ledgerlab.py` | yes |
| Model roles | `registry/roles.yaml` | family rule tested |

## Not built

- Agent handlers for ingest, discover, extract, verify, write, conformance, layout, publish, live_check. The CLI fails honestly at the first one.
- Shared site shell and layout components; home index generator.
- Real `opencode run` flags (unverified), `tools/list` surface probe, URL audit port.
- Voice rule (needs the user's samples).
- Fixture runs: rules (Ark Nova), verify (Russia morale), learn (Saudi military). These need the OpenCode host, keys and models.

## Run the tests

```
pip install pytest pyyaml jsonschema
python -m pytest docs/deep-research-rewrite/ledgerlab/tests -q
```

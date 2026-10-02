# ledgerlab (working name)

Draft rewrite of `deep-research`. Agents load `SKILL.md`, not this file. Design record (glossary, ADRs 0001-0024, layout atlas, handoff): Bearmancer/system-config, `.claude/plans/deep-research/rewrite/`.

This folder is not an installed skill. Activation (copying to `~/.claude/skills/ledgerlab`) waits for the user and is described in the handoff.

## What is built

| Piece | File | Tested |
|---|---|---|
| Routing registry (surfaces, paradigms, rounds, fetch ladder, error codes) | `registry/registry.yaml`, `scripts/registry.py` | yes |
| Generated routing table | `scripts/gen_routing_table.py` -> `references/routing.md` | drift test |
| Ledger schema, status invariants, visual-read family rule, rotation and round audit against the attempt log, conformance | `schema/`, `scripts/ledger.py`, `scripts/ledger_check.py` | yes, incl. seeded bad claim |
| Attempt log | `scripts/log_attempt.py` | yes |
| Mode inference | `scripts/infer_mode.py` | yes |
| Key memory, OS-level rotation lock, one-rotation-per-event generation counter, unknown-failure counter | `scripts/keystate.py` | yes, incl. concurrent agents |
| Driver: phases (including `render`), run.yaml, suspend/resume, failure report, waves with a shared deadline | `scripts/driver.py`, `scripts/cli.py` | yes |
| Model roles and model-family map | `registry/roles.yaml`, `registry.load_roles` | family rule tested; model ids unverified |

## Not built

- Agent handlers for ingest, discover, extract, verify, write, conformance, layout, render, publish, live_check. The CLI fails honestly at the first one.
- Shared site shell and layout components; home index generator.
- `tools/list` surface probe, URL audit port, POST scripts named in the registry (they live in the old `deep-research` skill).
- Fixture runs: rules (Ark Nova), verify (Russia morale), learn (Saudi military). These need the OpenCode host, keys and models.

## Run

Scripts form the `scripts` package; run them from this folder:

```
uv run --with pyyaml --with jsonschema python -m scripts.cli start --site-root <abs path> --topic <slug> "<prompt>"
```

## Run the tests

From the repository root:

```
uv run --with pytest --with pyyaml --with jsonschema pytest ledgerlab/tests --basetemp <empty temp dir>
```

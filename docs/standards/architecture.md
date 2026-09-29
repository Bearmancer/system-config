# Architecture Standards

Checkable rules, each with its why. An empty section means no rule has been settled yet; launch's C5 sediment pass fills it.

## Module boundaries

- Every script in this repo reads local state and writes to this repo or a remote. It never writes back into `~/.claude`, `~/.config/opencode` or `~/.omo`. (Why: restore is a deliberate manual reverse copy, so a bug here cannot corrupt live config.) The rule covers this repo's scripts only: the deep-research skill's `switch_api_key.py` lives in `~/.claude/skills` and writes the active key files to `~/.config/opencode/secrets/<svc>` by design.

- Shared logic lives in `SystemConfig.psm1`; the root entry points (`install.ps1`, `run-sync.ps1`, `backup-agents.ps1`) import it and stay a few lines long, and `scripts/` holds tests. (Why: one module keeps every task and test calling the same code.)

## Error handling

- Each Daily sync step reports failure by name and never stops the steps after it. (Why: one broken service must not skip the backup.)

## Dependency direction

## Seams and depth

- A seam is a real boundary that two modules already cross in both directions. One adapter makes a hypothetical seam; two adapters make it real. (Checkable: count the callers. Why: speculative abstraction is a tax paid before the need exists.)
- A deep module puts much behavior behind a small interface. Deepen a module before widening its interface. (Why: the interface is the permanent tax.)

# Architecture Standards

Checkable rules, each with its why. An empty section means no rule has been settled yet; launch's C5 sediment pass fills it.

## Module boundaries

- Every script in this repo reads local state and writes to this repo or a remote. It never writes back into `~/.claude`, `~/.config/opencode` or `~/.omo`. (Why: restore is a deliberate manual reverse copy, so a bug here cannot corrupt live config.)

## Error handling

- Each Daily sync step reports failure by name and never stops the steps after it. (Why: one broken service must not skip the backup.)

## Dependency direction

## Seams and depth

- A seam is a real boundary that two modules already cross in both directions. One adapter makes a hypothetical seam; two adapters make it real. (Checkable: count the callers. Why: speculative abstraction is a tax paid before the need exists.)
- A deep module puts much behavior behind a small interface. Deepen a module before widening its interface. (Why: the interface is the permanent tax.)

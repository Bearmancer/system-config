# Status invariants, independence, compound sentences, tooling

- `ledger check` enforces: true = truth bar met and no credible contradiction; untrue = contradicting evidence meets the bar and no credible support; interpretive = at least 2 positions, each with a T1/T2 source; not-found = 5 rounds done with no qualifying evidence either way; visual-read adds the two-read rule.
- Independence of sources is decided by the verifier agent, which records a one-line rationale in the evidence entry. Publisher and cites are still recorded for audit. (User chose agent judgement over a scripted rule.)
- A lesson sentence is publishable only if every mapped claim is true, or is labelled interpretive in a debate block.
- Enforcement: JSON Schema + Python `ledger check` + pytest fixtures including a seeded bad claim. The same check runs in the gate and in tests.

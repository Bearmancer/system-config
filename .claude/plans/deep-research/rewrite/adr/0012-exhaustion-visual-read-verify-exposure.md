# Key exhaustion, visual reads, verify-page exposure

- Keys rotate automatically. If one MCP exhausts its whole key pool (8-9 keys), the run terminates early, saves the ledger, and asks the user. This is the single permitted question in a run.
- Claims from images or scans carry `visual-read`; `true` needs reads from two distinct model families. Families are counted through the model-to-family map in `registry/roles.yaml`, so two reads by one family (or two ids of one family) count once.
- Alternative path, and the only one while a single vision model family is available: one visual read plus text corroboration. The ledger check accepts it whenever a read and a text corroboration are both recorded; a corroboration without any visual read fails.
- Verify pages are published to the public site with `noindex`, unlinked from the home index. The repo is public, so this reduces discovery only; it is not privacy.
- Publishing reproduces no copyrighted text beyond short attributed quotes; research may use everything fetched.
- Verifier re-checks every claim, all statuses (no sampling).

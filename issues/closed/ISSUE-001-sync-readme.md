# ISSUE-001: Sync README with current workflow contracts

- Priority: medium
- Type: documentation
- Status: closed

## Problem

`README.md` does not yet mention `workflow-invariants.md`, public CSV outputs,
actual LHCO event-count handling, event-count recovery, or the single selection
strategy invariant.

## Risk

Cross-agent users may read README first and miss current controlling rules.

## Candidate Fix

Update README after the script/manifest contracts are stable enough to describe
without changing them again immediately. In practice, wait until the MG5 config
runner, LHCO count helper, LHCO merge helper, and manifest-driven audit schema
are specified or implemented.

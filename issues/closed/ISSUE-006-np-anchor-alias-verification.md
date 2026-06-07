# ISSUE-006: Make `np_anchor` alias verification deterministic

- Priority: medium
- Type: script/spec candidate
- Status: closed

## Problem

Phase 5 says `np_anchor` must match the anchor operator's
`np_o_{anchor_global_idx}` sample, but does not define verification.

## Risk

Agents may accidentally duplicate, mismatch, or overwrite the anchor alias.

## Candidate Fix

- record `alias_for` in Phase 5 metadata
- record the anchor source path and alias output path
- verify the alias resolves to the same physical sample as the selected anchor
  operator sample, either by copying from the anchor sample or by recording an
  explicit alias relationship in metadata
- verify the aliased LHCO is parseable and non-empty using the LHCO count helper
- prefer copying from the selected anchor sample rather than launching a second
  anchor run

## Script Relation

This should not become a separate helper. Empty or malformed LHCO detection
belongs in the LHCO count helper, because the relevant failure mode is usually
Delphes/root2lhco/card output producing an empty or invalid LHCO.

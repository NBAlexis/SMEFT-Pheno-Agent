# ISSUE-007: Clarify Phase 8 score CSV pass flags

- Priority: medium
- Type: data schema
- Status: closed

## Problem

Phase 8 score CSVs may include an ambiguous generic threshold-pass flag, but
each candidate algorithm has its own optimal threshold while Phase 9 selects one
final strategy.

## Risk

Manuscripts may confuse non-selected algorithm pass flags with the final
production selection.

## Candidate Fix

- use `pass_algorithm_optimal_threshold` for Phase 8 candidate algorithms
- use `pass_final_strategy` only for the Phase 9 selected algorithm/threshold

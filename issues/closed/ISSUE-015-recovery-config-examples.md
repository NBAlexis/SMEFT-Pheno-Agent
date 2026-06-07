# ISSUE-015: Add concrete runner/recovery JSON examples

- Priority: medium
- Type: documentation
- Status: closed

## Problem

The scripts now define an implicit JSON contract, but the reference docs do not
show complete configs for Phase 5 SM, Phase 5 pure NP, and Phase 6 scan
recovery.

## Risk

Agents may pass incomplete configs, wrong output labels, or wrong directories,
especially when wiring `run_mg5_config.py` and `recover_lhco_count.py` together.

## Candidate Fix

Add concise examples to `reference/madgraph-reference.md` or a small dedicated
reference:

- Phase 5 SM config: produces `sm.lhco`
- Phase 5 pure NP config: produces `np_o_N.lhco`
- Phase 6 scan config: takes `c_scan`, produces `np_o_N_f0...np_o_N_f10`
- recovery config: sets `attempt_root`, `merged_output_dir`, and
  `metadata_path` to the expected phase output directories

# ISSUE-013: Add MG5 runner preflight config validation

- Priority: high
- Type: script robustness
- Status: closed

## Problem

Some config errors are detected only after MG5 has already run. Examples:

- `output_labels` length mismatch is checked after launch, because the current
  code compares labels to the actual `run_count`
- scan mode validates actual `new_runs == 11` after launch but does not validate
  input shape before launch
- `c_scan` is not checked for positive finite numeric value
- scan mode can fall back to `scan_f0...scan_f10` if neither `operator` nor
  `output_prefix` is provided

## Risk

A bad JSON config can waste long MG5 runtime before failing with a predictable
schema error.

## Candidate Fix

Add a `validate_config(cfg)` function that runs before process creation:

- `process_mode` is one of the supported modes
- scan mode requires `c_scan`, positive finite
- scan mode requires `operator` or `output_prefix`
- scan mode rejects `output_labels` unless it has length exactly `11`
- non-scan mode accepts exactly one output label
- `coefficient_mode` is valid and has the required fields
- `nevents` is positive integer

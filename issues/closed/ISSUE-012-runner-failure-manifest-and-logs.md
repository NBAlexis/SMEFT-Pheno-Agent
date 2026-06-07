# ISSUE-012: Write MG5 runner failure manifests and logs

- Priority: high
- Type: script robustness
- Status: closed

## Problem

`scripts/run_mg5_config.py` records stdout/stderr log paths only after
`run_mg5(...)` returns successfully. If MG5 process creation or launch fails,
the runner raises before writing a structured result JSON.

## Risk

Recovery metadata may contain only a short exception string, without the full
MG5 stdout/stderr paths needed for debugging. This weakens `workflow.log` and
bug-report reproducibility.

## Candidate Fix

- make `run_mg5.py` expose stdout/stderr/log paths even on failure, or add a
  wrapper in `run_mg5_config.py` that always captures subprocess output to files
- always write `result_json` with `status: failed` when a runner-level exception
  occurs after config parsing begins
- include failure stage: `model_validation`, `create_process`, `setup_delphes`,
  `parse_param_card`, `launch`, `postprocess`, or `count`
- preserve order file paths and log paths for failed attempts

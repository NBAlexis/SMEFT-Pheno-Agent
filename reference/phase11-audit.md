# Phase 11: Self-Consistency Audit

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Systematic validation of all preceding phases before declaring completion.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

# Initialize logger
from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
logger.phase_start("11")
```

**Cleanup MUST be completed before Phase 11.** See [`cleanup.md`](cleanup.md). All MG5 process directories must have been moved from `mg5path` to `results/mg5_processes/`.

**Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase3/operator_claims.json`). Phase 11 runs independently for each `(energy, luminosity)` pair.

## Step 11.1: File Existence Check

```python
with workflow_step(logger, "11", "check_file_existence"):
```

Verify every expected file exists and has size > 0. In multi-run mode, read all paths as `results/{RUN_DIR}/...`.

| File | Phase | Action if Missing |
|------|-------|-------------------|
| `results/data/phase3/operator_claims.json` | 3 | Abort |
| `results/data/phase3/cross_sections.json` | 3 | Abort |
| `results/data/phase3/anchor.json` | 3 | Abort |
| `results/data/phase4/coefficient_ranges.json` | 4 | Abort |
| `results/data/phase4/sm_baseline.json` | 4 | Abort |
| `results/data/phase5/sm.lhco` | 5 | Abort |
| `results/data/phase5/np_anchor.lhco` | 5 | Abort |
| `results/data/phase6/np_o_*_f*.lhco` | 6 | Abort |
| `results/data/phase7/sm.csv` | 7 | Abort |
| `results/data/phase7/np_anchor.csv` | 7 | Abort |
| `results/data/phase7/algorithm_comparison.json` | 7 | Abort |
| `results/algorithms/anchor_*.pkl` | 7 | Abort |
| `results/algorithms/compute_scores.py` | 7 | Abort |
| `results/data/phase8/threshold_optimization.json` | 8 | Abort |
| `results/data/phase8/csfit_o_*_{alg}.json` | 8 | Abort |
| `results/data/phase9/constraint_table.json` | 9 | Abort |
| `results/data/phase9/algorithm_selection.json` | 9 | Warn: cannot generate comparison plot |
| `results/plots/roc_anchor.pdf` | 7 | Warn: missing ROC plot |
| `results/plots/threshold_comparison.pdf` | 8 | Warn: missing threshold comparison plot |
| `results/report.html` or `results/report.pdf` | 10 | Abort |
| `results/mg5_processes/cleanup_log.json` | Cleanup | Warn: cleanup may not have run |
| `results/mg5_processes/` (non-empty) | Cleanup | Warn: process directories not collected |
| `results/orders/` (non-empty or missing) | Cleanup | Warn: order files not collected |

**Phase 6 spot-check**: For each operator in `operator_claims.json`, verify at least one scan file exists (e.g., `np_o_1_f0.lhco`). If any operator has zero scan files, abort.


## Step 11.2: Numerical Sanity

```python
with workflow_step(logger, "11", "check_numerical_sanity"):
```

| Phase | Checks |
|-------|--------|
| 3 | At least one operator claimed globally; `anchor` is set |
| 4 | `cs_sm > 0`, `c_{scan} > 0`, `c_{scan} < 1e3`, `c_{scan}` finite |
| 7 | All selected algorithms trained successfully; `algorithm_comparison.json` records AUC (for reporting only) and model paths |
| 8 | `csfit_sm > 0`, `csfit_np >= 0`, residual < 50% for all operators |
| 9 | `fmin < 0 < fmax`, monotonicity for all operators |


## Step 11.3: Cross-Phase Consistency

```python
with workflow_step(logger, "11", "check_cross_phase_consistency"):
```

| Check | Expected | Action |
|-------|----------|--------|
| Phase 3 claimed ops == Phase 6 scanned ops == Phase 8 fitted ops == Phase 9 constrained ops | Same global operator list | Abort |
| Phase 7 algorithms == Phase 8 algorithms | Same set of trained algorithms | Abort |
| Phase 8 `csfit_sm` ≈ Phase 9 `csfit_sm` (per algorithm, per operator) | Identical per alg/op | Warn |
| Phase 8 constraint interval ≈ Phase 9 constraint interval (per alg/op at S=2) | `[-c_{n_{s=2}}, c_{n_{s=2}}]` match | Warn |
| Actual events == `{nev_scan}` | Match | Abort if modified outside debug |
| Report table == Phase 9 table | Match | Abort |
| `anchor.json` model matches Phase 4/5 SM model | Same model | Abort |


## Step 11.4: Audit Log

```python
with workflow_step(logger, "11", "write_audit_log",
                   inputs={"overall_status": overall_status}):
```

```json
{
  "status": "PASS" | "WARN" | "FAIL",
  "checks": {
    "file_existence": {"passed": N, "failed": M, "details": [...]},
    "numerical_sanity": {"passed": N, "failed": M, "details": [...]},
    "cross_phase_consistency": {"passed": N, "failed": M, "details": [...]}
  },
  "abort_reasons": [...],
  "warnings": [...]
}
```

```python
logger.phase_complete("11")
```

| Status | Condition | Action |
|--------|-----------|--------|
| PASS | No abort, no warnings | Deliver report |
| WARN | No abort, has warnings | Deliver report with audit log |
| FAIL | Any abort condition | Do NOT deliver. Return log to user |

## Phase Transition

After `logger.phase_complete("11")` is called and `audit_report.json` is written:

1. **Check final status immediately**.
2. **If PASS or WARN**: Deliver the report and audit log to the user. Workflow is complete.
3. **If FAIL**: Return the audit log to the user. Do NOT deliver the report.
4. This is the **final phase**. No further phases exist.

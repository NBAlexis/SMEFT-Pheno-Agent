# Phase 9: Self-Consistency Audit

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Systematic validation of all preceding phases before declaring completion.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

# Initialize logger
from scripts.workflow_logger import WorkflowLogger
logger = WorkflowLogger(config.workdir)
logger.phase_start("9")
```

**Cleanup MUST be completed before Phase 9.** See [`cleanup.md`](cleanup.md). All MG5 process directories must have been moved from `mg5path` to `results/mg5_processes/`.

**Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase1/operator_claims.json`). Phase 9 runs independently for each `(energy, luminosity)` pair.

## Step 9.1: File Existence Check

```python
logger.step_start("9", "check_file_existence")
```

Verify every expected file exists and has size > 0. In multi-run mode, read all paths as `results/{RUN_DIR}/...`.

| File | Phase | Action if Missing |
|------|-------|-------------------|
| `results/data/phase1/operator_claims.json` | 1 | Abort |
| `results/data/phase1/cross_sections.json` | 1 | Abort |
| `results/data/phase1/anchor.json` | 1 | Abort |
| `results/data/phase2/coefficient_ranges.json` | 2 | Abort |
| `results/data/phase2/sm_baseline.json` | 2 | Abort |
| `results/data/phase3/sm.lhco` | 3 | Abort |
| `results/data/phase3/np_anchor.lhco` | 3 | Abort |
| `results/data/phase4/np_o_*_f*.lhco` | 4 | Abort |
| `results/data/phase5/sm.csv` | 5 | Abort |
| `results/data/phase5/np_anchor.csv` | 5 | Abort |
| `results/data/phase5/algorithm_comparison.json` | 5 | Abort |
| `results/algorithms/anchor_*.pkl` | 5 | Abort |
| `results/algorithms/compute_scores.py` | 5 | Abort |
| `results/data/phase6/threshold_optimization.json` | 6 | Abort |
| `results/data/phase6/csfit_o_*_{alg}.json` | 6 | Abort |
| `results/data/phase7/constraint_table.json` | 7 | Abort |
| `results/data/phase7/algorithm_selection.json` | 7 | Warn: cannot generate comparison plot |
| `results/plots/roc_anchor.pdf` | 5 | Warn: missing ROC plot |
| `results/plots/threshold_comparison.pdf` | 6 | Warn: missing threshold comparison plot |
| `results/report.html` or `results/report.pdf` | 8 | Abort |
| `results/mg5_processes/cleanup_log.json` | Cleanup | Warn: cleanup may not have run |
| `results/mg5_processes/` (non-empty) | Cleanup | Warn: process directories not collected |
| `results/orders/` (non-empty or missing) | Cleanup | Warn: order files not collected |

**Phase 4 spot-check**: For each operator in `operator_claims.json`, verify at least one scan file exists (e.g., `np_o_1_f0.lhco`). If any operator has zero scan files, abort.

```python
logger.step_complete("9", "check_file_existence", outputs={"passed": passed, "failed": failed})
```

## Step 9.2: Numerical Sanity

```python
logger.step_start("9", "check_numerical_sanity")
```

| Phase | Checks |
|-------|--------|
| 1 | At least one operator claimed globally; `anchor` is set |
| 2 | `cs_sm > 0`, `c_{scan} > 0`, `c_{scan} < 1e3`, `c_{scan}` finite |
| 5 | All selected algorithms trained successfully; `algorithm_comparison.json` records AUC (for reporting only) and model paths |
| 6 | `csfit_sm > 0`, `csfit_np >= 0`, residual < 50% for all operators |
| 7 | `fmin < 0 < fmax`, monotonicity for all operators |

```python
logger.step_complete("9", "check_numerical_sanity", outputs={"passed": passed, "failed": failed})
```

## Step 9.3: Cross-Phase Consistency

```python
logger.step_start("9", "check_cross_phase_consistency")
```

| Check | Expected | Action |
|-------|----------|--------|
| P1 claimed ops == P4 scanned ops == P6 fitted ops == P7 constrained ops | Same global operator list | Abort |
| P5 algorithms == P6 algorithms | Same set of trained algorithms | Abort |
| P6 `csfit_sm` ≈ P7 `csfit_sm` (per algorithm, per operator) | Identical per alg/op | Warn |
| P6 constraint interval ≈ P7 constraint interval (per alg/op at S=2) | `[-c_{n_{s=2}}, c_{n_{s=2}}]` match | Warn |
| Actual events == `{nev_scan}` | Match | Abort if modified outside debug |
| Report table == P7 table | Match | Abort |
| `anchor.json` model matches P2/P3 SM model | Same model | Abort |

```python
logger.step_complete("9", "check_cross_phase_consistency", outputs={"passed": passed, "failed": failed})
```

## Step 9.4: Audit Log

```python
logger.step_start("9", "write_audit_log", inputs={"overall_status": overall_status})
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
logger.step_complete("9", "write_audit_log", outputs={"audit_log_path": "results/data/phase9/audit_log.json", "status": overall_status})
logger.phase_complete("9")
```

| Status | Condition | Action |
|--------|-----------|--------|
| PASS | No abort, no warnings | Deliver report |
| WARN | No abort, has warnings | Deliver report with audit log |
| FAIL | Any abort condition | Do NOT deliver. Return log to user |

# Phase 11: Self-Consistency Audit

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE - once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose

Systematically validate all preceding phases before declaring completion. Phase 11
must distinguish data/workflow failures from manuscript-writing quality warnings.
Remaining manuscript validation issues do not undo cleanup and do not block
delivery when the manuscript file exists and the issues are archived.

## Prerequisite

Load the configuration:

```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
logger.phase_start("11")
```

Cleanup must be completed before Phase 11. See [`cleanup.md`](cleanup.md).

Multi-run note: in multi-run mode, all paths below are under the run directory,
for example `results/E10_L1000/data/phase3/operator_claims.json`.

## Step 11.1: File Existence Check

```python
with workflow_step(logger, "11", "check_file_existence"):
```

Verify expected files exist and have size greater than zero.

| File | Phase | Action if missing |
|---|---|---|
| `results/data/phase3/operator_claims.json` | 3 | Abort |
| `results/data/phase3/cross_sections.json` | 3 | Abort |
| `results/data/phase3/anchor.json` | 3 | Abort |
| `results/data/phase4/coefficient_ranges.json` | 4 | Abort |
| `results/data/phase4/sm_baseline.json` | 4 | Abort |
| `results/data/phase5/sm.lhco` | 5 | Abort |
| `results/data/phase5/np_anchor.lhco` | 5 | Abort |
| `results/data/phase5/np_o_*.lhco` | 5 | Abort |
| `results/data/phase6/np_o_*_f*.lhco` | 6 | Abort |
| `results/data/phase7/sm.csv` | 7 | Abort |
| `results/data/phase7/np_anchor.csv` | 7 | Abort |
| `results/data/phase7/np_o_*.csv` | 7 | Abort |
| `results/data/phase7/scores/*_scores.csv` | 7 | Abort |
| `results/data/phase7/algorithm_comparison.json` | 7 | Abort |
| `results/algorithms/anchor_*.pkl` | 7 | Abort |
| `results/algorithms/compute_scores.py` | 7 | Abort |
| `results/data/phase8/threshold_optimization.json` | 8 | Abort |
| `results/data/phase8/csv/np_o_*_f*.csv` | 8 | Abort |
| `results/data/phase8/scores/*/np_o_*_f*_scores.csv` | 8 | Abort |
| `results/data/phase8/csfit_o_*_{alg}.json` | 8 | Abort |
| `results/data/phase9/constraint_table.json` | 9 | Abort |
| `results/data/phase9/algorithm_selection.json` | 9 | Warn |
| `results/data/phase10/manuscript_evidence.json` | 10 | Warn |
| `results/data/phase10/reference_paper_plan.json` | 10 | Warn |
| `results/data/phase10/literature_plan.json` | 10 | Warn |
| `results/data/phase10/manuscript_validation.json` | 10 | Warn |
| `results/plots/roc_anchor.pdf` | 7 | Warn |
| `results/plots/threshold_comparison.pdf` | 8 | Warn |
| `results/manuscript.html` or `results/manuscript.pdf` | 10 | Abort |
| `results/mg5_processes/cleanup_log.json` | Cleanup | Warn |
| `results/mg5_processes/` non-empty | Cleanup | Warn |
| `results/orders/` non-empty | Cleanup | Warn |

Phase 6 spot-check: for each operator in `operator_claims.json`, verify at least
one scan file exists, such as `np_o_1_f0.lhco`. Abort if an operator has zero
scan files.

## Step 11.2: Numerical Sanity

```python
with workflow_step(logger, "11", "check_numerical_sanity"):
```

| Phase | Checks |
|---|---|
| 3 | At least one operator claimed globally; `anchor` is set |
| 4 | `cs_sm > 0`; `coefficient_ranges.json` has one finite two-significant-digit `c_scan` in `(0, 1e3)` for every claimed operator |
| 7 | All selected algorithms trained; AUC and model paths recorded |
| 8 | `csfit_sm > 0`, `csfit_np >= 0`, residual warnings recorded |
| 9 | `fmin < 0 < fmax`; one anchor-selected algorithm is used for all final constraints |
| 10 | `manuscript_validation.json` status is `pass` or `issues_remaining`; `reference_paper_plan.json` exists; `literature_plan.json` has `toolchain`, `foundational`, `comparison_citations`, and `section_usage` groups |

Do not require `S=5` intervals to be narrower than `S=3` or `S=2`; larger
significance thresholds can require larger coefficient deviations.

## Step 11.3: Cross-Phase Consistency

Relevant invariants:
[`workflow-invariants.md`](workflow-invariants.md) Single Selection Strategy,
Publication Data, and Actual Event Counts.

```python
with workflow_step(logger, "11", "check_cross_phase_consistency"):
```

| Check | Expected | Action |
|---|---|---|
| Phase 3 claimed ops == Phase 6 scanned ops == Phase 8 fitted ops == Phase 9 constrained ops | Same global operator list | Abort |
| Phase 7 algorithms == Phase 8 algorithms | Same trained algorithm set | Abort |
| Phase 5 claimed pure NP ops == Phase 7 pure NP CSV ops | Same global operator list | Abort |
| Phase 6 scanned points == Phase 8 scan CSV points | Same operator/point list | Abort |
| Phase 9 selected algorithm is chosen from anchor operator comparison | Same anchor-selected algorithm | Abort |
| Phase 9 selected algorithm == manuscript final algorithm | Same algorithm for all final constraints | Warn |
| Phase 8 event denominators | Actual loaded LHCO counts from CutExperiment, positive for every scan point | Abort if missing, zero, equal-by-assumption to `nev_scan`, or taken from banner |
| Manuscript table == Phase 9 table | Match | Warn and record in manuscript validation |
| `reference_paper_plan.papers_to_cite` entries are included in `literature_plan.comparison_citations` | Same comparison-citation set | Warn |
| `anchor.json` model matches Phase 4/5 SM model | Same model | Abort |

## Step 11.4: Audit Log

```python
with workflow_step(logger, "11", "write_audit_log",
                   inputs={"overall_status": overall_status}):
```

Write:

```
results/audit_report.json
```

Format:

```json
{
  "status": "PASS | WARN | FAIL",
  "checks": {
    "file_existence": {"passed": 0, "failed": 0, "details": []},
    "numerical_sanity": {"passed": 0, "failed": 0, "details": []},
    "cross_phase_consistency": {"passed": 0, "failed": 0, "details": []}
  },
  "abort_reasons": [],
  "warnings": [],
  "manuscript_validation_status": "pass | issues_remaining | missing"
}
```

```python
logger.phase_complete("11")
```

| Status | Condition | Action |
|---|---|---|
| PASS | No abort, no warnings | Deliver manuscript and audit log |
| WARN | No abort, has warnings or manuscript issues remaining | Deliver manuscript and audit log |
| FAIL | Any abort condition | Return audit log; do not claim workflow success |

## Phase Transition

After `logger.phase_complete("11")` is called and `audit_report.json` is written:

1. Check final status immediately.
2. If PASS or WARN, deliver the manuscript and audit log to the user.
3. If FAIL, return the audit log to the user.
4. This is the final phase.

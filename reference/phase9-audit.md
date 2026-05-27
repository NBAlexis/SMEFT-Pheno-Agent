# Phase 9: Self-Consistency Audit

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Systematic validation of all preceding phases before declaring completion.

## Prerequisites

**Cleanup MUST be completed before Phase 9.** See [`cleanup.md`](cleanup.md). All MG5 process directories must have been moved from `mg5path` to `results/mg5_processes/`.

**Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase1/operators.json`). Phase 9 runs independently for each `(energy, luminosity)` pair.

## Step 9.1: File Existence Check

Verify every expected file exists and has size > 0. In multi-run mode, read all paths as `results/{RUN_DIR}/...`.

| File | Phase | Action if Missing |
|------|-------|-------------------|
| `results/data/phase1/operators.json` | 1 | Abort |
| `results/data/phase1/cross_sections.json` | 1 | Abort |
| `results/data/phase2/coefficient_ranges.json` | 2 | Abort |
| `results/data/phase2/sm_baseline.json` | 2 | Abort |
| `results/data/phase3/sm.lhco` | 3 | Abort |
| `results/data/phase5/sm.csv` | 5 | Abort |
| `results/data/phase5/algorithm_comparison.json` | 5 | Abort |
| `results/data/phase7/constraint_table.json` | 7 | Abort |
| `results/data/phase7/algorithm_selection.json` | 7 | Warn: cannot generate comparison plot |
| `results/report.html` or `results/report.pdf` | 8 | Abort |
| `results/mg5_processes/cleanup_log.json` | Cleanup | Warn: cleanup may not have run |
| `results/mg5_processes/` (non-empty) | Cleanup | Warn: process directories not collected |
| `results/orders/` (non-empty or missing) | Cleanup | Warn: order files not collected |

## Step 9.2: Numerical Sanity

| Phase | Checks |
|-------|--------|
| 1 | `sigma_i > 0` for at least one operator |
| 2 | `cs_sm > 0`, `c1 > 0`, `c1 < 1e3`, `c1` finite |
| 5 | `0.5 < AUC <= 1.0` |
| 6 | `csfit_sm > 0`, `csfit_np >= 0`, residual < 50% |
| 7 | `fmin < 0 < fmax`, monotonicity |

## Step 9.3: Cross-Phase Consistency

| Check | Expected | Action |
|-------|----------|--------|
| P1 ops == P2 ops | Same list | Abort |
| P5 ops == P6 ops == P7 ops | Same list | Abort |
| P6 `csfit_sm` ≈ P7 `csfit_sm` (per algorithm) | Identical per alg | Warn |
| Actual events == `{nev_scan}` | Match | Abort if modified outside debug |
| Report table == P7 table | Match | Abort |

## Step 9.4: Audit Log

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

| Status | Condition | Action |
|--------|-----------|--------|
| PASS | No abort, no warnings | Deliver report |
| WARN | No abort, has warnings | Deliver report with audit log |
| FAIL | Any abort condition | Do NOT deliver. Return log to user |

# Phase 12: Self-Consistency Audit

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE - once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose

Systematically validate all preceding phases before declaring completion. Phase 12
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
logger.phase_start("12")
```

Cleanup and Phase 11 replay packaging must be completed before Phase 12. See
[`cleanup.md`](cleanup.md) and [`phase11-replay.md`](phase11-replay.md).
Here cleanup means large intermediate files may be removed, while
runner-recorded process folders and order files are archived by moving into
`results/mg5_processes/` and `results/orders/`. Empty archive directories are a
cleanup failure, not a successful deletion.

Multi-run note: in multi-run mode, all paths below are under the run directory,
for example `results/E10_L1000/data/phase3/operator_claims.json`.

## Step 12.1: File Existence Check

```python
with workflow_step(logger, "12", "check_file_existence"):
```

Use the manifest-driven audit helper first:

```bash
python scripts/audit_expected_outputs.py {workdir} \
  --phase10-required-ids-json reference/manuscript-checklist-required-ids.json \
  --json-out results/audit_expected_outputs.json
```

Then verify any additional run-specific files exist and have size greater than
zero. The helper builds the expected operator/scan/algorithm matrix from
`operator_claims.json`, `scan_manifest.json`, and `algorithm_comparison.json`.
It also parses Phase 5/6 `event_count_recovery.json` and checks merged output
paths, loaded counts, source banners, merged cross-sections, warnings, and
zero-event failure records. It reads the Phase 10 required checklist IDs from
`reference/manuscript-checklist-required-ids.json`; if the audit helper is copied
to a target separately from the skill folder, copy this JSON too or pass its
target path with `--phase10-required-ids-json`. Do not rely only on wildcards
when a manifest is available.

| File | Phase | Action if missing |
|---|---|---|
| `results/data/phase2/environment_manifest.json` | 2 | Abort |
| `results/data/phase3/operator_claims.json` | 3 | Abort |
| `results/data/phase3/cross_sections.json` | 3 | Abort |
| `results/data/phase3/anchor.json` | 3 | Abort |
| Phase 3 runner result JSONs referenced by `model_status.json` | 3 | Abort |
| `results/data/phase4/coefficient_ranges.json` | 4 | Abort |
| `results/data/phase4/sm_baseline.json` | 4 | Abort |
| `results/data/phase4/sm_baseline_result.json` | 4 | Abort |
| `results/data/phase5/sm.lhco` | 5 | Abort |
| `results/data/phase5/np_anchor.lhco` | 5 | Abort |
| `results/data/phase5/np_o_*.lhco` | 5 | Abort |
| `results/data/phase5/sm_result.json` | 5 | Abort |
| `results/data/phase5/np_o_*_result.json` | 5 | Abort |
| `results/data/phase5/np_anchor_alias.json` | 5 | Abort |
| `results/data/phase5/event_count_recovery.json` | 5 | Abort |
| `results/data/phase6/np_o_*_f*.lhco` | 6 | Abort |
| `results/data/phase6/np_o_*_scan_result.json` | 6 | Abort |
| `scan_manifest.json` per-operator `weighted_order_guard` with positive `max_weighted_order` and runner-selected `WEIGHTED`/`Weighted` keyword | 6 | Abort |
| `results/data/phase6/event_count_recovery.json` | 6 | Abort |
| `results/data/phase7/sm.csv` | 7 | Abort |
| `results/data/phase7/np_anchor.csv` | 7 | Abort |
| `results/data/phase7/np_o_*.csv` | 7 | Abort |
| `results/data/phase7/feature_schema.json` | 7 | Abort |
| `results/data/phase7/algorithm_descriptions.json` | 7 | Abort |
| `results/data/phase7/phase7_validation.json` | 7 | Abort |
| `results/data/phase7/scores/*_scores.csv` | 7 | Abort |
| `results/data/phase7/algorithm_comparison.json` | 7 | Abort |
| `results/algorithms/anchor_*.pkl` | 7 | Abort |
| `results/algorithms/compute_scores.py` | 7 | Abort |
| `results/data/phase8/threshold_optimization.json` | 8 | Abort |
| `results/data/phase8/dataset_summary.json` | 8 | Abort |
| `results/data/phase8/csv/np_o_*_f*.csv` | 8 | Abort |
| `results/data/phase8/scores/*/np_o_*_f*_scores.csv` | 8 | Abort |
| `results/data/phase8/csfit_o_*_{alg}.json` | 8 | Abort |
| `results/data/phase9/constraint_table.json` | 9 | Abort |
| `results/data/phase9/constraint_table.csv` | 9 | Abort |
| `results/data/phase9/algorithm_selection.json` with selected algorithm and threshold | 9 | Abort |
| `results/data/phase10/manuscript_build_environment.json` | 10 | Abort |
| `results/data/phase10/manuscript_evidence.json` | 10 | Abort |
| `results/data/phase10/reference_paper_plan.json` | 10 | Abort |
| `results/data/phase10/literature_plan.json` | 10 | Abort |
| `results/data/phase10/manuscript_checklist.json` | 10 | Abort |
| `results/data/phase10/manuscript_trace_map.json` | 10 | Abort |
| `results/data/phase10/manuscript_validation.json` | 10 | Abort |
| `results/data/phase10/manuscript_draft_v1.*` | 10 | Abort |
| `results/plots/roc_anchor.pdf` | 7 | Abort |
| `results/plots/score_dist_all_pure_np_{alg}.pdf` | 7 | Abort |
| `results/plots/threshold_comparison.pdf` | 8 | Abort |
| `results/plots/csfit_plot_o_*_{alg}.pdf` | 8 | Abort |
| `results/plots/anchor_s2_constraint_range_vs_threshold.pdf` | 8 | Abort |
| `results/plots/anchor_s2_algorithm_constraint_bar.pdf` | 9 | Abort |
| `results/manuscript.pdf` and `.tex` if `phase10/manuscript_build_environment.json` has `pdf_required=true`; otherwise `results/manuscript.html` | 10 | Abort |
| `results/mg5_processes/cleanup_log.json` | Cleanup archive log | Abort |
| `results/mg5_processes/` non-empty archive of moved process folders | Cleanup archive | Abort |
| `results/orders/` non-empty archive of moved order files | Cleanup archive | Abort |
| `results/replay/replay.sh` | 11 | Abort |
| `results/replay/replay_manifest.json` | 11 | Abort |
| `results/replay/replay_validation.json` | 11 | Abort |
| `results/replay/data_files_report.md` | 11 | Abort |
| Phase drivers and report generator referenced by `replay_manifest.json` | 11 | Abort |

Phase 6 spot-check: for each operator in `operator_claims.json`, verify at least
one scan file exists, such as `np_o_1_f0.lhco`. Abort if an operator has zero
scan files.

## Step 12.2: Numerical Sanity

```python
with workflow_step(logger, "12", "check_numerical_sanity"):
```

| Phase | Checks |
|---|---|
| 3 | At least one operator claimed globally; `anchor` is set |
| 4 | `cs_sm > 0`; `coefficient_ranges.json` has one finite two-significant-digit `c_scan` in `(0, 1e3)` for every claimed operator |
| 7 | All selected algorithms trained; AUC, model paths, feature schema, score definitions, and pseudocode recorded |
| 8 | fixed `sigma0_after_cut`/`csfit_sm > 0`, `fit_intercept_fixed=true`, `csfit_np >= 0`, dataset summary complete, residual warnings recorded |
| 9 | `fmin < 0 < fmax`; one anchor-selected algorithm is used for all final constraints |
| 10 | `manuscript_validation.json` status is `pass` or `issues_remaining`; `manuscript_checklist.json` exists and was run for the final draft; `reference_paper_plan.json` exists; `literature_plan.json` has `toolchain`, `foundational`, `comparison_citations`, and `section_usage` groups; if `pdf_required=true`, `manuscript.pdf` and `.tex` exist |
| 11 | Replay validation records successful Bash syntax and clean-directory dry-run checks; manifest phase order is exactly 2 through 9; the report is non-empty and covers every declared numerical output |

Do not require `S=5` intervals to be narrower than `S=3` or `S=2`; larger
significance thresholds can require larger coefficient deviations.

## Step 12.3: Cross-Phase Consistency

Relevant invariants:
[`workflow-invariants.md`](workflow-invariants.md) Single Selection Strategy,
Publication Data, and Actual Event Counts.

```python
with workflow_step(logger, "12", "check_cross_phase_consistency"):
```

| Check | Expected | Action |
|---|---|---|
| Phase 3 claimed ops == Phase 6 scanned ops == Phase 8 fitted ops == Phase 9 constrained ops | Same global operator list | Abort |
| Phase 7 algorithms == Phase 8 algorithms | Same trained algorithm set | Abort |
| Phase 5 claimed pure NP ops == Phase 7 pure NP CSV ops | Same global operator list | Abort |
| Phase 6 scanned points == Phase 8 scan CSV points | Same operator/point list | Abort |
| Phase 6 weighted-order guard | Conservative bound extracted from Phase 4 SM and Phase 5 pure-NP process folders is used by the runner | Abort |
| Event-count recovery records | No selected sample below `10%` requested unless exhausted recovery red flag is recorded | Abort |
| Phase 9 selected algorithm is chosen from anchor operator comparison | Same anchor-selected algorithm | Abort |
| Phase 9 selected algorithm == manuscript final algorithm | Same algorithm for all final constraints | Warn |
| Phase 8 event denominators | Actual loaded LHCO counts from CutExperiment, positive for every scan point | Abort if missing, zero, equal-by-assumption to `nev_scan`, or taken from banner |
| Manuscript table == Phase 9 table | Match | Warn and record in manuscript validation |
| `reference_paper_plan.papers_to_cite` entries are included in `literature_plan.comparison_citations` | Same comparison-citation set | Warn |
| `anchor.json` model matches Phase 4/5 SM model | Same model | Abort |
| Phase 11 replay manifest output matrix == Phase 3-9 required numerical deliverables | Every required numerical JSON/CSV/LHCO/model/plot family has one producing step | Abort |
| Phase 11 replay computation inputs | Frozen config, external tools/models, packaged code, and raw inputs only; no original Phase 3-9 numerical result is consumed to produce replay results | Abort |
| Phase 11 data report == replay manifest output matrix | Every declared data file family is described with producer, format/schema, scientific meaning, units where applicable, and integrity metadata | Abort |

## Step 12.4: Audit Log

```python
with workflow_step(logger, "12", "write_audit_log",
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
logger.phase_complete("12")
```

| Status | Condition | Action |
|---|---|---|
| PASS | No abort, no warnings | Deliver manuscript and audit log |
| WARN | No abort, has warnings or manuscript issues remaining | Deliver manuscript and audit log |
| FAIL | Any abort condition | Return audit log; do not claim workflow success |

## Phase Transition

Before calling `logger.phase_complete("12")`, satisfy
[`deliverables-phase12.md`](deliverables-phase12.md). Missing deliverables
require self-repair, not user interaction.

After `logger.phase_complete("12")` is called and `audit_report.json` is written:

1. Check final status immediately.
2. If PASS or WARN, deliver the manuscript and audit log to the user.
3. If FAIL, return the audit log to the user.
4. This is the final phase.

# Phase 12: Self-Consistency Audit

> **Contract priority**: Preserve the research objective and deliverables. Apply
> the technical-failure and `phase_fail` definitions in `SKILL.md`.

## Purpose

Systematically validate the frozen research objective and expanded deliverables
contract before declaring completion. Phase 12 must distinguish unmet research
evidence from manuscript-writing quality warnings.
Remaining manuscript validation issues do not undo cleanup and do not block
delivery when the manuscript file exists and the issues are archived.

## Prerequisite

Load the configuration:

```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir, run_dir)
logger.phase_start("12")
```

Cleanup and Phase 11 replay packaging must be completed before Phase 12. See
[`cleanup.md`](cleanup.md) and [`phase11-replay.md`](phase11-replay.md).
Here cleanup means only ROOT/HEPMC intermediate files may be removed, while
runner-recorded process folders and order files are archived by moving into
`results/mg5_processes/` and `results/orders/`. Empty archive directories are a
cleanup failure, not a successful deletion.

Phase 12 may read replay files and recompute their checksums. It must not invoke
`replay.sh`, pass a dry-run flag, execute a replay step, start MG5, train a
model, or compare replayed and original numerical results.

Multi-run note: in multi-run mode, all paths below are under the run directory,
for example `results/E10_L1000/data/phase3/operator_claims.json`.

## Step 12.1: File Existence Check

```python
with workflow_step(logger, "12", "check_file_existence"):
```

Verify that the scientific objective and deliverable rules have not drifted,
then expand the frozen rules using the actual run manifests:

```bash
python scripts/research_contract.py verify {workdir}/results/run_config.json
python scripts/research_contract.py resolve {workdir}/results/run_config.json \
  --run-root {current_run_root} \
  --output {current_run_root}/deliverables_resolved.json
```

`resolve` must finish with no `pending_rules`. Pending selectors mean an
upstream manifest is missing; repair the responsible phase rather than deleting
or weakening the rule. Verify every resolved item exists, is non-empty where
appropriate, and passes its type/schema acceptance checks.

Then use the detailed manifest-driven audit helper:

```bash
python scripts/audit_expected_outputs.py {workdir} \
  {optional_run_dir_argument} \
  --phase10-required-ids-json reference/manuscript-checklist-required-ids.json \
  --json-out {current_run_root}/audit_expected_outputs.json
```

The helper supplies deeper content and consistency checks. It builds the
expected operator/scan/algorithm matrix from
`operator_claims.json`, `scan_manifest.json`, and `algorithm_comparison.json`.
It also parses Phase 5/6 `event_count_recovery.json` and checks merged output
paths, loaded counts, source banners, merged cross-sections, warnings, and
zero-event failure records. It reads the Phase 10 required checklist IDs from
`reference/manuscript-checklist-required-ids.json`; if the audit helper is copied
to a target separately from the skill folder, copy this JSON too or pass its
target path with `--phase10-required-ids-json`. Do not rely only on wildcards
when a manifest is available.

This first pass deliberately defers the Phase 12 audit files themselves so the
audit does not require its own not-yet-written output. After writing both
`audit_expected_outputs.json` and `audit_report.json`, run the final, non-writing
contract check:

```bash
python scripts/audit_expected_outputs.py {workdir} \
  {optional_run_dir_argument} \
  --phase10-required-ids-json reference/manuscript-checklist-required-ids.json \
  --include-final-artifacts
```

This command must return PASS or WARN. It checks the existing final artifacts
without rewriting either one, eliminating the self-audit cycle.

Use an empty `optional_run_dir_argument` in single-run mode and
`--run-dir {run_dir}` in multi-run mode. In the tables below, `Abort` means add
an `ok=false`, `severity="abort"` entry to the audit report, continue collecting
the remaining checks, and make the final audit status `FAIL`. It does not mean
stop before diagnostics or skip repair attempts.

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
| `results/replay/data_files_report.md` | 11 | Abort |
| Phase drivers and helpers referenced by `replay_manifest.json` | 11 | Abort |

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
| 7 | All selected algorithms trained; AUC recorded as descriptive/diagnostic information only; model paths, feature schema, score definitions, and pseudocode recorded |
| 8 | shared `f5` sources cover every claimed operator; repeated initial sources are proven Phase 6 recovery attempts; extra Phase 8 sources are anchor `f5` only; the merged cross-section is the source-banner arithmetic mean; score identities and counts follow the selected-threshold three-round/half-event rule; every fit uses the matching shared `sigma0_after_cut`; `csfit_np >= 0`; independent numerical review passes; dataset summary complete |
| 9 | `fmin < 0 < fmax`; final constraints follow the recorded `anchor_operator_only` or `per_operator_best` scope; all scientifically valid strategies are compared only by expected constraint-interval width and never by AUC; JSON and CSV agree; independent numerical review passes |
| 10 | `manuscript_validation.json` status is `pass` or `issues_remaining`, every frozen required manuscript item is present, and `major_issues` is empty; `issues_remaining` contains minor issues only; `reference_paper_plan.json` exists; `literature_plan.json` has `toolchain`, `foundational`, `comparison_citations`, and `section_usage` groups; if `pdf_required=true`, `manuscript.pdf` and `.tex` exist |
| 11 | Replay manifest phase order is exactly 2 through 9; every packaged input/code checksum matches; no replay command is executed |

Do not require `S=5` intervals to be narrower than `S=3` or `S=2`; larger
significance thresholds can require larger coefficient deviations.

## Step 12.3: Cross-Phase Consistency

Relevant invariants:
[`workflow-invariants.md`](workflow-invariants.md) Selection Scope,
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
| Event-count recovery records | No selected sample below `10%` requested; otherwise recovery remains incomplete and the producing Phase cannot pass | Abort |
| Phase 9 selection scope | `anchor_operator_only` is the default when scientifically adequate; user-requested or evidence-driven `per_operator_best` records rationale/evidence and uses the narrowest-interval scientifically valid recorded Phase 7 strategy for every claimed operator | Abort |
| Phase 9 selection == manuscript final selection | Same scope and same per-operator algorithm/threshold assignments | Warn |
| Phase 8 event denominators | Actual loaded LHCO counts from CutExperiment, positive for every scan point | Abort if missing, zero, equal-by-assumption to `nev_scan`, or taken from banner |
| Phase 8 shared `f5` background | The set of initial-source operators equals all claimed operators; accepted Phase 6 recovery may contribute multiple listed attempts for one operator; additional rounds are anchor `f5` only and no more than three; formulas match observed or half-event counts; each algorithm/threshold uses the same shared background value in every operator fit | Abort |
| Manuscript table == Phase 9 table | Match | Warn and record in manuscript validation |
| `reference_paper_plan.papers_to_cite` entries are included in `literature_plan.comparison_citations` | Same comparison-citation set | Warn |
| `anchor.json` model matches Phase 4/5 SM model | Same model | Abort |
| Phase 11 replay manifest output matrix == Phase 3-9 required numerical deliverables | Every required numerical JSON/CSV/LHCO/model/plot family has one producing step | Abort |
| Phase 11 replay computation inputs | Packaged config/code, recorded external installations, selected model/card files, and manifest `source_inputs` only; no original Phase 3-9 numerical result is consumed by a production step | Abort |
| Current objective == `research_contract.json` | Canonical scientific projection and SHA-256 match | Abort |
| Resolved deliverables == frozen rules expanded from actual manifests | No pending rule; no rule removed because of technical difficulty | Abort |
| Every resolved deliverable passes acceptance | Required path exists and satisfies its declared type/schema | Abort |

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
    "research_contract": {"passed": 0, "failed": 0, "details": []},
    "deliverables_contract": {"passed": 0, "failed": 0, "details": []},
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
| FAIL | Any required contract item remains unmet | Return audit log with the unmet item, attempted repairs, and evidence; do not claim workflow success |

## Phase Transition

Before calling `logger.phase_complete("12")`, write `audit_report.json`, run the
final `--include-final-artifacts` check, and satisfy
[`deliverables-phase12.md`](deliverables-phase12.md). Missing deliverables
require self-repair, not user interaction.

After `logger.phase_complete("12")` is called:

1. Check final status immediately.
2. If PASS or WARN, deliver the manuscript and audit log to the user.
3. If FAIL, return the audit log and the unresolved contract items. A technical
   command failure alone is not a final failure; Phase 12 may report final FAIL
   only after repair and alternative implementation attempts establish that the
   frozen item cannot be fulfilled.
4. This is the final phase.

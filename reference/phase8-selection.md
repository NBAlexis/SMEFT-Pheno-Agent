# Phase 8: Apply Selection and Fit Cross-Section

> **Contract priority**: Preserve the research objective and deliverables. Apply the technical-failure and `phase_fail` definitions in `SKILL.md`.

## Purpose
For each trained ML algorithm, apply its threshold to scan samples, fit the selected cross-section, and find the optimal threshold. In multi-model mode, threshold optimization uses the **anchor operator's** scan data. Every operator fit uses one shared `f5` event pool for the fixed background term.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

# Initialize logger
from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir, run_dir)
logger.phase_start("8")
```

Read `anchor.json` from Phase 3. The anchor operator (`o_1` by convention) provides the scan data for threshold optimization.

Read `results/data/phase6/scan_manifest.json`. Phase 6 launches MG5 with a
scan expression and does not need to precompute the 11 numeric coefficients.
Phase 8 may reconstruct `scan_coeffs` from each operator's manifest `c_scan`
for fitting and plotting:

```python
scan_coeffs = [-c_scan + 0.2 * c_scan * n for n in range(11)]
```

## Step 8.0: Build the Shared `f5` Event Pool

Follow [`phase8-shared-f5.md`](phase8-shared-f5.md) completely. It defines the
canonical Phase 6 sources, banner arithmetic mean, single-point anchor runner,
score-derived event counts, three-round zero handling, output fields, and
required checks. Do not use a half-event value before the third additional
round.

## Step 8.1: Convert Scan LHCO to CSV

```python
with workflow_step(logger, "8", "convert_scan_lhco_to_csv",
                   inputs={"num_operators": len(operator_claims), "points_per_operator": 11}):
```

Convert all Phase 6 `.lhco` files to `.csv` using the same feature extraction as
Phase 7 and the event-count rules in
[`event-count-recovery.md`](event-count-recovery.md). For every scan point,
record:

- `requested_event_count`: locked `nev_scan` from `run_config.json`
- `loaded_lhco_event_count`: `LoadLHCOlympics(lhco).GetEventCount()` immediately after loading
- `surviving_final_state_event_count`: feature-row count after final-state cuts
- `count_source`: `CutExperiment LoadLHCOlympics(...).GetEventCount(); not banner`

Banner files may be used for cross-sections only. Do not use banner event counts
for efficiencies, denominators, or manuscript evidence.

The scan CSV files are publication data, not temporary files. Save them under:

```
results/data/phase8/csv/np_o_{g_idx}_f{i}.csv
```

for every globally claimed operator `o_{g_idx}` and every scan point
`i = 0, ..., 10`.


## Step 8.2: Score All Scan Points (Per Algorithm)

```python
with workflow_step(logger, "8", "score_scan_points",
                   inputs={"num_algorithms": len(alg_data["anchor"])}):
```

Load algorithms from `algorithm_comparison.json` under the `"anchor"` key:

```python
from scripts.read_results import read_algorithm_comparison

alg_data = read_algorithm_comparison(config.workdir)

for alg_name, alg_info in alg_data["anchor"].items():
    clf = joblib.load(alg_info["algorithm_path"])
    # ... load features X from CSV ...
    import sys
    sys.path.insert(0, os.path.join(config.workdir, "results", "algorithms"))
    from compute_scores import compute_scores
    scores = compute_scores(clf, X)  # normalized [0, 1], higher = more NP-like
```

Compute scores for all events in each scan point. The `compute_scores` function was produced in Phase 7 (Step 7.2.3) and handles normalization automatically for all algorithm types.

Use `alg_name` exactly as the stable algorithm key from
`algorithm_comparison.json["anchor"]` for score directories, fit JSON filenames,
plots, and threshold records. Do not invent a second sanitized name in Phase 8.

Save per-event scan scores for every algorithm:

```
results/data/phase8/scores/{alg}/np_o_{g_idx}_f{i}_scores.csv
```

Each score CSV must contain at least:

```
event_index, score, source_csv
```

`event_index` is the zero-based row identity in `source_csv`. It must cover
`0` through `row_count-1` exactly once; duplicated, missing, negative, or
non-integer identities are invalid.

Before final Phase 9 selection, candidate score CSVs may include
`pass_algorithm_optimal_threshold`. After the final selection scope is applied,
the score CSVs used for each operator's final constraint may include
`pass_final_strategy`. Do not write any generic or ambiguous optimal-threshold
pass flag.

## Step 8.3: Optimize Threshold Per Algorithm (using anchor operator)

### Reference Operator Selection

**Explicitly use the anchor operator** (from `anchor.json`, which is `o_1` by convention):

```python
# The anchor is always the first claimed operator
ref_op = "o_1"
```

Load the anchor operator's scan data: `np_o_1_f0.lhco` through `np_o_1_f10.lhco`.

### Event Counts

Read the requested scan count only as metadata. The denominator for efficiencies
and selected cross-sections is the actual LHCO event count for that scan point:

```python
events = LoadLHCOlympics(lhco_path)
loaded_event_count = events.GetEventCount()
assert loaded_event_count > 0
```

Never replace `loaded_event_count` with `nev_scan`, and never use event counts
from the MG5 banner.

### Threshold Scan Per Algorithm

For **each algorithm**, use exactly
`[0.00, 0.02, ..., 0.98, 1.00]`. Apply the zero-count procedure in
[`phase8-shared-f5.md`](phase8-shared-f5.md) before calculating an interval.
An unresolved zero at an unselected threshold is excluded from the finite-width
comparison and does not automatically request another MG5 run.

```python
with workflow_step(logger, "8", f"optimize_threshold_{alg_name}",
                   inputs={"algorithm": alg_name, "num_thresholds": 51}):
```
1. Count passing events per scan point: `m_x` for each scan coefficient value `c_x`. Reconstruct `c_x` from the operator's Phase 6 manifest `c_scan` using `[-c_scan + 0.2 * c_scan * n for n in range(11)]`.
   A threshold with zero passing events in every anchor scan point is recorded
   as `no_selected_scan_events` and excluded from optimization.
2. Compute cut cross-section:
   ```
   cs_cut_x = cs_x * m_x / loaded_event_count_x
   ```
   where `cs_x` is `outputs[*].cross_section_pb` from the corresponding Phase 6
   runner result JSON, and `loaded_event_count_x` is the actual LHCO event
   count from CutExperiment. The Phase 6 runner already parsed the banner and
   recorded this value. Except for the explicitly defined additional anchor `f5`
   rounds in Step 8.0, Phase 8 does not rerun MadGraph. If the value is missing
   or non-finite, repair the Phase 6 result rather than inventing or reparsing it
   in Phase 8.
   The total selection efficiency is `m_x / loaded_event_count_x`. If useful,
   also record conditional ML efficiency as
   `m_x / surviving_final_state_event_count_x`.
3. Fit the quadratic with a **fixed intercept**:
   ```
   csfit(f) = sigma0_after_cut + f*csfit_int + f^2*csfit_np
   ```
   where `sigma0_after_cut` is the accepted shared-`f5` value for this
   algorithm and threshold from `shared_f5_background.json`. For the required
   scan expression, `f5` is the coefficient-zero point. Do not fit the constant
   term and do not replace it with an individual operator's `f5`, an uncut SM
   cross-section, or a Phase 5 pure-SM value.

   Fit only `csfit_int` and `csfit_np` using:
   ```
   cs_cut_x - sigma0_after_cut = f_x*csfit_int + f_x^2*csfit_np
   ```
4. Solve `S_stat = 2` with physical luminosity converted to the inverse unit
   matching the fitted cross-section. In the default workflow, `csfit_*` is in
   pb and `config.luminosity` is in fb^-1, so use
   `L_pb_inv = config.luminosity * 1000`. The factor `1000` is only the
   `fb^-1 -> pb^-1` unit conversion; if cross-sections are stored in another
   unit, convert accordingly.

   Use [`significance-reference.md`](significance-reference.md):
   ```
   N_bg = L_pb_inv * sigma0_after_cut
   N_sig = L_pb_inv * (f * csfit_int + f^2 * csfit_np)
   S_stat = sqrt(2 * [(N_bg + N_sig) * ln(1 + N_sig/N_bg) - N_sig])
   ```

   Solve `S_stat(f) = 2` for `f`. The coefficient interval is defined by the
   real roots of this equation. Filter out complex roots using
   [`significance-reference.md`](significance-reference.md). The upper bound is
   the smallest positive real root; the lower bound is the largest negative
   real root.
5. Record constraint width: `upper_bound - lower_bound` (full interval width)

Select the threshold that **minimizes the full real-root constraint width** for each algorithm individually.


Record per algorithm:
```json
{
  "algorithm": "{alg_name}",
  "optimal_threshold": 0.62,
  "constraint_width_at_optimal": 0.045,
  "threshold_scan": [
    {
      "threshold": 0.62,
      "anchor_scan_passing_event_count": 24891,
      "shared_f5_passing_event_count": 18520,
      "effective_passing_event_count": 18520.0,
      "background_status": "observed_events",
      "sigma0_after_cut_pb": 0.0012,
      "fit_intercept_fixed": true,
      "lower_bound": -0.021,
      "upper_bound": 0.024,
      "constraint_width": 0.045
    }
  ]
}
```

At the top level of `threshold_optimization.json`, record an independent review
of the numerical calculation:

```json
"numerical_validation": {
  "status": "pass",
  "method": "independent recalculation of counts, fixed-intercept fits, significance roots, and selected widths using the method actually adopted",
  "evidence_paths": ["data/phase8/threshold_optimization.json", "data/phase8/csfit_o_1_bdt.json"]
}
```

The LLM performs this scientific review after reading the produced data. When
the run uses a method not covered by the bundled audit, modify or add a checker
for the actual method, record its path/checksum in the workflow log, and cite its
output in `evidence_paths`. Do not change a check merely to accept unexplained
numbers.

Record per scan point:

```json
{
  "operator": "o_1",
  "point": 0,
  "coefficient": -0.12,
  "requested_event_count": 1000000,
  "loaded_lhco_event_count": 998412,
  "surviving_final_state_event_count": 972300,
  "passing_event_count": 18520,
  "total_selection_efficiency": 0.01855,
  "conditional_ml_efficiency": 0.01905,
  "cs_x_pb": 0.034,
  "cs_cut_x_pb": 0.000631,
  "is_f0_point": false
}
```

### Parameter Passing Safety

When calling `fit_and_solve`, add type assertions to prevent silent swaps:

```python
def fit_and_solve(scan_coeffs, scan_features, scan_cs, clf_alg, threshold, op, L):
    assert isinstance(scan_features, dict), \
        f"scan_features must be dict, got {type(scan_features)}"
    assert isinstance(scan_cs, list), \
        f"scan_cs must be list, got {type(scan_cs)}"
    ...
```

## Step 8.4: Apply Each Algorithm's Optimal Threshold to All Operators

```python
with workflow_step(logger, "8", "apply_thresholds_all_operators",
                   inputs={"num_algorithms": len(alg_data["anchor"]), "num_operators": len(operator_claims)}):
```

For **each algorithm**, using **its own** optimal threshold from Step 8.3, repeat the quadratic fit for **EVERY globally claimed operator** (`o_1` through `o_N`).

For each operator `o_{g_idx}`:
- Load its scan data: `np_o_{g_idx}_f0.lhco` through `np_o_{g_idx}_f10.lhco`
- Apply the algorithm's threshold
- Fit the quadratic with that algorithm's shared `f5` background as the fixed intercept and
  record `sigma0_after_cut`, `csfit_int`, `csfit_np`,
  `fit_intercept_fixed=true`, and `f0_label="f5"`
- Use each scan point's own `loaded_lhco_event_count` as the denominator for
  `cs_cut_x`. Do not use the anchor denominator for non-anchor operators.

## Step 8.5: Plot

```python
with workflow_step(logger, "8", "plot_csfit_and_threshold_comparison",
                   inputs={"num_algorithms": len(alg_data["anchor"]), "num_operators": len(operator_claims)}):
```

For each algorithm and each operator: scatter `cs_cut_x` points + fitted curve `csfit(f)`.

Also plot **algorithm comparison**: for the anchor operator, show constraint width vs threshold for all algorithms on the same plot.

Also plot the **anchor S=2 constraint range vs threshold**: for the anchor
operator and every trained algorithm, show the lower and upper real-root
constraint bounds as functions of threshold. This plot is manuscript evidence
for how the selected threshold changes the expected coefficient range.

## Step 8.6: Build Dataset Summary

Before completing Phase 8, write:

```
results/data/phase8/dataset_summary.json
```

This file is the manuscript source for the dataset table. Build it from Phase 5
runner result JSONs, Phase 6 scan result/recovery metadata, Phase 7
`event_counts.json`, and Phase 8 `scan_event_counts.json`. For every SM, pure
NP, and scan dataset row include:

- `dataset_id`
- `loaded_lhco_event_count`
- `surviving_final_state_event_count`
- `final_state_cut`
- `raw_cross_section_pb`
- `final_state_cut_cross_section_pb`
- `cross_section_source`: runner result, recovery metadata, or banner path
- `public_csv_path`
- `score_csv_paths`; for scan rows, include every Phase 8 algorithm score CSV;
  for SM and pure-NP rows, include the corresponding Phase 7 score CSVs.

Compute `final_state_cut_cross_section_pb` as
`raw_cross_section_pb * surviving_final_state_event_count / loaded_lhco_event_count`.
This is not the ML-threshold-selected `cs_cut_x`.

```python
logger.phase_complete("8")
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase8/...`). See `SKILL.md` Output Layout.

```
results/data/phase8/
  shared_f5.lhco
  shared_f5_merge.json
  shared_f5_background.json
  csv/shared_f5.csv
  csv/np_o_1_f0.csv, ..., csv/np_o_N_f10.csv
  scores/{alg}/shared_f5_scores.csv
  scores/{alg}/np_o_1_f0_scores.csv, ..., scores/{alg}/np_o_N_f10_scores.csv
  threshold_optimization.json    # per-algorithm optimal thresholds (from anchor)
  scan_event_counts.json         # requested, loaded, surviving, and passing counts
  dataset_summary.json
  csfit_o_1_{alg1}.json, csfit_o_1_{alg2}.json, ...
  csfit_o_2_{alg1}.json, csfit_o_2_{alg2}.json, ...
  ...
  csfit_o_N_{alg1}.json, csfit_o_N_{alg2}.json, ...
results/plots/
  csfit_plot_o_1_{alg1}.pdf, csfit_plot_o_1_{alg2}.pdf, ...
  csfit_plot_o_2_{alg1}.pdf, csfit_plot_o_2_{alg2}.pdf, ...
  ...
  csfit_plot_o_N_{alg1}.pdf, csfit_plot_o_N_{alg2}.pdf, ...
  threshold_comparison.pdf       # all algorithms on one plot (anchor operator)
  anchor_s2_constraint_range_vs_threshold.pdf
```

Each `csfit_o_*_{alg}.json` must include at least:

```json
{
  "fit_intercept_fixed": true,
  "f0_label": "f5",
  "sigma0_after_cut_pb": 0.0012,
  "csfit_sm": 0.0012,
  "csfit_int": 0.034,
  "csfit_np": 1.8,
  "fit_model": "sigma(f)=sigma0_after_cut+f*csfit_int+f^2*csfit_np"
}
```

`csfit_sm` is retained only as a backward-compatible alias for
`sigma0_after_cut_pb`; it must equal the algorithm's accepted shared-`f5`
background value.

## Validation

Relevant invariants:
[`workflow-invariants.md`](workflow-invariants.md) Selection Scope,
Publication Data, Actual Event Counts, and Execution Continuity.

- `csfit_sm > 0`
- `csfit_sm` or `sigma0_after_cut` equals the accepted shared-`f5` background
  value and is not a fitted intercept
- The initial shared pool covers every claimed operator. A direct Phase 6 scan
  contributes one source; when Phase 6 recovery was used, include every
  successful attempt that actually entered its merged `f5` sample. Additional
  Phase 8 sources, if needed, are anchor `f5` samples only.
- Before three additional rounds, an unselected zero passing count remains null
  and is excluded from automatic width comparison. A zero at an algorithm's
  candidate final threshold requests the next anchor round. After three rounds,
  a remaining zero uses the half-event formula while preserving the observed
  count as zero.
- For one algorithm and threshold, every operator fit has the same
  `sigma0_after_cut_pb`
- `csfit_np >= 0`
- every `csfit_o_*_{alg}.json` records `fit_intercept_fixed=true` and
  `f0_label="f5"`
- Every scan point has positive `loaded_lhco_event_count`
- No efficiency or `cs_cut_x` denominator is requested `nev_scan` or a banner event count
- Every Phase 6 LHCO scan point has a corresponding public CSV under `results/data/phase8/csv/`
- Every algorithm has per-event scan score CSVs under `results/data/phase8/scores/{alg}/`
- Scan CSV row counts match `surviving_final_state_event_count`
- `dataset_summary.json` exists and every row has loaded event count,
  final-state-cut surviving count, raw cross-section, final-state-cut
  cross-section, and exact final-state cut expression
- Residual: `|cs_cut_x - csfit(f_x)| / csfit(f_x) < 0.5` for all points

## Phase Transition

Before calling `logger.phase_complete("8")`, satisfy
[`deliverables-phase8.md`](deliverables-phase8.md). Missing deliverables require
self-repair, not user interaction.

After all operators are fitted and all JSON files are written:

1. **Check validation rules immediately**: If any fit residual exceeds 0.5, flag warning but continue.
2. **If validation passes**: **proceed immediately to Phase 9 without stopping.**
3. **Do NOT**: summarize results, ask for confirmation, present options, or wait for user input.

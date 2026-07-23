# Phase 9: Compute Expected Coefficient Constraints

> **Contract priority**: Preserve the research objective and deliverables. Apply the technical-failure and `phase_fail` definitions in `SKILL.md`.

## Purpose

Compute expected Wilson-coefficient constraints at significance levels `S = 2, 3, 5`
for **all globally claimed operators**. Use `anchor_operator_only` by default.
Use `per_operator_best` when the user requested it in
`analysis_notes.additional_requirements`, or when the LLM finds scientific
evidence that the common strategy cannot produce a usable result for one or
more operators. This is an evidence-based research decision, not a fixed list of
scripted conditions.

## Prerequisite

Load the configuration:

```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir, run_dir)
logger.phase_start("9")
```

Read:

- `results/data/phase3/operator_claims.json`
- `results/data/phase3/anchor.json`
- `results/data/phase8/threshold_optimization.json`
- all Phase 8 fit files

## Formula

Use [`significance-reference.md`](significance-reference.md).

For each operator `o_n` and each significance `s in {2, 3, 5}`, solve
`S_stat = s`.

Preferred Asimov formula:

$$
S_{\mathrm{stat}} =
\sqrt{2 \left[ (N_{\mathrm{bg}} + N_{\mathrm{sig}})
\ln\left(1 + \frac{N_{\mathrm{sig}}}{N_{\mathrm{bg}}}\right)
- N_{\mathrm{sig}} \right]}
$$

where:

- `L` is the integrated luminosity converted to the inverse unit matching
  `csfit_*`
- In the default workflow, `csfit_*` is in pb and `config.luminosity` is in
  fb^-1, so `L = config.luminosity * 1000` in pb^-1
- `N_bg = L * sigma0_after_cut`, where `sigma0_after_cut` is the fixed
  Phase 8 shared-`f5` selected cross-section for the algorithm and threshold
- `N_sig = L * (f * csfit_int + f^2 * csfit_np)`
- `N_all = N_bg + N_sig`

The factor `1000` is only the `fb^-1 -> pb^-1` unit conversion. If any
cross-section fit is stored in another unit, convert luminosity to the matching
inverse unit before computing event counts.

Use the Asimov formula unless the run configuration explicitly selects another
formula. Do not use the older `N_sig / sqrt(N_bg + N_sig)` or
`N_sig / sqrt(N_bg)` approximations in Phase 9.

## Step 9.1: Select the Final Strategy

Relevant invariant:
[`workflow-invariants.md`](workflow-invariants.md) Selection Scope.

```python
with workflow_step(logger, "9", "select_anchor_algorithm",
                   inputs={"anchor": anchor, "num_algorithms": len(alg_data["anchor"])}):
```

The standard selection procedure uses only the anchor operator's Phase 8 fits:

1. Load the anchor operator from `anchor.json`; this is the first non-zero operator found in Phase 3.
2. For each trained algorithm, compute the `S=2` constraint interval for the anchor operator.
3. Select the algorithm with the narrowest `S=2` interval width.
4. Record full anchor intervals for all algorithms.

With `debug=false`, the LLM may judge a candidate scientifically unusable
because of inadequate event support, an invalid fit, or numerical instability,
and must repair the affected Phase 7-9 work when feasible. With `debug=true`, a
candidate is usable for workflow testing when it yields finite, internally
consistent, traceable fit and constraint outputs; repair technical or numerical
failure, but do not add full-size runs only to establish formal statistical
reliability. Among candidates usable under the selected `debug` setting, select
only by expected `S=2` coefficient-constraint interval width. Do not use AUC or
another classifier metric to rank or select the final strategy. Record the fixed
comparison method in `selection_criterion` and support candidate validity
decisions with `selection_rationale` and `selection_evidence`.

Output field:

```json
{
  "anchor_operator": "o_1",
  "anchor_model": "MODEL",
  "selected_algorithm": "RandomForestClassifier",
  "selected_threshold": 0.62,
  "selection_scope": "anchor_operator_only",
  "selection_criterion": "narrowest_anchor_S2_constraint_width",
  "selection_rationale": "The common anchor strategy gives usable fits and constraints for every claimed operator.",
  "selection_evidence": ["data/phase8/threshold_optimization.json"],
  "source_threshold_optimization_entry": "results/data/phase8/threshold_optimization.json:anchor.RandomForestClassifier"
}
```

For `anchor_operator_only`, the selected algorithm and its Phase 8 optimal
threshold form the single final strategy for every operator.

For `per_operator_best`, retain the top-level anchor comparison for provenance.
For every operator, let the LLM determine which recorded candidates are usable
under the selected `debug` setting, then choose the algorithm and evaluated
threshold with the narrowest expected `S=2` coefficient-constraint interval.
Fit validity, selected-event support, and numerical stability may exclude a
candidate or trigger repair, but cannot become an alternative ranking metric. Add:

```json
{
  "selection_scope": "per_operator_best",
  "selection_rationale": "The common strategy does not produce a usable result for o_2; operator-specific selections are used.",
  "selection_evidence": [
    "run_config.json:analysis_notes.additional_requirements",
    "data/phase8/csfit_o_2_RandomForestClassifier.json"
  ],
  "operator_selections": {
    "o_1": {
      "selected_algorithm": "RandomForestClassifier",
      "selected_threshold": 0.62,
      "selection_criterion": "narrowest_operator_S2_constraint_width"
    }
  }
}
```

The keys of `operator_selections` must exactly equal the Phase 3 claimed
operators. Re-aggregate existing results when they are sufficient. If the
evidence reveals a technical or scientific-validity problem in earlier work,
repair and rerun the affected Phase 7-9 producers rather than forcing an
existing result to fit the default procedure.

## Step 9.2: Compute Final Constraints

```python
with workflow_step(logger, "9", "compute_final_constraints",
                   inputs={"selected_algorithm": selected_algorithm,
                           "num_operators": len(operator_claims),
                           "significance_levels": [2, 3, 5]}):
```

For every globally claimed operator:

1. Load the Phase 8 fit for the strategy selected by `selection_scope`.
2. Verify the fit has `fit_intercept_fixed=true` and that its
   `sigma0_after_cut`/`csfit_sm` equals the matching algorithm record in
   `shared_f5_background.json`.
3. Solve constraints at `S = 2, 3, 5`.
4. Store normalized-coefficient intervals and physical-coefficient intervals if both are available.
5. Include the fixed intercept and fit coefficients used to compute the constraint.

## Step 9.3: Record Algorithm Comparison Data

Still record comparison data for transparency:

- anchor operator intervals for every algorithm
- optional per-operator S=2 intervals for non-selected algorithms
- AUC values from Phase 7 as descriptive diagnostics only; never use them to
  rank or select a final strategy
- a bar plot comparing the anchor operator's `S_stat = 2` coefficient interval
  width for every trained algorithm

This descriptive data is not the strategy-selection rule or final physical
result.

Save the plot to:

```
results/plots/anchor_s2_algorithm_constraint_bar.pdf
```

## Root Selection

For each operator and significance level:

- report the interval `[c_lower, c_upper]`
- solve `S_stat(c) = S`; the coefficient limits are real roots of this equation
- discard complex roots using [`significance-reference.md`](significance-reference.md)
- `c_upper` is the smallest positive real root
- `c_lower` is the largest negative real root
- if only symmetric constraints are supported by the solver, replace the solver
  or record the result as incomplete; do not silently force symmetry

Do not enforce a monotonicity rule that contradicts the chosen significance
definition. For discovery-style thresholds, larger `S` normally requires a larger
coefficient deviation.

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase9/...`). See `SKILL.md` Output Layout.

```
results/data/phase9/
  constraint_table.json
  constraint_table.csv
  algorithm_selection.json
results/plots/
  anchor_s2_algorithm_constraint_bar.pdf
```

`constraint_table.json` must include:

```json
{
  "selection_scope": "anchor_operator_only | per_operator_best",
  "anchor_operator": "o_1",
  "selected_algorithm": "RandomForestClassifier",
  "constraints": {
    "o_1": {
      "selected_algorithm": "RandomForestClassifier",
      "selected_threshold": 0.62,
      "S2": [-0.1, 0.1], "S3": [-0.2, 0.2], "S5": [-0.3, 0.3]
    }
  }
}
```

For `per_operator_best`, also copy the complete `operator_selections` object
from `algorithm_selection.json` into `constraint_table.json`. For
`anchor_operator_only`, the per-constraint algorithm and threshold fields are
recommended and must agree with the top-level selection when present.

Add a top-level independent review record to `constraint_table.json`:

```json
"numerical_validation": {
  "status": "pass",
  "method": "independent recalculation of every S=2,3,5 interval from the recorded fits, luminosity, units, and significance definition",
  "evidence_paths": ["data/phase9/constraint_table.json", "data/phase8/csfit_o_1_bdt.json"]
}
```

The LLM checks the actual method used by the project. If that method differs
from the bundled default, update or add the corresponding checker and record its
path, checksum, command, and output in `workflow.log`; do not weaken validation
only to hide a discrepancy.

`constraint_table.csv` contains exactly one row per claimed operator and at
least these columns:

```text
operator,selected_algorithm,selected_threshold,S2_lower,S2_upper,S3_lower,S3_upper,S5_lower,S5_upper
```

`algorithm_selection.json` must include:

```json
{
  "anchor_operator": "o_1",
  "selected_algorithm": "RandomForestClassifier",
  "selected_threshold": 0.62,
  "selection_criterion": "narrowest_anchor_S2_constraint_width",
  "selection_scope": "anchor_operator_only",
  "selection_rationale": "The common anchor strategy gives usable fits and constraints for every claimed operator.",
  "selection_evidence": ["data/phase8/threshold_optimization.json"],
  "source_threshold_optimization_entry": "results/data/phase8/threshold_optimization.json:anchor.RandomForestClassifier",
  "anchor_intervals_by_algorithm": {
    "RandomForestClassifier": {"S2": [-0.1, 0.1]},
    "LogisticRegression": {"S2": [-0.2, 0.2]}
  },
  "comparison_only_intervals": {
    "o_2": {
      "RandomForestClassifier": {"selected_threshold": 0.62, "S2": [-0.4, 0.4]},
      "LogisticRegression": {"selected_threshold": 0.54, "S2": [-0.3, 0.3]}
    }
  }
}
```

When `selection_scope=per_operator_best`, `comparison_only_intervals` must
contain every non-anchor operator and every trained algorithm usable under the
selected `debug` setting and considered for that operator. Each candidate
records the evaluated `selected_threshold` and its expected `S2` interval. If an algorithm cannot
produce an interval usable under the selected `debug` setting after repair,
omit it from this numeric comparison and explain the exclusion in
`selection_rationale` with an entry in `selection_evidence`. Select the narrowest recorded interval.

```python
logger.phase_complete("9")
```

## Validation

- The top-level `selected_algorithm` and `selected_threshold` record the anchor
  comparison result in both scopes.
- `anchor_operator_only` uses that same pair for every operator.
- `per_operator_best` records every operator in `operator_selections`, and each
  constraint row uses its recorded algorithm and threshold. Its rationale and
  evidence explain either the user request or why the common strategy was not
  usable under the selected `debug` setting.
- All reported intervals have real numeric lower and upper bounds.
- Fit coefficients and the fixed `f=0` intercept used for constraints are
  archived or referenced.
- Every consumed Phase 8 fit records `fit_intercept_fixed=true`; if an older
  three-parameter free-intercept fit is found, recompute Phase 8 fits before
  computing constraints.
- Per-operator choices may be final only when `selection_scope` is
  `per_operator_best`; otherwise they are labeled comparison-only. For each
  non-anchor operator, the selected candidate has the narrowest recorded finite
  `S2` interval among candidates usable under the selected `debug` setting.
- `results/plots/anchor_s2_algorithm_constraint_bar.pdf` exists and uses only
  anchor-operator `S=2` intervals.

## Phase Transition

Before calling `logger.phase_complete("9")`, satisfy
[`deliverables-phase9.md`](deliverables-phase9.md). Missing deliverables require
self-repair, not user interaction.

After `logger.phase_complete("9")` is called and `constraint_table.json` is written:

1. Check validation rules immediately and log warnings.
2. Proceed immediately to Phase 10 without stopping.
3. Do not summarize results, ask for confirmation, present options, or wait for user input.

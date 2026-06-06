# Phase 9: Compute Expected Coefficient Constraints

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE - once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose

Compute expected Wilson-coefficient constraints at significance levels `S = 2, 3, 5`
for **all globally claimed operators**. The production algorithm is selected once
from the first non-zero anchor operator, then applied to every operator.

Do not select a different final algorithm or threshold for each operator.

## Prerequisite

Load the configuration:

```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
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
- `N_bg = L * csfit_sm`
- `N_sig = L * (f * csfit_int + f^2 * csfit_np)`
- `N_all = N_bg + N_sig`

The factor `1000` is only the `fb^-1 -> pb^-1` unit conversion. If any
cross-section fit is stored in another unit, convert luminosity to the matching
inverse unit before computing event counts.

Use the Asimov formula unless the run configuration explicitly selects another
formula. Do not use the older `N_sig / sqrt(N_bg + N_sig)` or
`N_sig / sqrt(N_bg)` approximations in Phase 9.

## Step 9.1: Select the Anchor Algorithm

Relevant invariant:
[`workflow-invariants.md`](workflow-invariants.md) Single Selection Strategy.

```python
with workflow_step(logger, "9", "select_anchor_algorithm",
                   inputs={"anchor": anchor, "num_algorithms": len(alg_data["anchor"])}):
```

Use only the anchor operator's Phase 8 fits to select the production algorithm:

1. Load the anchor operator from `anchor.json`; this is the first non-zero operator found in Phase 3.
2. For each trained algorithm, compute the `S=2` constraint interval for the anchor operator.
3. Select the algorithm with the narrowest `S=2` interval width.
4. Record full anchor intervals for all algorithms.

Output field:

```json
{
  "anchor_operator": "o_1",
  "anchor_model": "MODEL",
  "selected_algorithm": "RandomForestClassifier",
  "selection_scope": "anchor_operator_only",
  "selection_criterion": "narrowest_anchor_S2_constraint_width"
}
```

The selected algorithm is the only algorithm used for the final physical
constraint table.

## Step 9.2: Compute Final Constraints

```python
with workflow_step(logger, "9", "compute_final_constraints",
                   inputs={"selected_algorithm": selected_algorithm,
                           "num_operators": len(operator_claims),
                           "significance_levels": [2, 3, 5]}):
```

For every globally claimed operator:

1. Load the Phase 8 fit for `selected_algorithm`.
2. Solve constraints at `S = 2, 3, 5`.
3. Store normalized-coefficient intervals and physical-coefficient intervals if both are available.
4. Include the fit coefficients used to compute the constraint.

## Step 9.3: Record Algorithm Comparison Data

Still record comparison data for transparency:

- anchor operator intervals for every algorithm
- optional per-operator S=2 intervals for non-selected algorithms
- AUC values from Phase 7

This comparison data is not the final physical result.

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

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase9/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase9/
  constraint_table.json
  constraint_table.csv
  algorithm_selection.json
```

`constraint_table.json` must include:

```json
{
  "selection_scope": "anchor_operator_only",
  "anchor_operator": "o_1",
  "selected_algorithm": "RandomForestClassifier",
  "constraints": {
    "o_1": {"S2": [-0.1, 0.1], "S3": [-0.2, 0.2], "S5": [-0.3, 0.3]},
    "o_2": {"S2": [-0.4, 0.4], "S3": [-0.5, 0.5], "S5": [-0.7, 0.7]}
  }
}
```

`algorithm_selection.json` must include:

```json
{
  "anchor_operator": "o_1",
  "selected_algorithm": "RandomForestClassifier",
  "selection_criterion": "narrowest_anchor_S2_constraint_width",
  "anchor_intervals_by_algorithm": {
    "RandomForestClassifier": {"S2": [-0.1, 0.1]},
    "LogisticRegression": {"S2": [-0.2, 0.2]}
  },
  "comparison_only_intervals": {
    "o_2": {
      "RandomForestClassifier": {"S2": [-0.4, 0.4]},
      "LogisticRegression": {"S2": [-0.3, 0.3]}
    }
  }
}
```

```python
logger.phase_complete("9")
```

## Validation

- `selected_algorithm` is chosen from the anchor operator only.
- `constraint_table.json` uses the same `selected_algorithm` for every operator.
- All reported intervals have real numeric lower and upper bounds.
- Fit coefficients used for constraints are archived or referenced.
- If per-operator best algorithms are computed for comparison, they are labeled comparison-only.

## Phase Transition

After `logger.phase_complete("9")` is called and `constraint_table.json` is written:

1. Check validation rules immediately and log warnings.
2. Proceed immediately to Phase 10 without stopping.
3. Do not summarize results, ask for confirmation, present options, or wait for user input.

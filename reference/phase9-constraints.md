# Phase 9: Compute Expected Coefficient Constraints

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Compute the final expected Wilson coefficient constraints at significance levels S = 2, 3, 5 using the **best algorithm** per operator. Constraints are computed for **ALL globally claimed operators** (`o_1` through `o_N`) from all models. Also generate comparison data to justify algorithm selection.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

# Initialize logger
from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
logger.phase_start("9")
```

Read `operator_claims.json` from Phase 3 to know the total number of global operators.

## Formula

For each operator `o_n` (where `n` is the global index), solve $S_{\mathrm{stat}} = s$ for $s \in \{2, 3, 5\}$.

**Preferred (Asimov formula, used in published papers):**

$$
S_{\mathrm{stat}} = \sqrt{2 \left[ (N_{\mathrm{bg}} + N_{\mathrm{sig}}) \ln\left(1 + \frac{N_{\mathrm{sig}}}{N_{\mathrm{bg}}}\right) - N_{\mathrm{sig}} \right]}
$$

where:
- $L = \ell \times 1000$ is the integrated luminosity in pb$^{-1}$
- $N_{\mathrm{bg}} = L \cdot \mathrm{csfit}_{\mathrm{sm}}$ is the number of SM background events
- $N_{\mathrm{sig}} = L \cdot (f \cdot \mathrm{csfit}_{\mathrm{int}} + f^{2} \cdot \mathrm{csfit}_{\mathrm{np}})$ is the number of signal events
- $N_{\mathrm{all}} = N_{\mathrm{bg}} + N_{\mathrm{sig}}$ is the total number of events

**Alternative (standard formula):**

$$
S_{\mathrm{stat}} = \frac{N_{\mathrm{sig}}}{\sqrt{N_{\mathrm{all}}}}
$$

Use the Asimov formula unless there is a specific reason to use the standard approximation.

## Best Algorithm Selection

```python
with workflow_step(logger, "9", "select_best_algorithms",
                   inputs={"num_operators": len(operator_claims), "num_algorithms": len(alg_data["anchor"])}):
```

Before computing final constraints, select the best algorithm per operator:

1. Load all algorithm fit results from Phase 8
2. For each algorithm, compute the full constraint interval $[f_{\min}, f_{\max}]$ at $S=2$
3. Select algorithm with **narrowest interval width** ($f_{\max} - f_{\min}$) as best
4. Record the full interval for every algorithm (needed for the comparison plot)

**Note**: The best algorithm may differ from the highest-AUC algorithm. This is expected and should be reported.

```python}})
```

## Final Constraint Computation

```python
with workflow_step(logger, "9", "compute_final_constraints",
                   inputs={"num_operators": len(operator_claims), "significance_levels": [2, 3, 5]}):
```

Using **only the best algorithm's** fit results, compute constraints for **all globally claimed operators** at $S = 2, 3, 5$.

## Root Selection

For each operator `o_n` and each significance $s$:
- The constraint interval is $[-c_{n_{s}}, c_{n_{s}}]$
- $c_{n_{s}}$ = smallest positive real root (upper bound)
- $-c_{n_{s}}$ = largest negative real root (lower bound, closest to 0)

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase9/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

Final constraint table (best algorithm only):

```
results/data/phase9/
  constraint_table.json          # best algorithm constraints for ALL operators
  constraint_table.csv
  algorithm_selection.json       # full intervals for all algorithms (for comparison plot)
```

Final constraint table format:

| Operator | Source Model | $S=2$ | $S=3$ | $S=5$ |
|----------|-------------|-------|-------|-------|
| o_1 | AQGCm_UFO | $[-c_{1_{s=2}}, c_{1_{s=2}}]$ | $[-c_{1_{s=3}}, c_{1_{s=3}}]$ | $[-c_{1_{s=5}}, c_{1_{s=5}}]$ |
| o_2 | AQGCm_UFO | $[-c_{2_{s=2}}, c_{2_{s=2}}]$ | $[-c_{2_{s=3}}, c_{2_{s=3}}]$ | $[-c_{2_{s=5}}, c_{2_{s=5}}]$ |
| o_3 | AQGCs_UFO | $[-c_{3_{s=2}}, c_{3_{s=2}}]$ | $[-c_{3_{s=3}}, c_{3_{s=3}}]$ | $[-c_{3_{s=5}}, c_{3_{s=5}}]$ |
| ... | ... | ... | ... | ... |

Algorithm selection record (must contain **full intervals**, not just widths):

```json
{
  "o_1": {
    "best_algorithm": "{alg_best}",
    "selection_criterion": "narrowest_constraint_width_S2",
    "intervals_by_algorithm": {
      "{alg_best}": {"S2": [-0.045, 0.048], "S3": [-0.032, 0.034], "S5": [-0.021, 0.023]},
      "{alg2}": {"S2": [-0.062, 0.065]},
      "{alg3}": {"S2": [-0.089, 0.092]}
    }
  },
  "o_2": { ... },
  "o_3": { ... }
}
```

**Note**: Only the best algorithm stores S3 and S5 intervals. Non-best algorithms store S2 only (used for the comparison plot). The `constraint_table.json` contains the final physical result (best algorithm at all significance levels for all operators).

```python
logger.phase_complete("9")
```

## Validation

- $c_{n_{s}} > 0$ for all operators and all $s$ (upper bound must be positive)
- $c_{n_{s=5}} < c_{n_{s=3}} < c_{n_{s=2}}}$ (constraints tighten with higher significance)

If monotonicity is violated, flag as constraint error.

## Phase Transition

After `logger.phase_complete("9")` is called and `constraint_table.json` is written:

1. **Check validation rules immediately**: If monotonicity is violated, flag warning but continue.
2. **If validation passes**: **proceed immediately to Phase 10 without stopping.**
3. **Do NOT**: summarize results, ask for confirmation, present options, or wait for user input.

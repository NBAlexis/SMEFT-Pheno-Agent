# Phase 6: Apply Selection and Fit Cross-Section

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
For each trained ML algorithm, apply its threshold to scan samples, fit the selected cross-section, and find the optimal threshold. In multi-model mode, threshold optimization uses the **anchor operator's** scan data only. The optimal threshold is then applied to ALL globally claimed operators.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

# Initialize logger
from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
logger.phase_start("6")
```

Read `anchor.json` from Phase 1. The anchor operator (`o_1` by convention) provides the scan data for threshold optimization.

## Step 6.1: Convert Scan LHCO to CSV

```python
with workflow_step(logger, "6", "convert_scan_lhco_to_csv",
                   inputs={"num_operators": len(operator_claims), "points_per_operator": 11}):
```

Convert all Phase 4 `.lhco` files to `.csv` using same feature extraction as Phase 5.


## Step 6.2: Score All Scan Points (Per Algorithm)

```python
with workflow_step(logger, "6", "score_scan_points",
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

Compute scores for all events in each scan point. The `compute_scores` function was produced in Phase 5 (Step 5.2.3) and handles normalization automatically for all algorithm types.

```python)})
```

## Step 6.3: Optimize Threshold Per Algorithm (using anchor operator)

### Reference Operator Selection

**Explicitly use the anchor operator** (from `anchor.json`, which is `o_1` by convention):

```python
# The anchor is always the first claimed operator
ref_op = "o_1"
```

Load the anchor operator's scan data: `np_o_1_f0.lhco` through `np_o_1_f10.lhco`.

### Event Count

Read `nev_scan` from `sm_baseline.json` (field `n_scan`). **Do NOT hardcode.**

```python
from scripts.read_results import read_sm_baseline
baseline = read_sm_baseline(config.workdir)
nev_scan = baseline["n_scan"]
```

### Threshold Scan Per Algorithm

For **each algorithm**, for each threshold in 51 points on [0, 1]:

```python
with workflow_step(logger, "6", f"optimize_threshold_{alg_name}",
                   inputs={"algorithm": alg_name, "num_thresholds": 51}):
```
1. Count passing events per scan point: `m_x` for each scan coefficient value `c_x` (11 points from `-c_{n_{scan}}` to `+c_{n_{scan}}`, including c=0)
2. Compute cut cross-section:
   ```
   cs_cut_x = cs_x * m_x / nev_scan
   ```
   where `cs_x` from banner (use canonical parser in [`madgraph-reference.md`](madgraph-reference.md)) and `nev_scan` from configuration.
3. Fit quadratic: `csfit(f) = csfit_sm + f*csfit_int + f^2*csfit_np`
4. Solve `S_stat = 2` with physics luminosity `L = luminosity * 1000`

   **Significance formula (Asimov, preferred):**
   ```
   N_bg = L * csfit_sm
   N_sig = L * (f * csfit_int + f^2 * csfit_np)
   S_stat = sqrt(2 * [(N_bg + N_sig) * ln(1 + N_sig/N_bg) - N_sig])
   ```

   Solve `S_stat(f) = 2` for `f`. The constraint interval is `[-c_{n_{s=2}}, c_{n_{s=2}}]` where `c_{n_{s=2}}` is the positive bound.
5. Record constraint width: `2 * c_{n_{s=2}}` (full interval width)

Select the threshold that **minimizes the constraint width `2 * c_{n_{s=2}}`** for each algorithm individually.


Record per algorithm:
```json
{
  "algorithm": "{alg_name}",
  "optimal_threshold": 0.62,
  "constraint_width_at_optimal": 0.045
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

## Step 6.4: Apply Each Algorithm's Optimal Threshold to All Operators

```python
with workflow_step(logger, "6", "apply_thresholds_all_operators",
                   inputs={"num_algorithms": len(alg_data["anchor"]), "num_operators": len(operator_claims)}):
```

For **each algorithm**, using **its own** optimal threshold from Step 6.3, repeat the quadratic fit for **EVERY globally claimed operator** (`o_1` through `o_N`).

For each operator `o_{g_idx}`:
- Load its scan data: `np_o_{g_idx}_f0.lhco` through `np_o_{g_idx}_f10.lhco`
- Apply the algorithm's threshold
- Fit quadratic and record coefficients

For each operator `o_{g_idx}`:
- Load its scan data: `np_o_{g_idx}_f0.lhco` through `np_o_{g_idx}_f10.lhco`
- Apply the algorithm's threshold
- Fit quadratic and record coefficients

```python * len(alg_data["anchor"])})
```

## Step 6.5: Plot

```python
with workflow_step(logger, "6", "plot_csfit_and_threshold_comparison",
                   inputs={"num_algorithms": len(alg_data["anchor"]), "num_operators": len(operator_claims)}):
```

For each algorithm and each operator: scatter `cs_cut_x` points + fitted curve `csfit(f)`.

Also plot **algorithm comparison**: for the anchor operator, show constraint width vs threshold for all algorithms on the same plot.

```python
logger.phase_complete("6")
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase6/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase6/
  threshold_optimization.json    # per-algorithm optimal thresholds (from anchor)
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
```

## Validation

- `csfit_sm > 0`
- `csfit_np >= 0`
- Residual: `|cs_cut_x - csfit(f_x)| / csfit(f_x) < 0.5` for all points

# Phase 6: Apply Selection and Fit Cross-Section

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
For each trained ML algorithm, apply its threshold to scan samples, fit the selected cross-section, and find the optimal threshold.

## Step 6.1: Convert Scan LHCO to CSV

Convert all Phase 4 `.lhco` files to `.csv` using same feature extraction as Phase 5.

## Step 6.2: Score All Scan Points (Per Algorithm)

For each algorithm in `algorithm_comparison.json`:

```python
clf = joblib.load(alg_info["algorithm_path"])
```

Compute scores for all events in each scan point.

## Step 6.3: Optimize Threshold Per Algorithm (using o1)

### Reference Operator Selection

**Explicitly use `o1`:**
```python
ref_op = "o1"
if ref_op not in nonzero_ops:
    ref_op = nonzero_ops[0]  # Fallback only
```

**Do NOT use `nonzero_ops[0]`** — dictionary order is unreliable.

### Event Count

Read `nev_scan` from `sm_baseline.json` (field `n_scan`). **Do NOT hardcode.**

### Threshold Scan Per Algorithm

For **each algorithm**, for each threshold in 51 points on [0, 1]:
1. Count passing events per scan point: `m0...m10`
2. Compute cut cross-section:
   ```
   cs_cut_x = cs_x * m_x / nev_scan
   ```
   where `cs_x` from banner (use canonical parser in [`madgraph-reference.md`](madgraph-reference.md)) and `nev_scan` from configuration.
3. Fit quadratic: `csfit(f) = csfit_sm + f*csfit_int + f^2*csfit_np`
4. Solve `S_stat = 2` with physics luminosity `L = luminosity * 1000`
5. Record `fmax - fmin`

Select the threshold that **minimizes `fmax - fmin`** for each algorithm individually.

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

For **each algorithm**, using **its own** optimal threshold from Step 6.3, repeat the quadratic fit for **every operator**.

## Step 6.5: Plot

For each algorithm and each operator: scatter `cs_cut_x` points + fitted curve `csfit(f)`.

Also plot **algorithm comparison**: for a representative operator, show constraint width vs threshold for all algorithms on the same plot.

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase6/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase6/
  threshold_optimization.json    # per-algorithm optimal thresholds
  csfit_o1_{alg1}.json, csfit_o1_{alg2}.json, ...
results/plots/
  csfit_plot_o1_{alg1}.pdf, csfit_plot_o1_{alg2}.pdf, ...
  threshold_comparison.pdf       # all algorithms on one plot
```

## Validation

- `csfit_sm > 0`
- `csfit_np >= 0`
- Residual: `|cs_cut_x - csfit(f_x)| / csfit(f_x) < 0.5` for all points

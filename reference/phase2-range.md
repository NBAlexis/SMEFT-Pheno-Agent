# Phase 2: Estimate Coefficient Range

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Determine the scan range `[-c1, c1]` for each non-zero operator.

## Step 2.1: Generate SM Baseline

Create SM process (`NP=0`), launch with all coefficients = 0.0, `nevents = {nev_phase2}`.

Extract `cs_sm` from `run_XX_tag_1_banner.txt` using the canonical banner parser in [`madgraph-reference.md`](madgraph-reference.md).

## Step 2.2: Compute Expected Event Counts

Known values from Phase 1:
- `cs_np` = cross-section at `c0` (pb)
- `c0` = coefficient value used in Phase 1
- `n_scan` = `{nev_scan}`

Effective luminosity:
```
L' = n_scan / cs_sm
```

Formulas:
```
N_SM = n_scan
N_NP(c1) = (c1^2 / c0^2) * (n_scan / cs_sm) * cs_np
S_stat(c1) = N_NP(c1) / sqrt(N_SM + N_NP(c1))
```

## Step 2.3: Solve for c1

Solve `S_stat(c1) = 2`:

```
N_NP^2 - 4*N_NP - 4*n_scan = 0
N_NP = 2 + 2*sqrt(1 + n_scan)
c1 = c0 * sqrt(N_NP * cs_sm / (n_scan * cs_np))
```

**Edge case:** If `cs_sm = 0`, abort. Verify process definition and energy.

Scan range: `[-c1, c1]`

Repeat for every non-zero operator.

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase2/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase2/
  coefficient_ranges.json    # {fi: [-c1, c1]} for each operator
  sm_baseline.json           # {cs_sm, n_scan, L_prime}
```

## Validation

- `cs_sm > 0`
- `c1 > 0` and finite
- `c1 < 1e3`

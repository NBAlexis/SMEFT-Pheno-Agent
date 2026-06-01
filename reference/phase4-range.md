# Phase 4: Estimate Coefficient Range

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Determine the unified scan range `[-c_{scan}, c_{scan}]` for all operators. The range is computed **once** using the **anchor operator** (from `anchor.json`), and the same `c_{scan}` applies to ALL globally claimed operators (i.e., `c_{n_{scan}} = c_{scan}` for all `n`).

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

from scripts.normalize_process_name import normalize_process_name
folder_base = normalize_process_name(config.process)

# Initialize logger
from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
logger.phase_start("4")
```

## Rationale

The coefficient range depends on the SM baseline cross-section and the NP cross-section at the test point. Using the anchor operator (the first sensitive operator found) provides a representative estimate. The same range is applied to all operators because:
- The scan range is primarily determined by the SM statistics (`cs_sm` and `nev_scan`)
- Using different ranges per operator would fragment the workflow
- A single unified range simplifies Phase 6 scanning and Phase 9 constraint computation

## Step 4.1: Generate SM Baseline

Create SM process using the **anchor model** (from `anchor.json`):

```
import model {anchor_model}
generate {process_name} NP=0
output {folder_base}_{anchor_model}_p4_SM
```

Launch with `set {block_name} {idx} 0.0` for all coefficients, `nevents = {nev_phase4}`. The `{block_name}` is obtained from `parse_param_card.py` output (e.g. `anoinputs`, `dim8`). See [`madgraph-reference.md`](madgraph-reference.md) Coefficient Block for syntax.

Extract `cs_sm` from `run_XX_tag_1_banner.txt` using the script:

```bash
python scripts/extract_cross_section.py {banner_path}
```

```python
with workflow_step(logger, "4", "generate_sm_baseline",
                   inputs={"anchor_model": anchor_model,
                           "nevents": config.locked_event_counts.nev_phase4}):
    # Write order, run MG5, extract cs_sm
    pass  # implementation here
```

## Step 4.2: Compute Expected Event Counts

Known values from Phase 3 (anchor operator):
- `cs_np` = cross-section at `c_{n_{default}}` (pb)
- `c_{n_{default}}` = default coefficient value used in Phase 3 for the anchor operator
- `n_scan` = `{nev_scan}`

Effective luminosity:
```
L' = n_scan / cs_sm
```

Formulas:
```
N_SM = n_scan
N_NP(c_{scan}) = (c_{scan}^2 / c_{n_{default}}^2) * (n_scan / cs_sm) * cs_np
S_stat(c_{scan}) = N_NP(c_{scan}) / sqrt(N_SM + N_NP(c_{scan}))
```

## Step 4.3: Solve for c_{scan}

Solve `S_stat(c_{scan}) = 2`:

```
N_NP^2 - 4*N_NP - 4*n_scan = 0
N_NP = 2 + 2*sqrt(1 + n_scan)
c_{scan} = c_{n_{default}} * sqrt(N_NP * cs_sm / (n_scan * cs_np))
```

**Critical:** The formula includes `c_{n_{default}}` (the default coefficient value used in Phase 3 for the anchor). Do NOT omit it — if `c_{n_{default}} = 1.0e-12` (typical gQGC_UFO default), omitting it produces `c_{scan}` values ~1e12× too large and unphysical cross-sections (up to 1e+19 pb).

**Edge case:** If `cs_sm = 0`, abort. Verify process definition and energy.

Scan range: `[-c_{scan}, c_{scan}]` — applies to **all** globally claimed operators (`c_{n_{scan}} = c_{scan}` for all `n`).

```python
with workflow_step(logger, "4", "compute_c_scan",
                   inputs={"cs_sm": cs_sm, "cs_np": cs_np,
                           "c_default": c_default,
                           "n_scan": config.locked_event_counts.nev_scan}):
    # Compute c_scan using the formula above
    import math
    N_NP = 2 + 2 * math.sqrt(1 + n_scan)
    c_scan = c_default * math.sqrt(N_NP * cs_sm / (n_scan * cs_np))
    if cs_sm == 0:
        raise ValueError("cs_sm is zero; aborting.")

    # Write outputs
    phase4_dir = os.path.join(config.workdir, "results", run_dir, "data", "phase4")
    os.makedirs(phase4_dir, exist_ok=True)
    with open(os.path.join(phase4_dir, "coefficient_ranges.json"), "w") as f:
        json.dump({"global": [-c_scan, c_scan]}, f, indent=2)
    with open(os.path.join(phase4_dir, "sm_baseline.json"), "w") as f:
        json.dump({"cs_sm": cs_sm, "n_scan": n_scan, "L_prime": n_scan / cs_sm,
                   "anchor_model": anchor_model, "c_scan": c_scan}, f, indent=2)

logger.phase_complete("4")
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase4/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase4/
  coefficient_ranges.json    # { "global": [-c_{scan}, c_{scan}] }  (single range for all operators)
  sm_baseline.json           # {cs_sm, n_scan, L_prime, anchor_model, c_scan}
```

## Validation

- `cs_sm > 0`
- `c_{scan} > 0` and finite
- `c_{scan} < 1e3`

## Phase Transition

After `logger.phase_complete("4")` is called and all JSON outputs are written:

1. **Check validation rules immediately**: If `cs_sm <= 0` or `c_{scan}` is invalid, abort with red flag.
2. **If validation passes**: **proceed immediately to Phase 5 without stopping.**
3. **Do NOT**: summarize results, ask for confirmation, present options, or wait for user input.

# Phase 2: Estimate Coefficient Range

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
from scripts.workflow_logger import WorkflowLogger
logger = WorkflowLogger(config.workdir)
logger.phase_start("2")
```

## Rationale

The coefficient range depends on the SM baseline cross-section and the NP cross-section at the test point. Using the anchor operator (the first sensitive operator found) provides a representative estimate. The same range is applied to all operators because:
- The scan range is primarily determined by the SM statistics (`cs_sm` and `nev_scan`)
- Using different ranges per operator would fragment the workflow
- A single unified range simplifies Phase 4 scanning and Phase 7 constraint computation

## Step 2.1: Generate SM Baseline

```python
logger.step_start("2", "generate_sm_baseline", inputs={"anchor_model": anchor_model, "nevents": config.nev_phase2})
```

Create SM process using the **anchor model** (from `anchor.json`):

```
import model {anchor_model}
generate {process_name} NP=0
output {folder_base}_{anchor_model}_p2_SM
```

Launch with `set {block_name} {idx} 0.0` for all coefficients, `nevents = {nev_phase2}`. The `{block_name}` is obtained from `parse_param_card.py` output (e.g. `anoinputs`, `dim8`). See [`madgraph-reference.md`](madgraph-reference.md) Coefficient Block for syntax.

Extract `cs_sm` from `run_XX_tag_1_banner.txt` using the script:

```bash
python scripts/extract_cross_section.py {banner_path}
```

```python
logger.step_complete("2", "generate_sm_baseline", outputs={"cs_sm": cs_sm, "banner_path": banner_path})
```

## Step 2.2: Compute Expected Event Counts

Known values from Phase 1 (anchor operator):
- `cs_np` = cross-section at `c_{n_{default}}` (pb)
- `c_{n_{default}}` = default coefficient value used in Phase 1 for the anchor operator
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

## Step 2.3: Solve for c_{scan}

```python
logger.step_start("2", "compute_c_scan", inputs={"cs_sm": cs_sm, "cs_np": cs_np, "c_default": c_default, "n_scan": config.nev_scan})
```

Solve `S_stat(c_{scan}) = 2`:

```
N_NP^2 - 4*N_NP - 4*n_scan = 0
N_NP = 2 + 2*sqrt(1 + n_scan)
c_{scan} = c_{n_{default}} * sqrt(N_NP * cs_sm / (n_scan * cs_np))
```

**Critical:** The formula includes `c_{n_{default}}` (the default coefficient value used in Phase 1 for the anchor). Do NOT omit it — if `c_{n_{default}} = 1.0e-12` (typical gQGC_UFO default), omitting it produces `c_{scan}` values ~1e12× too large and unphysical cross-sections (up to 1e+19 pb).

**Edge case:** If `cs_sm = 0`, abort. Verify process definition and energy.

Scan range: `[-c_{scan}, c_{scan}]` — applies to **all** globally claimed operators (`c_{n_{scan}} = c_{scan}` for all `n`).

```python
logger.step_complete("2", "compute_c_scan", outputs={"c_scan": c_scan})
logger.phase_complete("2")
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase2/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase2/
  coefficient_ranges.json    # { "global": [-c_{scan}, c_{scan}] }  (single range for all operators)
  sm_baseline.json           # {cs_sm, n_scan, L_prime, anchor_model, c_scan}
```

## Validation

- `cs_sm > 0`
- `c_{scan} > 0` and finite
- `c_{scan} < 1e3`

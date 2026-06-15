# Phase 4: Estimate Per-Operator Coefficient Ranges

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE - once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose

Determine one scan range `[-c_scan, c_scan]` for each globally claimed
operator. The SM baseline is generated once, but every operator gets its own
positive scan bound computed from that operator's Phase 3 cross-section and
default coefficient.

The anchor operator is used only to choose a valid model for the SM baseline
folder name. The anchor range must never be reused for non-anchor operators.

Hard rules:
- Compute one `c_scan` per globally claimed operator.
- Store ranges under `coefficient_ranges.json["operators"]["o_N"]`.
- Round each stored `c_scan` to two significant digits.
- Do not write a `"global"` range for new runs.

## Prerequisite

Load the configuration:

```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
logger.phase_start("4")
```

Read:

```
results/data/phase3/anchor.json
results/data/phase3/operator_claims.json
results/data/phase3/cross_sections.json
```

## Step 4.1: Generate SM Baseline

Generate the SM baseline through `scripts/run_mg5_config.py` using
`process_mode="pure_sm"` and `nevents = {nev_phase4}`. Read `cs_sm` from
`outputs[0].cross_section_pb` in the runner result JSON.

```json
{
  "mg5path": "/opt/MG5_aMC",
  "model": "AQGCm_UFO",
  "process": "mu+ mu- > a j j",
  "process_mode": "pure_sm",
  "run_label": "E10_L1000",
  "ebeam1": 5000.0,
  "ebeam2": 5000.0,
  "nevents": 10000,
  "delphes_card": "delphes_card_MuonColliderDet.tcl",
  "cutexperiment_path": "/opt/CutExperiment",
  "output_label": "phase4_sm",
  "output_dir": "/work/results/data/phase4",
  "result_json": "/work/results/data/phase4/sm_baseline_result.json"
}
```

Do not infer banner names or replace runner/parser failures with `cs_sm = 0`.

## Step 4.2: Compute Expected Event Counts Per Operator

For every claimed operator `o_N`, use values from Phase 3:

- `cs_np_N`: cross-section at the Phase 3 default coefficient, in pb
- `c_default_N`: default coefficient value used in Phase 3 for this operator
- `n_scan`: locked Phase 6 scan event count

Use the statistical-significance definition in
[`significance-reference.md`](significance-reference.md). Do not substitute
`N_sig / sqrt(N_bg + N_sig)` or `N_sig / sqrt(N_bg)`.

Effective luminosity for the range estimate:

```text
L_prime = n_scan / cs_sm
```

Per-operator approximation:

```text
N_SM = n_scan
N_NP_N(c) = (c^2 / c_default_N^2) * L_prime * cs_np_N
S_stat_N(c) = sqrt(2 * ((N_SM + N_NP_N(c)) * log(1 + N_NP_N(c) / N_SM) - N_NP_N(c)))
```

## Step 4.3: Solve Per-Operator Scan Bounds

For each claimed operator, solve `S_stat_N(c_scan_N) = 2` numerically. Phase 4
needs only the smallest positive real root because it defines a symmetric scan
range.

Use a monotonic positive-root solver such as bracketing plus bisection:

```text
N_SM = n_scan
L_prime = n_scan / cs_sm
N_NP_N(c) = (c^2 / c_default_N^2) * L_prime * cs_np_N
find the smallest positive real c_scan_N where S_stat_N(c_scan_N) = 2
```

**Critical:** The formula includes each operator's own `c_default_N`. Omitting
it can inflate scan ranges by many orders of magnitude.

**Edge cases:**
- If `cs_sm = 0`, abort. Verify process definition and beam energies.
- If any claimed operator has `cs_np_N <= 0` or missing Phase 3 metadata, abort
  Phase 4 with a concrete red flag after logging the offending operator.

```python
with workflow_step(logger, "4", "compute_operator_scan_ranges",
                   inputs={"cs_sm": cs_sm,
                           "num_operators": len(operator_claims),
                           "n_scan": config.locked_event_counts.nev_scan}):
    import json
    import math
    import os
    if cs_sm <= 0:
        raise ValueError("cs_sm is zero or negative; aborting.")

    n_scan = config.locked_event_counts.nev_scan
    N_SM = n_scan
    L_prime = n_scan / cs_sm

    def round_sig(x, digits=2):
        if x == 0:
            return 0.0
        return round(x, digits - 1 - int(math.floor(math.log10(abs(x)))))

    cross_sections_by_global = {
        str(entry["global_idx"]): entry
        for entry in cross_sections.values()
        if "global_idx" in entry
    }

    operator_ranges = {}
    for g_idx, claim in operator_claims.items():
        op_key = f"o_{g_idx}"
        if str(g_idx) not in cross_sections_by_global:
            raise ValueError(f"{op_key}: missing Phase 3 cross-section metadata.")

        xs = cross_sections_by_global[str(g_idx)]
        cs_np = float(xs["sigma"])
        c_default = float(xs["c_default"])
        if cs_np <= 0:
            raise ValueError(f"{op_key}: cs_np is non-positive; cannot estimate c_scan.")
        if c_default == 0:
            raise ValueError(f"{op_key}: c_default is zero; cannot estimate c_scan.")

        def n_np(c):
            return (c * c / (c_default * c_default)) * L_prime * cs_np

        def s_stat(c):
            ns = n_np(c)
            return math.sqrt(2.0 * ((N_SM + ns) * math.log(1.0 + ns / N_SM) - ns))

        lo, hi = 0.0, abs(c_default)
        while s_stat(hi) < 2.0:
            hi *= 2.0
        for _ in range(100):
            mid = 0.5 * (lo + hi)
            if s_stat(mid) < 2.0:
                lo = mid
            else:
                hi = mid

        c_scan = round_sig(hi, 2)
        operator_ranges[op_key] = {
            "range": [-c_scan, c_scan],
            "c_scan": c_scan,
            "model": claim["model"],
            "anoinput_idx": claim["anoinput_idx"],
            "name": claim["name"],
            "cs_np": cs_np,
            "c_default": c_default,
            "range_estimate": "operator_default_quadratic_np_approximation"
        }

    phase4_dir = os.path.join(config.workdir, "results", run_dir, "data", "phase4")
    os.makedirs(phase4_dir, exist_ok=True)
    with open(os.path.join(phase4_dir, "coefficient_ranges.json"), "w") as f:
        json.dump({"significant_digits": 2, "operators": operator_ranges}, f, indent=2)
    with open(os.path.join(phase4_dir, "sm_baseline.json"), "w") as f:
        json.dump({"cs_sm": cs_sm, "n_scan": n_scan, "L_prime": L_prime,
                   "anchor_model": anchor_model,
                   "significance_formula": "asimov",
                   "range_scope": "per_operator"}, f, indent=2)

logger.phase_complete("4")
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase4/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```text
results/data/phase4/
  coefficient_ranges.json
  sm_baseline.json
```

`coefficient_ranges.json` schema:

```json
{
  "significant_digits": 2,
  "operators": {
    "o_1": {
      "range": [-1.2e-12, 1.2e-12],
      "c_scan": 1.2e-12,
      "model": "AQGCm_UFO",
      "anoinput_idx": 1,
      "name": "fM0",
      "cs_np": 0.01,
      "c_default": 1e-12,
      "range_estimate": "operator_default_quadratic_np_approximation"
    }
  }
}
```

## Validation

- `cs_sm > 0`
- every claimed operator has exactly one entry in `coefficient_ranges.json`
- every `c_scan` is finite, positive, and `< 1e3`
- every stored `c_scan` is rounded to two significant digits
- no new-run `coefficient_ranges.json` contains a `"global"` range

## Phase Transition

After `logger.phase_complete("4")` is called and all JSON outputs are written:

1. Check validation rules immediately. If `cs_sm <= 0` or any operator range is invalid, abort with a red flag.
2. If validation passes, proceed immediately to Phase 5 without stopping.
3. Do not summarize results, ask for confirmation, present options, or wait for user input.

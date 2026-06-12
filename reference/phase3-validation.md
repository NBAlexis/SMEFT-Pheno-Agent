# Phase 3: Validate New Physics Impact (Multi-Model)

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE - once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Identify which SMEFT operators across **all specified models** actually affect the chosen process. Operators are globally deduplicated and continuously numbered. The first non-zero operator found across all models becomes the **anchor** for ML training and threshold optimization.

## Phase 3 Loop Completion Contract

The completion unit of Phase 3 is the full coefficient loop across all requested models. A single coefficient result is never a phase-level decision.

Required loop behavior:
1. Build the complete ordered coefficient list from every requested model.
2. Test each coefficient exactly once unless it is a duplicate already claimed from an earlier model.
3. Record every result, including `sigma = 0`.
4. Continue immediately after each coefficient, regardless of whether `sigma` is zero or non-zero.
5. Evaluate the zero-nonzero-operators red flag only after `tested_count == total_coefficients`.

Forbidden during the loop:
- Do not ask the user what to do.
- Do not test the SM baseline.
- Do not reduce `nev_phase3`.
- Do not stop because the first few coefficients have `sigma = 0`.
- Do not infer process insensitivity until every coefficient in every model has been tested.

Use `config.locked_event_counts.nev_phase3` for every Phase 3 launch. Never invent or resize the event count.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

# Initialize logger
from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
logger.phase_start("3")
```

All variables (`config.process`, `config.models`, `config.madgraph_path`, `config.energy`, etc.) are read from `config`.

## Global Operator Deduplication Rules

1. **Iterate models in the order provided by the user** (e.g., `[model_A, model_B, ...]`)
2. **For each model**, test all anoinput coefficients individually
3. **Claim an operator** (assign it a global index) **only if**:
   - Its cross-section `sigma > 0` (it affects the process)
   - Its name has **not** been claimed by an earlier model
4. **Skip an operator** if its name was already claimed by an earlier model (same operator name in a later model is considered a duplicate)
5. **Global continuous numbering**: claimed operators are numbered `o_1, o_2, ..., o_N` in the order they are first encountered

## Data Structures

### `claimed` dictionary
Maps operator name -> source model name:
```python
claimed = {
    "fS0": "AQGCm_UFO",
    "fS1": "AQGCm_UFO",
    "fM0": "AQGCs_UFO",
    ...
}
```

### `operator_claims.json`
Maps global index -> operator metadata:
```json
{
  "1": {"model": "AQGCm_UFO", "anoinput_idx": 1, "name": "fS0"},
  "2": {"model": "AQGCm_UFO", "anoinput_idx": 2, "name": "fS1"},
  "3": {"model": "AQGCs_UFO", "anoinput_idx": 1, "name": "fM0"},
  ...
}
```

### `model_status` dictionary
Records per-model Feynman diagram generation status and detailed coefficient results:
```python
model_status = {
    "nTGC_UFO_11g1": {
        "has_feynman_diagrams": True,
        "num_coefficients": 14,
        "coefficients": {
            "C1": {"c_default": 1.0, "sigma": 0.0},
            "C2": {"c_default": 1.0, "sigma": 0.0},
            ...
        }
    },
    "nTGC_UFO_12g2": {
        "has_feynman_diagrams": False,
        "error": "NoDiagramException: ..."
    }
}
```

### `anchor`
The first non-zero operator encountered when iterating all models in order:
```python
anchor = {
    "global_idx": 1,
    "model": "AQGCm_UFO",
    "anoinput_idx": 1,
    "name": "fS0"
}
```

## Step 3.1: Iterate All Models

For each `model_name` in the user-provided model list (in order):

### Step 3.1.1 Create NP Process Directory and Discover Coefficients

Create the NP process through the config runner in `create_np` mode. This mode
creates the process, parses `param_card.dat`, writes the result JSON, and does
not launch events.

```json
{
  "mg5path": "/opt/MG5_aMC",
  "model": "AQGCm_UFO",
  "process": "mu+ mu- > a j j",
  "process_mode": "create_np",
  "result_json": "/work/results/data/phase3/AQGCm_UFO_create_np_result.json"
}
```

Run:

```bash
python scripts/run_mg5_config.py phase3_create_np_AQGCm_UFO.json
```

Read `available_coefficients` and `coefficient_block` from the result JSON.
If MG5 reports no Feynman diagrams during this NP process-creation step, treat
that model/process combination as a confirmed zero-contribution case: set
`model_status[model_name].has_feynman_diagrams = False`, record the MG5
stdout/stderr/error paths, assign no operators from that model, and continue to
the next user-provided model. Do not run the per-coefficient loop for a model
whose NP process has no diagrams. Abort only for setup failures such as a
missing UFO model, invalid MG5 path, or an unreadable result JSON.

### Step 3.1.2 Extract Coefficients from Runner Result

Read `coefficient_block` and `available_coefficients` from the
`create_np` result JSON. These fields are produced by `parse_param_card.py`
inside the runner.

**Validation:** If parsed names include `MZ`, `MW`, `WT` or values near 90,
the parser leaked into `Block mass`. Report this as a parser bug.

### Step 3.1.3 Test Each Coefficient Individually

**Execution key: do not stop inside the coefficient loop.**

> After testing one coefficient, continue immediately to the next coefficient
> regardless of whether the current cross-section is zero or non-zero. Do not
> run an SM baseline, inspect other models, report a red flag, or stop the
> workflow from inside this loop.

For each coefficient `fi` in this model:

1. Determine `c_{n_{default}}`: default from param_card, or `1.0` if default is `0.0`
2. Write a runner JSON using `process_mode="pure_np"`,
   `target_coefficient.index = idx`, `target_coefficient.value = c_default`,
   `coefficient_mode="explicit"`, and
   `nevents = config.locked_event_counts.nev_phase3`.
3. Run `python scripts/run_mg5_config.py {json_path}`. The runner creates the
   process/order internally, captures stdout/stderr, converts ROOT to LHCO,
   parses the banner, records actual LHCO count, and performs zero-cross-section
   double-checks when needed.
4. Read `sigma_i` from `outputs[0].cross_section_pb` in the result JSON. Any
   positive value, even `1e-10 pb`, means the operator couples to the process.
   Do not parse stdout, infer banner names, or replace a runner/parser failure
   with `0.0`.
   If the runner reports `sigma_i = 0`, accept it only after its zero-cross-section
   double-check confirms either a `0.0` banner or a missing banner, matching
   zero-cross-section MG5 logs, and no substantial LHE payload.
   This per-run double-check is separate from process creation: a no-diagram
   process-creation result is already a confirmed zero-contribution model and
   does not need banner/LHE evidence.
5. **Record result in `model_status`**: Always record the coefficient's
   `c_default`, `sigma_i`, result JSON path, stdout/stderr paths, and zero-check
   report if present.
6. **Deduplication check**:
   - If `sigma_i > 0` and `fi` NOT in `claimed`:
     - Assign next global index `g_idx`
     - `claimed[fi] = model_name`
     - `operator_claims[g_idx] = {"model": model_name, "anoinput_idx": idx, "name": fi}`
     - Record cross-section: `cross_sections[fi] = {"sigma": sigma_i, "c_default": c_default, "model": model_name, "global_idx": g_idx}`
     - If this is the first non-zero operator across all models, set it as `anchor`
   - If `sigma_i > 0` and `fi` IS in `claimed`, log the duplicate and do not assign a new global index.
   - If `sigma_i == 0`, exclude it only after the runner zero-cross-section double-check has confirmed it.
7. **Immediately proceed to the next coefficient. Do NOT pause, do NOT branch to other tasks.**

Runner JSON example:

```json
{
  "mg5path": "/opt/MG5_aMC",
  "model": "AQGCm_UFO",
  "process": "mu+ mu- > a j j",
  "process_mode": "pure_np",
  "operator": "C3",
  "target_coefficient": {"index": 3, "value": 1.0e-12},
  "coefficient_mode": "explicit",
  "energy_tev": 10,
  "nevents": 10000,
  "delphes_card": "delphes_card_MuonColliderDet.tcl",
  "cutexperiment_path": "/opt/CutExperiment",
  "output_label": "phase3_AQGCm_UFO_C3",
  "output_dir": "/work/results/data/phase3",
  "result_json": "/work/results/data/phase3/AQGCm_UFO_C3_result.json"
}
```

## Step 3.2: Write Global Metadata

After all models have been processed:

1. Write `operator_claims.json`
2. Write `cross_sections.json` (includes all tested operators, not just claimed ones)
3. Write `model_status.json` (per-model Feynman diagram status and full coefficient-cross-section table)
4. Write `anchor.json`:
```json
{
  "global_idx": 1,
  "model": "AQGCm_UFO",
  "anoinput_idx": 1,
  "name": "fS0"
}
```

```python
import json

with workflow_step(logger, "3", "write_global_metadata",
                   inputs={"num_claimed": len(operator_claims),
                           "num_tested": len(cross_sections)}):
    phase3_dir = os.path.join(config.workdir, "results", run_dir, "data", "phase3")
    os.makedirs(phase3_dir, exist_ok=True)
    with open(os.path.join(phase3_dir, "operator_claims.json"), "w") as f:
        json.dump(operator_claims, f, indent=2)
    with open(os.path.join(phase3_dir, "cross_sections.json"), "w") as f:
        json.dump(cross_sections, f, indent=2)
    with open(os.path.join(phase3_dir, "model_status.json"), "w") as f:
        json.dump(model_status, f, indent=2)
    with open(os.path.join(phase3_dir, "anchor.json"), "w") as f:
        json.dump(anchor if anchor else {}, f, indent=2)

logger.phase_complete("3")
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase3/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase3/
  operator_claims.json       # {global_idx: {model, anoinput_idx, name}}
  cross_sections.json        # {fi: {sigma, c_default, model, global_idx}} for all tested
  model_status.json          # {model: {has_feynman_diagrams, num_coefficients, coefficients: {fi: {c_default, sigma}}}}
  anchor.json                # {global_idx, model, anoinput_idx, name}
```

## Validation

| Check | Action on Failure |
|-------|-------------------|
| `generate` succeeds for every model | Abort and report MG5 error |
| At least one operator claimed globally | Abort: process insensitive to all provided models. **Before aborting, emit a full `model_status` report** (see below). |
| `anchor` is set | Abort: no non-zero operators found. **Before aborting, emit a full `model_status` report** (see below). |

## Zero Cross-Section Report (Required)

If **all** tested operators return `sigma = 0` (or if `anchor` is not set), the workflow MUST abort with a red flag. **Before aborting**, output a detailed report that includes:

1. **Per-model Feynman diagram status** (from `model_status.json`):
   - Model name
   - `has_feynman_diagrams`: `True` / `False`
   - If `False`, the MG5 error / exception that caused the failure

2. **For every model with `has_feynman_diagrams = True`**: a complete table of **all** coefficients tested, showing:
   - Operator name (e.g., `C1`, `C2`)
   - `c_default` value used
   - `sigma` (pb) - even if `0.0`

Example report format:

```
Phase 3 Complete - Zero Non- Zero Operators Found
==================================================

Model: nTGC_UFO_11g1
  has_feynman_diagrams: True
  num_coefficients: 14
  Results:
    C1   c_default=1.0e-12   sigma=0.0 pb
    C2   c_default=1.0e-12   sigma=0.0 pb
    ...
    C14  c_default=1.0e-12   sigma=0.0 pb

Model: nTGC_UFO_12g2
  has_feynman_diagrams: False
  error: NoDiagramException: No diagram found for mu+ mu- > a j j NP>0

RED FLAG: No operator claimed. Process is insensitive to all provided models.
```

This report is written to the log and to a file `results/data/phase3/phase3_report.txt` so the user can inspect the full result without re-running MG5.

## Prohibited Behaviors During Phase 3 (CRITICAL)

The following behaviors constitute a **critical violation** of the Execution Continuity rule and **MUST NOT occur** under any circumstances:

| Prohibited Behavior | Why It's Forbidden | Correct Action |
|---------------------|-------------------|----------------|
| **Stopping after the first (or any) coefficient returns sigma = 0** | A single zero cross-section is a valid physical result. The phase must complete before any red flag is checked. | Record the result and **immediately continue** to the next coefficient. |
| **Testing SM baseline (all coefficients = 0) during Phase 3** | SM baseline is a Phase 4 operation. Doing it in Phase 3 is a phase boundary violation. | Stay in the coefficient testing loop. SM baseline comes **after** all coefficients are tested. |
| **Skipping remaining coefficients because "the process seems insensitive"** | Insensitivity can only be determined after ALL coefficients are tested. | Test every coefficient in every model. No exceptions. |
| **Switching to the next model before finishing the current model** | Model order is preserved for deduplication. Incomplete testing corrupts the claimed operator list. | Finish all coefficients in the current model before moving to the next. |
| **Reporting red flags or asking the user mid-phase** | Red flags are checked **only after the phase completes**. | Complete the phase silently. Report findings at the phase boundary. |
| **Reimplementing `extract_cross_section()` instead of using `scripts/extract_cross_section.py`** | The canonical script handles MG5 v3.x `Integrated weight (pb)` and older formats correctly. A handwritten regex will miss v3.x banners, silently corrupt all cross-section data, and produce false zero-cross-section reports. | Always call `scripts/extract_cross_section.py` (or import `extract_cross_section` from it). Never write your own parser. |

> **Highest-priority loop rule:** If there are 10 coefficients, test all 10
> coefficients even if the first 9 return zero. Mid-loop stopping is forbidden.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Testing models in wrong order | Use user-provided order exactly |
| Claiming duplicate operators | Check `claimed` dict before assigning global index |
| Forgetting to include model in process dir name | Always prefix/suffix with model name to avoid collisions |
| Not setting anchor if first model has all-zero operators | Continue to next model; anchor is first non-zero across ALL models |

## Phase Transition

After `logger.phase_complete("3")` is called and all JSON outputs are written:

1. **Check validation rules immediately**: If `anchor` is not set, emit the Zero Cross-Section Report and abort.
2. **If validation passes** (at least one operator claimed, anchor is set): **proceed immediately to Phase 4 without stopping.**
3. **Do NOT**: summarize results, ask for confirmation, present options, or wait for user input. The workflow runs to completion automatically per [`SKILL.md`](../SKILL.md) SUPREME RULE.

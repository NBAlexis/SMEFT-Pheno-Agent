# Phase 1: Validate New Physics Impact (Multi-Model)

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Identify which SMEFT operators across **all specified models** actually affect the chosen process. Operators are globally deduplicated and continuously numbered. The first non-zero operator found across all models becomes the **anchor** for ML training and threshold optimization.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

# Derive process directory base name
from scripts.normalize_process_name import normalize_process_name
folder_base = normalize_process_name(config.process)

# Initialize logger
from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
logger.phase_start("1")
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
Maps operator name → source model name:
```python
claimed = {
    "fS0": "AQGCm_UFO",
    "fS1": "AQGCm_UFO",
    "fM0": "AQGCs_UFO",
    ...
}
```

### `operator_claims.json`
Maps global index → operator metadata:
```json
{
  "1": {"model": "AQGCm_UFO", "anoinput_idx": 1, "name": "fS0"},
  "2": {"model": "AQGCm_UFO", "anoinput_idx": 2, "name": "fS1"},
  "3": {"model": "AQGCs_UFO", "anoinput_idx": 1, "name": "fM0"},
  ...
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

## Step 1.1: Iterate All Models

For each `model_name` in the user-provided model list (in order):

### 1.1.1 Create NP Process Directory

Order file:
```
import model {model_name}
generate {process_name} NP>0
output {folder_base}_{model_name}_p1_NP
```

> **Process directory naming**: Include the model name to avoid conflicts when multiple models define the same process. Example: `ee_a_jj_AQGCm_UFO_p1_NP`.

Run and check return code. Abort on any MG5 error.

```python
with workflow_step(logger, "1", f"mg5_generate_np_{model_name}",
                   inputs={"model": model_name, "process": config.process}):
    order_path = os.path.join(config.workdir, "results", run_dir, "orders", f"order_{model_name}.txt")
    os.makedirs(os.path.dirname(order_path), exist_ok=True)
    with open(order_path, "w") as f:
        f.write(f"import model {model_name}\n")
        f.write(f"generate {config.process} NP>0\n")
        f.write(f"output {folder_base}_{model_name}_p1_NP\n")
    subprocess.run([os.path.join(config.madgraph_path, "bin", "mg5_aMC"), order_path],
                   cwd=config.madgraph_path, check=True)
```

### 1.1.2 Extract Coefficients from param_card.dat

Read the coefficient block from `{mg5path}/{folder_base}_{model_name}_p1_NP/Cards/param_card.dat`.

**Use the script** (do not reimplement):

```bash
python scripts/parse_param_card.py {param_card_path}
```

Or import in Python:
```python
from scripts.parse_param_card import parse_anoinputs
from scripts.workflow_logger import workflow_step

with workflow_step(logger, "1", f"parse_param_card_{model_name}",
                   inputs={"model": model_name}):
    param_card_path = os.path.join(config.madgraph_path,
                                   f"{folder_base}_{model_name}_p1_NP",
                                   "Cards", "param_card.dat")
    result = parse_anoinputs(param_card_path, scan_default=1.0e-12)
    block_name = result["block_name"]       # e.g. "anoinputs" or "dim8"
    coefficients = result["coefficients"]   # {"1": 1.0e-12, "2": 0.0, ...}
```

The script handles case-insensitive Block matching, scan syntax retention, and Block boundary detection.

**Validation:** If parsed names include `MZ`, `MW`, `WT` or values ~90, the parser leaked into `Block mass`. Report this as a parser bug.

### 1.1.3 Test Each Coefficient Individually

**执行锁 — 严禁中途停止：**

> **无论当前测试结果如何（零或非零），测试完一个系数后必须立即继续下一个系数。**
> **严禁在循环中途：测 SM 基线、检查其他模型、报告异常、或停止工作流。**
> **如果有 10 个算符，哪怕 9 个为 0 也必须测完 10 个算符。**

For each coefficient `fi` in this model:

1. Determine `c_{n_{default}}`: default from param_card, or `1.0` if default is `0.0`
2. Write launch order with `set {block_name} {idx} {c_{n_{default}}}` for `fi`, `set {block_name} {other_idx} 0.0` for all others, `nevents = {nev_phase1}`. See [`madgraph-reference.md`](madgraph-reference.md) Coefficient Block for the exact syntax.
   - `block_name` is obtained from `parse_param_card.py` output (`block_name` field), e.g., `anoinputs` or `dim8`.
3. Run MG5, check return code
4. Post-process: find latest `run_XX`, convert ROOT→LHCO, validate
5. Extract `sigma_i` from the run banner using the canonical `extract_cross_section()` function defined in [`madgraph-reference.md`](madgraph-reference.md). **Any positive cross-section** — even `1e-10 pb` — indicates the operator couples to the process. Only `sigma_i == 0` (or parse failure) should exclude an operator.
6. **Deduplication check**:
   - If `sigma_i > 0` and `fi` NOT in `claimed`: 
     - Assign next global index `g_idx`
     - `claimed[fi] = model_name`
     - `operator_claims[g_idx] = {"model": model_name, "anoinput_idx": idx, "name": fi}`
     - Record cross-section: `cross_sections[fi] = {"sigma": sigma_i, "c_default": c_{n_{default}}, "model": model_name, "global_idx": g_idx}`
       - Note: The JSON field is named `c_default` (no curly braces) for valid JSON key syntax. It corresponds to the coefficient value $c_{n_{default}}$ documented throughout the workflow.
     - If this is the **first** non-zero operator across all models, set it as `anchor`
   - If `sigma_i > 0` and `fi` IS in `claimed`:
     - Log: "Operator `{fi}` already claimed by `{claimed[fi]}`. Skipping duplicate from `{model_name}`."
     - Do NOT assign a global index
   - If `sigma_i == 0`: exclude (no claim)
7. **Immediately proceed to the next coefficient. Do NOT pause, do NOT branch to other tasks.**

```python
for idx, default_val in coefficients.items():
    fi = f"C{idx}"
    c_default = default_val if default_val != 0.0 else 1.0
    with workflow_step(logger, "1", f"test_coeff_{model_name}_{fi}",
                       inputs={"coefficient": fi, "c_default": c_default}):
        # Build and write launch order
        launch_order = os.path.join(config.workdir, "results", run_dir,
                                    "orders", f"launch_{model_name}_{fi}.txt")
        with open(launch_order, "w") as f:
            f.write(f"launch {folder_base}_{model_name}_p1_NP\n")
            for other_idx in coefficients:
                val = c_default if other_idx == idx else 0.0
                f.write(f"set {block_name} {other_idx} {val}\n")
            f.write(f"set nevents {nev_phase1}\n")
            f.write("done\n")

        # Run MG5
        subprocess.run([os.path.join(config.madgraph_path, "bin", "mg5_aMC"),
                        launch_order],
                       cwd=config.madgraph_path, check=True)

        # Extract cross-section from latest run banner
        # (post-processing and deduplication logic here)
```

## Step 1.2: Write Global Metadata

After all models have been processed:

1. Write `operator_claims.json`
2. Write `cross_sections.json` (includes all tested operators, not just claimed ones)
3. Write `anchor.json`:
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

with workflow_step(logger, "1", "write_global_metadata",
                   inputs={"num_claimed": len(operator_claims),
                           "num_tested": len(cross_sections)}):
    phase1_dir = os.path.join(config.workdir, "results", run_dir, "data", "phase1")
    os.makedirs(phase1_dir, exist_ok=True)
    with open(os.path.join(phase1_dir, "operator_claims.json"), "w") as f:
        json.dump(operator_claims, f, indent=2)
    with open(os.path.join(phase1_dir, "cross_sections.json"), "w") as f:
        json.dump(cross_sections, f, indent=2)
    with open(os.path.join(phase1_dir, "anchor.json"), "w") as f:
        json.dump(anchor if anchor else {}, f, indent=2)

logger.phase_complete("1")
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase1/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase1/
  operator_claims.json       # {global_idx: {model, anoinput_idx, name}}
  cross_sections.json        # {fi: {sigma, c_default, model, global_idx}} for all tested
  anchor.json                # {global_idx, model, anoinput_idx, name}
```

## Validation

| Check | Action on Failure |
|-------|-------------------|
| `generate` succeeds for every model | Abort and report MG5 error |
| At least one operator claimed globally | Abort: process insensitive to all provided models |
| `anchor` is set | Abort: no non-zero operators found |

## Prohibited Behaviors During Phase 1 (CRITICAL)

The following behaviors constitute a **critical violation** of the Execution Continuity rule and **MUST NOT occur** under any circumstances:

| Prohibited Behavior | Why It's Forbidden | Correct Action |
|---------------------|-------------------|----------------|
| **Stopping after the first (or any) coefficient returns σ = 0** | A single zero cross-section is a valid physical result. The phase must complete before any red flag is checked. | Record the result and **immediately continue** to the next coefficient. |
| **Testing SM baseline (all coefficients = 0) during Phase 1** | SM baseline is a Phase 2 operation. Doing it in Phase 1 is a phase boundary violation. | Stay in the coefficient testing loop. SM baseline comes **after** all coefficients are tested. |
| **Skipping remaining coefficients because "the process seems insensitive"** | Insensitivity can only be determined after ALL coefficients are tested. | Test every coefficient in every model. No exceptions. |
| **Switching to the next model before finishing the current model** | Model order is preserved for deduplication. Incomplete testing corrupts the claimed operator list. | Finish all coefficients in the current model before moving to the next. |
| **Reporting red flags or asking the user mid-phase** | Red flags are checked **only after the phase completes**. | Complete the phase silently. Report findings at the phase boundary. |

> **执行锁 — 最高优先级规则：**
> 如果有 10 个算符，哪怕 9 个为 0 也必须测完 10 个算符。中途停止是严格禁止的。

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Testing models in wrong order | Use user-provided order exactly |
| Claiming duplicate operators | Check `claimed` dict before assigning global index |
| Forgetting to include model in process dir name | Always prefix/suffix with model name to avoid collisions |
| Not setting anchor if first model has all-zero operators | Continue to next model; anchor is first non-zero across ALL models |

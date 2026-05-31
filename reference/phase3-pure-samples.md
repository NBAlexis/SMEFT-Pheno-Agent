# Phase 3: Generate Pure SM and Pure NP Samples

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Generate high-statistics pure samples for ML training. In multi-model mode, ML training is performed **once** using the **anchor operator only**. Therefore, only the anchor model's SM sample and the anchor operator's NP sample are needed.

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
logger.phase_start("3")
```

Read `anchor.json` from Phase 1 to determine the anchor model and anchor operator.

## Step 3.1: Pure SM Sample

```python
logger.step_start("3", "generate_sm_sample", inputs={"anchor_model": anchor_model, "nevents": config.nev_sm})
```

1. **Create SM process directory using the anchor model:**
   ```
   import model {anchor_model}
   generate {process_name} NP=0
   output {folder_base}_{anchor_model}_p3_SM
   ```
2. Copy Delphes card and dependencies
3. Launch with `set {block_name} {idx} 0.0` for all coefficients, `nevents = {nev_sm}`. The `{block_name}` is obtained from `parse_param_card.py` output. See [`madgraph-reference.md`](madgraph-reference.md) Coefficient Block for syntax.
4. Post-process (ROOT→LHCO, validate, clean large files)
5. Copy to results:
```
results/data/phase3/sm_banner.txt
results/data/phase3/sm.lhco
```

```python
logger.step_complete("3", "generate_sm_sample", outputs={"lhco_path": "results/data/phase3/sm.lhco"})
```

> **Multi-run note:** In multi-run mode, all `results/` paths above are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase3/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

## Step 3.2: Pure NP Sample (Anchor Operator Only)

```python
logger.step_start("3", "generate_np_anchor", inputs={"anchor_model": anchor_model, "anchor_operator": anchor_name, "c_scan": c_scan, "nevents": config.nev_np})
```

Generate the NP sample **only for the anchor operator**:

1. **Create NP process directory using the anchor model:**
   ```
   import model {anchor_model}
   generate {process_name} NP>0
   output {folder_base}_{anchor_model}_p3_NP
   ```
2. Launch with `set {block_name} {anchor_anoinput_idx} {c_{n_{scan}}}` for the anchor operator (from Phase 2 range `c_{scan}`), `set {block_name} {other_idx} 0.0` for all others, `nevents = {nev_np}`. The `{block_name}` is obtained from `parse_param_card.py` output. See [`madgraph-reference.md`](madgraph-reference.md) Coefficient Block for syntax.
3. Post-process
4. Copy to results:
```
results/data/phase3/np_anchor_banner.txt
results/data/phase3/np_anchor.lhco
```

```python
logger.step_complete("3", "generate_np_anchor", outputs={"lhco_path": "results/data/phase3/np_anchor.lhco"})
logger.phase_complete("3")
```

> **Note**: The NP sample is named `np_anchor` (not `np_o1`) to make it clear this is the anchor-specific training sample. The ML algorithms trained on this sample will be applied to ALL operators in later phases.

> **Multi-run note:** In multi-run mode, all `results/` paths above are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase3/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

## Validation

- `sm.lhco` must exist and be non-empty (abort if missing)
- `np_anchor.lhco` must exist and be non-empty (abort if missing)

# Phase 5: Generate Pure SM and Pure NP Samples

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
from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
logger.phase_start("5")
```

Read `anchor.json` from Phase 3 to determine the anchor model and anchor operator.
Read `coefficient_ranges.json` from Phase 4 and use only the anchor operator's
own range for the anchor NP training sample:
`anchor_c_scan = coefficient_ranges["operators"][f"o_{anchor_global_idx}"]["c_scan"]`.

## Step 5.1: Pure SM Sample

1. **Create SM process directory using the anchor model:**
   ```
   import model {anchor_model}
   generate {process_name} NP=0
   output {folder_base}_{anchor_model}_p5_SM
   ```
2. Copy Delphes card and dependencies
3. Launch with `set {block_name} {idx} 0.0` for all coefficients, `nevents = {nev_sm}`. The `{block_name}` is obtained from `parse_param_card.py` output. See [`madgraph-reference.md`](madgraph-reference.md) Coefficient Block for syntax.
4. Post-process (ROOT→LHCO, validate, clean large files)
5. Copy to results:
```
results/data/phase5/sm_banner.txt
results/data/phase5/sm.lhco
```

```python
with workflow_step(logger, "5", "generate_sm_sample",
                   inputs={"anchor_model": anchor_model,
                           "nevents": config.locked_event_counts.nev_sm}):
    # Required actions: write the MG5 order, run MG5, post-process ROOT to LHCO,
    # validate outputs, copy results, and log subprocess stdout/stderr paths.
```

> **Multi-run note:** In multi-run mode, all `results/` paths above are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase5/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

## Step 5.2: Pure NP Sample (Anchor Operator Only)

Generate the NP sample **only for the anchor operator**:

1. **Create NP process directory using the anchor model:**
   ```
   import model {anchor_model}
   generate {process_name} NP>0
   output {folder_base}_{anchor_model}_p5_NP
   ```
2. Launch with `set {block_name} {anchor_anoinput_idx} {anchor_c_scan}` for the anchor operator, where `anchor_c_scan` is read from the anchor operator's own Phase 4 range. Set `{block_name} {other_idx} 0.0` for all others, and use `nevents = {nev_np}`. The `{block_name}` is obtained from `parse_param_card.py` output. See [`madgraph-reference.md`](madgraph-reference.md) Coefficient Block for syntax.
3. Post-process
4. Copy to results:
```
results/data/phase5/np_anchor_banner.txt
results/data/phase5/np_anchor.lhco
```

```python
with workflow_step(logger, "5", "generate_np_anchor",
                   inputs={"anchor_model": anchor_model,
                           "anchor_operator": anchor_name,
                           "anchor_c_scan": anchor_c_scan,
                           "nevents": config.locked_event_counts.nev_np}):
    # Required actions: write the MG5 order, run MG5, post-process ROOT to LHCO,
    # validate outputs, copy results, and log subprocess stdout/stderr paths.

logger.phase_complete("5")
```

> **Note**: The NP sample is named `np_anchor` (not `np_o1`) to make it clear this is the anchor-specific training sample. The ML algorithms trained on this sample will be applied to ALL operators in later phases.

> **Multi-run note:** In multi-run mode, all `results/` paths above are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase5/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

## Validation

- `sm.lhco` must exist and be non-empty (abort if missing)
- `np_anchor.lhco` must exist and be non-empty (abort if missing)

## Phase Transition

After `logger.phase_complete("5")` is called and all LHCO files are copied:

1. **Check validation rules immediately**: If either LHCO file is missing, abort.
2. **If validation passes**: **proceed immediately to Phase 6 without stopping.**
3. **Do NOT**: summarize results, ask for confirmation, present options, or wait for user input.

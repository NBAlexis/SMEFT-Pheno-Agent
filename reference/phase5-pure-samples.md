# Phase 5: Generate Pure SM and Pure NP Samples

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Generate high-statistics pure samples. In multi-model mode, ML training is
performed **once** using the **anchor operator only**, but pure NP samples for
all globally claimed operators are still required for publication data and score
distribution plots.

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

Read `anchor.json` from Phase 3 to determine the anchor model and anchor
operator. Read `operator_claims.json` from Phase 3 and
`coefficient_ranges.json` from Phase 4. Each claimed operator uses its own
Phase 4 range:

```python
c_scan = coefficient_ranges["operators"][f"o_{global_idx}"]["c_scan"]
```

## Step 5.1: Pure SM Sample

1. **Create SM process directory using the anchor model:**
   ```
   import model {anchor_model}
   generate {process_name} NP=0
   output {folder_base}_{anchor_model}_p5_SM
   ```
2. Copy Delphes card and dependencies
3. Launch with `set {block_name} {idx} 0.0` for all coefficients, `nevents = {nev_sm}`. The `{block_name}` is obtained from `parse_param_card.py` output. See [`madgraph-reference.md`](madgraph-reference.md) Coefficient Block for syntax.
4. Post-process (ROOT→LHCO, validate, apply event-count recovery from
   [`madgraph-reference.md`](madgraph-reference.md), clean large files)
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

## Step 5.2: Pure NP Samples for All Claimed Operators

Generate one pure NP sample for **every globally claimed operator**. The anchor
operator's sample is used for ML training. Non-anchor pure NP samples are not
used for training or algorithm selection; they are publication artifacts for
CSV release, score-distribution histograms, and manuscript evidence.

For each operator `o_{g_idx}`:

1. **Create NP process directory using that operator's source model:**
   ```
   import model {operator_model}
   generate {process_name} NP>0
   output {folder_base}_{operator_model}_p5_NP_o_{g_idx}
   ```
2. Launch with `set {block_name} {anoinput_idx} {c_scan}` for that operator,
   where `c_scan` is read from that operator's own Phase 4 range. Set all other
   Wilson coefficients in the same UFO coefficient block to `0.0`, and use
   `nevents = {nev_np}`. The `{block_name}` is obtained from
   `parse_param_card.py` output. See [`madgraph-reference.md`](madgraph-reference.md)
   Coefficient Block for syntax.
3. Post-process and apply event-count recovery from
   [`madgraph-reference.md`](madgraph-reference.md)
4. Copy to results:
```
results/data/phase5/np_o_{g_idx}_banner.txt
results/data/phase5/np_o_{g_idx}.lhco
```

For compatibility with Phase 7 training, also write an anchor alias:

```
results/data/phase5/np_anchor_banner.txt
results/data/phase5/np_anchor.lhco
results/data/phase5/event_count_recovery.json
```

The alias must point to the same physics sample as
`np_o_{anchor_global_idx}.lhco`; do not launch a duplicate anchor run merely to
create the alias.

```python
for op_key, claim in operator_claims.items():
    with workflow_step(logger, "5", f"generate_np_{op_key}",
                       inputs={"model": claim["model"],
                               "operator": claim["name"],
                               "c_scan": coefficient_ranges["operators"][op_key]["c_scan"],
                               "nevents": config.locked_event_counts.nev_np}):
        # Required actions: write the MG5 order, run MG5, post-process ROOT to
        # LHCO, validate outputs, copy results, and log subprocess stdout/stderr
        # paths.

logger.phase_complete("5")
```

> **Note**: `np_anchor` is an alias for the anchor operator's `np_o_{g_idx}`
sample. Training uses only this anchor alias. Histogram and public-data outputs
must include every `np_o_{g_idx}` sample.

> **Multi-run note:** In multi-run mode, all `results/` paths above are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase5/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

## Validation

Relevant invariants:
[`workflow-invariants.md`](workflow-invariants.md) Publication Data and
Execution Continuity.

- `sm.lhco` must exist and be non-empty (abort if missing)
- `np_o_{g_idx}.lhco` must exist and be non-empty for every globally claimed operator (abort if missing)
- `np_anchor.lhco` must exist and be non-empty, and must match the anchor operator sample (abort if missing)
- `event_count_recovery.json` records requested and actual LHCO counts, recovery attempts, and selected output paths for SM and every pure-NP sample
- No sample with actual LHCO count below `10%` of requested `nevents` may pass validation unless the full recovery ladder has been attempted and the remaining deficiency is recorded as a red flag

## Phase Transition

After `logger.phase_complete("5")` is called and all LHCO files are copied:

1. **Check validation rules immediately**: If any required LHCO file is missing, abort.
2. **If validation passes**: **proceed immediately to Phase 6 without stopping.**
3. **Do NOT**: summarize results, ask for confirmation, present options, or wait for user input.

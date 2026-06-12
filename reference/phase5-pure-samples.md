# Phase 5: Generate Pure SM and Pure NP Samples

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE - once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Phase 5 can be long-running because it produces pure NP samples for every
globally claimed operator. Runtime length is not a reason to ask whether to
continue, reduce event counts, or skip non-anchor samples.

Generate high-statistics pure samples. In multi-model mode, ML training is
performed **once** using the **anchor operator only**, but pure NP samples for
all globally claimed operators are still required for publication data and score
distribution plots.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

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

1. Build a `scripts/run_mg5_config.py` JSON with `process_mode="pure_sm"`,
   `nevents = {nev_sm}`, and output label `sm`.
2. Run it through the event-count recovery wrapper when the loaded LHCO count is
   below the recovery threshold.
3. Post-processing is runner-owned: Delphes card setup, ROOT-to-LHCO conversion,
   banner parsing, stdout/stderr capture, and actual LHCO counting are recorded
   in the result JSON.
4. Apply event-count recovery from [`event-count-recovery.md`](event-count-recovery.md), then clean large files.
5. Copy to results:
```
results/data/phase5/sm_banner.txt
results/data/phase5/sm.lhco
```

```python
with workflow_step(logger, "5", "generate_sm_sample",
                   inputs={"anchor_model": anchor_model,
                           "nevents": config.locked_event_counts.nev_sm}):
    # Required action: run scripts/run_mg5_config.py (or recovery wrapper)
    # from a JSON config and record the result JSON/stdout/stderr paths.
```

> **Multi-run note:** In multi-run mode, all `results/` paths above are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase5/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

## Step 5.2: Pure NP Samples for All Claimed Operators

Generate one pure NP sample for **every globally claimed operator**. The anchor
operator's sample is used for ML training. Non-anchor pure NP samples are not
used for training or algorithm selection; they are publication artifacts for
CSV release, score-distribution histograms, and manuscript evidence.

For each operator `o_{g_idx}`:

1. Build a `scripts/run_mg5_config.py` JSON using that operator's source model,
   `process_mode="pure_np"`, `target_coefficient.index = anoinput_idx`,
   `coefficient_mode="c_scan"`, that operator's own Phase 4 `c_scan`, and
   `nevents = {nev_np}`.
2. The runner sets only that target coefficient nonzero and sets the other
   coefficients in the same UFO coefficient block to `0.0`.
3. Post-process and apply event-count recovery from
   [`event-count-recovery.md`](event-count-recovery.md)
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
create the alias. Record `alias_for`, the source path, and the alias path in
Phase 5 metadata, and verify the aliased LHCO with the count helper.

```python
for op_key, claim in operator_claims.items():
    with workflow_step(logger, "5", f"generate_np_{op_key}",
                       inputs={"model": claim["model"],
                               "operator": claim["name"],
                               "c_scan": coefficient_ranges["operators"][op_key]["c_scan"],
                               "nevents": config.locked_event_counts.nev_np}):
        # Required action: run scripts/run_mg5_config.py (or recovery wrapper)
        # from a JSON config and record the result JSON/stdout/stderr paths.

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
- Apply [`event-count-recovery.md`](event-count-recovery.md): no sample with actual LHCO count below `10%` of requested `nevents` may pass validation unless recovery has been attempted and the remaining deficiency is recorded as a red flag

## Phase Transition

After `logger.phase_complete("5")` is called and all LHCO files are copied:

1. **Check validation rules immediately**: If any required LHCO file is missing, abort.
2. **If validation passes**: **proceed immediately to Phase 6 without stopping.**
3. **Do NOT**: summarize results, ask for confirmation, present options, or wait for user input.

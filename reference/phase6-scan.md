# Phase 6: Generate SM+NP Coefficient Scan Samples

> **Contract priority**: Preserve the research objective and deliverables. Apply the technical-failure and `phase_fail` definitions in `SKILL.md`.

## Purpose

Generate one MG5 scan launch per globally claimed operator. Each operator uses
its own Phase 4 `c_scan` and is scanned in its source model. Output filenames
use global numbering (`o_1`, `o_2`, ...) to keep all downstream phases aligned.

Do not precompute the 11 coefficient values. Use MG5 scan syntax:

```text
scan:[-c_scan + 0.2 * c_scan * n for n in range(11)]
```

where `c_scan` is replaced by the operator-specific numeric value from Phase 4.

## Long-Run Lock

Phase 6 is expected to be expensive. Runs lasting 4-8 hours, several days,
several weeks, or more than two months are acceptable and must not be treated as
abnormal.

Forbidden behavior:
- Do not stop with messages such as "impractical in an interactive session",
  "too long", or "estimated runtime is unacceptable".
- Do not ask whether to continue, split the scan, reduce event counts, enable
  debug mode, drop operators, or reduce the scan grid because of runtime.
- Do not treat slow MG5 convergence, large HEPMC/ROOT files, or long
  Delphes/root2lhco conversion as a technical failure requiring recovery.
- Do not summarize intermediate progress and wait for user input.

Required behavior when the foreground session is not suitable:
1. Start or continue a durable job on the selected execution target with
   `scripts/durable_exec.py`, `tmux`, `screen`, `nohup`, `systemd-run`, or the
   local batch scheduler. Native Windows is not a valid local MG5 target.
2. Write durable progress state under `results/data/phase6/`:
   - `scan_manifest.json`: every required operator, model, `c_scan`, exact MG5
     scan expression, expected point count `11`, and expected output labels
     `f0` through `f10`.
   - `phase6_progress.json`: an `operators` object with exactly every Phase 3
     `o_N` key. Each value contains `status` (`pending`, `running`,
     `failed_retrying`, or `completed`) and `completed_labels`. A completed
     operator lists `f0` through `f10` in order.
3. Continue monitoring or resume from the manifest. Partial completion is a
   checkpoint, not a stop condition.
4. Log time estimates only as diagnostics. They must not alter `nev_scan`,
   operators, models, scan expressions, or transitions.

## Prerequisite

Load the configuration:

```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir, run_dir)
logger.phase_start("6")
```

Read:

```text
results/data/phase3/operator_claims.json
results/data/phase5/np_o_N_result.json
results/data/phase4/coefficient_ranges.json
results/data/phase4/sm_baseline_result.json
```

From `coefficient_ranges.json`, read each operator's own range:

```python
op_key = f"o_{g_idx}"
c_scan = coefficient_ranges["operators"][op_key]["c_scan"]
```

Do not use the anchor operator's range for any other operator.

Before launching the first scan, create:

```python
phase6_dir = os.path.join(config.workdir, "results", "data", "phase6")
os.makedirs(phase6_dir, exist_ok=True)
manifest_path = os.path.join(phase6_dir, "scan_manifest.json")
progress_path = os.path.join(phase6_dir, "phase6_progress.json")
```

`scan_manifest.json` records scan expressions and expected labels; it does not
need the 11 numeric coefficient values.

Write progress atomically after each state change. Before Phase 6 completion,
every operator status must be `completed` and its `completed_labels` must be
exactly `f0` through `f10`; file existence alone is not a completed state.

## Critical Rules: Fresh Retry After Failure

- Never delete files from an existing `run_XX` and re-launch.
- Never run `launch` on a process directory with already processed or modified runs.
- If a scan attempt fails, treat that process directory as abandoned:
  1. Rename the process directory to a `_broken_{timestamp}` suffix without
     deleting ROOT, HEPMC, logs, cards, banners, or other diagnostic files.
  2. Inspect and preserve the files needed to diagnose the failure.
  3. Create a fresh process directory and re-run from scratch.
- "Abandoned" means renamed for later cleanup/audit, not deleted. Do not delete
  the process directory; deleting directories can trigger approval prompts and
  break unattended execution.
- Event-count recovery is different: if MG5 succeeds but LHCO count is low,
  run another compatible attempt and merge LHCO outputs. Do not mark successful
  low-count attempts as `_broken_*`.
- Do not rename individual `run_XX` folders; this breaks run-number tracking.

## Step 6.1: Create Scan Process Directories

For each operator scan, the standard path is to write a runner JSON and call
`scripts/run_mg5_config.py` or `scripts/recover_lhco_count.py`. The runner creates the process directory,
writes MG5 orders internally, captures stdout/stderr, and records the chosen
process folder in the result JSON.

If this path fails, inspect the process, card dependencies, MG5 orders, and logs.
Repair the runner or use a custom process directory/order/launch implementation
that preserves the 11-point scan, weighted-order guard, naming schema, and full
result provenance.

Before each SM+NP scan process is created, call
`scripts/extract_weighted_order.py` on the Phase 4 pure-SM process folder and
this operator's Phase 5 pure-NP process folder, using the target MG5 UFO model
directory. Pass the returned `max_weighted_order` to the runner as
`weighted_order`. The runner will create the SM+NP process with
`WEIGHTED=w`, retrying automatically with old-MG5 `Weighted=w` if needed. Record
the script JSON path, `max_weighted_order`, and runner-selected keyword under
the operator entry in `scan_manifest.json` as `weighted_order_guard`.

If `extract_weighted_order.py` fails, preserve its complete error text. Report
the model directory and every inspected `SubProcesses/subproc.mg`,
`matrix1.ps`, and `coupling_orders.py` path. When a diagram uses an order absent
from the model hierarchy, name each missing order explicitly, for example
`Missing coupling-order hierarchies for: QCD`; do not return a generic
"Weighted failed" message. Repair the parser or model-path selection, or
compute the same conservative maximum weighted order manually from those files
and record the formula, input values, and reason in `weighted_order_guard`.
Do not guess an order silently, ask the user, or perform diagram-count judgment
in phase logic.

## Step 6.2: Launch Scan Per Operator

For each globally claimed operator `o_{g_idx}`:

```python
with workflow_step(logger, "6", f"scan_operator_o_{g_idx}",
                   inputs={"operator": f"o_{g_idx}", "model": model_name,
                           "anoinput_idx": anoinput_idx, "c_scan": c_scan}):
```

1. Look up its source model and anoinput index from `operator_claims.json`.
2. With the standard runner, use its fresh process directory and recorded path.
   A custom recovery may manage the directory explicitly but must never reuse a
   contaminated failed run and must record the chosen path.
3. Read this operator's own Phase 4 `c_scan`.
4. Build the MG5 scan expression without expanding the 11 values:

```python
op_key = f"o_{g_idx}"
c_scan = coefficient_ranges["operators"][op_key]["c_scan"]
c_scan_text = f"{c_scan:.2g}"  # Phase 4 already rounded c_scan to two significant digits.
scan_expression = f"[-{c_scan_text} + 0.2 * {c_scan_text} * n for n in range(11)]"
```

When using `scripts/run_mg5_config.py`, pass `c_scan` and let the script build
this expression. Do not pass a precomputed list of 11 coefficients.

Runner config:

```json
{
  "mg5path": "/opt/MG5_aMC",
  "model": "AQGCm_UFO",
  "process": "mu+ mu- > a j j",
  "process_mode": "scan",
  "operator": "o_3",
  "target_coefficient": {"index": 3},
  "c_scan": 1.2e-12,
  "weighted_order": 7,
  "run_label": "E10_L1000",
  "ebeam1": 5000.0,
  "ebeam2": 5000.0,
  "nevents": 1000000,
  "delphes_card": "delphes_card_MuonColliderDet.tcl",
  "cutexperiment_path": "/opt/CutExperiment",
  "output_prefix": "np_o_3",
  "output_dir": "/work/results/data/phase6",
  "result_json": "/work/results/data/phase6/np_o_3_scan_result.json"
}
```

Rules:
- Pass only the operator-specific rounded Phase 4 `c_scan`; the runner builds the MG5 scan expression internally.
- Pass the conservative `weighted_order` extracted from the Phase 4 SM and
  Phase 5 pure-NP process folders so SM `NP=0` diagrams are not dropped.
- Do not pass a precomputed list of 11 coefficients.
- The runner validates that scan mode creates exactly 11 runs and maps them to `f0` through `f10`.
- For every collider type, pass explicit `ebeam1` and `ebeam2` from the active
  `run_configurations` entry. Do not pass center-of-mass energy fields to the
  runner.
- Pass `run_label` from the active `run_configurations[*].run_dir` so the MG5
  process folder records the beam/luminosity configuration.
- Phase 6 scans contain only operators already confirmed non-zero in Phase 3.
  A missing scan banner, a zero scan banner cross-section, or fewer than 11
  scan runs is a run-output failure to retry, not a physics zero to accept.

Record in `scan_manifest.json`:

```json
{
  "o_1": {
    "model": "AQGCm_UFO",
    "anoinput_idx": 1,
    "c_scan": 1.2e-12,
    "scan_expression": "[-1.2e-12 + 0.2 * 1.2e-12 * n for n in range(11)]",
    "point_count": 11,
    "labels": ["f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10"],
    "weighted_order_guard": {
      "max_weighted_order": 7,
      "status": "pass",
      "sm_result_json": "results/data/phase4/sm_baseline_result.json",
      "np_result_json": "results/data/phase5/np_o_1_result.json",
      "weighted_order_json": "results/data/phase6/np_o_1_weighted_order.json",
      "runner_selected_keyword": "WEIGHTED"
    }
  }
}
```

## Run Tracking

Do not use `runs[-11:]` or handwritten run-folder discovery in phase code. The
runner records `run_folders`, output labels, copied LHCO paths, copied banner
paths, stdout/stderr paths, and loaded LHCO counts in the result JSON. Scan
mode is valid only when the runner reports exactly 11 runs.

## Failure Recovery: Retry Per Operator

If MG5 fails or ROOT-to-LHCO conversion fails for any operator scan:

1. Log the failure with operator name, model, process folder, return code, and
   stdout/stderr paths.
2. Update `phase6_progress.json` marking the current operator as
   `failed_retrying`.
3. Preserve ROOT/HEPMC, logs, cards, banners, metadata, and the directory until
   the failure has been diagnosed. Delete ROOT/HEPMC only during final cleanup
   after the relevant evidence and required outputs have been secured.
4. Rename the runner-created process directory to a `_broken_{timestamp}` suffix
   if the runner has not already done so.
5. Recreate a fresh process directory through the runner or an equivalent
   diagnosed recovery path.
6. Re-run the scan launch for the same operator.
7. Repeat while testing new evidence-based fixes. Stop only for explicit user
   instruction or documented proof that the frozen scan deliverables are
   impossible, not because the standard runner exhausted its own retries.

Each operator scan is an independent retry scope. An earlier operator's success
does not protect a later operator from needing its own retry.

## Step 6.3: Use Runner Outputs

Do not infer run folders, banner filenames, ROOT filenames, or LHCO filenames.
For a successful scan, read these fields from the runner result JSON:

- `run_folders`: exactly 11 run folders
- `outputs[*].label`: `np_o_{g_idx}_f0` through `np_o_{g_idx}_f10`
- `outputs[*].lhco_path`
- `outputs[*].banner_path`
- `outputs[*].cross_section_pb`
- `outputs[*].loaded_lhco_event_count`
- `launch.stdout_path` / `launch.stderr_path`

The runner converts ROOT to LHCO, copies banners/LHCO files to `output_dir`,
parses cross-sections, and records actual LHCO counts. Use global operator
index `o_{g_idx}` in `output_prefix`; do not use model-internal anoinput index
in filenames.

## Step 6.4: Event Count Recovery

After copying the 11 LHCO files for one operator, apply the event-count recovery
policy in [`event-count-recovery.md`](event-count-recovery.md).

For Phase 6, the recovery unit is the full operator scan. Use the recovery
orchestrator so every attempt is merged by scan-point label: all `f0` outputs
together, all `f1` outputs together, through `f10`. Do not choose one attempt
over another.

Write:

```text
results/data/phase6/event_count_recovery.json
```

with requested counts, actual LHCO counts, fractions, recovery profile enum,
attempt numbers, merged output paths, all source banners, and merged
cross-sections.

After all operators have been processed:

```python
logger.phase_complete("6")
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase6/...`). See `SKILL.md` Output Layout.

```text
results/data/phase6/
  scan_manifest.json
  phase6_progress.json
  event_count_recovery.json
  np_o_1_scan_result.json, ..., np_o_N_scan_result.json
  np_o_1_f0_banner.txt    np_o_1_f0.lhco
  ...
  np_o_1_f10_banner.txt   np_o_1_f10.lhco
  np_o_2_f0_banner.txt    np_o_2_f0.lhco
  ...
  np_o_N_f10_banner.txt   np_o_N_f10.lhco
```

Keep every `np_o_{g_idx}_scan_result.json`. Phase 10 uses these runner
manifests to locate process folders, banners, LHCO paths, cross-sections, and
representative Feynman diagrams.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Expanding 11 coefficient values in Python before launch | Use the MG5 `scan:[-c_scan + 0.2 * c_scan * n for n in range(11)]` expression |
| Using the anchor range for all operators | Read `coefficient_ranges["operators"][op_key]["c_scan"]` per operator |
| `runs[-11:]` heuristic | Use set-difference to identify new runs |
| Re-launching on existing runs | Preserve evidence, rename the process directory, create fresh |
| Using model-internal index in filename | Always use global index `o_{g_idx}` |
| Reusing a failed scan process directory | Create a fresh directory with the runner or equivalent custom orchestration and record it |
| Reusing a failed process folder | Rename it to `_broken_{timestamp}` and create a fresh process folder |
| Stopping because runtime is hours, weeks, or months | Start durable execution and continue/resume |
| Asking the user to reduce events or confirm continuation | Never ask during Phase 6; event counts are locked |
| Hand-checking Phase 6 diagram counts | Do not spend phase logic on diagram-count judgment; use `extract_weighted_order.py` and pass `weighted_order` to the runner |
| File named `!` containing conversion usage text | Call `convert_root_to_lhco.py` with correct args and log stdout/stderr instead of shell clobber redirection |
| Treating LHCO count below requested `nevents` as final failure | Use event-count recovery; a sample below `10%` cannot pass the Phase 6 delivery check |
| Using `hard_survey > 2` | Do not exceed `hard_survey = 2`; it is too slow for this workflow |

## Phase Transition

Before calling `logger.phase_complete("6")`, satisfy
[`deliverables-phase6.md`](deliverables-phase6.md). Missing deliverables require
self-repair, not user interaction.

After all operators are scanned and all LHCO files are copied:

1. Check validation immediately. If any scan point is missing, continue/resume/retry from `phase6_progress.json`; if any scan point has actual LHCO count below `10%` of `nev_scan`, complete the standard recovery ladder, diagnose its failures, and try contract-preserving alternatives. Final termination requires evidence that the frozen scan deliverable is impossible.
2. If validation passes, proceed immediately to Phase 7 without stopping.
3. Do not summarize results, ask for confirmation, present options, or wait for user input.

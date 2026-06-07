# Phase 6: Generate SM+NP Coefficient Scan Samples

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE - once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

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
  Delphes/root2lhco conversion as a red flag.
- Do not summarize intermediate progress and wait for user input.

Required behavior when the foreground session is not suitable:
1. Start or continue a durable job on the selected execution target with
   `scripts/durable_exec.py`, `tmux`, `screen`, `nohup`, `systemd-run`, or the
   local batch scheduler. Native Windows is not a valid local MG5 target.
2. Write durable progress state under `results/data/phase6/`:
   - `scan_manifest.json`: every required operator, model, `c_scan`, exact MG5
     scan expression, expected point count `11`, and expected output labels
     `f0` through `f10`.
   - `phase6_progress.json`: completed, running, failed/retrying, and pending
     units.
3. Continue monitoring or resume from the manifest. Partial completion is a
   checkpoint, not a stop condition.
4. Log time estimates only as diagnostics. They must not alter `nev_scan`,
   operators, models, scan expressions, or transitions.

## Prerequisite

Load the configuration:

```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

from scripts.normalize_process_name import normalize_process_name
folder_base = normalize_process_name(config.process)

from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
logger.phase_start("6")
```

Read:

```text
results/data/phase3/operator_claims.json
results/data/phase4/coefficient_ranges.json
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

## Critical Rules: Prevent tag_2 Corruption

- Never delete files from an existing `run_XX` and re-launch.
- Never run `launch` on a process directory with already processed or modified runs.
- If the entire process directory must be re-run:
  1. Remove large temporary files across all runs after required outputs are secured.
  2. Rename the process directory to a `_broken_{timestamp}` suffix.
  3. Create a fresh process directory and re-run from scratch.
- Do not rename individual `run_XX` folders; this breaks run-number tracking.
- If `tag_2` appears, the process directory was reused incorrectly.

## Step 6.1: Create Scan Process Directories

For each unique model that has at least one claimed operator, create one scan
process directory:

```python
with workflow_step(logger, "6", f"create_scan_dir_{model_name}",
                   inputs={"model": model_name}):
```

```text
import model {model_name}
generate {process_name}
output {folder_base}_{model_name}_p6
```

Multiple operators from the same model share the same
`{folder_base}_{model_name}_p6` directory.

## Step 6.2: Launch Scan Per Operator

For each globally claimed operator `o_{g_idx}`:

```python
with workflow_step(logger, "6", f"scan_operator_o_{g_idx}",
                   inputs={"operator": f"o_{g_idx}", "model": model_name,
                           "anoinput_idx": anoinput_idx, "c_scan": c_scan}):
```

1. Look up its source model and anoinput index from `operator_claims.json`.
2. Use the process directory `{folder_base}_{model_name}_p6`.
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

Launch order:

```text
launch {folder_base}_{model_name}_p6
detector = Delphes
analysis = OFF
0
set {block_name} {anoinput_idx} scan:{scan_expression}
set {block_name} {other_idx} 0.0
...
set ebeam1 = {ebeam_value}
set ebeam2 = {ebeam_value}
set nevents = {nev_scan}
0
```

Rules:
- Use `set {block_name} {lha_code} scan:[-c_scan + 0.2 * c_scan * n for n in range(11)]`, with the actual rounded Phase 4 `c_scan` substituted into the expression.
- Do not use bare `set {number} = scan:[...]`; MG5 silently ignores it.
- The coefficient block name is obtained from `parse_param_card.py`.
- The scan expression tells MG5 to generate the 11 runs.
- Compute `ebeam_value` in GeV using the named conversion
  `tev_to_gev = 1000.0`: `ebeam_value = energy_tev * tev_to_gev / 2`.
  The factor is only `1 TeV = 1000 GeV`.
- The trailing `0` confirms run-card settings and starts generation.

Record in `scan_manifest.json`:

```json
{
  "o_1": {
    "model": "AQGCm_UFO",
    "anoinput_idx": 1,
    "c_scan": 1.2e-12,
    "scan_expression": "[-1.2e-12 + 0.2 * 1.2e-12 * n for n in range(11)]",
    "point_count": 11,
    "labels": ["f0", "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10"]
  }
}
```

## Run Tracking

Do not use `runs[-11:]`. Use set-difference to track exactly which runs were
created by the current launch:

```python
events_dir = os.path.join(MG5PATH, PROC_SCAN, "Events")
existing = set(d for d in os.listdir(events_dir) if d.startswith("run_"))

with workflow_step(logger, "6", f"scan_launch_o_{g_idx}",
                   inputs={"order": order_path, "scan_expression": scan_expression}):
    subprocess.run([...])

all_runs = set(d for d in os.listdir(events_dir) if d.startswith("run_"))
new_runs = sorted(all_runs - existing, key=lambda x: int(x.split("_")[1]))
```

`new_runs` must contain exactly 11 runs.

## Failure Recovery: Retry Per Operator

If MG5 fails or ROOT-to-LHCO conversion fails for any operator scan:

1. Log the failure with operator name, model, process folder, return code, and
   stdout/stderr paths.
2. Update `phase6_progress.json` marking the current operator as
   `failed_retrying`.
3. Clean temporary ROOT/LHE/HEPMC files in the process directory after required
   debug outputs are secured.
4. Rename the process directory to `{folder_base}_{model_name}_p6_broken_{timestamp}`.
5. Recreate the process directory from scratch.
6. Re-run the scan launch for the same operator.
7. Repeat until success unless a proven unrecoverable error or explicit user
   stop occurs.

Each operator scan is an independent retry scope. An earlier operator's success
does not protect a later operator from needing its own retry.

## Step 6.3: Convert ROOT to LHCO

For each new run, convert the Delphes ROOT output to LHCO format.

Use the script; do not reimplement conversion:

```bash
python scripts/convert_root_to_lhco.py {mg5path} {folder_base}_{model_name}_p6 {run}
```

Or in Python:

```python
from scripts.convert_root_to_lhco import convert_root_to_lhco

for run in new_runs:
    convert_root_to_lhco(mg5path, f"{folder_base}_{model_name}_p6", run)
```

This produces `{run}.lhco` in the same Events directory.

## Step 6.4: Rename Output Files

Map each new run to `np_o_{g_idx}_f{index}` by run order:

```text
new_runs[0]  -> np_o_{g_idx}_f0_banner.txt,  np_o_{g_idx}_f0.lhco
new_runs[1]  -> np_o_{g_idx}_f1_banner.txt,  np_o_{g_idx}_f1.lhco
...
new_runs[10] -> np_o_{g_idx}_f10_banner.txt, np_o_{g_idx}_f10.lhco
```

Use global operator index `o_{g_idx}`, not model-internal anoinput index.

```python
for i, run in enumerate(new_runs):
    banner_path = os.path.join(events_dir, run, f"{run}_tag_1_banner.txt")
    run_lhco = os.path.join(events_dir, run, f"{run}.lhco")
    dest_banner = f"np_o_{g_idx}_f{i}_banner.txt"
    dest_lhco = f"np_o_{g_idx}_f{i}.lhco"
    # Copy banner and LHCO to results/data/phase6/.
```

## Step 6.5: Event Count Recovery

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

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase6/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```text
results/data/phase6/
  scan_manifest.json
  phase6_progress.json
  event_count_recovery.json
  np_o_1_f0_banner.txt    np_o_1_f0.lhco
  ...
  np_o_1_f10_banner.txt   np_o_1_f10.lhco
  np_o_2_f0_banner.txt    np_o_2_f0.lhco
  ...
  np_o_N_f10_banner.txt   np_o_N_f10.lhco
```

## Common Mistakes

| Mistake | Fix |
|---|---|
| Expanding 11 coefficient values in Python before launch | Use the MG5 `scan:[-c_scan + 0.2 * c_scan * n for n in range(11)]` expression |
| Using the anchor range for all operators | Read `coefficient_ranges["operators"][op_key]["c_scan"]` per operator |
| `runs[-11:]` heuristic | Use set-difference to identify new runs |
| Re-launching on existing runs | Remove large temps, rename the process directory, create fresh |
| Using model-internal index in filename | Always use global index `o_{g_idx}` |
| Creating one process dir per operator | Create one per model |
| `tag_2` ROOT files | Indicates an existing run was modified and re-launched |
| Stopping because runtime is hours, weeks, or months | Start durable execution and continue/resume |
| Asking the user to reduce events or confirm continuation | Never ask during Phase 6; event counts are locked |
| File named `!` containing conversion usage text | Call `convert_root_to_lhco.py` with correct args and log stdout/stderr instead of shell clobber redirection |
| Treating LHCO count below requested `nevents` as fatal | Use event-count recovery; only counts below `10%` after the full ladder are red flags |
| Using `hard_survey > 2` | Do not exceed `hard_survey = 2`; it is too slow for this workflow |

## Phase Transition

After all operators are scanned and all LHCO files are copied:

1. Check validation immediately. If any scan point is missing, continue/resume/retry from `phase6_progress.json`; if any scan point has actual LHCO count below `10%` of `nev_scan`, complete the event-count recovery ladder before declaring a red flag. Abort only for concrete unrecoverable filesystem, physics-generation, or exhausted-recovery errors.
2. If validation passes, proceed immediately to Phase 7 without stopping.
3. Do not summarize results, ask for confirmation, present options, or wait for user input.

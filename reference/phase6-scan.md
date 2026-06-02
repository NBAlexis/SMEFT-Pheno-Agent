# Phase 6: Generate SM+NP Coefficient Scan Samples

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Generate 11 scan points per **globally claimed operator** across the coefficient range `[-c_{n_{scan}}, c_{n_{scan}}]`. Each operator is scanned in its **source model** (the model that claimed it). Output filenames use **global numbering** (`o_1`, `o_2`, ...) to maintain consistency across all phases.

## Long-Run Lock

Phase 6 is expected to be expensive. Runs lasting 4-8 hours, several days, several weeks, or more than two months are acceptable and must not be treated as abnormal.

Forbidden behavior:
- Do not stop with messages such as "impractical in an interactive session", "too long", or "estimated runtime is unacceptable".
- Do not ask whether to continue, split the scan, reduce event counts, enable debug mode, drop operators, or reduce the 11-point scan grid because of runtime.
- Do not treat slow MG5 convergence, large HEPMC/ROOT files, or long Delphes/root2lhco conversion as a red flag.
- Do not summarize partial progress and wait for user input.

Required behavior when the foreground session is not suitable:
1. Start or continue a durable job on the selected execution target with `scripts/durable_exec.py`, `tmux`, `screen`, `nohup`, `systemd-run`, or the local batch scheduler.
   On native Windows, switch to the configured WSL2/SSH target for long MG5/Delphes jobs instead of relying on native Windows background execution.
2. Write a durable progress state under `results/data/phase6/`:
   - `scan_manifest.json`: all required `(operator, model, scan_index, coefficient)` units.
   - `phase6_progress.json`: completed, running, failed/retrying, and pending units.
3. Continue monitoring or resume from the manifest. Partial completion is a checkpoint, not a stop condition.
4. Log time estimates only as diagnostics. They must not alter `nev_scan`, operators, models, scan points, or transitions.

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
logger.phase_start("6")
```

Read `operator_claims.json` and `coefficient_ranges.json` from previous phases.

From `coefficient_ranges.json`, read the unified range: `c_{scan} = coefficient_ranges["global"][1]` (the positive bound). The same `c_{n_{scan}} = c_{scan}` applies to all operators.

Before launching the first scan, create the manifest:

```python
phase6_dir = os.path.join(config.workdir, "results", "data", "phase6")
os.makedirs(phase6_dir, exist_ok=True)
manifest_path = os.path.join(phase6_dir, "scan_manifest.json")
progress_path = os.path.join(phase6_dir, "phase6_progress.json")
```

`scan_manifest.json` must include every globally claimed operator and all 11 scan coefficients. `phase6_progress.json` must be updated after each scan point conversion/copy, and after each retry.

## Critical Rules — Prevent tag_2 Corruption

- **NEVER** delete files from an existing `run_XX` and re-launch
- **NEVER** run `launch` on a process directory with partially processed runs
- **If the entire process directory must be re-run** (e.g., scan corrupted, too many bad runs):
  1. Remove large temporary files across all runs to free disk: `find Events/run_*/ -name "*.root" -o -name "*.lhe.gz" -o -name "*.hepmc.gz" | xargs rm -f`
  2. Rename the process directory: `mv {folder_name} {folder_name}_broken`
  3. Create a fresh process directory and re-run from scratch
- Do **NOT** rename individual `run_XX` folders — this breaks run-number tracking
- If `tag_2` appears, you violated this rule

## Step 6.1: Create Scan Process Directories

For each **unique model** that has at least one claimed operator, create ONE scan process directory:

```python
with workflow_step(logger, "6", f"create_scan_dir_{model_name}",
                   inputs={"model": model_name}):
```

```
import model {model_name}
generate {process_name}
output {folder_base}_{model_name}_p6
```


> **Process directory naming**: `{folder_base}_{model_name}_p6` ensures each model has its own directory. Multiple operators from the same model share one directory.

## Step 6.2: Generate Scan Points Per Operator

For each globally claimed operator `o_{g_idx}` (from `operator_claims.json`):

```python
with workflow_step(logger, "6", f"scan_operator_o_{g_idx}",
                   inputs={"operator": f"o_{g_idx}", "model": model_name,
                           "anoinput_idx": anoinput_idx, "c_scan": c_scan}):
```

1. Look up its source model and anoinput index from `operator_claims.json`
2. Use the process directory `{folder_base}_{model_name}_p6`
3. Generate 11 scan points programmatically — **do not hand-compute the values**:

```python
c_scan = coefficient_ranges["global"][1]  # positive bound from Phase 4
coefficient_list = [-c_scan + 0.2 * c_scan * n for n in range(11)]
scan_values = ",".join(str(v) for v in coefficient_list)
```

Launch order (follows [`madgraph-reference.md`](madgraph-reference.md) Event Generation Order template):

```
launch {folder_base}_{model_name}_p6
detector = Delphes
analysis = OFF
0
set {block_name} {anoinput_idx} scan:[{scan_values}]
set {block_name} {other_idx} 0.0
...
set ebeam1 = {ebeam_value}
set ebeam2 = {ebeam_value}
set nevents = {nev_scan}
0
```

- `ebeam_value = energy * 1000 / 2` (GeV). See [`madgraph-reference.md`](madgraph-reference.md) Energy Assignment.
- Use `set {block_name} {lha_code} scan:[v1, v2, ...]` (not bare `set {number} = scan:[...]`, which MG5 silently ignores). The `{block_name}` is obtained from `parse_param_card.py` output.
- The scan syntax tells MG5 to generate one run per value.
- The trailing `0` confirms run card settings and starts generation.

### Run Tracking (Critical)

**Do NOT use `runs[-11:]`.** Use set-difference to track exactly which runs were created:

```python
events_dir = os.path.join(MG5PATH, PROC_SCAN, "Events")
existing = set(d for d in os.listdir(events_dir) if d.startswith("run_"))

with workflow_step(logger, "6", f"scan_launch_o_{g_idx}",
                   inputs={"order": order_path}):
    subprocess.run([...])  # MG5 launch command

all_runs = set(d for d in os.listdir(events_dir) if d.startswith("run_"))
new_runs = sorted(all_runs - existing, key=lambda x: int(x.split("_")[1]))
# new_runs contains exactly the runs from this launch
```

### Failure Recovery — Infinite Retry

If MG5 fails (non-zero exit code) or ROOT→LHCO conversion fails for any operator scan:

1. **Log the failure** with the operator name and error reason.
2. **Update `phase6_progress.json`** marking the current operator/scan unit as `failed_retrying`.
3. **Clean temporary files** in the process directory:
   ```bash
   find {mg5path}/{folder_base}_{model_name}_p6/Events/run_*/ \
       \( -name "*.root" -o -name "*.lhe.gz" -o -name "*.hepmc.gz" \) -delete
   ```
4. **Rename the process directory** to a broken suffix (preserve it for debugging):
   ```python
   import time
   broken_name = f"{folder_base}_{model_name}_p6_broken_{int(time.time())}"
   os.rename(f"{mg5path}/{folder_base}_{model_name}_p6",
             f"{mg5path}/{broken_name}")
   ```
5. **Do not ask the user what to do.** Do not print a stop prompt. The failure is handled by the retry loop unless an explicit user stop command was already received outside this phase logic.
6. **Recreate the process directory** from scratch:
   ```
   import model {model_name}
   generate {process_name}
   output {folder_base}_{model_name}_p6
   ```
7. **Re-run the scan launch** for the same operator.
8. **Repeat from step 1 until success.** Runtime length and repeated recoverable failures do not convert into a request for user input.

```python})
```

> **Critical**: This retry applies per-operator. An earlier operator's success does NOT protect a later operator from needing its own retry. Each operator scan is an independent retry scope.

## Step 6.3: Convert ROOT to LHCO

```python
with workflow_step(logger, "6", f"root_to_lhco_o_{g_idx}",
                   inputs={"num_runs": len(new_runs)}):
```

For each new run, convert the Delphes ROOT output to LHCO format:

**Use the script** (do not reimplement):
```bash
python scripts/convert_root_to_lhco.py {mg5path} {folder_base}_{model_name}_p6 {run}
```

Or in Python:
```python
from scripts.convert_root_to_lhco import convert_root_to_lhco

for run in new_runs:
    convert_root_to_lhco(mg5path, f"{folder_base}_{model_name}_p6", run)
```


This produces `{run}.lhco` in the same Events directory. See [`madgraph-reference.md`](madgraph-reference.md) ROOT→LHCO Conversion for details.

## Step 6.4: Rename Output Files (Global Numbering)

```python
with workflow_step(logger, "6", f"rename_outputs_o_{g_idx}",
                   inputs={"num_runs": len(new_runs)}):
```

Map each new run to `np_o_{g_idx}_f{index}` by run order (sorted by run number):

```
run_XX → np_o_1_f0_banner.txt,  np_o_1_f0.lhco   (coefficient = -c_{n_{scan}})
run_YY → np_o_1_f1_banner.txt,  np_o_1_f1.lhco   (coefficient = -c_{n_{scan}} + 0.2*c_{n_{scan}})
run_ZZ → np_o_1_f2_banner.txt,  np_o_1_f2.lhco   (coefficient = -c_{n_{scan}} + 0.4*c_{n_{scan}})
...
```

Use set-difference to identify `new_runs`, then sort by run number:

```python
new_runs = sorted(all_runs - existing, key=lambda x: int(x.split("_")[1]))
for i, run in enumerate(new_runs):
    banner_path = os.path.join(events_dir, run, f"{run}_tag_1_banner.txt")
    run_lhco = os.path.join(events_dir, run, f"{run}.lhco")
    dest_banner = f"np_o_{g_idx}_f{i}_banner.txt"
    dest_lhco   = f"np_o_{g_idx}_f{i}.lhco"
    # Copy banner and lhco to results/data/phase6/
```

```python)]})
```

> **Important**: The output uses **global operator index** (`o_{g_idx}`), NOT the model-internal anoinput index. This ensures all downstream phases reference operators consistently.

After all operators have been processed:

```python
logger.phase_complete("6")
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase6/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase6/
  scan_manifest.json
  phase6_progress.json
  np_o_1_f0_banner.txt    np_o_1_f0.lhco
  np_o_1_f1_banner.txt    np_o_1_f1.lhco
  np_o_1_f2_banner.txt    np_o_1_f2.lhco
  ...
  np_o_1_f10_banner.txt   np_o_1_f10.lhco
  np_o_2_f0_banner.txt    np_o_2_f0.lhco
  np_o_2_f1_banner.txt    np_o_2_f1.lhco
  ...
  np_o_2_f10_banner.txt   np_o_2_f10.lhco
  ...
  np_o_N_f0_banner.txt    np_o_N_f0.lhco
  ...
  np_o_N_f10_banner.txt   np_o_N_f10.lhco
```

## Common Mistakes for This Phase

| Mistake | Fix |
|---------|-----|
| `runs[-11:]` heuristic | Use set-difference to identify new runs |
| Re-launching on existing runs | Remove large temps, rename the **process directory** (not individual runs), create fresh |
| Using model-internal index in filename | Always use global index `o_{g_idx}` |
| Creating one process dir per operator | Create one per **model** (operators from the same model share a directory) |
| tag_2 ROOT files | Only happens if existing runs were modified and re-launched |
| Hardcoding `tag_1` in root2lhco call | Check which tag actually exists |
| Stopping because the estimate is 4-8 hours, weeks, or months | Start durable execution and continue/resume from `phase6_progress.json` |
| Asking the user to reduce events or confirm continuation | Never ask during Phase 6; event counts are locked |
| File named `!` containing `convert_root_to_lhco.py` usage text | The conversion script was called with wrong arguments and output was redirected with shell clobber syntax. Use `python scripts/convert_root_to_lhco.py {mg5path} {process_folder} {run_folder}` and log stdout/stderr paths instead of `> !` |

## Phase Transition

After all operators are scanned and all LHCO files are copied:

1. **Check validation rules immediately**: If any scan point is missing, continue/resume/retry from `phase6_progress.json`; abort only if the missing output is caused by a concrete unrecoverable filesystem or physics-generation error.
2. **If validation passes**: **proceed immediately to Phase 7 without stopping.**
3. **Do NOT**: summarize results, ask for confirmation, present options, or wait for user input.

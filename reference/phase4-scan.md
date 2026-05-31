# Phase 4: Generate SM+NP Coefficient Scan Samples

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Generate 11 scan points per **globally claimed operator** across the coefficient range `[-c_{n_{scan}}, c_{n_{scan}}]`. Each operator is scanned in its **source model** (the model that claimed it). Output filenames use **global numbering** (`o_1`, `o_2`, ...) to maintain consistency across all phases.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

from scripts.normalize_process_name import normalize_process_name
folder_base = normalize_process_name(config.process)
```

Read `operator_claims.json` and `coefficient_ranges.json` from previous phases.

From `coefficient_ranges.json`, read the unified range: `c_{scan} = coefficient_ranges["global"][1]` (the positive bound). The same `c_{n_{scan}} = c_{scan}` applies to all operators.

## Critical Rules — Prevent tag_2 Corruption

- **NEVER** delete files from an existing `run_XX` and re-launch
- **NEVER** run `launch` on a process directory with partially processed runs
- **If the entire process directory must be re-run** (e.g., scan corrupted, too many bad runs):
  1. Remove large temporary files across all runs to free disk: `find Events/run_*/ -name "*.root" -o -name "*.lhe.gz" -o -name "*.hepmc.gz" | xargs rm -f`
  2. Rename the process directory: `mv {folder_name} {folder_name}_broken`
  3. Create a fresh process directory and re-run from scratch
- Do **NOT** rename individual `run_XX` folders — this breaks run-number tracking
- If `tag_2` appears, you violated this rule

## Step 4.1: Create Scan Process Directories

For each **unique model** that has at least one claimed operator, create ONE scan process directory:

```
import model {model_name}
generate {process_name}
output {folder_base}_{model_name}_p4
```

> **Process directory naming**: `{folder_base}_{model_name}_p4` ensures each model has its own directory. Multiple operators from the same model share one directory.

## Step 4.2: Generate Scan Points Per Operator

For each globally claimed operator `o_{g_idx}` (from `operator_claims.json`):

1. Look up its source model and anoinput index from `operator_claims.json`
2. Use the process directory `{folder_base}_{model_name}_p4`
3. Generate 11 scan points:

```python
coefficient_list = [-c_{n_{scan}} + 0.2*c_{n_{scan}}*n for n in range(0, 11)]
```

Launch order (follows [`madgraph-reference.md`](madgraph-reference.md) Event Generation Order template):

```
launch {folder_base}_{model_name}_p4
detector = Delphes
analysis = OFF
0
set {block_name} {anoinput_idx} scan:[{comma-separated values}]
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

# Run MG5
subprocess.run([...])

all_runs = set(d for d in os.listdir(events_dir) if d.startswith("run_"))
new_runs = sorted(all_runs - existing, key=lambda x: int(x.split("_")[1]))
# new_runs contains exactly the runs from this launch
```

## Step 4.3: Convert ROOT to LHCO

For each new run, convert the Delphes ROOT output to LHCO format:

**Use the script** (do not reimplement):
```bash
python scripts/convert_root_to_lhco.py {mg5path}/{folder_base}_{model_name}_p4/Events/{run}/ {run}.root
```

Or in Python:
```python
from scripts.convert_root_to_lhco import convert_root_to_lhco

for run in new_runs:
    root_file = os.path.join(events_dir, run, f"{run}_tag_1_delphes_events.root")
    convert_root_to_lhco(root_file)
```

This produces `{run}.lhco` in the same Events directory. See [`madgraph-reference.md`](madgraph-reference.md) ROOT→LHCO Conversion for details.

## Step 4.4: Rename Output Files (Global Numbering)

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
    # Copy banner and lhco to results/data/phase4/
```

> **Important**: The output uses **global operator index** (`o_{g_idx}`), NOT the model-internal anoinput index. This ensures all downstream phases reference operators consistently.

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase4/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase4/
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

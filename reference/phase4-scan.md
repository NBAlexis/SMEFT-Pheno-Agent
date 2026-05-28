# Phase 4: Generate SM+NP Coefficient Scan Samples

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Generate 11 scan points per operator across the coefficient range `[-c1, c1]`.

## Critical Rules — Prevent tag_2 Corruption

- **NEVER** delete files from an existing `run_XX` and re-launch
- **NEVER** run `launch` on a process directory with partially processed runs
- **If the entire process directory must be re-run** (e.g., scan corrupted, too many bad runs):
  1. Remove large temporary files across all runs to free disk: `find Events/run_*/ -name "*.root" -o -name "*.lhe.gz" -o -name "*.hepmc.gz" | xargs rm -f`
  2. Rename the process directory: `mv {folder_name} {folder_name}_broken`
  3. Create a fresh process directory and re-run from scratch
- Do **NOT** rename individual `run_XX` folders — this breaks run-number tracking
- If `tag_2` appears, you violated this rule

## Step 4.1: Create Scan Process Directory

```
import model {model_name}
generate {process_name}
output {folder_base}_p4
```

## Step 4.2: Generate Scan Points

For each operator `oi` with range `[-c1, c1]`:

```python
coefficient_list = [-c1 + 0.2*c1*n for n in range(0, 11)]
```

Launch order (follows [`madgraph-reference.md`](madgraph-reference.md) Event Generation Order template):

```
launch {folder_base}_p4
detector = Delphes
analysis = OFF
0
set anoinputs {idx} scan:[{comma-separated values}]
set anoinputs {other_idx} 0.0
...
set ebeam1 = {ebeam_value}
set ebeam2 = {ebeam_value}
set nevents = {nev_scan}
0
```

- `ebeam_value = energy * 1000 / 2` (GeV). See [`madgraph-reference.md`](madgraph-reference.md) Energy Assignment.
- Use `set anoinputs {lha_code} scan:[v1, v2, ...]` (not bare `set {number} = scan:[...]`, which MG5 silently ignores).
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

## Step 4.3: Rename Output Files

Map each new run to `np_oi_f{index}` by run order (sorted by run number):

```
run_XX → np_oi_f0_banner.txt,  np_oi_f0.lhco   (coefficient = -c1)
run_YY → np_o1_f1_banner.txt,  np_o1_f1.lhco   (coefficient = -c1 + 0.2*c1)
run_ZZ → np_o1_f2_banner.txt,  np_o1_f2.lhco   (coefficient = -c1 + 0.4*c1)
...
```

Use set-difference to identify `new_runs`, then sort by run number:

```python
new_runs = sorted(all_runs - existing, key=lambda x: int(x.split("_")[1]))
for i, run in enumerate(new_runs):
    banner_path = os.path.join(events_dir, run, f"{run}_tag_1_banner.txt")
    run_lhco = os.path.join(events_dir, run, f"{run}.lhco")
    dest_banner = f"np_oi_f{i}_banner.txt"
    dest_lhco   = f"np_oi_f{i}.lhco"
    # Copy banner and lhco to results/data/phase4/
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase4/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase4/
  np_o1_f0_banner.txt    np_o1_f0.lhco
  np_o1_f1_banner.txt    np_o1_f1.lhco
  np_o1_f2_banner.txt    np_o1_f2.lhco
  ...
  np_o1_f10_banner.txt   np_o1_f10.lhco
  np_o2_f0_banner.txt    np_o2_f0.lhco
  np_o2_f1_banner.txt    np_o2_f1.lhco
  ...
  np_o2_f10_banner.txt   np_o2_f10.lhco
  ...
```

## Common Mistakes for This Phase

| Mistake | Fix |
|---------|-----|
| `runs[-11:]` heuristic | Use set-difference to identify new runs |
| Re-launching on existing runs | Remove large temps, rename the **process directory** (not individual runs), create fresh |

| tag_2 ROOT files | Only happens if existing runs were modified and re-launched |
| Hardcoding `tag_1` in root2lhco call | Check which tag actually exists |

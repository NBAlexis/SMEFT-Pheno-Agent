# Cleanup: Collect MG5 Process Folders

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE â€?once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
After all event generation is complete and results have been extracted to `results/data/`, move the MG5 process directories from `mg5path` to the working directory to prevent `mg5path` from accumulating unmanaged folders across multiple runs.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

from scripts.normalize_process_name import normalize_process_name
folder_base = normalize_process_name(config.process)
```

## When to Run

Execute **after Phase 10 (manuscript generation)** and **before Phase 11 (audit)**. At this point, all required files (banners, LHCO, CSV, plots, manuscript) have already been copied to `results/`.

## Critical Rule

Use **`mv`** (move), not `cp` (copy). The process directories are large and no longer needed in `mg5path` once results are extracted. Moving saves disk space.

## Process Directories to Collect

Identify all process directories created during this workflow.

**Single-model mode:** Directory names follow the pattern `{folder_base}_p{phase}_{timestamp}_*{suffix}` (per `madgraph-reference.md` convention).

**Multi-model mode:** Directory names include the model name: `{folder_base}_{model}_p{phase}` (no timestamp needed since model names prevent collisions).

Use glob patterns to match both conventions:

| Phase | Process Directory Pattern |
|-------|---------------------------|
| 3 | `{folder_base}_p3_*_NP` or `{folder_base}_*_p3_NP` |
| 4 | `{folder_base}_p4_*_SM` or `{folder_base}_*_p4_SM` |
| 5 SM | `{folder_base}_p5_*_SM` or `{folder_base}_*_p5_SM` |
| 5 NP | `{folder_base}_p5_*_NP` or `{folder_base}_*_p5_NP` |
| 6 | `{folder_base}_p6_*` or `{folder_base}_*_p6` |

> **Note**: The glob patterns use `*` to match either the timestamp suffix (single-model) or the model name (multi-model).

## Order Files to Collect

All order files written to `mg5path/` during this workflow must also be moved. Order file naming follows the pattern:

```
order_p{phase}_{timestamp}_{random_suffix}.txt
```

Examples: `order_p3_20260525_01.txt`, `order_p4_20260525_01.txt`, etc.

## Collection Procedure

1. Create destination directories:
   ```bash
   mkdir -p {workdir}/results/mg5_processes
   mkdir -p {workdir}/results/orders
   ```

2. Move each process directory:
   ```python
   import shutil, os, glob

   # In multi-run mode, prefix with the run subdirectory (e.g., results/E10_L1000/)
   results_prefix = os.path.join(workdir, "results")
   if run_subdir:  # e.g., "E10_L1000" in multi-run mode; None in single-run
       results_prefix = os.path.join(results_prefix, run_subdir)

   mg5_processes_dir = os.path.join(results_prefix, "mg5_processes")
   orders_dir = os.path.join(results_prefix, "orders")
   os.makedirs(mg5_processes_dir, exist_ok=True)
   os.makedirs(orders_dir, exist_ok=True)

   # Use glob to match both single-model (timestamped) and multi-model (model-named) directories
   process_dir_patterns = [
       f"{folder_base}_p3_*_NP",      # Phase 3 NP (single-model timestamped)
       f"{folder_base}_*_p3_NP",      # Phase 3 NP (multi-model)
       f"{folder_base}_p4_*_SM",      # Phase 4 SM (single-model)
       f"{folder_base}_*_p4_SM",      # Phase 4 SM (multi-model)
       f"{folder_base}_p6_*",         # Phase 6 scan (single-model)
       f"{folder_base}_*_p6",         # Phase 6 scan (multi-model)
       f"{folder_base}_p5_*_SM",      # Phase 5 SM (single-model)
       f"{folder_base}_*_p5_SM",      # Phase 5 SM (multi-model)
       f"{folder_base}_p5_*_NP",      # Phase 5 NP (single-model)
       f"{folder_base}_*_p5_NP",      # Phase 5 NP (multi-model)
   ]

   moved_dirs = []
   for pattern in process_dir_patterns:
       for src in glob.glob(os.path.join(mg5path, pattern)):
           if os.path.isdir(src):
               dst = os.path.join(mg5_processes_dir, os.path.basename(src))
               if os.path.exists(dst):
                   raise RuntimeError(f"Destination already exists: {dst}")
               shutil.move(src, dst)
               moved_dirs.append(os.path.basename(src))
   ```

3. Move all order files created during this run:
   ```python
   # Match order files created by this workflow
   order_pattern = os.path.join(mg5path, "order_p*.txt")
   order_files = glob.glob(order_pattern)

   moved_orders = []
   for src in order_files:
       dst = os.path.join(orders_dir, os.path.basename(src))
       shutil.move(src, dst)
       moved_orders.append(os.path.basename(src))
   ```

4. Record cleanup log:
   ```json
   {
     "cleanup_time": "2026-05-26T10:00:00",
     "source": "/home/user/MG5_aMC_v3_5_6",
     "destination_processes": "/home/user/work/results/E10_L1000/mg5_processes",
     "destination_orders": "/home/user/work/results/E10_L1000/orders",
     "moved_directories": ["mup_mum_to_ll_vlvl_p3_20260525_01_NP", "mup_mum_to_ll_vlvl_AQGCm_UFO_p3_NP", ...],
     "moved_order_files": ["order_p3_20260525_01.txt", "order_p4_20260525_01.txt", ...],
     "total_moved_dirs": 5,
     "total_moved_orders": 8
   }
   ```

   **Multi-run note**: In multi-run mode, the destination paths include the run subdirectory (e.g., `results/E10_L1000/mg5_processes`).

## Safety Checks

Before moving, verify:
1. All required result files exist in `results/data/` and `results/plots/` (quick spot-check). In multi-run mode, check under `results/E{e}_L{l}/data/` and `results/E{e}_L{l}/plots/`.
2. Process directories are not currently being written to by a running MG5 process
3. The destination does not already contain a directory or file with the same name (if so, abort and report)

## Validation

After cleanup:
- `mg5path` should contain **no** process directories from this workflow
- `mg5path` should contain **no** order files matching `order_p*.txt` from this workflow
- Phase 11 audit should verify the cleanup log exists and records both directories and order files

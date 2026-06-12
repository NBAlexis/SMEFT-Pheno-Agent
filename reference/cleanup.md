# Cleanup: Collect MG5 Process Folders

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE - once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
After all event generation is complete and results have been extracted to `results/data/`, move the MG5 process directories from `mg5path` to the working directory to prevent `mg5path` from accumulating unmanaged folders across multiple runs.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")
```

## When to Run

Execute **after Phase 10 (manuscript generation)** and **before Phase 11 (audit)**. At this point, all required files (banners, LHCO, CSV, plots, manuscript) have already been copied to `results/`.

## Critical Rule

Use **`mv`** (move), not `cp` (copy). The process directories are large and no longer needed in `mg5path` once results are extracted. Moving saves disk space.

## Process Directories to Collect

Identify all process directories created during this workflow.

The config runner names process directories with the normalized process base, model name, mode suffix (`SM`, `NP`, `SMNP`, or `SCAN`), and timestamp. Failed runner-owned directories may have an additional `_broken_{timestamp}` suffix.
Keep `_broken_*` process directories until cleanup. They may have had large
ROOT/LHE/HEPMC files removed already, but the directory itself must be moved
into the project results for audit/debugging rather than deleted during the
workflow.

Prefer the exact `process_dir` and `broken_process_dir` values recorded in
runner result JSON files. This is required for multi-process runs, where
`config.process` may be a list and agents must not hand-compute folder names.

## Order Files to Collect

All order files written to `mg5path/` during this workflow must also be moved.
Use the exact `create_process.order_file_path` and `launch.order_file_path`
values recorded in runner result JSON files.

## Collection Procedure

1. Create destination directories:
   ```bash
   mkdir -p {workdir}/results/mg5_processes
   mkdir -p {workdir}/results/orders
   ```

2. Move each process directory:
   ```python
   import shutil, os, glob, json

   # In multi-run mode, prefix with the run subdirectory (e.g., results/E10_L1000/)
   results_prefix = os.path.join(workdir, "results")
   if run_subdir:  # e.g., "E10_L1000" in multi-run mode; None in single-run
       results_prefix = os.path.join(results_prefix, run_subdir)

   mg5_processes_dir = os.path.join(results_prefix, "mg5_processes")
   orders_dir = os.path.join(results_prefix, "orders")
   os.makedirs(mg5_processes_dir, exist_ok=True)
   os.makedirs(orders_dir, exist_ok=True)

   def iter_json_objects(obj):
       if isinstance(obj, dict):
           yield obj
           for value in obj.values():
               yield from iter_json_objects(value)
       elif isinstance(obj, list):
           for item in obj:
               yield from iter_json_objects(item)

   runner_manifests = glob.glob(os.path.join(results_prefix, "data", "**", "*.json"), recursive=True)
   process_dirs = set()
   order_files = set()
   for manifest_path in runner_manifests:
       try:
           with open(manifest_path, encoding="utf-8") as f:
               manifest = json.load(f)
       except Exception:
           continue
       for record in iter_json_objects(manifest):
           for key in ("process_dir", "broken_process_dir"):
               value = record.get(key)
               if value and os.path.isdir(value):
                   process_dirs.add(value)
           value = record.get("order_file_path")
           if value and os.path.exists(value):
               order_files.add(value)

   moved_dirs = []
   for src in sorted(process_dirs):
       dst = os.path.join(mg5_processes_dir, os.path.basename(src))
       if os.path.exists(dst):
           raise RuntimeError(f"Destination already exists: {dst}")
       shutil.move(src, dst)
       moved_dirs.append(os.path.basename(src))
   ```

3. Move all order files created during this run:
   ```python
   moved_orders = []
   for src in sorted(order_files):
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
     "moved_directories": ["mup_mum_to_ll_vlvl_AQGCm_UFO_NP_20260526_100000", ...],
     "moved_order_files": ["order_create_mup_mum_to_ll_vlvl_AQGCm_UFO_NP_20260526_100000_01.txt", ...],
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
- `mg5path` should contain **no** runner order files recorded in the manifests
- Phase 11 audit should verify the cleanup log exists and records both directories and order files

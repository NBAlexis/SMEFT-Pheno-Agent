# Cleanup: Collect MG5 Process Folders

> **Contract priority**: Preserve the research objective and deliverables. Apply the technical-failure and `phase_fail` definitions in `SKILL.md`.

## Purpose
After all event generation is complete and results have been extracted to `results/data/`, move the MG5 process directories from `mg5path` to the working directory to prevent `mg5path` from accumulating unmanaged folders across multiple runs.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")
```

## When to Run

Execute **after Phase 10 (manuscript generation)** and **before Phase 11 (replay packaging)**. At this point, all required files (banners, LHCO, CSV, plots, manuscript) have already been copied to `results/`.

## Critical Rule

Cleanup means **archive by moving**, not deleting. Use **`mv`** (move), not
`cp` (copy), for MG5 process directories and order files. The only files that
may be deleted during cleanup are `.root`, `.hepmc`, and `.hepmc.gz` files after
required outputs are secured. LHE/LHE.GZ files, cards, banners, logs, JSON,
order files, scripts, configuration files, and all other process contents are
small files under this workflow's cleanup definition and must be archived.
Never delete a runner-recorded process directory or order file as a shortcut;
move it under `results/mg5_processes/` or `results/orders/` for audit/debugging.

## Process Directories to Collect

Identify all process directories created during this workflow.

The config runner names process directories with the normalized process base, model name, mode suffix (`SM`, `NP`, `SMNP`, or `SCAN`), and timestamp. Failed runner-owned directories may have an additional `_broken_{timestamp}` suffix.
Keep `_broken_*` process directories until cleanup. Preserve their ROOT and
HEPMC files until the failure has been diagnosed; the directory itself must be moved
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

Use the bundled archiver with the current run root:

```bash
python scripts/archive_mg5_outputs.py {current_run_root} --delete-large
```

Omit `--delete-large` when storage does not require ROOT/HEPMC deletion. The
script reads every JSON file below `data/`, prefers `broken_process_dir` over
`process_dir`, collects every recorded `order_file_path`, moves the discovered
items, and writes `mg5_processes/cleanup_log.json`. It refuses destination-name
collisions and fails after writing the log when any recorded source is missing.

The log has this structure:

```json
{
  "cleanup_time": "2026-05-26T10:00:00+00:00",
  "destination_processes": "/home/user/work/results/E10_L1000/mg5_processes",
  "destination_orders": "/home/user/work/results/E10_L1000/orders",
  "expected_process_dirs": ["/path/to/process_A", "/path/to/process_B_broken_20260526"],
  "moved_process_dirs": ["/home/user/work/results/E10_L1000/mg5_processes/process_A"],
  "missing_process_dirs": [],
  "expected_order_files": ["/path/to/order_create_process_A.txt"],
  "moved_order_files": ["/home/user/work/results/E10_L1000/orders/order_create_process_A.txt"],
  "missing_order_files": [],
  "deleted_files": ["/path/to/process_A/Events/run_01/events.root"],
  "total_moved_dirs": 2,
  "total_moved_orders": 1
}
```

If a runner-recorded process directory or order file is absent, recover it if
possible and rerun the script. Do not complete cleanup while either missing
list is non-empty. The audit requires every expected basename to appear exactly
once in moved or missing and every moved path to exist.

**Multi-run note**: In multi-run mode, the destination paths include the run
subdirectory, for example `results/E10_L1000/mg5_processes`.

## Safety Checks

Before moving, verify:
1. All required result files exist in `results/data/` and `results/plots/` (quick spot-check). In multi-run mode, check under `results/{run_dir}/data/` and `results/{run_dir}/plots/`, where `{run_dir}` is copied from `run_configurations[*].run_dir`.
2. Process directories are not currently being written to by a running MG5 process
3. If the destination already contains the same name, compare checksums, merge
   only non-conflicting content, and record the decision in `cleanup_log.json`;
   do not overwrite an unequal file silently.

## Validation

Before treating cleanup as complete, satisfy
[`deliverables-cleanup.md`](deliverables-cleanup.md). Missing cleanup
deliverables require self-repair, not user interaction.

After cleanup:
- `mg5path` should contain **no** process directories from this workflow
- `mg5path` should contain **no** runner order files recorded in the manifests
- Phase 12 audit should verify the cleanup log exists and records both directories and order files

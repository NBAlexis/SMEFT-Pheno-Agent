# Cleanup Deliverables: Process-Folder Collection

Consumes: Phase 10 final manuscript plus runner manifests from earlier phases.

Must deliver:
- `results/mg5_processes/cleanup_log.json`.
- Moved runner-recorded MG5 process directories, including `_broken_*`
  directories, under `results/mg5_processes/`.
- Moved runner-recorded order files under `results/orders/`.
- Only `.root`, `.hepmc`, and `.hepmc.gz` intermediate files may be deleted
  after required outputs are secured. LHE/LHE.GZ and all other process files,
  runner-recorded process directories, and order files must be archived by
  moving, not deleted.
- `cleanup_log.json` must include `expected_process_dirs`,
  `moved_process_dirs`, `missing_process_dirs`, `expected_order_files`,
  `moved_order_files`, and `missing_order_files`.
- `expected_process_dirs` and `expected_order_files` must be populated from
  runner manifests; empty expected lists mean earlier phases did not use the
  required runner records.
- If the log records deleted paths, every path must end in `.root`, `.hepmc`, or
  `.hepmc.gz`; record deleted paths so Phase 12 can reject accidental removal of
  LHE, cards, banners, logs, JSON, order files, scripts, or configurations.

Manuscript dependency: none directly, but Phases 11 and 12 use this for reproducibility
and disk hygiene evidence.

If missing or incomplete: inspect runner manifests, move remaining recorded
directories/order files, and update the cleanup log. Do not delete process
directories as a shortcut.

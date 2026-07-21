# Phase 6 Deliverables: Coefficient Scans

Consumes: Phase 3 claimed operators and Phase 4 per-operator `c_scan` values.

Must deliver:
- `results/data/phase6/scan_manifest.json` listing every claimed operator,
  operator-specific `c_scan`, scan expression, `point_count=11`, and labels
  `f0` through `f10`.
- In each `scan_manifest.json` operator entry, `weighted_order_guard` with the
  extracted `max_weighted_order`, source SM/NP runner result paths, script JSON
  path or manual recovery reason, and the runner-selected `WEIGHTED`/`Weighted`
  keyword.
- `results/data/phase6/phase6_progress.json`.
- `results/data/phase6/np_o_N_scan_result.json` for every claimed operator.
- For every claimed operator and every label `f0` through `f10`:
  `np_o_N_fi.lhco` and `np_o_N_fi_banner.txt`.
- `results/data/phase6/event_count_recovery.json` with scan-point merged
  outputs, all source banners, loaded LHCO counts, and merged cross-sections.
- For every claimed operator and every scan label `f0` through `f10`, the final
  loaded LHCO event count after recovery must be greater than `10%` of the
  requested scan event count.

Manuscript dependency: coefficient scan datasets, scan coefficients, scan
cross-sections, loaded event counts, and fit/plot source data.

If missing or incomplete: resume from `phase6_progress.json` or rerun the
specific operator scan. Runtime is never a reason to skip Phase 6. A missing
operator, missing scan point, or scan point with loaded LHCO event count not
greater than `10%` of the requested scan event count blocks Phase 7 until
recovery succeeds or a structured `phase_fail` record permitted by `SKILL.md` is recorded.

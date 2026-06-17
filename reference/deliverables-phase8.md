# Phase 8 Deliverables: Selection and Fits

Consumes: Phase 6 scans and Phase 7 algorithms/features/scores.

Must deliver:
- Public scan CSV files for every claimed operator and every `f0`-`f10` point.
- Per-event scan score CSVs for every trained algorithm, every claimed
  operator, and every scan point:
  `results/data/phase8/scores/{alg}/np_o_N_fi_scores.csv`, where `{alg}` is
  the stable key from Phase 7 `algorithm_comparison.json["anchor"]`.
- `results/data/phase8/scan_event_counts.json` with loaded LHCO counts,
  final-state-cut counts, passing counts, and explicit denominators.
- `results/data/phase8/threshold_optimization.json` with anchor-only threshold
  scans for every algorithm, including lower/upper real-root bounds and widths.
- `results/data/phase8/dataset_summary.json` with loaded counts, final-state
  counts, raw cross-sections, final-state-cut cross-sections, exact cuts, and
  public CSV/score paths.
- `results/data/phase8/csfit_o_N_{alg}.json` for every claimed operator and
  every trained algorithm key, using fixed
  `sigma(f)=sigma0_after_cut+f*sigma_int+f^2*sigma_NP`.
- `results/plots/csfit_plot_o_N_{alg}.pdf` for every claimed operator and
  trained algorithm key.
- `results/plots/threshold_comparison.pdf` and
  `results/plots/anchor_s2_constraint_range_vs_threshold.pdf`.

Manuscript dependency: threshold strategy, event-selection efficiencies, dataset
table, fixed-intercept fit coefficients, selected cross-section vs fit plots,
and anchor threshold-scan evidence.

If missing or incomplete: recompute the missing conversion, score, threshold
scan, fit, or plot. Do not drop an operator or algorithm because fitting failed;
diagnose and repair before Phase 9.

# Phase 8 Deliverables: Selection and Fits

Consumes: Phase 6 scans and Phase 7 algorithms/features/scores.

Must deliver:
- A shared Phase 8 `f5` LHCO pool at `results/data/phase8/shared_f5.lhco`,
  formed initially from exactly one `f5` sample for every Phase 3 claimed
  operator and extended only by the allowed additional anchor `f5` rounds.
- `results/data/phase8/shared_f5_merge.json`, retaining every source LHCO and
  banner record plus the merged loaded count and arithmetic mean of source
  banner cross-sections.
- `results/data/phase8/csv/shared_f5.csv`, produced from the merged LHCO with
  the same feature extraction used for scan data.
- `results/data/phase8/shared_f5_background.json`, recording the source
  operators, anchor-only additional `f5` rounds, merged counts, and one fixed
  background record for every trained algorithm.
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

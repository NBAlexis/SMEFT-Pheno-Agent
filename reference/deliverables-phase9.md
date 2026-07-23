# Phase 9 Deliverables: Constraints

Consumes: Phase 8 fits/thresholds and Phase 7 algorithm comparison.

Must deliver:
- `results/data/phase9/algorithm_selection.json` recording the final selection
  scope. By default, `anchor_operator_only` selects one strategy from
  anchor-operator `S_stat=2` interval widths. This comparison criterion cannot be
  replaced by AUC or another metric. `per_operator_best` additionally records an
  `operator_selections` entry for every claimed operator. It
  must include `selected_algorithm`, `selected_threshold`, `anchor_operator`,
  `selection_scope`, `selection_criterion`, `selection_rationale`,
  `selection_evidence`, and the source entry in `threshold_optimization.json`.
  The rationale explains why the recorded scope was used. For every non-anchor
  operator it also records `comparison_only_intervals` with the evaluated
  threshold and finite `S2` interval for every scientifically usable candidate;
  the selected candidate must have the narrowest interval. Excluded candidates
  require a reason and evidence, not an alternative ranking metric.
- `results/data/phase9/constraint_table.json` and `.csv` with final
  `S_stat=2,3,5` intervals for every claimed operator and the algorithm and
  threshold actually used for each row. The JSON also records the independent
  numerical review method, pass status, and evidence paths; the CSV must contain
  exactly one row per operator and agree numerically with the JSON.
- `results/plots/anchor_s2_algorithm_constraint_bar.pdf`.

Manuscript dependency: final coefficient-constraint table, explicit selection
scope, anchor algorithm-comparison bar plot, and significance-level results.

If missing or incomplete: recompute constraints from Phase 8 fits. If a fit is
missing or uses a free intercept, return to Phase 8 repair rather than omitting
the operator.

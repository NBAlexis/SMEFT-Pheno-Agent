# Phase 9 Deliverables: Constraints

Consumes: Phase 8 fits/thresholds and Phase 7 algorithm comparison.

Must deliver:
- `results/data/phase9/algorithm_selection.json` recording the final selection
  scope. `anchor_operator_only` selects one strategy from anchor-operator
  `S_stat=2` interval widths. `per_operator_best` additionally records an
  `operator_selections` entry for every claimed operator. It
  must include `selected_algorithm`, `selected_threshold`, `anchor_operator`,
  `selection_scope`, `selection_criterion`, and the source entry in
  `threshold_optimization.json`.
- `results/data/phase9/constraint_table.json` and `.csv` with final
  `S_stat=2,3,5` intervals for every claimed operator and the algorithm and
  threshold actually used for each row.
- `results/plots/anchor_s2_algorithm_constraint_bar.pdf`.

Manuscript dependency: final coefficient-constraint table, explicit selection
scope, anchor algorithm-comparison bar plot, and significance-level results.

If missing or incomplete: recompute constraints from Phase 8 fits. If a fit is
missing or uses a free intercept, return to Phase 8 repair rather than omitting
the operator.

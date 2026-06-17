# Phase 9 Deliverables: Constraints

Consumes: Phase 8 fits/thresholds and Phase 7 algorithm comparison.

Must deliver:
- `results/data/phase9/algorithm_selection.json` selecting exactly one final
  event-selection strategy from anchor-operator `S_stat=2` interval widths. It
  must include `selected_algorithm`, `selected_threshold`, `anchor_operator`,
  `selection_scope`, `selection_criterion`, and the source entry in
  `threshold_optimization.json`.
- `results/data/phase9/constraint_table.json` and `.csv` with final
  `S_stat=2,3,5` intervals for every claimed operator using the same selected
  algorithm and threshold.
- `results/plots/anchor_s2_algorithm_constraint_bar.pdf`.

Manuscript dependency: final coefficient-constraint table, single-strategy
statement, anchor algorithm-comparison bar plot, and significance-level results.

If missing or incomplete: recompute constraints from Phase 8 fits. If a fit is
missing or uses a free intercept, return to Phase 8 repair rather than omitting
the operator.

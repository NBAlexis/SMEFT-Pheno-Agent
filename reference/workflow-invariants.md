# Workflow Invariants

These rules apply across phases. Before `logger.phase_complete("N")`, run the
relevant checks below, fix violating artifacts, log the correction, and continue
without asking the user during Execution Mode.

## Selection Scope

- `anchor_operator_only` is the default: choose one algorithm and one score
  threshold from the anchor operator and use them for every operator.
- `per_operator_best` is also valid: for each operator, select the narrowest
  `S_stat=2` interval from the complete Phase 8 operator-by-algorithm fits.
  Use each algorithm's already recorded Phase 8 optimal threshold; this is a
  re-aggregation of existing results and does not rerun simulation or training.
- Record the final scope in `algorithm_selection.json`. For
  `per_operator_best`, record `operator_selections` for every claimed operator.
- Non-anchor pure NP samples are for public CSV data, score histograms, and
  manuscript evidence only.
- Do not mix the two scopes silently or omit an operator selection.

## Actual Event Counts

- `nev_*` values are requested generation targets, not actual event counts.
- Actual LHCO counts below the requested target are not failures by themselves.
  Counts below `10%` of the requested target trigger automatic MG5 run-card
  recovery before the sample may be accepted.
- If recovery produces multiple parseable attempts, downstream analysis uses the
  merged LHCO and merged metadata defined in `event-count-recovery.md`.
- Selection efficiencies and selected cross-sections use
  `LoadLHCOlympics(...).GetEventCount()` as the LHCO denominator.
- Banner files may be used for cross-sections only, never for actual event
  counts.
- Phase 8 fixed backgrounds use the merged loaded count of the shared `f5`
  pool and the arithmetic mean of all source banner cross-sections. A zero
  selected count triggers up to three additional anchor `f5` rounds; the
  event-generation target remains the locked `nev_scan`.

## Publication Data

- Phase 7 pure-sample CSV files, Phase 8 scan CSV files, and all per-event score
  CSV files are publication data.
- Do not delete publication CSV or score CSV files during cleanup.
- Phase 10 evidence must record public CSV and score CSV paths when available.

## Execution Continuity

- Runtime length is not a stop condition.
- Do not reduce event counts, operators, scan points, algorithms, or thresholds
  for speed.
- Do not ask the user whether to continue after Execution Mode begins.

# Workflow Invariants

These rules apply across phases. Before `logger.phase_complete("N")`, run the
relevant checks below, fix violating artifacts, log the correction, and continue
without asking the user during Execution Mode.

## Single Selection Strategy

- For each collider run, the final production event-selection strategy is
  exactly one algorithm plus one score threshold.
- The strategy is chosen only from the anchor operator.
- Non-anchor pure NP samples are for public CSV data, score histograms, and
  manuscript evidence only.
- Do not choose per-operator production algorithms or per-operator thresholds.

## Actual Event Counts

- `nev_*` values are requested generation targets, not actual event counts.
- Selection efficiencies and selected cross-sections use
  `LoadLHCOlympics(...).GetEventCount()` as the LHCO denominator.
- Banner files may be used for cross-sections only, never for actual event
  counts.

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

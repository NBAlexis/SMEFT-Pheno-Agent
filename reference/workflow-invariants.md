# Workflow Invariants

These rules apply across phases. Before `logger.phase_complete("N")`, run the
relevant checks below, fix violating artifacts, log the correction, and continue
without asking the user during Execution Mode.

## Selection Scope

With `debug=false`, a scientifically usable result means that the LLM judges the
event support, fit validity, numerical stability, and resulting constraints
sufficient for a defensible scientific report and records the supporting data.
With `debug=true`, a result usable for the workflow test need only provide
finite, internally consistent, traceable outputs that exercise the complete
workflow; it is not a claim of statistical reliability. Neither judgment is the
name of a scripted status or one fixed numerical cutoff.

- `anchor_operator_only` is the default: choose one algorithm and one score
  threshold from the anchor operator and use them for every operator when the
  resulting fits and constraints are usable under the selected `debug` setting.
- `per_operator_best` is valid when the user requested it in
  `analysis_notes.additional_requirements`, or when the LLM finds evidence that
  the common strategy cannot produce a result usable under the selected `debug`
  setting for one or more operators. Let the LLM make this decision from the
  recorded evidence; do not reduce it to a fixed list of scripted failure states.
- For `per_operator_best`, choose the trained algorithm and threshold that give
  the narrowest expected coefficient-constraint interval among the
  candidates usable under the selected `debug` setting and recorded for that
  operator in Phase 8.
  Existing Phase 8 results may be
  re-aggregated, or affected Phase 7-9 work may be repaired and rerun when the
  evidence requires it.
- Record `selection_scope`, a non-empty `selection_rationale`, and
  `selection_evidence` paths in `algorithm_selection.json`. For
  `per_operator_best`, also record `operator_selections` for every claimed
  operator. The evidence may point to the user's additional requirement or to
  Phase 7-9 data demonstrating why the default is inadequate.
- Non-anchor pure NP samples are for public CSV data, score histograms, and
  manuscript evidence only.
- Do not mix the two scopes silently or omit an operator selection.

## Scientific Method and Audit

- Generate every numerical analysis sample with MG5 and pass it through
  Delphes. Undetected LHE events are not analysis inputs.
- With `debug=false`, treat the locked scientific event counts as per-run minima;
  if support is scientifically insufficient, add full-size runs and merge them.
  With `debug=true`, use the locked reduced counts to test the complete workflow,
  not strict statistical reliability. Never lower the values locked for either
  mode after Phase 1.
- Convert Delphes LHCO to CSV and use a trained ML score threshold for final
  selection. A fixed final-state particle-number preselection is allowed, but a
  traditional hand-designed kinematic cut analysis cannot replace the ML stage.
- Compute coefficient constraints only from fitted selected cross-sections and
  the declared signal-significance formula.
- Compare strategies usable under the selected `debug` setting only by expected
  coefficient-constraint interval width. AUC is descriptive or diagnostic only.
- Deliver every manuscript item in the frozen Phase 10 list. Earlier evidence
  requirements exist to support that list, not to add unrelated work.
- The research objective, fixed method boundaries, and required scientific
  outputs have priority over a default algorithm, implementation, or audit.
- Keep the six fixed method boundaries, frozen deliverable paths, formats,
  required fields, and full operator coverage. ML algorithms, implementations,
  hyperparameters, fitting implementations, and audit code may change when the
  actual data justify the change and the replacement validates the method that
  was really used.
- Record the reason, evidence paths, changed code checksum, and affected outputs.
  Do not edit an audit only to convert an unexplained failure into a pass.
- Use deterministic checks for facts without scientific discretion, including
  file structure, event identities, arithmetic, checksums, and agreement between
  JSON and CSV. Leave method choice and interpretation of unusual scientific
  behavior to the LLM, supported by recorded evidence.

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
- Do not reduce event counts below the values locked for the selected `debug`
  setting, or reduce operators, scan points, algorithms, or thresholds for speed.
- Do not ask the user whether to continue after Execution Mode begins.

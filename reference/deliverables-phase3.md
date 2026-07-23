# Phase 3 Deliverables: Operator Impact

Consumes: Phase 1 config and Phase 2 validated environment.

Must deliver:
- `results/data/phase3/operator_claims.json` covering every globally claimed
  non-zero operator with stable `o_N` numbering.
- `results/data/phase3/cross_sections.json` covering all tested coefficients,
  including zero results.
- `results/data/phase3/model_status.json` with exactly the configured model
  names and the `coefficient_count`, `tested_count`, and per-coefficient fields
  defined in `phase3-validation.md`.
- `results/data/phase3/anchor.json` for the first non-zero operator.
- Every Phase 3 runner result JSON produced by create-NP and per-coefficient
  tests, with paths recorded in `model_status.json`. These manifests must
  retain runner metadata such as process directories, order files,
  stdout/stderr paths, zero-cross-section checks, and parsed cross-sections.
  Every numerical result also records `event_generator=MadGraph5`,
  `detector_simulation=Delphes`,
  `analysis_event_format=LHCO_from_Delphes_ROOT`, the non-empty Delphes card,
  and the requested event count. The create-NP result is exempt because it only
  creates a process folder and does not produce analysis events.
- If no operator is claimed, `results/data/phase3/phase3_report.txt` before the
  red-flag stop.

Manuscript dependency: active operator set, anchor operator, model/source UFO,
available coefficient metadata, and zero-contribution evidence.

If missing or incomplete: resume the coefficient loop until every coefficient
in every requested model has a recorded result. Do not drop zero operators
silently and do not ask the user about partial sensitivity.

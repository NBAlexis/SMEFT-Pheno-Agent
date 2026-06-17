# Phase 3 Deliverables: Operator Impact

Consumes: Phase 1 config and Phase 2 validated environment.

Must deliver:
- `results/data/phase3/operator_claims.json` covering every globally claimed
  non-zero operator with stable `o_N` numbering.
- `results/data/phase3/cross_sections.json` covering all tested coefficients,
  including zero results.
- `results/data/phase3/model_status.json` with per-model diagram status and
  coefficient results.
- `results/data/phase3/anchor.json` for the first non-zero operator.
- Every Phase 3 runner result JSON produced by create-NP and per-coefficient
  tests, with paths recorded in `model_status.json`. These manifests must
  retain runner metadata such as process directories, order files,
  stdout/stderr paths, zero-cross-section checks, and parsed cross-sections.
- If no operator is claimed, `results/data/phase3/phase3_report.txt` before the
  red-flag stop.

Manuscript dependency: active operator set, anchor operator, model/source UFO,
available coefficient metadata, and zero-contribution evidence.

If missing or incomplete: resume the coefficient loop until every coefficient
in every requested model has a recorded result. Do not drop zero operators
silently and do not ask the user about partial sensitivity.

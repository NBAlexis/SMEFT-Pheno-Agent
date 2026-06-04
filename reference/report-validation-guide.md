# Report Validation Guide

Validate the report after every draft. Write validation output to
`results/data/phase10/report_validation.json`.

## Revision Loop

Use a bounded loop:

1. Draft `report_draft_v1`.
2. Validate.
3. If validation fails, revise and write `report_draft_v2`.
4. Validate.
5. If validation still fails, revise once more and write the final report.
6. Validate the final report and archive remaining issues.

Maximum revisions after the first draft: `2`.

Never block cleanup or Phase 11 because the report remains imperfect. After the
revision limit, write `report_validation.json` with `status: "issues_remaining"`
and continue to cleanup and audit.

## Blocking During Phase 10

Stop only for unrecoverable file-writing, parser, or output-generation errors.
Scientific/style validation failures are not stop conditions after the revision
limit.

## Required Checks

Mark these as `major` if they fail:

- report uses approximate event counts such as `~2500`
- generated event counts are missing or inconsistent with evidence
- final-state particle cut is missing
- events after final-state cuts are missing
- feature table lacks ordering
- feature table lacks units
- preprocessing/standardization is missing
- trained algorithms lack self-contained descriptions
- hyperparameter table is missing
- anchor operator is missing
- final algorithm is not selected by the first non-zero operator
- final constraints use per-operator best algorithms without explicit user request
- numeric fit coefficients are missing
- significance formula symbols are undefined
- report uses a significance formula inconsistent with `significance-reference.md`
- constraint bounds are not described as real roots with upper = smallest positive
  real root and lower = largest negative real root
- required toolchain citations are missing
- foundational SMEFT/aQGC/ML-in-HEP references are available but none are cited
- `literature_plan.json` is missing role groups for `toolchain`,
  `foundational`, `comparison_citations`, and `section_usage`
- `reference_paper_plan.json` is missing when user-list comparison papers are available

Mark these as `minor`:

- figure captions are too terse
- optional fit-quality metrics are unavailable
- HTML styling is plain but readable
- Feynman diagrams are unavailable but the absence is documented

## Output Requirements

`report_validation.json` must include:

```json
{
  "status": "pass | issues_remaining",
  "drafts_written": 3,
  "max_revisions": 2,
  "major_issues": [],
  "minor_issues": [],
  "continued_to_cleanup": true
}
```

The final report may be delivered with remaining issues only when the revision
limit has been reached and the issues are archived.

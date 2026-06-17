# Manuscript Validation Guide

Validate the manuscript after every draft. Write validation output to
`results/data/phase10/manuscript_validation.json`.

## Revision Loop

Use a bounded loop:

1. Draft `manuscript_draft_v1`.
2. Validate.
3. If validation fails, revise and write `manuscript_draft_v2`.
4. Validate.
5. If validation still fails, revise once more and write the final manuscript.
6. Validate the final manuscript and archive remaining issues.

Maximum revisions after the first draft: `2`.

Never block cleanup or Phase 11 because the manuscript remains imperfect. After the
revision limit, write `manuscript_validation.json` with `status: "issues_remaining"`
and continue to cleanup and audit.

The revision limit applies only to manuscript-writing quality issues. Missing
upstream required artifacts, missing required data tables, missing required
plots when the underlying data exists, or missing final PDF/HTML format
deliverables must trigger repair of the responsible phase artifact or produce a
Phase 11 `FAIL`; do not hide them as acceptable `issues_remaining`.

## Blocking During Phase 10

Stop only for unrecoverable file-writing, parser, or output-generation errors.
Scientific/style validation failures are not stop conditions after the revision
limit.

## Required Checks

First inspect `results/data/phase10/manuscript_checklist.json`. Any checklist
item marked `missing` while the corresponding evidence field is non-null is a
validation issue.

Mark these as `major` if they fail:

- `manuscript_build_environment.json` is missing target/local LaTeX probe
  results or the `pdf_required` field
- `pdf_required=true` but the final non-empty `results/manuscript.pdf` and
  `results/manuscript.tex` are missing
- HTML is treated as the final deliverable even though target or local LaTeX is
  available
- manuscript uses approximate event counts such as `~2500`
- requested event counts or actual loaded LHCO event counts are missing or inconsistent with evidence
- manuscript uses banner event counts as actual event counts
- selection efficiencies do not state or use actual LHCO loaded counts as denominators
- final-state particle cut is missing
- events after final-state cuts are missing
- dataset table is missing loaded events, final-state-cut surviving events, raw
  cross-sections, final-state-cut cross-sections, or the exact cut expression
- feature table lacks ordering
- feature table lacks units
- preprocessing/standardization is missing
- trained algorithms lack self-contained descriptions
- trained algorithms lack pseudocode
- trained algorithms lack clear mathematical score definitions
- hyperparameter table is missing
- anchor operator is missing
- final algorithm is not selected by the first non-zero operator
- final constraints use per-operator best algorithms or thresholds
- numeric fit coefficients are missing
- manuscript treats the quadratic-fit constant term as a free fitted parameter
  instead of the fixed `f=0` selected cross-section after cuts/selection
- fit-coefficient table is missing globally claimed operators
- coefficient scan lower/upper bounds are missing
- required figures are missing while underlying data exists: Feynman diagrams,
  score histograms, anchor ROC, SM+NP fit comparisons, anchor S=2
  constraint-range-vs-threshold curve, or anchor S=2 algorithm-comparison bar
  plot
- significance formula symbols are undefined
- manuscript uses a significance formula inconsistent with `significance-reference.md`
- constraint bounds are not described as real roots with upper = smallest positive
  real root and lower = largest negative real root
- final expected constraint table is missing any globally claimed operator or
  any requested level among `S_stat = 2, 3, 5`
- required toolchain citations are missing
- foundational SMEFT/aQGC/ML-in-HEP references are available but none are cited
- `literature_plan.json` is missing role groups for `toolchain`,
  `foundational`, `comparison_citations`, and `section_usage`
- `reference_paper_plan.json` is missing when user-list comparison papers are available
- `manuscript_checklist.json` is missing or was not updated for the current draft
- Feynman diagrams are unavailable but missing reasons are not recorded per
  process and per SM/NP class in both `manuscript_evidence.json` and
  `manuscript_validation.json`

Mark these as `minor`:

- figure captions are too terse
- optional fit-quality metrics are unavailable
- HTML styling is plain but readable
- Feynman diagrams are unavailable but the absence is documented

## Output Requirements

`manuscript_validation.json` must include:

```json
{
  "status": "pass | issues_remaining",
  "drafts_written": 3,
  "max_revisions": 2,
  "checklist_path": "results/data/phase10/manuscript_checklist.json",
  "major_issues": [],
  "minor_issues": [],
  "continued_to_cleanup": true
}
```

The final manuscript may be delivered with remaining issues only when the revision
limit has been reached and the issues are archived.

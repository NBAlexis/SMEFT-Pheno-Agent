# Manuscript Validation Guide

Before formal validation, complete the three-pass manuscript completeness loop
defined in `phase10-manuscript.md`. Write validation output to
`results/data/phase10/manuscript_validation.json`.

## Revision Loop

Use a bounded loop:

1. Draft `manuscript_draft_v1`.
2. Run three completeness passes, each listing all missing required content and
   repairing missing items whose evidence exists.
3. Validate the resulting draft.
4. If validation fails, revise within the remaining revision budget.
5. Validate the final manuscript, repair every missing required item, and
   archive only remaining minor issues.

Maximum revisions after the first draft: `2`.

The revision limit applies only to optional prose and presentation improvements.
Missing upstream evidence, required content, required tables or plots, or the
required final format must trigger autonomous repair. Phase 10 cannot complete
until every frozen required item is present or satisfies its explicit allowed
missing-reason rule and `major_issues` is empty.

## Blocking During Phase 10

Treat file-writing, parser, and output-generation errors as technical recovery
tasks. Stop only with documented proof that the frozen manuscript deliverable
cannot be produced by any reasonable equivalent implementation.
Minor style issues are not stop conditions after the revision limit. Missing
required content remains a Phase 10 repair task.

## Required Checks

First inspect `results/data/phase10/manuscript_completeness_passes.json`,
`results/data/phase10/manuscript_checklist.json`, and
`results/data/phase10/manuscript_trace_map.json`. The checklist must contain
every required ID from `manuscript-checklist-required-ids.json`; the trace map
must contain the same IDs and point to both evidence and a manuscript location.
Missing IDs, missing trace records, or `present` items without manuscript
locations are major validation issues.

`manuscript_completeness_passes.json` must contain at least three pass records,
each with `missing_items`, `repair_actions`, and `remaining_missing_items`.

Any checklist item marked `missing` while the corresponding evidence field is
non-null is a validation issue.

Mark these as `major` if they fail:

- `manuscript_build_environment.json` is missing target/local LaTeX probe
  results or the `pdf_required` field
- manuscript is not organized as a scientific paper with clear sections covering
  motivation/background, theory/model, event generation and data preparation,
  ML methodology, event-selection optimization, numerical fits/constraints, and
  conclusions in a logical order
- `pdf_required=true` but the final non-empty `results/manuscript.pdf` and
  `results/manuscript.tex` are missing
- HTML is treated as the final deliverable even though target or local LaTeX is
  available
- manuscript uses approximate event counts such as `~2500`
- requested event counts or actual loaded LHCO event counts are missing or inconsistent with evidence
- the manuscript omits the `debug` setting, or `debug=true` is not identified as
  a reduced-event workflow test in the title page or front matter, abstract,
  numerical-results section, and conclusion
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
- anchor-comparison provenance is missing, or the reported final strategy does
  not follow the Phase 9 scope, rationale, evidence, and recorded selections
- final constraints do not follow the recorded `selection_scope`, or a
  `per_operator_best` result omits an operator's selected algorithm or threshold
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
- `manuscript_checklist.json` omits a required checklist ID
- `manuscript_completeness_passes.json` is missing, has fewer than three passes,
  or fails to list missing items and repair actions for each pass
- `manuscript_trace_map.json` is missing, omits a required checklist ID, or
  lacks evidence/manuscript locations for a present item
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
  "completeness_passes": 3,
  "checklist_path": "results/data/phase10/manuscript_checklist.json",
  "major_issues": [],
  "minor_issues": [],
  "continued_to_cleanup": true
}
```

Use `status: "pass"` when `major_issues` and `minor_issues` are empty and every
required checklist ID is `present`. Use `status: "issues_remaining"` only when
every required checklist ID is `present`, `major_issues` is empty, and minor
writing or presentation issues remain after the revision budget.

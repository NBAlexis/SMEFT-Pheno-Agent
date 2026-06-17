# Manuscript Checklist

Use this checklist after each manuscript draft and before validation. For every
item, record `present`, `missing`, or `not_applicable` in
`results/data/phase10/manuscript_checklist.json`. If an item is missing and the
evidence contains the value, revise the manuscript before validating.

The JSON must include the checked draft path and one record per item:

```json
{
  "draft_path": "results/data/phase10/manuscript_draft_v2.tex",
  "items": [
    {"id": "data.actual_lhco_counts", "status": "present", "evidence_path": "results/data/phase10/manuscript_evidence.json", "note": ""}
  ]
}
```

## Physics Setup

- Process list is written exactly as studied, including multi-process `add process`
  cases.
- Collider type, beam energies, displayed `sqrt(s)`, luminosity, detector card,
  and toolchain versions are stated.
- UFO model, active coefficients/operators, and anchor operator are stated at
  the highest supported evidence level.
- Representative SM and NP Feynman diagrams are included or their absence is
  documented.
- Coefficient scan lower and upper bounds are reported for every globally claimed
  non-zero operator.

## Data Samples

- Requested event counts and actual loaded LHCO event counts are both reported
  for SM, pure NP, and scan samples.
- Actual event counts come from loaded LHCO files, not MG5 banners.
- Final-state particle cut is stated explicitly.
- Surviving event counts after final-state cuts are reported.
- A dataset table lists, for each dataset: loaded LHCO event count, event count
  after the final-state particle-number cut, raw cross-section, cross-section
  after the final-state particle-number cut, and the exact cut expression used.
- Threshold-passing counts and efficiency denominators are reported.
- Cross-sections before and after selection include units.
- Public CSV paths and score CSV paths are listed for SM, pure NP, and scan
  samples.

## Features and ML

- The feature list/table is included, ordered, and every feature has a unit or
  `dimensionless`.
- Feature definitions include particle ordering rules and derived formulas where
  applicable.
- Preprocessing/standardization method and fit sample are stated.
- Every trained algorithm has a self-contained description, hyperparameters,
  score meaning, train/test split, and random seed.
- Every trained algorithm has manuscript pseudocode.
- Every trained algorithm has a mathematical score definition `s(x)`, output
  range, and direction (`higher = more NP-like`).
- AUC and score-distribution evidence are discussed for SM versus each pure NP
  operator.
- Score histograms for SM and every globally claimed pure-NP operator are
  included.
- The anchor SM-vs-NP ROC plot is included.

## Selection and Fits

- The final event-selection strategy is selected only from the first non-zero
  anchor operator.
- The paper states that the same final algorithm and threshold are used for all
  operators in that collider configuration.
- Threshold scan range, selected threshold, and anchor-operator comparison are
  reported.
- For the anchor operator, the `S_stat = 2` expected coefficient constraint
  range as a function of threshold is plotted.
- Scan coefficient values and fitted curves are shown for each reported operator.
- SM+NP selected cross-section points are compared with fitted curves for every
  globally claimed operator.
- Numeric coefficients in
  `sigma(f) = sigma0_after_cut + f sigma_int + f^2 sigma_NP` are reported with
  units.
- The manuscript states that `sigma0_after_cut` is fixed from the `f=0` scan
  point after cuts/selection, not fitted.
- A fit-coefficient table covers every globally claimed operator.
- Fit quality or residual information is included if Phase 8 produced it;
  otherwise the manuscript states that no fit-quality diagnostic was retained.
- The anchor-operator `S_stat = 2` algorithm-comparison bar plot is included.

## Constraints and Citations

- Significance formula matches `significance-reference.md` and all symbols,
  luminosity units, and cross-section units are defined.
- Constraint bounds are described as real roots: upper is the smallest positive
  real root, lower is the largest negative real root.
- Final constraints at the requested significance levels use the anchor-selected
  algorithm.
- The final expected coefficient constraint table lists every globally claimed
  operator at `S_stat = 2, 3, 5`.
- Toolchain citations and relevant SMEFT/aQGC/nTGC/ML-in-HEP citations are
  included.
- User-provided comparison papers are cited only for direct comparisons or
  specific claims, not merely because they were used as writing references.

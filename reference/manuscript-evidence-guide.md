# Manuscript Evidence Guide

Build `results/data/phase10/manuscript_evidence.json` before writing prose. This file is
the source of truth for the manuscript. If a value is unavailable, record `null` and a
`missing_reason`; do not fill it with guesses.

## Evidence Schema

Required top-level keys:

| Key | Purpose |
|---|---|
| `run` | process, collider, energy, luminosity, debug mode, detector card, tool versions |
| `model_description` | models, claimed operators, UFO parameters, anchor operator |
| `datasets` | requested events, actual LHCO events, final-state cuts, surviving events, cross-sections |
| `features` | ordered ML feature list with units and preprocessing |
| `algorithms` | trained algorithms, hyperparameters, AUC, score interpretation |
| `selection` | threshold scan, selected threshold, efficiencies |
| `fits` | quadratic fit coefficients and scan points |
| `constraints` | final constraints at S=2,3,5 using the anchor-selected algorithm |
| `figures` | available figure paths, captions, and section placement |
| `reference_papers` | user-list papers used for writing style, method comparison, or result comparison |
| `citations` | mandatory toolchain citations and selected literature citations, grouped by role |

## Dataset Evidence

For every SM, anchor NP, and scan dataset, record:

- dataset id and purpose
- model and operator, if applicable
- requested event count from `run_config.json` as an integer
- actual loaded LHCO event count from `LoadLHCOlympics(...).GetEventCount()` as an integer
- final-state particle multiplicity cut, for example `N_gamma >= 1, N_j >= 2`
- surviving event count after the final-state cut as an integer
- ML/selection passing event count when a threshold is applied
- efficiencies with denominators stated explicitly
- cross-section before and after selection, with units
- public CSV path and score CSV path, when available
- composition: `SM only`, `SM + NP`, or `SM + NP + interference`

Approximate counts are invalid in the final paper. If only an approximate count is
available, write the exact evidence field as `null`, record the approximation in
`notes`, and let validation request a revision or flag a residual issue.

Do not use event counts from MG5 banners. Banner event counts may be requested
targets, not actual LHCO output. Selection efficiencies and selected
cross-sections must be normalized by actual loaded LHCO counts.

## Feature Evidence

Record features as an ordered list. Each feature must include:

- index, starting at 1
- code name used by the analysis
- paper symbol
- unit, or `dimensionless`
- physical definition
- particle assignment and ordering rule, such as leading photon by energy
- formula for derived quantities

Record preprocessing separately:

- `standardization`: `none`, `standard_scaler`, or another concrete method
- source sample used to fit preprocessing parameters
- whether the same preprocessing is applied to SM, NP, and scan samples

## Model Evidence for Arbitrary UFOs

Do not require a closed-form operator expression for arbitrary user UFOs.
Use the best available level:

| Level | Available information | Manuscript content |
|---|---|---|
| `formula` | trusted operator formula exists in references | formula and coefficient definition |
| `ufo_parameter` | param card block/index/name are known | UFO model, block, index, name, scan coefficient |
| `model_only` | only model and non-zero sensitivity are known | model name, process, sensitivity result, limitation note |

Never upgrade the level by inference.

## Fit Evidence

For every reported fit, record:

- operator
- algorithm
- threshold
- scan coefficient values
- fitted coefficients in `sigma(f) = sigma_SM + f sigma_int + f^2 sigma_NP`
- units for every coefficient
- fit quality if available: residuals, covariance, R2, or chi-square

The paper must include numeric fit coefficients. If unavailable, validation must
record a major issue.

## Citation Evidence

Record citation IDs from `literature_plan.json` by role:

- `toolchain`: tools actually used
- `foundational`: SMEFT/aQGC/nTGC/ML-in-HEP background references
- `comparison_citations`: user-list papers cited only because the manuscript makes a direct comparison or uses a specific claim
- `section_usage`: section-to-reference mapping

Do not put style-only reference papers into `citations`; record them under
`reference_papers` and `reference_paper_plan.json`.

## Comparison Evidence

Record reference-paper usage from `reference_paper_plan.json`:

- `style_references`: papers used to calibrate section structure and detail level
- `method_references`: papers used to compare method descriptions or workflow design
- `result_comparison_references`: papers whose numeric results are directly compared
- `papers_to_cite`: subset that must also appear in `literature_plan.json`

Using a paper as a style or method-format reference does not by itself require a
bibliography citation.

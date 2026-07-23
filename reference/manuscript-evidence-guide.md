# Manuscript Evidence Guide

Build `results/data/phase10/manuscript_evidence.json` before writing prose. This file is
the source of truth for the manuscript. If a value is unavailable, record `null` and a
`missing_reason`; do not fill it with guesses.

## Evidence Schema

Required top-level keys:

| Key | Purpose |
|---|---|
| `run` | process, collider, beam energies, displayed sqrt(s), luminosity, debug mode, detector card, tool versions |
| `model_description` | models, claimed operators, UFO parameters, anchor operator |
| `datasets` | requested events, actual LHCO events, final-state cuts, surviving events, cross-sections |
| `features` | ordered ML feature list with units and preprocessing |
| `algorithms` | trained algorithms, hyperparameters, AUC, score interpretation |
| `selection` | threshold scan, selected threshold, efficiencies |
| `fits` | quadratic fit coefficients and scan points |
| `constraints` | final constraints at S=2,3,5, recorded selection scope, and the algorithm and threshold used for each operator |
| `figures` | available figure paths, captions, and section placement |
| `reference_papers` | user-list papers used for writing style, method comparison, or result comparison |
| `citations` | mandatory toolchain citations and selected literature citations, grouped by role |

## Toolchain Evidence

Read `results/data/phase2/environment_manifest.json` for execution target,
validated paths, tool versions, probe commands, venv Python path, package
versions, model locations, and detector-card provenance. Do not reconstruct
tool versions from conversation text.

## Collider Energy Evidence

Use `run_configurations[*].ebeam1` and `run_configurations[*].ebeam2` as the
source of truth for beam energies in GeV. `sqrt(s)` is manuscript-only and must
be computed with:

```bash
python scripts/beam_energy.py --run-config {workdir}/results/run_config.json --json-out {workdir}/results/data/phase10/collider_energy.json
```

Read `sqrt_s_tev` from `collider_energy.json` for prose and tables. Do not
derive `sqrt(s)` inline and do not treat it as an MG5 runner input.

## Dataset Evidence

Read `results/data/phase8/dataset_summary.json` first. It is the preferred
source for the manuscript dataset table because it joins event counts,
final-state cuts, raw cross-sections, and final-state-cut cross-sections.

For every SM, anchor NP, and scan dataset, record:

- dataset id and purpose
- model and operator, if applicable
- requested event count from `run_config.json` as an integer
- actual loaded LHCO event count from `LoadLHCOlympics(...).GetEventCount()` as an integer
- event-count recovery attempts, merged outputs, and merged cross-sections, if recovery was triggered
- final-state particle multiplicity cut, for example `N_gamma >= 1, N_j >= 2`
- surviving event count after the final-state cut as an integer
- ML/selection passing event count when a threshold is applied
- efficiencies with denominators stated explicitly
- cross-section before and after selection, with units
- public CSV path and score CSV path
- composition: `SM only`, `SM + NP`, or `SM + NP + interference`

Also build a dataset-summary table for the manuscript. Each row must include:
dataset id, loaded LHCO event count, event count after the final-state
particle-number cut, raw cross-section, cross-section after the final-state
particle-number cut, units, and the exact final-state cut expression. The
post-final-state-cut cross-section uses the final-state-cut efficiency, not the
ML score threshold.

Approximate counts are invalid in the final paper. If only an approximate count is
available, write the exact evidence field as `null`, record the approximation in
`notes`, and let validation request a revision or flag a residual issue.

Do not use event counts from MG5 banners. Banner event counts may be requested
targets, not actual LHCO output. Selection efficiencies and selected
cross-sections must be normalized by actual loaded LHCO counts.

## Feature Evidence

Read `results/data/phase7/feature_schema.json`; do not reconstruct the feature
order or units from memory.

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

## Algorithm Evidence

Read `results/data/phase7/algorithm_descriptions.json` and
`results/data/phase7/algorithm_comparison.json`.

For every trained algorithm, record:

- algorithm name and implementation class
- short self-contained method description
- hyperparameters used in training
- pseudocode suitable for the manuscript
- exact score definition used by `compute_scores.py`, written as a mathematical
  function `s(x)` with output range and direction (`higher = more NP-like`)
- AUC on the anchor SM-vs-NP test set
- ROC figure path
- score-histogram figure path for SM and every globally claimed pure-NP operator

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
- coefficient scan lower and upper bounds
- fixed `sigma0_after_cut` from the shared `f5` pool after cuts/selection,
  including its source operators, additional anchor rounds, observed passing
  count, and any half-event convention
- fitted coefficients in
  `sigma(f) = sigma0_after_cut + f sigma_int + f^2 sigma_NP`
- `fit_intercept_fixed=true` and `f0_label="f5"` for the standard 11-point scan
- units for every coefficient
- fit quality if Phase 8 retained it: residuals, covariance, R2, or chi-square
- SM+NP selected cross-section versus fit figure path

The paper must include numeric fit coefficients. If unavailable, validation must
record a major issue.

## Figure Evidence

Record figure paths and captions for:

- representative Feynman diagrams for SM and NP, or documented missing reasons
- SM-vs-anchor-NP ROC plot
- score histograms comparing SM with every globally claimed pure-NP operator
- SM+NP selected cross-section points versus fitted curve for every globally
  claimed operator
- anchor-operator `S_stat = 2` expected coefficient constraint range versus
  threshold
- anchor-operator `S_stat = 2` algorithm-comparison bar plot

If a required figure is unavailable but the underlying data exists, create the
figure before drafting. If the underlying data is missing, record the missing
reason and let validation flag the issue.

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

# Manuscript Sections Guide

Write a self-contained paper. The reader should understand the physics process,
dataset construction, ML method, event selection, fit, and constraints without
reading the workflow logs.

## Abstract

Include process, collider energy, luminosity, model family, recorded selection
scope, selected algorithm or algorithms, and the main constraints. Do not
mention workflow internals.

## Introduction

Establish the research question:

- why new-physics searches benefit from efficient event selection
- why the selected process and final state are relevant
- why ML-assisted event selection is useful for high-dimensional kinematics
- how this study differs from or extends prior aQGC/nTGC/ML studies

Use citations selected by `literature_plan.json`. Do not claim aQGC/nTGC/SMEFT
relationships more strongly than the model evidence supports.

## Theoretical Framework

Describe the model at the highest supported evidence level:

- formula-level operator definitions when available
- otherwise a UFO-parameter table with model, block, index, name, and scan unit
- state that one coefficient is varied at a time unless the run config says otherwise
- state which operator is the first non-zero anchor operator

If operator formulas are unavailable, say so plainly and do not invent them.

## Event Generation and Data Preparation

Mandatory content:

- MG5, UFO, Pythia/Delphes/root2lhco/CutExperiment tool chain with citations
- detector card and collider setup
- exact requested event counts and actual loaded LHCO event counts
- exact final-state particle cut
- exact surviving event counts after that cut
- dataset table with loaded events, final-state-cut surviving events, raw
  cross-section, final-state-cut cross-section, and the exact cut expression
- threshold-passing counts and efficiency denominators for selected samples
- public CSV data paths for SM, pure NP, and scan samples
- dataset composition table for SM, anchor NP, and scans
- scan coefficient table with all 11 points
- scan coefficient lower/upper bounds for every globally claimed non-zero
  operator
- representative Feynman diagrams, or a documented missing-diagram reason

Final-state cuts, event counts, and efficiency denominators must be written in
the main text or tables, not only implied by feature names.

## Machine Learning Methodology

For each trained algorithm, provide a compact self-contained description:

- what object the algorithm learns
- how the score is interpreted
- the mathematical score definition `s(x)` and its output range
- relevant hyperparameters
- preprocessing and standardization
- train/test split and random seed
- concise pseudocode

The manuscript must include pseudocode and a clear score definition for every
trained algorithm. A reader should understand how each score is constructed and
why larger scores mean more NP-like events.

## Event Selection Optimization

State that algorithms are evaluated on the first non-zero anchor operator.
The selected production algorithm is the anchor algorithm with the narrowest
S=2 constraint width after threshold optimization.

Manuscript:

- threshold scan range
- selected threshold for each algorithm
- SM and NP efficiencies
- constraint-width comparison on the anchor operator
- bar plot comparing anchor-operator `S_stat = 2` interval widths for all
  trained algorithms
- curve showing the anchor operator's `S_stat = 2` expected coefficient
  constraint range as a function of threshold
- final selection scope and selected algorithm or algorithms

Do not choose a different best algorithm or threshold separately for each
operator.

## Numerical Results and Expected Constraints

Include:

- quadratic fit equation
- statement that the fit intercept is fixed to the `f=0` selected
  cross-section after cuts/selection
- numeric fit coefficients with units
- scan points and fitted curves
- fit-coefficient table for every globally claimed operator
- SM+NP selected cross-section points compared with fitted curves for every
  globally claimed operator
- significance formula from [`significance-reference.md`](significance-reference.md), with all symbols defined
- final constraint table for every globally claimed operator at S=2,3,5 using
  the algorithm and threshold recorded for each operator by the final selection scope
- optional comparison table for non-selected algorithms, clearly labeled

When discussing constraint intervals, state that the upper bound is the smallest
positive real root and the lower bound is the largest negative real root of the
significance equation. Do not present complex roots as physical constraints.

For significance thresholds, larger S generally requires a larger coefficient
deviation to reach discovery/evidence. Do not enforce a monotonicity rule that
contradicts the actual significance definition.

## Conclusions

Summarize the anchor algorithm, main constraints, and practical interpretation.
Do not introduce new numbers, figures, or unsupported comparison claims.

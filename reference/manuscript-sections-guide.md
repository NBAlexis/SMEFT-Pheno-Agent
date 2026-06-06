# Manuscript Sections Guide

Write a self-contained paper. The reader should understand the physics process,
dataset construction, ML method, event selection, fit, and constraints without
reading the workflow logs.

## Abstract

Include process, collider energy, luminosity, model family, anchor-selected
algorithm, and the main constraints. Do not mention workflow internals.

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
- exact generated event counts
- exact final-state particle cut
- exact surviving event counts after that cut
- dataset composition table for SM, anchor NP, and scans
- scan coefficient table with all 11 points
- representative Feynman diagrams when available

Final-state cuts and event counts must be written in the main text or tables,
not only implied by feature names.

## Machine Learning Methodology

For each trained algorithm, provide a compact self-contained description:

- what object the algorithm learns
- how the score is interpreted
- relevant hyperparameters
- preprocessing and standardization
- train/test split and random seed

Pseudocode is not required. A reader should still understand how each score is
constructed and why it can separate SM-like and NP-like events.

## Event Selection Optimization

State that algorithms are evaluated on the first non-zero anchor operator.
The selected production algorithm is the anchor algorithm with the narrowest
S=2 constraint width after threshold optimization.

Manuscript:

- threshold scan range
- selected threshold for each algorithm
- SM and NP efficiencies
- constraint-width comparison on the anchor operator
- final anchor-selected algorithm

Do not choose a different best algorithm separately for each operator unless the
user explicitly requested per-operator selection.

## Numerical Results and Expected Constraints

Include:

- quadratic fit equation
- numeric fit coefficients with units
- scan points and fitted curves
- significance formula from [`significance-reference.md`](significance-reference.md), with all symbols defined
- final constraints at S=2,3,5 using the anchor-selected algorithm
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

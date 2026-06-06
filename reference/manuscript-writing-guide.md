# Manuscript Writing Guide

Phase 10 writes a publication-style HEP phenomenology paper, not a workflow summary.
The paper may be LaTeX/PDF or HTML; both formats must follow the same scientific
content standard.

## Required Reading Order

Read these files in order during Phase 10:

1. [`manuscript-evidence-guide.md`](manuscript-evidence-guide.md): build the structured facts before drafting.
2. [`manuscript-sections-guide.md`](manuscript-sections-guide.md): write each paper section from the evidence.
3. [`manuscript-comparison-guide.md`](manuscript-comparison-guide.md): select user-list papers for writing/comparison guidance.
4. [`manuscript-citation-guide.md`](manuscript-citation-guide.md): select actual citations from the toolchain and literature bank.
5. [`manuscript-literature-bank.md`](manuscript-literature-bank.md): use the SMEFT/aQGC/nTGC/ML-in-HEP citation warehouse.
6. [`significance-reference.md`](significance-reference.md): use the shared significance and root-selection rules.
7. [`manuscript-validation-guide.md`](manuscript-validation-guide.md): validate and revise with a bounded retry loop.

## Paper Structure

Use this section order unless the user explicitly requested a different journal format:

1. Abstract
2. Introduction
3. Theoretical Framework
4. Event Generation and Data Preparation
5. Machine Learning Methodology
6. Event Selection Optimization
7. Numerical Results and Expected Constraints
8. Conclusions
9. References

## Hard Rules

- Draft only from `manuscript_evidence.json`, `reference_paper_plan.json`, `literature_plan.json`, and existing result files.
- Do not replace missing exact values with approximate text such as `~2500`.
- Do not invent mathematical operator definitions for arbitrary UFO models.
- When exact operator formulas are unavailable, describe the UFO parameter at model/block/index/name level.
- Treat HTML as a formal paper output when LaTeX is unavailable.
- The final constraints must use the algorithm selected by the first non-zero operator unless the user explicitly requested per-operator algorithm selection.
- The significance formula and constraint-root rules must match [`significance-reference.md`](significance-reference.md).
- The reference-paper plan must not force user-list papers into the bibliography; cite them only when the manuscript makes a direct comparison or uses a specific claim.
- The literature plan must use role-based citation groups and include relevant arXiv identifiers from [`manuscript-literature-bank.md`](manuscript-literature-bank.md).
- Validation failures are revision inputs, not stop conditions. After the bounded revision loop, archive remaining issues and continue to cleanup and audit.

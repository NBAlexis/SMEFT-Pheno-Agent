# Manuscript Writing Guide

Phase 10 writes a publication-style HEP phenomenology paper, not a workflow summary.
The final paper must be PDF when `pdflatex` or `latexmk` is available on either
the execution target or the local control environment. HTML must follow the
same scientific content standard, but it is only a fallback when both LaTeX
probes fail.

## Step-Specific References

Do not load every manuscript reference at the start of Phase 10. Load each file
when its step begins:

| Phase 10 step | References |
|---|---|
| Build evidence | [`manuscript-evidence-guide.md`](manuscript-evidence-guide.md) |
| Plan comparisons and citations | [`manuscript-comparison-guide.md`](manuscript-comparison-guide.md), then [`manuscript-citation-guide.md`](manuscript-citation-guide.md) and [`manuscript-literature-bank.md`](manuscript-literature-bank.md) as directed |
| Draft | [`manuscript-sections-guide.md`](manuscript-sections-guide.md) and [`significance-reference.md`](significance-reference.md) |
| Check and revise | [`manuscript-checklist.md`](manuscript-checklist.md) and [`manuscript-validation-guide.md`](manuscript-validation-guide.md) |

This changes only when instructions enter context. It does not remove any
manuscript evidence, section, citation, equation, checklist, or validation
requirement.

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
- Treat HTML as a formal paper output only when both target and local LaTeX are
  unavailable. If either side has `pdflatex` or `latexmk`, the final deliverable
  must include `manuscript.pdf` and `manuscript.tex`.
- The final constraints must use the Phase 9 selection scope exactly. Treat the
  anchor-selected common strategy as the default, and explain the recorded
  scientific reason when a user-requested or evidence-driven per-operator
  strategy is used.
- The significance formula and constraint-root rules must match [`significance-reference.md`](significance-reference.md).
- The reference-paper plan must not force user-list papers into the bibliography; cite them only when the manuscript makes a direct comparison or uses a specific claim.
- The literature plan must use role-based citation groups and include relevant arXiv identifiers from [`manuscript-literature-bank.md`](manuscript-literature-bank.md).
- The manuscript checklist must be run after every draft; missing checklist items with available evidence are revision targets.
- Validation failures are revision inputs, not stop conditions. After the bounded revision loop, archive remaining issues and continue to cleanup and audit.

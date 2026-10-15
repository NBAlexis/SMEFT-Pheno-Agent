# Manuscript Writing Guide

Phase 10 writes a publication-style HEP phenomenology paper, not a workflow summary.
The quality target is a coherent scientific argument comparable in completeness
to a research article: the reader should understand the question, the analysis
design, the evidence, what the results mean, and where the conclusions stop.
The final paper must be PDF when `pdflatex` or `latexmk` is available on either
the execution target or the local control environment. HTML must follow the
same scientific content standard, but it is only a fallback when both LaTeX
probes fail.

For `debug=true`, preserve the complete paper structure but label the title page
or front matter, abstract, numerical-results section, and conclusion as a
reduced-event workflow test. Do not present its constraints as statistically
reliable or publication-ready. For `debug=false`, write the normal
publication-quality manuscript.

## Step-Specific References

Do not load every manuscript reference at the start of Phase 10. Load each file
when its step begins:

| Phase 10 step | References |
|---|---|
| Build evidence | [`manuscript-evidence-guide.md`](manuscript-evidence-guide.md) |
| Plan comparisons and citations | [`manuscript-comparison-guide.md`](manuscript-comparison-guide.md), then [`manuscript-citation-guide.md`](manuscript-citation-guide.md) and [`manuscript-literature-bank.md`](manuscript-literature-bank.md) as directed |
| Blueprint and draft | [`manuscript-sections-guide.md`](manuscript-sections-guide.md), [`manuscript-comparison-guide.md`](manuscript-comparison-guide.md), and [`significance-reference.md`](significance-reference.md) |
| Check and revise | [`manuscript-checklist.md`](manuscript-checklist.md) and [`manuscript-validation-guide.md`](manuscript-validation-guide.md) |

This changes only when instructions enter context. It does not remove any
manuscript evidence, section, citation, equation, checklist, or validation
requirement.

## Terms used in Phase 10

- **Manuscript blueprint**: a JSON plan made before drafting. It states the
  research question, contribution, section purposes, claims, evidence paths,
  planned interpretation, and limitations. It guides writing but does not
  change the frozen research objective.
- **Argument map**: the same manuscript-blueprint artifact viewed as a map from
  claims to evidence and planned explanation; it is not a second file or a
  second contract.
- **Result ledger**: the blueprint list in which each important result has four
  separate statements: the observed result, its interpretation, its relevant
  comparison or context, and its limitation, plus evidence paths.
- **Applicability review**: a recorded decision for a possible analysis (for
  example fit quality, finite Monte Carlo uncertainty, EFT validity, systematic
  effects, or an external comparison). `completed` means evidence is discussed;
  `not_applicable` means the question does not apply to this study;
  `not_implemented` means it could matter but was not performed and must be
  stated as a limitation.
- **Quality review**: the final prose-level check that the paper answers its
  question, aligns claims with evidence, interprets important results, reports
  applicable robustness information, and states its scope and limitations.
- **Evidence path**: a repository-relative path (optionally with a JSON field
  fragment) to an artifact that supports a planned claim or number.

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
- Draft from `manuscript_blueprint.json` as the argument and section map. The
  blueprint must point back to evidence; it is not permission to add unsupported
  numbers or claims.
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

## Scientific-paper quality bar

The manuscript must do more than enumerate phase outputs. Before drafting,
identify the central question and the paper's contribution. For each important
result, connect the numerical observation to an interpretation, a relevant
comparison or context, and a limitation. This is especially important for the
choice of algorithm/threshold, the fitted coefficient dependence, the final
coefficient intervals, and any result that differs between operators.

Use a separate applicability review for questions such as finite-MC
uncertainty, fit quality, EFT validity, systematic effects, external-result
comparison, or data-quality anomalies. Perform an analysis when the evidence and
research question make it relevant; otherwise record why it is not applicable or
was not implemented and state the consequence. Do not add a decorative section
with invented results just to resemble another paper.

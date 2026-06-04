# Phase 10: Generate Publication-Quality Report

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE - once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose

Generate a self-contained HEP phenomenology paper from structured evidence. The
paper may be LaTeX/PDF or HTML. HTML is a valid final format when LaTeX is not
available.

Phase 10 must not write a loose workflow summary. It must first build evidence,
then draft, validate, revise with a bounded loop, and archive remaining issues.

## Prerequisite

Load the configuration:

```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
logger.phase_start("10")
```

Read the report guides in this order:

1. [`report-writing-guide.md`](report-writing-guide.md)
2. [`report-evidence-guide.md`](report-evidence-guide.md)
3. [`report-sections-guide.md`](report-sections-guide.md)
4. [`report-comparison-guide.md`](report-comparison-guide.md)
5. [`report-citation-guide.md`](report-citation-guide.md)
6. [`report-literature-bank.md`](report-literature-bank.md)
7. [`significance-reference.md`](significance-reference.md)
8. [`report-validation-guide.md`](report-validation-guide.md)

## Step 10.1: Select Output Format

```python
with workflow_step(logger, "10", "select_report_format", inputs={}):
```

Use LaTeX/PDF when `pdflatex` is available. Otherwise generate HTML.

HTML requirements:

- render formulas with MathJax or equivalent
- use readable paper-style CSS
- reference figures clearly with captions
- prefer linked/copied local figure files over enormous base64 blobs when possible
- include bibliography and section numbering

## Step 10.2: Build Paper Evidence

```python
with workflow_step(logger, "10", "build_paper_evidence",
                   inputs={"source": "results/data"}):
```

Create:

```
results/data/phase10/paper_evidence.json
```

Follow [`report-evidence-guide.md`](report-evidence-guide.md). The evidence must
include exact event counts, final-state cuts, ordered features with units,
preprocessing, algorithm metadata, fit coefficients, constraints, figures, and
citations.

If a required value is unavailable, record `null` and `missing_reason`. Do not
write approximate values into the evidence as exact facts.

## Step 10.3: Build Reference-Paper and Literature Plans

```python
with workflow_step(logger, "10", "build_reference_and_literature_plans",
                   inputs={"reference_papers": True}):
```

Create both files:

```
results/data/phase10/reference_paper_plan.json
results/data/phase10/literature_plan.json
```

Follow [`report-comparison-guide.md`](report-comparison-guide.md) for
`reference_paper_plan.json`. User-list papers are writing/comparison references,
not default citations.

Follow [`report-citation-guide.md`](report-citation-guide.md) for
`literature_plan.json`. Include mandatory toolchain citations and foundational
SMEFT/aQGC/nTGC/ML-in-HEP citations. Add user-list papers only under
`comparison_citations` when the final report directly compares with that paper
or relies on a specific claim from it.

## Step 10.4: Draft the Paper

```python
with workflow_step(logger, "10", "draft_report",
                   inputs={"format": report_format}):
```

Write `report_draft_v1.html` or `report_draft_v1.tex` from:

- `paper_evidence.json`
- `reference_paper_plan.json`
- `literature_plan.json`
- the section rules in [`report-sections-guide.md`](report-sections-guide.md)

Mandatory paper content:

- exact generated event counts
- exact final-state particle cut
- exact surviving event counts after the cut
- ordered feature table with units
- preprocessing/standardization statement
- self-contained descriptions of all trained algorithms
- threshold optimization and efficiencies
- numeric fit coefficients with units
- final constraints using the anchor-selected algorithm from Phase 9
- adequate references

Do not use text such as `~2500` for event counts. Do not choose a different
final algorithm per operator unless the user requested that mode.

## Step 10.5: Validate and Revise

```python
with workflow_step(logger, "10", "validate_and_revise_report",
                   inputs={"max_revisions": 2}):
```

Follow [`report-validation-guide.md`](report-validation-guide.md).

Bounded loop:

1. Validate draft v1.
2. If validation fails, revise to draft v2.
3. Validate draft v2.
4. If validation fails, revise once more and write the final report.
5. Validate the final report and archive remaining issues.

Maximum revisions after the first draft: `2`.

Validation failures do not block cleanup or Phase 11 after the revision limit.
Write:

```
results/data/phase10/report_validation.json
```

with `status: "pass"` or `status: "issues_remaining"`.

## Feynman Diagram Evidence

Collect representative diagrams during Step 10.2 before drafting, when available
from the anchor model process directories:

| Process type | Location |
|---|---|
| SM baseline | `{mg5path}/{folder_base}_{anchor_model}_p4_SM/SubProcesses/P*/` |
| NP sample | `{mg5path}/{folder_base}_{anchor_model}_p5_NP/SubProcesses/P*/` |

Copy selected diagrams to:

```
results/data/feynman_diagrams/
```

If diagrams are unavailable, document the missing reason in `paper_evidence.json`
and `report_validation.json`; do not block report generation.

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/report.pdf`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/report.pdf       # if LaTeX succeeds
results/report.tex       # if LaTeX is used
results/report.html      # if HTML fallback is used
results/data/phase10/
  paper_evidence.json
  reference_paper_plan.json
  literature_plan.json
  report_validation.json
  report_draft_v1.*
  report_draft_v2.*      # if needed
  report_draft_v3.*      # if the second revision is needed
```

```python
logger.phase_complete("10")
```

## Phase Transition

After the final report and validation file are written:

1. Log remaining validation issues, if any.
2. Proceed immediately to cleanup and then Phase 11.
3. Do not ask for confirmation, present options, or wait for user input.

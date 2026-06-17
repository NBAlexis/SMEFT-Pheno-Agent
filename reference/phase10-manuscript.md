# Phase 10: Generate Publication-Quality Manuscript

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE - once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose

Generate a self-contained HEP phenomenology manuscript from structured evidence.
The final manuscript must be PDF whenever any usable LaTeX toolchain is
available on either the selected execution target or the local control
environment. HTML is a fallback format only when both places lack usable
`pdflatex`/`latexmk`.

Phase 10 must not write a loose workflow summary. It must read the manuscript
guides, build evidence, draft, validate, revise with a bounded loop, and archive
remaining issues.

## Prerequisite

Load the configuration:

```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")

from scripts.workflow_logger import WorkflowLogger, workflow_step
logger = WorkflowLogger(config.workdir)
logger.phase_start("10")
```

Read the manuscript guides in this order:

1. [`manuscript-writing-guide.md`](manuscript-writing-guide.md)
2. [`manuscript-evidence-guide.md`](manuscript-evidence-guide.md)
3. [`manuscript-sections-guide.md`](manuscript-sections-guide.md)
4. [`manuscript-comparison-guide.md`](manuscript-comparison-guide.md)
5. [`manuscript-citation-guide.md`](manuscript-citation-guide.md)
6. [`manuscript-literature-bank.md`](manuscript-literature-bank.md)
7. [`significance-reference.md`](significance-reference.md)
8. [`manuscript-checklist.md`](manuscript-checklist.md)
9. [`manuscript-validation-guide.md`](manuscript-validation-guide.md)

## Step 10.1: Select Manuscript Build Environment

```python
with workflow_step(logger, "10", "select_manuscript_build_environment", inputs={}):
```

Check LaTeX in both places before choosing the manuscript format. This check is
mandatory even if an HTML draft already exists.

1. **Target environment**: run on the selected MG5 execution target with
   `scripts/remote_exec.py --config {local_run_config}`:
   ```bash
   sh -lc 'command -v latexmk || command -v pdflatex'
   ```
2. **Local control environment**: run locally where the agent controls files:
   ```bash
   latexmk --version
   pdflatex --version
   ```
   This local check may run on a native Windows control host. That exception is
   only for compiling the synced manuscript, figures, and data; MG5/Delphes
   execution still requires Linux through local Linux, SSH, or WSL2.

Selection rules:

- If target LaTeX exists, build LaTeX/PDF on the target and write
  `{workdir}/results/manuscript.tex` and `{workdir}/results/manuscript.pdf`.
- Else if local LaTeX exists, copy required Phase 10 inputs from the target to a
  local build directory with `scripts/sync_from_target.py`, build the PDF
  locally, then copy `manuscript.tex` and `manuscript.pdf` back to the target
  with `scripts/sync_to_target.py`.
- Else generate `manuscript.html` on the target.

Hard format rule: if either `target_latex_available=true` or
`local_latex_available=true`, `pdf_required=true` and Phase 10 is incomplete
until `results/manuscript.pdf` and `results/manuscript.tex` exist and are
non-empty. Do not choose HTML merely because the target lacks LaTeX when local
LaTeX is available. Do not treat an existing `manuscript.html` as satisfying
Phase 10 when `pdf_required=true`.

Record the probes, selected format, and reason in
`results/data/phase10/manuscript_build_environment.json`:

```json
{
  "target_latex_available": true,
  "local_latex_available": false,
  "pdf_required": true,
  "selected_format": "pdf",
  "build_location": "target",
  "target_probe": {"command": "sh -lc 'command -v latexmk || command -v pdflatex'", "returncode": 0},
  "local_probe": {"commands": ["latexmk --version", "pdflatex --version"], "available": false},
  "html_allowed": false,
  "reason": "target LaTeX is available"
}
```

HTML requirements:

- render formulas with MathJax or equivalent
- use readable paper-style CSS
- reference figures clearly with captions
- prefer linked/copied local figure files over enormous base64 blobs when possible
- include bibliography and section numbering

## Step 10.2: Build Manuscript Evidence

Relevant invariants:
[`workflow-invariants.md`](workflow-invariants.md) Single Selection Strategy,
Publication Data, and Actual Event Counts.

```python
with workflow_step(logger, "10", "build_manuscript_evidence",
                   inputs={"source": "results/data"}):
```

Create:

```
results/data/phase10/manuscript_evidence.json
results/data/phase10/collider_energy.json
```

Follow [`manuscript-evidence-guide.md`](manuscript-evidence-guide.md). The
evidence must include exact requested event counts, actual LHCO event counts,
final-state cuts, ordered features with units, preprocessing, algorithm
metadata, fit coefficients, constraints, figures, and citations.

Required structured sources:

```
results/data/phase2/environment_manifest.json
results/data/phase7/feature_schema.json
results/data/phase7/algorithm_descriptions.json
results/data/phase8/dataset_summary.json
```

Use `scripts/beam_energy.py` to populate `collider_energy.json` from the active
`run_config.json`; do not recompute `sqrt(s)` in prose or by hand.

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

Follow [`manuscript-comparison-guide.md`](manuscript-comparison-guide.md) for
`reference_paper_plan.json`. User-list papers are writing/comparison references,
not default citations.

Follow [`manuscript-citation-guide.md`](manuscript-citation-guide.md) for
`literature_plan.json`. Include mandatory toolchain citations and foundational
SMEFT/aQGC/nTGC/ML-in-HEP citations. Add user-list papers only under
`comparison_citations` when the final manuscript directly compares with that
paper or relies on a specific claim from it.

## Step 10.4: Draft the Manuscript

```python
with workflow_step(logger, "10", "draft_manuscript",
                   inputs={"format": manuscript_format}):
```

Write `manuscript_draft_v1.html` or `manuscript_draft_v1.tex` from:

- `manuscript_evidence.json`
- `reference_paper_plan.json`
- `literature_plan.json`
- the section rules in [`manuscript-sections-guide.md`](manuscript-sections-guide.md)

Mandatory manuscript content:

- representative Feynman diagrams, or a documented missing-diagram reason
- coefficient scan lower/upper bounds for every globally claimed non-zero
  operator
- exact requested event counts and actual loaded LHCO event counts
- event-count recovery attempts when actual LHCO counts required recovery
- exact final-state particle cut
- exact surviving event counts after the cut
- dataset table with loaded event counts, final-state-cut surviving counts, raw
  cross-sections, final-state-cut cross-sections, and the exact final-state cut
- threshold-passing counts and explicit efficiency denominators
- public CSV and score CSV data-release paths for SM, pure NP, and scan samples
- ordered feature table with units
- preprocessing/standardization statement
- self-contained descriptions of all trained algorithms
- pseudocode for every trained ML algorithm
- mathematical score definition for every trained ML algorithm
- threshold optimization and efficiencies
- anchor-operator `S_stat = 2` expected coefficient constraint range versus
  threshold plot
- fixed `f=0` selected cross-section and numeric fit coefficients with units
- score histograms for SM and every globally claimed pure-NP operator
- anchor SM-vs-NP ROC plot
- SM+NP selected cross-section points compared with fitted curves for every
  globally claimed operator
- fit-coefficient table covering every globally claimed operator
- anchor-operator `S_stat = 2` algorithm-comparison bar plot
- final `S_stat = 2, 3, 5` constraint table for all globally claimed operators
  using the anchor-selected algorithm from Phase 9
- adequate references

Do not use text such as `~2500` for event counts. Do not use event counts from
MG5 banners as actual generated counts. Do not choose a different final
algorithm per operator unless the user requested that mode.

## Step 10.5: Validate and Revise

```python
with workflow_step(logger, "10", "validate_and_revise_manuscript",
                   inputs={"max_revisions": 2}):
```

Before each validation pass, run the checklist in
[`manuscript-checklist.md`](manuscript-checklist.md) and write:

```
results/data/phase10/manuscript_checklist.json
```

If a checklist item is missing and the required evidence exists, revise before
calling the draft valid. Then follow
[`manuscript-validation-guide.md`](manuscript-validation-guide.md).

Bounded loop:

1. Validate draft v1.
2. If validation fails, revise to draft v2.
3. Validate draft v2.
4. If validation fails, revise once more and write the final manuscript.
5. Validate the final manuscript and archive remaining issues.

Maximum revisions after the first draft: `2`.

Validation failures do not block cleanup or Phase 11 after the revision limit.
Write:

```
results/data/phase10/manuscript_validation.json
```

with `status: "pass"` or `status: "issues_remaining"`.

## Feynman Diagram Evidence

Collect representative diagrams during Step 10.2 before drafting from the
process directories recorded in runner result manifests:

| Process type | Location |
|---|---|
| SM baseline | `process_dir/SubProcesses/P*/` from the SM runner manifest |
| NP sample | `process_dir/SubProcesses/P*/` from the anchor NP runner manifest |

Use retained Phase 5 and Phase 6 runner manifests first:

```
results/data/phase5/sm_result.json
results/data/phase5/np_o_*_result.json
results/data/phase6/np_o_*_scan_result.json
```

Copy selected diagrams to:

```
results/data/feynman_diagrams/
```

For a multi-process `run_config.process` list, inspect the MG5 process folders
and diagram filenames/subprocess directories to match diagrams back to each
input process. Ensure that each requested process has at least one
representative SM diagram and at least one representative NP diagram, or an
explicit missing reason for that process/class. If any process lacks an SM or NP
diagram, record exactly which process and which class is missing in
`manuscript_evidence.json`; do not silently substitute a diagram from another
process.

If diagrams are unavailable, document the missing reason in
`manuscript_evidence.json.figures.feynman_diagrams` and
`manuscript_validation.json`, with one record per process and per SM/NP class;
do not silently substitute a diagram from another process. Missing diagrams do
not block manuscript generation when the reason is documented.

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/manuscript.pdf`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/manuscript.pdf       # required if target or local LaTeX exists
results/manuscript.tex       # required with manuscript.pdf
results/manuscript.html      # allowed only if target and local LaTeX are both unavailable
results/data/phase10/
  manuscript_build_environment.json
  manuscript_evidence.json
  reference_paper_plan.json
  literature_plan.json
  manuscript_checklist.json
  manuscript_validation.json
  manuscript_draft_v1.*
  manuscript_draft_v2.*      # if needed
  manuscript_draft_v3.*      # if the second revision is needed
```

```python
logger.phase_complete("10")
```

## Phase Transition

Before calling `logger.phase_complete("10")`, satisfy
[`deliverables-phase10.md`](deliverables-phase10.md). Missing deliverables
require self-repair or bounded manuscript revision, not user interaction.

After the final manuscript and validation file are written:

1. Log remaining validation issues, if any.
2. Proceed immediately to cleanup and then Phase 11.
3. Do not ask for confirmation, present options, or wait for user input.

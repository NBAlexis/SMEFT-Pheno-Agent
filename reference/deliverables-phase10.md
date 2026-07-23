# Phase 10 Deliverables: Manuscript

Consumes: all Phase 1-9 deliverables plus manuscript references.

Must deliver:
- `results/data/phase10/manuscript_build_environment.json` with target and
  local LaTeX probe results, `target_latex_available`,
  `local_latex_available`, `pdf_required`, `selected_format`, and
  `build_location`.
- `results/data/phase10/collider_energy.json`.
- `results/data/phase10/manuscript_evidence.json`.
- `results/data/phase10/reference_paper_plan.json` and
  `literature_plan.json`.
- `results/data/phase10/manuscript_checklist.json` for the final draft.
- `results/data/phase10/manuscript_trace_map.json` mapping every required
  checklist ID to evidence and to a manuscript location.
- `results/data/phase10/manuscript_completeness_passes.json` with at least
  three passes listing missing required content and the repair actions taken
  before formal validation.
- `results/data/phase10/manuscript_validation.json` with `status` equal to
  `pass` or `issues_remaining`; either status requires every frozen manuscript
  item to be complete and `major_issues` to be empty. `issues_remaining` may
  contain minor writing or presentation issues only.
- `results/data/phase10/manuscript_draft_v1.*`. If revisions occur, also
  `manuscript_draft_v2.*` and `manuscript_draft_v3.*` as produced by the
  bounded revision loop. The final PDF/HTML deliverable is separate from these
  drafts.
- If `pdf_required=true`, final non-empty `results/manuscript.pdf` and
  `results/manuscript.tex`. HTML does not satisfy the deliverable in this case.
- If `pdf_required=false`, final non-empty `results/manuscript.html`; this is
  allowed only when both target and local LaTeX probes failed.
- Representative Feynman diagrams copied under `results/data/feynman_diagrams/`.
  If the retained MG5 runner manifests do not contain usable diagrams, missing
  reasons must be recorded per process and per SM/NP class in both
  `manuscript_evidence.json.figures.feynman_diagrams` and
  `manuscript_validation.json`.

Manuscript dependency: this is the manuscript phase. It must write a paper, not
a workflow summary. With `debug=true`, the paper must clearly identify itself as
a reduced-event workflow test and must not claim publication-ready numerical
results; all other Phase 10 files and sections remain required.

If missing or incomplete: rerun the LaTeX probes, choose PDF whenever target or
local LaTeX is available, rebuild evidence, create missing figures from
existing data, run the three-pass completeness loop, update the checklist and
trace map, and repair every missing frozen manuscript item. The revision limit
applies only to optional prose and presentation improvements; it never permits
Phase 10 to complete with missing required content or a major issue. Missing
upstream required artifacts must be repaired in the responsible phase. Do not
ask the user to choose missing content.

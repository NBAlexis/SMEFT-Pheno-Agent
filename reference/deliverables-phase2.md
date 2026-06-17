# Phase 2 Deliverables: Environment

Consumes: Phase 1 `run_config.json`.

Must deliver:
- Initialized `results/workflow.log` with `skill_version`, `skill_commit`, and
  detailed step records.
- Validated MG5, CutExperiment, model directories, Delphes card, target
  execution, run directories, and locked event counts.
- Created workflow venv and `results/jobs/`.
- `results/data/phase2/environment_manifest.json` with execution target,
  validated paths, tool versions/probe commands, venv Python path, selected
  Delphes card path, model locations, and locked event-count mode.
- Updated `run_config.json` if CutExperiment was cloned or a safe workdir
  correction was needed.

Manuscript dependency: toolchain provenance, execution environment, detector
card availability, and reproducibility metadata.

If missing or invalid: fix the environment, rerun the failed validation step, or
write `phase_fail` only for a concrete unrecoverable dependency/configuration
failure.

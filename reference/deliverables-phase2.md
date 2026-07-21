# Phase 2 Deliverables: Environment

Consumes: Phase 1 `run_config.json`, `research_contract.json`,
`deliverables_contract.json`, and `contract_lock.json`.

Must deliver:
- Initialized `results/workflow.log` with `skill_version`, `skill_commit`, and
  detailed step records. Every record includes the frozen `objective_sha256`.
- Consumed the Phase 1 CutExperiment result, and validated model directories,
  Delphes card, target execution, run directories, and locked event counts.
  MG5 stack validation happens in Phase 1.
- Created workflow venv and `results/jobs/`.
- `results/data/phase2/environment_manifest.json` with execution target,
  tool versions/probe commands, venv Python path, selected Delphes card path,
  model locations, locked event-count mode, research-objective hash, and
  deliverables-template hash.
- Successful `scripts/research_contract.py verify` against the current
  `run_config.json`.
- Updated `run_config.json` only for a safe workdir correction if needed.

Manuscript dependency: toolchain provenance, execution environment, detector
card availability, and reproducibility metadata.

If missing or invalid: fix or replace the technical implementation, repair the
environment, or migrate to a scientifically equivalent target and rerun the
validation. Write `phase_fail` only with evidence that the frozen contract is
impossible, never solely because a dependency install, path, card, or standard
script failed.

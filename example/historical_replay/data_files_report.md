# Replay Package User Guide

## How to run

```bash
cd results/replay
./replay.sh                     # default output: ./replayed-results
./replay.sh --output /path/dir  # custom output root
./replay.sh --resume            # resume after interruption (step checksums must match)
```

Requirements on this machine: the project virtualenv
(`/mnt/e/SMEFT-Pheno-Agent-GLM-test/venv`, override with `SMEFT_PYTHON`),
MadGraph5_aMC@NLO at the `madgraph_path` recorded in `run_config.json`,
the CutExperiment repository at `cutexperiment_path`, `sha256sum`, and
bash. A full replay regenerates all phase 2-9 numerical deliverables and
can take days of computation.

## What is stored where

- `replay.sh` - entry point described above; verifies package checksums,
  prepares the output working tree (contracts, bundled scripts, reference
  data), exports `SMEFT_WORKDIR`, and runs phases 2-9 in order with
  per-step stdout/stderr logs under `<output>/replay_logs/`.
- `replay_manifest.json` - machine-readable manifest: packaged-file
  checksums, frozen algorithm/seed lock, external dependencies, and the
  phase 2-9 step list with every numerical output path.
- `steps/` - the eight phase drivers. Each is the study driver with a
  single change: the working directory is read from `SMEFT_WORKDIR`
  instead of the original hardcoded path.
- `support/` - bundled scripts (`*.py`), skill `reference/` files, and
  auxiliary project modules copied into the replay working tree.
- `inputs/` - JSON-identical copies of the frozen `run_config.json` and
  the three contract files.
- After a successful run, the regenerated deliverables appear under
  `<output>/results/...` at exactly the relative paths listed in the
  manifest steps (e.g. `results/data/phase8/threshold_optimization.json`).

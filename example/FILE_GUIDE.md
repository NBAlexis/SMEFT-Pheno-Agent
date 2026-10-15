# Reference Artifact File Guide

This directory contains the lightweight reference artifacts accompanying the
SMEFT-Pheno-Agent article. Original scripts and JSON records retain their
directory structure. Large event-level datasets are not included.

## File Locations

- `results/run_config.json`: reference-run configuration.
- `results/research_contract.json`, `results/deliverables_contract.json`, and
  `results/contract_lock.json`: original frozen contracts.
- `results/data/phase2/` through `results/data/phase10/`: recorded phase JSON,
  including environment and operator records, scans, feature schemas, algorithm
  choices and seeds, thresholds, fits, and final intervals.
- `results/workflow.log`, `results/audit_report.json`, and
  `results/audit_expected_outputs.json`: complete original execution log and
  audit records.
- `session_scripts/`: phase analysis programs and repair scripts actually used
  in the reference execution.
- `runtime_support/` and `results/algorithms/`: runtime utilities and
  algorithm-related code.
- `historical_replay/` and `historical_validation/`: historical replay package
  and comparison records.
- `frozen_replay/`: revised frozen-check package, kept separate from the
  historical version.
- `analysis_lock.json` and `toolchain_lock.json`: recorded algorithms, seeds,
  threshold, and toolchain identities.
- `tables/` and `plots/`: compact numerical tables and publication figures.
- `validation/`: results of executed numerical replays and toolchain identity
  checks.
- `source_manifest.json`: original file provenance and SHA-256 hashes.
- `checksums.sha256`: integrity checksums for the files in this directory.
- `scripts/`: three additional utilities allowing this directory to be used
  independently for compact numerical replay.

LHE, ROOT, LHCO, HEPMC, large per-event feature/score CSV files, and large model
artifacts are excluded. Absolute paths retained in historical JSON identify
the original execution environment; they do not imply that the referenced
large files are included in this archive.

## Reconstruct Tables Without Event Data

With Python 3.10 or newer, run the following command from this directory:

```text
python scripts/replay_reference_numerics.py . --output numerical-replay-output
```

The output directory must be new or empty. The command refits the eight
operator scans using compact recorded inputs and computes 24 intervals. It
does not generate events, retrain classifiers, or rescore individual events.

Full Monte Carlo regeneration requires the recorded external tools and newly
generated samples that are not included here. See `README.md` and
`frozen_replay/README_REVISION.md` for the validation scope of the historical
and revised packages. A static check is not a full numerical reproduction.

## Repository Placement

Place the contents of this directory under `examples/reference_run/` in the
skill repository. The included `scripts/` supports the command above directly
from that directory. Large raw datasets do not need to be uploaded with these
software artifacts.

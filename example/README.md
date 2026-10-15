# September 2026 reference run

This directory contains the lightweight reference artifacts supplied for
review and public use. See [`FILE_GUIDE.md`](FILE_GUIDE.md) for a file guide.
Scripts and original JSON retain their directory structure; large event
samples and per-event feature/score datasets are excluded.

This example accompanies the revised SMEFT-Pheno-Agent article. It contains
session programs, the actual JSON configuration/manifests and compact numeric
inputs. Large event samples and per-event feature/score files are omitted.

The reference uses `mu+ mu- > vl vl~ j j`, gQGC_UFO, 10 TeV, 10 ab^-1 and
unpolarised beams. The ten-member algorithm pool has three recorded eligibility
exclusions; gradient boosting, isolation forest and MLP were trained. The
production selector is MLP at 0.98. Tables and plots here use that study.

## Contents

- `results/`: byte-preserved original configuration, contracts, phase JSON,
  full audit reports and workflow log.
- `session_scripts/`: actual study-specific programs and relevant repairs.
- `runtime_support/`: the Python utilities copied into that execution.
- `historical_replay/`, `historical_validation/`: the original package and
  comparison evidence, preserved as recorded.
- `frozen_replay/`: a separately named correction that loads the original
  algorithm list/seeds and preserves the feature-header convention.
  Its `--check-only` entry point validates package/toolchain identity without
  starting Monte Carlo generation.
- `analysis_lock.json`, `toolchain_lock.json`: consolidated revision locks.
- `fit_quality.json`: unweighted diagnostics derived from the selected counts.
- `regeneration_comparison.json`: actual Phase-9 comparison, correcting the
  empty/null-field limitations of the original comparison report.
- `tables/`, `plots/`, `score_histograms.json`: compact publication inputs.
- `validation/`: numerical replay and toolchain identity/mismatch checks.
- `source_manifest.json`, `checksums.sha256`: origin and integrity records.

Historical JSON retains its original absolute paths, so that it does not
silently change the evidence. Those paths identify the generating environment;
they are not files shipped inside this example. Do not treat the historical
environment probe's unsupported MG5 `--version` as a version observation.
The supplemental capture reads the installation's `VERSION` file instead.

## Reconstruct the numerical tables without event data

From this example directory, using Python 3.10 or newer:

```text
python scripts/replay_reference_numerics.py . --output numerical-replay-output
```

The output directory must be new or empty. This calculation refits the selected
eight cross-section scans from recorded per-point selected counts/cross sections,
reconstructs the recorded candidate widths, and solves S=2,3,5 for 24 intervals.
It checks the frozen feature-schema checksum and algorithm/threshold identity.
It does not regenerate events, extract features, retrain classifiers or rescore
individual events. The output `numerical_replay_validation.json` states that
scope and the tolerance. Six tests on Windows and WSL/Linux are supplied.

## Full Monte Carlo regeneration

Install the model, MG5/Pythia/Delphes and CutExperiment using the recorded
environment; supply the paths recorded in `toolchain_lock.json` and the run
configuration. The actual session and replay programs show all generation
settings. Users must generate the omitted event samples themselves. Full
generation can require weeks and hundreds of GB; it introduces new generator
and shower fluctuations. Exact event-level analysis requires the same samples
and preprocessing, in addition to frozen algorithms and seeds.

The historical replay completed but redrew the candidates, selected extra trees
at 1.00, and produced interval widths 0.685-0.731 times the original. It is a
regeneration with changed methodology, not exact reproduction. Null Phase-5
comparison fields are not evidence that event samples are byte-identical.
The amended full package has a corrected frozen seed path and static/unit
checks, but has not been run through another full generation during revision.

## Publication and interpretation

The outputs are central, expected, single-coefficient Asimov sensitivities.
Finite-MC errors and experiment/theory/detector systematics are not propagated.
No partial-wave unitarity bound or EFT-validity cut is applied. Phase-4 range
setting and Phase-7 classifier training are separately documented provenance.

This archive is locally prepared for upload. No release tag or Zenodo DOI has
yet been minted. See `RELEASE_REVIEW.md` for the full skill repository's release checklist.

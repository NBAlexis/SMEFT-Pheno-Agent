# Phase 11 Deliverables: Numerical Replay Package

Consumes: the frozen run configuration, Phase 2-9 provenance and numerical
artifacts, Phase 10 manuscript evidence, workflow log, and cleanup archive.

Must deliver under each run root:

- `results/replay/replay.sh`, executable and usable with `./replay.sh` without
  prompts or edits.
- `results/replay/replay_manifest.json` with ordered Phase 2-9 commands, inputs,
  outputs, seeds, parameters, and SHA-256 checksums.
- All phase drivers and helpers referenced by the manifest under
  `results/replay/steps/` or `results/replay/support/`.
- `results/replay/data_files_report.md`, describing every declared numerical
  output with its producer, format/schema, scientific meaning, units,
  dimensions, provenance, and integrity metadata.
- `results/replay/replay_validation.json` proving Bash syntax validation,
  clean-directory dry-run order, referenced-file checksum validation, output
  coverage, report coverage, and absence of original-result production inputs.

The default replay must start in a new output directory and regenerate all
Phase 3-9 numerical results in order, plus Phase 2 environment provenance. It
must not reuse original numerical outputs as production inputs. A full replay is
not required to complete Phase 11.

Manuscript dependency: the manuscript can cite the replay package and data-file
report as reproducibility material; replay does not regenerate Phase 10.

If missing or incomplete: recover commands and parameters from the frozen
configuration, manifests, logs, and actual phase drivers; regenerate the package
and repeat validation. Do not substitute a prose recipe for the executable
entry point.

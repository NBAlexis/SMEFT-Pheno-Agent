# Phase 11 Deliverables: Numerical Replay Package

Consumes: the frozen research objective and deliverables contract, run
configuration, Phase 2-9 provenance and numerical artifacts, Phase 10 manuscript
evidence, workflow log, and cleanup archive.

Must deliver under each run root:

- `results/replay/replay.sh`, executable and usable with `./replay.sh` without
  prompts or edits.
- `results/replay/replay_manifest.json` with ordered Phase 2-9 commands, inputs,
  outputs, parameters, external dependency identities, and SHA-256 checksums.
  Its `algorithm_lock` must
  freeze every actually trained algorithm and the Phase 9 production algorithm,
  including implementation identity, hyperparameters, score
  definition, the Phase 7 algorithm-selection seed, each algorithm's training
  seed, model-output path, explicit selection scope, exact Phase 9
  rationale/evidence provenance, packaged implementation checksums, and a valid
  canonical lock hash.
- Frozen copies of `research_contract.json`, `deliverables_contract.json`, and
  `contract_lock.json` referenced by the replay manifest.
- All phase drivers and helpers referenced by the manifest under
  `results/replay/steps/` or `results/replay/support/`.
- `results/replay/data_files_report.md`, telling the user the exact replay
  command and where each produced result file or file group will be stored
  after a successful run. Its content is not a numerical validation artifact.
The package must provide a one-command entry point that can start a new output
directory and run the Phase 2-9 numerical workflow in order later. It must not
reuse original numerical outputs as production inputs. Phase 11 only writes the
replay materials; it does not execute or dry-run them and does not compare
numerical results.

Manuscript dependency: the manuscript can cite the replay package and data-file
report as reproducibility material; replay does not regenerate Phase 10.

If missing or incomplete: recover commands and parameters from the frozen
configuration, manifests, logs, and actual phase drivers; regenerate the
missing package files. Do not substitute a prose recipe for the executable
entry point and do not run the replay as a completion test.

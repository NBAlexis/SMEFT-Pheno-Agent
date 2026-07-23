# Phase 11: Package the Numerical Replay Script

> **Contract priority**: Preserve the research objective and deliverables. Apply
> the technical-failure and `phase_fail` definitions in `SKILL.md`.

## Purpose

Create a one-command script that can rerun the Phase 2-9 numerical workflow in
order when a user later needs to investigate a result. Also write a concise
Markdown user guide that explains how to run it and where its outputs will be
stored.

Phase 11 only builds the package. Do not execute `replay.sh`, run a dry-run,
repeat any numerical phase, compare new and original results, or claim that the
package has reproduced the study. A replay can take weeks.

Phase 10, cleanup, and Phase 12 are outside the replayed numerical scope.

## Package Layout

Create one package under each run root:

```text
replay/
  replay.sh
  replay_manifest.json
  data_files_report.md
  run_config.json
  research_contract.json
  deliverables_contract.json
  contract_lock.json
  inputs/
  steps/
  support/
```

`./replay.sh` must start at Phase 2, run through Phase 9 in order, require no
prompts or manual edits, and write to a new package-relative output directory.
It may support `--output` and `--resume`. Do not add a Phase 11 execution or
validation mode.

## Package Inputs

Use the actual run configuration, runner results, workflow log, and phase code
to package:

- JSON-content-identical copies of `run_config.json`,
  `research_contract.json`, `deliverables_contract.json`, and
  `contract_lock.json`;
- every project-specific Phase 2-9 driver and helper used by the replay;
- every user-supplied input file needed before Phase 2 under `inputs/`;
- the final algorithms, implementations, hyperparameters, score definitions,
  model-output paths, and production-algorithm selection used by the study;
- the selected UFO model and detector-card identities;
- external MG5, Pythia, Delphes, root2lhco, CutExperiment, Python, and package
  paths/versions plus available file or directory checksums.

Do not package credentials or tokens. Document required secret environment
variable names without recording their values.

## Replay Manifest

Write `replay_manifest.json` with this minimum structure:

```json
{
  "schema_version": "1.0",
  "entrypoint": "replay.sh",
  "phase_order": ["2", "3", "4", "5", "6", "7", "8", "9"],
  "default_output": "replayed-results",
  "source_inputs": [
    {
      "path": "inputs/user_input.dat",
      "sha256": "64 hexadecimal characters",
      "provided_before_phase2": true
    }
  ],
  "external_dependencies": [
    {
      "name": "MadGraph5_aMC@NLO",
      "path": "/opt/MG5_aMC",
      "version": "recorded version",
      "sha256": "recorded checksum or null with checksum_unavailable_reason"
    }
  ],
  "package_sha256": {
    "replay.sh": "sha256",
    "run_config.json": "sha256",
    "research_contract.json": "sha256",
    "deliverables_contract.json": "sha256",
    "contract_lock.json": "sha256",
    "data_files_report.md": "sha256"
  },
  "algorithm_lock": {
    "algorithm_selection_seed": 12345,
    "trained_algorithms": [],
    "production_algorithm": "stable algorithm key",
    "selection_scope": "anchor_operator_only | per_operator_best",
    "operator_selections": {},
    "selection_provenance": {
      "selection_method": "exact Phase 9 selection_criterion",
      "selection_rationale": "exact Phase 9 selection_rationale",
      "selection_evidence": ["exact", "Phase 9", "evidence paths"],
      "source": "data/phase9/algorithm_selection.json"
    },
    "packaged_files": {"steps/phase7.py": "sha256"},
    "lock_sha256": "canonical SHA-256 without lock_sha256"
  },
  "steps": [
    {
      "phase": "2",
      "name": "environment_validation",
      "command": ["python", "steps/phase2.py"],
      "inputs": ["run_config.json"],
      "outputs": ["data/phase2/environment_manifest.json"],
      "sha256": {"steps/phase2.py": "sha256"}
    }
  ],
  "report": "data_files_report.md"
}
```

`package_sha256` covers `replay.sh`, the report, frozen JSON copies, and every
packaged file that exists before replay starts, except `replay_manifest.json`
itself because a file cannot contain its own final checksum. Step `sha256` maps
repeat the checksums needed by that step. Every source input must exist inside
the package and match its recorded SHA-256. External installations may remain
outside the package, but their identity must be sufficient for later diagnosis.

List every Phase 2-9 numerical deliverable in exactly one step's `outputs`.
Output globs are allowed only when their operator, scan-point, or algorithm
expansion is recorded. Production steps must not read original Phase 3-9
results. Original results are evidence used to construct this package, not
inputs used by `replay.sh`.

For `anchor_operator_only`, `production_algorithm` is the single final
algorithm and `operator_selections` is an empty object. For `per_operator_best`, keep
`production_algorithm` as the anchor-comparison result for backward-compatible
provenance and copy the complete Phase 9 `operator_selections` map into the
lock. Copy Phase 9 `selection_criterion`, `selection_rationale`, and
`selection_evidence` exactly into `selection_provenance`. Replay steps must apply
the recorded scope and map exactly.

Copy `algorithm_selection_seed` from Phase 7. Each `trained_algorithms` entry
must also copy the random seed used for that algorithm's data split and
training. The packaged Phase 7 step must use the frozen algorithm list and
these frozen seeds; it must not generate new randomness during replay.

## Replay Script

Generate a POSIX Bash entry point that:

1. uses `set -euo pipefail` and resolves package paths relative to itself;
2. checks required executables, packaged files, inputs, and checksums before a
   numerical command starts;
3. refuses to overwrite a non-empty output directory;
4. runs manifest steps in Phase 2-9 order with locked event counts and physics
   settings;
5. records each command, working directory, timestamps, return code,
   stdout/stderr paths, and completed-step checksums for later diagnosis;
6. permits resume only when the recorded completed-step checksums still match;
7. writes outputs below the output root documented in `data_files_report.md`.

After packaging, read the finished replay package and record your judgment on
whether one command can produce the expected Phase 2-9 numerical results.
Trust that judgment; do not execute the replay or use a prescribed checklist.

## Replay User Guide

Write `data_files_report.md` with only the information the user needs later:

1. the exact command for starting the replay, including supported output and
   resume options and required environment preparation;
2. the default output root and, after a successful run, which result files or
   file groups are stored at which relative paths.

Describe the actual generated script and manifest. The workflow may use
project-specific drivers or change its technical implementation while
preserving the research objective, so do not impose a universal report schema,
fixed scientific-description fields, or a numerical-validation section.

## Completion

After writing the package and report, record the completed generation step and
call `logger.phase_complete("11")`. Do not run a Phase 11 audit or any replay
command. Proceed to Phase 12, which performs static file inspection without
executing the replay. Do not ask the user to run it.

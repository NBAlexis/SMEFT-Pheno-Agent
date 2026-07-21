# Phase 11: Build the Numerical Replay Package

> **Contract priority**: Preserve the research objective and deliverables. Apply
> the technical-failure and `phase_fail` definitions in `SKILL.md`.

## Purpose

Produce a one-command replay package that includes every project-specific
driver, helper, configuration file, and card needed by the study. MG5, UFO,
Pythia, Delphes, and CutExperiment installations may remain external and their
required versions and content checksums must be recorded. It defines the
ordered numerical workflow and the file/report contract needed to rerun the
Phase 2-9 numerical subset of the frozen deliverables contract later. Also
produce a Markdown report that describes the data files made by the replay.

Phase 11 packages and validates the replay package; it does not rerun the full
study.
Phase 10 manuscript generation, cleanup, and Phase 12 audit are outside the
numerical replay scope.

## Prerequisite

Phase 10 and cleanup must be complete. Load the configuration and start logging:

```python
from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, workflow_step

config = load_run_config("{workdir}/results/run_config.json")
logger = WorkflowLogger(config.workdir, run_dir)
logger.phase_start("11")
```

Before packaging, run `scripts/research_contract.py verify`. Contract drift must
be corrected before replay generation. The replay may use different technical
orchestration from the original run, but it must preserve the same frozen
scientific objective and produce the same numerical deliverable paths, file
types, required JSON keys, and required CSV columns declared by
`deliverables_contract.json`.

In multi-run mode, create one replay package in each `results/{run_dir}/` root.
Create and validate the package on the selected Linux execution target. Native
Windows is not a replay execution target.

## Required Package

Write this layout under the current run root:

```text
results/replay/
  replay.sh
  replay_manifest.json
  replay_validation.json
  data_files_report.md
  run_config.json
  research_contract.json
  deliverables_contract.json
  contract_lock.json
  steps/
  support/
```

`steps/` contains the project-specific phase drivers needed by `replay.sh`.
`support/` contains only required helpers, including the report generator. Copy
or generate every non-bundled driver used in the original run; do not leave
essential computation only in conversation text, shell history, or
`workflow.log`.

The one-command entry point is:

```bash
./replay.sh
```

It must require no prompts or manual edits. It may accept optional `--output`,
`--resume`, and `--dry-run` flags, but a first invocation with no arguments must
run from the beginning into a new, package-relative output directory.

## Step 11.1: Freeze Inputs and Commands

With `workflow_step(logger, "11", "freeze_replay_inputs")`, derive replay
inputs from the actual run configuration, runner manifests, workflow log, and
phase artifacts. Package:

- a JSON-content-identical copy of `run_config.json`; credentials and tokens are
  forbidden in `run_config.json`, and replay-time secrets are supplied only by
  documented environment variables;
- JSON-content-identical copies of `research_contract.json`,
  `deliverables_contract.json`, and `contract_lock.json`;
- the exact Phase 2-9 drivers and helper versions needed to repeat the run;
- ordered commands, working directories, event counts, model and
  detector-card identities, algorithm parameters, and dependency versions;
- SHA-256 checksums for packaged scripts and configuration files.

"JSON-content-identical" means the parsed JSON values are equal; whitespace and
object-key order may differ. The replay does not require or invent MG5, Pythia,
or Delphes random seeds. Monte Carlo reproduction is evaluated by the numerical
comparison policy below, not by event-by-event identity.

Do not package credentials, private keys, access tokens, or host-specific secret
material. Fail with a concrete error if a required secret cannot be supplied by
an environment variable at replay time.

## Step 11.2: Generate the Ordered Manifest

Write `replay_manifest.json` with this minimum structure:

```json
{
  "schema_version": "1.0",
  "entrypoint": "replay.sh",
  "phase_order": ["2", "3", "4", "5", "6", "7", "8", "9"],
  "default_output": "replayed-results",
  "source_inputs": [],
  "algorithm_lock": {
    "trained_algorithms": [
      {
        "key": "gradient_boosting",
        "implementation": "sklearn.ensemble.GradientBoostingClassifier",
        "hyperparameters": {"n_estimators": 200},
        "score_definition": "predict_proba[:, 1]",
        "model_output": "algorithms/anchor_gradient_boosting.pkl"
      }
    ],
    "production_algorithm": "gradient_boosting",
    "selection_provenance": {
      "selection_method": "narrowest_anchor_S2_interval",
      "source": "data/phase9/algorithm_selection.json"
    },
    "packaged_files": {"steps/phase7.py": "...sha256..."},
    "lock_sha256": "...canonical SHA-256 without lock_sha256..."
  },
  "steps": [
    {
      "phase": "2",
      "name": "environment_validation",
      "command": ["python", "steps/phase2.py"],
      "inputs": ["run_config.json"],
      "outputs": ["data/phase2/environment_manifest.json"],
      "sha256": {"steps/phase2.py": "..."}
    }
  ],
  "monte_carlo_comparison": {
    "production_inputs_exclude_reference_results": true,
    "combined_standard_error_multiplier": 3.0,
    "fallback_limits": {
      "cross_sections": {"difference": "relative", "maximum": 0.10},
      "auc_and_thresholds": {"difference": "absolute", "maximum": 0.05},
      "fit_coefficients_and_constraint_endpoints": {"difference": "relative", "maximum": 0.20}
    },
    "comparison_output": "numerical_comparison.json"
  },
  "report": "data_files_report.md"
}
```

Use one or more steps per phase as needed. Preserve their executed order. Every
required numerical JSON, CSV, LHCO, trained-model, and plot family from Phases
3-9 must appear in exactly one step's `outputs`; Phase 2 environment provenance
must also be declared. Output globs are allowed only when the operator,
algorithm, or scan-point matrix that expands them is recorded in the manifest.

`algorithm_lock` freezes execution state at Phase 11, not the Phase 1 research
objective. Its trained keys must exactly match
`algorithm_comparison.json["anchor"]`; parameters and score definitions
must match `algorithm_descriptions.json`; `production_algorithm` must match
Phase 9 `algorithm_selection.json`; and every algorithm driver/helper required
for reproduction must appear in `packaged_files` with its actual SHA-256.

## Step 11.3: Generate `replay.sh`

With `workflow_step(logger, "11", "generate_replay_entrypoint")`, generate a
POSIX Bash entry point that:

1. Enables `set -euo pipefail`, resolves paths relative to its own location,
   validates the frozen config and required executables, and creates the output
   directory.
2. Refuses to overwrite a non-empty output directory unless explicit `--resume`
   semantics prove that completed steps match their recorded checksums.
3. Runs manifest steps in exact Phase 2, 3, 4, 5, 6, 7, 8, 9 order. A nonzero
   command stops that replay attempt with diagnostic state; it does not redefine
   the frozen replay objective or authorize dropping outputs.
4. Writes stdout/stderr, command, return code, timestamps, checksums, and step
   state under the replay output so a long run can resume safely.
5. Uses the locked event counts. It must not reduce
   statistics or silently substitute algorithms, models, cards, or scan points.
6. Generates `data_files_report.md` only after all numerical steps complete,
   then verifies that every manifest output exists and is non-empty.

Production steps may read only the packaged configuration and code, the
external installations named above, the selected UFO directories, detector
cards, and user-supplied source files explicitly listed in
`replay_manifest.json["source_inputs"]` with SHA-256 checksums. A source input is
a file supplied before Phase 2 that was not produced by any Phase 2-9 command.
Each list entry is
`{"path": "...", "sha256": "64 hexadecimal characters", "provided_before_phase2": true}`.
It must not copy, parse, fit, or otherwise consume original Phase 3-9 numerical
outputs to produce replay results. Original results may be used only by an
optional post-run comparison step that is clearly separated from production.

If a replay is actually executed later, the manifest may include an optional
comparison policy for comparing replay results with the original results. A
quantity passes when its absolute difference is no more than
`combined_standard_error_multiplier` times the combined standard error. If
either result lacks a standard error, use the corresponding fallback limit from
the manifest: relative difference for cross-sections and fit/constraint values,
and absolute difference for AUC/threshold values. The limits may be stricter,
but may not exceed 0.10, 0.05, and 0.20 respectively. Write every comparison,
uncertainty or fallback used, and pass/fail result to
`numerical_comparison.json`.

Phase 11 package construction itself is complete after the static and dry-run
checks below; it does not claim that replay outputs have already been
generated.

## Step 11.4: Write the Data-File Report

Write `data_files_report.md` in the package now as the documented output
contract, and make the replay's final report generator refresh it in the replay
output using actual metadata. Cover every output declared in the manifest.

For each file or well-defined file family, record:

- relative path or expansion rule;
- producing phase and step;
- file format and JSON keys, CSV columns, array shape, or model serialization;
- scientific meaning and units, explicitly stating `dimensionless` or `N/A`
  when appropriate;
- operator, scan point, algorithm, and run configuration dimensions;
- row/event count or shape when the replay has completed;
- SHA-256 checksum when the replay has completed;
- upstream inputs and downstream consumers.

Include short sections for replay scope, directory layout, provenance, naming
conventions, and known warnings. Do not replace the report with a bare file
listing or a dump of JSON keys.

## Step 11.5: Validate Without Recomputing the Study

With `workflow_step(logger, "11", "validate_replay_package")`, run all
applicable checks:

1. `bash -n replay.sh` succeeds; run `shellcheck` too when available.
2. `./replay.sh --dry-run --output <new-empty-temp-dir>` succeeds without
   launching MG5 or training and prints each declared command exactly once in
   manifest order.
3. The observed dry-run phase sequence is exactly 2 through 9.
4. Every referenced driver/helper exists, is non-empty, and matches its manifest
   checksum.
5. Every Phase 2-9 numerical item obtained by resolving the frozen deliverables
   contract has a manifest producer and a corresponding entry in
   `data_files_report.md`.
6. Static inspection confirms no production step reads original Phase 3-9
   result paths.
7. The algorithm lock canonical hash is valid, its Phase 7/9 values match the
   actual run, and every packaged algorithm implementation checksum matches.
8. `audit_expected_outputs.py --phase 11` confirms that every resolved Phase
   2-9 deliverable appears in exactly one manifest step, no production input is
   an original Phase 3-9 result, every output is named in
   `data_files_report.md`, and the Monte Carlo comparison limits do not exceed
   the maxima above.

Write results to `replay_validation.json`, including commands, return codes,
observed phase order, coverage counts, failures, warnings, and whether
`shellcheck` was available. Phase 11 does not require executing the full
replay.

## Phase Transition

Before calling `logger.phase_complete("11")`, satisfy
[`deliverables-phase11.md`](deliverables-phase11.md). Repair missing or invalid
package artifacts without user interaction.

```python
logger.phase_complete("11")
```

Proceed immediately to Phase 12 without stopping.

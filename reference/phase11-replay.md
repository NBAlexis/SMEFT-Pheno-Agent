# Phase 11: Build the Numerical Replay Package

> **Contract priority**: Preserve the frozen research objective and deliverables.
> Technical failure triggers diagnosis and recovery; stop only on explicit user
> instruction or documented proof that a frozen item is impossible.

## Purpose

Produce a self-contained, one-command replay package that starts from the frozen
research objective, deliverables contract, run configuration, and raw/external
physics inputs. It executes the numerical workflow in order and regenerates the
Phase 2-9 numerical subset of the frozen deliverables contract. Also produce a
Markdown report that describes the data files made by the replay.

Phase 11 packages and validates the replay; it does not rerun the full study.
Phase 10 manuscript generation, cleanup, and Phase 12 audit are outside the
numerical replay scope.

## Prerequisite

Phase 10 and cleanup must be complete. Load the configuration and start logging:

```python
from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, workflow_step

config = load_run_config("{workdir}/results/run_config.json")
logger = WorkflowLogger(config.workdir)
logger.phase_start("11")
```

Before packaging, run `scripts/research_contract.py verify`. Contract drift must
be corrected before replay generation. The replay may use different technical
orchestration from the original run, but it must preserve the same frozen
scientific objective and produce the same numerical deliverable schemas.

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

- an immutable copy of `run_config.json`, with secrets replaced by documented
  environment-variable references;
- immutable copies of `research_contract.json` and `deliverables_contract.json`;
- the exact Phase 2-9 drivers and helper versions needed to repeat the run;
- ordered commands, working directories, random seeds, event counts, model and
  detector-card identities, algorithm parameters, and dependency versions;
- SHA-256 checksums for packaged scripts/configuration and immutable raw inputs.

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
  "steps": [
    {
      "phase": "2",
      "name": "environment_validation",
      "command": ["python", "steps/phase2.py"],
      "inputs": ["run_config.json"],
      "outputs": ["data/phase2/environment_manifest.json"],
      "random_seeds": {},
      "sha256": {"steps/phase2.py": "..."}
    }
  ],
  "report": "data_files_report.md"
}
```

Use one or more steps per phase as needed. Preserve their executed order. Every
required numerical JSON, CSV, LHCO, trained-model, and plot family from Phases
3-9 must appear in exactly one step's `outputs`; Phase 2 environment provenance
must also be declared. Output globs are allowed only when the operator,
algorithm, or scan-point matrix that expands them is recorded in the manifest.

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
5. Uses the locked event counts and recorded random seeds. It must not reduce
   statistics or silently substitute algorithms, models, cards, or scan points.
6. Generates `data_files_report.md` only after all numerical steps complete,
   then verifies that every manifest output exists and is non-empty.

The replay may read the frozen configuration, packaged code, external MG5/UFO/
Delphes/CutExperiment installations, detector cards, and genuinely raw inputs.
It must not copy, parse, fit, or otherwise consume original Phase 3-9 numerical
outputs to produce replay results. Original results may be used only by an
optional post-run comparison step that is clearly separated from production.

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

Write results to `replay_validation.json`, including commands, return codes,
observed phase order, coverage counts, failures, warnings, and whether
`shellcheck` was available. A full replay is not required during Phase 11.

## Phase Transition

Before calling `logger.phase_complete("11")`, satisfy
[`deliverables-phase11.md`](deliverables-phase11.md). Repair missing or invalid
package artifacts without user interaction.

```python
logger.phase_complete("11")
```

Proceed immediately to Phase 12 without stopping.

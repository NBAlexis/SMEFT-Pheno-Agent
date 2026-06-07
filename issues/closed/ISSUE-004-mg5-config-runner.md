# ISSUE-004: Add config-driven MG5 launch runner with survey enum

- Priority: high
- Type: script candidate
- Status: closed

## Problem

Current `scripts/run_mg5.py` only executes an existing order file. It does not
read a run spec, write the MG5 order file, set run-card fields, select a
recovery survey profile, run MG5, convert ROOT to LHCO, or write workflow
metadata end to end.

## Risk

Agents still have to hand-write order files and recovery settings, which is
exactly where fragile mistakes occur.

## Candidate Script

`scripts/run_mg5_config.py`, or a replacement `scripts/run_mg5.py` mode.

## Execution Model

For SSH/WSL2 runs, upload the tool scripts and all required inputs to the remote
working/tool directory and execute there. MG5, Delphes/root2lhco conversion,
banner collection, LHCO counting, cleanup-candidate discovery, and result JSON
creation should all happen inside the same execution environment that runs
MadGraph. Avoid split local/remote execution rules for data-generation phases.

The only intentional exception is manuscript production: if the remote
environment has no LaTeX installation but the local environment does, Phase 10
may transfer the required figures/data/manuscript sources back to the local
working folder and compile the manuscript locally.

## Required Input JSON Capabilities

- process folder
- model
- process
- coefficient block settings
- beam energies
- polarization
- `nevents`
- Delphes card
- model name already synced/installed under `{mg5path}/models/`
- output labels
- survey profile enum

## Process Modes

- `pure_sm`: `generate {process} NP=0`
- `pure_np`: `generate {process} NP>0`
- `sm_np`: `generate {process}` with no NP suffix
- `scan`: coefficient scan for one operator using MG5 `scan:[...]`

The runner must validate that the UFO model already exists under
`{mg5path}/models/{model_name}`. UFO/model sync belongs to Phase 1/2 target
setup, not the MG5 runner. The runner must copy the required Delphes card and
Delphes card dependencies into the process directory after process creation and
before launch.

## Coefficient Modes

Pure-sample runs must support:

- `default`: target operator uses the parsed UFO/default coefficient
- `c_scan`: target operator uses the Phase 4 `c_scan`
- all non-target coefficients are set to `0.0`

## Survey Enum

The runner should hide raw `sde_strategy` and `hard_survey` settings behind an
enum:

- `default`
- `sde0_hs0`
- `sde0_hs1`
- `sde0_hs2`

Do not expose raw `sde_strategy` / `hard_survey` choice to the agent except as
the enum value.

## Result JSON

The runner should write a result JSON containing:

- process mode, model, process, operator, coefficient block/index/value
- scan expression and scan point labels when applicable
- survey enum used
- order file path and process directory
- run folders
- LHCO output paths
- banner paths
- parsed cross-sections from `scripts/extract_cross_section.py`
- exact loaded LHCO event counts from `scripts/count_lhco_events.py`
- copied Delphes card/dependency paths
- cleanup candidates: ROOT, LHE, HEPMC, and other large intermediate files
- stdout/stderr/log paths and return codes
- manifest fields needed by workflow logging and recovery metadata

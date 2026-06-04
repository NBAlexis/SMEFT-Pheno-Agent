---
name: automated-smeft-ml-pheno
description: Use when the user wants an automated SMEFT phenomenology study with MadGraph5, Delphes/root2lhco processing, CutExperiment feature extraction, machine-learning event selection, coefficient scans, expected Wilson-coefficient constraints, or a publication-style report. Trigger even when required inputs are missing: Phase 1 must collect them interactively before execution. Supports single or multiple UFO models and single or multiple (energy, luminosity) run pairs.
---

# Automated SMEFT Phenomenology with Machine Learning

Run an end-to-end SMEFT collider phenomenology workflow: collect study inputs, validate the environment, generate SM/NP samples with MadGraph5, convert event outputs, train ML selectors, optimize event selection, compute expected Wilson-coefficient constraints, generate a report, clean up MG5 process folders, and audit consistency.

## Operating Modes

This skill has exactly two modes.

### Phase 1 Intake Mode

Phase 1 is the only interactive stage. Use [`reference/phase1-input-collection.md`](reference/phase1-input-collection.md) as the controlling document.

Rules:
- Ask exactly the next intake question and then stop for the user reply.
- Every intake question must be bilingual: English first, Chinese on the next line.
- Do not proceed to Phase 2 until all intake fields are collected, validated, and written to `{workdir}/results/run_config.json`.
- If the latest user message requests restart/start over/retest, discard all prior physics/run fields and begin again at `[1/9]`.
- On restart, `madgraph_path` and `cutexperiment_path` may use remembered paths only as suggested defaults. They must still be asked; the user must type `yes` or provide a replacement.

### Execution Mode

Execution Mode begins only after Phase 1 writes a valid `run_config.json`. From Phase 2 onward, user interaction is disabled.

#### Stop / Pause Gate

In Execution Mode, before stopping, pausing, or asking the user any question, classify the reason.

Allowed reasons only: explicit user stop; proven unrecoverable error; red flag after a phase completion unit; durable handoff with no user decision required.

Forbidden reasons: runtime estimate; repeated work; capability already validated; asking whether to continue.

If the reason is forbidden, continue automatically. Do not ask the user.

#### Serial Phase Artifact Rule

During Phase N, do not create, modify, or execute artifacts for Phase N+1 or later.

Allowed waiting work: monitor current phase jobs, update current phase progress manifests, inspect current phase logs, retry current phase failures, and clean current phase intermediates after required outputs are secured.

Future-phase code, result files, plots, models, reports, or audit artifacts may be created only after the current phase completes.

## SUPREME RULE: Execution Continuity

Once Execution Mode starts, keep running until Phase 11 is complete, an unrecoverable error is proven, a documented red flag is evaluated after its phase completion unit, or an explicit user stop command is received.

Rules:
- Do not ask whether to continue.
- Do not ask whether to reduce event counts.
- Do not ask what to do with zero cross-sections.
- Do not stop because a command is slow.
- Do not stop because the estimated runtime is hours, days, weeks, or months.
- Do not declare a phase "impractical for an interactive session".
- Do not alter physical parameters for speed or convenience.
- Recover from MG5, Delphes, ROOT, root2lhco, filesystem, and parsing issues when a conservative recovery is possible; otherwise stop only with concrete evidence of an unrecoverable error.

## Long-Run Execution Contract

MadGraph/Delphes scans are allowed to run for 4-8 hours, several days, several weeks, or more than two months. Runtime length is normal physics-workflow behavior, not a red flag.

Hard rules:
- Time estimates may be written to logs, but they must never change the physics plan, event counts, operator list, scan grid, algorithms, or phase transitions.
- "Interactive session impracticality" is not a stop condition. If the foreground session is unsuitable for the expected duration, switch to durable execution instead of halting.
- Do not ask the user whether to continue, split the scan, reduce `nev_scan`, enable debug mode, drop operators, or run fewer scan points because of runtime.
- If a command may outlive the current agent session, start it with a durable mechanism on the selected execution target: `scripts/durable_exec.py`, `tmux`, `screen`, `nohup`, `systemd-run`, or a site batch scheduler when available.
- Native Windows is not a local execution mode for this workflow. On Windows, use WSL2 or SSH as the execution target.
- Durable execution must write enough state to resume: job name, PID/job id, command, working directory, stdout/stderr paths, and a phase progress manifest under `{workdir}/results/`.
- Storage pressure may trigger documented cleanup of intermediate ROOT/LHE/HEPMC files after required outputs are copied. Storage pressure must not trigger event-count reduction.

## Workflow Logging Contract

`{workdir}/results/workflow.log` is mandatory from Phase 2 onward.

Rules:
- The first action in Phase 2 must initialize and validate the log with `scripts/workflow_logger.py {workdir} --touch`, or the target-aware equivalent through `scripts/remote_exec.py`.
- Every phase must append `phase_start` before any filesystem, subprocess, download, install, or analysis operation.
- Every phase must append `phase_complete` only after its completion unit is satisfied, or `phase_fail` only for a proven unrecoverable failure.
- Every execution phase must contain step records. A phase with only `phase_start`/`phase_complete` and no `level="step"` records is an invalid bug-report log, even if resume technically works.
- Repeated `phase_start` for the same phase before a completion/failure record must be logged as a recovery/resume anomaly with the reason.
- Do not create workflow files with heredoc markers, shell EOF redirection, or shell clobber redirection. Forbidden patterns include `cat <<EOF`, `python <<EOF`, `python - <<EOF`, `> EOF`, `>> EOF`, `> !`, and `>!`.
- A file literally named `EOF` or `!` in `{workdir}` or `{workdir}/results` is a logging/bootstrap violation. Stop the current shell-writing approach, initialize `workflow.log`, record the anomaly, and continue using Python file APIs or bundled scripts.
- Do not rely on conversation text as a log. The JSONL `workflow.log` is the resume source of truth.
- `workflow.log` is also the bug-report source of truth. Records must include enough detail to diagnose failures after publication: commands or script arguments, target paths, return codes, output paths, retry attempts, exception type, traceback, and relevant stdout/stderr log paths.
- Prefer `run_logged_subprocess(...)` from `scripts/workflow_logger.py` for subprocesses so command arguments, cwd, return code, duration, stdout/stderr paths, and output tails are recorded consistently.

## Required Inputs

Phase 1 must collect and validate:

| Field | Meaning |
|---|---|
| `execution` | Where commands run: current Linux/Unix shell, SSH target, or WSL2 target |
| `madgraph_path` | Absolute path to MadGraph5, or auto-installed path |
| `workdir` | Directory where all workflow outputs are written |
| `process` | Physics process only; no `NP=`, `QED=`, or `QCD=` suffix |
| `models` | One or more UFO model names, preserving user order |
| `energy` | Center-of-mass energy in TeV; scalar or list |
| `luminosity` | Integrated luminosity in fb^-1; scalar or list matching energy length |
| `cutexperiment_path` | Existing or cloned CutExperiment path |
| `delphes_card` | Recommended or user-selected detector card |
| `debug`, `algorithms`, `polarization`, `analysis_notes` | Optional settings from `[9/9]` |

## Locked Runtime Contract

Phase 1 writes these locked event counts to `run_config.json`; every phase must read them from config and never recompute or resize them.

| Key | Normal | Debug |
|---|---:|---:|
| `nev_phase3` | 10000 | 1000 |
| `nev_phase4` | 10000 | 1000 |
| `nev_sm` | 500000 | 50000 |
| `nev_np` | 100000 | 10000 |
| `nev_scan` | 1000000 | 100000 |

Only `debug=true`, explicitly collected in Phase 1, may select the debug values. No later phase may change them.

## Execution Target Contract

Phase 1 determines where commands execute and writes it to `run_config.json`.

| Mode | Meaning | Path interpretation |
|---|---|---|
| `local` | Run commands in the current Linux/Unix environment; unavailable on native Windows | local filesystem paths |
| `ssh` | Run commands on a remote Linux host through SSH | paths on the SSH host |
| `wsl2` | Run commands inside a local WSL2 Linux distro | paths inside WSL2 |

From Phase 2 onward, do not hand-write ad-hoc SSH or WSL command prefixes. Use `scripts/remote_exec.py` for target-aware command execution when `execution.mode` is `ssh` or `wsl2`.

In SSH/WSL2 mode, Phase 1 must write two identical `run_config.json` copies: a local control copy readable by the agent, and the target copy at `{workdir}/results/run_config.json`. The local control copy is used only for orchestration; workflow outputs remain on the selected execution target.

## Phase Completion Contracts

Every phase has a completion unit. Red flags are evaluated only after that unit completes.

| Phase | Completion unit | Early stop allowed? |
|---|---|---|
| 2 | All environment checks finish | Only unrecoverable missing dependency or invalid config |
| 3 | Every coefficient in every requested model is tested | No. Individual `sigma=0` is a valid result |
| 4 | SM baseline and coefficient range are written | Only `cs_sm=0` or MG5 failure |
| 5 | Pure SM and anchor NP samples are generated | Only unrecoverable generation/conversion failure |
| 6 | All 11 scan points for all claimed operators are processed | No partial scan red flag; no runtime red flag |
| 7 | All selected ML algorithms are trained and recorded | No early algorithm filtering |
| 8 | Threshold optimization and fits are attempted for required algorithms/operators | Fit issues are recorded unless unrecoverable |
| 9 | Constraints are computed for S=2,3,5 where mathematically possible | Numerical red flags are recorded |
| 10 | Report is generated | Use HTML fallback if PDF generation fails |
| Cleanup | MG5 process folders/orders are moved into results | Only filesystem failure |
| 11 | Audit file is written | Final report only |

### Phase 3 Loop Lock

Phase 3 must complete the full operator loop before any sensitivity decision.

For each coefficient:
1. Run MG5 with the locked Phase 3 event count.
2. Extract and record `sigma`.
3. If `sigma > 0`, claim/deduplicate the operator.
4. Continue immediately to the next coefficient.

Only after `tested_count == total_coefficients_across_all_models` may Phase 3 check whether `nonzero_count == 0`. If all operators are zero, write the full zero-cross-section report and stop. Several zero operators are not a reason to ask the user or stop.

## Workflow References

| Phase | Purpose | Reference |
|---|---|---|
| 1 | Input collection | [`reference/phase1-input-collection.md`](reference/phase1-input-collection.md) |
| 2 | Environment validation | [`reference/phase2-env.md`](reference/phase2-env.md) |
| 3 | Operator sensitivity validation | [`reference/phase3-validation.md`](reference/phase3-validation.md) |
| 4 | Coefficient range estimate | [`reference/phase4-range.md`](reference/phase4-range.md) |
| 5 | Pure SM/NP samples | [`reference/phase5-pure-samples.md`](reference/phase5-pure-samples.md) |
| 6 | Coefficient scans | [`reference/phase6-scan.md`](reference/phase6-scan.md) |
| 7 | ML training | [`reference/phase7-ml-training.md`](reference/phase7-ml-training.md) |
| 8 | Selection and fitting | [`reference/phase8-selection.md`](reference/phase8-selection.md) |
| 9 | Constraints | [`reference/phase9-constraints.md`](reference/phase9-constraints.md) |
| 10 | Report | [`reference/phase10-report.md`](reference/phase10-report.md) |
| Cleanup | Process-folder collection | [`reference/cleanup.md`](reference/cleanup.md) |
| 11 | Audit | [`reference/phase11-audit.md`](reference/phase11-audit.md) |

Use the MadGraph conventions in [`reference/madgraph-reference.md`](reference/madgraph-reference.md), model-copy rules in [`reference/model-dependencies.md`](reference/model-dependencies.md), CutExperiment rules in [`reference/cutexperiment-reference.md`](reference/cutexperiment-reference.md), and report guidance in [`reference/report-writing-guide.md`](reference/report-writing-guide.md).

## Scripts

Prefer bundled scripts for deterministic pieces:

| Script | Purpose |
|---|---|
| `scripts/load_run_config.py` | Load/validate `run_config.json` |
| `scripts/install_mg5.py` | Install MG5 after the agent dynamically resolves the Launchpad download URL |
| `scripts/install_cutexperiment.py` | Clone/validate CutExperiment |
| `scripts/remote_exec.py` | Run commands locally, over SSH, or inside WSL2 |
| `scripts/sync_to_target.py` | Copy local files/directories such as `run_config.json` or bundled UFO models to SSH/WSL2 targets |
| `scripts/durable_exec.py` | Start/status long-running commands without relying on an interactive session |
| `scripts/run_mg5.py` | Run MG5 order files with return-code checking |
| `scripts/parse_param_card.py` | Parse coefficient blocks |
| `scripts/extract_cross_section.py` | Parse MG5 banner cross-sections |
| `scripts/setup_delphes_card.py` | Copy Delphes cards/dependencies |
| `scripts/convert_root_to_lhco.py` | Convert ROOT outputs to LHCO |
| `scripts/workflow_logger.py` | Append-only phase/step log |
| `scripts/read_results.py` | Typed JSON result readers |

## Output Layout

Single run:

```text
results/
  run_config.json
  workflow.log
  data/
  plots/
  algorithms/
  mg5_processes/
  orders/
  report.html or report.pdf
```

Multi-run:

```text
results/
  run_config.json
  E10_L1000/
    workflow.log
    data/
    plots/
    algorithms/
    mg5_processes/
    orders/
    report.html or report.pdf
  E14_L3000/
    ...
```

All paths are relative to `workdir`. Never write workflow outputs into the skill directory.

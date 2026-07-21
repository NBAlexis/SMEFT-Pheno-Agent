---
name: automated-smeft-ml-pheno
description: "Use for serious long-running SMEFT collider phenomenology studies: collect inputs, run MadGraph5/Delphes/root2lhco/CutExperiment, train ML selectors, scan Wilson coefficients, compute constraints, and produce a scientific manuscript."
---

# Automated SMEFT Phenomenology with Machine Learning

Run an end-to-end SMEFT collider phenomenology workflow: collect study inputs, validate the environment, generate SM/NP samples with MadGraph5, convert event outputs, train ML selectors, optimize event selection, compute expected Wilson-coefficient constraints, generate a publication-style manuscript, clean up MG5 process folders, package a one-command numerical replay, and audit consistency.

## Research Mission

This skill is for serious scientific research, not quick demonstration runs. The
goal is to produce a scientifically usable manuscript after numerical
simulation, with reproducible data, plots, fit coefficients, constraints, and
audit logs.

After Phase 1 collects the required inputs, Phases 2-12 are an automated,
unattended research workflow. Week-scale or longer computation is expected and
normal. Do not downgrade the workflow to a progress summary, run report,
partial result, informal answer, reduced scan, reduced event count, or HTML
fallback while LaTeX is available or build errors are recoverable.

## Highest-Priority Contract

At the end of Phase 1, create two immutable contracts from the validated
`run_config.json`:

- `results/research_contract.json` freezes the scientific question and choices
  that determine its meaning.
- `results/deliverables_contract.json` freezes the required evidence and the
  deterministic rules that expand it for runs, operators, scan points, and
  algorithms.

These contracts define the task. Do not reduce, reinterpret, replace, or silently
edit either contract because a tool fails, a standard script is unsuitable, the
runtime is long, or the environment changes. Technical locations and
implementations may change when the scientific objective, schemas, provenance,
and required outputs remain equivalent.

The phases and bundled scripts are the tested standard execution path, not the
research objective. Start from them because they encode known-good conventions.
When they fail or do not fit the actual run, inspect the evidence, diagnose the
cause, and repair, extend, replace, or write scripts as needed. A command, card,
dependency, runner, parser, or conversion failure is a technical problem to
solve; it is not by itself evidence that the research failed.

Terminate without completing the contracts only after recording concrete
evidence that the frozen research objective or a required deliverable is
impossible to fulfill. Exhaust reasonable unattended recovery, alternative
implementations, and scientifically equivalent environment migration first.

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

Execution Mode begins only after Phase 1 writes a valid `run_config.json` and
initializes both frozen contracts. From Phase 2 onward, user interaction is
disabled.

#### Contract-Preserving Autonomy

In Execution Mode, continue autonomously toward the frozen contracts. Runtime,
repeated failures, a broken standard script, a missing package, a Delphes-card
dependency, or an unfamiliar technical problem is not a reason to ask the user
what to do. Investigate logs and artifacts, test hypotheses, preserve failed
attempt evidence, and choose the next technically sound recovery.

Follow the phase order by default because downstream artifacts depend on
upstream results. It is acceptable to create diagnostic code, adapters, or
recovery helpers whenever they are needed to unblock the current scientific
deliverable. Record deviations from the standard path and why the replacement
is scientifically equivalent.

#### Phase-End Invariant Self-Check

Before `logger.phase_complete("N")` in any execution phase, read
[`reference/workflow-invariants.md`](reference/workflow-invariants.md), check the
invariants relevant to that phase, fix violating artifacts, log the correction,
and continue without asking the user.

#### Phase Delivery Gate

Before `logger.phase_complete("N")`, verify the relevant subset of the frozen
deliverables contract and read the deliverable file linked by the
current phase reference (for example, Phase 5 reads only
`reference/deliverables-phase5.md`). Phase 1 missing intake fields must be
re-asked; Phases 2-12 missing deliverables must be repaired or resumed
autonomously. Do not advance to the next phase until the gate passes. Do not
load other phase deliverable files unless repairing an upstream failure or
running Phase 12 audit.

Delivery definitions:
- Paths in deliverable files are relative to the current run root: `results/`
  for single-run mode, or `results/{run_dir}/` for multi-run mode.
- A delivered file must exist and be non-empty. JSON must parse and contain the
  required keys; CSV/PDF/LHCO/plot files must be non-empty; any path referenced
  inside a JSON deliverable must exist unless an explicit allowed
  `missing_reason` field is required by that phase.
- `o_N` always means the global operator key from Phase 3
  `operator_claims.json`, not a UFO-internal coefficient index.
- `alg` means the stable algorithm key used in
  `algorithm_comparison.json["anchor"]`. Use the same key for model files,
  score directories, fit files, plots, and manuscript evidence.

## Long-Run Execution Contract

Runtime from hours to months is normal. Never change physics, event counts,
operators, scan points, or algorithms because of time estimates. Use
`scripts/durable_exec.py`, `tmux`, `screen`, `nohup`, `systemd-run`, or a site
scheduler when work may outlive the foreground session, and record resumable job
state plus stdout/stderr paths.

- Native Windows is not a local execution mode for this workflow. On Windows, use WSL2 or SSH as the execution target.
- Storage pressure may trigger documented cleanup of intermediate ROOT/LHE/HEPMC files after required outputs are copied. Storage pressure must not trigger event-count reduction.

## Workflow Logging Contract

`{workdir}/results/workflow.log` is the mandatory resume and bug-report record
from Phase 2 onward. Initialize it before Phase 2 work. Record skill version and
commit, phase/step boundaries, commands, cwd, return codes, outputs, retries,
exceptions, and stdout/stderr paths.

- Every phase must append `phase_complete` only after its contract subset is
  satisfied. Write `phase_fail` only when the frozen contract is demonstrably
  impossible, not merely when a command or standard script fails.

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

## Execution Target

Phase 1 records `local`, `ssh`, or `wsl2` execution. Treat target and tool paths
as mutable technical state, not as the scientific objective.
Use `scripts/remote_exec.py` as the standard target-aware adapter for SSH/WSL2.
If it is the source of a technical failure, repair it or use an equivalent
logged execution method that preserves target semantics and provenance.

In SSH/WSL2 mode, keep identical local-control and target copies of
`run_config.json` and both frozen contracts.

## Phase Completion Contracts

Every phase must satisfy its frozen contract subset before completion:

| Phase | Completion unit |
|---|---|
| 2 | Environment and contract verification |
| 3 | Every coefficient in every requested model tested; zero-result branch reported |
| 4-6 | Baselines, per-operator ranges, pure samples, and all 11-point scans |
| 7-9 | Frozen algorithm strategy, fits, and S=2,3,5 constraints |
| 10 | Publication manuscript and evidence |
| Cleanup | Process/order provenance archived |
| 11 | One-command numerical replay and data-file report |
| 12 | Fully resolved deliverables contract and final audit |

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
| 10 | Manuscript | [`reference/phase10-manuscript.md`](reference/phase10-manuscript.md) |
| Cleanup | Process-folder collection | [`reference/cleanup.md`](reference/cleanup.md) |
| 11 | Numerical replay package | [`reference/phase11-replay.md`](reference/phase11-replay.md) |
| 12 | Audit | [`reference/phase12-audit.md`](reference/phase12-audit.md) |

Use the MadGraph conventions in [`reference/madgraph-reference.md`](reference/madgraph-reference.md), event-count/recovery rules in [`reference/event-count-recovery.md`](reference/event-count-recovery.md), model-copy rules in [`reference/model-dependencies.md`](reference/model-dependencies.md), CutExperiment rules in [`reference/cutexperiment-reference.md`](reference/cutexperiment-reference.md), and manuscript guidance in [`reference/manuscript-writing-guide.md`](reference/manuscript-writing-guide.md).
Each phase reference links its own `deliverables-phaseN.md` completion contract. Read only the current phase's deliverable file during normal execution.

## Scripts

Use bundled scripts as the standard path for deterministic and fragile pieces.
When they work, prefer them to reduce avoidable variation. They are not an
implementation restriction: inspect, patch, wrap, or replace them, and write
project-specific scripts when the run requires it. Any alternative must preserve
the frozen objective, required output schemas, physics settings, seeds/event
counts, logs, checksums, and provenance. Package non-bundled production code in
Phase 11 so the study remains replayable.

Key entry points are `load_run_config.py`, `research_contract.py`,
`remote_exec.py`, `durable_exec.py`, `run_mg5_config.py`,
`recover_lhco_count.py`, `workflow_logger.py`, and
`audit_expected_outputs.py`. Read the current phase reference for the smaller
parsers, conversion helpers, installation tools, and expected schemas.

## Output Layout

Keep global contracts under `{workdir}/results/`; keep single-run outputs there
or multi-run outputs under `results/{run_dir}/`. The frozen deliverables template
in [`reference/deliverables-contract-template.json`](reference/deliverables-contract-template.json)
is the authoritative layout. Never write workflow outputs into the skill folder.

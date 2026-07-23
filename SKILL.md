---
name: automated-smeft-ml-pheno
description: "Use for full SMEFT collider phenomenology studies or debug-mode workflow tests: collect inputs, run MadGraph5/Delphes/root2lhco/CutExperiment, train ML selectors, scan Wilson coefficients, compute constraints, and produce the required manuscript and replay artifacts."
---

# Automated SMEFT Phenomenology with Machine Learning

Run an end-to-end SMEFT collider phenomenology workflow: collect study inputs, validate the environment, generate SM/NP samples with MadGraph5, convert event outputs, train ML selectors, optimize event selection, compute expected Wilson-coefficient constraints, generate a publication-style manuscript, clean up MG5 process folders, package a one-command numerical replay script and data-file report, and audit consistency.

## Research Mission

With `debug=false`, use this skill for serious scientific research whose goal is
a scientifically usable manuscript with reproducible data, plots, fit
coefficients, constraints, and audit logs. With `debug=true`, test the same
complete workflow and deliverable structure with the reduced locked event
counts; do not describe its numerical results as statistically reliable or
publication-ready.

After Phase 1 collects the required inputs, Phases 2-12 are automated and
unattended. Week-scale or longer computation is normal for `debug=false`.
Do not downgrade either `debug` setting to a progress summary, partial result,
informal answer, reduced scan, event counts below the values locked for that
setting, or an HTML fallback while LaTeX is available or build errors are
recoverable.

## Highest-Priority Contract

At the end of Phase 1, create two immutable contracts and one contract lock from the validated
`run_config.json`:

- `results/research_contract.json` freezes the scientific question and choices
  that determine its meaning.
- `results/deliverables_contract.json` freezes the required evidence and the
  deterministic rules that expand it for runs, operators, scan points, and
  algorithms.
- `results/contract_lock.json` binds the exact two contract documents and their
  objective/template hashes as one frozen set.

Here `immutable` and `frozen` mean that `research_contract.py init` compares
parsed JSON content and refuses to overwrite an existing different value, while
`research_contract.py verify` checks the objective, template, and lock SHA-256
values. They do not mean filesystem read-only permissions.

These contracts define the task. Do not reduce, reinterpret, replace, or silently
edit either contract because a tool fails, a standard script is unsuitable, the
runtime is long, or the environment changes. Technical locations and
implementations may change only when `research_contract.py verify` still
returns `status="ok"`, every declared deliverable keeps the same path and
acceptance fields, all locked physics settings and event counts are unchanged,
and the replacement records its command, code checksum, inputs, and outputs in
`workflow.log`. Deliverable paths, formats, required
keys/columns, and acceptance rules are fixed contract requirements; an
alternative implementation must satisfy them exactly rather than weakening or
renaming them.

The research contract also freezes these six method boundaries after Phase 1:

- Generate every numerical analysis sample with MG5 and Delphes. Never analyze
  events taken directly from an undetected LHE file.
- With `debug=false`, treat the five locked scientific event counts below as
  per-run minima. If statistical support is still insufficient, add full-size
  runs and merge them. With `debug=true`, use the locked reduced counts to test
  the complete workflow and do not claim strict scientific reliability from
  those results.
- Convert Delphes LHCO events to CSV and make the final selection with a trained
  ML score threshold. A fixed final-state particle-number preselection is
  allowed; a traditional hand-designed kinematic cut analysis cannot replace
  the ML selection.
- Derive expected coefficient constraints only from fitted cross-sections after
  ML selection and the declared signal-significance formula.
- Compare strategies usable under the selected `debug` setting only by expected
  coefficient-constraint interval width. AUC may describe or diagnose a
  classifier but must never rank or select the final strategy.
- Deliver every Phase 10 manuscript item frozen in
  `phase10_required_manuscript_items`. Earlier phases must provide the evidence
  needed for those items without inventing unrelated scientific requirements.

ML algorithms, implementations, and hyperparameters remain changeable. With
`debug=false`, the LLM may reject or repair a candidate with inadequate event
support, invalid fits, or numerical instability. With `debug=true`, repair
technical failures and unusable numerical outputs, but do not add full-size runs
only to obtain formal statistical reliability. Under either `debug` setting it
may use `per_operator_best`; among candidates usable under that setting it must
still choose the narrowest expected constraint interval.

The phases and bundled scripts are the tested standard execution path, not the
research objective. Start from them because they encode known-good conventions.
When they fail or do not fit the actual run, inspect the evidence, diagnose the
cause, and repair, extend, replace, or write scripts as needed. A command, card,
dependency, runner, cross-section extraction, or conversion failure is a technical problem to
solve; it is not by itself evidence that the research failed.

A technical failure is a command, dependency, environment, card,
file-conversion, or implementation error that prevents a required output from
being produced; a valid zero cross-section or other valid negative scientific
result is not a technical failure. Diagnose the recorded error, attempt a
targeted repair, and then try an alternative implementation or another
compatible Linux target when applicable.

Write `phase_fail` only after creating
`results/failures/phase{N}_failure.json` (or the current multi-run root
equivalent) with `technical_cause`, `affected_deliverables`, `attempts`,
`evidence_paths`, and `why_no_remaining_method_can_preserve_the_contract`.
Every `attempts` entry must contain `command_or_code_path`, `change_tested`,
`return_code`, `stdout_path`, and `stderr_path`. The final field must identify the exact
objective field or deliverable acceptance rule that every remaining method
would violate. Repeated command failure without this evidence does not permit
`phase_fail`.

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
initializes both frozen contracts plus their lock. From Phase 2 onward, user interaction is
disabled.

#### Contract-Preserving Autonomy

In Execution Mode, continue autonomously toward the frozen contracts. Runtime,
repeated failures, a broken standard script, a missing package, a Delphes-card
dependency, or an unfamiliar technical problem is not a reason to ask the user
what to do. Investigate logs and artifacts, test hypotheses, preserve failed
attempt evidence, and choose the next technically sound recovery.

Treat validator output as diagnostic evidence. When a deliverable check fails,
read its `failure_code`, `failure_reason`, missing keys/columns, and path details,
then repair the producer or artifact. Never delete or relax an acceptance rule to
make a technical failure disappear.

The scientific objective and the six fixed method boundaries have priority over
a default implementation or bundled audit. An ML algorithm, its hyperparameters,
a fitting implementation, or an audit check may be changed when the actual data
or a user additional requirement gives a scientific reason. Record the reason,
evidence paths, changed code and checksum, and affected outputs. Keep the frozen
deliverable paths, file formats, required fields, and operator coverage. Changing
an audit to validate the actual contract-preserving method is allowed; changing
it only to turn an unexplained failure into a pass is not.

Use `anchor_operator_only` as the default final-selection strategy because one
anchor-trained selector is normally adequate for related operators. This is a
rebuttable default, not a frozen research choice. Use `per_operator_best` when
the user requested it in `analysis_notes.additional_requirements`, or when the
data show that the common strategy lacks sufficient event support, a valid fit,
numerical stability, or reportable constraints for one or more operators. Let
the LLM judge that evidence, record the rationale and evidence in Phase 9, and
freeze the actual final choice only in Phase 11.

Follow the phase order by default because downstream artifacts depend on
upstream results. It is acceptable to create diagnostic code, adapters, or
recovery helpers whenever they are needed to unblock the current scientific
deliverable. Record deviations from the standard path and the verification
results required by the Highest-Priority Contract section.

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

Phase 11 is the only exception to this delivery gate. It only writes the replay
package and data-file report; `WorkflowLogger.phase_complete("11")` records
completion without invoking an audit. Phase 12 performs the non-executing
static inspection of those files. Neither phase runs replay code.

Run `python scripts/audit_expected_outputs.py {workdir} --phase N` and add
`--run-dir {run_dir}` in multi-run mode. `WorkflowLogger.phase_complete()` runs
the same check and raises an error instead of writing a completed record when a
current-Phase rule fails. A current-Phase rule is an entry in
`deliverables_contract.json["template"]["rules"]` whose `phase` equals `N`.
In audit output, `severity="abort"` means a required check failed: continue
collecting diagnostics, set the audit status to `FAIL`, repair the producer, and
rerun the check. It never means skip diagnostics or immediately write
`phase_fail`.

Delivery definitions:
- Paths in deliverable files are relative to the current run root: `results/`
  for single-run mode, or `results/{run_dir}/` for multi-run mode.
- Set the phase variable `run_dir=None` when `run_configurations` contains one
  entry. When it contains more than one entry, process each entry separately and
  set `run_dir` to that entry's non-empty `run_dir` value. Pass the same value to
  `WorkflowLogger`, `research_contract.py --run-root`, and
  `audit_expected_outputs.py --run-dir`.
- A delivered file must exist and be non-empty. JSON must parse and contain the
  required keys; CSV/PDF/LHCO/plot files must be non-empty; any path referenced
  inside a JSON deliverable must exist unless an explicit allowed
  `missing_reason` field is required by that phase.
- `o_N` always means the global operator key from Phase 3
  `operator_claims.json`, not a UFO-internal coefficient index.
- `alg` means the stable algorithm key used in
  `algorithm_comparison.json["anchor"]`. Use the same key for model files,
  score directories, fit files, plots, and manuscript evidence.
- `analysis_notes.focused_operators` changes only plot, table, and manuscript
  emphasis; it never reduces the required operator set. Phase 10 records every
  focused operator and manuscript preference in
  `manuscript_evidence.json["analysis_notes_trace"]`. Apply every
  `analysis_notes.additional_requirements` entry in each phase listed in its
  `applies_to_phases` field and record a completed workflow step for it.

## Long-Run Execution Contract

Runtime from hours to months is normal for `debug=false`; `debug=true` uses the
locked reduced counts specifically to test the workflow at lower cost. Never
change physics, event counts locked for the selected `debug` setting, operators,
scan points, or algorithms because of time estimates. Use
`scripts/durable_exec.py`, `tmux`, `screen`, `nohup`, `systemd-run`, or a site
scheduler when work may outlive the foreground session, and record resumable job
state plus stdout/stderr paths.

- Native Windows is not a local execution mode for this workflow. On Windows, use WSL2 or SSH as the execution target.
- Storage pressure may trigger documented deletion of intermediate ROOT and
  HEPMC files after required outputs are secured. LHE/LHE.GZ files, cards,
  banners, logs, JSON, order files, scripts, and configuration files are not
  deletion targets; archive them with the recorded MG5 process directories.
  Storage pressure must not trigger event-count reduction.

## Workflow Logging Contract

`{workdir}/results/workflow.log` is the mandatory resume and bug-report record
from Phase 2 onward. Initialize it before Phase 2 work. Record skill version and
commit, phase/step boundaries, commands, cwd, return codes, outputs, retries,
exceptions, and stdout/stderr paths.

- Every phase must append `phase_complete` only after its current-Phase rules
  pass. `phase_fail` means the event written by `WorkflowLogger.phase_fail()`
  after the required failure JSON above exists; a command failure alone never
  permits it.

## Locked Runtime Contract

Phase 1 writes the event counts selected by `debug` to `run_config.json`; every
phase must read them from config and must not lower them. `debug=false` is the
formal scientific mode: the scientific values below are per-run minima, and
insufficient statistical support requires another full-size run followed by a
merge of accepted events and metadata. `debug=true` is a workflow test: it must
exercise the complete MG5/Delphes, LHCO-to-CSV, ML-selection, constraint, and
deliverable path, but the reduced results are not strict scientific results and
do not require full-size statistical convergence.

| Key | Scientific (`debug=false`) | Workflow test (`debug=true`) |
|---|---:|---:|
| `nev_phase3` | 10000 | 1000 |
| `nev_phase4` | 10000 | 1000 |
| `nev_sm` | 500000 | 50000 |
| `nev_np` | 100000 | 10000 |
| `nev_scan` | 1000000 | 100000 |

The selected `debug` setting and all five corresponding values are frozen after
Phase 1. Do not switch a formal run to debug or reduce the locked values for
either setting later because execution is slow. All other fixed method
boundaries apply unchanged under both settings.

## Execution Target

Phase 1 records `local`, `ssh`, or `wsl2` execution. Treat target and tool paths
as mutable technical state, not as the scientific objective.
Use `scripts/remote_exec.py` as the standard target-aware adapter for SSH/WSL2.
If it is the source of a technical failure, repair it or use another logged
method that executes the same command on the configured SSH host or WSL2
distribution. Record command, target, cwd, return code, stdout/stderr paths, and
rerun `research_contract.py verify` afterward.

In SSH/WSL2 mode, keep identical local-control and target copies of
`run_config.json`, both frozen contracts, and `contract_lock.json`.

## Phase Completion Contracts

Every phase except Phase 11 must satisfy all rules whose `phase` value equals
that phase before completion. Phase 11 follows the delivery-gate exception
above: it records package generation without running an audit, and Phase 12
performs the non-executing static inspection.

| Phase | Completion unit |
|---|---|
| 2 | Environment and contract verification |
| 3 | Every coefficient in every requested model tested; zero-result branch reported |
| 4-6 | Baselines, per-operator ranges, pure samples, and all 11-point scans |
| 7-9 | Recorded trained algorithms, fits, selected production algorithm, and S=2,3,5 constraints |
| 10 | Manuscript and evidence; publication-ready only for `debug=false`, clearly labeled workflow-test output for `debug=true` |
| Cleanup | Process/order provenance archived |
| 11 | One-command numerical replay package and data-file report |
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
| 8 | Selection and fitting | [`reference/phase8-selection.md`](reference/phase8-selection.md) and [`reference/phase8-shared-f5.md`](reference/phase8-shared-f5.md) |
| 9 | Constraints | [`reference/phase9-constraints.md`](reference/phase9-constraints.md) |
| 10 | Manuscript | [`reference/phase10-manuscript.md`](reference/phase10-manuscript.md) |
| Cleanup | Process-folder collection | [`reference/cleanup.md`](reference/cleanup.md) |
| 11 | Numerical replay package and data-file report | [`reference/phase11-replay.md`](reference/phase11-replay.md) |
| 12 | Audit | [`reference/phase12-audit.md`](reference/phase12-audit.md) |

Load shared references only when the current phase needs them:

| Phases | Shared reference |
|---|---|
| 1-2 | [`reference/model-dependencies.md`](reference/model-dependencies.md) |
| 3-6 | [`reference/madgraph-reference.md`](reference/madgraph-reference.md) |
| 5-8 | [`reference/event-count-recovery.md`](reference/event-count-recovery.md) and [`reference/cutexperiment-reference.md`](reference/cutexperiment-reference.md) |
| 10 | [`reference/manuscript-writing-guide.md`](reference/manuscript-writing-guide.md) and only the guides it selects |

Each phase reference links its own `deliverables-phaseN.md` completion contract.
During normal execution, read the current phase reference, its listed shared
references, and only that phase's deliverable file. Load another phase only to
repair a specific upstream artifact.

## Scripts

Use bundled scripts as the standard path for deterministic and fragile pieces.
When they work, prefer them to reduce avoidable variation. They are not an
implementation restriction: inspect, patch, wrap, or replace them, and write
project-specific scripts when the run requires it. Any alternative must preserve
the frozen objective, required output schemas, physics settings, event
counts, logs, checksums, and provenance. Package non-bundled production code in
Phase 11 so the study remains replayable. Algorithms are execution methodology,
not part of the Phase 1 research objective. Phase 11 must freeze the algorithms
actually trained and selected, including implementations, hyperparameters,
score definitions, model-output paths, the exact Phase 9 selection criterion,
rationale, evidence, operator assignments, and packaged code checksums.
Before Phase 11, an algorithm or its implementation may change to resolve a
technical or scientific-validity problem. After such a change, rerun every
affected Phase 7-10 producer so all algorithm keys, scores, fits, constraints,
plots, and manuscript evidence agree. Phase 11 then records the final actual
state; it does not retroactively add algorithms to the Phase 1 objective.

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

## Rule Precedence

Apply conflicting instructions in this order:

1. `research_contract.json` defines the scientific objective.
2. `deliverables_contract.json["template"]` defines required paths, types,
   required keys and columns, fixed values, and minimum sizes.
3. `deliverables-phaseN.md` and the Phase reference explain how to produce those
   exact files. They may add scientific consistency checks but may not rename or
   remove a template item.
4. `audit_expected_outputs.py` is the tested default implementation for checking
   the two JSON documents and cross-phase numerical consistency. If the actual
   scientifically justified method requires a different check, modify or replace
   the checker, record that implementation and its evidence, and keep the frozen
   deliverable paths, formats, required fields, and operator coverage. Do not
   weaken a check merely to hide an unexplained failure.

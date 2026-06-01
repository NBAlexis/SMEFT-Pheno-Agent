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

## SUPREME RULE: Execution Continuity

Once Execution Mode starts, keep running until the workflow reaches a valid phase-completion boundary, an unrecoverable error, a documented red flag after phase completion, or an explicit user stop command.

Rules:
- Do not ask whether to continue.
- Do not ask whether to reduce event counts.
- Do not ask what to do with zero cross-sections.
- Do not stop because a command is slow.
- Do not alter physical parameters for speed or convenience.
- Recover from MG5, Delphes, ROOT, root2lhco, filesystem, and parsing issues when a conservative recovery is possible; otherwise stop only with concrete evidence of an unrecoverable error.

## Required Inputs

Phase 1 must collect and validate:

| Field | Meaning |
|---|---|
| `madgraph_path` | Absolute path to MadGraph5, or auto-installed path |
| `workdir` | Directory where all workflow outputs are written |
| `process` | Physics process only; no `NP=`, `QED=`, or `QCD=` suffix |
| `models` | One or more UFO model names, preserving user order |
| `energy` | Center-of-mass energy in TeV; scalar or list |
| `luminosity` | Integrated luminosity in fb^-1; scalar or list matching energy length |
| `cutexperiment_path` | Existing or cloned CutExperiment path |
| `delphes_card` | Recommended or user-selected detector card |
| `preferences` | Optional settings from `[9/9]` |

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

## Phase Completion Contracts

Every phase has a completion unit. Red flags are evaluated only after that unit completes.

| Phase | Completion unit | Early stop allowed? |
|---|---|---|
| 2 | All environment checks finish | Only unrecoverable missing dependency or invalid config |
| 3 | Every coefficient in every requested model is tested | No. Individual `sigma=0` is a valid result |
| 4 | SM baseline and coefficient range are written | Only `cs_sm=0` or MG5 failure |
| 5 | Pure SM and anchor NP samples are generated | Only unrecoverable generation/conversion failure |
| 6 | All 11 scan points for all claimed operators are processed | No partial scan red flag |
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

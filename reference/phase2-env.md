# Phase 2: Environment Validation

> **Contract priority**: Preserve the research objective and deliverables. Apply the technical-failure and `phase_fail` definitions in `SKILL.md`.

## Purpose

Verify all non-MG5 dependencies exist before starting the workflow. Phase 1 has
already validated the MG5 stack. Phase 2 reads the local control copy of
`run_config.json`, the two frozen contracts, and `contract_lock.json` produced by Phase 1. In SSH/WSL2
mode, the same four JSON files must also exist at `{workdir}/results/` on the
selected target. No parameter should be sourced from conversation history or
user interaction.

## Prerequisite

```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")
```

All steps below reference fields from `config`.

## Execution Target

Read `config.execution.mode` before running any command:

| Mode | Meaning | Path semantics |
|---|---|---|
| `local` | Run commands in the current Linux/Unix environment; invalid on native Windows | local filesystem paths |
| `ssh` | Run commands on `config.execution.ssh_target` | Linux paths on the SSH host |
| `wsl2` | Run commands inside WSL2 | Linux paths inside the WSL2 distro |

For target-aware commands, use:

```bash
python scripts/remote_exec.py --config {local_run_config} --cwd {target_cwd} -- {command}
```

Use `remote_exec.py` as the standard SSH/WSL adapter. A custom or repaired
adapter is allowed when it preserves command, cwd, return-code, and stdout/stderr
provenance. In SSH and WSL2 modes, do not validate target paths with local
`os.path.exists`.

Native Windows is not a valid `local` execution target for MG5. If `config.execution.mode == "local"` on Windows, `load_run_config.py` must fail and Phase 1 must be rerun with WSL2 or SSH.

## Long-Run Setup

Create `{workdir}/results/jobs/` on the selected execution target. Later phases may use this directory for durable PID, stdout, stderr, and status files when a command may outlive the foreground agent session.

Runtime duration is not a validation failure. Do not reject a configuration because a later MG5/Delphes phase may take hours, days, weeks, or months.

## Log Bootstrap

This is the first executable action in Phase 2. It must happen before dependency checks, downloads, installs, or MG5 commands:

```bash
python scripts/workflow_logger.py {workdir} --touch
```

In SSH/WSL2 mode, run the same command on the selected target through `scripts/remote_exec.py`.

Then start Phase 2:

```python
from scripts.workflow_logger import WorkflowLogger

logger = WorkflowLogger(config.workdir, run_dir)
logger.assert_ready()
logger.phase_start("2")
```

If `{workdir}/EOF`, `{workdir}/!`, `{workdir}/results/EOF`, or `{workdir}/results/!` exists, treat it as evidence that heredoc, shell redirection, or shell clobber syntax was used incorrectly. Do not continue with that shell-writing pattern. Initialize `workflow.log`, record the anomaly with `logger.step(...)`, and use Python file APIs or bundled scripts for subsequent file writes.

Bug-report logging requirements:
- A phase is not adequately logged unless it contains `level="step"` records for the major operations in that phase.
- For every subprocess, log the executable/script, arguments, target cwd, return code, stdout/stderr log path, and produced output paths.
- Prefer `run_logged_subprocess(...)` from `scripts/workflow_logger.py` over bare `subprocess.run(...)`.
- For every recovery attempt, log the failed unit, reason, cleanup action, renamed/broken directory, retry attempt number, and final success/failure.
- For every exception, preserve the exception type and traceback in `workflow.log`.

## Resume / Checkpoint Behaviour

Before starting any work, check whether a previous workflow run was interrupted:

```python
from scripts.workflow_logger import WorkflowLogger

logger = WorkflowLogger(config.workdir, run_dir)
resume_phase = logger.get_resume_phase()
logger.phase_start("2")
```

| `resume_phase` | Action |
|---|---|
| `None` | No prior log: start normally from Phase 2 |
| `"2"` | Phase 1 completed, Phase 2 not started: start Phase 2 |
| `"3"` to `"11"` | Last completed phase was N-1; skip to `resume_phase` after validation |
| `"12"` | Phase 11 replay packaging is complete, or Phase 12 is being re-audited; run Phase 12 |

Logs created before skill version `0.25` used Phase 11 for the audit. The logger
maps that legacy completion back to the new Phase 11 so the replay package is
created before Phase 12.

When resuming, still run all Phase 2 validation steps every time.

## Steps

1. **Validate `run_config.json`**
   ```python
   with workflow_step(logger, "2", "validate_run_config"):
       config = load_run_config(local_run_config)
   ```
   Verify `execution.mode` is `local`, `ssh`, or `wsl2`. For SSH mode, verify `execution.ssh_target` exists. For SSH/WSL2 mode, verify `remote_exec.py -- true` returns 0 and that the target copies of all three Phase 1 contract files exist.

   Verify the frozen task before dependency work:
   ```bash
   python scripts/research_contract.py verify {workdir}/results/run_config.json
   ```
   A changed execution target, host path, MG5 path, CutExperiment path, workdir,
   or implementation script is allowed when verification still passes. A change
   to the scientific objective or deliverable template is contract drift and
   must be reverted to the frozen value, not accepted as a recovery shortcut.

2. **Consume the Phase 1 MG5 validation**
   Phase 1 already verifies the full MG5 stack, including `bin/mg5_aMC` or
   `bin/mg5`, `HEPTools/pythia8/`, `HEPTools/lhapdf6_py3/`, and
   `Delphes/cards/`, before accepting `run_config.json`. Phase 2 does not
   repeat install remediation; it only uses the accepted `madgraph_path` for
   downstream setup and provenance.

3. **Use `cutexperiment_path`**
   Use `config.cutexperiment_path` for downstream runners, event counting, and
   provenance. Phase 2 does not handle CutExperiment installation or repair.

4. **Validate models**
   ```python
   with workflow_step(logger, "2", "validate_models",
                      inputs={"models": config.models}):
   ```
   For each model, check `{config.madgraph_path}/models/{model}` on the target. If absent, check the skill's local `dependency/` directory; if available, copy/sync it into the target MG5 `models/` directory with:
   ```bash
   python scripts/sync_to_target.py --config {local_run_config} {skill_dir}/dependency/{model} {madgraph_path}/models/{model}
   ```
   Then re-check the model path on the selected target. If the model is missing
   or sync fails, inspect the source/target paths and stderr, repair or replace
   the transfer, and search the documented model sources. Terminate only after
   proving that the frozen model cannot be obtained or made loadable.

5. **Validate physics inputs and locked event counts**
   ```python
   with workflow_step(logger, "2", "validate_physics_inputs",
                      inputs={"run_configurations": config.run_configurations,
                              "luminosity": config.luminosity}):
       assert config.event_counts_locked is True
   ```
   Validate positive `run_configurations[*].ebeam1`, `run_configurations[*].ebeam2`,
   luminosity values, matching list lengths, and event counts that exactly match
   the selected `debug` mode in `SKILL.md`: full-size scientific minima for
   `debug=false`, or reduced complete-workflow test values for `debug=true`. For
   ep, `config.energy` may be null.

6. **Create Python virtual environment**
   Create `{config.workdir}/venv/` on the selected target and install required packages directly into that venv:
   ```bash
   python -m venv {workdir}/venv
   {workdir}/venv/bin/pip install numpy scipy scikit-learn joblib matplotlib
   ```
   Optional dependencies (`xgboost`, `lightgbm`, `torch`) are installed on demand in Phase 7.

7. **Validate Delphes card**
   Resolve `config.delphes_card` relative to `{config.madgraph_path}/Delphes/cards/` unless it is already absolute. Validate the resolved card path on the selected target and require `.tcl` or `.dat`.

8. **Working directory guard**
   In local Linux/Unix mode only, if `config.workdir` is inside the skill directory, move it to the skill directory's parent and update `run_config.json`. In SSH/WSL2 mode, skip this local containment guard because target paths are not local paths.

9. **Run directory setup**
   For each `config.run_configurations` entry, create these directories on the selected target:
   ```text
   {workdir}/results/{run_dir}/data
   {workdir}/results/{run_dir}/plots
   {workdir}/results/{run_dir}/algorithms
   {workdir}/results/{run_dir}/mg5_processes
   {workdir}/results/{run_dir}/orders
   ```

10. **Write environment manifest**
    Write this structured provenance file under each run root:
    ```text
    results/data/phase2/environment_manifest.json
    ```
    Include execution mode/target, MG5 path and version probe,
    CutExperiment path and commit/version probe when available, Delphes card
    resolved path, model paths, venv Python path, installed Python package
    versions, locked event-count mode, and every probe command with return code.
    Also include `research_objective_sha256`, `deliverables_template_sha256`,
    and the paths used to verify the complete locked contract set.
    Phase 10 uses this file for toolchain provenance; do not leave tool
    versions only in `workflow.log`.

```python
logger.phase_complete("2")
```

## Critical Rules

- Always use the venv created in Step 6 for Python operations in later phases.
- Never fall back to system Python for workflow analysis scripts.
- All workflow outputs must be written under `{workdir}/results/` on the selected execution target.
- Every MG5 subprocess must be logged with equivalent command, cwd, return-code,
  stdout/stderr, and output provenance. `workflow_step(...)` is the standard
  helper, but a repaired or custom execution path may provide equivalent logs.

## Phase Transition

Before calling `logger.phase_complete("2")`, satisfy
[`deliverables-phase2.md`](deliverables-phase2.md). Missing deliverables require
self-repair, not user interaction.

After `logger.phase_complete("2")` is called and run directories are set up:

1. If validation fails, diagnose and repair the environment or migrate to a
   another Linux target, rerun `research_contract.py verify`, and repeat every
   Phase 2 check. Use `phase_fail` only after creating the failure JSON required
   by `SKILL.md`.
2. If validation passes, proceed immediately to Phase 3 without stopping.
3. Do not summarize results, ask for confirmation, present options, or wait for user input.

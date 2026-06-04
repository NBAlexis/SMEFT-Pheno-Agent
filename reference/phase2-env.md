# Phase 2: Environment Validation

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE: once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose

Verify all dependencies exist before starting the workflow. Phase 2 reads the local control copy of `run_config.json` produced by Phase 1. In SSH/WSL2 mode, the same JSON must also exist at `{workdir}/results/run_config.json` on the selected target. No parameter should be sourced from conversation history or user interaction.

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

Do not hand-write ad-hoc SSH or WSL prefixes in later phases. In SSH and WSL2 modes, do not validate target paths with local `os.path.exists`.

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

logger = WorkflowLogger(config.workdir)
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

logger = WorkflowLogger(config.workdir)
resume_phase = logger.get_resume_phase()
logger.phase_start("2")
```

| `resume_phase` | Action |
|---|---|
| `None` | No prior log: start normally from Phase 2 |
| `"2"` | Phase 1 completed, Phase 2 not started: start Phase 2 |
| `"3"` to `"10"` | Last completed phase was N-1; skip to `resume_phase` after validation |
| `"11"` or later | Workflow already finished; run Phase 11 audit only |

When resuming, still run all Phase 2 validation steps every time.

## Steps

1. **Validate `run_config.json`**
   ```python
   with workflow_step(logger, "2", "validate_run_config"):
       config = load_run_config(local_run_config)
   ```
   Verify `execution.mode` is `local`, `ssh`, or `wsl2`. For SSH mode, verify `execution.ssh_target` exists. For SSH/WSL2 mode, verify `remote_exec.py -- true` returns 0 and that the target copy `{workdir}/results/run_config.json` exists.

2. **Validate MadGraph5**
   ```python
   with workflow_step(logger, "2", "validate_madgraph5",
                      inputs={"mg5path": config.madgraph_path,
                              "mode": config.execution.mode}):
   ```
   - Local mode: verify `{config.madgraph_path}/bin/mg5_aMC` or `{config.madgraph_path}/bin/mg5` exists locally.
   - SSH/WSL2 mode: verify the same path on the target through `remote_exec.py`.
   - If `config.auto_installed_mg5` is true, also verify `HEPTools/pythia8/`, `HEPTools/lhapdf6_py3/`, and `Delphes/cards/` on the selected target.

3. **Validate CutExperiment**
   ```python
   with workflow_step(logger, "2", "validate_cutexperiment",
                      inputs={"cutexperiment_path": config.cutexperiment_path}):
   ```
   If set, verify it exists on the selected target. If missing or user selected `clone`, run `python scripts/install_cutexperiment.py {config.workdir}/CutExperiment` on the selected target, parse `CutExperiment path: ...`, update `run_config.json`, and continue.

4. **Validate models**
   ```python
   with workflow_step(logger, "2", "validate_models",
                      inputs={"models": config.models}):
   ```
   For each model, check `{config.madgraph_path}/models/{model}` on the target. If absent, check the skill's local `dependency/` directory; if available, copy/sync it into the target MG5 `models/` directory with:
   ```bash
   python scripts/sync_to_target.py --config {local_run_config} {skill_dir}/dependency/{model} {madgraph_path}/models/{model}
   ```
   Then re-check the model path on the selected target. If the model is missing in both locations or sync fails, stop with the missing model name and the sync stderr path.

5. **Validate physics inputs and locked event counts**
   ```python
   with workflow_step(logger, "2", "validate_physics_inputs",
                      inputs={"energy": config.energy, "luminosity": config.luminosity}):
       assert config.event_counts_locked is True
   ```
   Validate positive energy/luminosity values, matching list lengths, and exact locked event counts for the selected `debug` value.

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

```python
logger.phase_complete("2")
```

## Critical Rules

- Always use the venv created in Step 6 for Python operations in later phases.
- Never fall back to system Python for workflow analysis scripts.
- All workflow outputs must be written under `{workdir}/results/` on the selected execution target.
- Every MG5 subprocess must be wrapped by `workflow_step(...)` and must check the return code.

## Phase Transition

After `logger.phase_complete("2")` is called and run directories are set up:

1. If any critical validation failed, abort with a concrete red flag.
2. If validation passes, proceed immediately to Phase 3 without stopping.
3. Do not summarize results, ask for confirmation, present options, or wait for user input.

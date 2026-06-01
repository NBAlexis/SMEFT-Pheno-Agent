# Phase 0: Environment Validation

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Verify all dependencies exist before starting the workflow. Phase 0 reads the workflow configuration from **`run_config.json`** (produced by Phase -1). No parameter should be sourced from conversation history or user interaction.

## Prerequisite

Load the configuration:

```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")
```

All steps below reference fields from `config` (e.g., `config.madgraph_path`, `config.models`).

## Resume / Checkpoint Behaviour

Before starting any work, check whether a previous workflow run was interrupted:

```python
from scripts.workflow_logger import WorkflowLogger

logger = WorkflowLogger(config.workdir)
resume_phase = logger.get_resume_phase()
```

| `resume_phase` | Action |
|----------------|--------|
| `None` | No prior log — start normally from Phase 0 |
| `"0"` | Phase -1 completed, Phase 0 not started — start Phase 0 |
| `"1"` to `"8"` | Last completed phase was N‑1 — skip to phase `resume_phase` |
| `"9"` or `"10"` | Workflow already finished — run Phase 9 audit only |

When resuming, **still run Step 1–9** (environment validation must pass every time), but skip phase execution bodies for already-completed phases. Log a `started` + `completed` pair for each skipped phase so the log remains continuous.

```python
logger.phase_start("0")
```

## Steps

1. **Validate `run_config.json`**:
   ```python
   with workflow_step(logger, "0", "validate_run_config"):
       config = load_run_config(os.path.join(config.workdir, "results", "run_config.json"))
       resume_phase = logger.get_resume_phase()
   ```
   Verify the file exists and `load_run_config` returns without error. If missing or invalid, STOP and report: "run_config.json not found or invalid. Phase -1 must complete successfully before Phase 0."
   - Also check `workflow.log` for resume info (see Resume section above).
2. **MadGraph5**:
   ```python
   with workflow_step(logger, "0", "validate_madgraph5",
                      inputs={"mg5path": config.madgraph_path,
                              "auto_installed": config.auto_installed_mg5}):
   ```
   - If `config.auto_installed_mg5` is true (see [`madgraph-installation.md`](madgraph-installation.md)):
     - Verify `bin/mg5_aMC`, `HEPTools/pythia8/`, `HEPTools/lhapdf6_py3/`, and `Delphes/cards/` all exist under `config.madgraph_path`. If any component is missing, report: "MG5 auto-install incomplete — {component} missing. Re-run installer or provide a manual path."
     - The installer script prints an environment report at the end showing current `PATH` / `LD_LIBRARY_PATH` and recommended exports. The script does **not** modify any environment variable. The LLM/skill should inspect the report and the user's `~/.bashrc`, then decide whether to set the exports for the current session and/or append them to `~/.bashrc` (with `# MG5_auto_install` markers).
   - Otherwise: verify `config.madgraph_path` exists and contains `bin/mg5_aMC`
   ```python
       pass  # validation logic inside the block above
   ```
3. **CutExperiment**:
   ```python
   with workflow_step(logger, "0", "validate_cutexperiment",
                      inputs={"cutexperiment_path": config.cutexperiment_path}):
   ```
   - If `config.cutexperiment_path` is set: verify it exists
   - If not set: clone from `https://gitee.com/NBAlexis/CutExperiment.git` into `{config.workdir}/CutExperiment`, update `config.cutexperiment_path` in memory, and write the updated path back to `run_config.json`
   ```python
       pass  # validation / clone logic inside the block above
   ```
4. **Model(s)**:
   ```python
   with workflow_step(logger, "0", "validate_models",
                      inputs={"models": config.models}):
   ```
   `config.models` is a list of model names.
   - For **each** model in the list:
     - Check `{config.madgraph_path}/models/{model}` exists
     - If not, check the skill's `dependency/` directory. If the model exists there, copy it to `{config.madgraph_path}/models/{model}`. If the model is missing in both locations, STOP and report the missing model.
   - If any model fails validation, STOP and report the missing model.
   ```python
       pass  # validation / copy logic inside the block above
   ```
5. **Physics inputs**:
   ```python
   with workflow_step(logger, "0", "validate_physics_inputs",
                      inputs={"energy": config.energy, "luminosity": config.luminosity}):
       for e in config.energy:
           if e <= 0:
               raise ValueError(f"energy must be > 0, got {e}")
       for l in config.luminosity:
           if l <= 0:
               raise ValueError(f"luminosity must be > 0, got {l}")
   ```
6. **Python virtual environment**:
   ```python
   from scripts.workflow_logger import workflow_step
   ```
   Create a local venv under `{config.workdir}/venv/` and install all required packages directly. Do NOT check whether packages exist in the system Python — a fresh venv starts empty.

```python
import os, subprocess, sys

venv_dir = os.path.join(config.workdir, "venv")
python_bin = os.path.join(venv_dir, "bin", "python")
pip_bin = os.path.join(venv_dir, "bin", "pip")

with workflow_step(logger, "0", "setup_venv", inputs={"venv_dir": venv_dir}):
    # Create venv if not exists
    if not os.path.exists(venv_dir):
        subprocess.run([sys.executable, "-m", "venv", venv_dir], check=True)

    # Install required packages (always run — idempotent)
    subprocess.run(
        [pip_bin, "install", "numpy", "scipy", "scikit-learn", "joblib", "matplotlib"],
        check=True
    )
```

Record `python_bin` in memory (e.g., write to a small metadata file or set an environment variable) so Phases 1–9 know which Python interpreter to use for all subsequent Python operations.

> **Optional dependencies** (`xgboost`, `lightgbm`, `torch`) are **NOT** installed in Phase 0. They are installed on-demand in Phase 5 into the same venv when the corresponding algorithm is selected. See [`phase5-ml-training.md`](phase5-ml-training.md) Section 5.2.1.

7. **Delphes card**:
   ```python
   with workflow_step(logger, "0", "validate_delphes_card",
                      inputs={"delphes_card": config.delphes_card}):
       card_path = os.path.join(config.madgraph_path, "Delphes", "cards", config.delphes_card)
       if not os.path.exists(card_path):
           if config.custom_card and os.path.exists(config.custom_card):
               pass  # custom card is valid
           else:
               raise ValueError(f"Delphes card not found: {config.delphes_card}")
   ```

8. **Working Directory guard**:
   ```python
   with workflow_step(logger, "0", "guard_workdir",
                      inputs={"workdir": config.workdir}):
       skill_dir = os.path.dirname(os.path.abspath("SKILL.md"))
       if config.workdir.startswith(skill_dir):
           parent = os.path.dirname(skill_dir)
           config.workdir = parent
           with open(os.path.join(config.workdir, "results", "run_config.json"), "w") as f:
               json.dump(config.__dict__, f, indent=2)
           print(f"Work directory adjusted to {parent} to avoid writing into the skill installation.")
   ```

9. **Run directory setup**:
   All `results/` paths are relative to `config.workdir`. For each entry in `config.run_configurations`, create `{config.workdir}/results/{run_dir}/` with subdirectories `data/`, `plots/`, `algorithms/`, `mg5_processes/`, `orders/`. ALL subsequent phases MUST write to these directories, NEVER to bare `results/`.

```python
import os

run_dirs = []
with workflow_step(logger, "0", "setup_run_directories",
                   inputs={"num_runs": len(config.run_configurations)}):
    for run in config.run_configurations:
        run_dir = os.path.join(config.workdir, "results", run.run_dir)
        run_dirs.append(run.run_dir)
        for sub in ["data", "plots", "algorithms", "mg5_processes", "orders"]:
            os.makedirs(os.path.join(run_dir, sub), exist_ok=True)

logger.phase_complete("0")
```

## Critical Rules

- **ALWAYS use the venv created in Step 6** (`{workdir}/venv/`) for all Python operations in Phases 1–9. Do NOT fall back to system Python.
- Do NOT hardcode paths to external virtual environments (e.g., `../example1/venv`)
- **All file paths MUST be resolved relative to `{workdir}`**. Never assume the current working directory is correct; always use `os.path.join(workdir, "results", ...)` or `os.chdir(workdir)` before file operations.

## MG5 Return Code Checking

Every MG5 subprocess MUST be wrapped by `workflow_step(...)` and MUST check the return code:

```python
with workflow_step(logger, phase, "mg5_launch", inputs={"order": order_path}):
    result = subprocess.run(
        ["./bin/mg5_aMC", order_path],
        cwd=MG5PATH,
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"STDOUT:\n{result.stdout}")
        print(f"STDERR:\n{result.stderr}")
        raise RuntimeError(f"MG5 failed with exit code {result.returncode}")
```

## Phase Transition

After `logger.phase_complete("0")` is called and run directories are set up:

1. **Check validation rules immediately**: If any critical check failed, abort with red flag.
2. **If validation passes**: **proceed immediately to Phase 1 without stopping.**
3. **Do NOT**: summarize results, ask for confirmation, present options, or wait for user input.

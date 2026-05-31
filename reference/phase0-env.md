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

## Steps

1. **Validate `run_config.json`**: Verify the file exists and `load_run_config` returns without error. If missing or invalid, STOP and report: "run_config.json not found or invalid. Phase -1 must complete successfully before Phase 0."
2. **MadGraph5**:
   - If `config.auto_installed_mg5` is true (see [`madgraph-installation.md`](madgraph-installation.md)):
     - Verify `bin/mg5_aMC`, `HEPTools/pythia8/`, `HEPTools/lhapdf6_py3/`, and `Delphes/cards/` all exist under `config.madgraph_path`. If any component is missing, report: "MG5 auto-install incomplete — {component} missing. Re-run installer or provide a manual path."
     - The installer script prints an environment report at the end showing current `PATH` / `LD_LIBRARY_PATH` and recommended exports. The script does **not** modify any environment variable. The LLM/skill should inspect the report and the user's `~/.bashrc`, then decide whether to set the exports for the current session and/or append them to `~/.bashrc` (with `# MG5_auto_install` markers).
   - Otherwise: verify `config.madgraph_path` exists and contains `bin/mg5_aMC`
3. **CutExperiment**:
   - If `config.cutexperiment_path` is set: verify it exists
   - If not set: clone from `https://gitee.com/NBAlexis/CutExperiment.git` into `{config.workdir}/CutExperiment`, update `config.cutexperiment_path` in memory, and write the updated path back to `run_config.json`
4. **Model(s)**: `config.models` is a list of model names.
   - For **each** model in the list:
     - Check `{config.madgraph_path}/models/{model}` exists
     - If not, check the skill's `dependency/` directory. If the model exists there, copy it to `{config.madgraph_path}/models/{model}`. If the model is missing in both locations, STOP and report the missing model.
   - If any model fails validation, STOP and report the missing model.
5. **Physics inputs**: Validate all values in `config.energy` > 0 and all values in `config.luminosity` > 0
6. **Python packages**: Verify `numpy`, `scipy`, `sklearn`, `joblib`, `matplotlib` are importable

```python
import importlib
required = ["numpy", "scipy", "sklearn", "joblib", "matplotlib"]
missing = [p for p in required if importlib.util.find_spec(p) is None]
if missing:
    pip_names = ["scikit-learn" if p == "sklearn" else p for p in missing]
    raise ImportError(f"Missing packages: {missing}. Run: pip install {' '.join(pip_names)}")
```

7. **Delphes card**: Verify `config.delphes_card` exists at `{config.madgraph_path}/Delphes/cards/{config.delphes_card}`. If `config.custom_card` is set, verify it exists at the given absolute path. If neither exists, this is a validation error — `run_config.json` was not properly validated in Phase -1.

8. **Working Directory guard**: Verify `config.workdir` is NOT inside the Skill Directory (where `SKILL.md` is located). If it is, update `config.workdir` to the Skill Directory's parent, write the updated value back to `run_config.json`, and report: "Work directory adjusted to `{parent}` to avoid writing into the skill installation."

9. **Run directory setup**: All `results/` paths are relative to `config.workdir`. For each entry in `config.run_configurations`, create `{config.workdir}/results/{run_dir}/` with subdirectories `data/`, `plots/`, `algorithms/`, `mg5_processes/`, `orders/`. ALL subsequent phases MUST write to these directories, NEVER to bare `results/`.

```python
import os
for run in config.run_configurations:
    run_dir = os.path.join(config.workdir, "results", run.run_dir)
    for sub in ["data", "plots", "algorithms", "mg5_processes", "orders"]:
        os.makedirs(os.path.join(run_dir, sub), exist_ok=True)
```

## Critical Rules

- Do NOT hardcode paths to external virtual environments (e.g., `../example1/venv`)
- Create a local venv if needed, or install packages system-wide
- **All file paths MUST be resolved relative to `{workdir}`**. Never assume the current working directory is correct; always use `os.path.join(workdir, "results", ...)` or `os.chdir(workdir)` before file operations.

## MG5 Return Code Checking

Every MG5 subprocess MUST check the return code:

```python
result = subprocess.run(
    ["./bin/mg5_aMC", "order.txt"],
    cwd=MG5PATH,
    capture_output=True,
    text=True
)
if result.returncode != 0:
    print(f"STDOUT:\n{result.stdout}")
    print(f"STDERR:\n{result.stderr}")
    raise RuntimeError(f"MG5 failed with exit code {result.returncode}")
```

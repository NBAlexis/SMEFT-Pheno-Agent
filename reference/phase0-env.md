# Phase 0: Environment Validation

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Verify all dependencies exist before starting the workflow.

## Steps

1. **Required inputs**: Verify all required inputs are present (`madgraph_path`, `process`, `model`, `energy`, `luminosity`). `cutexperiment_path` is optional. If any required inputs are missing, STOP and ask the user (see [`reference/phase-minus1-input-collection.md`](phase-minus1-input-collection.md)).
2. **MadGraph5**:
   - If `madgraph_path` was **auto-installed** in Phase -1 (see [`madgraph-installation.md`](madgraph-installation.md)):
     - Verify `bin/mg5_aMC`, `HEPTools/pythia8/`, `HEPTools/lhapdf6_py3/`, and `Delphes/cards/` all exist. If any component is missing, report: "MG5 auto-install incomplete — {component} missing. Re-run installer or provide a manual path."
     - The installer script prints an environment report at the end showing current `PATH` / `LD_LIBRARY_PATH` and recommended exports. The script does **not** modify any environment variable. The LLM/skill should inspect the report and the user's `~/.bashrc`, then decide whether to set the exports for the current session and/or append them to `~/.bashrc` (with `# MG5_auto_install` markers).
   - Otherwise: verify `madgraph_path` exists and contains `bin/mg5_aMC`
3. **CutExperiment**:
   - If `cutexperiment_path` is provided: verify it exists
   - If not provided: ask the user if they have CutExperiment installed
   - If user does not have it: clone from `https://gitee.com/NBAlexis/CutExperiment.git` into the working directory and use `./CutExperiment` as the path
4. **Model(s)**: `model` may be a single model name or a list of model names.
   - For **each** model in the list:
     - Check `{madgraph_path}/models/{model}` exists
     - If not, check the skill's `dependency/` directory (same directory as `SKILL.md`). If the model exists there, offer to copy it to `{madgraph_path}/models/` (see [`SKILL.md`](../SKILL.md) Phase -1 Step 4). If the model is missing in both locations, STOP and ask the user.
   - If any model fails validation, STOP and report the missing model.
5. **Physics inputs**: Validate `energy > 0` and `luminosity > 0`
6. **Python packages**: Verify `numpy`, `scipy`, `sklearn`, `joblib`, `matplotlib` are importable

```python
import importlib
required = ["numpy", "scipy", "sklearn", "joblib", "matplotlib"]
missing = [p for p in required if importlib.util.find_spec(p) is None]
if missing:
    pip_names = ["scikit-learn" if p == "sklearn" else p for p in missing]
    raise ImportError(f"Missing packages: {missing}. Run: pip install {' '.join(pip_names)}")
```

7. **Delphes card**: If `delphes_card` was user-specified, verify it exists at `{madgraph_path}/Delphes/cards/{delphes_card}`. If it was auto-selected in Phase -1, verify the file exists. If neither, run the auto-recommendation logic from [`reference/phase-minus1-input-collection.md`](phase-minus1-input-collection.md) and verify the resulting card exists.

8. **Working Directory guard**: Verify `workdir` is NOT inside the Skill Directory (where `SKILL.md` is located). If it is, use the Skill Directory's parent instead and report: "Work directory adjusted to `{parent}` to avoid writing into the skill installation."

9. **Run directory setup**: All `results/` paths are relative to `{workdir}`. For each `(energy, luminosity)` pair, compute `RUN_DIR = f"E{energy}_L{luminosity}"` with dots replaced by underscores. Create `{workdir}/results/{RUN_DIR}/` with subdirectories `data/`, `plots/`, `algorithms/`, `mg5_processes/`, `orders/`. ALL subsequent phases MUST write to this directory, NEVER to bare `results/`. In single-run mode, use `{workdir}/results/` directly.

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

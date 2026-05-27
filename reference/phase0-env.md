# Phase 0: Environment Validation

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Verify all dependencies exist before starting the workflow.

## Steps

1. **Required inputs**: Verify all required inputs are present (`madgraph_path`, `process`, `model`, `energy`, `luminosity`). `cutexperiment_path` is optional. If any required inputs are missing, STOP and ask the user (see `SKILL.md` "Missing Input Handling").
2. **MadGraph5**: Verify `madgraph_path` exists and contains `bin/mg5_aMC`
3. **CutExperiment**:
   - If `cutexperiment_path` is provided: verify it exists
   - If not provided: ask the user if they have CutExperiment installed
   - If user does not have it: clone from `https://gitee.com/NBAlexis/CutExperiment.git` into the working directory and use `./CutExperiment` as the path
4. **Model**: Check `{madgraph_path}/models/{model}` exists
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

7. **Delphes card**: If `delphes_card` was user-specified, verify it exists at `{madgraph_path}/Delphes/cards/{delphes_card}`. If it was auto-selected in Phase -1, verify the file exists. If neither, run the auto-recommendation logic from [`SKILL.md`](../SKILL.md) and verify the resulting card exists.

8. **Run directory setup (multi-run mode)**: For each `(energy, luminosity)` pair, compute `RUN_DIR = f"E{energy}_L{luminosity}"` with dots replaced by underscores. Create `results/{RUN_DIR}/` with subdirectories `data/`, `plots/`, `algorithms/`, `mg5_processes/`, `orders/`. ALL subsequent phases MUST write to this directory, NEVER to bare `results/`.

## Critical Rules

- Do NOT hardcode paths to external virtual environments (e.g., `../example1/venv`)
- Create a local venv if needed, or install packages system-wide

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

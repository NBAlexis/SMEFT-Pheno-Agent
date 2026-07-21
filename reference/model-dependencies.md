# Model Dependencies (UFO Models)

> **Contract priority**: Preserve the frozen research objective and deliverables. Technical failure triggers diagnosis and recovery; stop only on explicit user instruction or documented proof that a frozen item is impossible.

The `dependency/` directory in the skill repository contains SMEFT UFO (Universal FeynRules Output) models that can be automatically copied to the user's MadGraph5 installation when the requested model is not found in `{mg5path}/models/`.

## Directory Structure

```
dependency/
  {model_name}/         # Each subdirectory is a UFO model
    __init__.py
    particles.py
    vertices.py
    couplings.py
    lorentz.py
    parameters.py
    ...
```

## Usage Flow

During **Phase 1** (Input Collection), after the user provides the model name:

1. Check if `{madgraph_path}/models/{model}` exists
2. If **yes**: proceed
3. If **no**:
   - Scan `dependency/` at runtime (do **not** hardcode the list)
   - If `{skill_dir}/dependency/{model}` exists:
     > "[4/9] Model `{model}` was not found in `{madgraph_path}/models/`. The skill has this model in its dependency folder. Copy it to `{mg5path}/models/`? (Type `yes` to copy, or provide an alternative model name:)"
   - If the user answers `yes`: copy the model directory recursively. In SSH/WSL2 mode, use `scripts/sync_to_target.py --config {local_run_config} {skill_dir}/dependency/{model} {madgraph_path}/models/{model}`.
   - If the user provides a different model name: repeat the check
   - If the model is not in `dependency/` either: report missing and ask again

## Important Rules

- **Never hardcode the model list.** The `dependency/` folder may be updated at any time. The LLM must scan the directory at runtime.
- **Copy, do not move.** Always use `scripts/sync_to_target.py`, `cp -r`, or `shutil.copytree` to copy from `dependency/` to `mg5path/models/`. Never modify the source files in `dependency/`.
- **Model name matching.** The subdirectory name in `dependency/` must exactly match the model name the user provides (e.g. `AQGCm_UFO`).

## Runtime Scan

At workflow start, scan the `dependency/` directory to discover available models:

```python
import os
skill_dir = os.path.dirname(os.path.abspath(__file__))
dependency_dir = os.path.join(skill_dir, "dependency")
available_models = [d for d in os.listdir(dependency_dir)
                    if os.path.isdir(os.path.join(dependency_dir, d))]
```

**Never hardcode a model list.** The `dependency/` folder is updated independently of the skill code.

## Adding New Models

To add a new UFO model to the skill:

1. Place the model directory under `dependency/{model_name}/`
2. Ensure the directory name matches the model name expected by MG5 (`import model {model_name}`)
3. No code changes are required — the skill scans `dependency/` at runtime

## Phase 2 Validation

Phase 2 verifies that every model in `config.models` exists under `{config.madgraph_path}/models/`. If a model is missing, Phase 2 attempts to copy it from the skill's `dependency/` directory with `scripts/sync_to_target.py` for SSH/WSL2 targets or local copy for Linux local targets. If copying fails or the model is not in `dependency/`, report: "Model `{model}` not found in MG5 and not available in skill dependencies. Re-run Phase 1 or install manually."

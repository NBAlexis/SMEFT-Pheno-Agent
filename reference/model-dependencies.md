# Model Dependencies (UFO Models)

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

During **Phase -1** (Input Collection), after the user provides the model name:

1. Check if `{madgraph_path}/models/{model}` exists
2. If **yes**: proceed
3. If **no**:
   - Scan `dependency/` at runtime (do **not** hardcode the list)
   - If `{skill_dir}/dependency/{model}` exists:
     > "[4/9] Model `{model}` was not found in `{madgraph_path}/models/`. The skill has this model in its dependency folder. Copy it to `{mg5path}/models/`? (Type `yes` to copy, or provide an alternative model name:)"
   - If the user answers `yes`: copy the model directory recursively
   - If the user provides a different model name: repeat the check
   - If the model is not in `dependency/` either: report missing and ask again

## Important Rules

- **Never hardcode the model list.** The `dependency/` folder may be updated at any time. The LLM must scan the directory at runtime.
- **Copy, do not move.** Always use `cp -r` (or `shutil.copytree`) to copy from `dependency/` to `mg5path/models/`. Never modify the source files in `dependency/`.
- **Model name matching.** The subdirectory name in `dependency/` must exactly match the model name the user provides (e.g. `AQGCm_UFO`).

## Current Contents

> **Note:** This list is for reference only. The skill must scan `dependency/` at runtime rather than relying on this list.

| Model | Description |
|-------|-------------|
| `AQGCm_UFO` | Anomalous Quartic Gauge Couplings (muon-specific) |
| `AQGCs_UFO` | Anomalous Quartic Gauge Couplings (s-channel) |
| `AQGCt_UFO` | Anomalous Quartic Gauge Couplings (t-channel) |
| `gQGC_UFO`  | General Quartic Gauge Couplings |

## Adding New Models

To add a new UFO model to the skill:

1. Place the model directory under `dependency/{model_name}/`
2. Ensure the directory name matches the model name expected by MG5 (`import model {model_name}`)
3. No code changes are required — the skill scans `dependency/` at runtime

## Phase 0 Validation

If `auto_installed_mg5 = true`, Phase 0 also verifies that the model was successfully copied (if applicable). If `{madgraph_path}/models/{model}` is still missing after Phase -1, report: "Model `{model}` not found in MG5 and was not copied from dependencies. Re-run Phase -1 or install manually."

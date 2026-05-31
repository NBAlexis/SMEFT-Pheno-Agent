# Phase 5: Train ML Event Selection Strategy

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Train and compare ML algorithms to distinguish SM from NP events. In multi-model mode, training is performed **once** using the **anchor operator's** SM and NP samples. The trained algorithms are then applied to ALL globally claimed operators in later phases.

## Prerequisite

Load the configuration:
```python
from scripts.load_run_config import load_run_config
config = load_run_config("{workdir}/results/run_config.json")
```

Read `anchor.json` from Phase 1. The anchor operator defines the SM vs NP discrimination task.

## Step 5.1: Convert LHCO to CSV

Use CutExperiment to load `.lhco` files and extract feature vectors:

```python
from Interfaces.LHCOlympics import LoadLHCOlympics
from DataStructure.Particles import ParticleType

def lhco_to_features(lhco_path, process_name=config.process):
    """Extract features dynamically based on the final-state particles in process_name.

    Follows the CutExperiment pipeline (see reference/cutexperiment-reference.md):
    1. Parse process_name to identify expected final-state particles
    2. Select visible particles sorted by energy (descending)
    3. Extract four-momenta; append missing momentum (px, py) if neutrinos present
    """
    from Interfaces.LHCOlympics import LoadLHCOlympics
    from DataStructure.Particles import ParticleType

    events = LoadLHCOlympics(lhco_path)

    # Determine expected particle types from process_name
    # (right-hand side of '>', excluding QED=/QCD=/NP= suffixes)
    # Implementation: see reference/cutexperiment-reference.md Step 1
    visible_types, has_neutrinos = parse_final_state(process_name)  # returns (list[ParticleType], bool)
    n_expected = len(visible_types)

    features = []
    for event in events.events:
        # Collect visible particles of the expected types
        particles = [p for p in event.particles if p.particleType in visible_types]
        particles.sort(key=lambda p: p.momentum.values[0], reverse=True)  # sort by energy
        selected = particles[:n_expected]
        if len(selected) < n_expected:
            continue

        vec = []
        for p in selected:
            vec.extend(p.momentum.values)  # [E, px, py, pz]

        if has_neutrinos:
            vis_px = sum(p.momentum.values[1] for p in event.particles
                         if p.particleType != ParticleType.Missing)
            vis_py = sum(p.momentum.values[2] for p in event.particles
                         if p.particleType != ParticleType.Missing)
            vec.extend([-vis_px, -vis_py])  # missing momentum

        features.append(vec)
    return np.array(features)
```

Save as `.csv`:
```
sm.lhco → sm.csv
np_anchor.lhco → np_anchor.csv
```

**Feature extraction must match the final state.** The `process_name` determines which particles are selected and how many. See [`cutexperiment-reference.md`](cutexperiment-reference.md) for the full pipeline.

## Step 5.2: Algorithm Pool and Selection Strategy

### 5.2.1 Define the Algorithm Pool

Maintain a pool of **at least 10 candidate algorithms**. Example pool (from scikit-learn and compatible libraries):

| # | Algorithm | Type | Extra Dependency |
|---|-----------|------|------------------|
| 1 | GradientBoostingClassifier | Ensemble | — |
| 2 | RandomForestClassifier | Ensemble | — |
| 3 | XGBClassifier | Ensemble | `xgboost` |
| 4 | LGBMClassifier | Ensemble | `lightgbm` |
| 5 | SVC (RBF kernel) | Kernel | — |
| 6 | SVC (poly kernel) | Kernel | — |
| 7 | LogisticRegression | Linear | — |
| 8 | MLPClassifier | Neural Network | — |
| 9 | IsolationForest | Anomaly Detection | — |
| 10 | ExtraTreesClassifier | Ensemble | — |
| 11 | AdaBoostClassifier | Ensemble | — |
| 12 | KNeighborsClassifier | Distance-based | — |
| 13 | PyTorch NN (custom) | Neural Network | `torch` |

If `config.algorithms` is set in `run_config.json`, use those instead of the pool.

**On-demand dependency installation:**
If a selected algorithm requires a package not yet installed (e.g., `xgboost`, `lightgbm`, or `torch`), install it into the **same venv** created in Phase 0:

```python
import os, subprocess

venv_python = os.path.join(config.workdir, "venv", "bin", "python")

# Example: selected algorithm needs xgboost
try:
    from xgboost import XGBClassifier
except ImportError:
    subprocess.check_call([venv_python, "-m", "pip", "install", "xgboost"])
    from xgboost import XGBClassifier
```

### 5.2.2 Random Initial Selection

Use a random seed (e.g., hash of `process_name + anchor_model + anchor_name`) to randomly select **3 algorithms** from the pool.

```python
import random
rng = random.Random(hash(process_name + anchor_model + anchor_name) % (2**32))
selected = rng.sample(algorithm_pool, 3)
```

### 5.2.3 Write `compute_scores` Function

Before training, write a unified score-computation function. This function is used in Phase 5 (ROC/AUC) and Phase 6 (threshold optimization). Save it to `{workdir}/results/algorithms/compute_scores.py`:

```python
import numpy as np

def compute_scores(clf, X):
    """Compute normalized scores in [0, 1] for any fitted model.
    Higher = more NP-like."""
    if hasattr(clf, "predict_proba"):
        return clf.predict_proba(X)[:, 1]
    if hasattr(clf, "decision_function"):
        raw = clf.decision_function(X)
        return 1.0 / (1.0 + np.exp(-raw))
    if hasattr(clf, "score_samples"):
        raw = -clf.score_samples(X)
    else:
        raise ValueError(f"No score method on {type(clf).__name__}")
    min_val, max_val = raw.min(), raw.max()
    if max_val - min_val < 1e-12:
        return np.ones_like(raw) * 0.5
    return (raw - min_val) / (max_val - min_val + 1e-10)
```

### 5.2.4 Train

Train on the **anchor operator's** SM and NP samples:

1. Load `sm.csv` and `np_anchor.csv`
2. Balance: `n = min(len(sm), len(np_data))`
3. Stack: `X = np.vstack([sm[:n], np_data[:n]])`, `y = [0]*n + [1]*n`
4. Train/test split: 80/20
5. Train the selected algorithms
6. **Compute and record AUC for each** using the `compute_scores` function from Step 5.2.3 — **this is for report plotting only, NOT for algorithm selection**
7. Plot ROC curves and save to `results/plots/roc_anchor.pdf`

> **Algorithm selection is deferred to Phase 6.** Phase 5 trains exactly the 3 randomly selected algorithms (or user-specified algorithms). No expansion, no AUC-based filtering. The best algorithm is determined by the narrowest `S_stat = 2` constraint width in Phase 6.

## Step 5.3: Score Distribution Histograms

For **every trained algorithm**, plot training-set score distributions:
- Style: `plt.hist(..., histtype='step')`
- Colors: SM=blue, NP=red
- Bins: 31 equal-width on [0, 1]
- y-axis: log scale if peak counts differ by >10x
- Filename: `score_dist_anchor_{alg}.pdf`

## Step 5.4: Save All Algorithms

Save **every fitted model** (including those from expansion rounds):
```python
for alg_name, clf in fitted_clfs.items():
    model_path = os.path.join(config.workdir, "results", "algorithms", f"anchor_{alg_name}.pkl")
    joblib.dump(clf, model_path)
```

Record all AUCs in `algorithm_comparison.json`:
```json
{
  "anchor": {
    "{alg1}": {"auc": 0.9876, "algorithm_path": "..."},
    "{alg2}": {"auc": 0.9654, "algorithm_path": "..."},
    "{alg3}": {"auc": 0.9432, "algorithm_path": "..."},
    "{alg4}": {"auc": 0.6543, "algorithm_path": "..."}
  },
  "algorithm_pool": ["{alg1}", "{alg2}", "{alg3}", "{alg4}", "..."],
  "tested_count": 6,
  "initial_random_seed": 12345,
  "anchor_operator": "fS0",
  "anchor_model": "AQGCm_UFO"
}
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase5/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase5/
  sm.csv, np_anchor.csv
  algorithm_comparison.json
results/plots/
  roc_anchor.pdf
  score_dist_anchor_{alg1}.pdf, score_dist_anchor_{alg2}.pdf, ...
results/algorithms/
  anchor_{alg1}.pkl, anchor_{alg2}.pkl, anchor_{alg3}.pkl, ...
```

## Validation

- `0.5 < AUC <= 1.0` for anchor training

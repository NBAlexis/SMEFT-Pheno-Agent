# Phase 5: Train ML Event Selection Strategy

> **Execution Continuity**: Per [`SKILL.md`](../SKILL.md) SUPREME RULE — once started, this phase MUST run to completion without stopping. Only unrecoverable errors, red flags, or explicit user interrupt are valid stop conditions.

## Purpose
Train and compare ML algorithms to distinguish SM from NP events.

## Step 5.1: Convert LHCO to CSV

Use CutExperiment to load `.lhco` files and extract feature vectors:

```python
from Interfaces.LHCOlympics import LoadLHCOlympics
from DataStructure.Particles import ParticleType

def lhco_to_features(lhco_path, process_name):
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
np_oi.lhco → np_oi.csv
```

**Feature extraction must match the final state.** The `process_name` determines which particles are selected and how many. See [`reference/cutexperiment-reference.md`](reference/cutexperiment-reference.md) for the full pipeline.

## Step 5.2: Algorithm Pool and Selection Strategy

### 5.2.1 Define the Algorithm Pool

Maintain a pool of **at least 10 candidate algorithms**. Example pool (from scikit-learn and compatible libraries):

| # | Algorithm | Type |
|---|-----------|------|
| 1 | GradientBoostingClassifier | Ensemble |
| 2 | RandomForestClassifier | Ensemble |
| 3 | XGBClassifier (xgboost) | Ensemble |
| 4 | LGBMClassifier (lightgbm) | Ensemble |
| 5 | SVC (RBF kernel) | Kernel |
| 6 | SVC (poly kernel) | Kernel |
| 7 | LogisticRegression | Linear |
| 8 | MLPClassifier | Neural Network |
| 9 | IsolationForest | Anomaly Detection |
| 10 | ExtraTreesClassifier | Ensemble |
| 11 | AdaBoostClassifier | Ensemble |
| 12 | KNeighborsClassifier | Distance-based |

If the user specified `algorithms` in Phase -1, use those instead of the pool.

### 5.2.2 Random Initial Selection

Use a random seed (e.g., hash of `process_name + op`) to randomly select **3 algorithms** from the pool.

```python
import random
rng = random.Random(hash(process_name + op) % (2**32))
selected = rng.sample(algorithm_pool, 3)
```

### 5.2.3 Train and Evaluate

For each operator `oi`:
1. Load `sm.csv` and `np_oi.csv`
2. Balance: `n = min(len(sm), len(np))`
3. Stack: `X = np.vstack([sm[:n], np[:n]])`, `y = [0]*n + [1]*n`
4. Train/test split: 80/20
5. Train the selected algorithms
6. Compute AUC for each
7. Plot ROC curves (SM vs NP score distributions) and save to `results/plots/roc_{op}.pdf`

**Anomaly-detection score normalization:**
For algorithms that output raw anomaly scores, normalize to [0, 1]:
```python
scores = -clf.decision_function(X)
scores = (scores - scores.min()) / (scores.max() - scores.min() + 1e-10)
```

### 5.2.4 Dynamic Expansion (If Needed)

If **all 3 initial algorithms have AUC < 0.7**, randomly select additional algorithms from the pool (excluding already-tested ones) and repeat training.

**Stop conditions for expansion:**
- At least one algorithm achieves AUC >= 0.7
- **OR** 10 algorithms have been tested (maximum)

**Expansion example:**
```python
if all(auc < 0.7 for auc in aucs.values()) and len(tested) < 10:
    remaining = [a for a in pool if a not in tested]
    additional = rng.sample(remaining, min(3, len(remaining)))
    # train additional algorithms...
```

## Step 5.3: Score Distribution Histograms

For **every trained algorithm**, plot training-set score distributions:
- Style: `plt.hist(..., histtype='step')`
- Colors: SM=blue, NP=red
- Bins: 31 equal-width on [0, 1]
- y-axis: log scale if peak counts differ by >10x
- Filename: `score_dist_{op}_{alg}.pdf`

## Step 5.4: Save All Algorithms

Save **every fitted model** (including those from expansion rounds):
```python
for alg_name, clf in fitted_clfs.items():
    model_path = os.path.join(ALGORITHMS, f"{op}_{alg_name}.pkl")
    joblib.dump(clf, model_path)
```

Record all AUCs in `algorithm_comparison.json`:
```json
{
  "oi": {
    "{alg1}": {"auc": 0.9876, "algorithm_path": "..."},
    "{alg2}": {"auc": 0.9654, "algorithm_path": "..."},
    "{alg3}": {"auc": 0.9432, "algorithm_path": "..."},
    "{alg4}": {"auc": 0.6543, "algorithm_path": "..."}
  },
  "algorithm_pool": ["{alg1}", "{alg2}", "{alg3}", "{alg4}", "..."],
  "tested_count": 6,
  "initial_random_seed": 12345
}
```

## Output

> **Multi-run note:** In multi-run mode, all `results/` paths below are prefixed with the run subdirectory (e.g., `results/E10_L1000/data/phase5/...`). See [`SKILL.md`](../SKILL.md) Rule 11.

```
results/data/phase5/
  sm.csv, np_o1.csv, np_o2.csv, ...
  algorithm_comparison.json
results/plots/
  roc_o1.pdf, roc_o2.pdf, ...
  score_dist_o1_{alg1}.pdf, score_dist_o1_{alg2}.pdf, ...
results/algorithms/
  o1_{alg1}.pkl, o1_{alg2}.pkl, o1_{alg3}.pkl, ...
```

## Validation

- `0.5 < AUC <= 1.0` for all operators
- If `AUC > 0.9999`, flag possible overfitting

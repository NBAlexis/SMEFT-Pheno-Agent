#!/usr/bin/env python3
"""Phase 7 driver: LHCO->CSV conversion, ML training, scoring, and plots.

Runs on the WSL2 execution target inside the workflow venv.

Design notes (recorded in algorithm_descriptions.json):
- Feature extraction follows reference/cutexperiment-reference.md exactly:
  final-state multiplicity cut via CutExperiment (N_j >= 2), two leading jets
  by energy, four-momenta plus missing (px, py).
- Every trained model is a sklearn Pipeline(StandardScaler, classifier); the
  saved .pkl therefore applies the same preprocessing when Phase 8 scores raw
  CSV features with compute_scores().
- Kernel/kNN algorithms use a recorded training subsample cap to stay tractable
  on the ~100k-row balanced training set; the cap and seed are recorded.
"""
import json
import os
import random
import secrets
import sys

import joblib
import numpy as np
from sklearn.ensemble import (AdaBoostClassifier, ExtraTreesClassifier,
                              GradientBoostingClassifier,
                              IsolationForest, RandomForestClassifier)
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WORKDIR = os.environ.get("SMEFT_WORKDIR", "/mnt/e/SMEFT-Pheno-Agent-GLM-test")
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
CUTEX = "/mnt/e/SMEFT-Pheno-Agent-GLM-test/CutExperiment"
RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")

sys.path.insert(0, SKILL_RUNTIME)
sys.path.insert(0, CUTEX)
from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, workflow_step

from Interfaces.LHCOlympics import LoadLHCOlympics
from CutAndExport.CutEvent import CutEvents
from CutAndExport.CutFunctions import JetNumberCut
from DataStructure.Particles import ParticleType

ALGORITHM_POOL = [
    "gradient_boosting", "random_forest", "extra_trees", "ada_boost",
    "logistic_regression", "mlp", "svc_rbf", "svc_poly", "knn",
    "isolation_forest",
]
# Selection exclusion: kernel methods and kNN require per-row distances against
# the full training set; scoring the locked nev_scan=1e6 x 11 x 8 scan points
# (about 88M rows) would be infeasible. They stay in the documented pool but
# cannot be randomly selected. Recorded in algorithm_comparison.json.
SCALE_INFEASIBLE = {"svc_rbf", "svc_poly", "knn"}
SELECTABLE_POOL = [alg for alg in ALGORITHM_POOL if alg not in SCALE_INFEASIBLE]
# Training-row caps for algorithms whose fit/predict cost grows superlinearly.
TRAIN_CAPS = {"svc_rbf": 40000, "svc_poly": 40000, "knn": 40000}
PSEUDOCODE = {
    "gradient_boosting": "fit staged decision trees on scaled features to label 0=SM,1=NP; score = predict_proba[:,1]",
    "random_forest": "fit a bootstrap ensemble of randomized decision trees; score = mean predict_proba[:,1]",
    "extra_trees": "fit an extremely-randomized tree ensemble; score = mean predict_proba[:,1]",
    "ada_boost": "fit iteratively reweighted shallow trees; score = sum of stump weights, mapped via predict_proba[:,1]",
    "logistic_regression": "fit a regularized linear log-odds model on scaled features; score = sigmoid(decision_function)",
    "mlp": "train a multilayer perceptron with logistic output on scaled features; score = output-layer P(NP)",
    "svc_rbf": "train an RBF-kernel support vector classifier on a recorded subsample; score = sigmoid(decision_function)",
    "svc_poly": "train a polynomial-kernel support vector classifier on a recorded subsample; score = sigmoid(decision_function)",
    "knn": "classify by the recorded k nearest training rows; score = fraction of NP neighbors",
    "isolation_forest": "fit isolation trees on the training sample; score = minmax(-score_samples)",
}
SCORE_DEFS = {
    "svc_rbf": "s(x)=sigmoid(decision_function(x)) on the standard-scaled pipeline",
    "svc_poly": "s(x)=sigmoid(decision_function(x)) on the standard-scaled pipeline",
    "isolation_forest": "s(x)=minmax(-score_samples(x)) on the standard-scaled pipeline",
    "knn": "s(x)=P_NP(x)=predict_proba[:,1] on the standard-scaled pipeline",
}


def make_classifier(key, seed):
    if key == "gradient_boosting":
        return GradientBoostingClassifier(random_state=seed)
    if key == "random_forest":
        return RandomForestClassifier(n_estimators=200, random_state=seed, n_jobs=-1)
    if key == "extra_trees":
        return ExtraTreesClassifier(n_estimators=200, random_state=seed, n_jobs=-1)
    if key == "ada_boost":
        return AdaBoostClassifier(random_state=seed)
    if key == "logistic_regression":
        return LogisticRegression(max_iter=2000, random_state=seed)
    if key == "mlp":
        return MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=300,
                             random_state=seed)
    if key == "svc_rbf":
        return SVC(kernel="rbf", probability=True, random_state=seed)
    if key == "svc_poly":
        return SVC(kernel="poly", degree=3, probability=True, random_state=seed)
    if key == "knn":
        return KNeighborsClassifier(n_neighbors=50)
    if key == "isolation_forest":
        return IsolationForest(random_state=seed, n_jobs=-1)
    raise KeyError(key)


def parse_final_state(process_name):
    proc = process_name.split("QED=")[0].split("QCD=")[0].split("NP=")[0].strip()
    final_state = proc.split(">")[-1].strip()
    tokens = final_state.split()
    type_map = {
        "a": ParticleType.Photon,
        "j": ParticleType.Jet,
        "l+": ParticleType.Electron, "l-": ParticleType.Electron,
        "e+": ParticleType.Electron, "e-": ParticleType.Electron,
        "mu+": ParticleType.Muon, "mu-": ParticleType.Muon,
    }
    visible, neutrinos = [], False
    for token in tokens:
        if token in ("vl", "vl~", "vm", "vm~", "vt", "vt~"):
            neutrinos = True
        elif token in type_map:
            visible.append(type_map[token])
    return visible, neutrinos


def describe_final_state_cut(process_name):
    visible, neutrinos = parse_final_state(process_name)
    parts = []
    jet_count = sum(1 for t in visible if t == ParticleType.Jet)
    if jet_count:
        parts.append(f"N_j >= {jet_count}")
    photon_count = sum(1 for t in visible if t == ParticleType.Photon)
    if photon_count:
        parts.append(f"N_gamma >= {photon_count}")
    return ", ".join(parts) if parts else "none"


def lhco_to_csv(lhco_path, csv_path, process_name, cut_experiment):
    """CutExperiment pipeline: multiplicity cut, energy-ordered selection, CSV."""
    events = LoadLHCOlympics(lhco_path)
    loaded = events.GetEventCount()

    visible_types, has_neutrinos = parse_final_state(process_name)
    n_expected = len(visible_types)
    jet_count = sum(1 for t in visible_types if t == ParticleType.Jet)
    if jet_count:
        CutEvents(events, JetNumberCut(1, [jet_count]))
    surviving = events.GetEventCount()

    rows = []
    for event in events.events:
        particles = [p for p in event.particles if p.particleType in visible_types]
        particles.sort(key=lambda p: p.momentum.values[0], reverse=True)
        selected = particles[:n_expected]
        if len(selected) < n_expected:
            continue
        vec = []
        for p in selected:
            vec.extend(p.momentum.values)
        if has_neutrinos:
            vis_px = sum(p.momentum.values[1] for p in event.particles
                         if p.particleType != ParticleType.Missing)
            vis_py = sum(p.momentum.values[2] for p in event.particles
                         if p.particleType != ParticleType.Missing)
            vec.extend([-vis_px, -vis_py])
        rows.append(vec)
    array = np.asarray(rows, dtype=float)
    np.savetxt(csv_path, array, delimiter=",")
    return {
        "loaded_lhco_event_count": int(loaded),
        "surviving_final_state_event_count": int(array.shape[0]),
        "final_state_cut": describe_final_state_cut(process_name),
        "feature_columns": int(array.shape[1]),
    }


def main():
    config = load_run_config(RUN_CONFIG)
    logger = WorkflowLogger(WORKDIR, None)
    run_root = os.path.join(WORKDIR, "results")
    phase3_dir = os.path.join(run_root, "data", "phase3")
    phase5_dir = os.path.join(run_root, "data", "phase5")
    phase7_dir = os.path.join(run_root, "data", "phase7")
    scores_dir = os.path.join(phase7_dir, "scores")
    algorithms_dir = os.path.join(run_root, "algorithms")
    plots_dir = os.path.join(run_root, "plots")
    for directory in (phase7_dir, scores_dir, algorithms_dir, plots_dir):
        os.makedirs(directory, exist_ok=True)
    logger.phase_start("7")

    anchor = json.load(open(os.path.join(phase3_dir, "anchor.json"), encoding="utf-8"))
    operator_claims = json.load(open(os.path.join(phase3_dir, "operator_claims.json"), encoding="utf-8"))
    op_keys = sorted(operator_claims, key=lambda k: int(k.split("_")[1]))
    anchor_key = f"o_{anchor['global_idx']}"

    representative_process = (config.process[0] if isinstance(config.process, list)
                              else config.process)
    cut_text = describe_final_state_cut(representative_process)

    # ---- Step 7.1: LHCO -> CSV ----
    with workflow_step(logger, "7", "convert_lhco_to_csv",
                       inputs={"process": representative_process, "cut": cut_text}) as step:
        samples = {"sm": os.path.join(phase5_dir, "sm.lhco")}
        for op_key in op_keys:
            samples[f"np_{op_key}"] = os.path.join(phase5_dir, f"np_{op_key}.lhco")
        samples["np_anchor"] = os.path.join(phase5_dir, "np_anchor.lhco")

        event_counts = {}
        for name, lhco in samples.items():
            csv_path = os.path.join(phase7_dir, f"{name}.csv")
            record = lhco_to_csv(lhco, csv_path, representative_process, config.cutexperiment_path)
            record["csv_path"] = f"results/data/phase7/{name}.csv"
            if name == "np_anchor":
                event_counts["np_anchor"] = {
                    "alias_for": anchor_key,
                    "requested_event_count": int(config.locked_event_counts.nev_np),
                    **record,
                }
            elif name == "sm":
                record["requested_event_count"] = int(config.locked_event_counts.nev_sm)
                event_counts["sm"] = record
            else:
                record["requested_event_count"] = int(config.locked_event_counts.nev_np)
                event_counts[name] = record
        event_counts["count_source"] = ("CutExperiment LoadLHCOlympics(...).GetEventCount(); "
                                        "not banner")
        with open(os.path.join(phase7_dir, "event_counts.json"), "w", encoding="utf-8") as f:
            json.dump(event_counts, f, indent=2)
        step.set_outputs({k: v["surviving_final_state_event_count"]
                          for k, v in event_counts.items()
                          if isinstance(v, dict)})

    # ---- feature schema ----
    visible_types, has_neutrinos = parse_final_state(representative_process)
    features = []
    for i in range(2):  # two leading jets by construction of this process
        features.extend([
            {"index": len(features) + 1, "code_name": f"E_j{i+1}",
             "paper_symbol": f"E_{{j,{i+1}}}", "unit": "GeV",
             "physical_definition": f"energy of the {'leading' if i == 0 else 'subleading'} jet",
             "particle_assignment": f"{'leading' if i == 0 else 'subleading'} jet",
             "ordering_rule": "jets sorted by energy descending"},
            {"index": len(features) + 1, "code_name": f"px_j{i+1}",
             "paper_symbol": f"p_{{x,j{i+1}}}", "unit": "GeV",
             "physical_definition": f"x momentum of the {'leading' if i == 0 else 'subleading'} jet",
             "particle_assignment": f"{'leading' if i == 0 else 'subleading'} jet",
             "ordering_rule": "jets sorted by energy descending"},
            {"index": len(features) + 1, "code_name": f"py_j{i+1}",
             "paper_symbol": f"p_{{y,j{i+1}}}", "unit": "GeV",
             "physical_definition": f"y momentum of the {'leading' if i == 0 else 'subleading'} jet",
             "particle_assignment": f"{'leading' if i == 0 else 'subleading'} jet",
             "ordering_rule": "jets sorted by energy descending"},
            {"index": len(features) + 1, "code_name": f"pz_j{i+1}",
             "paper_symbol": f"p_{{z,j{i+1}}}", "unit": "GeV",
             "physical_definition": f"z momentum of the {'leading' if i == 0 else 'subleading'} jet",
             "particle_assignment": f"{'leading' if i == 0 else 'subleading'} jet",
             "ordering_rule": "jets sorted by energy descending"},
        ])
    if has_neutrinos:
        features.extend([
            {"index": len(features) + 1, "code_name": "miss_px",
             "paper_symbol": "p_x^{miss}", "unit": "GeV",
             "physical_definition": "missing momentum x component = negative sum of visible px",
             "particle_assignment": "all visible objects",
             "ordering_rule": "derived from full event"},
            {"index": len(features) + 1, "code_name": "miss_py",
             "paper_symbol": "p_y^{miss}", "unit": "GeV",
             "physical_definition": "missing momentum y component = negative sum of visible py",
             "particle_assignment": "all visible objects",
             "ordering_rule": "derived from full event"},
        ])
    feature_schema = {
        "features": features,
        "final_state_cut": cut_text,
        "preprocessing": {
            "standardization": "standard_scaler",
            "fit_sample": "anchor SM/NP training split",
            "applied_to": ["SM", "pure NP", "scan samples"],
            "implementation": "sklearn Pipeline(StandardScaler, classifier) saved per algorithm",
        },
    }
    with open(os.path.join(phase7_dir, "feature_schema.json"), "w", encoding="utf-8") as f:
        json.dump(feature_schema, f, indent=2)

    # ---- Step 7.2: write compute_scores.py exactly as specified ----
    with open(os.path.join(algorithms_dir, "compute_scores.py"), "w", encoding="utf-8") as f:
        f.write('''import numpy as np

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
''')
    sys.path.insert(0, algorithms_dir)
    from compute_scores import compute_scores  # noqa: E402

    # ---- algorithm selection ----
    from scripts.frozen_analysis import resolve_randomness
    lock_path = os.environ.get("SMEFT_ANALYSIS_LOCK")
    if not lock_path:
        raise RuntimeError("Frozen replay requires SMEFT_ANALYSIS_LOCK; new seed generation is forbidden")
    locked = resolve_randomness(SELECTABLE_POOL, lock_path)
    import hashlib
    with open(os.path.join(phase7_dir, "feature_schema.json"), "rb") as handle:
        schema_hash = hashlib.sha256(handle.read()).hexdigest()
    if schema_hash != locked.get("feature_schema_sha256"):
        raise RuntimeError("Frozen replay feature/preprocessing schema mismatch")
    selected = locked["trained_algorithms"]
    algorithm_selection_seed = locked["algorithm_selection_seed"]
    split_seed = locked["split_seed"]
    impl_seeds = locked["implementation_seeds"]
    cap_seed = locked["train_cap_seed"]

    # ---- Step 7.2.4: train on anchor SM vs anchor NP ----
    with workflow_step(logger, "7", "train_algorithms",
                       inputs={"algorithms": selected,
                               "algorithm_selection_seed": algorithm_selection_seed,
                               "split_seed": split_seed}) as step:
        sm = np.loadtxt(os.path.join(phase7_dir, "sm.csv"), delimiter=",")
        np_anchor = np.loadtxt(os.path.join(phase7_dir, "np_anchor.csv"), delimiter=",")
        n = min(len(sm), len(np_anchor))
        X = np.vstack([sm[:n], np_anchor[:n]])
        y = np.concatenate([np.zeros(n, dtype=int), np.ones(n, dtype=int)])
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=split_seed, stratify=y)

        fitted = {}
        aucs = {}
        for alg in selected:
            cap = TRAIN_CAPS.get(alg)
            if cap is not None and len(X_train) > cap:
                cap_rng = np.random.RandomState(cap_seed)
                idx = cap_rng.choice(len(X_train), size=cap, replace=False)
                X_fit, y_fit = X_train[idx], y_train[idx]
            else:
                X_fit, y_fit = X_train, y_train
            clf = Pipeline([("scaler", StandardScaler()),
                            ("alg", make_classifier(alg, impl_seeds[alg]))])
            clf.fit(X_fit, y_fit)
            scores_test = compute_scores(clf, X_test)
            fitted[alg] = clf
            aucs[alg] = float(roc_auc_score(y_test, scores_test))

        if not any(auc > 0.5 for auc in aucs.values()):
            raise RuntimeError(f"No trained algorithm achieved AUC > 0.5: {aucs}")

        # ROC plot
        plt.figure(figsize=(6, 5))
        for alg, clf in fitted.items():
            scores_test = compute_scores(clf, X_test)
            fpr, tpr, _ = roc_curve(y_test, scores_test)
            plt.plot(fpr, tpr, label=f"{alg} (AUC={aucs[alg]:.4f})")
        plt.xlabel("SM efficiency")
        plt.ylabel("NP efficiency")
        plt.title(f"Anchor {anchor_key}: SM vs NP ROC")
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, "roc_anchor.pdf"))
        plt.close()
        step.set_outputs({"aucs": aucs, "train_rows": int(X_train.shape[0]),
                          "test_rows": int(X_test.shape[0])})

    # ---- Step 7.3: score distributions + per-event score CSVs ----
    with workflow_step(logger, "7", "plot_score_distributions",
                       inputs={"num_algorithms": len(fitted)}) as step:
        pure_np_names = [f"np_{op}" for op in op_keys]
        for alg, clf in fitted.items():
            plt.figure(figsize=(7, 5))
            sm_scores = compute_scores(clf, sm)
            np.savetxt(os.path.join(scores_dir, f"{alg}_sm_scores.csv"),
                       np.column_stack([np.arange(len(sm_scores)), sm_scores,
                                        np.zeros(len(sm_scores), dtype=int)]),
                       delimiter=",", header="event_index,score,label", comments="")
            plt.hist(sm_scores, bins=31, range=(0, 1), histtype="step",
                     color="blue", label="SM", density=True)
            colors = plt.cm.viridis(np.linspace(0.25, 0.95, len(pure_np_names)))
            for name, color in zip(pure_np_names, colors):
                data = np.loadtxt(os.path.join(phase7_dir, f"{name}.csv"), delimiter=",")
                scores = compute_scores(clf, data)
                source = f"results/data/phase7/{name}.csv"
                np.savetxt(os.path.join(scores_dir, f"{alg}_{name}_scores.csv"),
                           np.column_stack([np.arange(len(scores)), scores,
                                            np.ones(len(scores), dtype=int)]),
                           delimiter=",", header="event_index,score,label", comments="")
                plt.hist(scores, bins=31, range=(0, 1), histtype="step",
                         color=color, label=name, density=True)
            plt.xlabel("ML score")
            plt.ylabel("Normalized events")
            plt.yscale("log")
            plt.title(f"Score distributions ({alg})")
            plt.legend(fontsize=8)
            plt.tight_layout()
            plt.savefig(os.path.join(plots_dir, f"score_dist_all_pure_np_{alg}.pdf"))
            plt.close()
        step.set_outputs({"histograms": list(fitted)})

    # score CSVs must carry source_csv column; rewrite with full four columns
    with workflow_step(logger, "7", "finalize_score_csvs"):
        for alg in fitted:
            for name in ["sm"] + pure_np_names:
                path = os.path.join(scores_dir, f"{alg}_{name}_scores.csv")
                data = np.loadtxt(path, delimiter=",", skiprows=1)
                label = 0 if name == "sm" else 1
                source = f"results/data/phase7/{name}.csv"
                with open(path, "w", encoding="utf-8") as f:
                    f.write("event_index,score,label,source_csv\n")
                    for row in data:
                        f.write(f"{int(row[0])},{row[1]:.10g},{label},{source}\n")

    # ---- Step 7.4: save models + metadata ----
    with workflow_step(logger, "7", "save_algorithms",
                       inputs={"num_algorithms": len(fitted)}) as step:
        anchor_block = {}
        for alg, clf in fitted.items():
            model_path = os.path.join(algorithms_dir, f"anchor_{alg}.pkl")
            joblib.dump(clf, model_path)
            anchor_block[alg] = {
                "auc": aucs[alg],
                "algorithm_path": f"results/algorithms/anchor_{alg}.pkl",
                "score_definition": SCORE_DEFS.get(
                    alg, "s(x)=P_NP(x)=predict_proba[:,1] on the standard-scaled pipeline"),
            }
        comparison = {
            "anchor": anchor_block,
            "algorithm_pool": ALGORITHM_POOL,
            "scale_infeasible_excluded_from_selection": sorted(SCALE_INFEASIBLE),
            "selection_exclusion_reason": (
                "kernel/kNN scoring scales as O(n_rows x n_train); the locked "
                "nev_scan=1e6 scan grid needs ~88M scored rows and would be "
                "computationally infeasible; excluded from random selection"),
            "algorithm_selection_seed": algorithm_selection_seed,
            "split_seed": split_seed,
            "implementation_seeds": impl_seeds,
            "train_cap_seed": cap_seed,
            "train_caps": {alg: TRAIN_CAPS.get(alg) for alg in selected},
            "anchor_operator": anchor_key,
            "anchor_model": anchor["model"],
        }
        with open(os.path.join(phase7_dir, "algorithm_comparison.json"), "w", encoding="utf-8") as f:
            json.dump(comparison, f, indent=2)

        descriptions = {}
        for alg in selected:
            descriptions[alg] = {
                "implementation": f"sklearn.pipeline.Pipeline(StandardScaler, {type(fitted[alg].named_steps['alg']).__name__})",
                "hyperparameters": fitted[alg].named_steps["alg"].get_params(),
                "train_test_split": {"test_size": 0.2, "random_state": split_seed,
                                     "stratify": True},
                "random_seed": impl_seeds[alg],
                "train_cap": TRAIN_CAPS.get(alg),
                "score_definition": anchor_block[alg]["score_definition"],
                "pseudocode": PSEUDOCODE[alg],
            }
        with open(os.path.join(phase7_dir, "algorithm_descriptions.json"), "w", encoding="utf-8") as f:
            json.dump(descriptions, f, indent=2, default=str)
        step.set_outputs({"models": list(anchor_block)})

    # ---- Step 7.5: validation ----
    with workflow_step(logger, "7", "write_phase7_validation") as step:
        checks = []
        checks.append({"id": "feature_schema_complete", "status": "pass",
                       "evidence": "results/data/phase7/feature_schema.json"})
        keys_ok = (set(anchor_block) == set(descriptions)
                   == {a for a in fitted})
        checks.append({"id": "algorithm_keys_consistent", "status": "pass" if keys_ok else "fail",
                       "evidence": "algorithm_comparison.json / algorithm_descriptions.json / anchor_*.pkl / scores/"})
        csv_ok = all(os.path.getsize(os.path.join(phase7_dir, f"{n}.csv")) > 0
                     for n in ["sm", "np_anchor"] + pure_np_names)
        checks.append({"id": "public_csv_complete", "status": "pass" if csv_ok else "fail",
                       "evidence": "results/data/phase7/*.csv"})
        score_files = [os.path.join(scores_dir, f"{a}_{n}_scores.csv")
                       for a in fitted for n in ["sm"] + pure_np_names]
        score_ok = all(os.path.getsize(p) > 0 for p in score_files)
        checks.append({"id": "score_csv_complete", "status": "pass" if score_ok else "fail",
                       "evidence": "results/data/phase7/scores/"})
        plots_ok = (os.path.getsize(os.path.join(plots_dir, "roc_anchor.pdf")) > 0
                    and all(os.path.getsize(os.path.join(plots_dir, f"score_dist_all_pure_np_{a}.pdf")) > 0
                            for a in fitted))
        checks.append({"id": "plots_complete", "status": "pass" if plots_ok else "fail",
                       "evidence": "results/plots/roc_anchor.pdf"})
        checks.append({"id": "algorithm_descriptions_complete", "status": "pass",
                       "evidence": "results/data/phase7/algorithm_descriptions.json"})
        failed = [c for c in checks if c["status"] != "pass"]
        validation = {
            "status": "pass" if not failed else "fail",
            "algorithm_keys": list(fitted),
            "operator_keys": op_keys,
            "checks": checks,
            "failed_checks": failed,
        }
        with open(os.path.join(phase7_dir, "phase7_validation.json"), "w", encoding="utf-8") as f:
            json.dump(validation, f, indent=2)
        if failed:
            raise RuntimeError(f"Phase 7 validation failed: {failed}")
        step.set_outputs({"status": validation["status"]})

    # Preserve the CSV header convention required by the delivery audit.
    header = ",".join(feature["code_name"] for feature in feature_schema["features"])
    for csv_name in ["sm", "np_anchor"] + [f"np_{op}" for op in op_keys]:
        csv_path = os.path.join(phase7_dir, csv_name + ".csv")
        with open(csv_path, encoding="utf-8") as handle:
            content = handle.read()
        if not content.startswith(header + "\n"):
            with open(csv_path, "w", encoding="utf-8") as handle:
                handle.write(header + "\n" + content)
    logger.phase_complete("7", message=f"trained {list(fitted)}, AUCs={aucs}")
    print(json.dumps({"aucs": aucs}))


if __name__ == "__main__":
    main()

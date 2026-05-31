#!/usr/bin/env python3
"""
Compute normalized ML scores for a set of events.

Handles both classifiers (predict_proba / decision_function) and
anomaly detectors (raw anomaly scores requiring normalization).

Usage:
    from scripts.compute_ml_scores import compute_scores
    scores = compute_scores(clf, X)

CLI:
    python scripts/compute_ml_scores.py model.pkl features.npy scores.npy
"""
import argparse
import numpy as np
import joblib


def compute_scores(clf, X):
    """Compute normalized scores in [0, 1] for any fitted model.

    Args:
        clf: fitted sklearn-compatible estimator
        X: feature array (n_samples, n_features)

    Returns:
        scores: array of shape (n_samples,) in range [0, 1]
                Higher = more NP-like
    """
    # Try predict_proba first (classifiers)
    if hasattr(clf, "predict_proba"):
        proba = clf.predict_proba(X)
        # proba shape: (n_samples, n_classes)
        # Class 1 = NP, so return P(NP)
        return proba[:, 1]

    # Try decision_function (SVM, etc.)
    if hasattr(clf, "decision_function"):
        raw = clf.decision_function(X)
        # Map (-inf, +inf) -> [0, 1] via sigmoid
        return 1.0 / (1.0 + np.exp(-raw))

    # Anomaly detectors: raw anomaly scores
    if hasattr(clf, "score_samples"):
        raw = clf.score_samples(X)  # higher = more "normal" (SM-like)
        # Flip so higher = more anomalous (NP-like)
        raw = -raw
    elif hasattr(clf, "decision_function"):
        raw = -clf.decision_function(X)
    else:
        raise ValueError(
            f"Model {type(clf).__name__} has no recognized score method "
            "(predict_proba, decision_function, score_samples)"
        )

    # Normalize to [0, 1]
    min_val = raw.min()
    max_val = raw.max()
    if max_val - min_val < 1e-12:
        return np.ones_like(raw) * 0.5
    return (raw - min_val) / (max_val - min_val + 1e-10)


def main():
    parser = argparse.ArgumentParser(description="Compute ML scores from a trained model")
    parser.add_argument("model", help="Path to trained model .pkl file")
    parser.add_argument("features", help="Path to features .npy file")
    parser.add_argument("output", help="Path to write scores .npy file")
    args = parser.parse_args()

    clf = joblib.load(args.model)
    X = np.load(args.features)
    scores = compute_scores(clf, X)
    np.save(args.output, scores)
    print(f"Scores saved to {args.output}: shape={scores.shape}, range=[{scores.min():.4f}, {scores.max():.4f}]")


if __name__ == "__main__":
    main()

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

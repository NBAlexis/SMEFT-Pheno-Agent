# Phase 7 Deliverables: ML Training

Consumes: Phase 5 pure SM/NP samples and Phase 3 anchor metadata.

Must deliver:
- Public CSV files: `sm.csv`, `np_anchor.csv`, and `np_o_N.csv` for every
  claimed operator.
- `results/data/phase7/event_counts.json` with requested counts, actual loaded
  LHCO counts, final-state-cut counts, and exact cut expressions.
- `results/data/phase7/feature_schema.json` with ordered features, units,
  definitions, particle assignment, ordering rules, and preprocessing metadata.
- `results/data/phase7/algorithm_comparison.json` and
  `algorithm_descriptions.json` for every trained algorithm, including AUC,
  hyperparameters, score definition, pseudocode, and a stable `algorithm_key`.
- `results/data/phase7/phase7_validation.json` with `status: "pass"`,
  algorithm keys, operator keys, passed validation records, and no failed
  checks.
- `results/algorithms/compute_scores.py` and
  `results/algorithms/anchor_{alg}.pkl` for every trained algorithm, where
  `{alg}` is the stable key from `algorithm_comparison.json["anchor"]`.
- Per-event score CSVs for SM and every pure-NP operator for every trained
  algorithm:
  `results/data/phase7/scores/{alg}_sm_scores.csv` and
  `results/data/phase7/scores/{alg}_np_o_N_scores.csv`.
- `results/plots/roc_anchor.pdf` and
  `results/plots/score_dist_all_pure_np_{alg}.pdf` for every trained algorithm.

Manuscript dependency: feature table, preprocessing statement, algorithm
descriptions/pseudocode, mathematical score definitions, AUC/ROC evidence,
score histograms, and public data paths.

If missing or incomplete: rebuild conversions, retrain/rescore, or recreate
plots from the saved data, then rerun `phase7_validation.json`. Do not filter
algorithms early and do not omit non-anchor pure-NP histograms.

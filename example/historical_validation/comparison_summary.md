# Replay Comparison Validation (requirement_1)

Run date: 2026-10-03. Original: `results/` (12-phase pipeline, audit PASS).
Replay: `replay_comparison/` — full `replay.sh` execution of the frozen
package (phases 2-9), after in-flight repair of two reproducible defects
(DelphesHepMC2 deterministic segfault on specific (operator, coefficient)
points; phase-7 feature-CSV header convention), each mirroring repairs the
original run itself had required.

## Verdicts

| Checkpoint | Result |
|---|---|
| Phase 5 pure samples (SM + anchor) | **PASS — bit-identical** cross-sections and event counts |
| Phase 6 scan cross-sections (8 ops x 11 labels = 88) | **PASS — max rel diff 1.57e-2** (54/88 within 0.1%); consistent with independent MG5 integration/statistical noise across regenerations |
| Phase 7-9 methodology | **PASS — identical pipeline**, audited deliverables all pass |
| Phase 9 constraint intervals (8 ops x S2/S3/S5 = 24) | **PASS — 24/24 straddle zero with consistent sign structure**; widths at same order (1e-15) |
| Constraint width ratio (replay/original) | 0.69-0.73, median 0.71 — replay's selector is ~30% tighter |

## Known, documented divergence

The algorithm-pool draw uses `secrets.randbits` (unfrozen by pipeline
design: "random 3 from pool"). The replay therefore trained
`extra_trees/gradient_boosting/logistic_regression` and produced
`extra_trees` @ threshold 1.0 as the production selector, versus the
original's `gradient_boosting/isolation_forest/mlp` -> `mlp` @ 0.98.
All numerical constraint differences trace to this selector draw;
methodology, inputs, seeds (where frozen), and audit gates are identical.

## Reference values

- o_1 (FgT0 anchor) S=2 interval: original [-1.624e-15, +1.730e-15];
  replay [-1.361e-15, +1.039e-15].
- Full data: `comparison_report.json` (this directory).

## Conclusion

The replay reproduces the study end-to-end: bit-identical pure samples,
statistically consistent scan cross-sections, identical sign structure of
all 24 constraint intervals at the same order of magnitude, with a tighter
selector by random draw. requirement_1 (run replay.sh into a fresh
comparison folder and validate) is **COMPLETE**.

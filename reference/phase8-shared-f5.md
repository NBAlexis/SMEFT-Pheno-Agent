# Phase 8 Shared `f5` Background

Use this reference when building the common coefficient-zero event sample,
handling zero selected events, or auditing `sigma0_after_cut_pb`.

## Initial Sources

For every Phase 3 operator key `o_N`, use exactly:

```text
data/phase6/np_o_N_f5.lhco
data/phase6/np_o_N_f5_banner.txt
data/phase6/np_o_N_scan_result.json
```

Verify that the scan result records the operator's Phase 3 model, the active
process and beam settings, `nevents=nev_scan`, and scan label `f5`. The runner
sets every non-target coefficient to zero, and `f5` sets the target coefficient
to zero. Different operators may come from different requested UFO models, but
each source model must equal that operator's Phase 3 model.

Merge the LHCO files with:

```text
python scripts/merge_lhco.py ... \
  --cross-section-rule banner_arithmetic_mean
```

Write:

```text
data/phase8/shared_f5.lhco
data/phase8/shared_f5_merge.json
data/phase8/csv/shared_f5.csv
```

`merged_cross_section_pb` is the arithmetic mean of all source banner
cross-sections. It is not weighted by loaded event counts. The denominator for
selection efficiency remains the loaded event count of the merged LHCO file.
Convert the merged LHCO with the Phase 7 feature extraction. The shared feature
CSV row count is `surviving_final_state_event_count`.

For every algorithm, write:

```text
data/phase8/scores/{algorithm}/shared_f5_scores.csv
```

Each row contains `event_index`, `score`, and `source_csv`; `source_csv` must
name `data/phase8/csv/shared_f5.csv`. Define a passing event by
`score >= threshold`.

## Zero Selected Events

Use the same shared pool for all algorithms. For each of the 51 thresholds:

Derive `anchor_scan_passing_event_count` from the eleven anchor score CSVs as
the sum of events with `score >= threshold`. Then:

1. If `anchor_scan_passing_event_count` is zero, record
   `background_status="no_selected_scan_events"`; exclude that threshold from
   optimization and leave the effective count, background, interval, and width
   null.
2. Otherwise count shared-`f5` events with `score >= threshold`.
3. If the count is positive, calculate
   `merged_cross_section_pb * passing_event_count /
   loaded_lhco_event_count`.
4. If the count is zero before three additional rounds, do not calculate a
   background, interval, or width. Record
   `background_status="additional_anchor_f5_required"`, generate one additional
   anchor `f5` sample, rebuild the shared pool, and recompute all algorithms and
   thresholds.
5. If the count remains zero after three additional rounds, set only
   `effective_passing_event_count=0.5` and calculate
   `merged_cross_section_pb * 0.5 / loaded_lhco_event_count`. Keep
   `passing_event_count=0` and record
   `background_status="half_event_after_three_zero_rounds"`.

Never use `0.5` before the third additional round. Add at most one sample per
round and no more than three samples in total. Phase 8 cannot complete while an
otherwise usable threshold has `additional_anchor_f5_required`.

## Additional Anchor Sample

Use `scripts/run_mg5_config.py` with `process_mode="sm_np_point"`. Copy the
anchor Phase 6 process, model, beam, polarization, weighted-order, MadSpin, and
Delphes settings; use the locked `nev_scan`; set the anchor coefficient
explicitly to zero; set every other coefficient to zero. Use a new process/run
and unique output paths for every round.

Example fields:

```json
{
  "process_mode": "sm_np_point",
  "operator": "o_1",
  "target_coefficient": {"index": 1, "value": 0.0},
  "coefficient_mode": "explicit",
  "nevents": 1000000,
  "output_label": "shared_f5_anchor_round_1",
  "output_dir": "results/data/phase8/shared_f5_sources",
  "result_json": "results/data/phase8/shared_f5_sources/anchor_round_1_result.json"
}
```

Retain the result JSON, banner, LHCO, process directory, and order file. They
prove the zero coefficient, locked event target, and independent run. Source
LHCO, banner, and runner-result paths must be non-empty and unique across the
initial and additional sources.

## Background Record

Write `data/phase8/shared_f5_background.json`:

```json
{
  "schema_version": "1.0",
  "source_operators": ["o_1"],
  "anchor_operator": "o_1",
  "initial_f5_sources": [
    {
      "operator": "o_1",
      "model": "model_a",
      "scan_label": "f5",
      "lhco_path": "data/phase6/np_o_1_f5.lhco",
      "banner_path": "data/phase6/np_o_1_f5_banner.txt",
      "runner_result_json": "data/phase6/np_o_1_scan_result.json"
    }
  ],
  "additional_anchor_f5_rounds": 0,
  "additional_anchor_f5_sources": [],
  "loaded_lhco_event_count": 1997200,
  "surviving_final_state_event_count": 1950000,
  "merged_cross_section_pb": 0.034,
  "cross_section_rule": "banner_arithmetic_mean",
  "algorithms": {
    "bdt": {
      "status": "accepted",
      "threshold": 0.62,
      "passing_event_count": 18520,
      "effective_passing_event_count": 18520.0,
      "convention": "observed_events",
      "sigma0_after_cut_pb": 0.0003153
    }
  }
}
```

Each additional source also records `round`, `model`, `runner_result_json`,
`requested_event_count`, `loaded_lhco_event_count`, and
`banner_cross_section_pb`. Keep merge source order equal to the initial source
list followed by the additional source list.

Use `scripts/calculate_shared_f5_background.py` for the final formula and the
decision that another round is required.

## Required Checks

- Source operator keys equal Phase 3 keys in order.
- Initial source paths are the corresponding Phase 6 `f5` deliverables.
- Additional sources are unique anchor `f5` runs with `nevents=nev_scan`.
- Every source exists and has a banner cross-section.
- `shared_f5_merge.json` names `shared_f5.lhco`, contains the same ordered
  sources, and uses `banner_arithmetic_mean`.
- Shared feature and score CSV row counts agree for every algorithm.
- Score-derived passing counts, threshold records, background formulas, and
  fixed fit intercepts agree.

# Event Count and Recovery Contract

Use this reference whenever a phase validates generated LHCO files, recovers
low event counts, merges recovery attempts, or computes selection efficiencies.

## Definitions

- `requested_event_count` is the original target dataset size for the sample or
  scan point. For merged recovery outputs, it is not the sum of planned
  `nevents` across attempts.
- `loaded_lhco_event_count` is the count returned by CutExperiment
  `LoadLHCOlympics(...).GetEventCount()` for the exact LHCO file being analyzed.
- Banner files are cross-section sources only. Never use banner event counts or
  planned `nevents` as efficiency denominators.

## Acceptance Rules

For each generated sample or scan point:

| Loaded/requested fraction | Action |
|---|---|
| `>= 0.9` | Accept normally |
| `>= 0.1` and `< 0.9` | Accept with warning |
| `< 0.1` | Run event-count recovery before any red flag |
| zero or unparsable LHCO | Treat as likely Delphes/root2lhco/card failure, not a normal hard-survey success |

Recovery must not change physics parameters, coefficients, beam energy,
polarization, cuts, algorithms, locked event targets, or scan grids.

## Recovery Execution

Phase 5 and Phase 6 should call the recovery orchestrator rather than manually
choosing among attempts.

The recovery orchestrator runs the MG5 config runner with survey profiles:

| Profile | Meaning |
|---|---|
| `default` | no explicit recovery run-card settings |
| `sde0_hs0` | `sde_strategy = 0`, `hard_survey = 0` |
| `sde0_hs1` | `sde_strategy = 0`, `hard_survey = 1` |
| `sde0_hs2` | `sde_strategy = 0`, `hard_survey = 2` |

`hard_survey = 2` is the maximum for this workflow.

## LHCO Merge Rule

Merge parseable non-empty recovery attempts with the LHCO merge helper.

- Keep all source banners; banners are not merged.
- Count each source with CutExperiment before merging.
- Verify the merged LHCO count equals the sum of source loaded counts.
- Compute the merged cross-section as the
  loaded-LHCO-event-count-weighted average of source banner cross-sections.
- Preserve metadata for every source count, banner, source cross-section, merged
  count, and merged cross-section.

## Phase Use

- Phase 5: apply recovery per SM or pure-NP sample.
- Phase 6: apply recovery per operator scan; group attempts by scan-point label
  before merging.
- Phase 7: when converting pure samples to CSV, record loaded counts from the
  exact LHCO file being converted.
- Phase 8: when computing `cs_cut`, use each scan point's loaded count as the
  denominator. If the scan point is merged, use the merged loaded count.

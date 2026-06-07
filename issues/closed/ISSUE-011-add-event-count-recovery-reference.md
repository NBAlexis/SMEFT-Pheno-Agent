# ISSUE-011: Add dedicated event-count recovery reference

- Priority: high
- Type: workflow documentation
- Status: closed

## Problem

Event-count recovery is rare but complex, and the same rules affect Phase 5,
Phase 6, Phase 7, and Phase 8. If the full recovery/counting logic is repeated
inside each phase, it may distract agents from the normal workflow and increase
the chance of inconsistent behavior.

## Risk

Agents may mix planned `nevents`, banner metadata, raw LHCO counts, merged LHCO
counts, and recovery attempt counts. This can break cut-efficiency denominators,
scan-point metadata, and cross-section fitting.

## Candidate Reference

`reference/event-count-recovery.md`

## Required Content

- define `requested_event_count` as the original target dataset size, not the sum
  of planned `nevents` across recovery attempts
- define `loaded_lhco_event_count` as the value returned by CutExperiment
  `LoadLHCOlympics(...).GetEventCount()`
- forbid using banner event counts or planned `nevents` as efficiency
  denominators
- define acceptance/recovery thresholds:
  - `>=90%`: accept
  - `10%-90%`: accept with warning
  - `<10%`: run recovery
  - zero-event or unparsable LHCO: classify as likely Delphes/root2lhco/card
    failure, not normal hard-survey recovery success
- define that Phase 5/6 call the recovery orchestrator instead of manually
  selecting a best attempt
- define LHCO merge behavior:
  - merge parseable non-empty attempts
  - keep all source banners
  - compute merged cross-section as the loaded-LHCO-event-count-weighted average
    of source banner cross-sections
- define Phase 7/8 denominator behavior:
  - use the actual loaded LHCO count of the file being analyzed
  - use merged loaded count when analyzing merged LHCO

## Phase Integration

Keep phase files short. Phase 5, Phase 6, Phase 7, and Phase 8 should reference
this document rather than restating the full recovery/counting policy.

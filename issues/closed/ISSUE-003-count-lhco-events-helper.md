# ISSUE-003: Add deterministic LHCO event-count helper

- Priority: high
- Type: script candidate
- Status: closed

## Problem

Phase 5/6 require exact LHCO counts and recovery metadata, but agents must
currently reimplement `LoadLHCOlympics(...).GetEventCount()` and JSON writing.
The same count operation is also needed after merged LHCO files are produced,
because downstream cut efficiencies must use the actual loaded LHCO event count
of the file being analyzed, not the planned MG5 `nevents`.

## Risk

Different agents may write inconsistent count schemas, forget the
requested/actual distinction, or accidentally use banner event counts.

## Candidate Script

`scripts/count_lhco_events.py`

## Candidate Behavior

- input: `lhco_path`, `requested_nevents`, optional dataset id
- output JSON fields: `requested_event_count`, `loaded_lhco_event_count`,
  `fraction`, `count_source`, `count_context`
- for merged recovery outputs, `requested_event_count` means the original target
  dataset size, not the sum of planned `nevents` across recovery attempts
- support `count_context: mg5_output` for raw LHCO produced by a single
  MG5/Delphes/root2lhco run
- support `count_context: merged_output` for LHCO produced by the merge helper
  and later used for cut-efficiency denominators
- fail if LHCO is missing or cannot be parsed
- report zero loaded events explicitly as `loaded_lhco_event_count: 0`; this is
  an invalid/empty-sample condition, usually requiring Delphes/root2lhco/card
  investigation, not a normal hard-survey recovery path

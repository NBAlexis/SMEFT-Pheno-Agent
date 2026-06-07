# ISSUE-005: Add LHCO merge helper for recovery attempts

- Priority: high
- Type: script candidate
- Status: closed

## Problem

Phase 6 recovery should merge all recovery attempts by scan-point label.
CutExperiment supports merging LHCO event sets, so the agent should not choose
one attempt over another.

## Evidence

`F:\Pywork\CutExperiment\Interfaces\UsefulFunctions.py` provides
`CombineEventsLHCO(fileNames, targetFileName)`, which loads each LHCO file,
calls `AddEventSet`, writes with `SaveToLHCO`, and verifies the merged count.

## Risk

Without a bundled merge helper, agents may choose one attempt over another, drop
useful generated events, or merge incorrectly.

## Candidate Script

`scripts/merge_lhco.py`

## Candidate Behavior

- input: ordered LHCO paths, output LHCO path, optional metadata path
- import CutExperiment from `cutexperiment_path`
- merge using `LoadLHCOlympics`, `AddEventSet`, and `SaveToLHCO`
- write source counts, merged count, and source paths
- verify `merged_count == sum(source_counts)`
- keep every source banner path in metadata; banners are not merged
- accept per-source cross-section values parsed from each source banner
- write the merged cross-section as the loaded-LHCO-event-count-weighted average
  of the source cross-sections
- write enough metadata to reproduce the weighted average, including source
  counts, source cross-sections, and the final merged cross-section

## Cross-Section Rule

For Phase 6 scan points, a merged LHCO may combine attempts with distinct banner
cross-section estimates. The downstream cross-section for the merged LHCO is the
loaded-LHCO-event-count-weighted average of the source banner cross-sections.
All original banners must remain available for audit/debugging.

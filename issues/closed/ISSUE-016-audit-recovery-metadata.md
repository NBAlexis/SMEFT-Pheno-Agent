# ISSUE-016: Audit recovery metadata contents, not just files

- Priority: medium
- Type: audit robustness
- Status: closed

## Problem

`scripts/audit_expected_outputs.py` checks that `event_count_recovery.json`
exists, but it does not inspect recovery metadata content.

## Risk

Phase 11 can miss inconsistencies such as:

- merged outputs below the 10% floor
- missing source banner lists
- missing merged cross-section values
- missing warning records for 10%-90% loaded counts
- mismatch between recovery merged output paths and expected Phase 5/6 files

## Candidate Fix

Extend `audit_expected_outputs.py` to parse Phase 5/6 recovery metadata and
validate:

- every expected sample/scan label has a recovery or accepted record
- final loaded counts are positive and meet the documented floor unless a red
  flag is recorded
- merged cross-sections are present when multiple attempts are merged
- all source banner paths exist
- final merged LHCO paths match the expected Phase 5/6 data files

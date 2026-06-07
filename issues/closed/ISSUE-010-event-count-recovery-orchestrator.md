# ISSUE-010: Add event-count recovery orchestrator

- Priority: high
- Type: script candidate
- Status: closed

## Problem

The MG5 config runner can execute one configured run with one survey profile,
and the LHCO merge helper can merge successful attempts. A separate, deterministic
recovery orchestrator is still needed so agents do not manually decide which
attempt is "best" or when to continue.

## Risk

Without a recovery orchestrator, agents may stop early, select one arbitrary
attempt, ignore mergeable events, or apply the `<10% requested events` rule
inconsistently.

## Candidate Script

`scripts/recover_lhco_count.py`

## Candidate Behavior

- input: base MG5 run JSON, requested event count, recovery survey enum order,
  output merged LHCO path, output metadata path
- treat the requested event count as the original target dataset size; do not
  replace it with the sum of planned `nevents` across recovery attempts
- call the MG5 config runner for the default attempt and, if needed, additional
  enum profiles such as `sde0_hs0`, `sde0_hs1`, and `sde0_hs2`
- after each parseable non-empty LHCO, call the LHCO count helper
- merge parseable non-empty attempts with the LHCO merge helper
- continue until merged loaded LHCO event count is at least `10%` of the
  requested event count, or until the allowed recovery profiles are exhausted
- classify zero-event or malformed LHCO attempts separately as likely
  Delphes/root2lhco/card failures; do not treat them as normal hard-survey
  recovery successes
- write metadata containing every attempt, survey enum, LHCO path, banner path,
  loaded count, parsed cross-section, merge status, final merged count, and final
  merged cross-section

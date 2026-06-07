# ISSUE-014: Keep zero-event LHCO out of hard-survey recovery

- Priority: high
- Type: recovery policy
- Status: closed

## Problem

`count_lhco_events.py` marks loaded count zero as `zero_events`, but
`recover_lhco_count.py` currently continues through the survey profile ladder
when no usable events are counted.

## Risk

Zero-event LHCO is usually a Delphes/root2lhco/card or output-production problem,
not a normal hard-survey event-count shortage. Continuing through
`sde0_hs0/sde0_hs1/sde0_hs2` can waste time and obscure the real failure.

## Candidate Fix

- if a run produces parseable LHCO with zero loaded events, record
  `zero_event_failure`
- do not treat zero-event outputs as normal event-count recovery successes
- stop the recovery ladder for that unit and require the agent to inspect/fix
  Delphes/root2lhco/card/output generation before rerunning
- keep nonzero-but-below-10% outputs on the normal recovery path

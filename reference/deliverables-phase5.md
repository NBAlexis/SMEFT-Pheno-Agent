# Phase 5 Deliverables: Pure Samples

Consumes: Phase 3 operator/anchor metadata and Phase 4 per-operator ranges.

Must deliver:
- `results/data/phase5/sm.lhco`, `sm_banner.txt`, and `sm_result.json`.
- `results/data/phase5/np_o_N.lhco`, `np_o_N_banner.txt`, and
  `np_o_N_result.json` for every globally claimed operator.
- `results/data/phase5/np_anchor.lhco`, `np_anchor_banner.txt`, and
  `np_anchor_alias.json`.
- `results/data/phase5/event_count_recovery.json` with requested counts, actual
  LHCO counts, recovery attempts, selected/merged output paths, and cross
  sections.
- For every delivered SM or pure-NP LHCO sample, the final loaded LHCO event
  count after recovery must be at least `10%` of its requested event count.

Each recovery call passes the shared phase record and identifies its unit:

```json
{
  "metadata_path": "results/data/phase5/event_count_recovery.json",
  "recovery_unit": "sm or np_o_N",
  "required_units": ["sm", "np_o_1", "...", "np_o_N"]
}
```

Manuscript dependency: SM and pure-NP public data, actual event counts, raw
cross-sections, recovery notes, and all pure-NP score histograms.

If missing or incomplete: rerun/resume the specific SM or pure-NP unit through
the MG5 runner or event-count recovery wrapper. Counts below the requested
target are not failures by themselves; counts below `10%` of the
requested target are incomplete until recovery succeeds or a structured
`phase_fail` record permitted by `SKILL.md` is
recorded.

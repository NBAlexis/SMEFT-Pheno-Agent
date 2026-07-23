# Phase 4 Deliverables: Coefficient Ranges

Consumes: Phase 3 `operator_claims.json`, `cross_sections.json`, and
`anchor.json`.

Must deliver:
- `results/data/phase4/sm_baseline.json` with positive SM cross-section,
  significance formula metadata, and the Phase 6 scan event target.
- `results/data/phase4/sm_baseline_result.json` with the runner manifest for
  the SM baseline generation, including process directory, order file,
  stdout/stderr paths, banner path, LHCO path, and parsed cross-section. It must
  record `event_generator=MadGraph5`, `detector_simulation=Delphes`,
  `analysis_event_format=LHCO_from_Delphes_ROOT`, the selected Delphes card,
  and `nevents >= nev_phase4`.
- `results/data/phase4/coefficient_ranges.json` with exactly one finite,
  positive, two-significant-digit `c_scan` for every globally claimed operator.

Manuscript dependency: scan lower/upper bounds and SM baseline context.

If missing or incomplete: recompute the SM baseline or per-operator ranges. Do
not reuse the anchor range for other operators and do not proceed with a
missing operator range.

# Phase 12 Deliverables: Audit

Consumes: all phase deliverables, cleanup output, and the Phase 11 replay package.

Must deliver:
- Successful verification of `results/research_contract.json` and
  `results/deliverables_contract.json` against the current configuration.
- `results/deliverables_resolved.json`, expanded from the frozen rules using the
  actual operator, scan-label, algorithm, replay, and manuscript-format
  manifests, with no pending rules.
- `results/audit_expected_outputs.json` from `scripts/audit_expected_outputs.py`.
  The audit record must include the Phase 10 required-ID source
  `reference/manuscript-checklist-required-ids.json`.
- `results/audit_report.json` with `PASS`, `WARN`, or `FAIL`.
- Cross-phase checks for operator sets, scan points, algorithms, event-count
  denominators, final selected algorithm, manuscript consistency, cleanup, and
  replay-package coverage and independence, plus an existence/type/schema check
  for every resolved contract item.

Manuscript dependency: final consistency statement and bug-report evidence.

If missing or incomplete: rerun the audit and repair the responsible phase or
technical implementation. Do not remove or weaken a frozen rule. Write final
`FAIL` only with the exact unmet contract items, attempted diagnoses and
recoveries, and concrete evidence that they cannot be fulfilled.

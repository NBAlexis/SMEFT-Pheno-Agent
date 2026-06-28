# Phase 11 Deliverables: Audit

Consumes: all phase deliverables and cleanup output.

Must deliver:
- `results/audit_expected_outputs.json` from `scripts/audit_expected_outputs.py`.
  The audit record must include the Phase 10 required-ID source
  `reference/manuscript-checklist-required-ids.json`.
- `results/audit_report.json` with `PASS`, `WARN`, or `FAIL`.
- Cross-phase checks for operator sets, scan points, algorithms, event-count
  denominators, final selected algorithm, manuscript consistency, and cleanup.

Manuscript dependency: final consistency statement and bug-report evidence.

If missing or incomplete: rerun the audit. If the audit finds a missing required
upstream artifact, repair the responsible phase artifact when possible; otherwise
write `FAIL` with concrete evidence.

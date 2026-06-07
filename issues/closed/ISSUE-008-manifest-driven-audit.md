# ISSUE-008: Make Phase 11 file checks manifest-driven

- Priority: low
- Type: future script planning
- Status: closed

## Problem

Phase 11 combines wildcard checks with cross-phase consistency rules.

## Risk

Wildcards may miss missing operator/scan-point combinations when some files
exist but the full expected matrix is incomplete.

## Current Decision

Do not implement a concrete `audit_expected_outputs` script yet. Its design
depends on the MG5 runner, LHCO count helper, LHCO merge helper, and Phase 8
score/selection metadata schemas, plus the event-count recovery orchestrator.
Implementing audit before those manifests are stable would likely duplicate
rules and create another source of inconsistency.

## Candidate Future Fix

- build expected files from `operator_claims.json`, `scan_manifest.json`,
  event-count/merge manifests, and algorithm metadata
- check each expected file explicitly

## Script Relation

May become `scripts/audit_expected_outputs.py` after upstream manifest schemas
stabilize.

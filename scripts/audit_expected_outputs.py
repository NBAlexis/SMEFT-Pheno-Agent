#!/usr/bin/env python3
"""Manifest-driven output audit for the SMEFT-ML workflow."""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from typing import Any, Dict, Iterable, List, Optional


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _result_root(workdir: str, run_dir: Optional[str]) -> str:
    if run_dir:
        return os.path.join(workdir, "results", run_dir)
    return os.path.join(workdir, "results")


def _exists_nonempty(path: str) -> Dict[str, Any]:
    return {
        "path": path,
        "exists": os.path.exists(path),
        "size": os.path.getsize(path) if os.path.exists(path) else 0,
        "ok": os.path.exists(path) and os.path.getsize(path) > 0,
    }


def _operators(root: str) -> List[str]:
    claims_path = os.path.join(root, "data", "phase3", "operator_claims.json")
    if not os.path.exists(claims_path):
        return []
    claims = _load_json(claims_path)
    return sorted(claims.keys(), key=lambda k: int(str(k).split("_")[-1]))


def _scan_labels(root: str, operators: Iterable[str]) -> Dict[str, List[str]]:
    manifest_path = os.path.join(root, "data", "phase6", "scan_manifest.json")
    manifest = _load_json(manifest_path) if os.path.exists(manifest_path) else {}
    labels = {}
    for op in operators:
        op_manifest = manifest.get(op, {})
        labels[op] = list(op_manifest.get("labels") or [f"f{i}" for i in range(11)])
    return labels


def _algorithm_names(root: str) -> List[str]:
    path = os.path.join(root, "data", "phase7", "algorithm_comparison.json")
    if not os.path.exists(path):
        return []
    data = _load_json(path)
    return sorted((data.get("anchor") or {}).keys())


def _expected_files(root: str) -> List[Dict[str, Any]]:
    expected: List[Dict[str, Any]] = []
    operators = _operators(root)
    scan_labels = _scan_labels(root, operators)
    algorithms = _algorithm_names(root)

    fixed = [
        ("data/phase2/environment_manifest.json", "abort"),
        ("data/phase3/operator_claims.json", "abort"),
        ("data/phase3/cross_sections.json", "abort"),
        ("data/phase3/anchor.json", "abort"),
        ("data/phase4/coefficient_ranges.json", "abort"),
        ("data/phase4/sm_baseline.json", "abort"),
        ("data/phase4/sm_baseline_result.json", "abort"),
        ("data/phase5/sm.lhco", "abort"),
        ("data/phase5/sm_result.json", "abort"),
        ("data/phase5/np_anchor.lhco", "abort"),
        ("data/phase5/np_anchor_alias.json", "abort"),
        ("data/phase5/event_count_recovery.json", "abort"),
        ("data/phase6/event_count_recovery.json", "abort"),
        ("data/phase6/scan_manifest.json", "abort"),
        ("data/phase7/sm.csv", "abort"),
        ("data/phase7/np_anchor.csv", "abort"),
        ("data/phase7/event_counts.json", "abort"),
        ("data/phase7/feature_schema.json", "abort"),
        ("data/phase7/algorithm_comparison.json", "abort"),
        ("data/phase7/algorithm_descriptions.json", "abort"),
        ("algorithms/compute_scores.py", "abort"),
        ("data/phase8/threshold_optimization.json", "abort"),
        ("data/phase8/scan_event_counts.json", "abort"),
        ("data/phase8/dataset_summary.json", "abort"),
        ("data/phase9/constraint_table.json", "abort"),
        ("data/phase9/constraint_table.csv", "abort"),
        ("data/phase9/algorithm_selection.json", "abort"),
        ("data/phase10/manuscript_build_environment.json", "abort"),
        ("data/phase10/manuscript_evidence.json", "abort"),
        ("data/phase10/reference_paper_plan.json", "abort"),
        ("data/phase10/literature_plan.json", "abort"),
        ("data/phase10/manuscript_checklist.json", "abort"),
        ("data/phase10/manuscript_validation.json", "abort"),
    ]
    for rel, severity in fixed:
        expected.append({"rel_path": rel, "severity": severity, "source": "fixed"})

    for op in operators:
        expected.append({"rel_path": f"data/phase5/np_{op}_result.json", "severity": "abort", "source": "operator_claims"})
        expected.append({"rel_path": f"data/phase5/np_{op}.lhco", "severity": "abort", "source": "operator_claims"})
        expected.append({"rel_path": f"data/phase7/np_{op}.csv", "severity": "abort", "source": "operator_claims"})
        expected.append({"rel_path": f"data/phase6/np_{op}_scan_result.json", "severity": "abort", "source": "operator_claims"})
        for label in scan_labels.get(op, []):
            expected.append({"rel_path": f"data/phase6/np_{op}_{label}.lhco", "severity": "abort", "source": "scan_manifest"})
            expected.append({"rel_path": f"data/phase8/csv/np_{op}_{label}.csv", "severity": "abort", "source": "scan_manifest"})
            for alg in algorithms:
                expected.append({
                    "rel_path": f"data/phase8/scores/{alg}/np_{op}_{label}_scores.csv",
                    "severity": "abort",
                    "source": "algorithm_comparison+scan_manifest",
                })
        for alg in algorithms:
            expected.append({"rel_path": f"data/phase8/csfit_{op}_{alg}.json", "severity": "abort", "source": "algorithm_comparison"})

    for alg in algorithms:
        expected.append({"rel_path": f"data/phase7/scores/{alg}_sm_scores.csv", "severity": "abort", "source": "algorithm_comparison"})
        for op in operators:
            expected.append({"rel_path": f"data/phase7/scores/{alg}_np_{op}_scores.csv", "severity": "abort", "source": "algorithm_comparison+operator_claims"})
        expected.append({"rel_path": f"algorithms/anchor_{alg}.pkl", "severity": "abort", "source": "algorithm_comparison"})
        expected.append({"rel_path": f"plots/score_dist_all_pure_np_{alg}.pdf", "severity": "abort", "source": "algorithm_comparison"})
        for op in operators:
            expected.append({"rel_path": f"plots/csfit_plot_{op}_{alg}.pdf", "severity": "abort", "source": "algorithm_comparison+operator_claims"})

    fixed_plots = [
        ("plots/roc_anchor.pdf", "abort"),
        ("plots/threshold_comparison.pdf", "abort"),
        ("plots/anchor_s2_constraint_range_vs_threshold.pdf", "abort"),
        ("plots/anchor_s2_algorithm_constraint_bar.pdf", "abort"),
    ]
    for rel, severity in fixed_plots:
        expected.append({"rel_path": rel, "severity": severity, "source": "fixed_plot"})

    return expected


def _recovery_metadata_checks(root: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    for phase in ("phase5", "phase6"):
        rel_path = os.path.join("data", phase, "event_count_recovery.json")
        path = os.path.join(root, rel_path)
        if not os.path.exists(path):
            continue
        try:
            data = _load_json(path)
        except Exception as exc:
            checks.append({
                "rel_path": rel_path,
                "severity": "abort",
                "source": "recovery_metadata",
                "path": path,
                "ok": False,
                "error": f"Could not parse recovery metadata: {exc}",
            })
            continue

        status = data.get("status")
        if status not in {"accepted", "zero_event_failure", "exhausted_recovery_red_flag"}:
            checks.append({
                "rel_path": rel_path,
                "severity": "abort",
                "source": "recovery_metadata",
                "path": path,
                "ok": False,
                "error": f"Unexpected recovery status: {status!r}",
            })

        if status == "accepted":
            merged_outputs = data.get("merged_outputs")
            if not isinstance(merged_outputs, list) or not merged_outputs:
                checks.append({
                    "rel_path": rel_path,
                    "severity": "abort",
                    "source": "recovery_metadata",
                    "path": path,
                    "ok": False,
                    "error": "accepted recovery metadata has no merged_outputs",
                })
                continue
            for item in merged_outputs:
                label = item.get("label", "<missing>")
                lhco_path = item.get("lhco_path")
                count = int(item.get("loaded_lhco_event_count", 0))
                requested = int(item.get("requested_event_count", data.get("requested_event_count", 0)) or 0)
                source_banners = item.get("source_banners_retained") or []
                merged_cross_section = item.get("merged_cross_section_pb")
                ok = True
                errors = []
                if not lhco_path or not os.path.exists(lhco_path):
                    ok = False
                    errors.append("merged LHCO path missing")
                if count <= 0:
                    ok = False
                    errors.append("merged loaded count is not positive")
                if requested > 0 and count < 0.1 * requested:
                    ok = False
                    errors.append("merged loaded count is below 10% requested")
                missing_banners = [p for p in source_banners if p and not os.path.exists(p)]
                if missing_banners:
                    ok = False
                    errors.append(f"missing source banners: {missing_banners}")
                if len(source_banners) > 1 and merged_cross_section is None:
                    ok = False
                    errors.append("missing merged cross-section for multi-attempt merge")
                checks.append({
                    "rel_path": f"{rel_path}:{label}",
                    "severity": "abort",
                    "source": "recovery_metadata",
                    "path": path,
                    "ok": ok,
                    "errors": errors,
                })

            for warning in data.get("warnings", []):
                fraction = warning.get("fraction")
                if fraction is None or not (0.1 <= float(fraction) < 0.9):
                    checks.append({
                        "rel_path": rel_path,
                        "severity": "abort",
                        "source": "recovery_metadata",
                        "path": path,
                        "ok": False,
                        "error": f"Invalid warning fraction: {warning}",
                    })

        if status == "zero_event_failure" and not data.get("zero_event_failure"):
            checks.append({
                "rel_path": rel_path,
                "severity": "abort",
                "source": "recovery_metadata",
                "path": path,
                "ok": False,
                "error": "zero_event_failure status missing zero_event_failure details",
            })
    return checks


def _iter_json_objects(obj: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(obj, dict):
        yield obj
        for value in obj.values():
            yield from _iter_json_objects(value)
    elif isinstance(obj, list):
        for item in obj:
            yield from _iter_json_objects(item)


def _phase3_runner_manifest_checks(root: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    rel_path = os.path.join("data", "phase3", "model_status.json")
    path = os.path.join(root, rel_path)
    if not os.path.exists(path):
        return checks
    try:
        data = _load_json(path)
    except Exception as exc:
        return [{
            "rel_path": rel_path,
            "severity": "abort",
            "source": "phase3_runner_manifests",
            "path": path,
            "ok": False,
            "error": f"Could not parse model_status.json: {exc}",
        }]

    result_paths = set()
    for record in _iter_json_objects(data):
        for key in ("create_np_result_json", "result_json", "result_json_path", "runner_result_json"):
            value = record.get(key)
            if isinstance(value, str) and value:
                result_paths.add(value)

    for result_path in sorted(result_paths):
        full_path = result_path if os.path.isabs(result_path) else os.path.join(root, result_path)
        try:
            rel = os.path.relpath(full_path, root)
        except ValueError:
            rel = full_path
        checks.append({
            "rel_path": rel,
            "severity": "abort",
            "source": "phase3_runner_manifests",
            **_exists_nonempty(full_path),
        })
    return checks


def _phase9_strategy_checks(root: str) -> List[Dict[str, Any]]:
    rel_path = os.path.join("data", "phase9", "algorithm_selection.json")
    path = os.path.join(root, rel_path)
    if not os.path.exists(path):
        return []
    try:
        data = _load_json(path)
    except Exception as exc:
        return [{
            "rel_path": rel_path,
            "severity": "abort",
            "source": "phase9_final_strategy",
            "path": path,
            "ok": False,
            "error": f"Could not parse algorithm_selection.json: {exc}",
        }]

    required = [
        "selected_algorithm",
        "selected_threshold",
        "anchor_operator",
        "selection_scope",
        "selection_criterion",
        "source_threshold_optimization_entry",
    ]
    missing = [key for key in required if key not in data or data.get(key) in (None, "")]
    return [{
        "rel_path": rel_path,
        "severity": "abort",
        "source": "phase9_final_strategy",
        "path": path,
        "ok": not missing,
        "missing_keys": missing,
    }]


def _cleanup_log_checks(root: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    for rel_dir in ("mg5_processes", "orders"):
        full_dir = os.path.join(root, rel_dir)
        entries = os.listdir(full_dir) if os.path.isdir(full_dir) else []
        checks.append({
            "rel_path": rel_dir,
            "severity": "abort",
            "source": "cleanup_log",
            "path": full_dir,
            "ok": os.path.isdir(full_dir) and bool(entries),
            "entry_count": len(entries),
        })

    rel_path = os.path.join("mg5_processes", "cleanup_log.json")
    path = os.path.join(root, rel_path)
    if not os.path.exists(path):
        checks.append({
            "rel_path": rel_path,
            "severity": "abort",
            "source": "cleanup_log",
            "path": path,
            "ok": False,
            "error": "Missing cleanup log",
        })
        return checks
    try:
        data = _load_json(path)
    except Exception as exc:
        checks.append({
            "rel_path": rel_path,
            "severity": "abort",
            "source": "cleanup_log",
            "path": path,
            "ok": False,
            "error": f"Could not parse cleanup log: {exc}",
        })
        return checks
    required = [
        "expected_process_dirs",
        "moved_process_dirs",
        "missing_process_dirs",
        "expected_order_files",
        "moved_order_files",
        "missing_order_files",
    ]
    missing = [key for key in required if key not in data or not isinstance(data.get(key), list)]
    no_expected_records = not data.get("expected_process_dirs") and not data.get("expected_order_files")
    checks.append({
        "rel_path": rel_path,
        "severity": "abort",
        "source": "cleanup_log",
        "path": path,
        "ok": not missing and not no_expected_records,
        "missing_or_nonlist_keys": missing,
        "no_expected_records": no_expected_records,
    })
    return checks


def _resolve_inside_root(root: str, path_value: str) -> str:
    if os.path.isabs(path_value):
        return path_value
    return os.path.join(root, path_value)


def _phase10_manuscript_checks(root: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []

    draft_glob = os.path.join(root, "data", "phase10", "manuscript_draft_v1.*")
    drafts = [path for path in glob.glob(draft_glob) if os.path.getsize(path) > 0]
    checks.append({
        "rel_path": "data/phase10/manuscript_draft_v1.*",
        "severity": "abort",
        "source": "phase10_manuscript",
        "path": draft_glob,
        "ok": bool(drafts),
        "matched_paths": drafts,
    })

    checklist_rel = os.path.join("data", "phase10", "manuscript_checklist.json")
    checklist_path = os.path.join(root, checklist_rel)
    if os.path.exists(checklist_path):
        try:
            checklist = _load_json(checklist_path)
            items = checklist.get("items")
            draft_path = checklist.get("draft_path")
            bad_status = []
            if isinstance(items, list):
                bad_status = [
                    item.get("id", "<missing>")
                    for item in items
                    if item.get("status") not in {"present", "missing", "not_applicable"}
                ]
            checks.append({
                "rel_path": checklist_rel,
                "severity": "abort",
                "source": "phase10_checklist_schema",
                "path": checklist_path,
                "ok": isinstance(items, list) and bool(items) and bool(draft_path) and not bad_status,
                "bad_status_items": bad_status,
                "has_draft_path": bool(draft_path),
                "item_count": len(items) if isinstance(items, list) else 0,
            })
        except Exception as exc:
            checks.append({
                "rel_path": checklist_rel,
                "severity": "abort",
                "source": "phase10_checklist_schema",
                "path": checklist_path,
                "ok": False,
                "error": f"Could not parse manuscript_checklist.json: {exc}",
            })

    validation_rel = os.path.join("data", "phase10", "manuscript_validation.json")
    validation_path = os.path.join(root, validation_rel)
    validation: Dict[str, Any] = {}
    if os.path.exists(validation_path):
        try:
            validation = _load_json(validation_path)
            status = validation.get("status")
            checks.append({
                "rel_path": validation_rel,
                "severity": "abort",
                "source": "phase10_validation_schema",
                "path": validation_path,
                "ok": status in {"pass", "issues_remaining"},
                "status": status,
            })
        except Exception as exc:
            checks.append({
                "rel_path": validation_rel,
                "severity": "abort",
                "source": "phase10_validation_schema",
                "path": validation_path,
                "ok": False,
                "error": f"Could not parse manuscript_validation.json: {exc}",
            })

    literature_rel = os.path.join("data", "phase10", "literature_plan.json")
    literature_path = os.path.join(root, literature_rel)
    if os.path.exists(literature_path):
        try:
            literature = _load_json(literature_path)
            required = ["toolchain", "foundational", "comparison_citations", "section_usage"]
            missing = [key for key in required if key not in literature]
            checks.append({
                "rel_path": literature_rel,
                "severity": "abort",
                "source": "phase10_literature_schema",
                "path": literature_path,
                "ok": not missing,
                "missing_keys": missing,
            })
        except Exception as exc:
            checks.append({
                "rel_path": literature_rel,
                "severity": "abort",
                "source": "phase10_literature_schema",
                "path": literature_path,
                "ok": False,
                "error": f"Could not parse literature_plan.json: {exc}",
            })

    evidence_rel = os.path.join("data", "phase10", "manuscript_evidence.json")
    evidence_path = os.path.join(root, evidence_rel)
    if os.path.exists(evidence_path):
        try:
            evidence = _load_json(evidence_path)
            diagrams = ((evidence.get("figures") or {}).get("feynman_diagrams"))
            records = _terminal_diagram_records(diagrams)
            missing_reasons = [r for r in records if r.get("missing_reason")]
            bad_records = []
            for record in records:
                path_value = record.get("path") or record.get("figure_path")
                if path_value:
                    resolved = _resolve_inside_root(root, str(path_value))
                    if not os.path.exists(resolved) or os.path.getsize(resolved) == 0:
                        bad_records.append({"record": record, "error": "diagram path missing or empty"})
                elif not record.get("missing_reason"):
                    bad_records.append({"record": record, "error": "no path and no missing_reason"})
            validation_mentions_feynman = "feynman" in json.dumps(validation, sort_keys=True).lower()
            checks.append({
                "rel_path": evidence_rel + ":figures.feynman_diagrams",
                "severity": "abort",
                "source": "phase10_feynman_evidence",
                "path": evidence_path,
                "ok": bool(records) and not bad_records and (not missing_reasons or validation_mentions_feynman),
                "record_count": len(records),
                "bad_records": bad_records,
                "missing_reason_count": len(missing_reasons),
                "validation_mentions_feynman": validation_mentions_feynman,
            })
        except Exception as exc:
            checks.append({
                "rel_path": evidence_rel + ":figures.feynman_diagrams",
                "severity": "abort",
                "source": "phase10_feynman_evidence",
                "path": evidence_path,
                "ok": False,
                "error": f"Could not parse Feynman diagram evidence: {exc}",
            })

    return checks


def _terminal_diagram_records(value: Any) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    if isinstance(value, list):
        for item in value:
            records.extend(_terminal_diagram_records(item))
    elif isinstance(value, dict):
        if any(key in value for key in ("path", "figure_path", "missing_reason")):
            records.append(value)
        else:
            for item in value.values():
                records.extend(_terminal_diagram_records(item))
    return records


def _manuscript_format_checks(root: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    rel_path = os.path.join("data", "phase10", "manuscript_build_environment.json")
    env_path = os.path.join(root, rel_path)
    if not os.path.exists(env_path):
        return [{
            "rel_path": rel_path,
            "severity": "abort",
            "source": "phase10_format",
            "path": env_path,
            "ok": False,
            "error": "Missing manuscript build environment; cannot decide PDF vs HTML requirement",
        }]

    try:
        env = _load_json(env_path)
    except Exception as exc:
        return [{
            "rel_path": rel_path,
            "severity": "abort",
            "source": "phase10_format",
            "path": env_path,
            "ok": False,
            "error": f"Could not parse manuscript build environment: {exc}",
        }]

    if "pdf_required" not in env:
        checks.append({
            "rel_path": rel_path,
            "severity": "abort",
            "source": "phase10_format",
            "path": env_path,
            "ok": False,
            "error": "Missing pdf_required field",
        })
        return checks

    pdf_required = bool(env.get("pdf_required"))
    if pdf_required:
        pdf = _exists_nonempty(os.path.join(root, "manuscript.pdf"))
        tex = _exists_nonempty(os.path.join(root, "manuscript.tex"))
        checks.append({
            "rel_path": "manuscript.pdf",
            "severity": "abort",
            "source": "phase10_format",
            **pdf,
        })
        checks.append({
            "rel_path": "manuscript.tex",
            "severity": "abort",
            "source": "phase10_format",
            **tex,
        })
    else:
        html = _exists_nonempty(os.path.join(root, "manuscript.html"))
        checks.append({
            "rel_path": "manuscript.html",
            "severity": "abort",
            "source": "phase10_format",
            **html,
        })

    selected_format = str(env.get("selected_format", "")).lower()
    if pdf_required and selected_format == "html":
        checks.append({
            "rel_path": rel_path,
            "severity": "abort",
            "source": "phase10_format",
            "path": env_path,
            "ok": False,
            "error": "selected_format=html while pdf_required=true",
        })
    return checks


def audit_expected_outputs(workdir: str, run_dir: Optional[str] = None) -> Dict[str, Any]:
    root = _result_root(os.path.abspath(os.path.expanduser(workdir)), run_dir)
    expected = _expected_files(root)
    checks = []
    for item in expected:
        path = os.path.join(root, item["rel_path"])
        rec = dict(item)
        rec.update(_exists_nonempty(path))
        checks.append(rec)
    checks.extend(_recovery_metadata_checks(root))
    checks.extend(_phase3_runner_manifest_checks(root))
    checks.extend(_phase9_strategy_checks(root))
    checks.extend(_cleanup_log_checks(root))
    checks.extend(_phase10_manuscript_checks(root))

    checks.extend(_manuscript_format_checks(root))

    failures = [c for c in checks if not c["ok"] and c["severity"] == "abort"]
    warnings = [c for c in checks if not c["ok"] and c["severity"] == "warn"]
    return {
        "schema_version": "1.0",
        "root": root,
        "status": "FAIL" if failures else ("WARN" if warnings else "PASS"),
        "checks": checks,
        "failures": failures,
        "warnings": warnings,
        "expected_count": len(checks),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit expected workflow outputs")
    parser.add_argument("workdir")
    parser.add_argument("--run-dir", default=None)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    report = audit_expected_outputs(args.workdir, run_dir=args.run_dir)
    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)
            f.write("\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] in {"PASS", "WARN"} else 2


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Manifest-driven output audit for the SMEFT-ML workflow."""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import sys
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple


PHASE7_VALIDATION_CHECK_IDS = {
    "feature_schema_complete",
    "algorithm_keys_consistent",
    "algorithm_descriptions_complete",
    "public_csv_complete",
    "score_csv_complete",
    "plots_complete",
}


def _phase10_required_items_path(override_path: Optional[str] = None) -> str:
    if override_path:
        return os.path.abspath(os.path.expanduser(override_path))
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(script_dir, "..", "reference", "manuscript-checklist-required-ids.json"),
        os.path.join(os.getcwd(), "reference", "manuscript-checklist-required-ids.json"),
        os.path.join(os.getcwd(), "..", "reference", "manuscript-checklist-required-ids.json"),
    ]
    for path in candidates:
        normalized = os.path.abspath(path)
        if os.path.exists(normalized):
            return normalized
    return os.path.abspath(candidates[0])


def _phase10_required_checklist_ids(override_path: Optional[str] = None) -> Tuple[Set[str], str, Optional[str]]:
    path = _phase10_required_items_path(override_path)
    if not os.path.exists(path):
        return set(), path, "Missing canonical checklist ID JSON"
    try:
        data = _load_json(path)
    except Exception as exc:
        return set(), path, f"Could not parse canonical checklist ID JSON: {exc}"

    required_items = data.get("required_items")
    if not isinstance(required_items, list):
        return set(), path, "canonical checklist ID JSON missing required_items list"
    ids = {
        item.get("id")
        for item in required_items
        if isinstance(item, dict) and isinstance(item.get("id"), str) and item.get("id")
    }
    if not ids:
        return set(), path, "No checklist IDs found in canonical checklist ID JSON"
    if len(ids) != len(required_items):
        return set(), path, "canonical checklist ID JSON has duplicate or invalid id entries"
    return ids, path, None


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


def _resolved_deliverable_checks(root: str) -> List[Dict[str, Any]]:
    rel_path = "deliverables_resolved.json"
    path = os.path.join(root, rel_path)
    if not os.path.exists(path):
        return [{
            "rel_path": rel_path,
            "severity": "abort",
            "source": "frozen_deliverables_contract",
            "path": path,
            "ok": False,
            "error": "Missing resolved deliverables contract",
        }]
    try:
        contract = _load_json(path)
    except Exception as exc:
        return [{
            "rel_path": rel_path,
            "severity": "abort",
            "source": "frozen_deliverables_contract",
            "path": path,
            "ok": False,
            "error": f"Could not parse resolved deliverables contract: {exc}",
        }]

    checks: List[Dict[str, Any]] = []
    pending = contract.get("pending_rules") or []
    checks.append({
        "rel_path": rel_path + ":pending_rules",
        "severity": "abort",
        "source": "frozen_deliverables_contract",
        "path": path,
        "ok": contract.get("status") == "resolved" and not pending,
        "status": contract.get("status"),
        "pending_rules": pending,
    })

    for item in contract.get("resolved") or []:
        declared = item.get("path", "<missing>")
        full_path = item.get("absolute_path")
        kind = item.get("type", "file")
        record = {
            "rel_path": declared,
            "severity": "abort",
            "source": "frozen_deliverables_contract",
            "path": full_path,
            "declared_type": kind,
            "rule_id": item.get("rule_id"),
        }
        try:
            if not isinstance(full_path, str) or not full_path:
                raise ValueError("missing absolute_path")
            if kind == "glob":
                matches = [candidate for candidate in glob.glob(full_path) if os.path.getsize(candidate) > 0]
                record.update({"ok": bool(matches), "matched_paths": matches})
            elif kind == "directory":
                record["ok"] = os.path.isdir(full_path)
            elif kind == "nonempty_directory":
                entries = os.listdir(full_path) if os.path.isdir(full_path) else []
                record.update({"ok": bool(entries), "entry_count": len(entries)})
            elif kind == "json":
                _load_json(full_path)
                record.update(_exists_nonempty(full_path))
            elif kind == "jsonl":
                with open(full_path, "r", encoding="utf-8-sig") as handle:
                    lines = [line for line in handle if line.strip()]
                for line in lines:
                    json.loads(line)
                record.update({
                    "ok": bool(lines),
                    "exists": True,
                    "size": os.path.getsize(full_path),
                    "record_count": len(lines),
                })
            elif kind == "executable":
                record.update(_exists_nonempty(full_path))
                record["executable"] = os.access(full_path, os.X_OK)
                record["ok"] = record["ok"] and record["executable"]
            else:
                record.update(_exists_nonempty(full_path))
        except Exception as exc:
            record.update({"ok": False, "error": str(exc)})
        checks.append(record)
    return checks


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
        ("data/phase7/phase7_validation.json", "abort"),
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
        ("data/phase10/manuscript_trace_map.json", "abort"),
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


def _phase6_weighted_order_checks(root: str) -> List[Dict[str, Any]]:
    rel_path = os.path.join("data", "phase6", "scan_manifest.json")
    path = os.path.join(root, rel_path)
    if not os.path.exists(path):
        return []
    try:
        data = _load_json(path)
    except Exception as exc:
        return [{
            "rel_path": rel_path,
            "severity": "abort",
            "source": "phase6_weighted_order_guard",
            "path": path,
            "ok": False,
            "error": f"Could not parse scan_manifest.json: {exc}",
        }]

    checks: List[Dict[str, Any]] = []
    for op_key, record in sorted(data.items()):
        guard = record.get("weighted_order_guard") if isinstance(record, dict) else None
        missing = []
        if not isinstance(guard, dict):
            missing = ["weighted_order_guard"]
            guard = {}
        for key in ("max_weighted_order", "status", "sm_result_json", "np_result_json"):
            if key not in guard:
                missing.append(key)
        status = guard.get("status")
        max_weighted_order = guard.get("max_weighted_order")
        weighted_ok = isinstance(max_weighted_order, int) and max_weighted_order > 0
        provenance_ok = bool(guard.get("weighted_order_json") or guard.get("manual_recovery_reason"))
        keyword = guard.get("runner_selected_keyword")
        keyword_ok = keyword in {"WEIGHTED", "Weighted"}
        runner_rel = os.path.join("data", "phase6", f"np_{op_key}_scan_result.json")
        runner_path = os.path.join(root, runner_rel)
        runner_weighted_order = None
        runner_keyword = None
        runner_ok = False
        runner_error = None
        if os.path.exists(runner_path):
            try:
                runner = _load_json(runner_path)
                create_process = runner.get("create_process") or {}
                runner_weighted_order = create_process.get("weighted_order")
                runner_keyword = create_process.get("weighted_keyword")
                runner_ok = (
                    runner_weighted_order == max_weighted_order
                    and runner_keyword == keyword
                )
            except Exception as exc:
                runner_error = f"Could not parse runner result: {exc}"
        else:
            runner_error = "Missing Phase 6 scan runner result JSON"
        checks.append({
            "rel_path": f"{rel_path}:{op_key}.weighted_order_guard",
            "severity": "abort",
            "source": "phase6_weighted_order_guard",
            "path": path,
            "ok": (
                not missing
                and status in {"pass", "manual_recovered"}
                and weighted_ok
                and provenance_ok
                and keyword_ok
                and runner_ok
            ),
            "missing_keys": missing,
            "status": status,
            "max_weighted_order": max_weighted_order,
            "has_provenance": provenance_ok,
            "runner_selected_keyword": keyword,
            "runner_result_rel_path": runner_rel,
            "runner_weighted_order": runner_weighted_order,
            "runner_weighted_keyword": runner_keyword,
            "runner_error": runner_error,
        })
    return checks


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
    candidates = [os.path.join(root, path_value)]
    parent = root
    while True:
        next_parent = os.path.dirname(parent)
        if next_parent == parent:
            break
        parent = next_parent
        candidates.append(os.path.join(parent, path_value))
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate
    return candidates[0]


def _has_any_key(data: Dict[str, Any], keys: Iterable[str]) -> bool:
    return any(key in data and data.get(key) not in (None, "", [], {}) for key in keys)


def _algorithm_description_map(data: Any) -> Dict[str, Dict[str, Any]]:
    if not isinstance(data, dict):
        return {}
    algorithms = data.get("algorithms")
    if isinstance(algorithms, dict):
        return {str(k): v for k, v in algorithms.items() if isinstance(v, dict)}
    if isinstance(algorithms, list):
        mapped = {}
        for item in algorithms:
            if isinstance(item, dict):
                key = item.get("algorithm_key") or item.get("key") or item.get("name")
                if key:
                    mapped[str(key)] = item
        return mapped
    metadata_keys = {
        "schema_version",
        "created_at",
        "anchor_operator",
        "anchor_model",
        "notes",
    }
    return {
        str(k): v
        for k, v in data.items()
        if k not in metadata_keys and isinstance(v, dict)
    }


def _csv_has_columns(path: str, required_columns: Iterable[str]) -> Dict[str, Any]:
    result = _exists_nonempty(path)
    if not result["ok"]:
        result["columns"] = []
        result["missing_columns"] = list(required_columns)
        return result
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            columns = next(reader, [])
    except Exception as exc:
        result["ok"] = False
        result["error"] = f"Could not read CSV header: {exc}"
        result["columns"] = []
        result["missing_columns"] = list(required_columns)
        return result
    normalized = {col.strip() for col in columns}
    missing = [col for col in required_columns if col not in normalized]
    result["ok"] = result["ok"] and not missing
    result["columns"] = columns
    result["missing_columns"] = missing
    return result


def _phase7_content_checks(root: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    operators = _operators(root)
    algorithms = _algorithm_names(root)

    feature_rel = os.path.join("data", "phase7", "feature_schema.json")
    feature_path = os.path.join(root, feature_rel)
    if os.path.exists(feature_path):
        try:
            data = _load_json(feature_path)
            features = data.get("features")
            preprocessing = data.get("preprocessing")
            if not isinstance(features, list):
                features = []
            bad_features = []
            for idx, feature in enumerate(features):
                if not isinstance(feature, dict):
                    bad_features.append({"index": idx, "error": "not an object"})
                    continue
                missing = []
                if not _has_any_key(feature, ("index", "idx", "feature_index")):
                    missing.append("index")
                if not _has_any_key(feature, ("unit", "units")):
                    missing.append("unit")
                if not _has_any_key(feature, ("definition", "physical_definition", "description")):
                    missing.append("definition")
                if not _has_any_key(feature, ("particle_assignment", "particle", "source_particle")):
                    missing.append("particle_assignment")
                if not _has_any_key(feature, ("ordering_rule", "order", "sorting_rule")):
                    missing.append("ordering_rule")
                if missing:
                    bad_features.append({"index": idx, "missing": missing})
            checks.append({
                "rel_path": feature_rel,
                "severity": "abort",
                "source": "phase7_feature_schema_content",
                "path": feature_path,
                "ok": bool(features) and not bad_features and isinstance(preprocessing, dict) and bool(preprocessing),
                "feature_count": len(features),
                "bad_features": bad_features,
                "has_preprocessing": isinstance(preprocessing, dict) and bool(preprocessing),
            })
        except Exception as exc:
            checks.append({
                "rel_path": feature_rel,
                "severity": "abort",
                "source": "phase7_feature_schema_content",
                "path": feature_path,
                "ok": False,
                "error": f"Could not parse feature_schema.json: {exc}",
            })

    comparison_rel = os.path.join("data", "phase7", "algorithm_comparison.json")
    comparison_path = os.path.join(root, comparison_rel)
    if os.path.exists(comparison_path):
        try:
            data = _load_json(comparison_path)
            anchor = data.get("anchor") or {}
            bad = []
            for alg, record in sorted(anchor.items()):
                if not isinstance(record, dict):
                    bad.append({"algorithm": alg, "error": "record is not an object"})
                    continue
                auc = record.get("auc")
                try:
                    auc_ok = 0.5 < float(auc) <= 1.0
                except (TypeError, ValueError):
                    auc_ok = False
                missing = [
                    key for key in ("algorithm_path", "score_definition")
                    if record.get(key) in (None, "", [], {})
                ]
                if not auc_ok or missing:
                    bad.append({"algorithm": alg, "auc": auc, "auc_ok": auc_ok, "missing": missing})
            checks.append({
                "rel_path": comparison_rel,
                "severity": "abort",
                "source": "phase7_algorithm_comparison_content",
                "path": comparison_path,
                "ok": bool(anchor) and not bad,
                "algorithm_count": len(anchor),
                "bad_records": bad,
            })
        except Exception as exc:
            checks.append({
                "rel_path": comparison_rel,
                "severity": "abort",
                "source": "phase7_algorithm_comparison_content",
                "path": comparison_path,
                "ok": False,
                "error": f"Could not parse algorithm_comparison.json: {exc}",
            })

    desc_rel = os.path.join("data", "phase7", "algorithm_descriptions.json")
    desc_path = os.path.join(root, desc_rel)
    if os.path.exists(desc_path):
        try:
            desc_map = _algorithm_description_map(_load_json(desc_path))
            missing_algs = [alg for alg in algorithms if alg not in desc_map]
            bad = []
            for alg in algorithms:
                record = desc_map.get(alg, {})
                missing = []
                if not _has_any_key(record, ("hyperparameters", "params")):
                    missing.append("hyperparameters")
                if not _has_any_key(record, ("train_test_split", "split")):
                    missing.append("train_test_split")
                if not _has_any_key(record, ("random_seed", "seed")):
                    missing.append("random_seed")
                if not _has_any_key(record, ("score_definition", "score")):
                    missing.append("score_definition")
                if not _has_any_key(record, ("pseudocode", "pseudo_code")):
                    missing.append("pseudocode")
                if missing:
                    bad.append({"algorithm": alg, "missing": missing})
            checks.append({
                "rel_path": desc_rel,
                "severity": "abort",
                "source": "phase7_algorithm_descriptions_content",
                "path": desc_path,
                "ok": bool(algorithms) and not missing_algs and not bad,
                "missing_algorithms": missing_algs,
                "bad_records": bad,
            })
        except Exception as exc:
            checks.append({
                "rel_path": desc_rel,
                "severity": "abort",
                "source": "phase7_algorithm_descriptions_content",
                "path": desc_path,
                "ok": False,
                "error": f"Could not parse algorithm_descriptions.json: {exc}",
            })

    validation_rel = os.path.join("data", "phase7", "phase7_validation.json")
    validation_path = os.path.join(root, validation_rel)
    if os.path.exists(validation_path):
        try:
            data = _load_json(validation_path)
            checks_list = data.get("checks") if isinstance(data.get("checks"), list) else []
            present_ids = {item.get("id") for item in checks_list if isinstance(item, dict)}
            missing_ids = sorted(PHASE7_VALIDATION_CHECK_IDS - present_ids)
            failed = data.get("failed_checks") or [
                item for item in checks_list
                if isinstance(item, dict) and item.get("status") not in {"pass", "present"}
            ]
            checks.append({
                "rel_path": validation_rel,
                "severity": "abort",
                "source": "phase7_validation_gate",
                "path": validation_path,
                "ok": data.get("status") == "pass" and not missing_ids and not failed,
                "status": data.get("status"),
                "missing_check_ids": missing_ids,
                "failed_checks": failed,
            })
        except Exception as exc:
            checks.append({
                "rel_path": validation_rel,
                "severity": "abort",
                "source": "phase7_validation_gate",
                "path": validation_path,
                "ok": False,
                "error": f"Could not parse phase7_validation.json: {exc}",
            })

    required_score_columns = ["event_index", "score", "label", "source_csv"]
    for alg in algorithms:
        rels = [os.path.join("data", "phase7", "scores", f"{alg}_sm_scores.csv")]
        rels.extend(os.path.join("data", "phase7", "scores", f"{alg}_np_{op}_scores.csv") for op in operators)
        for rel in rels:
            path = os.path.join(root, rel)
            checks.append({
                "rel_path": rel,
                "severity": "abort",
                "source": "phase7_score_csv_schema",
                **_csv_has_columns(path, required_score_columns),
            })

    return checks


def _phase10_manuscript_checks(root: str, required_ids_json: Optional[str] = None) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    required_checklist_ids, checklist_reference_path, checklist_reference_error = _phase10_required_checklist_ids(
        required_ids_json
    )
    checks.append({
        "rel_path": os.path.join("reference", "manuscript-checklist-required-ids.json") + ":required_ids",
        "severity": "abort",
        "source": "phase10_required_checklist_source",
        "path": checklist_reference_path,
        "ok": checklist_reference_error is None and bool(required_checklist_ids),
        "error": checklist_reference_error,
        "required_id_count": len(required_checklist_ids),
    })

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
    checklist_items_by_id: Dict[str, Dict[str, Any]] = {}
    missing_checklist_ids: List[str] = []
    bad_checklist_items: List[Dict[str, Any]] = []
    if os.path.exists(checklist_path):
        try:
            checklist = _load_json(checklist_path)
            items = checklist.get("items")
            draft_path = checklist.get("draft_path")
            if isinstance(items, list):
                for item in items:
                    if not isinstance(item, dict):
                        bad_checklist_items.append({"id": "<non_object>", "error": "item is not an object"})
                        continue
                    item_id = item.get("id")
                    if item_id:
                        checklist_items_by_id[str(item_id)] = item
                    status = item.get("status")
                    if status not in {"present", "missing"}:
                        bad_checklist_items.append({"id": item_id or "<missing>", "error": f"bad status {status!r}"})
                    if status == "present" and not item.get("manuscript_location"):
                        bad_checklist_items.append({"id": item_id or "<missing>", "error": "present item lacks manuscript_location"})
            missing_checklist_ids = sorted(required_checklist_ids - set(checklist_items_by_id))
            checks.append({
                "rel_path": checklist_rel,
                "severity": "abort",
                "source": "phase10_checklist_schema",
                "path": checklist_path,
                "ok": (
                    isinstance(items, list)
                    and bool(items)
                    and bool(draft_path)
                    and not missing_checklist_ids
                    and not bad_checklist_items
                ),
                "missing_required_ids": missing_checklist_ids,
                "bad_items": bad_checklist_items,
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

    trace_rel = os.path.join("data", "phase10", "manuscript_trace_map.json")
    trace_path = os.path.join(root, trace_rel)
    trace_items_by_id: Dict[str, Dict[str, Any]] = {}
    missing_trace_ids: List[str] = []
    bad_trace_items: List[Dict[str, Any]] = []
    if os.path.exists(trace_path):
        try:
            trace = _load_json(trace_path)
            raw_items = trace.get("items")
            if isinstance(raw_items, dict):
                trace_items_by_id = {str(k): v for k, v in raw_items.items() if isinstance(v, dict)}
            elif isinstance(raw_items, list):
                for item in raw_items:
                    if isinstance(item, dict) and item.get("id"):
                        trace_items_by_id[str(item["id"])] = item
            missing_trace_ids = sorted(required_checklist_ids - set(trace_items_by_id))
            for item_id, item in sorted(trace_items_by_id.items()):
                status = item.get("status") or checklist_items_by_id.get(item_id, {}).get("status")
                if item_id in required_checklist_ids and status == "present":
                    if not item.get("evidence_path"):
                        bad_trace_items.append({"id": item_id, "error": "present item lacks evidence_path"})
                    if not item.get("manuscript_location"):
                        bad_trace_items.append({"id": item_id, "error": "present item lacks manuscript_location"})
            checks.append({
                "rel_path": trace_rel,
                "severity": "abort",
                "source": "phase10_trace_map_schema",
                "path": trace_path,
                "ok": bool(trace_items_by_id) and not missing_trace_ids and not bad_trace_items,
                "missing_required_ids": missing_trace_ids,
                "bad_items": bad_trace_items,
                "item_count": len(trace_items_by_id),
            })
        except Exception as exc:
            checks.append({
                "rel_path": trace_rel,
                "severity": "abort",
                "source": "phase10_trace_map_schema",
                "path": trace_path,
                "ok": False,
                "error": f"Could not parse manuscript_trace_map.json: {exc}",
            })

    validation_rel = os.path.join("data", "phase10", "manuscript_validation.json")
    validation_path = os.path.join(root, validation_rel)
    validation: Dict[str, Any] = {}
    if os.path.exists(validation_path):
        try:
            validation = _load_json(validation_path)
            status = validation.get("status")
            major_issues = validation.get("major_issues") or []
            validation_required = {
                "status": str,
                "drafts_written": int,
                "max_revisions": int,
                "checklist_path": str,
                "major_issues": list,
                "minor_issues": list,
                "continued_to_cleanup": bool,
            }
            validation_bad_fields = []
            for key, expected_type in validation_required.items():
                if key not in validation:
                    validation_bad_fields.append({"field": key, "error": "missing"})
                elif not isinstance(validation.get(key), expected_type):
                    validation_bad_fields.append({
                        "field": key,
                        "error": f"expected {expected_type.__name__}",
                    })
            checklist_path_value = validation.get("checklist_path")
            checklist_path_exists = False
            if isinstance(checklist_path_value, str) and checklist_path_value:
                checklist_resolved = _resolve_inside_root(root, checklist_path_value)
                checklist_path_exists = os.path.exists(checklist_resolved)
            checklist_has_missing_required = any(
                (checklist_items_by_id.get(item_id) or {}).get("status") == "missing"
                for item_id in required_checklist_ids
            )
            pass_consistent = (
                status != "pass"
                or (not major_issues and not missing_checklist_ids and not missing_trace_ids and not checklist_has_missing_required)
            )
            remaining_consistent = status != "issues_remaining" or validation.get("continued_to_cleanup") is True
            checks.append({
                "rel_path": validation_rel,
                "severity": "abort",
                "source": "phase10_validation_schema",
                "path": validation_path,
                "ok": (
                    status in {"pass", "issues_remaining"}
                    and not validation_bad_fields
                    and checklist_path_exists
                    and pass_consistent
                    and remaining_consistent
                ),
                "status": status,
                "bad_fields": validation_bad_fields,
                "checklist_path_exists": checklist_path_exists,
                "major_issue_count": len(major_issues) if isinstance(major_issues, list) else "non_list",
                "pass_consistent": pass_consistent,
                "issues_remaining_consistent": remaining_consistent,
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


def audit_expected_outputs(
    workdir: str,
    run_dir: Optional[str] = None,
    phase10_required_ids_json: Optional[str] = None,
) -> Dict[str, Any]:
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
    checks.extend(_phase6_weighted_order_checks(root))
    checks.extend(_phase7_content_checks(root))
    checks.extend(_phase9_strategy_checks(root))
    checks.extend(_cleanup_log_checks(root))
    checks.extend(_phase10_manuscript_checks(root, required_ids_json=phase10_required_ids_json))

    checks.extend(_manuscript_format_checks(root))
    checks.extend(_resolved_deliverable_checks(root))

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
    parser.add_argument(
        "--phase10-required-ids-json",
        default=None,
        help="Optional path to reference/manuscript-checklist-required-ids.json",
    )
    args = parser.parse_args()

    report = audit_expected_outputs(
        args.workdir,
        run_dir=args.run_dir,
        phase10_required_ids_json=args.phase10_required_ids_json,
    )
    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)
            f.write("\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] in {"PASS", "WARN"} else 2


if __name__ == "__main__":
    sys.exit(main())

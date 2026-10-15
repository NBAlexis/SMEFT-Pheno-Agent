#!/usr/bin/env python3
"""Manifest-driven output audit for the SMEFT-ML workflow."""

from __future__ import annotations

import argparse
import ast
from bisect import bisect_right
import csv
import fnmatch
import glob
import hashlib
import json
import math
import os
import re
import sys
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

try:
    from .research_contract import resolve_contract
    from .calculate_shared_f5_background import MAX_ADDITIONAL_ANCHOR_ROUNDS
    from .extract_cross_section import extract_cross_section
except ImportError:  # Direct script execution.
    from research_contract import resolve_contract
    from calculate_shared_f5_background import MAX_ADDITIONAL_ANCHOR_ROUNDS
    from extract_cross_section import extract_cross_section


PHASE7_VALIDATION_CHECK_IDS = {
    "feature_schema_complete",
    "algorithm_keys_consistent",
    "algorithm_descriptions_complete",
    "public_csv_complete",
    "score_csv_complete",
    "plots_complete",
}

CROSS_FILE_ACCEPTANCE_IMPLEMENTATIONS = {
    "phase3.complete_coefficient_loop",
    "phase4.mg5_delphes_lhco_and_event_minimum",
    "phase5.mg5_delphes_lhco_and_event_minimum",
    "phase6.complete_scan_matrix",
    "phase7.complete_algorithm_set",
    "phase8.numerical_content",
    "phase9.numerical_content",
    "phase10.analysis_notes_trace",
    "phase11.replay_package_static_checks",
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


def _phase10_required_items(override_path: Optional[str] = None) -> Tuple[List[Dict[str, Any]], str, Optional[str]]:
    path = _phase10_required_items_path(override_path)
    if not os.path.exists(path):
        return [], path, "Missing canonical checklist ID JSON"
    try:
        data = _load_json(path)
    except Exception as exc:
        return [], path, f"Could not parse canonical checklist ID JSON: {exc}"
    items = data.get("required_items")
    if not isinstance(items, list) or not items or any(
        not isinstance(item, dict)
        or not isinstance(item.get("id"), str)
        or not item.get("id")
        or not isinstance(item.get("required_content"), str)
        or not item.get("required_content")
        for item in items
    ):
        return [], path, "canonical checklist JSON has invalid required_items"
    if len({item["id"] for item in items}) != len(items):
        return [], path, "canonical checklist JSON has duplicate required item IDs"
    return items, path, None


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _result_root(workdir: str, run_dir: Optional[str]) -> str:
    if run_dir:
        return os.path.join(workdir, "results", run_dir)
    return os.path.join(workdir, "results")


def _exists_nonempty(path: str) -> Dict[str, Any]:
    result = {
        "path": path,
        "exists": os.path.exists(path),
        "size": os.path.getsize(path) if os.path.exists(path) else 0,
        "ok": os.path.exists(path) and os.path.getsize(path) > 0,
    }
    if not result["ok"]:
        result.update({
            "failure_code": "file_missing_or_empty",
            "failure_reason": f"Required file is missing or empty: {path}",
        })
    return result


def _path_is_within(path: str, base: str) -> bool:
    try:
        return os.path.commonpath([os.path.abspath(path), os.path.abspath(base)]) == os.path.abspath(base)
    except ValueError:
        return False


def _manifest_reference_path(root: str, value: str) -> str:
    if os.path.isabs(value):
        return os.path.abspath(value)
    normalized = value.replace("\\", "/").lstrip("./")
    current = os.path.abspath(root)
    results_root = None
    while True:
        if os.path.basename(current).lower() == "results":
            results_root = current
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    if normalized.split("/", 1)[0].lower() == "results" and results_root:
        return os.path.abspath(os.path.join(os.path.dirname(results_root), *normalized.split("/")))
    return os.path.abspath(os.path.join(root, *normalized.split("/")))


def _set_failure(record: Dict[str, Any], code: str, reason: str) -> None:
    record.update({"ok": False, "failure_code": code, "failure_reason": reason})


def _validate_declared_artifact(
    path: str,
    kind: str,
    record: Dict[str, Any],
    specification: Optional[Dict[str, Any]] = None,
) -> None:
    specification = specification or {}
    if kind == "glob":
        matches = [candidate for candidate in glob.glob(path) if os.path.isfile(candidate)]
        nonempty = [candidate for candidate in matches if os.path.getsize(candidate) > 0]
        record.update({"matched_paths": nonempty, "match_count": len(nonempty)})
        if not nonempty:
            _set_failure(record, "glob_no_nonempty_match", f"No non-empty file matches {path}")
        else:
            record["ok"] = True
        return
    if kind == "directory":
        if not os.path.isdir(path):
            _set_failure(record, "directory_missing", f"Required directory does not exist: {path}")
        else:
            record["ok"] = True
        return
    if kind == "nonempty_directory":
        entries = os.listdir(path) if os.path.isdir(path) else []
        record["entry_count"] = len(entries)
        if not entries:
            _set_failure(record, "directory_empty_or_missing", f"Required directory is missing or empty: {path}")
        else:
            record["ok"] = True
        return
    if not os.path.isfile(path):
        _set_failure(record, "file_missing", f"Required {kind} file does not exist: {path}")
        return
    size = os.path.getsize(path)
    record.update({"exists": True, "size": size})
    if size <= 0:
        _set_failure(record, "file_empty", f"Required {kind} file is empty: {path}")
        return

    if kind == "json":
        with open(path, "r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
        json_type = specification.get("json_type")
        expected_type = {"object": dict, "array": list}.get(json_type)
        if expected_type is not None and not isinstance(data, expected_type):
            raise ValueError(f"JSON must be a {json_type}")
        required_keys = specification.get("required_keys") or []
        if required_keys:
            if not isinstance(data, dict):
                raise ValueError("required_keys can only be checked on a JSON object")
            missing = [key for key in required_keys if key not in data]
            if missing:
                raise ValueError(f"JSON is missing required keys: {missing}")
        required_values = specification.get("required_values") or {}
        if required_values:
            if not isinstance(data, dict):
                raise ValueError("required_values can only be checked on a JSON object")
            mismatches = {
                key: {"expected": value, "actual": data.get(key)}
                for key, value in required_values.items()
                if data.get(key) != value
            }
            if mismatches:
                raise ValueError(f"JSON has incorrect fixed values: {mismatches}")
        if isinstance(data, dict) and len(data) < int(specification.get("min_properties", 0)):
            raise ValueError(
                f"JSON object has {len(data)} properties; expected at least "
                f"{specification.get('min_properties')}"
            )
        if isinstance(data, list) and len(data) < int(specification.get("min_items", 0)):
            raise ValueError(
                f"JSON array has {len(data)} items; expected at least {specification.get('min_items')}"
            )
    elif kind == "jsonl":
        record_count = 0
        with open(path, "r", encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"JSONL record {line_number} is invalid: {exc}") from exc
                record_count += 1
        if not record_count:
            raise ValueError("JSONL file has no records")
        record["record_count"] = record_count
    elif kind == "csv":
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle)
            header = next(reader, [])
            data_rows = sum(1 for row in reader if any(cell.strip() for cell in row))
        if not header or not any(cell.strip() for cell in header):
            raise ValueError("CSV header is missing or empty")
        min_data_rows = int(specification.get("min_data_rows", 1))
        if data_rows < min_data_rows:
            raise ValueError(
                f"CSV contains {data_rows} data rows; expected at least {min_data_rows}"
            )
        required_columns = specification.get("required_columns") or []
        missing_columns = [column for column in required_columns if column not in header]
        if missing_columns:
            raise ValueError(f"CSV is missing required columns: {missing_columns}")
        record.update({"columns": header, "data_rows": data_rows})
    elif kind == "pdf":
        with open(path, "rb") as handle:
            signature = handle.read(8)
            handle.seek(max(0, size - 2048))
            trailer = handle.read()
        if not signature.startswith(b"%PDF-"):
            raise ValueError("PDF signature %PDF- is missing")
        if b"%%EOF" not in trailer:
            raise ValueError("PDF end marker %%EOF is missing")
    elif kind == "lhco":
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            has_event_header = any(line.lstrip().startswith("0") for line in handle if line.strip())
        if not has_event_header:
            raise ValueError("LHCO file has no event header line beginning with 0")
    elif kind == "python":
        with open(path, "r", encoding="utf-8-sig") as handle:
            ast.parse(handle.read(), filename=path)
    elif kind == "markdown":
        with open(path, "r", encoding="utf-8-sig") as handle:
            if not handle.read().strip():
                raise ValueError("Markdown file contains no text")
    elif kind == "text":
        with open(path, "r", encoding="utf-8-sig") as handle:
            if not handle.read().strip():
                raise ValueError("Text file contains no text")
    elif kind == "html":
        with open(path, "r", encoding="utf-8-sig") as handle:
            content = handle.read().strip().lower()
        if not content:
            raise ValueError("HTML file contains no text")
        if "<html" not in content or "</html>" not in content:
            raise ValueError("HTML file is missing opening or closing html element")
    elif kind == "executable":
        if not os.access(path, os.X_OK):
            raise ValueError("File is not executable on this target")
        record["executable"] = True
    elif kind not in {"file", "model"}:
        raise ValueError(f"Unknown deliverable type: {kind}")
    record["ok"] = True


def _resolved_deliverable_checks(
    root: str,
    include_final_artifacts: bool = True,
    contract_override: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    rel_path = "deliverables_resolved.json"
    path = os.path.join(root, rel_path)
    if contract_override is None and not os.path.exists(path):
        return [{
            "rel_path": rel_path,
            "severity": "abort",
            "source": "frozen_deliverables_contract",
            "path": path,
            "ok": False,
            "error": "Missing resolved deliverables contract",
        }]
    try:
        contract = contract_override if contract_override is not None else _load_json(path)
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
    contract_root_value = contract.get("run_root")
    results_dir_value = contract.get("results_dir")
    contract_root = (
        os.path.abspath(contract_root_value)
        if isinstance(contract_root_value, str) and contract_root_value
        else ""
    )
    results_dir = (
        os.path.abspath(results_dir_value)
        if isinstance(results_dir_value, str) and results_dir_value
        else ""
    )
    root = os.path.abspath(root)
    current = root
    expected_results_dir = None
    while True:
        if os.path.basename(current).lower() == "results":
            expected_results_dir = current
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    if expected_results_dir is None:
        expected_results_dir = root
    root_ok = contract_root == root
    checks.append({
        "rel_path": rel_path + ":run_root",
        "severity": "abort",
        "source": "frozen_deliverables_contract",
        "path": path,
        "ok": root_ok,
        "declared_run_root": contract_root,
        "expected_run_root": root,
        "failure_reason": None if root_ok else "Resolved contract belongs to a different run root",
    })
    results_dir_ok = expected_results_dir is not None and results_dir == expected_results_dir
    checks.append({
        "rel_path": rel_path + ":results_dir",
        "severity": "abort",
        "source": "frozen_deliverables_contract",
        "path": path,
        "ok": results_dir_ok,
        "declared_results_dir": results_dir,
        "expected_results_dir": expected_results_dir,
        "failure_reason": None if results_dir_ok else "Resolved contract declares the wrong global results directory",
    })
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

    deferred = []
    for item in contract.get("resolved") or []:
        if str(item.get("phase")) == "12" and not include_final_artifacts:
            deferred.append(item.get("path"))
            continue
        declared = item.get("path", "<missing>")
        stored_path = item.get("absolute_path")
        kind = item.get("type", "file")
        base = expected_results_dir if item.get("scope") == "global_results" else root
        full_path = os.path.abspath(os.path.join(base, str(declared)))
        record = {
            "rel_path": declared,
            "severity": "abort",
            "source": "frozen_deliverables_contract",
            "path": full_path,
            "declared_type": kind,
            "rule_id": item.get("rule_id"),
            "phase": item.get("phase"),
        }
        try:
            if not isinstance(declared, str) or not declared:
                raise ValueError("Resolved item is missing its declared relative path")
            if item.get("scope") == "global_results" and not expected_results_dir:
                raise ValueError("Could not infer the global results directory from the run root")
            if not base:
                raise ValueError("Resolved item has no valid scope base")
            if not _path_is_within(full_path, base):
                raise ValueError(f"Declared path escapes its {item.get('scope')} base: {declared}")
            if not isinstance(stored_path, str) or os.path.abspath(stored_path) != full_path:
                raise ValueError(
                    f"Stored absolute_path does not match the path recomputed from scope and declaration: {stored_path!r}"
                )
            _validate_declared_artifact(full_path, kind, record, item)
        except Exception as exc:
            _set_failure(record, "acceptance_check_failed", str(exc))
        checks.append(record)
    if deferred:
        checks.append({
            "rel_path": "phase12.audit:deferred_final_artifacts",
            "severity": "info",
            "source": "frozen_deliverables_contract",
            "path": root,
            "ok": True,
            "deferred": True,
            "deferred_paths": deferred,
            "reason": "Final audit artifacts are checked after both audit files have been written",
        })
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
        ("data/phase3/model_status.json", "abort"),
    ]
    if operators:
        fixed.extend([
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
        ])
    else:
        fixed.append(("data/phase3/phase3_report.txt", "abort"))
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

        operators = _operators(root) or []
        expected_units = (
            ["sm"] + [f"np_{operator}" for operator in operators]
            if phase == "phase5"
            else operators
        )
        if not isinstance(data.get("units"), dict):
            checks.append({
                "rel_path": rel_path,
                "severity": "abort",
                "source": "recovery_metadata",
                "path": path,
                "ok": False,
                "error": "event_count_recovery.json must contain a units object covering the full phase",
            })
            continue

        units = data["units"]
        actual_units = set(str(value) for value in units)
        missing_units = sorted(set(expected_units) - actual_units)
        extra_units = sorted(actual_units - set(expected_units))
        declared_required = [str(value) for value in data.get("required_units") or []]
        aggregate_ok = (
            not missing_units
            and not extra_units
            and declared_required == expected_units
            and data.get("status") == "accepted"
            and not data.get("missing_units")
            and not data.get("incomplete_units")
        )
        checks.append({
            "rel_path": rel_path + ":unit_coverage",
            "severity": "abort",
            "source": "recovery_metadata",
            "path": path,
            "ok": aggregate_ok,
            "expected_units": expected_units,
            "actual_units": sorted(actual_units),
            "missing_units": missing_units,
            "extra_units": extra_units,
            "declared_required_units": declared_required,
            "aggregate_status": data.get("status"),
        })

        for unit_name in expected_units:
            unit_data = units.get(unit_name)
            if not isinstance(unit_data, dict):
                continue
            status = unit_data.get("status")
            if status != "accepted":
                checks.append({
                    "rel_path": f"{rel_path}:{unit_name}",
                    "severity": "abort",
                    "source": "recovery_metadata",
                    "path": path,
                    "ok": False,
                    "error": f"Recovery unit {unit_name} is not accepted: {status!r}",
                })
                continue
            profile_lines = {
                "default": [],
                "sde2_hs0": ["set sde_strategy = 2"],
                "sde2_hs1": ["set sde_strategy = 2", "set hard_survey = 1"],
                "sde2_hs2": ["set sde_strategy = 2", "set hard_survey = 2"],
                # legacy names kept so older recovery metadata still validates
                "sde0_hs0": ["set sde_strategy = 2"],
                "sde0_hs1": ["set sde_strategy = 2", "set hard_survey = 1"],
                "sde0_hs2": ["set sde_strategy = 2", "set hard_survey = 2"],
            }
            for attempt in unit_data.get("attempts") or []:
                if not isinstance(attempt, dict):
                    continue
                profile = attempt.get("survey_profile")
                attempt_status = attempt.get("status")
                result = attempt.get("result") if isinstance(attempt.get("result"), dict) else {}
                launch = result.get("launch") if isinstance(result.get("launch"), dict) else {}
                order_path = launch.get("order_file_path")
                errors = []
                if profile not in profile_lines:
                    errors.append(f"unknown survey_profile: {profile!r}")
                if attempt_status == "failed" and not launch:
                    if not attempt.get("error"):
                        errors.append("failed pre-launch attempt lacks exact error text")
                    order_text = ""
                else:
                    if not order_path or not os.path.isfile(order_path):
                        errors.append(f"launch order file is missing: {order_path!r}")
                        order_text = ""
                    else:
                        with open(order_path, "r", encoding="utf-8-sig", errors="replace") as handle:
                            order_text = handle.read()
                if profile in profile_lines and not (attempt_status == "failed" and not launch):
                    for expected_line in profile_lines[profile]:
                        if expected_line not in order_text:
                            errors.append(f"launch order lacks {expected_line!r}")
                    if profile == "default" and (
                        "set sde_strategy" in order_text or "set hard_survey" in order_text
                    ):
                        errors.append("default profile launch order contains recovery settings")
                checks.append({
                    "rel_path": f"{rel_path}:{unit_name}:attempt_{attempt.get('attempt_index')}",
                    "severity": "abort",
                    "source": "recovery_launch_order",
                    "path": order_path or path,
                    "ok": not errors,
                    "survey_profile": profile,
                    "errors": errors,
                })
            merged_outputs = unit_data.get("merged_outputs")
            if not isinstance(merged_outputs, list) or not merged_outputs:
                checks.append({
                    "rel_path": rel_path,
                    "severity": "abort",
                    "source": "recovery_metadata",
                    "path": path,
                    "ok": False,
                    "error": f"accepted recovery unit {unit_name} has no merged_outputs",
                })
                continue
            for item in merged_outputs:
                label = item.get("label", "<missing>")
                lhco_path = item.get("lhco_path")
                count = int(item.get("loaded_lhco_event_count", 0))
                requested = int(item.get("requested_event_count", unit_data.get("requested_event_count", 0)) or 0)
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

            for warning in unit_data.get("warnings", []):
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
        full_path = _manifest_reference_path(root, result_path)
        rel = os.path.relpath(full_path, root)
        record = {
            "rel_path": rel,
            "severity": "abort",
            "source": "phase3_runner_manifests",
            **_exists_nonempty(full_path),
        }
        if not _path_is_within(full_path, root):
            _set_failure(
                record,
                "phase3_manifest_path_outside_run_root",
                f"Phase 3 runner manifest path escapes the run root: {result_path}",
            )
        elif not record["ok"]:
            _set_failure(
                record,
                "phase3_runner_result_missing",
                f"Phase 3 runner result is missing or empty: {full_path}",
            )
        checks.append(record)
    return checks


def _runner_result_boundary_checks(root: str, phase: str) -> List[Dict[str, Any]]:
    """Verify numerical runner records prove the fixed MG5/Delphes/LHCO chain."""
    result_paths: Set[str] = set()
    operators = _operators(root)
    if phase == "3":
        status_path = os.path.join(root, "data", "phase3", "model_status.json")
        if os.path.exists(status_path):
            try:
                for item in _iter_json_objects(_load_json(status_path)):
                    for key in ("create_np_result_json", "result_json", "result_json_path", "runner_result_json"):
                        value = item.get(key)
                        if isinstance(value, str) and value:
                            result_paths.add(_manifest_reference_path(root, value))
            except Exception:
                return []  # The Phase 3 manifest checks report the parse error.
    elif phase == "5":
        result_paths.add(os.path.join(root, "data", "phase5", "sm_result.json"))
        result_paths.update(
            os.path.join(root, "data", "phase5", f"np_{operator}_result.json")
            for operator in operators
        )
    elif phase == "6":
        result_paths.update(
            os.path.join(root, "data", "phase6", f"np_{operator}_scan_result.json")
            for operator in operators
        )
    elif phase == "4":
        result_paths.add(os.path.join(root, "data", "phase4", "sm_baseline_result.json"))
    elif phase == "8":
        background_path = os.path.join(root, "data", "phase8", "shared_f5_background.json")
        if os.path.exists(background_path):
            try:
                background = _load_json(background_path)
                for item in background.get("additional_anchor_f5_sources") or []:
                    if isinstance(item, dict) and isinstance(item.get("runner_result_json"), str):
                        result_paths.add(
                            _manifest_reference_path(root, item["runner_result_json"])
                        )
            except Exception:
                return []  # The Phase 8 shared-background checks report the parse error.
    else:
        return []

    config_path = os.path.join(_global_results_root(root), "run_config.json")
    try:
        config = _load_json(config_path)
    except Exception:
        config = {}
    default_count_key = {
        "3": "nev_phase3",
        "4": "nev_phase4",
        "5": None,
        "6": "nev_scan",
        "8": "nev_scan",
    }[phase]
    locked_counts = config.get("locked_event_counts") or {}
    checks: List[Dict[str, Any]] = []
    for path in sorted(result_paths):
        if not os.path.isfile(path):
            continue  # Frozen path checks report missing result files.
        rel = os.path.relpath(path, root)
        errors: List[str] = []
        try:
            data = _load_json(path)
            mode = data.get("process_mode")
            if data.get("event_generator") != "MadGraph5":
                errors.append("event_generator must be MadGraph5")
            if mode != "create_np":
                if data.get("status") != "completed":
                    errors.append("numerical runner result must have status=completed")
                if data.get("detector_simulation") != "Delphes":
                    errors.append("detector_simulation must be Delphes")
                if data.get("analysis_event_format") != "LHCO_from_Delphes_ROOT":
                    errors.append("analysis_event_format must be LHCO_from_Delphes_ROOT")
                card = data.get("delphes_card")
                if not isinstance(card, str) or not card.strip():
                    errors.append("delphes_card must be non-empty")
                elif config and card != config.get("delphes_card"):
                    errors.append("delphes_card differs from run_config")
                count_key = default_count_key
                if phase == "5":
                    count_key = "nev_sm" if mode == "pure_sm" else "nev_np"
                expected_count = locked_counts.get(count_key) if count_key else None
                nevents = data.get("nevents")
                if not isinstance(nevents, int) or isinstance(nevents, bool):
                    errors.append("nevents must be an integer")
                elif isinstance(expected_count, int) and nevents < expected_count:
                    errors.append(
                        f"nevents {nevents} is below the locked per-run minimum {expected_count}"
                    )
                outputs = data.get("outputs")
                if not isinstance(outputs, list) or not outputs:
                    errors.append("numerical runner result must contain outputs")
                else:
                    for index, output in enumerate(outputs):
                        if not isinstance(output, dict):
                            errors.append(f"outputs[{index}] must be an object")
                            continue
                        cross_section = output.get("cross_section_pb")
                        if not _finite_number(cross_section) or float(cross_section) < 0.0:
                            errors.append(f"outputs[{index}].cross_section_pb must be finite and non-negative")
                        elif float(cross_section) > 0.0:
                            lhco_path = output.get("lhco_path")
                            loaded = output.get("loaded_lhco_event_count")
                            resolved_lhco = (
                                _manifest_reference_path(root, lhco_path)
                                if isinstance(lhco_path, str)
                                else ""
                            )
                            if not resolved_lhco or not os.path.isfile(resolved_lhco) or os.path.getsize(resolved_lhco) <= 0:
                                errors.append(f"outputs[{index}] positive cross-section lacks non-empty Delphes LHCO")
                            if not isinstance(loaded, int) or isinstance(loaded, bool) or loaded <= 0:
                                errors.append(f"outputs[{index}] positive cross-section lacks a positive loaded LHCO count")
                            elif isinstance(nevents, int) and loaded < 0.1 * nevents:
                                errors.append(
                                    f"outputs[{index}] loaded LHCO count is below 10% of the requested per-run count"
                                )
        except Exception as exc:
            errors.append(f"could not parse runner result: {exc}")
        checks.append({
            "rel_path": rel + ":fixed_method_boundaries",
            "severity": "abort",
            "source": "mg5_delphes_lhco_and_event_minimum",
            "path": path,
            "ok": not errors,
            "errors": errors,
        })
    return checks


def _global_results_root(root: str) -> str:
    current = os.path.abspath(root)
    while True:
        if os.path.basename(current).lower() == "results":
            return current
        parent = os.path.dirname(current)
        if parent == current:
            return os.path.abspath(root)
        current = parent


def _cross_file_acceptance_definition_checks(
    root: str, phase: Optional[str] = None
) -> List[Dict[str, Any]]:
    path = os.path.join(_global_results_root(root), "deliverables_contract.json")
    if not os.path.exists(path):
        return []
    record: Dict[str, Any] = {
        "rel_path": "deliverables_contract.json:cross_file_acceptance_rules",
        "severity": "abort",
        "source": "cross_file_acceptance_definitions",
        "path": path,
    }
    try:
        template = _load_json(path).get("template") or {}
        rules = template.get("cross_file_acceptance_rules")
        if not isinstance(rules, list):
            raise ValueError("cross_file_acceptance_rules must be a list")
        selected = [
            item for item in rules
            if isinstance(item, dict) and (phase is None or str(item.get("phase")) == str(phase))
        ]
        declared = {item.get("id") for item in selected}
        malformed = [
            item for item in selected
            if not isinstance(item.get("id"), str)
            or not isinstance(item.get("requirements"), list)
            or not item.get("requirements")
        ]
        unimplemented = sorted(declared - CROSS_FILE_ACCEPTANCE_IMPLEMENTATIONS)
        missing_definitions = (
            sorted(CROSS_FILE_ACCEPTANCE_IMPLEMENTATIONS - declared)
            if phase is None
            else []
        )
        record.update({
            "ok": not malformed and not unimplemented and not missing_definitions,
            "phase": phase,
            "declared_ids": sorted(declared),
            "unimplemented_ids": unimplemented,
            "missing_definition_ids": missing_definitions,
            "malformed_rules": malformed,
        })
    except Exception as exc:
        _set_failure(record, "cross_file_acceptance_definitions_invalid", str(exc))
    return [record]


def _phase3_completeness_checks(root: str) -> List[Dict[str, Any]]:
    rel_path = os.path.join("data", "phase3", "model_status.json")
    path = os.path.join(root, rel_path)
    if not os.path.exists(path):
        return []
    record: Dict[str, Any] = {
        "rel_path": rel_path + ":complete_coefficient_loop",
        "severity": "abort",
        "source": "phase3_complete_coefficient_loop",
        "path": path,
    }
    try:
        config = _load_json(os.path.join(_global_results_root(root), "run_config.json"))
        expected_models = [str(model) for model in config.get("models") or []]
        model_status = _load_json(path)
        claims = _load_json(os.path.join(root, "data", "phase3", "operator_claims.json"))
        cross_sections = _load_json(os.path.join(root, "data", "phase3", "cross_sections.json"))
        actual_models = sorted(model_status)
        bad_models = []
        expected_claim_keys = set()
        expected_cross_section_keys = set()
        ordered_claim_keys = [f"o_{index}" for index in range(1, len(claims) + 1)]
        bad_claim_records = [
            key for key, value in claims.items()
            if not isinstance(value, dict)
            or any(field not in value for field in ("model", "anoinput_idx", "name"))
        ]
        for model in expected_models:
            status = model_status.get(model)
            if not isinstance(status, dict):
                bad_models.append({"model": model, "error": "missing model record"})
                continue
            missing = [
                key for key in ("has_feynman_diagrams", "create_np_result_json")
                if key not in status or status.get(key) in (None, "")
            ]
            if status.get("has_feynman_diagrams") is True:
                coefficients = status.get("coefficients")
                expected_count = status.get("coefficient_count")
                tested_count = status.get("tested_count")
                coefficient_errors = []
                if not isinstance(coefficients, dict):
                    coefficient_errors.append("coefficients must be an object")
                    coefficients = {}
                if not isinstance(expected_count, int) or expected_count <= 0:
                    coefficient_errors.append("coefficient_count must be a positive integer")
                if tested_count != expected_count or len(coefficients) != expected_count:
                    coefficient_errors.append(
                        "tested_count and coefficient record count must equal coefficient_count"
                    )
                for name, value in coefficients.items():
                    expected_cross_section_keys.add(f"{model}:{name}")
                    if not isinstance(value, dict) or any(
                        key not in value for key in ("c_default", "sigma", "result_json")
                    ):
                        coefficient_errors.append(
                            f"coefficient {name} must contain c_default, sigma, and result_json"
                        )
                        continue
                    if not _finite_number(value.get("sigma")) or float(value["sigma"]) < 0.0:
                        coefficient_errors.append(f"coefficient {name} sigma must be finite and non-negative")
                    elif float(value["sigma"]) > 0.0:
                        global_idx = value.get("global_idx")
                        operator_key = (
                            str(global_idx)
                            if isinstance(global_idx, str) and str(global_idx).startswith("o_")
                            else f"o_{global_idx}"
                        )
                        expected_claim_keys.add(operator_key)
                        if operator_key not in claims:
                            coefficient_errors.append(
                                f"coefficient {name} has sigma > 0 but {operator_key} is missing from operator_claims.json"
                            )
                if coefficient_errors:
                    bad_models.append({"model": model, "errors": coefficient_errors})
            elif status.get("has_feynman_diagrams") is False:
                if not status.get("no_diagram_reason"):
                    missing.append("no_diagram_reason")
            else:
                missing.append("has_feynman_diagrams must be boolean")
            if missing:
                bad_models.append({"model": model, "missing_or_invalid": missing})
        claim_set_matches = set(claims) == expected_claim_keys
        cross_section_keys_match = set(cross_sections) == expected_cross_section_keys
        anchor_matches = True
        if claims:
            anchor = _load_json(os.path.join(root, "data", "phase3", "anchor.json"))
            first_claim = claims.get("o_1") or {}
            anchor_matches = (
                anchor.get("global_idx") in (1, "1", "o_1")
                and all(anchor.get(key) == first_claim.get(key) for key in ("model", "anoinput_idx", "name"))
            )
        record.update({
            "ok": (
                actual_models == sorted(expected_models)
                and not bad_models
                and claim_set_matches
                and cross_section_keys_match
                and list(claims) == ordered_claim_keys
                and not bad_claim_records
                and anchor_matches
            ),
            "expected_models": expected_models,
            "actual_models": actual_models,
            "bad_models": bad_models,
            "expected_claim_keys": sorted(expected_claim_keys),
            "actual_claim_keys": sorted(claims),
            "claim_set_matches": claim_set_matches,
            "required_ordered_claim_keys": ordered_claim_keys,
            "bad_claim_records": bad_claim_records,
            "anchor_matches_o_1": anchor_matches,
            "expected_cross_section_keys": sorted(expected_cross_section_keys),
            "actual_cross_section_keys": sorted(cross_sections),
            "cross_section_keys_match": cross_section_keys_match,
        })
    except Exception as exc:
        _set_failure(record, "phase3_completeness_invalid", str(exc))
    return [record]


def _phase6_scan_matrix_checks(root: str) -> List[Dict[str, Any]]:
    rel_path = os.path.join("data", "phase6", "scan_manifest.json")
    path = os.path.join(root, rel_path)
    if not os.path.exists(path):
        return []
    record: Dict[str, Any] = {
        "rel_path": rel_path + ":complete_scan_matrix",
        "severity": "abort",
        "source": "phase6_complete_scan_matrix",
        "path": path,
    }
    try:
        manifest = _load_json(path)
        operators = _operators(root)
        expected_labels = [f"f{i}" for i in range(11)]
        bad = []
        for operator in operators:
            value = manifest.get(operator)
            if not isinstance(value, dict):
                bad.append({"operator": operator, "error": "missing operator record"})
                continue
            errors = []
            if value.get("labels") != expected_labels:
                errors.append("labels must be exactly f0 through f10 in order")
            if value.get("point_count") != 11:
                errors.append("point_count must equal 11")
            try:
                if float(value.get("c_scan")) <= 0:
                    errors.append("c_scan must be positive")
            except (TypeError, ValueError):
                errors.append("c_scan must be numeric")
            if not value.get("scan_expression"):
                errors.append("scan_expression is required")
            if errors:
                bad.append({"operator": operator, "errors": errors})
        record.update({
            "ok": set(manifest) == set(operators) and not bad,
            "expected_operators": operators,
            "actual_operators": sorted(manifest),
            "bad_records": bad,
        })
    except Exception as exc:
        _set_failure(record, "phase6_scan_matrix_invalid", str(exc))
    return [record]


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
        "selection_rationale",
        "selection_evidence",
        "source_threshold_optimization_entry",
    ]
    missing = [key for key in required if key not in data or data.get(key) in (None, "")]
    algorithms = _algorithm_names(root)
    operators = _operators(root)
    selected_algorithm = data.get("selected_algorithm")
    selection_scope = data.get("selection_scope")
    invalid = []
    if selected_algorithm not in algorithms:
        invalid.append("selected_algorithm is not a Phase 7 anchor algorithm")
    if selection_scope not in {"anchor_operator_only", "per_operator_best"}:
        invalid.append("selection_scope must be anchor_operator_only or per_operator_best")
    if data.get("selection_criterion") != "narrowest_anchor_S2_constraint_width":
        invalid.append(
            "selection_criterion must be narrowest_anchor_S2_constraint_width; "
            "AUC or another metric cannot select the final strategy"
        )
    if not isinstance(data.get("selection_rationale"), str) or not data["selection_rationale"].strip():
        invalid.append("selection_rationale must be non-empty")
    evidence = data.get("selection_evidence")
    if not isinstance(evidence, list) or not evidence or any(
        not isinstance(value, str) or not value.strip() for value in evidence
    ):
        invalid.append("selection_evidence must be a non-empty list of evidence paths")
    try:
        threshold = float(data.get("selected_threshold"))
        if not 0.0 <= threshold <= 1.0:
            invalid.append("selected_threshold must be in [0, 1]")
    except (TypeError, ValueError):
        invalid.append("selected_threshold must be numeric")
    if selection_scope == "per_operator_best":
        operator_selections = data.get("operator_selections")
        if not isinstance(operator_selections, dict):
            invalid.append("operator_selections must be an object for per_operator_best")
        elif set(operator_selections) != set(operators):
            invalid.append("operator_selections keys must exactly match Phase 3 claimed operators")
        else:
            for operator in operators:
                value = operator_selections.get(operator)
                if not isinstance(value, dict):
                    invalid.append(f"operator_selections.{operator} must be an object")
                    continue
                if value.get("selected_algorithm") not in algorithms:
                    invalid.append(
                        f"operator_selections.{operator}.selected_algorithm is not present in Phase 7"
                    )
                try:
                    operator_threshold = float(value.get("selected_threshold"))
                    if not 0.0 <= operator_threshold <= 1.0:
                        invalid.append(
                            f"operator_selections.{operator}.selected_threshold must be in [0, 1]"
                        )
                except (TypeError, ValueError):
                    invalid.append(
                        f"operator_selections.{operator}.selected_threshold must be numeric"
                    )
                if value.get("selection_criterion") != "narrowest_operator_S2_constraint_width":
                    invalid.append(
                        f"operator_selections.{operator}.selection_criterion must be "
                        "narrowest_operator_S2_constraint_width"
                    )
    return [{
        "rel_path": rel_path,
        "severity": "abort",
        "source": "phase9_final_strategy",
        "path": path,
        "ok": not missing and not invalid,
        "missing_keys": missing,
        "invalid_values": invalid,
    }]


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _valid_interval(value: Any) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(_finite_number(item) for item in value)
        and float(value[0]) < 0.0 < float(value[1])
    )


def _numerical_validation_errors(data: Dict[str, Any]) -> List[str]:
    validation = data.get("numerical_validation")
    if not isinstance(validation, dict):
        return ["numerical_validation must be an object"]
    errors = []
    if validation.get("status") != "pass":
        errors.append("numerical_validation.status must be pass")
    if not isinstance(validation.get("method"), str) or not validation["method"].strip():
        errors.append("numerical_validation.method must be non-empty")
    evidence = validation.get("evidence_paths")
    if not isinstance(evidence, list) or not evidence or any(
        not isinstance(value, str) or not value.strip() for value in evidence
    ):
        errors.append("numerical_validation.evidence_paths must be a non-empty list")
    return errors


def _csv_data_row_count(path: str) -> int:
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return sum(1 for row in reader if row)


def _shared_score_counts(
    root: str,
    path: str,
    thresholds: List[float],
    expected_source_csv: str,
) -> Tuple[int, List[int], List[str]]:
    differences = [0] * (len(thresholds) + 1)
    row_count = 0
    errors: List[str] = []
    event_indices: Set[int] = set()
    expected_source_abs = os.path.normcase(os.path.abspath(expected_source_csv))
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"event_index", "score", "source_csv"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            return 0, [0] * len(thresholds), [
                "score CSV must contain event_index, score, and source_csv"
            ]
        for row_number, row in enumerate(reader, start=2):
            row_count += 1
            try:
                event_index = int(row["event_index"])
            except (TypeError, ValueError):
                errors.append(f"row {row_number} event_index must be an integer")
            else:
                if event_index < 0:
                    errors.append(f"row {row_number} event_index must be non-negative")
                elif event_index in event_indices:
                    errors.append(f"row {row_number} duplicates event_index {event_index}")
                else:
                    event_indices.add(event_index)
            try:
                score = float(row["score"])
            except (TypeError, ValueError):
                errors.append(f"row {row_number} score must be numeric")
                continue
            if not math.isfinite(score) or not 0.0 <= score <= 1.0:
                errors.append(f"row {row_number} score must be finite and in [0, 1]")
                continue
            source_value = row.get("source_csv") or ""
            source_abs = _manifest_reference_path(root, source_value)
            if os.path.normcase(os.path.abspath(source_abs)) != expected_source_abs:
                errors.append(
                    f"row {row_number} source_csv must name {os.path.basename(expected_source_csv)}"
                )
            last_passing = bisect_right(thresholds, score) - 1
            if last_passing >= 0:
                differences[0] += 1
                differences[last_passing + 1] -= 1
    expected_indices = set(range(row_count))
    if event_indices != expected_indices:
        missing = sorted(expected_indices - event_indices)
        unexpected = sorted(event_indices - expected_indices)
        if missing:
            errors.append(f"event_index is missing zero-based identities: {missing[:10]}")
        if unexpected:
            errors.append(f"event_index has identities outside the source row range: {unexpected[:10]}")
    counts = []
    running = 0
    for index in range(len(thresholds)):
        running += differences[index]
        counts.append(running)
    return row_count, counts, errors


def _phase8_shared_f5_checks(root: str) -> List[Dict[str, Any]]:
    """Audit the shared Phase 8 f5 pool and its zero-event convention."""
    rel_path = os.path.join("data", "phase8", "shared_f5_background.json")
    path = os.path.join(root, rel_path)
    if not os.path.exists(path):
        return []
    record: Dict[str, Any] = {
        "rel_path": rel_path + ":shared_pool_and_background",
        "severity": "abort",
        "source": "phase8_shared_f5_background",
        "path": path,
    }
    try:
        data = _load_json(path)
        operators = _operators(root)
        algorithms = _algorithm_names(root)
        claims_path = os.path.join(root, "data", "phase3", "operator_claims.json")
        claims = _load_json(claims_path) if os.path.exists(claims_path) else {}
        errors: List[str] = []
        if data.get("schema_version") != "1.0":
            errors.append("schema_version must be 1.0")
        if data.get("source_operators") != operators:
            errors.append("source_operators must equal Phase 3 claimed operators in order")
        anchor = data.get("anchor_operator")
        anchor_path = os.path.join(root, "data", "phase3", "anchor.json")
        expected_anchor = operators[0] if operators else None
        if os.path.exists(anchor_path):
            anchor_data = _load_json(anchor_path)
            expected_anchor = f"o_{anchor_data.get('global_idx')}"
        if anchor != expected_anchor:
            errors.append("anchor_operator must match Phase 3 anchor.json")

        initial = data.get("initial_f5_sources")
        if not isinstance(initial, list):
            errors.append("initial_f5_sources must be a list")
            initial = []
        initial_operators = []
        initial_runners: Dict[str, Dict[str, Any]] = {}
        initial_outputs_by_lhco: Dict[str, Dict[str, Any]] = {}
        recovery_sources: Dict[str, List[Dict[str, Any]]] = {}
        for index, item in enumerate(initial):
            if not isinstance(item, dict):
                errors.append(f"initial_f5_sources[{index}] must be an object")
                continue
            if item.get("scan_label") != "f5":
                errors.append(f"initial_f5_sources[{index}].scan_label must be f5")
            operator = item.get("operator")
            initial_operators.append(operator)
            if operator not in operators:
                errors.append(f"initial_f5_sources[{index}] has an unclaimed operator")
            if item.get("model") != (claims.get(operator) or {}).get("model"):
                errors.append(f"initial_f5_sources[{index}].model differs from Phase 3")
            source_kind = item.get("source_kind")
            if source_kind not in {"direct_phase6_scan", "phase6_recovery_attempt"}:
                errors.append(
                    f"initial_f5_sources[{index}].source_kind must be direct_phase6_scan "
                    "or phase6_recovery_attempt"
                )
            expected_paths = None
            if source_kind == "direct_phase6_scan":
                expected_paths = {
                    "lhco_path": os.path.join("data", "phase6", f"np_{operator}_f5.lhco"),
                    "banner_path": os.path.join("data", "phase6", f"np_{operator}_f5_banner.txt"),
                    "runner_result_json": os.path.join(
                        "data", "phase6", f"np_{operator}_scan_result.json"
                    ),
                }
            elif source_kind == "phase6_recovery_attempt":
                recovery_sources.setdefault(str(operator), []).append(item)
                if item.get("recovery_unit") != operator:
                    errors.append(f"initial_f5_sources[{index}].recovery_unit must equal operator")
                attempt_index = item.get("recovery_attempt_index")
                if not isinstance(attempt_index, int) or isinstance(attempt_index, bool) or attempt_index < 0:
                    errors.append(
                        f"initial_f5_sources[{index}].recovery_attempt_index must be a non-negative integer"
                    )
            for key in ("lhco_path", "banner_path", "runner_result_json"):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    errors.append(f"initial_f5_sources[{index}].{key} must be non-empty")
                    continue
                actual = _manifest_reference_path(root, item[key])
                expected = (
                    os.path.abspath(os.path.join(root, expected_paths[key]))
                    if expected_paths is not None else None
                )
                if expected is not None and os.path.normcase(actual) != os.path.normcase(expected):
                    errors.append(
                        f"initial_f5_sources[{index}].{key} must be {expected_paths[key]}"
                    )
                if not os.path.isfile(actual) or os.path.getsize(actual) <= 0:
                    errors.append(f"initial_f5_sources[{index}].{key} is missing or empty")
            runner_path = _manifest_reference_path(root, str(item.get("runner_result_json") or ""))
            if os.path.isfile(runner_path):
                runner = _load_json(runner_path)
                initial_runners.setdefault(str(operator), runner)
                if runner.get("status") != "completed" or runner.get("process_mode") != "scan":
                    errors.append(f"initial_f5_sources[{index}] runner must be a completed scan")
                if runner.get("operator") != operator or runner.get("model") != item.get("model"):
                    errors.append(f"initial_f5_sources[{index}] runner operator/model mismatch")
                target = runner.get("target_coefficient") or {}
                if str(target.get("index")) != str((claims.get(operator) or {}).get("anoinput_idx")):
                    errors.append(f"initial_f5_sources[{index}] runner coefficient index mismatch")
                output = next(
                    (
                        value for value in runner.get("outputs") or []
                        if isinstance(value, dict) and value.get("label") == f"np_{operator}_f5"
                    ),
                    None,
                )
                if output is None:
                    errors.append(f"initial_f5_sources[{index}] runner lacks an f5 output")
                else:
                    lhco_key = os.path.normcase(
                        _manifest_reference_path(root, str(item.get("lhco_path") or ""))
                    )
                    initial_outputs_by_lhco[lhco_key] = output
                    for output_key, source_key in (("lhco_path", "lhco_path"), ("banner_path", "banner_path")):
                        output_path = output.get(output_key)
                        source_path = item.get(source_key)
                        if not isinstance(output_path, str) or not isinstance(source_path, str) or (
                            os.path.normcase(os.path.abspath(output_path))
                            != os.path.normcase(_manifest_reference_path(root, source_path))
                        ):
                            errors.append(
                                f"initial_f5_sources[{index}].{source_key} differs from runner f5 output"
                            )
        if sorted(set(initial_operators), key=lambda key: operators.index(key) if key in operators else len(operators)) != operators:
            errors.append("initial_f5_sources must cover every claimed operator")
        for operator in operators:
            operator_items = [item for item in initial if isinstance(item, dict) and item.get("operator") == operator]
            direct_items = [
                item for item in operator_items
                if item.get("source_kind") == "direct_phase6_scan"
            ]
            recovered_items = recovery_sources.get(operator, [])
            if direct_items and recovered_items:
                errors.append(f"initial_f5_sources cannot mix direct and recovery sources for {operator}")
            if len(direct_items) > 1:
                errors.append(f"initial_f5_sources may contain only one direct source for {operator}")
            if recovered_items:
                recovery_path = os.path.join(root, "data", "phase6", "event_count_recovery.json")
                try:
                    aggregate = _load_json(recovery_path)
                    unit = (aggregate.get("units") or {}).get(operator) or {}
                    if unit.get("status") != "accepted":
                        errors.append(f"Phase 6 recovery unit {operator} must be accepted")
                    expected_sources = []
                    for attempt in unit.get("attempts") or []:
                        attempt_index = attempt.get("attempt_index")
                        result = attempt.get("result") or {}
                        config = attempt.get("config") or {}
                        for output in result.get("outputs") or []:
                            if (
                                isinstance(output, dict)
                                and output.get("label") == f"np_{operator}_f5"
                                and int(output.get("loaded_lhco_event_count", 0)) > 0
                            ):
                                expected_sources.append((
                                    attempt_index,
                                    os.path.normcase(os.path.abspath(output.get("lhco_path", ""))),
                                    os.path.normcase(os.path.abspath(output.get("banner_path", ""))),
                                    os.path.normcase(os.path.abspath(config.get("result_json", ""))),
                                ))
                    actual_sources = sorted((
                        item.get("recovery_attempt_index"),
                        os.path.normcase(_manifest_reference_path(root, str(item.get("lhco_path") or ""))),
                        os.path.normcase(_manifest_reference_path(root, str(item.get("banner_path") or ""))),
                        os.path.normcase(_manifest_reference_path(root, str(item.get("runner_result_json") or ""))),
                    ) for item in recovered_items)
                    if actual_sources != sorted(expected_sources):
                        errors.append(
                            f"initial_f5_sources recovery entries for {operator} must exactly match "
                            "the successful f5 attempts in Phase 6 recovery metadata"
                        )
                except (OSError, ValueError, TypeError) as exc:
                    errors.append(f"could not verify Phase 6 recovery sources for {operator}: {exc}")

        run_config_path = os.path.join(_global_results_root(root), "run_config.json")
        run_config = _load_json(run_config_path) if os.path.exists(run_config_path) else {}
        nev_scan = ((run_config.get("locked_event_counts") or {}).get("nev_scan"))
        active_run = None
        run_configurations = run_config.get("run_configurations") or []
        if len(run_configurations) == 1:
            active_run = run_configurations[0]
        else:
            root_name = os.path.basename(os.path.abspath(root))
            active_run = next(
                (
                    value for value in run_configurations
                    if isinstance(value, dict) and value.get("run_dir") == root_name
                ),
                None,
            )
        for operator, runner in initial_runners.items():
            if nev_scan is not None and runner.get("nevents") != nev_scan:
                errors.append(f"initial {operator} runner nevents differs from locked nev_scan")
            if run_config and runner.get("process") != run_config.get("process"):
                errors.append(f"initial {operator} runner process differs from run_config")
            if active_run:
                for key in ("ebeam1", "ebeam2"):
                    if not (
                        _finite_number(runner.get(key))
                        and _finite_number(active_run.get(key))
                        and math.isclose(float(runner[key]), float(active_run[key]), rel_tol=0.0, abs_tol=1e-12)
                    ):
                        errors.append(f"initial {operator} runner {key} differs from run_config")
            if run_config and runner.get("polarization") != run_config.get("polarization"):
                errors.append(f"initial {operator} runner polarization differs from run_config")
            if run_config and runner.get("delphes_card") != run_config.get("delphes_card"):
                errors.append(f"initial {operator} runner delphes_card differs from run_config")

        additional = data.get("additional_anchor_f5_sources", [])
        if not isinstance(additional, list):
            errors.append("additional_anchor_f5_sources must be a list")
            additional = []
        for index, item in enumerate(additional):
            if not isinstance(item, dict):
                errors.append(f"additional_anchor_f5_sources[{index}] must be an object")
                continue
            if item.get("operator") != anchor or item.get("scan_label") != "f5":
                errors.append(
                    f"additional_anchor_f5_sources[{index}] must be anchor_operator f5"
                )
            if item.get("source_kind") != "additional_anchor_f5":
                errors.append(
                    f"additional_anchor_f5_sources[{index}].source_kind must be additional_anchor_f5"
                )
            if item.get("round") != index + 1:
                errors.append("additional anchor rounds must be numbered consecutively from 1")
            round_number = index + 1
            expected_paths = {
                "lhco_path": os.path.join(
                    "data", "phase8", "shared_f5_sources",
                    f"shared_f5_anchor_round_{round_number}.lhco",
                ),
                "banner_path": os.path.join(
                    "data", "phase8", "shared_f5_sources",
                    f"shared_f5_anchor_round_{round_number}_banner.txt",
                ),
                "runner_result_json": os.path.join(
                    "data", "phase8", "shared_f5_sources",
                    f"anchor_round_{round_number}_result.json",
                ),
            }
            if item.get("model") != (claims.get(anchor) or {}).get("model"):
                errors.append(f"additional_anchor_f5_sources[{index}].model differs from anchor")
            for key in ("lhco_path", "banner_path", "runner_result_json"):
                if not isinstance(item.get(key), str) or not item[key].strip():
                    errors.append(f"additional_anchor_f5_sources[{index}].{key} must be non-empty")
                    continue
                actual = _manifest_reference_path(root, item[key])
                expected = os.path.abspath(os.path.join(root, expected_paths[key]))
                if os.path.normcase(actual) != os.path.normcase(expected):
                    errors.append(
                        f"additional_anchor_f5_sources[{index}].{key} must be {expected_paths[key]}"
                    )
                if not os.path.isfile(actual) or os.path.getsize(actual) <= 0:
                    errors.append(f"additional_anchor_f5_sources[{index}].{key} is missing or empty")
            if item.get("requested_event_count") != nev_scan:
                errors.append(f"additional_anchor_f5_sources[{index}] must use locked nev_scan")
            result_path = _manifest_reference_path(root, str(item.get("runner_result_json") or ""))
            if os.path.isfile(result_path):
                runner = _load_json(result_path)
                if runner.get("status") != "completed" or runner.get("process_mode") != "sm_np_point":
                    errors.append(f"additional_anchor_f5_sources[{index}] runner must be completed sm_np_point")
                if runner.get("operator") != anchor or runner.get("model") != item.get("model"):
                    errors.append(f"additional_anchor_f5_sources[{index}] runner operator/model mismatch")
                if runner.get("coefficient_mode") != "explicit":
                    errors.append(f"additional_anchor_f5_sources[{index}] runner coefficient_mode must be explicit")
                target = runner.get("target_coefficient") or {}
                if str(target.get("index")) != str((claims.get(anchor) or {}).get("anoinput_idx")):
                    errors.append(f"additional_anchor_f5_sources[{index}] runner coefficient index mismatch")
                try:
                    target_value = float(target.get("value"))
                except (TypeError, ValueError):
                    target_value = math.nan
                if target_value != 0.0:
                    errors.append(f"additional_anchor_f5_sources[{index}] runner coefficient value must be zero")
                if runner.get("nevents") != nev_scan:
                    errors.append(f"additional_anchor_f5_sources[{index}] runner nevents differs from locked nev_scan")
                baseline = initial_runners.get(str(anchor)) or {}
                for key in (
                    "process", "ebeam1", "ebeam2", "polarization", "delphes_card",
                    "weighted_order", "madspin",
                ):
                    if runner.get(key) != baseline.get(key):
                        errors.append(f"additional_anchor_f5_sources[{index}] runner {key} differs from anchor scan")
                expected_label = f"shared_f5_anchor_round_{round_number}"
                output = next(
                    (
                        value for value in runner.get("outputs") or []
                        if isinstance(value, dict) and value.get("label") == expected_label
                    ),
                    None,
                )
                if output is None:
                    errors.append(f"additional_anchor_f5_sources[{index}] runner lacks {expected_label}")
                else:
                    if output.get("loaded_lhco_event_count") != item.get("loaded_lhco_event_count"):
                        errors.append(f"additional_anchor_f5_sources[{index}] loaded count differs from runner")
                    if not (
                        _finite_number(output.get("cross_section_pb"))
                        and _finite_number(item.get("banner_cross_section_pb"))
                        and math.isclose(
                            float(output["cross_section_pb"]),
                            float(item["banner_cross_section_pb"]),
                            rel_tol=1e-12,
                            abs_tol=1e-15,
                        )
                    ):
                        errors.append(f"additional_anchor_f5_sources[{index}] banner cross-section differs from runner")
                    for output_key, source_key in (("lhco_path", "lhco_path"), ("banner_path", "banner_path")):
                        output_path = output.get(output_key)
                        source_path = item.get(source_key)
                        if not isinstance(output_path, str) or not isinstance(source_path, str) or (
                            os.path.normcase(os.path.abspath(output_path))
                            != os.path.normcase(_manifest_reference_path(root, source_path))
                        ):
                            errors.append(
                                f"additional_anchor_f5_sources[{index}].{source_key} differs from runner output"
                            )
        if data.get("additional_anchor_f5_rounds") != len(additional):
            errors.append("additional_anchor_f5_rounds must equal additional source count")
        if not 0 <= len(additional) <= MAX_ADDITIONAL_ANCHOR_ROUNDS:
            errors.append("additional anchor f5 rounds must be between 0 and 3")
        declared_sources = initial + additional
        for key in ("lhco_path", "banner_path", "runner_result_json"):
            values = [
                os.path.normcase(_manifest_reference_path(root, item[key]))
                for item in declared_sources
                if isinstance(item, dict) and isinstance(item.get(key), str)
            ]
            if len(values) != len(set(values)):
                errors.append(f"all shared f5 {key} values must be unique")

        loaded = data.get("loaded_lhco_event_count")
        merged_cs = data.get("merged_cross_section_pb")
        valid_loaded = isinstance(loaded, int) and not isinstance(loaded, bool) and loaded > 0
        valid_merged_cs = _finite_number(merged_cs) and float(merged_cs) > 0.0
        if not valid_loaded:
            errors.append("loaded_lhco_event_count must be a positive integer")
        if not valid_merged_cs:
            errors.append("merged_cross_section_pb must be a finite positive number")
        if data.get("cross_section_rule") != "banner_arithmetic_mean":
            errors.append("cross_section_rule must be banner_arithmetic_mean")

        surviving = data.get("surviving_final_state_event_count")
        if not isinstance(surviving, int) or isinstance(surviving, bool) or surviving < 0:
            errors.append("surviving_final_state_event_count must be a non-negative integer")
            surviving = None
        elif valid_loaded and surviving > loaded:
            errors.append(
                "surviving_final_state_event_count cannot exceed loaded_lhco_event_count"
            )
        shared_lhco_path = os.path.join(root, "data", "phase8", "shared_f5.lhco")
        if not os.path.isfile(shared_lhco_path) or os.path.getsize(shared_lhco_path) <= 0:
            errors.append("data/phase8/shared_f5.lhco is missing or empty")
        shared_csv_path = os.path.join(root, "data", "phase8", "csv", "shared_f5.csv")
        if not os.path.isfile(shared_csv_path) or os.path.getsize(shared_csv_path) <= 0:
            errors.append("data/phase8/csv/shared_f5.csv is missing or empty")
        elif surviving is not None:
            try:
                if _csv_data_row_count(shared_csv_path) != surviving:
                    errors.append(
                        "shared_f5.csv row count differs from surviving_final_state_event_count"
                    )
            except (OSError, csv.Error) as exc:
                errors.append(f"could not read shared_f5.csv: {exc}")

        merge_path = os.path.join(root, "data", "phase8", "shared_f5_merge.json")
        if not os.path.exists(merge_path):
            errors.append("data/phase8/shared_f5_merge.json is missing")
        else:
            merge = _load_json(merge_path)
            expected_output_path = os.path.abspath(shared_lhco_path)
            merge_output_path = merge.get("output_lhco_path")
            if not isinstance(merge_output_path, str) or (
                os.path.normcase(_manifest_reference_path(root, merge_output_path))
                != os.path.normcase(expected_output_path)
            ):
                errors.append("shared_f5_merge.json output_lhco_path must name data/phase8/shared_f5.lhco")
            if merge.get("cross_section_rule") != "banner_arithmetic_mean":
                errors.append("shared_f5_merge.json cross_section_rule must be banner_arithmetic_mean")
            if merge.get("merged_loaded_lhco_event_count") != loaded:
                errors.append("loaded_lhco_event_count differs from shared_f5_merge.json")
            merge_cs = merge.get("merged_cross_section_pb")
            if not (_finite_number(merge_cs) and _finite_number(merged_cs)) or not math.isclose(
                float(merge_cs), float(merged_cs), rel_tol=1e-12, abs_tol=1e-15
            ):
                errors.append("merged_cross_section_pb differs from shared_f5_merge.json")
            merge_sources = merge.get("source_records")
            if not isinstance(merge_sources, list):
                errors.append("shared_f5_merge.json source_records must be a list")
            else:
                if len(merge_sources) != len(declared_sources):
                    errors.append("shared_f5_merge.json source count differs from declared f5 sources")
                else:
                    parsed_banner_cross_sections: List[float] = []
                    source_count_sum = 0
                    for index, (declared, merged_source) in enumerate(zip(declared_sources, merge_sources)):
                        banner_cross_section = None
                        if not isinstance(declared, dict):
                            errors.append(f"shared_f5_background.json source {index} must be an object")
                            continue
                        if not isinstance(merged_source, dict):
                            errors.append(f"shared_f5_merge.json source_records[{index}] must be an object")
                            continue
                        for declared_key, merged_key in (("lhco_path", "lhco_path"), ("banner_path", "banner_path")):
                            declared_path = declared.get(declared_key)
                            merged_source_path = merged_source.get(merged_key)
                            if not isinstance(declared_path, str) or not isinstance(merged_source_path, str):
                                errors.append(
                                    f"shared_f5_merge.json source_records[{index}].{merged_key} must be a path"
                                )
                                continue
                            expected_path = _manifest_reference_path(root, declared_path)
                            if os.path.normcase(os.path.abspath(merged_source_path)) != os.path.normcase(expected_path):
                                errors.append(
                                    f"shared_f5_merge.json source_records[{index}].{merged_key} "
                                    "differs from shared_f5_background.json"
                                )
                        banner_path = declared.get("banner_path")
                        if isinstance(banner_path, str):
                            banner_abs = _manifest_reference_path(root, banner_path)
                            try:
                                banner_cross_section = extract_cross_section(banner_abs)
                            except (OSError, ValueError) as exc:
                                errors.append(f"could not read source banner {index}: {exc}")
                            else:
                                parsed_banner_cross_sections.append(float(banner_cross_section))
                                merged_source_cs = merged_source.get("cross_section_pb")
                                if not _finite_number(merged_source_cs) or not math.isclose(
                                    float(merged_source_cs),
                                    float(banner_cross_section),
                                    rel_tol=1e-12,
                                    abs_tol=1e-15,
                                ):
                                    errors.append(
                                        f"shared_f5_merge.json source_records[{index}].cross_section_pb "
                                        "differs from its banner"
                                    )
                                declared_cs = declared.get("banner_cross_section_pb")
                                if declared_cs is not None and (
                                    not _finite_number(declared_cs)
                                    or not math.isclose(
                                        float(declared_cs),
                                        float(banner_cross_section),
                                        rel_tol=1e-12,
                                        abs_tol=1e-15,
                                    )
                                ):
                                    errors.append(
                                        f"shared_f5_background.json source {index} banner_cross_section_pb "
                                        "differs from its banner"
                                    )
                        source_count = merged_source.get("loaded_lhco_event_count")
                        if not isinstance(source_count, int) or isinstance(source_count, bool) or source_count <= 0:
                            errors.append(
                                f"shared_f5_merge.json source_records[{index}].loaded_lhco_event_count "
                                "must be a positive integer"
                            )
                        else:
                            source_count_sum += source_count
                            declared_count = declared.get("loaded_lhco_event_count")
                            if declared_count is not None and declared_count != source_count:
                                errors.append(
                                    f"shared_f5_background.json source {index} loaded_lhco_event_count "
                                    "differs from shared_f5_merge.json"
                                )
                            if index < len(initial):
                                declared_lhco = _manifest_reference_path(
                                    root, str(declared.get("lhco_path") or "")
                                )
                                runner_output = initial_outputs_by_lhco.get(
                                    os.path.normcase(declared_lhco)
                                ) or {}
                                if runner_output.get("loaded_lhco_event_count") != source_count:
                                    errors.append(
                                        f"initial_f5_sources[{index}] loaded count differs from runner f5 output"
                                    )
                                if banner_cross_section is not None and (
                                    not _finite_number(runner_output.get("cross_section_pb"))
                                    or not math.isclose(
                                        float(runner_output["cross_section_pb"]),
                                        float(banner_cross_section),
                                        rel_tol=1e-12,
                                        abs_tol=1e-15,
                                    )
                                ):
                                    errors.append(
                                        f"initial_f5_sources[{index}] cross-section differs from runner f5 output"
                                    )
                    if merge.get("source_count_sum") != source_count_sum:
                        errors.append("shared_f5_merge.json source_count_sum differs from source records")
                    if valid_loaded and source_count_sum != loaded:
                        errors.append("loaded_lhco_event_count differs from sum of source records")
                    if len(parsed_banner_cross_sections) == len(declared_sources) and parsed_banner_cross_sections:
                        banner_mean = sum(parsed_banner_cross_sections) / len(parsed_banner_cross_sections)
                        if not valid_merged_cs or not math.isclose(
                            float(merged_cs), banner_mean, rel_tol=1e-12, abs_tol=1e-15
                        ):
                            errors.append(
                                "merged_cross_section_pb must equal the arithmetic mean of source banners"
                            )

        backgrounds = data.get("algorithms")
        if not isinstance(backgrounds, dict):
            errors.append("algorithms must be an object")
            backgrounds = {}
        if set(backgrounds) != set(algorithms):
            errors.append("algorithms must exactly equal Phase 7 algorithm keys")
        for algorithm in algorithms:
            item = backgrounds.get(algorithm)
            if not isinstance(item, dict):
                errors.append(f"algorithms.{algorithm} must be an object")
                continue
            if not _finite_number(item.get("threshold")) or not 0.0 <= float(item["threshold"]) <= 1.0:
                errors.append(f"algorithms.{algorithm}.threshold must be in [0, 1]")
            threshold_path = os.path.join(root, "data", "phase8", "threshold_optimization.json")
            if os.path.exists(threshold_path):
                threshold_data = _load_json(threshold_path)
                expected_threshold = ((threshold_data.get("anchor") or {}).get(algorithm) or {}).get("optimal_threshold")
                if not (
                    _finite_number(item.get("threshold"))
                    and _finite_number(expected_threshold)
                    and math.isclose(float(item["threshold"]), float(expected_threshold), rel_tol=0.0, abs_tol=1e-12)
                ):
                    errors.append(f"algorithms.{algorithm}.threshold differs from threshold_optimization.json")
            passing = item.get("passing_event_count")
            if not isinstance(passing, int) or isinstance(passing, bool) or passing < 0:
                errors.append(f"algorithms.{algorithm}.passing_event_count must be non-negative integer")
                continue
            sigma = item.get("sigma0_after_cut_pb")
            effective = item.get("effective_passing_event_count")
            rounds = len(additional)
            if passing > 0:
                expected_effective = float(passing)
                expected_convention = "observed_events"
                if not valid_loaded or not valid_merged_cs:
                    errors.append(f"algorithms.{algorithm} formula needs valid merged inputs")
                elif not _finite_number(sigma) or not math.isclose(
                    float(sigma), float(merged_cs) * passing / loaded, rel_tol=1e-12, abs_tol=1e-15
                ):
                    errors.append(f"algorithms.{algorithm} has the wrong observed-event formula")
            elif rounds < MAX_ADDITIONAL_ANCHOR_ROUNDS:
                expected_effective = None
                expected_convention = "unresolved_zero"
                errors.append(
                    f"algorithms.{algorithm} requires another anchor f5 round before Phase 8 can pass"
                )
                if sigma is not None or effective is not None:
                    errors.append(
                        f"algorithms.{algorithm} must remain unresolved before three zero rounds"
                    )
            else:
                expected_effective = 0.5
                expected_convention = "half_event_after_three_zero_rounds"
                if not valid_loaded or not valid_merged_cs:
                    errors.append(f"algorithms.{algorithm} formula needs valid merged inputs")
                elif not _finite_number(sigma) or not math.isclose(
                    float(sigma), float(merged_cs) * 0.5 / loaded, rel_tol=1e-12, abs_tol=1e-15
                ):
                    errors.append(f"algorithms.{algorithm} has the wrong half-event formula")
            if item.get("effective_passing_event_count") != expected_effective:
                errors.append(f"algorithms.{algorithm}.effective_passing_event_count is inconsistent")
            if item.get("convention") != expected_convention:
                errors.append(f"algorithms.{algorithm}.convention is inconsistent")
            expected_status = "accepted" if passing > 0 or rounds == MAX_ADDITIONAL_ANCHOR_ROUNDS else "additional_anchor_f5_required"
            if item.get("status") != expected_status:
                errors.append(f"algorithms.{algorithm}.status is inconsistent")
            if valid_loaded and passing > loaded:
                errors.append(f"algorithms.{algorithm}.passing_event_count exceeds loaded count")
            score_path = os.path.join(
                root, "data", "phase8", "scores", algorithm, "shared_f5_scores.csv"
            )
            if not os.path.isfile(score_path) or os.path.getsize(score_path) <= 0:
                errors.append(f"shared_f5_scores.csv is missing or empty for {algorithm}")
            elif _finite_number(item.get("threshold")) and surviving is not None:
                try:
                    score_rows, score_counts, score_errors = _shared_score_counts(
                        root,
                        score_path,
                        [float(item["threshold"])],
                        shared_csv_path,
                    )
                    errors.extend(
                        f"{algorithm} shared score CSV: {message}" for message in score_errors
                    )
                    if score_rows != surviving:
                        errors.append(
                            f"{algorithm} shared score CSV row count differs from "
                            "surviving_final_state_event_count"
                        )
                    if score_counts[0] != passing:
                        errors.append(
                            f"algorithms.{algorithm}.passing_event_count differs from scores at threshold"
                        )
                except (OSError, csv.Error) as exc:
                    errors.append(f"could not read shared score CSV for {algorithm}: {exc}")

        fit_values: Dict[str, float] = {}
        for operator in operators:
            for algorithm in algorithms:
                fit_path = os.path.join(root, "data", "phase8", f"csfit_{operator}_{algorithm}.json")
                if not os.path.exists(fit_path):
                    continue
                fit = _load_json(fit_path)
                value = fit.get("sigma0_after_cut_pb")
                expected = (backgrounds.get(algorithm) or {}).get("sigma0_after_cut_pb")
                if not _finite_number(value) or not _finite_number(expected) or not math.isclose(
                    float(value), float(expected), rel_tol=1e-12, abs_tol=1e-15
                ):
                    errors.append(f"{operator}/{algorithm} does not use the shared background value")
                if _finite_number(value):
                    prior = fit_values.get(algorithm)
                    if prior is not None and not math.isclose(float(value), prior, rel_tol=1e-12, abs_tol=1e-15):
                        errors.append(f"all operators must share sigma0_after_cut_pb for {algorithm}")
                    fit_values[algorithm] = float(value)

        record.update({
            "ok": not errors,
            "expected_operators": operators,
            "expected_algorithms": algorithms,
            "additional_anchor_f5_rounds": len(additional),
            "invalid_values": errors,
        })
    except Exception as exc:
        _set_failure(record, "phase8_shared_f5_background_invalid", str(exc))
    return [record]


def _phase8_numerical_checks(root: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    operators = _operators(root)
    algorithms = _algorithm_names(root)
    threshold_rel = os.path.join("data", "phase8", "threshold_optimization.json")
    threshold_path = os.path.join(root, threshold_rel)
    if os.path.exists(threshold_path):
        record: Dict[str, Any] = {
            "rel_path": threshold_rel + ":numerical_content",
            "severity": "abort",
            "source": "phase8_threshold_numerical_content",
            "path": threshold_path,
        }
        try:
            data = _load_json(threshold_path)
            anchor = data.get("anchor")
            bad = []
            validation_errors = _numerical_validation_errors(data)
            if not isinstance(anchor, dict):
                raise ValueError("threshold_optimization.json must contain an anchor object")
            expected_thresholds = [0.02 * index for index in range(51)]
            background_path = os.path.join(root, "data", "phase8", "shared_f5_background.json")
            background_data = _load_json(background_path) if os.path.exists(background_path) else {}
            loaded = background_data.get("loaded_lhco_event_count")
            merged_cs = background_data.get("merged_cross_section_pb")
            rounds = background_data.get("additional_anchor_f5_rounds")
            valid_background_inputs = (
                isinstance(loaded, int)
                and not isinstance(loaded, bool)
                and loaded > 0
                and _finite_number(merged_cs)
                and float(merged_cs) > 0.0
                and isinstance(rounds, int)
                and not isinstance(rounds, bool)
                and 0 <= rounds <= MAX_ADDITIONAL_ANCHOR_ROUNDS
            )
            shared_csv_path = os.path.join(root, "data", "phase8", "csv", "shared_f5.csv")
            anchor_operator = background_data.get("anchor_operator")
            anchor_labels = (
                _scan_labels(root, [anchor_operator]).get(anchor_operator, [])
                if isinstance(anchor_operator, str) and anchor_operator
                else []
            )
            for algorithm in algorithms:
                value = anchor.get(algorithm)
                errors = []
                if not isinstance(value, dict):
                    bad.append({"algorithm": algorithm, "errors": ["missing algorithm record"]})
                    continue
                threshold = value.get("optimal_threshold")
                width = value.get("constraint_width_at_optimal")
                scan = value.get("threshold_scan")
                score_counts = None
                score_path = os.path.join(
                    root, "data", "phase8", "scores", algorithm, "shared_f5_scores.csv"
                )
                if os.path.isfile(score_path):
                    try:
                        _, score_counts, score_errors = _shared_score_counts(
                            root, score_path, expected_thresholds, shared_csv_path
                        )
                        errors.extend(
                            f"shared score CSV: {message}" for message in score_errors
                        )
                    except (OSError, csv.Error) as exc:
                        errors.append(f"could not read shared score CSV: {exc}")
                else:
                    errors.append("shared_f5_scores.csv is missing")

                anchor_score_counts = [0] * len(expected_thresholds)
                anchor_scores_complete = bool(anchor_operator and anchor_labels)
                for label in anchor_labels:
                    anchor_source_csv = os.path.join(
                        root, "data", "phase8", "csv", f"np_{anchor_operator}_{label}.csv"
                    )
                    anchor_score_path = os.path.join(
                        root,
                        "data",
                        "phase8",
                        "scores",
                        algorithm,
                        f"np_{anchor_operator}_{label}_scores.csv",
                    )
                    if not os.path.isfile(anchor_source_csv) or not os.path.isfile(anchor_score_path):
                        errors.append(f"anchor score/source CSV is missing for {label}")
                        anchor_scores_complete = False
                        continue
                    try:
                        source_rows = _csv_data_row_count(anchor_source_csv)
                        score_rows, point_counts, point_errors = _shared_score_counts(
                            root,
                            anchor_score_path,
                            expected_thresholds,
                            anchor_source_csv,
                        )
                        errors.extend(
                            f"anchor {label} score CSV: {message}" for message in point_errors
                        )
                        if score_rows != source_rows:
                            errors.append(f"anchor {label} score/source CSV row counts differ")
                        for index, count in enumerate(point_counts):
                            anchor_score_counts[index] += count
                    except (OSError, csv.Error) as exc:
                        errors.append(f"could not read anchor score/source CSV for {label}: {exc}")
                        anchor_scores_complete = False

                candidates: List[Tuple[float, float]] = []
                if not isinstance(scan, list) or len(scan) != 51:
                    errors.append("threshold_scan must contain exactly 51 entries")
                else:
                    for index, point in enumerate(scan):
                        if not isinstance(point, dict) or any(
                            key not in point
                            for key in (
                                "threshold",
                                "anchor_scan_passing_event_count",
                                "shared_f5_passing_event_count",
                                "effective_passing_event_count",
                                "background_status",
                                "sigma0_after_cut_pb",
                                "fit_intercept_fixed",
                                "lower_bound",
                                "upper_bound",
                                "constraint_width",
                            )
                        ):
                            errors.append(f"threshold_scan[{index}] is missing required fields")
                            continue
                        point_threshold = point.get("threshold")
                        if not _finite_number(point_threshold) or not math.isclose(
                            float(point_threshold),
                            expected_thresholds[index],
                            rel_tol=0.0,
                            abs_tol=1e-12,
                        ):
                            errors.append(
                                f"threshold_scan[{index}].threshold must be {expected_thresholds[index]:.2f}"
                            )
                        anchor_count = point.get("anchor_scan_passing_event_count")
                        if not isinstance(anchor_count, int) or isinstance(anchor_count, bool) or anchor_count < 0:
                            errors.append(
                                f"threshold_scan[{index}].anchor_scan_passing_event_count "
                                "must be a non-negative integer"
                            )
                            continue
                        if anchor_scores_complete and anchor_count != anchor_score_counts[index]:
                            errors.append(
                                f"threshold_scan[{index}].anchor_scan_passing_event_count "
                                "differs from the eleven anchor score CSVs"
                            )
                        shared_count = point.get("shared_f5_passing_event_count")
                        if not isinstance(shared_count, int) or isinstance(shared_count, bool) or shared_count < 0:
                            errors.append(
                                f"threshold_scan[{index}].shared_f5_passing_event_count "
                                "must be a non-negative integer"
                            )
                            continue
                        if score_counts is not None and shared_count != score_counts[index]:
                            errors.append(
                                f"threshold_scan[{index}].shared_f5_passing_event_count "
                                "differs from shared_f5_scores.csv"
                            )

                        status = point.get("background_status")
                        effective = point.get("effective_passing_event_count")
                        sigma = point.get("sigma0_after_cut_pb")
                        lower = point.get("lower_bound")
                        upper = point.get("upper_bound")
                        point_width = point.get("constraint_width")
                        if anchor_count == 0:
                            if status != "no_selected_scan_events":
                                errors.append(
                                    f"threshold_scan[{index}].background_status must be "
                                    "no_selected_scan_events"
                                )
                            if any(item is not None for item in (effective, sigma, lower, upper, point_width)):
                                errors.append(
                                    f"threshold_scan[{index}] must not contain a background or interval "
                                    "when no anchor scan event passes"
                                )
                            continue

                        expected_status = None
                        expected_effective = None
                        expected_sigma = None
                        if shared_count > 0:
                            expected_status = "observed_events"
                            expected_effective = float(shared_count)
                            if valid_background_inputs:
                                expected_sigma = float(merged_cs) * shared_count / loaded
                        elif valid_background_inputs and rounds < MAX_ADDITIONAL_ANCHOR_ROUNDS:
                            expected_status = "unresolved_zero"
                            if any(item is not None for item in (effective, sigma, lower, upper, point_width)):
                                errors.append(
                                    f"threshold_scan[{index}] must remain unresolved before three "
                                    "additional anchor rounds"
                                )
                        elif valid_background_inputs:
                            expected_status = "half_event_after_three_zero_rounds"
                            expected_effective = 0.5
                            expected_sigma = float(merged_cs) * 0.5 / loaded
                        else:
                            errors.append(
                                f"threshold_scan[{index}] cannot verify background because shared_f5_background.json "
                                "has invalid merged inputs"
                            )

                        if expected_status is not None and status != expected_status:
                            errors.append(
                                f"threshold_scan[{index}].background_status must be {expected_status}"
                            )
                        if expected_status == "unresolved_zero":
                            continue
                        if effective != expected_effective:
                            errors.append(
                                f"threshold_scan[{index}].effective_passing_event_count is inconsistent"
                            )
                        if expected_sigma is None or not _finite_number(sigma) or not math.isclose(
                            float(sigma), expected_sigma, rel_tol=1e-12, abs_tol=1e-15
                        ):
                            errors.append(
                                f"threshold_scan[{index}].sigma0_after_cut_pb has the wrong formula"
                            )
                        if point.get("fit_intercept_fixed") is not True:
                            errors.append(f"threshold_scan[{index}].fit_intercept_fixed must be true")
                        if not _valid_interval([lower, upper]):
                            errors.append(f"threshold_scan[{index}] must contain a valid lower/upper interval")
                        if not _finite_number(point_width) or float(point_width) <= 0.0:
                            errors.append(f"threshold_scan[{index}].constraint_width must be positive")
                        elif _finite_number(lower) and _finite_number(upper) and not math.isclose(
                            float(point_width), float(upper) - float(lower), rel_tol=1e-12, abs_tol=1e-15
                        ):
                            errors.append(
                                f"threshold_scan[{index}].constraint_width must equal upper_bound-lower_bound"
                            )
                        elif _finite_number(point_threshold):
                            candidates.append((float(point_width), float(point_threshold)))

                if not candidates:
                    errors.append("threshold_scan contains no usable finite positive constraint width")
                else:
                    minimum_width = min(item[0] for item in candidates)
                    selected_candidates = [
                        item for item in candidates
                        if math.isclose(item[0], minimum_width, rel_tol=1e-12, abs_tol=1e-15)
                    ]
                    if not _finite_number(threshold) or not any(
                        math.isclose(float(threshold), item[1], rel_tol=0.0, abs_tol=1e-12)
                        for item in selected_candidates
                    ):
                        errors.append(
                            "optimal_threshold must select a threshold with the minimum finite positive width"
                        )
                    if not _finite_number(width) or not math.isclose(
                        float(width), minimum_width, rel_tol=1e-12, abs_tol=1e-15
                    ):
                        errors.append(
                            "constraint_width_at_optimal must equal the selected minimum width"
                        )
                if errors:
                    bad.append({"algorithm": algorithm, "errors": errors})
            record.update({
                "ok": set(anchor) == set(algorithms) and not bad and not validation_errors,
                "expected_algorithms": algorithms,
                "actual_algorithms": sorted(anchor),
                "bad_records": bad,
                "validation_errors": validation_errors,
            })
        except Exception as exc:
            _set_failure(record, "phase8_threshold_content_invalid", str(exc))
        checks.append(record)

    for operator in operators:
        for algorithm in algorithms:
            rel_path = os.path.join("data", "phase8", f"csfit_{operator}_{algorithm}.json")
            path = os.path.join(root, rel_path)
            if not os.path.exists(path):
                continue
            record = {
                "rel_path": rel_path + ":numerical_content",
                "severity": "abort",
                "source": "phase8_fit_numerical_content",
                "path": path,
            }
            try:
                data = _load_json(path)
                required = (
                    "fit_intercept_fixed",
                    "f0_label",
                    "sigma0_after_cut_pb",
                    "csfit_sm",
                    "csfit_int",
                    "csfit_np",
                    "fit_model",
                )
                missing = [key for key in required if key not in data]
                errors = []
                if data.get("fit_intercept_fixed") is not True:
                    errors.append("fit_intercept_fixed must be true")
                if data.get("f0_label") != "f5":
                    errors.append("f0_label must be f5")
                if not all(_finite_number(data.get(key)) for key in ("sigma0_after_cut_pb", "csfit_sm", "csfit_int", "csfit_np")):
                    errors.append("fit coefficients must be finite numbers")
                elif not math.isclose(
                    float(data["sigma0_after_cut_pb"]),
                    float(data["csfit_sm"]),
                    rel_tol=1e-12,
                    abs_tol=0.0,
                ):
                    errors.append("csfit_sm must equal sigma0_after_cut_pb")
                if _finite_number(data.get("sigma0_after_cut_pb")) and float(data["sigma0_after_cut_pb"]) <= 0.0:
                    errors.append("sigma0_after_cut_pb must be positive")
                if _finite_number(data.get("csfit_np")) and float(data["csfit_np"]) < 0.0:
                    errors.append("csfit_np must be non-negative")
                record.update({"ok": not missing and not errors, "missing_keys": missing, "invalid_values": errors})
            except Exception as exc:
                _set_failure(record, "phase8_fit_content_invalid", str(exc))
            checks.append(record)
    return checks


def _phase6_progress_checks(root: str) -> List[Dict[str, Any]]:
    rel_path = os.path.join("data", "phase6", "phase6_progress.json")
    path = os.path.join(root, rel_path)
    if not os.path.exists(path):
        return []
    record = {
        "rel_path": rel_path + ":operator_status",
        "severity": "abort",
        "source": "phase6_progress",
        "path": path,
    }
    try:
        data = _load_json(path)
        progress = data.get("operators")
        expected = _operators(root) or []
        if not isinstance(progress, dict):
            raise ValueError("phase6_progress.json operators must be an object")
        actual = set(str(value) for value in progress)
        errors = []
        if actual != set(expected):
            errors.append(
                f"operator keys must equal Phase 3 claims: expected={expected}, actual={sorted(actual)}"
            )
        allowed = {"pending", "running", "failed_retrying", "completed"}
        for operator in expected:
            item = progress.get(operator)
            if not isinstance(item, dict):
                errors.append(f"{operator} progress must be an object")
                continue
            status = item.get("status")
            if status not in allowed:
                errors.append(f"{operator} has invalid status {status!r}")
            if status != "completed":
                errors.append(f"{operator} is not completed: {status!r}")
            labels = item.get("completed_labels")
            if labels != [f"f{index}" for index in range(11)]:
                errors.append(f"{operator}.completed_labels must equal f0 through f10 in order")
        record.update({
            "ok": not errors,
            "expected_operators": expected,
            "actual_operators": sorted(actual),
            "errors": errors,
        })
    except Exception as exc:
        _set_failure(record, "phase6_progress_invalid", str(exc))
    return [record]


def _phase9_numerical_checks(root: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    operators = _operators(root)
    algorithms = _algorithm_names(root)
    selection_path = os.path.join(root, "data", "phase9", "algorithm_selection.json")
    threshold_path = os.path.join(root, "data", "phase8", "threshold_optimization.json")
    selected_algorithm = None
    selected_threshold = None
    selection_scope = None
    operator_selections: Dict[str, Any] = {}
    if os.path.exists(selection_path):
        selection = _load_json(selection_path)
        selected_algorithm = selection.get("selected_algorithm")
        selected_threshold = selection.get("selected_threshold")
        selection_scope = selection.get("selection_scope")
        selection_criterion = selection.get("selection_criterion")
        if selection_scope == "per_operator_best" and isinstance(selection.get("operator_selections"), dict):
            operator_selections = selection["operator_selections"]
        record = {
            "rel_path": "data/phase9/algorithm_selection.json:phase8_match",
            "severity": "abort",
            "source": "phase9_selection_matches_phase8",
            "path": selection_path,
        }
        errors = []
        expected_anchor = None
        if selected_algorithm not in algorithms:
            errors.append("selected_algorithm is not present in Phase 7")
        anchor_path = os.path.join(root, "data", "phase3", "anchor.json")
        if os.path.exists(anchor_path):
            anchor = _load_json(anchor_path)
            expected_anchor = f"o_{anchor.get('global_idx')}"
            if selection.get("anchor_operator") != expected_anchor:
                errors.append("anchor_operator does not match Phase 3 anchor.json")
        else:
            errors.append("Phase 3 anchor.json is missing")
        if os.path.exists(threshold_path) and selected_algorithm in algorithms:
            threshold_data = _load_json(threshold_path)
            threshold_anchor = threshold_data.get("anchor") or {}
            if selection_criterion == "narrowest_anchor_S2_constraint_width":
                expected = (threshold_anchor.get(selected_algorithm) or {}).get("optimal_threshold")
                if not (_finite_number(expected) and _finite_number(selected_threshold)) or not math.isclose(
                    float(expected), float(selected_threshold), rel_tol=0.0, abs_tol=1e-12
                ):
                    errors.append("default selection threshold does not equal the Phase 8 optimal threshold")
                widths = {
                    algorithm: value.get("constraint_width_at_optimal")
                    for algorithm, value in threshold_anchor.items()
                    if isinstance(value, dict) and _finite_number(value.get("constraint_width_at_optimal"))
                }
                if set(widths) != set(algorithms):
                    errors.append("Phase 8 optimal constraint widths do not cover every Phase 7 algorithm")
                elif selected_algorithm in widths:
                    minimum = min(float(value) for value in widths.values())
                    if not math.isclose(float(widths[selected_algorithm]), minimum, rel_tol=1e-12, abs_tol=0.0):
                        errors.append("default selected algorithm does not have the narrowest anchor S2 interval")
            else:
                evaluated = [
                    item.get("threshold")
                    for item in (threshold_anchor.get(selected_algorithm) or {}).get("threshold_scan") or []
                    if isinstance(item, dict) and _finite_number(item.get("threshold"))
                ]
                if not _finite_number(selected_threshold) or not any(
                    math.isclose(float(selected_threshold), float(value), rel_tol=0.0, abs_tol=1e-12)
                    for value in evaluated
                ):
                    errors.append("nondefault selected_threshold is not an evaluated Phase 8 threshold")
            if selection_scope == "per_operator_best":
                comparison_intervals = selection.get("comparison_only_intervals")
                if not isinstance(comparison_intervals, dict):
                    comparison_intervals = {}
                    errors.append(
                        "per_operator_best requires comparison_only_intervals for non-anchor operators"
                    )
                for operator in operators:
                    operator_selection = operator_selections.get(operator) or {}
                    algorithm = operator_selection.get("selected_algorithm")
                    actual_operator_threshold = operator_selection.get("selected_threshold")
                    if operator == expected_anchor:
                        if algorithm != selected_algorithm:
                            errors.append(
                                f"operator_selections.{operator}.selected_algorithm must equal the "
                                "top-level anchor selection"
                            )
                        if not (
                            _finite_number(actual_operator_threshold)
                            and _finite_number(selected_threshold)
                            and math.isclose(
                                float(actual_operator_threshold),
                                float(selected_threshold),
                                rel_tol=0.0,
                                abs_tol=1e-12,
                            )
                        ):
                            errors.append(
                                f"operator_selections.{operator}.selected_threshold must equal the "
                                "top-level anchor threshold"
                            )
                    else:
                        candidates = comparison_intervals.get(operator)
                        if not isinstance(candidates, dict) or not candidates:
                            errors.append(
                                f"comparison_only_intervals.{operator} must contain at least one "
                                "evaluated strategy usable under the selected debug setting"
                            )
                            continue
                        widths: Dict[str, float] = {}
                        for candidate_algorithm, candidate in candidates.items():
                            if candidate_algorithm not in algorithms or not isinstance(candidate, dict):
                                errors.append(
                                    f"comparison_only_intervals.{operator}.{candidate_algorithm} is invalid"
                                )
                                continue
                            interval = candidate.get("S2")
                            threshold = candidate.get("selected_threshold")
                            if not _valid_interval(interval) or not _finite_number(threshold):
                                errors.append(
                                    f"comparison_only_intervals.{operator}.{candidate_algorithm} must "
                                    "contain a valid S2 interval and numeric selected_threshold"
                                )
                                continue
                            widths[candidate_algorithm] = float(interval[1]) - float(interval[0])
                        selected_candidate = candidates.get(algorithm) or {}
                        expected_operator_threshold = selected_candidate.get("selected_threshold")
                        if algorithm not in widths:
                            errors.append(
                                f"operator_selections.{operator}.selected_algorithm is not a valid "
                                "recorded candidate"
                            )
                        elif not math.isclose(
                            widths[algorithm], min(widths.values()), rel_tol=1e-12, abs_tol=0.0
                        ):
                            errors.append(
                                f"operator_selections.{operator}.selected_algorithm does not have the "
                                "narrowest recorded S2 constraint interval"
                            )
                        if not (
                            _finite_number(expected_operator_threshold)
                            and _finite_number(actual_operator_threshold)
                            and math.isclose(
                                float(expected_operator_threshold),
                                float(actual_operator_threshold),
                                rel_tol=0.0,
                                abs_tol=1e-12,
                            )
                        ):
                            errors.append(
                                f"operator_selections.{operator}.selected_threshold differs from the "
                                "recorded minimum-width candidate"
                            )
        else:
            errors.append("Phase 8 threshold_optimization.json is missing or selected algorithm is invalid")
        record.update({"ok": not errors, "invalid_values": errors})
        checks.append(record)

    table_rel = os.path.join("data", "phase9", "constraint_table.json")
    table_path = os.path.join(root, table_rel)
    if os.path.exists(table_path):
        record = {
            "rel_path": table_rel + ":numerical_content",
            "severity": "abort",
            "source": "phase9_constraint_numerical_content",
            "path": table_path,
        }
        try:
            data = _load_json(table_path)
            constraints = data.get("constraints")
            bad = _numerical_validation_errors(data)
            if data.get("selection_scope") != selection_scope:
                bad.append("selection_scope differs from algorithm_selection.json")
            if selection_scope == "anchor_operator_only":
                if data.get("selected_algorithm") != selected_algorithm:
                    bad.append("selected_algorithm differs from algorithm_selection.json")
            elif selection_scope == "per_operator_best":
                if data.get("operator_selections") != operator_selections:
                    bad.append("operator_selections differs from algorithm_selection.json")
            else:
                bad.append("selection_scope must be anchor_operator_only or per_operator_best")
            if not isinstance(constraints, dict):
                bad.append("constraints must be an object")
                constraints = {}
            if set(constraints) != set(operators):
                bad.append("constraints keys must exactly match Phase 3 claimed operators")
            invalid_intervals = []
            for operator in operators:
                value = constraints.get(operator)
                if not isinstance(value, dict):
                    invalid_intervals.append({"operator": operator, "error": "missing constraint object"})
                    continue
                if selection_scope == "per_operator_best":
                    expected_selection = operator_selections.get(operator) or {}
                    if value.get("selected_algorithm") != expected_selection.get("selected_algorithm"):
                        invalid_intervals.append({
                            "operator": operator,
                            "error": "selected_algorithm differs from operator_selections",
                        })
                    expected_threshold = expected_selection.get("selected_threshold")
                    actual_threshold = value.get("selected_threshold")
                    if not (
                        _finite_number(expected_threshold)
                        and _finite_number(actual_threshold)
                        and math.isclose(
                            float(expected_threshold),
                            float(actual_threshold),
                            rel_tol=0.0,
                            abs_tol=1e-12,
                        )
                    ):
                        invalid_intervals.append({
                            "operator": operator,
                            "error": "selected_threshold differs from operator_selections",
                        })
                for significance in ("S2", "S3", "S5"):
                    if not _valid_interval(value.get(significance)):
                        invalid_intervals.append({"operator": operator, "significance": significance, "value": value.get(significance)})
            record.update({"ok": not bad and not invalid_intervals, "invalid_values": bad, "invalid_intervals": invalid_intervals})
        except Exception as exc:
            _set_failure(record, "phase9_constraint_content_invalid", str(exc))
        checks.append(record)

    csv_rel = os.path.join("data", "phase9", "constraint_table.csv")
    csv_path = os.path.join(root, csv_rel)
    required_columns = (
        "operator",
        "selected_algorithm",
        "selected_threshold",
        "S2_lower",
        "S2_upper",
        "S3_lower",
        "S3_upper",
        "S5_lower",
        "S5_upper",
    )
    csv_record = {
        "rel_path": csv_rel + ":content",
        "severity": "abort",
        "source": "phase9_constraint_csv_content",
        "path": csv_path,
    }
    csv_errors = []
    try:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            missing_columns = [
                column for column in required_columns
                if not reader.fieldnames or column not in reader.fieldnames
            ]
            rows = list(reader)
        if missing_columns:
            csv_errors.append(f"missing columns: {missing_columns}")
        row_operators = [row.get("operator") for row in rows]
        if len(rows) != len(operators) or set(row_operators) != set(operators):
            csv_errors.append("CSV must contain exactly one row per claimed operator")
        if len(row_operators) != len(set(row_operators)):
            csv_errors.append("CSV contains duplicate operator rows")
        table_data = _load_json(table_path) if os.path.exists(table_path) else {}
        table_constraints = table_data.get("constraints") or {}
        for row_number, row in enumerate(rows, start=2):
            operator = row.get("operator")
            expected_constraint = table_constraints.get(operator) or {}
            if selection_scope == "per_operator_best":
                expected_selection = operator_selections.get(operator) or {}
                expected_algorithm = expected_selection.get("selected_algorithm")
                expected_threshold = expected_selection.get("selected_threshold")
            else:
                expected_algorithm = selected_algorithm
                expected_threshold = selected_threshold
            if row.get("selected_algorithm") != expected_algorithm:
                csv_errors.append(f"row {row_number} selected_algorithm differs from JSON")
            try:
                actual_threshold = float(row.get("selected_threshold", ""))
                if not _finite_number(expected_threshold) or not math.isclose(
                    actual_threshold, float(expected_threshold), rel_tol=0.0, abs_tol=1e-12
                ):
                    csv_errors.append(f"row {row_number} selected_threshold differs from JSON")
            except (TypeError, ValueError):
                csv_errors.append(f"row {row_number} selected_threshold must be numeric")
            for significance in ("S2", "S3", "S5"):
                expected_interval = expected_constraint.get(significance)
                try:
                    actual_interval = [
                        float(row.get(f"{significance}_lower", "")),
                        float(row.get(f"{significance}_upper", "")),
                    ]
                except (TypeError, ValueError):
                    csv_errors.append(f"row {row_number} {significance} bounds must be numeric")
                    continue
                if not _valid_interval(expected_interval) or any(
                    not math.isclose(actual, float(expected), rel_tol=1e-12, abs_tol=1e-15)
                    for actual, expected in zip(actual_interval, expected_interval)
                ):
                    csv_errors.append(f"row {row_number} {significance} differs from JSON")
        csv_record.update({
            "ok": not csv_errors,
            "row_count": len(rows),
            "errors": csv_errors,
        })
    except Exception as exc:
        _set_failure(csv_record, "phase9_constraint_csv_invalid", str(exc))
    checks.append(csv_record)
    return checks


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
    deletion_keys = [
        "deleted_files",
        "removed_files",
        "deleted_large_files",
        "removed_large_files",
    ]
    deleted_paths = []
    for key in deletion_keys:
        values = data.get(key)
        if isinstance(values, list):
            deleted_paths.extend(str(value) for value in values)
    forbidden_deleted = [
        path for path in deleted_paths
        if not path.lower().endswith((".root", ".hepmc", ".hepmc.gz"))
    ]
    manifest_process_names = set()
    manifest_order_names = set()
    data_root = os.path.join(root, "data")
    if os.path.isdir(data_root):
        for current, _, filenames in os.walk(data_root):
            for filename in filenames:
                if not filename.endswith(".json"):
                    continue
                manifest_path = os.path.join(current, filename)
                try:
                    manifest_data = _load_json(manifest_path)
                except Exception:
                    continue
                for item in _iter_json_objects(manifest_data):
                    broken = item.get("broken_process_dir")
                    process = item.get("process_dir")
                    chosen_process = broken or process
                    if isinstance(chosen_process, str) and chosen_process:
                        manifest_process_names.add(os.path.basename(os.path.normpath(chosen_process)))
                    order = item.get("order_file_path")
                    if isinstance(order, str) and order:
                        manifest_order_names.add(os.path.basename(os.path.normpath(order)))
    accounting_errors = []
    for kind in ("process_dirs", "order_files"):
        expected_key = f"expected_{kind}"
        moved_key = f"moved_{kind}"
        missing_key = f"missing_{kind}"
        expected_values = [str(value) for value in data.get(expected_key) or []]
        moved_values = [str(value) for value in data.get(moved_key) or []]
        missing_values = [str(value) for value in data.get(missing_key) or []]
        expected_names = [os.path.basename(os.path.normpath(value)) for value in expected_values]
        moved_names = [os.path.basename(os.path.normpath(value)) for value in moved_values]
        missing_names = [os.path.basename(os.path.normpath(value)) for value in missing_values]
        if len(expected_names) != len(set(expected_names)):
            accounting_errors.append(f"{expected_key} contains duplicate basenames")
        if set(expected_names) != set(moved_names) | set(missing_names):
            accounting_errors.append(
                f"{expected_key} must equal {moved_key} plus {missing_key} by basename"
            )
        overlap = sorted(set(moved_names) & set(missing_names))
        if overlap:
            accounting_errors.append(f"{moved_key} and {missing_key} overlap: {overlap}")
        if missing_values:
            accounting_errors.append(f"{missing_key} must be empty before cleanup completes")
        absent_moved = [value for value in moved_values if not os.path.exists(value)]
        if absent_moved:
            accounting_errors.append(f"{moved_key} paths do not exist: {absent_moved}")
        manifest_names = manifest_process_names if kind == "process_dirs" else manifest_order_names
        if manifest_names and set(expected_names) != manifest_names:
            accounting_errors.append(
                f"{expected_key} does not match runner manifests: "
                f"expected={sorted(manifest_names)}, logged={sorted(set(expected_names))}"
            )
    checks.append({
        "rel_path": rel_path,
        "severity": "abort",
        "source": "cleanup_log",
        "path": path,
        "ok": not missing and not no_expected_records and not forbidden_deleted and not accounting_errors,
        "missing_or_nonlist_keys": missing,
        "no_expected_records": no_expected_records,
        "deleted_file_keys_checked": deletion_keys,
        "forbidden_deleted_files": forbidden_deleted,
        "accounting_errors": accounting_errors,
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


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: str) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _replay_algorithm_lock_checks(root: str) -> List[Dict[str, Any]]:
    manifest_rel = os.path.join("replay", "replay_manifest.json")
    manifest_path = os.path.join(root, manifest_rel)
    if not os.path.exists(manifest_path):
        return []
    record: Dict[str, Any] = {
        "rel_path": manifest_rel + ":algorithm_lock",
        "severity": "abort",
        "source": "phase11_algorithm_lock",
        "path": manifest_path,
    }
    try:
        manifest = _load_json(manifest_path)
        lock = manifest.get("algorithm_lock")
        if not isinstance(lock, dict):
            raise ValueError("replay_manifest.json is missing algorithm_lock object")
        stored_hash = lock.get("lock_sha256")
        lock_payload = {key: value for key, value in lock.items() if key != "lock_sha256"}
        if stored_hash != _canonical_sha256(lock_payload):
            raise ValueError("algorithm_lock.lock_sha256 does not match its canonical payload")

        comparison = _load_json(os.path.join(root, "data", "phase7", "algorithm_comparison.json"))
        expected_algorithms = set((comparison.get("anchor") or {}).keys())
        expected_selection_seed = comparison.get("algorithm_selection_seed")
        selection_seed_ok = (
            isinstance(expected_selection_seed, int)
            and not isinstance(expected_selection_seed, bool)
            and lock.get("algorithm_selection_seed") == expected_selection_seed
        )
        descriptions = _algorithm_description_map(
            _load_json(os.path.join(root, "data", "phase7", "algorithm_descriptions.json"))
        )
        trained = lock.get("trained_algorithms")
        if not isinstance(trained, list):
            raise ValueError("algorithm_lock.trained_algorithms must be a list")
        trained_map = {
            str(item.get("key")): item
            for item in trained
            if isinstance(item, dict) and item.get("key")
        }
        if set(trained_map) != expected_algorithms:
            raise ValueError(
                "algorithm_lock trained keys do not match Phase 7 anchor algorithms: "
                f"expected={sorted(expected_algorithms)}, actual={sorted(trained_map)}"
            )

        bad_algorithms = []
        for algorithm in sorted(expected_algorithms):
            frozen = trained_map[algorithm]
            source = descriptions.get(algorithm, {})
            missing = [
                key
                for key in (
                    "implementation",
                    "hyperparameters",
                    "random_seed",
                    "score_definition",
                    "model_output",
                )
                if key not in frozen or frozen.get(key) in (None, "")
            ]
            mismatches = []
            source_params = source.get("hyperparameters", source.get("params"))
            source_seed = source.get("random_seed", source.get("seed"))
            source_score = source.get("score_definition", source.get("score"))
            source_implementation = (
                source.get("implementation")
                or source.get("class_path")
                or source.get("class_name")
            )
            if source_params is not None and frozen.get("hyperparameters") != source_params:
                mismatches.append("hyperparameters")
            if source_seed is None or frozen.get("random_seed") != source_seed:
                mismatches.append("random_seed")
            if source_score is not None and frozen.get("score_definition") != source_score:
                mismatches.append("score_definition")
            if source_implementation is not None and frozen.get("implementation") != source_implementation:
                mismatches.append("implementation")
            expected_model = f"algorithms/anchor_{algorithm}.pkl"
            if str(frozen.get("model_output", "")).replace("\\", "/") != expected_model:
                mismatches.append("model_output")
            if missing or mismatches:
                bad_algorithms.append({
                    "algorithm": algorithm,
                    "missing": missing,
                    "source_mismatches": mismatches,
                })

        selection = _load_json(os.path.join(root, "data", "phase9", "algorithm_selection.json"))
        expected_production = selection.get("selected_algorithm")
        production_ok = lock.get("production_algorithm") == expected_production
        expected_scope = selection.get("selection_scope")
        actual_scope = lock.get("selection_scope")
        scope_ok = actual_scope == expected_scope
        operator_selections_ok = isinstance(lock.get("operator_selections"), dict)
        if expected_scope == "per_operator_best":
            operator_selections_ok = (
                isinstance(selection.get("operator_selections"), dict)
                and lock.get("operator_selections") == selection.get("operator_selections")
            )
        elif expected_scope == "anchor_operator_only":
            operator_selections_ok = operator_selections_ok and not lock.get("operator_selections")
        provenance = lock.get("selection_provenance")
        provenance_ok = (
            isinstance(provenance, dict)
            and provenance.get("selection_method") == selection.get("selection_criterion")
            and provenance.get("selection_rationale") == selection.get("selection_rationale")
            and provenance.get("selection_evidence") == selection.get("selection_evidence")
            and provenance.get("source") == "data/phase9/algorithm_selection.json"
        )

        packaged_files = lock.get("packaged_files")
        bad_files = []
        phase7_references = set()
        for step in manifest.get("steps") or []:
            if not isinstance(step, dict) or str(step.get("phase")) != "7":
                continue
            for rel in (step.get("sha256") or {}).keys():
                if isinstance(rel, str):
                    phase7_references.add(rel.replace("\\", "/").lstrip("./"))
            for token in step.get("command") or []:
                if isinstance(token, str) and token.endswith((".py", ".sh")):
                    phase7_references.add(token.replace("\\", "/").lstrip("./"))
        if not isinstance(packaged_files, dict) or not packaged_files:
            bad_files.append({"error": "algorithm_lock.packaged_files must be a non-empty checksum map"})
        else:
            packaged_normalized = {
                str(rel).replace("\\", "/").lstrip("./") for rel in packaged_files
            }
            missing_phase7_files = sorted(phase7_references - packaged_normalized)
            if missing_phase7_files:
                bad_files.append({
                    "error": "Phase 7 replay files are missing from algorithm_lock.packaged_files",
                    "paths": missing_phase7_files,
                })
            replay_root = os.path.join(root, "replay")
            for rel, expected_hash in sorted(packaged_files.items()):
                rel_norm = str(rel).replace("\\", "/").lstrip("./")
                full_path = os.path.abspath(os.path.join(replay_root, rel_norm))
                if not _path_is_within(full_path, replay_root):
                    bad_files.append({"path": rel, "error": "path escapes replay package"})
                elif not os.path.isfile(full_path):
                    bad_files.append({"path": rel, "error": "packaged algorithm file is missing"})
                elif _file_sha256(full_path) != expected_hash:
                    bad_files.append({"path": rel, "error": "SHA-256 mismatch"})

        ok = (
            selection_seed_ok
            and not bad_algorithms
            and production_ok
            and scope_ok
            and operator_selections_ok
            and provenance_ok
            and not bad_files
        )
        record.update({
            "ok": ok,
            "trained_algorithms": sorted(trained_map),
            "algorithm_selection_seed_ok": selection_seed_ok,
            "bad_algorithms": bad_algorithms,
            "expected_production_algorithm": expected_production,
            "actual_production_algorithm": lock.get("production_algorithm"),
            "expected_selection_scope": expected_scope,
            "actual_selection_scope": actual_scope,
            "operator_selections_ok": operator_selections_ok,
            "selection_provenance_ok": provenance_ok,
            "bad_packaged_files": bad_files,
        })
        if not ok:
            record["failure_reason"] = (
                "Phase 11 did not freeze the actual Phase 7/9 algorithms, parameters, "
                "random seeds, selection criterion, rationale, evidence, operator assignments, and "
                "packaged implementation checksums consistently"
            )
    except Exception as exc:
        _set_failure(record, "algorithm_lock_invalid", str(exc))
    return [record]


def _normalized_manifest_path(value: Any) -> Optional[str]:
    if not isinstance(value, str) or not value.strip():
        return None
    normalized = value.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if (
        not normalized
        or normalized.startswith("/")
        or re.match(r"^[A-Za-z]:/", normalized)
        or ".." in normalized.split("/")
    ):
        return None
    if normalized.startswith("replayed-results/"):
        normalized = normalized[len("replayed-results/"):]
    return normalized


def _replay_package_checks(root: str) -> List[Dict[str, Any]]:
    manifest_rel = os.path.join("replay", "replay_manifest.json")
    manifest_path = os.path.join(root, manifest_rel)
    if not os.path.exists(manifest_path):
        return []
    record: Dict[str, Any] = {
        "rel_path": manifest_rel + ":coverage_and_independence",
        "severity": "abort",
        "source": "phase11_replay_coverage_and_independence",
        "path": manifest_path,
    }
    try:
        manifest = _load_json(manifest_path)
        steps = manifest.get("steps")
        if not isinstance(steps, list) or not steps:
            raise ValueError("replay_manifest.json steps must be a non-empty list")
        manifest_errors = []
        if manifest.get("schema_version") != "1.0":
            manifest_errors.append("schema_version must be 1.0")
        if manifest.get("entrypoint") != "replay.sh":
            manifest_errors.append("entrypoint must be replay.sh")
        if manifest.get("phase_order") != [str(value) for value in range(2, 10)]:
            manifest_errors.append("phase_order must equal 2 through 9")
        if not isinstance(manifest.get("default_output"), str) or not manifest["default_output"].strip():
            manifest_errors.append("default_output must be a non-empty relative path")
        elif _normalized_manifest_path(manifest["default_output"]) is None:
            manifest_errors.append("default_output must be package-relative")
        if manifest.get("report") != "data_files_report.md":
            manifest_errors.append("report must be data_files_report.md")

        replay_root = os.path.join(root, "replay")
        replay_path = os.path.join(replay_root, "replay.sh")
        if os.path.isfile(replay_path):
            with open(replay_path, "r", encoding="utf-8-sig", errors="replace") as handle:
                replay_text = handle.read()
            if not replay_text.startswith("#!/"):
                manifest_errors.append("replay.sh must start with a shebang")
            if "set -euo pipefail" not in replay_text:
                manifest_errors.append("replay.sh must enable set -euo pipefail")
        package_checksums = manifest.get("package_sha256")
        package_checksum_errors = []
        if not isinstance(package_checksums, dict) or not package_checksums:
            package_checksum_errors.append("package_sha256 must be a non-empty map")
            package_checksums = {}
        mandatory_package_files = {
            "replay.sh",
            "run_config.json",
            "research_contract.json",
            "deliverables_contract.json",
            "contract_lock.json",
            "data_files_report.md",
        }
        source_inputs = manifest.get("source_inputs")
        source_input_errors = []
        if not isinstance(source_inputs, list):
            source_input_errors.append("source_inputs must be a list")
            source_inputs = []
        for index, item in enumerate(source_inputs):
            if not isinstance(item, dict) or any(
                key not in item for key in ("path", "sha256", "provided_before_phase2")
            ):
                source_input_errors.append(f"source_inputs[{index}] is missing required fields")
                continue
            if item.get("provided_before_phase2") is not True:
                source_input_errors.append(f"source_inputs[{index}].provided_before_phase2 must be true")
            if not isinstance(item.get("path"), str) or not item["path"].strip():
                source_input_errors.append(f"source_inputs[{index}].path must be non-empty")
                continue
            rel_path = _normalized_manifest_path(item["path"])
            full_path = os.path.abspath(os.path.join(replay_root, rel_path or ""))
            if not rel_path or not rel_path.startswith("inputs/") or not _path_is_within(full_path, replay_root):
                source_input_errors.append(f"source_inputs[{index}].path must stay under replay/inputs")
            elif not os.path.isfile(full_path):
                source_input_errors.append(f"source_inputs[{index}] file is missing: {rel_path}")
            if not isinstance(item.get("sha256"), str) or re.fullmatch(r"[0-9a-fA-F]{64}", item["sha256"]) is None:
                source_input_errors.append(f"source_inputs[{index}].sha256 must contain 64 hexadecimal characters")
            elif os.path.isfile(full_path) and _file_sha256(full_path) != item["sha256"].lower():
                source_input_errors.append(f"source_inputs[{index}] SHA-256 mismatch: {rel_path}")

        external_dependency_errors = []
        external_dependencies = manifest.get("external_dependencies")
        if not isinstance(external_dependencies, list) or not external_dependencies:
            external_dependency_errors.append("external_dependencies must be a non-empty list")
        else:
            dependency_names = []
            for index, item in enumerate(external_dependencies):
                if not isinstance(item, dict):
                    external_dependency_errors.append(f"external_dependencies[{index}] must be an object")
                    continue
                for key in ("name", "path", "version"):
                    if not isinstance(item.get(key), str) or not item[key].strip():
                        external_dependency_errors.append(f"external_dependencies[{index}].{key} must be non-empty")
                if isinstance(item.get("name"), str):
                    dependency_names.append(item["name"].lower())
                checksum = item.get("sha256")
                if checksum is None:
                    if not isinstance(item.get("checksum_unavailable_reason"), str) or not item["checksum_unavailable_reason"].strip():
                        external_dependency_errors.append(
                            f"external_dependencies[{index}] needs sha256 or checksum_unavailable_reason"
                        )
                elif not isinstance(checksum, str) or re.fullmatch(r"[0-9a-fA-F]{64}", checksum) is None:
                    external_dependency_errors.append(f"external_dependencies[{index}].sha256 is invalid")
            required_dependency_names = {
                "MadGraph": ("madgraph", "mg5"),
                "Pythia": ("pythia",),
                "Delphes": ("delphes",),
                "root2lhco": ("root2lhco",),
                "CutExperiment": ("cutexperiment",),
                "Python": ("python",),
            }
            for display_name, aliases in required_dependency_names.items():
                if not any(any(alias in name for alias in aliases) for name in dependency_names):
                    external_dependency_errors.append(
                        f"external_dependencies lacks {display_name} identity"
                    )
        observed_phases = [str(step.get("phase")) for step in steps if isinstance(step, dict)]
        unique_phase_order = []
        for phase in observed_phases:
            if not unique_phase_order or unique_phase_order[-1] != phase:
                unique_phase_order.append(phase)
        order_ok = unique_phase_order == [str(value) for value in range(2, 10)]

        outputs: Dict[str, int] = {}
        forbidden_inputs = []
        checksum_errors = []
        declared_checksums: Dict[str, str] = {}
        referenced_code = set()
        referenced_packaged_files = set(mandatory_package_files)
        for index, step in enumerate(steps):
            if not isinstance(step, dict):
                manifest_errors.append(f"steps[{index}] must be an object")
                continue
            command = step.get("command")
            if not isinstance(command, list) or not command or not all(isinstance(token, str) for token in command):
                manifest_errors.append(f"steps[{index}].command must be a non-empty string list")
                command = []
            for token in command:
                normalized_token = _normalized_manifest_path(token)
                if normalized_token is None:
                    if token.replace("\\", "/").endswith((".py", ".sh")):
                        manifest_errors.append(f"steps[{index}] command path escapes replay package: {token}")
                    continue
                if normalized_token.startswith(("steps/", "support/")) or normalized_token.endswith((".py", ".sh")):
                    referenced_code.add(normalized_token)
                    referenced_packaged_files.add(normalized_token)
            checksums = step.get("sha256")
            if not isinstance(checksums, dict) or not checksums:
                checksum_errors.append(f"steps[{index}].sha256 must be a non-empty map")
            else:
                for rel, expected_hash in checksums.items():
                    rel_norm = _normalized_manifest_path(str(rel))
                    if rel_norm is None:
                        checksum_errors.append(f"checksum path must be package-relative: {rel}")
                        continue
                    if rel_norm in declared_checksums and declared_checksums[rel_norm] != expected_hash:
                        checksum_errors.append(f"conflicting SHA-256 values for {rel_norm}")
                    declared_checksums[rel_norm] = expected_hash
            for value in step.get("outputs") or []:
                normalized = _normalized_manifest_path(value)
                if normalized:
                    outputs[normalized] = outputs.get(normalized, 0) + 1
                else:
                    manifest_errors.append(f"steps[{index}] output path must be package-relative: {value!r}")
            for value in step.get("inputs") or []:
                normalized = _normalized_manifest_path(value)
                if normalized:
                    candidate = os.path.abspath(os.path.join(replay_root, normalized))
                    if _path_is_within(candidate, replay_root) and os.path.isfile(candidate):
                        referenced_packaged_files.add(normalized)
                else:
                    manifest_errors.append(f"steps[{index}] input path must be package-relative: {value!r}")
                if normalized and any(
                    normalized.startswith(f"data/phase{phase}/") for phase in range(3, 10)
                ):
                    forbidden_inputs.append({"step_index": index, "path": value})

        for rel, expected_hash in sorted(declared_checksums.items()):
            full_path = os.path.abspath(os.path.join(replay_root, rel))
            if not _path_is_within(full_path, replay_root):
                checksum_errors.append(f"checksum path escapes replay package: {rel}")
            elif not os.path.isfile(full_path):
                checksum_errors.append(f"checksummed package file is missing: {rel}")
            elif not isinstance(expected_hash, str) or re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash) is None:
                checksum_errors.append(f"invalid SHA-256 for {rel}")
            elif _file_sha256(full_path) != expected_hash.lower():
                checksum_errors.append(f"SHA-256 mismatch for {rel}")
        missing_code_checksums = sorted(referenced_code - set(declared_checksums))
        if missing_code_checksums:
            checksum_errors.append(
                "referenced code lacks a step checksum: " + ", ".join(missing_code_checksums)
            )
        missing_package_checksums = sorted(referenced_packaged_files - set(package_checksums))
        packaged_files = set()
        if os.path.isdir(replay_root):
            for current, directories, filenames in os.walk(replay_root):
                directories[:] = [name for name in directories if name != "__pycache__"]
                for filename in filenames:
                    rel = os.path.relpath(os.path.join(current, filename), replay_root).replace("\\", "/")
                    if rel != "replay_manifest.json" and not filename.endswith((".pyc", ".pyo")):
                        packaged_files.add(rel)
        missing_package_checksums.extend(sorted(packaged_files - set(package_checksums)))
        missing_package_checksums = sorted(set(missing_package_checksums))
        if missing_package_checksums:
            package_checksum_errors.append(
                "packaged files lack package_sha256 entries: " + ", ".join(missing_package_checksums)
            )
        for rel, expected_hash in sorted(package_checksums.items()):
            rel_norm = _normalized_manifest_path(str(rel))
            if rel_norm is None:
                package_checksum_errors.append(f"package checksum path must be package-relative: {rel}")
                continue
            full_path = os.path.abspath(os.path.join(replay_root, rel_norm))
            if not _path_is_within(full_path, replay_root):
                package_checksum_errors.append(f"package checksum path escapes replay package: {rel}")
            elif not os.path.isfile(full_path):
                package_checksum_errors.append(f"package checksum file is missing: {rel}")
            elif not isinstance(expected_hash, str) or re.fullmatch(r"[0-9a-fA-F]{64}", expected_hash) is None:
                package_checksum_errors.append(f"invalid package SHA-256 for {rel}")
            elif _file_sha256(full_path) != expected_hash.lower():
                package_checksum_errors.append(f"package SHA-256 mismatch for {rel}")

        results_root = _global_results_root(root)
        config_path = os.path.join(results_root, "run_config.json")
        resolved = resolve_contract(
            config_path,
            run_root=root,
            results_dir=results_root,
            phases=[str(value) for value in range(2, 10)],
            write_output=False,
        )
        if resolved.get("pending_rules"):
            raise ValueError(
                f"Phase 2-9 deliverables cannot be resolved: {resolved['pending_rules']}"
            )
        expected_outputs = {
            str(item["path"]).replace("\\", "/")
            for item in resolved.get("resolved") or []
            if str(item.get("phase")) in {str(value) for value in range(2, 10)}
        }
        coverage_counts = {
            expected: sum(
                count for declared, count in outputs.items()
                if fnmatch.fnmatchcase(expected, declared)
            )
            for expected in expected_outputs
        }
        missing_outputs = sorted(path for path, count in coverage_counts.items() if count == 0)
        duplicate_outputs = sorted(path for path, count in coverage_counts.items() if count != 1 and count > 0)

        original_path_mentions = []
        original_root_text = os.path.abspath(root).replace("\\", "/")
        for directory in ("steps", "support"):
            base = os.path.join(replay_root, directory)
            if not os.path.isdir(base):
                continue
            for current, _, names in os.walk(base):
                for name in names:
                    if not name.endswith((".py", ".sh")):
                        continue
                    path = os.path.join(current, name)
                    with open(path, "r", encoding="utf-8-sig", errors="replace") as handle:
                        text = handle.read().replace("\\", "/")
                    if original_root_text in text or "../data/" + "phase" in text:
                        original_path_mentions.append(os.path.relpath(path, replay_root).replace("\\", "/"))

        immutable_copy_errors = []
        for name in ("run_config.json", "research_contract.json", "deliverables_contract.json", "contract_lock.json"):
            source = os.path.join(results_root, name)
            packaged = os.path.join(replay_root, name)
            if not os.path.isfile(source) or not os.path.isfile(packaged):
                immutable_copy_errors.append({"file": name, "error": "source or packaged copy missing"})
                continue
            if _load_json(source) != _load_json(packaged):
                immutable_copy_errors.append({"file": name, "error": "packaged JSON content differs from source"})

        ok = not any((
            manifest_errors,
            source_input_errors,
            external_dependency_errors,
            checksum_errors,
            package_checksum_errors,
            missing_outputs,
            duplicate_outputs,
            forbidden_inputs,
            original_path_mentions,
            immutable_copy_errors,
        )) and order_ok
        record.update({
            "ok": ok,
            "observed_phase_order": unique_phase_order,
            "expected_phase_order": [str(value) for value in range(2, 10)],
            "manifest_errors": manifest_errors,
            "source_input_errors": source_input_errors,
            "external_dependency_errors": external_dependency_errors,
            "checksum_errors": checksum_errors,
            "package_checksum_errors": package_checksum_errors,
            "missing_manifest_outputs": missing_outputs,
            "duplicate_manifest_outputs": duplicate_outputs,
            "forbidden_original_result_inputs": forbidden_inputs,
            "packaged_code_original_path_mentions": original_path_mentions,
            "immutable_copy_errors": immutable_copy_errors,
        })
    except Exception as exc:
        _set_failure(record, "phase11_replay_package_invalid", str(exc))
    return [record]


def _workflow_contract_binding_checks(root: str) -> List[Dict[str, Any]]:
    log_rel = "workflow.log"
    log_path = os.path.join(root, log_rel)
    if not os.path.exists(log_path):
        return []
    current = os.path.abspath(root)
    results_root = None
    while True:
        if os.path.basename(current).lower() == "results":
            results_root = current
            break
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    contract_path = os.path.join(results_root or root, "research_contract.json")
    record: Dict[str, Any] = {
        "rel_path": log_rel + ":objective_sha256",
        "severity": "abort",
        "source": "workflow_contract_binding",
        "path": log_path,
    }
    try:
        expected = _load_json(contract_path).get("objective_sha256")
        record_count = 0
        mismatches = []
        with open(log_path, "r", encoding="utf-8-sig") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                item = json.loads(line)
                record_count += 1
                if item.get("objective_sha256") != expected:
                    mismatches.append(line_number)
        record.update({
            "ok": bool(record_count) and not mismatches,
            "record_count": record_count,
            "expected_objective_sha256": expected,
            "mismatched_record_numbers": mismatches,
        })
        if not record["ok"]:
            record["failure_reason"] = (
                "Every workflow record must be bound to the frozen research objective hash"
            )
    except Exception as exc:
        _set_failure(record, "workflow_objective_binding_invalid", str(exc))
    return [record]


def _ensure_failure_diagnostics(checks: List[Dict[str, Any]]) -> None:
    for check in checks:
        if check.get("ok") or check.get("severity") == "info":
            continue
        if not check.get("failure_code"):
            check["failure_code"] = str(check.get("source") or "acceptance") + "_failed"
        if not check.get("failure_reason"):
            check["failure_reason"] = str(
                check.get("error")
                or f"Acceptance check failed for {check.get('rel_path', check.get('path', '<unknown>'))}; inspect the structured diagnostic fields"
            )


def _final_audit_artifact_checks(root: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    expected_path = os.path.join(root, "audit_expected_outputs.json")
    report_path = os.path.join(root, "audit_report.json")
    expected_status = None
    try:
        expected = _load_json(expected_path)
        expected_status = expected.get("status")
        missing = [
            key for key in ("status", "checks", "failures", "warnings", "expected_count")
            if key not in expected
        ]
        checks.append({
            "rel_path": "audit_expected_outputs.json:schema",
            "severity": "abort",
            "source": "phase12_final_artifact_schema",
            "path": expected_path,
            "ok": expected.get("status") in {"PASS", "WARN", "FAIL"}
            and isinstance(expected.get("checks"), list)
            and isinstance(expected.get("failures"), list)
            and isinstance(expected.get("warnings"), list)
            and not missing,
            "missing_keys": missing,
        })
    except Exception as exc:
        checks.append({
            "rel_path": "audit_expected_outputs.json:schema",
            "severity": "abort",
            "source": "phase12_final_artifact_schema",
            "path": expected_path,
            "ok": False,
            "error": str(exc),
        })

    try:
        report = _load_json(report_path)
        required_categories = {
            "research_contract",
            "deliverables_contract",
            "file_existence",
            "numerical_sanity",
            "cross_phase_consistency",
        }
        categories = report.get("checks") if isinstance(report.get("checks"), dict) else {}
        missing = [
            key for key in ("status", "checks", "abort_reasons", "warnings", "manuscript_validation_status")
            if key not in report
        ]
        bad_categories = []
        for category in sorted(required_categories):
            value = categories.get(category)
            if not isinstance(value, dict) or any(key not in value for key in ("passed", "failed", "details")):
                bad_categories.append(category)
        checks.append({
            "rel_path": "audit_report.json:schema",
            "severity": "abort",
            "source": "phase12_final_artifact_schema",
            "path": report_path,
            "ok": report.get("status") in {"PASS", "WARN", "FAIL"}
            and report.get("status") == expected_status
            and not missing
            and not bad_categories
            and isinstance(report.get("abort_reasons"), list)
            and isinstance(report.get("warnings"), list),
            "missing_keys": missing,
            "bad_check_categories": bad_categories,
            "expected_status": expected_status,
            "actual_status": report.get("status"),
        })
    except Exception as exc:
        checks.append({
            "rel_path": "audit_report.json:schema",
            "severity": "abort",
            "source": "phase12_final_artifact_schema",
            "path": report_path,
            "ok": False,
            "error": str(exc),
        })
    return checks


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
            config = _load_json(os.path.join(_global_results_root(root), "run_config.json"))
            configured_algorithms = config.get("algorithms")
            expected_algorithm_keys = (
                {str(value) for value in configured_algorithms}
                if isinstance(configured_algorithms, list) and configured_algorithms
                else None
            )
            selection_seed = data.get("algorithm_selection_seed")
            selection_seed_ok = (
                isinstance(selection_seed, int)
                and not isinstance(selection_seed, bool)
            )
            effective_algorithms = []
            for alg, record in sorted(anchor.items()):
                if not isinstance(record, dict):
                    bad.append({"algorithm": alg, "error": "record is not an object"})
                    continue
                auc = record.get("auc")
                try:
                    auc_value = float(auc)
                    auc_ok = 0.0 <= auc_value <= 1.0
                except (TypeError, ValueError):
                    auc_value = None
                    auc_ok = False
                if auc_value is not None and 0.5 < auc_value <= 1.0:
                    effective_algorithms.append(alg)
                missing = [
                    key for key in ("algorithm_path", "score_definition")
                    if record.get(key) in (None, "", [], {})
                ]
                if not auc_ok or missing:
                    bad.append({"algorithm": alg, "auc": auc, "auc_ok": auc_ok, "missing": missing})
            missing_configured = sorted(
                expected_algorithm_keys - set(anchor)
                if expected_algorithm_keys is not None
                else set()
            )
            failure_reasons = []
            if len(anchor) < 3:
                failure_reasons.append(
                    f"trained {len(anchor)} algorithms; Phase 7 requires at least 3"
                )
            if missing_configured:
                failure_reasons.append(
                    "missing user-configured algorithms: " + ", ".join(missing_configured)
                )
            if not effective_algorithms:
                failure_reasons.append(
                    "no trained algorithm has AUC > 0.5; diagnose the data and training, then try additional algorithms"
                )
            if not selection_seed_ok:
                failure_reasons.append(
                    "algorithm_selection_seed is missing or is not an integer"
                )
            if bad:
                failure_reasons.append(
                    "one or more algorithm records has an invalid AUC outside [0, 1] or missing output metadata"
                )
            checks.append({
                "rel_path": comparison_rel,
                "severity": "abort",
                "source": "phase7_algorithm_comparison_content",
                "path": comparison_path,
                "ok": (
                    len(anchor) >= 3
                    and not bad
                    and bool(effective_algorithms)
                    and selection_seed_ok
                    and (
                        expected_algorithm_keys.issubset(set(anchor))
                        if expected_algorithm_keys is not None
                        else True
                    )
                ),
                "algorithm_count": len(anchor),
                "configured_algorithm_keys": sorted(expected_algorithm_keys) if expected_algorithm_keys is not None else None,
                "minimum_algorithm_count": 3,
                "algorithm_selection_seed": selection_seed,
                "algorithm_selection_seed_ok": selection_seed_ok,
                "effective_algorithms_with_auc_above_0_5": effective_algorithms,
                "bad_records": bad,
                "failure_reasons": failure_reasons,
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
    datasets = [("sm", os.path.join("data", "phase7", "sm.csv"))]
    datasets.extend(
        (f"np_{op}", os.path.join("data", "phase7", f"np_{op}.csv"))
        for op in operators
    )
    for alg in algorithms:
        for dataset, source_rel in datasets:
            rel = os.path.join("data", "phase7", "scores", f"{alg}_{dataset}_scores.csv")
            path = os.path.join(root, rel)
            schema = _csv_has_columns(path, required_score_columns)
            identity_errors = []
            if schema.get("ok"):
                try:
                    source_path = os.path.join(root, source_rel)
                    source_rows = _csv_data_row_count(source_path)
                    score_rows, _, identity_errors = _shared_score_counts(
                        root, path, [], source_path
                    )
                    if score_rows != source_rows:
                        identity_errors.append("score/source CSV row counts differ")
                except (OSError, csv.Error) as exc:
                    identity_errors.append(f"could not verify score identities: {exc}")
            schema["ok"] = bool(schema.get("ok")) and not identity_errors
            schema["identity_errors"] = identity_errors
            checks.append({
                "rel_path": rel,
                "severity": "abort",
                "source": "phase7_score_csv_schema_and_identity",
                **schema,
            })

    return checks


def _phase10_manuscript_checks(root: str, required_ids_json: Optional[str] = None) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    required_items, checklist_reference_path, required_items_error = _phase10_required_items(
        required_ids_json
    )
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
    contract_path = os.path.join(_global_results_root(root), "deliverables_contract.json")
    frozen_items = None
    contract_error = None
    try:
        contract = _load_json(contract_path)
        frozen_items = (contract.get("template") or {}).get("phase10_required_manuscript_items")
    except Exception as exc:
        contract_error = f"Could not read frozen Phase 10 manuscript items: {exc}"
    checks.append({
        "rel_path": "deliverables_contract.json:phase10_required_manuscript_items",
        "severity": "abort",
        "source": "phase10_frozen_required_content",
        "path": contract_path,
        "ok": required_items_error is None and contract_error is None and frozen_items == required_items,
        "error": required_items_error or contract_error,
        "frozen_item_count": len(frozen_items) if isinstance(frozen_items, list) else 0,
        "canonical_item_count": len(required_items),
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
            required_content_complete = (
                not major_issues
                and not missing_checklist_ids
                and not missing_trace_ids
                and not checklist_has_missing_required
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
                    and required_content_complete
                    and remaining_consistent
                ),
                "status": status,
                "bad_fields": validation_bad_fields,
                "checklist_path_exists": checklist_path_exists,
                "major_issue_count": len(major_issues) if isinstance(major_issues, list) else "non_list",
                "required_content_complete": required_content_complete,
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
            config = _load_json(os.path.join(_global_results_root(root), "run_config.json"))
            notes = config.get("analysis_notes") or {
                "focused_operators": [],
                "manuscript_preferences": [],
                "additional_requirements": [],
            }
            trace = evidence.get("analysis_notes_trace")
            trace_errors = []
            if not isinstance(trace, dict):
                trace_errors.append("analysis_notes_trace must be an object")
                trace = {}
            focused = trace.get("focused_operators")
            requested_focused = list(notes.get("focused_operators") or [])
            if not isinstance(focused, dict) or focused.get("requested") != requested_focused:
                trace_errors.append("focused_operators.requested must equal run_config analysis_notes")
            elif not set(requested_focused).issubset(set(focused.get("covered") or [])):
                trace_errors.append("every focused operator must appear in focused_operators.covered")
            preference_records = trace.get("manuscript_preferences")
            if not isinstance(preference_records, list):
                preference_records = []
            recorded_preferences = {item.get("request") for item in preference_records if isinstance(item, dict)}
            if recorded_preferences != set(notes.get("manuscript_preferences") or []):
                trace_errors.append("manuscript preference trace does not match run_config")
            requirement_records = trace.get("additional_requirements")
            if not isinstance(requirement_records, list):
                requirement_records = []
            expected_ids = {item.get("id") for item in notes.get("additional_requirements") or []}
            recorded_ids = {item.get("id") for item in requirement_records if isinstance(item, dict)}
            if recorded_ids != expected_ids:
                trace_errors.append("additional requirement trace IDs do not match run_config")
            for item in preference_records + requirement_records:
                if not isinstance(item, dict) or item.get("status") not in {"applied", "not_applicable"} or not item.get("evidence"):
                    trace_errors.append("every trace item needs status applied/not_applicable and non-empty evidence")
            checks.append({
                "rel_path": evidence_rel + ":analysis_notes_trace",
                "severity": "abort",
                "source": "phase10_analysis_notes_trace",
                "path": evidence_path,
                "ok": not trace_errors,
                "errors": trace_errors,
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
    include_final_artifacts: bool = False,
) -> Dict[str, Any]:
    root = _result_root(os.path.abspath(os.path.expanduser(workdir)), run_dir)
    expected = _expected_files(root)
    checks = []
    for item in expected:
        path = os.path.join(root, item["rel_path"])
        rec = dict(item)
        rec.update(_exists_nonempty(path))
        checks.append(rec)
    checks.extend(_cross_file_acceptance_definition_checks(root))
    checks.extend(_recovery_metadata_checks(root))
    checks.extend(_phase3_runner_manifest_checks(root))
    for numerical_phase in ("3", "4", "5", "6", "8"):
        checks.extend(_runner_result_boundary_checks(root, numerical_phase))
    checks.extend(_phase3_completeness_checks(root))
    checks.extend(_phase6_scan_matrix_checks(root))
    checks.extend(_phase6_progress_checks(root))
    checks.extend(_phase6_weighted_order_checks(root))
    checks.extend(_phase7_content_checks(root))
    checks.extend(_phase8_shared_f5_checks(root))
    checks.extend(_phase8_numerical_checks(root))
    checks.extend(_phase9_strategy_checks(root))
    checks.extend(_phase9_numerical_checks(root))
    checks.extend(_replay_algorithm_lock_checks(root))
    checks.extend(_replay_package_checks(root))
    checks.extend(_workflow_contract_binding_checks(root))
    checks.extend(_cleanup_log_checks(root))
    checks.extend(_phase10_manuscript_checks(root, required_ids_json=phase10_required_ids_json))

    checks.extend(_manuscript_format_checks(root))
    checks.extend(_resolved_deliverable_checks(
        root, include_final_artifacts=include_final_artifacts
    ))
    if include_final_artifacts:
        checks.extend(_final_audit_artifact_checks(root))

    _ensure_failure_diagnostics(checks)
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


def audit_phase_deliverables(
    workdir: str,
    phase: str,
    run_dir: Optional[str] = None,
    phase10_required_ids_json: Optional[str] = None,
) -> Dict[str, Any]:
    workdir = os.path.abspath(os.path.expanduser(workdir))
    root = _result_root(workdir, run_dir)
    results_root = os.path.join(workdir, "results")
    contract = resolve_contract(
        os.path.join(results_root, "run_config.json"),
        run_root=root,
        results_dir=results_root,
        phases=[str(phase)],
        write_output=False,
    )
    checks = _resolved_deliverable_checks(
        root,
        include_final_artifacts=True,
        contract_override=contract,
    )
    checks.extend(_cross_file_acceptance_definition_checks(root, phase=str(phase)))
    phase = str(phase)
    if phase in {"5", "6"}:
        checks.extend(_recovery_metadata_checks(root))
    if phase in {"3", "4", "5", "6", "8"}:
        checks.extend(_runner_result_boundary_checks(root, phase))
    if phase == "3":
        checks.extend(_phase3_runner_manifest_checks(root))
        checks.extend(_phase3_completeness_checks(root))
    elif phase == "6":
        checks.extend(_phase6_scan_matrix_checks(root))
        checks.extend(_phase6_progress_checks(root))
        checks.extend(_phase6_weighted_order_checks(root))
    elif phase == "7":
        checks.extend(_phase7_content_checks(root))
    elif phase == "8":
        checks.extend(_phase8_shared_f5_checks(root))
        checks.extend(_phase8_numerical_checks(root))
    elif phase == "9":
        checks.extend(_phase9_strategy_checks(root))
        checks.extend(_phase9_numerical_checks(root))
    elif phase == "10":
        checks.extend(_phase10_manuscript_checks(root, required_ids_json=phase10_required_ids_json))
        checks.extend(_manuscript_format_checks(root))
    elif phase == "cleanup":
        checks.extend(_cleanup_log_checks(root))
    elif phase == "11":
        checks.extend(_replay_algorithm_lock_checks(root))
        checks.extend(_replay_package_checks(root))
    elif phase == "12":
        checks.extend(_final_audit_artifact_checks(root))
    if phase == "2":
        checks.extend(_workflow_contract_binding_checks(root))

    _ensure_failure_diagnostics(checks)
    failures = [check for check in checks if not check["ok"] and check["severity"] == "abort"]
    warnings = [check for check in checks if not check["ok"] and check["severity"] == "warn"]
    return {
        "schema_version": "1.0",
        "root": root,
        "phase": phase,
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
    parser.add_argument(
        "--phase",
        default=None,
        help="Check only deliverables whose frozen rule phase exactly matches this value",
    )
    parser.add_argument("--json-out", default=None)
    parser.add_argument(
        "--include-final-artifacts",
        action="store_true",
        help="Check Phase 12 audit artifacts after both final audit files have been written",
    )
    parser.add_argument(
        "--phase10-required-ids-json",
        default=None,
        help="Optional path to reference/manuscript-checklist-required-ids.json",
    )
    args = parser.parse_args()

    if args.phase is not None:
        report = audit_phase_deliverables(
            args.workdir,
            args.phase,
            run_dir=args.run_dir,
            phase10_required_ids_json=args.phase10_required_ids_json,
        )
    else:
        report = audit_expected_outputs(
            args.workdir,
            run_dir=args.run_dir,
            phase10_required_ids_json=args.phase10_required_ids_json,
            include_final_artifacts=args.include_final_artifacts,
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

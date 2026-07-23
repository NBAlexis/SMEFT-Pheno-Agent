#!/usr/bin/env python3
"""Orchestrate event-count recovery using MG5 runner, count helper, and merge helper."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Any, Dict, List, Optional

try:
    from .merge_lhco import merge_lhco
    from .run_mg5_config import run_from_config
except ImportError:  # Direct script execution.
    from merge_lhco import merge_lhco
    from run_mg5_config import run_from_config


DEFAULT_PROFILES = ["default", "sde0_hs0", "sde0_hs1", "sde0_hs2"]


def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _write_json(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def _write_cross_section_summary(
    path: str,
    label: str,
    cross_section_pb: float,
    source_banners: List[str],
) -> None:
    """Write the canonical Phase 5/6 cross-section text for a recovered sample."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("# Recovery-merged cross-section summary; not an original MG5 banner.\n")
        handle.write(f"# Dataset label: {label}\n")
        handle.write(f"Integrated weight (pb) : {cross_section_pb:.17g}\n")
        handle.write("# Source MG5 banners:\n")
        for source in source_banners:
            handle.write(f"# - {os.path.abspath(source)}\n")


def _read_optional_json(path: str) -> Dict[str, Any]:
    try:
        if path and os.path.exists(path):
            return _read_json(path)
    except Exception:
        pass
    return {}


def _attempt_config(base: Dict[str, Any], profile: str, attempt_index: int, attempt_dir: str) -> Dict[str, Any]:
    cfg = copy.deepcopy(base)
    cfg["survey_profile"] = profile
    cfg["create_process"] = True
    original_folder = cfg.get("process_folder")
    if original_folder:
        cfg["process_folder"] = f"{original_folder}_attempt{attempt_index}_{profile}"
    cfg["output_dir"] = os.path.join(attempt_dir, f"attempt_{attempt_index}_{profile}")
    cfg["result_json"] = os.path.join(cfg["output_dir"], "mg5_result.json")
    return cfg


def _usable_outputs(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    usable = []
    for out in result.get("outputs", []):
        count = int(out.get("loaded_lhco_event_count", 0))
        if count > 0 and os.path.exists(out["lhco_path"]):
            usable.append(out)
    return usable


def _zero_event_outputs(result: Dict[str, Any]) -> List[Dict[str, Any]]:
    zeros = []
    for out in result.get("outputs", []):
        zero_check = out.get("zero_cross_section_check") or {}
        if zero_check.get("confirmed"):
            continue
        count_record = out.get("count_record") or {}
        if count_record.get("status") == "zero_events" or int(out.get("loaded_lhco_event_count", 0)) == 0:
            zeros.append({
                "label": out.get("label"),
                "lhco_path": out.get("lhco_path"),
                "banner_path": out.get("banner_path"),
                "count_record": count_record,
            })
    return zeros


def _expected_labels(base: Dict[str, Any]) -> List[str]:
    if base.get("output_labels"):
        return list(base["output_labels"])
    if base.get("process_mode") == "scan":
        prefix = base.get("output_prefix")
        if not prefix:
            operator = base.get("operator")
            prefix = f"np_{operator}" if operator else "scan"
        return [f"{prefix}_f{i}" for i in range(11)]
    if base.get("output_label"):
        return [base["output_label"]]
    if base.get("process_mode") == "pure_sm":
        return ["sm"]
    if base.get("process_mode") == "pure_np" and base.get("operator"):
        return [f"np_{base['operator']}"]
    return ["sample"]


def _group_counts(attempts: List[Dict[str, Any]]) -> Dict[str, int]:
    totals: Dict[str, int] = {}
    for attempt in attempts:
        for out in _usable_outputs(attempt["result"]):
            label = str(out["label"])
            totals[label] = totals.get(label, 0) + int(out["loaded_lhco_event_count"])
    return totals


def _initial_attempt(
    config: Dict[str, Any], base: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """Load the successful low-count run that triggered recovery, when provided."""
    initial_path = config.get("initial_result_json")
    if not initial_path:
        return None
    initial_path = os.path.abspath(os.path.expanduser(str(initial_path)))
    result = _read_json(initial_path)
    if result.get("result_kind") == "event_count_recovery_summary":
        raise ValueError(
            "initial_result_json points to an event-count recovery summary; "
            "provide the original successful low-count MG5 result JSON"
        )
    if not isinstance(result.get("outputs"), list) or not result["outputs"]:
        raise ValueError(
            "initial_result_json does not contain the original MG5 outputs: " + initial_path
        )
    initial_config = copy.deepcopy(base)
    initial_config["result_json"] = initial_path
    return {
        "attempt_index": 0,
        "survey_profile": result.get("survey_profile", base.get("survey_profile", "default")),
        "status": "completed",
        "config": initial_config,
        "result_json": initial_path,
        "result": result,
    }


def _all_labels_reached(totals: Dict[str, int], labels: List[str], requested: int) -> bool:
    threshold = 0.1 * requested
    return bool(labels) and all(totals.get(label, 0) >= threshold for label in labels)


def _write_recovery_record(
    metadata_path: str,
    metadata: Dict[str, Any],
    recovery_unit: Any = None,
    required_units: Any = None,
) -> Dict[str, Any]:
    """Write one recovery result or update the phase-wide unit index."""
    if recovery_unit is None:
        _write_json(metadata_path, metadata)
        return metadata

    unit = str(recovery_unit)
    required = [str(value) for value in (required_units or [])]
    if unit not in required:
        required.append(unit)
    existing = _read_optional_json(metadata_path)
    units = existing.get("units") if isinstance(existing.get("units"), dict) else {}
    units[unit] = metadata
    missing_units = sorted(set(required) - set(units))
    incomplete_units = sorted(
        key for key in required
        if key in units and units[key].get("status") != "accepted"
    )
    aggregate = {
        "schema_version": "2.0",
        "required_units": required,
        "units": units,
        "missing_units": missing_units,
        "incomplete_units": incomplete_units,
        "status": "accepted" if not missing_units and not incomplete_units else "recovery_incomplete",
    }
    _write_json(metadata_path, aggregate)
    return aggregate


def recover_lhco_count(config: Dict[str, Any]) -> Dict[str, Any]:
    """Run attempts until merged loaded counts reach the 10% floor or profiles end."""
    base = config["base_mg5_config"]
    requested = int(config["requested_event_count"])
    profiles = list(config.get("recovery_profiles", DEFAULT_PROFILES))
    attempt_root = os.path.abspath(os.path.expanduser(config["attempt_root"]))
    merged_output_dir = os.path.abspath(os.path.expanduser(config["merged_output_dir"]))
    metadata_path = os.path.abspath(os.path.expanduser(config["metadata_path"]))
    recovery_unit = config.get("recovery_unit")
    required_units = config.get("required_units")
    os.makedirs(attempt_root, exist_ok=True)
    os.makedirs(merged_output_dir, exist_ok=True)

    labels = _expected_labels(base)
    initial_attempt = _initial_attempt(config, base)
    attempts: List[Dict[str, Any]] = [initial_attempt] if initial_attempt else []
    totals: Dict[str, int] = {}
    zero_event_failure = None

    if initial_attempt:
        zeros = _zero_event_outputs(initial_attempt["result"])
        if zeros:
            initial_attempt["status"] = "zero_event_failure"
            initial_attempt["zero_event_outputs"] = zeros
            zero_event_failure = {
                "attempt_index": 0,
                "survey_profile": initial_attempt["survey_profile"],
                "zero_event_outputs": zeros,
                "action": "inspect/fix Delphes, root2lhco, card, or output generation before rerunning",
            }
        totals = _group_counts(attempts)

    profiles_to_run = list(profiles)
    if initial_attempt and initial_attempt["survey_profile"] in profiles_to_run:
        profiles_to_run.remove(initial_attempt["survey_profile"])

    for attempt_index, profile in enumerate(profiles_to_run, start=len(attempts)):
        if zero_event_failure is not None or _all_labels_reached(totals, labels, requested):
            break
        cfg = _attempt_config(base, profile, attempt_index, attempt_root)
        try:
            result = run_from_config(cfg)
            attempt_record = {
                "attempt_index": attempt_index,
                "survey_profile": profile,
                "status": "completed",
                "config": cfg,
                "result": result,
            }
            zeros = _zero_event_outputs(result)
            if zeros:
                attempt_record["status"] = "zero_event_failure"
                attempt_record["zero_event_outputs"] = zeros
                zero_event_failure = {
                    "attempt_index": attempt_index,
                    "survey_profile": profile,
                    "zero_event_outputs": zeros,
                    "action": "inspect/fix Delphes, root2lhco, card, or output generation before rerunning",
                }
            attempts.append(attempt_record)
        except Exception as exc:
            failed_result = _read_optional_json(cfg.get("result_json", ""))
            attempts.append({
                "attempt_index": attempt_index,
                "survey_profile": profile,
                "status": "failed",
                "config": cfg,
                "error": f"{type(exc).__name__}: {exc}",
                "result": failed_result or {"outputs": []},
            })
        if zero_event_failure is not None:
            break
        totals = _group_counts(attempts)
        if _all_labels_reached(totals, labels, requested):
            break

    merged_outputs = []
    if zero_event_failure is not None:
        metadata = {
            "schema_version": "1.0",
            "requested_event_count": requested,
            "requested_event_count_definition": "original target dataset size, not sum of attempts",
            "recovery_profiles": profiles,
            "attempts": attempts,
            "merged_outputs": [],
            "final_loaded_counts": {},
            "threshold_fraction": 0.1,
            "threshold_reached": False,
            "warnings": [],
            "zero_event_failure": zero_event_failure,
            "status": "zero_event_failure",
        }
        _write_recovery_record(metadata_path, metadata, recovery_unit, required_units)
        return metadata

    for label in labels:
        sources = []
        banners = []
        for attempt in attempts:
            for out in _usable_outputs(attempt["result"]):
                if str(out["label"]) == str(label):
                    sources.append(out["lhco_path"])
                    banners.append(out["banner_path"])
        if not sources:
            merged_outputs.append({
                "label": label,
                "status": "missing_or_empty",
                "loaded_lhco_event_count": 0,
            })
            continue

        output_lhco = os.path.join(merged_output_dir, f"{label}.lhco")
        output_meta = os.path.join(merged_output_dir, f"{label}_merge.json")
        merge_meta = merge_lhco(
            sources,
            output_lhco,
            cutexperiment_path=base.get("cutexperiment_path"),
            source_banner_paths=banners,
            requested_event_count=requested,
            metadata_path=output_meta,
        )
        output_banner = os.path.join(merged_output_dir, f"{label}_banner.txt")
        _write_cross_section_summary(
            output_banner,
            label,
            merge_meta["merged_cross_section_pb"],
            merge_meta["source_banners_retained"],
        )
        merged_outputs.append({
            "label": label,
            "status": "merged",
            "lhco_path": output_lhco,
            "banner_path": output_banner,
            "merge_metadata_path": output_meta,
            "loaded_lhco_event_count": merge_meta["merged_loaded_lhco_event_count"],
            "requested_event_count": requested,
            "fraction": merge_meta["merged_loaded_lhco_event_count"] / float(requested),
            "merged_cross_section_pb": merge_meta["merged_cross_section_pb"],
            "source_banners_retained": merge_meta["source_banners_retained"],
            "source_lhco_paths": [
                record["lhco_path"] for record in merge_meta.get("source_records", [])
            ] or list(sources),
        })

    final_totals = {
        item["label"]: int(item.get("loaded_lhco_event_count", 0))
        for item in merged_outputs
    }
    threshold_reached = _all_labels_reached(final_totals, labels, requested)
    warnings = []
    for item in merged_outputs:
        fraction = item.get("fraction")
        if fraction is not None and 0.1 <= float(fraction) < 0.9:
            warnings.append({
                "label": item["label"],
                "warning": "loaded LHCO count is below 90% of requested count but above the 10% recovery floor",
                "fraction": fraction,
            })
    metadata = {
        "schema_version": "1.0",
        "requested_event_count": requested,
        "requested_event_count_definition": "original target dataset size, not sum of attempts",
        "recovery_profiles": profiles,
        "attempts": attempts,
        "merged_outputs": merged_outputs,
        "final_loaded_counts": final_totals,
        "threshold_fraction": 0.1,
        "threshold_reached": threshold_reached,
        "warnings": warnings,
        "status": "accepted" if threshold_reached else "recovery_incomplete",
    }

    canonical_result_path = base.get("result_json")
    if canonical_result_path:
        canonical_outputs = []
        for item in merged_outputs:
            canonical_outputs.append({
                "label": item["label"],
                "lhco_path": item.get("lhco_path"),
                "banner_path": item.get("banner_path"),
                "cross_section_pb": item.get("merged_cross_section_pb"),
                "loaded_lhco_event_count": item.get("loaded_lhco_event_count"),
                "recovery_merge_metadata_path": item.get("merge_metadata_path"),
                "source_banner_paths": item.get("source_banners_retained", []),
                "source_lhco_paths": item.get("source_lhco_paths", []),
            })
        canonical_result = copy.deepcopy(base)
        canonical_result.update({
            "status": "completed" if threshold_reached else "recovery_incomplete",
            "result_kind": "event_count_recovery_summary",
            "event_generator": "MadGraph5",
            "detector_simulation": "Delphes",
            "analysis_event_format": "LHCO_from_Delphes_ROOT",
            "outputs": canonical_outputs,
            "run_folders": [
                folder
                for attempt in attempts
                for folder in (attempt.get("result") or {}).get("run_folders", [])
            ],
            "recovery_attempt_result_jsons": [
                attempt.get("config", {}).get("result_json")
                for attempt in attempts
                if attempt.get("config", {}).get("result_json")
            ],
            "recovery_metadata_path": metadata_path,
        })
        _write_json(os.path.abspath(os.path.expanduser(canonical_result_path)), canonical_result)

    _write_recovery_record(metadata_path, metadata, recovery_unit, required_units)
    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Recover low LHCO counts")
    parser.add_argument("config_json")
    args = parser.parse_args()

    try:
        metadata = recover_lhco_count(_read_json(args.config_json))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0 if metadata["status"] == "accepted" else 3


if __name__ == "__main__":
    sys.exit(main())

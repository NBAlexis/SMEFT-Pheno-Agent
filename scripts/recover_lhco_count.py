#!/usr/bin/env python3
"""Orchestrate event-count recovery using MG5 runner, count helper, and merge helper."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from typing import Any, Dict, List

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


def _group_counts(attempts: List[Dict[str, Any]]) -> Dict[str, int]:
    totals: Dict[str, int] = {}
    for attempt in attempts:
        for out in _usable_outputs(attempt["result"]):
            label = str(out["label"])
            totals[label] = totals.get(label, 0) + int(out["loaded_lhco_event_count"])
    return totals


def _all_labels_reached(totals: Dict[str, int], labels: List[str], requested: int) -> bool:
    threshold = 0.1 * requested
    return bool(labels) and all(totals.get(label, 0) >= threshold for label in labels)


def recover_lhco_count(config: Dict[str, Any]) -> Dict[str, Any]:
    """Run attempts until merged loaded counts reach the 10% floor or profiles end."""
    base = config["base_mg5_config"]
    requested = int(config["requested_event_count"])
    profiles = list(config.get("recovery_profiles", DEFAULT_PROFILES))
    attempt_root = os.path.abspath(os.path.expanduser(config["attempt_root"]))
    merged_output_dir = os.path.abspath(os.path.expanduser(config["merged_output_dir"]))
    metadata_path = os.path.abspath(os.path.expanduser(config["metadata_path"]))
    os.makedirs(attempt_root, exist_ok=True)
    os.makedirs(merged_output_dir, exist_ok=True)

    labels = list(base.get("output_labels") or [base.get("output_label", "sample")])
    attempts: List[Dict[str, Any]] = []
    totals: Dict[str, int] = {}

    for attempt_index, profile in enumerate(profiles):
        cfg = _attempt_config(base, profile, attempt_index, attempt_root)
        try:
            result = run_from_config(cfg)
            attempts.append({
                "attempt_index": attempt_index,
                "survey_profile": profile,
                "status": "completed",
                "config": cfg,
                "result": result,
            })
        except Exception as exc:
            attempts.append({
                "attempt_index": attempt_index,
                "survey_profile": profile,
                "status": "failed",
                "config": cfg,
                "error": f"{type(exc).__name__}: {exc}",
                "result": {"outputs": []},
            })
        totals = _group_counts(attempts)
        if _all_labels_reached(totals, labels, requested):
            break

    merged_outputs = []
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
        merged_outputs.append({
            "label": label,
            "status": "merged",
            "lhco_path": output_lhco,
            "merge_metadata_path": output_meta,
            "loaded_lhco_event_count": merge_meta["merged_loaded_lhco_event_count"],
            "merged_cross_section_pb": merge_meta["merged_cross_section_pb"],
            "source_banners_retained": merge_meta["source_banners_retained"],
        })

    final_totals = {
        item["label"]: int(item.get("loaded_lhco_event_count", 0))
        for item in merged_outputs
    }
    threshold_reached = _all_labels_reached(final_totals, labels, requested)
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
        "status": "accepted" if threshold_reached else "exhausted_recovery_red_flag",
    }
    _write_json(metadata_path, metadata)
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


#!/usr/bin/env python3
"""Run one MG5 job from a JSON configuration and write a result manifest.

This runner is intentionally config-driven so agents do not hand-write fragile
MG5 launch orders. It executes in the same environment that owns the MG5 working
directory; for SSH/WSL2 workflows, upload this script and its companion scripts
to the target and run it there.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import time
from typing import Any, Dict, Iterable, List, Optional, Tuple

from convert_root_to_lhco import convert_root_to_lhco
from count_lhco_events import count_lhco_events
from extract_cross_section import extract_cross_section
from normalize_process_name import normalize_process_name
from parse_param_card import parse_coefficients
from run_mg5 import run_mg5
from setup_delphes_card import setup_delphes_card


SURVEY_PROFILES = {
    "default": [],
    "sde0_hs0": ["set sde_strategy = 0", "set hard_survey = 0"],
    "sde0_hs1": ["set sde_strategy = 0", "set hard_survey = 1"],
    "sde0_hs2": ["set sde_strategy = 0", "set hard_survey = 2"],
}

PROCESS_MODES = {
    "pure_sm": "NP=0",
    "pure_np": "NP>0",
    "sm_np": "",
    "scan": "",
}

LARGE_INTERMEDIATE_NAMES = {
    "unweighted_events.lhe.gz",
    "tag_1_pythia8_events.hepmc.gz",
    "tag_1_delphes_events.root",
}


def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _write_json(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def _timestamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def _unique_name(root: str, stem: str, suffix: str = "") -> str:
    for idx in range(1, 10000):
        name = f"{stem}_{idx:02d}{suffix}"
        if not os.path.exists(os.path.join(root, name)):
            return name
    raise RuntimeError(f"Could not create unique name under {root}: {stem}")


def _run_dirs(events_dir: str) -> set:
    if not os.path.isdir(events_dir):
        return set()
    return {d for d in os.listdir(events_dir) if d.startswith("run_")}


def _run_sort_key(name: str) -> int:
    try:
        return int(name.split("_", 1)[1])
    except Exception:
        return 10**9


def _copy_optional_outputs(src: str, output_dir: Optional[str], filename: str) -> str:
    if not output_dir:
        return src
    os.makedirs(output_dir, exist_ok=True)
    dest = os.path.join(output_dir, filename)
    shutil.copy2(src, dest)
    return os.path.abspath(dest)


def _generate_line(process: str, process_mode: str) -> str:
    suffix = PROCESS_MODES[process_mode]
    return f"generate {process} {suffix}".rstrip()


def _default_process_folder(mg5path: str, process: str, model: str, process_mode: str) -> str:
    folder_base = normalize_process_name(process)
    mode_suffix = {
        "pure_sm": "SM",
        "pure_np": "NP",
        "sm_np": "SMNP",
        "scan": "SCAN",
    }[process_mode]
    stem = f"{folder_base}_{model}_{mode_suffix}_{_timestamp()}"
    return _unique_name(mg5path, stem)


def _write_order(mg5path: str, name: str, lines: Iterable[str]) -> str:
    path = os.path.join(mg5path, name)
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line).rstrip() + "\n")
    return path


def _create_process(cfg: Dict[str, Any], process_folder: str) -> Dict[str, Any]:
    mg5path = cfg["mg5path"]
    process_mode = cfg["process_mode"]
    order_name = cfg.get(
        "create_order_filename",
        _unique_name(mg5path, f"order_create_{process_folder}", ".txt"),
    )
    lines = [
        f"import model {cfg['model']}",
        _generate_line(cfg["process"], process_mode),
        f"output {process_folder}",
    ]
    order_path = _write_order(mg5path, order_name, lines)
    result = run_mg5(mg5path, order_name)
    return {
        "order_file_path": order_path,
        "order_filename": order_name,
        "stdout_tail": result["stdout"][-4000:],
        "stderr_tail": result["stderr"][-4000:],
        "returncode": result["returncode"],
        "mg5_steps": result.get("mg5_steps"),
    }


def _coefficient_lines(cfg: Dict[str, Any], parsed: Dict[str, Any]) -> List[str]:
    block = cfg.get("coefficient_block") or parsed["block_name"]
    coefficients = {str(k): v for k, v in parsed["coefficients"].items()}
    target = cfg.get("target_coefficient") or {}
    target_index = str(target.get("index", "")) if target else ""

    if cfg["process_mode"] == "pure_sm":
        return [f"set {block} {idx} 0.0" for idx in sorted(coefficients, key=int)]

    lines = []
    for idx in sorted(coefficients, key=int):
        value = "0.0"
        if idx == target_index:
            if cfg["process_mode"] == "scan":
                scan_expression = cfg["scan_expression"]
                value = f"scan:{scan_expression}"
            else:
                value = str(target.get("value", coefficients[idx] or 1.0))
        lines.append(f"set {block} {idx} {value}")
    return lines


def _beam_lines(cfg: Dict[str, Any]) -> List[str]:
    if "ebeam1" in cfg and "ebeam2" in cfg:
        ebeam1 = cfg["ebeam1"]
        ebeam2 = cfg["ebeam2"]
    else:
        tev_to_gev = 1000.0
        energy_tev = float(cfg["energy_tev"])
        ebeam1 = energy_tev * tev_to_gev / 2.0
        ebeam2 = cfg.get("ebeam_proton", ebeam1)
    lines = [f"set ebeam1 = {ebeam1}", f"set ebeam2 = {ebeam2}"]
    pol = cfg.get("polarization")
    if isinstance(pol, dict):
        if "polbeam1" in pol:
            lines.append(f"set polbeam1 = {pol['polbeam1']}")
        if "polbeam2" in pol:
            lines.append(f"set polbeam2 = {pol['polbeam2']}")
    return lines


def _launch_process(cfg: Dict[str, Any], process_folder: str, parsed: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    mg5path = cfg["mg5path"]
    survey_profile = cfg.get("survey_profile", "default")
    if survey_profile not in SURVEY_PROFILES:
        raise ValueError(f"Unknown survey_profile {survey_profile!r}")

    events_dir = os.path.join(mg5path, process_folder, "Events")
    before = _run_dirs(events_dir)
    order_name = cfg.get(
        "launch_order_filename",
        _unique_name(mg5path, f"order_launch_{process_folder}_{survey_profile}", ".txt"),
    )
    lines = [
        f"launch {process_folder}",
        "detector = Delphes",
        "analysis = OFF",
        "0",
    ]
    lines.extend(_coefficient_lines(cfg, parsed))
    lines.extend(_beam_lines(cfg))
    lines.append(f"set nevents = {int(cfg['nevents'])}")
    lines.extend(SURVEY_PROFILES[survey_profile])
    lines.append("0")

    order_path = _write_order(mg5path, order_name, lines)
    result = run_mg5(mg5path, order_name)
    after = _run_dirs(events_dir)
    new_runs = sorted(after - before, key=_run_sort_key)
    if not new_runs:
        raise RuntimeError(f"No new run folders created in {events_dir}")

    return {
        "order_file_path": order_path,
        "order_filename": order_name,
        "survey_profile": survey_profile,
        "stdout_tail": result["stdout"][-4000:],
        "stderr_tail": result["stderr"][-4000:],
        "returncode": result["returncode"],
        "mg5_steps": result.get("mg5_steps"),
    }, new_runs


def _banner_path(mg5path: str, process_folder: str, run_folder: str) -> str:
    return os.path.join(
        mg5path,
        process_folder,
        "Events",
        run_folder,
        f"{run_folder}_tag_1_banner.txt",
    )


def _cleanup_candidates(mg5path: str, process_folder: str, run_folders: Iterable[str]) -> List[str]:
    candidates = []
    for run in run_folders:
        run_dir = os.path.join(mg5path, process_folder, "Events", run)
        for name in LARGE_INTERMEDIATE_NAMES:
            path = os.path.join(run_dir, name)
            if os.path.exists(path):
                candidates.append(os.path.abspath(path))
    return candidates


def _labels_for_runs(cfg: Dict[str, Any], run_count: int) -> List[str]:
    labels = cfg.get("output_labels")
    if labels:
        if len(labels) != run_count:
            raise ValueError("output_labels length must match created run count")
        return labels
    if cfg["process_mode"] == "scan":
        return [f"f{i}" for i in range(run_count)]
    return [cfg.get("output_label", "sample")]


def run_from_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Execute one MG5 config and return a result manifest."""
    cfg = dict(config)
    mg5path = os.path.abspath(os.path.expanduser(cfg["mg5path"]))
    cfg["mg5path"] = mg5path
    process_mode = cfg["process_mode"]
    if process_mode not in PROCESS_MODES:
        raise ValueError(f"process_mode must be one of {sorted(PROCESS_MODES)}")

    process_folder = cfg.get("process_folder") or _default_process_folder(
        mg5path, cfg["process"], cfg["model"], process_mode
    )
    process_dir = os.path.join(mg5path, process_folder)
    create_process = bool(cfg.get("create_process", not os.path.isdir(process_dir)))

    result: Dict[str, Any] = {
        "schema_version": "1.0",
        "mg5path": mg5path,
        "process_folder": process_folder,
        "process_dir": process_dir,
        "process_mode": process_mode,
        "model": cfg["model"],
        "process": cfg["process"],
        "operator": cfg.get("operator"),
        "target_coefficient": cfg.get("target_coefficient"),
        "scan_expression": cfg.get("scan_expression"),
        "survey_profile": cfg.get("survey_profile", "default"),
        "nevents": int(cfg["nevents"]),
        "created_process": create_process,
        "outputs": [],
        "cleanup_candidates": [],
    }

    if create_process:
        result["create_process"] = _create_process(cfg, process_folder)
    if not os.path.isdir(process_dir):
        raise RuntimeError(f"Process directory not found after creation: {process_dir}")

    copied_delphes_card = None
    if cfg.get("delphes_card"):
        copied_delphes_card = setup_delphes_card(mg5path, cfg["delphes_card"], process_folder)
    result["copied_delphes_card"] = copied_delphes_card

    param_card = os.path.join(process_dir, "Cards", "param_card.dat")
    parsed = parse_coefficients(param_card, block_name=cfg.get("coefficient_block"))
    result["coefficient_block"] = parsed["block_name"]
    result["available_coefficients"] = parsed["coefficients"]

    launch_result, new_runs = _launch_process(cfg, process_folder, parsed)
    result["launch"] = launch_result
    result["run_folders"] = new_runs

    labels = _labels_for_runs(cfg, len(new_runs))
    output_dir = cfg.get("output_dir")
    for label, run in zip(labels, new_runs):
        lhco_path = convert_root_to_lhco(mg5path, process_folder, run)
        banner_path = _banner_path(mg5path, process_folder, run)
        cross_section_pb = extract_cross_section(banner_path)
        count_record = count_lhco_events(
            lhco_path,
            requested_event_count=int(cfg["nevents"]),
            dataset_id=label,
            count_context="mg5_output",
            cutexperiment_path=cfg.get("cutexperiment_path"),
        )
        final_lhco = _copy_optional_outputs(lhco_path, output_dir, f"{label}.lhco")
        final_banner = _copy_optional_outputs(banner_path, output_dir, f"{label}_banner.txt")
        result["outputs"].append({
            "label": label,
            "run_folder": run,
            "lhco_path": os.path.abspath(final_lhco),
            "banner_path": os.path.abspath(final_banner),
            "source_lhco_path": os.path.abspath(lhco_path),
            "source_banner_path": os.path.abspath(banner_path),
            "cross_section_pb": cross_section_pb,
            "count_record": count_record,
            "loaded_lhco_event_count": count_record["loaded_lhco_event_count"],
        })

    result["cleanup_candidates"] = _cleanup_candidates(mg5path, process_folder, new_runs)

    result_json = cfg.get("result_json")
    if result_json:
        _write_json(result_json, result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one MG5 job from JSON config")
    parser.add_argument("config_json")
    args = parser.parse_args()

    try:
        result = run_from_config(_read_json(args.config_json))
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())


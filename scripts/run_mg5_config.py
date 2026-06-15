#!/usr/bin/env python3
"""Run one MG5 job from a JSON configuration and write a result manifest.

This runner is intentionally config-driven so agents do not hand-write fragile
MG5 launch orders. It executes in the same environment that owns the MG5 working
directory; for SSH/WSL2 workflows, upload this script and its companion scripts
to the target and run it there.

The ``process`` config field may be one MG5 process string or a list of process
strings. For lists, the runner writes one process creation order with
``generate <process_1> <mode_suffix>`` followed by
``add process <process_i> <mode_suffix>`` for every additional process. The
mode suffix, e.g. ``NP=0`` or ``NP>0``, belongs on each process line in the MG5
order and is appended here from ``process_mode``.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import sys
import time
import traceback
from typing import Any, Dict, Iterable, List, Optional, Tuple

from convert_root_to_lhco import convert_root_to_lhco
from count_lhco_events import count_lhco_events
from double_check_zero_cross_section import double_check_zero_cross_section
from extract_cross_section import extract_cross_section
from normalize_process_name import normalize_process_name
from parse_param_card import parse_coefficients
from run_mg5 import MG5RunError, run_mg5
from setup_delphes_card import setup_delphes_card


SURVEY_PROFILES = {
    "default": [],
    "sde0_hs0": ["set sde_strategy = 0", "set hard_survey = 0"],
    "sde0_hs1": ["set sde_strategy = 0", "set hard_survey = 1"],
    "sde0_hs2": ["set sde_strategy = 0", "set hard_survey = 2"],
}

PROCESS_MODES = {
    "create_np": "NP>0",
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

LARGE_INTERMEDIATE_SUFFIXES = (
    ".root",
    ".lhe",
    ".lhe.gz",
    ".hepmc",
    ".hepmc.gz",
)


def _read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _write_json(path: str, data: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def _write_text(path: str, text: str) -> str:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text or "")
    return os.path.abspath(path)


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


def _write_zero_cross_section_report(
    output_dir: Optional[str],
    label: str,
    report: Dict[str, Any],
) -> Dict[str, Any]:
    if output_dir:
        report_path = os.path.abspath(
            os.path.join(output_dir, f"{label}_zero_cross_section_check.json")
        )
        report["report_path"] = report_path
        _write_json(report_path, report)
    return report


def _processes_from_config(cfg: Dict[str, Any]) -> List[str]:
    process = cfg.get("process")
    if isinstance(process, str):
        processes = [process]
    elif isinstance(process, list):
        processes = process
    else:
        raise ValueError("process must be a string or a non-empty list of strings")

    cleaned = []
    for idx, item in enumerate(processes):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"process[{idx}] must be a non-empty string")
        cleaned.append(item.strip())
    if not cleaned:
        raise ValueError("process list must not be empty")
    return cleaned


def _process_label(process: Any) -> str:
    return " add ".join(process) if isinstance(process, list) else str(process)


def _process_order_lines(processes: List[str], process_mode: str) -> List[str]:
    suffix = PROCESS_MODES[process_mode]
    lines = []
    for idx, process in enumerate(processes):
        command = "generate" if idx == 0 else "add process"
        lines.append(f"{command} {process} {suffix}".rstrip())
    return lines


def _default_process_folder(
    mg5path: str,
    process: Any,
    model: str,
    process_mode: str,
    run_label: Optional[str] = None,
) -> str:
    folder_base = normalize_process_name(_process_label(process))
    mode_suffix = {
        "create_np": "NP",
        "pure_sm": "SM",
        "pure_np": "NP",
        "sm_np": "SMNP",
        "scan": "SCAN",
    }[process_mode]
    label_part = f"_{run_label}" if run_label else ""
    stem = f"{folder_base}_{model}_{mode_suffix}{label_part}_{_timestamp()}"
    return _unique_name(mg5path, stem)


def _safe_label(value: Any) -> Optional[str]:
    if value is None:
        return None
    text = normalize_process_name(str(value).strip())
    return text or None


def _write_order(mg5path: str, name: str, lines: Iterable[str]) -> str:
    path = os.path.join(mg5path, name)
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line).rstrip() + "\n")
    return path


def _log_dir(cfg: Dict[str, Any]) -> str:
    return os.path.abspath(
        os.path.expanduser(
            cfg.get("log_dir")
            or os.path.join(cfg.get("output_dir") or cfg["mg5path"], "logs")
        )
    )


def _record_mg5_logs(cfg: Dict[str, Any], stem: str, result: Dict[str, Any]) -> Dict[str, str]:
    log_dir = _log_dir(cfg)
    return {
        "stdout_path": _write_text(os.path.join(log_dir, f"{stem}.stdout.log"), result.get("stdout", "")),
        "stderr_path": _write_text(os.path.join(log_dir, f"{stem}.stderr.log"), result.get("stderr", "")),
    }


def _run_mg5_with_recorded_logs(
    cfg: Dict[str, Any],
    stem: str,
    mg5path: str,
    order_name: str,
) -> Tuple[Dict[str, Any], Dict[str, str]]:
    try:
        result = run_mg5(mg5path, order_name)
    except MG5RunError as exc:
        logs = _record_mg5_logs(cfg, stem, exc.result)
        raise RuntimeError(
            f"MG5 failed for {stem}; stdout/stderr saved at "
            f"{logs['stdout_path']} and {logs['stderr_path']}"
        ) from exc
    logs = _record_mg5_logs(cfg, stem, result)
    return result, logs


def _mark_process_dir_broken(process_dir: Optional[str]) -> Tuple[Optional[str], List[str]]:
    if not process_dir or not os.path.isdir(process_dir):
        return None, []
    removed = _remove_large_intermediates(process_dir)
    parent = os.path.dirname(process_dir)
    base = os.path.basename(process_dir)
    target = os.path.join(parent, f"{base}_broken_{_timestamp()}")
    for idx in range(1, 100):
        candidate = target if idx == 1 else f"{target}_{idx:02d}"
        if not os.path.exists(candidate):
            os.rename(process_dir, candidate)
            return os.path.abspath(candidate), removed
    raise RuntimeError(f"Could not mark failed process directory as broken: {process_dir}")


def _remove_large_intermediates(process_dir: str) -> List[str]:
    """Delete large MG5 intermediates inside a process dir before archiving it."""
    removed = []
    for root, _, files in os.walk(process_dir):
        for filename in files:
            lower = filename.lower()
            if not lower.endswith(LARGE_INTERMEDIATE_SUFFIXES):
                continue
            path = os.path.join(root, filename)
            try:
                os.remove(path)
                removed.append(os.path.abspath(path))
            except OSError:
                pass
    return removed


def _validate_model_exists(mg5path: str, model: str) -> str:
    model_dir = os.path.join(mg5path, "models", model)
    if not os.path.isdir(model_dir):
        raise RuntimeError(
            f"UFO model not found on MG5 target: {model_dir}. "
            "Sync or install the model before running MG5."
        )
    return os.path.abspath(model_dir)


def _sort_coefficient_keys(keys: Iterable[str]) -> List[str]:
    def key_fn(value: str):
        try:
            return (0, int(value))
        except ValueError:
            return (1, value)
    return sorted(keys, key=key_fn)


def _scan_expression_from_c_scan(cfg: Dict[str, Any]) -> str:
    if "c_scan" not in cfg:
        raise ValueError("scan mode requires c_scan")
    c_scan_text = str(cfg["c_scan"])
    return f"[-{c_scan_text} + 0.2 * {c_scan_text} * n for n in range(11)]"


def _positive_finite(value: Any, name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be numeric, got {value!r}")
    if not math.isfinite(parsed) or parsed <= 0:
        raise ValueError(f"{name} must be positive and finite, got {value!r}")
    return parsed


def validate_config(cfg: Dict[str, Any]) -> None:
    """Validate runner config before MG5 is started."""
    required = ["mg5path", "model", "process", "process_mode"]
    missing = [key for key in required if key not in cfg]
    if missing:
        raise ValueError(f"Missing required MG5 runner config fields: {missing}")
    _processes_from_config(cfg)

    process_mode = cfg["process_mode"]
    if process_mode not in PROCESS_MODES:
        raise ValueError(f"process_mode must be one of {sorted(PROCESS_MODES)}")
    if process_mode != "create_np":
        if "nevents" not in cfg:
            raise ValueError("nevents is required unless process_mode='create_np'")
        if int(cfg["nevents"]) <= 0:
            raise ValueError("nevents must be a positive integer")
    survey_profile = cfg.get("survey_profile", "default")
    if survey_profile not in SURVEY_PROFILES:
        raise ValueError(f"Unknown survey_profile {survey_profile!r}")
    if process_mode != "create_np":
        if "ebeam1" not in cfg or "ebeam2" not in cfg:
            raise ValueError(
                "runner config requires explicit ebeam1 and ebeam2 in GeV from run_configurations"
            )
        _positive_finite(cfg["ebeam1"], "ebeam1")
        _positive_finite(cfg["ebeam2"], "ebeam2")

    labels = cfg.get("output_labels")
    if labels is not None and not isinstance(labels, list):
        raise ValueError("output_labels must be a list when provided")

    coefficient_mode = cfg.get("coefficient_mode")
    if coefficient_mode is not None and coefficient_mode not in {"default", "c_scan", "explicit"}:
        raise ValueError("coefficient_mode must be one of default, c_scan, explicit")

    if process_mode == "create_np":
        return
    if process_mode == "scan":
        _positive_finite(cfg.get("c_scan"), "c_scan")
        if not (cfg.get("operator") or cfg.get("output_prefix") or cfg.get("output_labels")):
            raise ValueError("scan mode requires operator, output_prefix, or output_labels")
        if labels is not None and len(labels) != 11:
            raise ValueError("scan mode output_labels must have length exactly 11")
        target = cfg.get("target_coefficient") or {}
        if "index" not in target:
            raise ValueError("scan mode requires target_coefficient.index")
    else:
        if labels is not None and len(labels) != 1:
            raise ValueError("non-scan output_labels must have length exactly 1")
        if coefficient_mode == "c_scan":
            _positive_finite(cfg.get("c_scan"), "c_scan")
        if process_mode != "pure_sm":
            target = cfg.get("target_coefficient") or {}
            if "index" not in target:
                raise ValueError(f"{process_mode} requires target_coefficient.index")
            if coefficient_mode == "explicit" and "value" not in target:
                raise ValueError("coefficient_mode='explicit' requires target_coefficient.value")


def _create_process(cfg: Dict[str, Any], process_folder: str) -> Dict[str, Any]:
    mg5path = cfg["mg5path"]
    process_mode = cfg["process_mode"]
    processes = _processes_from_config(cfg)
    order_name = cfg.get(
        "create_order_filename",
        _unique_name(mg5path, f"order_create_{process_folder}", ".txt"),
    )
    lines = [
        f"import model {cfg['model']}",
        *_process_order_lines(processes, process_mode),
        f"output {process_folder}",
    ]
    order_path = _write_order(mg5path, order_name, lines)
    result, logs = _run_mg5_with_recorded_logs(
        cfg,
        f"create_{process_folder}",
        mg5path,
        order_name,
    )
    return {
        "order_file_path": order_path,
        "order_filename": order_name,
        **logs,
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
        return [f"set {block} {idx} 0.0" for idx in _sort_coefficient_keys(coefficients)]

    lines = []
    for idx in _sort_coefficient_keys(coefficients):
        value = "0.0"
        if idx == target_index:
            if cfg["process_mode"] == "scan":
                scan_expression = _scan_expression_from_c_scan(cfg)
                value = f"scan:{scan_expression}"
            else:
                coefficient_mode = cfg.get("coefficient_mode")
                if coefficient_mode is None:
                    coefficient_mode = "explicit" if "value" in target else "default"
                if coefficient_mode == "default":
                    value = str(coefficients[idx] or 1.0)
                elif coefficient_mode == "c_scan":
                    if "c_scan" not in cfg:
                        raise ValueError("coefficient_mode='c_scan' requires c_scan")
                    value = str(cfg["c_scan"])
                elif coefficient_mode == "explicit":
                    if "value" not in target:
                        raise ValueError("coefficient_mode='explicit' requires target_coefficient.value")
                    value = str(target["value"])
                else:
                    raise ValueError(
                        "coefficient_mode must be one of default, c_scan, explicit"
                    )
        lines.append(f"set {block} {idx} {value}")
    return lines


def _beam_lines(cfg: Dict[str, Any]) -> List[str]:
    ebeam1 = cfg["ebeam1"]
    ebeam2 = cfg["ebeam2"]
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
    ]
    if (cfg.get("madspin") or {}).get("enabled"):
        lines.append("madspin=ON")
    lines.extend([
        "detector = Delphes",
        "analysis = OFF",
        "0",
    ])
    lines.extend(_coefficient_lines(cfg, parsed))
    lines.extend(_beam_lines(cfg))
    lines.append(f"set nevents = {int(cfg['nevents'])}")
    lines.extend(SURVEY_PROFILES[survey_profile])
    lines.append("0")

    order_path = _write_order(mg5path, order_name, lines)
    result, logs = _run_mg5_with_recorded_logs(
        cfg,
        f"launch_{process_folder}_{survey_profile}",
        mg5path,
        order_name,
    )
    after = _run_dirs(events_dir)
    new_runs = sorted(after - before, key=_run_sort_key)
    if not new_runs:
        raise RuntimeError(f"No new run folders created in {events_dir}")
    if cfg["process_mode"] == "scan" and len(new_runs) != 11:
        raise RuntimeError(f"Expected 11 scan runs, got {len(new_runs)} in {events_dir}")

    return {
        "order_file_path": order_path,
        "order_filename": order_name,
        "survey_profile": survey_profile,
        **logs,
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
        prefix = cfg.get("output_prefix")
        if not prefix:
            operator = cfg.get("operator")
            prefix = f"np_{operator}" if operator else "scan"
        return [f"{prefix}_f{i}" for i in range(run_count)]
    if "output_label" in cfg:
        return [cfg["output_label"]]
    if cfg["process_mode"] == "pure_sm":
        return ["sm"]
    if cfg["process_mode"] == "pure_np" and cfg.get("operator"):
        return [f"np_{cfg['operator']}"]
    return ["sample"]


def run_from_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Execute one MG5 config and return a result manifest."""
    cfg = dict(config)
    stage = "config_validation"
    result: Dict[str, Any] = {
        "schema_version": "1.0",
        "status": "started",
        "mg5path": cfg.get("mg5path"),
        "process_folder": cfg.get("process_folder"),
        "process_mode": cfg.get("process_mode"),
        "run_label": cfg.get("run_label") or cfg.get("run_dir"),
        "model": cfg.get("model"),
        "process": cfg.get("process"),
        "process_validation": cfg.get("process_validation"),
        "operator": cfg.get("operator"),
        "target_coefficient": cfg.get("target_coefficient"),
        "coefficient_mode": cfg.get("coefficient_mode"),
        "c_scan": cfg.get("c_scan"),
        "ebeam1": cfg.get("ebeam1"),
        "ebeam2": cfg.get("ebeam2"),
        "madspin": cfg.get("madspin", {"enabled": False}),
        "survey_profile": cfg.get("survey_profile", "default"),
        "outputs": [],
        "cleanup_candidates": [],
    }
    try:
        validate_config(cfg)
        mg5path = os.path.abspath(os.path.expanduser(cfg["mg5path"]))
        cfg["mg5path"] = mg5path
        process_mode = cfg["process_mode"]
        result["mg5path"] = mg5path
        if "nevents" in cfg:
            result["nevents"] = int(cfg["nevents"])
        result["scan_expression"] = _scan_expression_from_c_scan(cfg) if process_mode == "scan" else None

        stage = "model_validation"
        model_dir = _validate_model_exists(mg5path, cfg["model"])
        result["model_dir"] = model_dir

        stage = "process_folder_resolution"
        process_folder = cfg.get("process_folder")
        if not process_folder:
            run_label = _safe_label(cfg.get("run_label") or cfg.get("run_dir"))
            process_folder = _default_process_folder(
                mg5path, cfg["process"], cfg["model"], process_mode, run_label=run_label
            )
        process_dir = os.path.join(mg5path, process_folder)
        create_process = bool(cfg.get("create_process", not os.path.isdir(process_dir)))
        result["process_folder"] = process_folder
        result["process_dir"] = process_dir
        result["created_process"] = create_process

        if create_process:
            stage = "create_process"
            result["create_process"] = _create_process(cfg, process_folder)
        if not os.path.isdir(process_dir):
            raise RuntimeError(f"Process directory not found after creation: {process_dir}")

        stage = "setup_delphes"
        copied_delphes_card = None
        if cfg.get("delphes_card"):
            copied_delphes_card = setup_delphes_card(mg5path, cfg["delphes_card"], process_folder)
        result["copied_delphes_card"] = copied_delphes_card

        stage = "parse_param_card"
        param_card = os.path.join(process_dir, "Cards", "param_card.dat")
        parsed = parse_coefficients(param_card, block_name=cfg.get("coefficient_block"))
        result["coefficient_block"] = parsed["block_name"]
        result["available_coefficients"] = parsed["coefficients"]

        if process_mode == "create_np":
            result["status"] = "completed"
            result_json = cfg.get("result_json")
            if result_json:
                _write_json(result_json, result)
            return result

        stage = "launch"
        launch_result, new_runs = _launch_process(cfg, process_folder, parsed)
        result["launch"] = launch_result
        result["run_folders"] = new_runs

        stage = "postprocess"
        labels = _labels_for_runs(cfg, len(new_runs))
        output_dir = cfg.get("output_dir")
        for label, run in zip(labels, new_runs):
            run_dir = os.path.join(mg5path, process_folder, "Events", run)
            banner_path = _banner_path(mg5path, process_folder, run)
            banner_missing = not os.path.exists(banner_path)
            zero_cross_section_check = None
            if banner_missing:
                if process_mode == "scan":
                    raise RuntimeError(
                        f"Scan run {run} for {label} is missing its banner. "
                        "Phase 6 scan inputs are non-zero operators; treat this as an MG5/run-output failure and retry."
                    )
                zero_cross_section_check = double_check_zero_cross_section(
                    None,
                    [launch_result.get("stdout_path")],
                    [launch_result.get("stderr_path")],
                    run_dir,
                    banner_missing=True,
                )
                zero_cross_section_check = _write_zero_cross_section_report(
                    output_dir, label, zero_cross_section_check
                )
                if not zero_cross_section_check["confirmed"]:
                    report_path = zero_cross_section_check.get("report_path")
                    suffix = f" Report: {report_path}" if report_path else ""
                    raise RuntimeError(
                        "Suspicious missing-banner zero cross-section claim: "
                        "banner is missing, "
                        "but MG5 logs/LHE evidence did not confirm a true zero cross section."
                        + suffix
                    )
                cross_section_pb = 0.0
                count_record = {
                    "dataset_id": label,
                    "status": "zero_cross_section_no_events",
                    "loaded_lhco_event_count": 0,
                    "requested_event_count": int(cfg["nevents"]),
                    "count_context": "mg5_output",
                    "reason": "MG5 confirmed zero cross-section with missing banner and no substantial LHE payload.",
                }
                result["outputs"].append({
                    "label": label,
                    "run_folder": run,
                    "lhco_path": None,
                    "banner_path": None,
                    "source_lhco_path": None,
                    "source_banner_path": os.path.abspath(banner_path),
                    "banner_missing": True,
                    "cross_section_pb": cross_section_pb,
                    "zero_cross_section_check": zero_cross_section_check,
                    "count_record": count_record,
                    "loaded_lhco_event_count": 0,
                })
                continue

            cross_section_pb = extract_cross_section(banner_path)
            if process_mode == "scan" and cross_section_pb == 0.0:
                raise RuntimeError(
                    f"Scan run {run} for {label} produced a zero banner cross-section. "
                    "Phase 6 scan inputs are non-zero operators; treat this as an MG5/run-output failure and retry."
                )
            if cross_section_pb == 0.0:
                zero_cross_section_check = double_check_zero_cross_section(
                    cross_section_pb,
                    [launch_result.get("stdout_path")],
                    [launch_result.get("stderr_path")],
                    run_dir,
                )
                zero_cross_section_check = _write_zero_cross_section_report(
                    output_dir, label, zero_cross_section_check
                )
                if not zero_cross_section_check["confirmed"]:
                    report_path = zero_cross_section_check.get("report_path")
                    suffix = f" Report: {report_path}" if report_path else ""
                    raise RuntimeError(
                        "Suspicious zero cross-section: banner parsed exactly 0 pb, "
                        "but MG5 logs/LHE evidence did not confirm a true zero cross section."
                        + suffix
                    )
                count_record = {
                    "dataset_id": label,
                    "status": "zero_cross_section_no_events",
                    "loaded_lhco_event_count": 0,
                    "requested_event_count": int(cfg["nevents"]),
                    "count_context": "mg5_output",
                    "reason": "MG5 confirmed zero cross-section with no substantial LHE payload.",
                }
                final_banner = _copy_optional_outputs(banner_path, output_dir, f"{label}_banner.txt")
                result["outputs"].append({
                    "label": label,
                    "run_folder": run,
                    "lhco_path": None,
                    "banner_path": os.path.abspath(final_banner),
                    "source_lhco_path": None,
                    "source_banner_path": os.path.abspath(banner_path),
                    "banner_missing": False,
                    "cross_section_pb": cross_section_pb,
                    "zero_cross_section_check": zero_cross_section_check,
                    "count_record": count_record,
                    "loaded_lhco_event_count": 0,
                })
                continue

            lhco_path = convert_root_to_lhco(mg5path, process_folder, run)
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
                "banner_missing": False,
                "cross_section_pb": cross_section_pb,
                "zero_cross_section_check": zero_cross_section_check,
                "count_record": count_record,
                "loaded_lhco_event_count": count_record["loaded_lhco_event_count"],
            })

        result["cleanup_candidates"] = _cleanup_candidates(mg5path, process_folder, new_runs)
        result["status"] = "completed"
        result_json = cfg.get("result_json")
        if result_json:
            _write_json(result_json, result)
        return result
    except Exception as exc:
        result["status"] = "failed"
        result["failure_stage"] = stage
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["traceback"] = traceback.format_exc()
        if result.get("created_process"):
            try:
                broken_dir, removed_files = _mark_process_dir_broken(result.get("process_dir"))
                result["broken_process_dir"] = broken_dir
                result["broken_cleanup_removed_files"] = removed_files
            except Exception as rename_exc:
                result["broken_process_dir"] = None
                result["broken_cleanup_removed_files"] = []
                result["broken_process_dir_error"] = f"{type(rename_exc).__name__}: {rename_exc}"
        try:
            result["failure_log_path"] = _write_text(
                os.path.join(_log_dir(cfg), f"failed_{stage}.log"),
                result["traceback"],
            )
        except Exception:
            result["failure_log_path"] = None
        if cfg.get("result_json"):
            _write_json(cfg["result_json"], result)
        raise


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

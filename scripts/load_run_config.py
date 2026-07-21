#!/usr/bin/env python3
"""
Load and validate the run configuration produced by Phase 1.

Usage:
    from scripts.load_run_config import load_run_config
    config = load_run_config("results/run_config.json")
    print(config.madgraph_path)
    print(config.delphes_card)

CLI:
    python scripts/load_run_config.py results/run_config.json

Returns a typed SimpleNamespace for attribute-style access.
"""
import argparse
import json
import os
import sys
from types import SimpleNamespace

REQUIRED_FIELDS = [
    "madgraph_path",
    "workdir",
    "process",
    "models",
    "energy",
    "luminosity",
    "delphes_card",
    "run_configurations",
]

OPTIONAL_FIELDS = [
    "collider_type",
    "ebeam_electron",
    "ebeam_proton",
    "polarization",
    "debug",
    "algorithms",
    "analysis_notes",
    "execution",
    "cutexperiment_path",
    "auto_installed_mg5",
    "process_validation",
    "madspin",
    "event_counts_locked",
    "locked_event_counts",
]

NORMAL_EVENT_COUNTS = {
    "nev_phase3": 10000,
    "nev_phase4": 10000,
    "nev_sm": 500000,
    "nev_np": 100000,
    "nev_scan": 1000000,
}

DEBUG_EVENT_COUNTS = {
    "nev_phase3": 1000,
    "nev_phase4": 1000,
    "nev_sm": 50000,
    "nev_np": 10000,
    "nev_scan": 100000,
}

VALID_EXECUTION_MODES = {"local", "ssh", "wsl2"}


def _dict_to_namespace(d):
    """Recursively convert dict to SimpleNamespace for attribute access."""
    if isinstance(d, dict):
        return SimpleNamespace(**{k: _dict_to_namespace(v) for k, v in d.items()})
    if isinstance(d, list):
        return [_dict_to_namespace(item) for item in d]
    return d


def load_run_config(path):
    """Load and validate run_config.json.

    Args:
        path: path to run_config.json

    Returns:
        SimpleNamespace with attribute access to all config fields.

    Raises:
        FileNotFoundError: if the file does not exist
        ValueError: if required fields are missing or invalid
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"run_config.json not found: {path}")

    with open(path, encoding="utf-8-sig") as f:
        data = json.load(f)

    # Validate version
    version = data.get("version")
    if version != "1.0":
        raise ValueError(f"Unsupported run_config version: {version!r} (expected '1.0')")

    # Validate required fields
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        raise ValueError(f"run_config.json missing required fields: {missing}")

    # Type checks
    if not isinstance(data["models"], list):
        raise ValueError(f"models must be a list, got {type(data['models'])}")
    if not data["models"] or any(not isinstance(model, str) or not model.strip() for model in data["models"]):
        raise ValueError("models must be a non-empty list of non-empty model names")
    if not isinstance(data["luminosity"], list):
        raise ValueError(f"luminosity must be a list, got {type(data['luminosity'])}")
    if not data["luminosity"] or any(float(value) <= 0 for value in data["luminosity"]):
        raise ValueError("luminosity must be a non-empty list of positive values")
    if not isinstance(data["run_configurations"], list):
        raise ValueError(
            f"run_configurations must be a list, got {type(data['run_configurations'])}"
        )
    if not data["run_configurations"]:
        raise ValueError("run_configurations must not be empty")
    collider_type = data.get("collider_type")
    if collider_type is not None and collider_type not in {"ee", "pp", "mumu", "ep"}:
        raise ValueError("collider_type must be one of ee, pp, mumu, ep when provided")
    if collider_type == "ep":
        if data["energy"] is not None:
            raise ValueError("energy must be null for ep; use explicit ebeam1/ebeam2")
    elif not isinstance(data["energy"], list):
        raise ValueError(f"energy must be a list for non-ep colliders, got {type(data['energy'])}")
    elif not data["energy"] or any(float(value) <= 0 for value in data["energy"]):
        raise ValueError("energy must be a non-empty list of positive values")
    if isinstance(data["process"], str):
        if not data["process"].strip():
            raise ValueError("process must not be empty")
    elif isinstance(data["process"], list):
        if not data["process"]:
            raise ValueError("process list must not be empty")
        for idx, process in enumerate(data["process"]):
            if not isinstance(process, str) or not process.strip():
                raise ValueError(f"process[{idx}] must be a non-empty string")
    else:
        raise ValueError(f"process must be a string or list of strings, got {type(data['process'])}")

    # Cross-check lengths and beam energies. Event generation uses ebeam1/ebeam2.
    if len(data["run_configurations"]) != len(data["luminosity"]):
        raise ValueError(
            f"run_configurations ({len(data['run_configurations'])}) and luminosity "
            f"({len(data['luminosity'])}) lengths must match"
        )
    if collider_type != "ep" and len(data["energy"]) != len(data["luminosity"]):
        raise ValueError(
            f"energy ({len(data['energy'])}) and luminosity ({len(data['luminosity'])}) "
            "lengths must match"
        )
    for idx, run_cfg in enumerate(data["run_configurations"]):
        if not isinstance(run_cfg, dict):
            raise ValueError(f"run_configurations[{idx}] must be an object")
        for key in ("ebeam1", "ebeam2"):
            if key not in run_cfg or float(run_cfg[key]) <= 0:
                raise ValueError(f"run_configurations[{idx}].{key} must be positive")
    if collider_type == "ep":
        for key in ("ebeam_electron", "ebeam_proton"):
            values = data.get(key)
            if not isinstance(values, list) or len(values) != len(data["luminosity"]):
                raise ValueError(f"{key} must be a list matching luminosity length for ep")
            for idx, value in enumerate(values):
                if float(value) <= 0:
                    raise ValueError(f"{key}[{idx}] must be positive")
        for idx, run_cfg in enumerate(data["run_configurations"]):
            if float(run_cfg["ebeam1"]) != float(data["ebeam_electron"][idx]):
                raise ValueError(f"run_configurations[{idx}].ebeam1 must match ebeam_electron[{idx}]")
            if float(run_cfg["ebeam2"]) != float(data["ebeam_proton"][idx]):
                raise ValueError(f"run_configurations[{idx}].ebeam2 must match ebeam_proton[{idx}]")

    polarization = data.get("polarization")
    if polarization is not None:
        if not isinstance(polarization, dict) or set(polarization) != {"polbeam1", "polbeam2"}:
            raise ValueError(
                "polarization must be null or an object with exactly polbeam1 and polbeam2"
            )
        for key in ("polbeam1", "polbeam2"):
            try:
                value = float(polarization[key])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"polarization.{key} must be numeric") from exc
            if not -1.0 <= value <= 1.0:
                raise ValueError(f"polarization.{key} must be in [-1, 1]")
            polarization[key] = value

    analysis_notes = data.get("analysis_notes")
    if analysis_notes is None:
        analysis_notes = {
            "focused_operators": [],
            "manuscript_preferences": [],
            "additional_requirements": [],
        }
        data["analysis_notes"] = analysis_notes
    if not isinstance(analysis_notes, dict) or set(analysis_notes) != {
        "focused_operators",
        "manuscript_preferences",
        "additional_requirements",
    }:
        raise ValueError(
            "analysis_notes must contain exactly focused_operators, "
            "manuscript_preferences, and additional_requirements"
        )
    for key in ("focused_operators", "manuscript_preferences"):
        values = analysis_notes[key]
        if not isinstance(values, list) or any(
            not isinstance(value, str) or not value.strip() for value in values
        ):
            raise ValueError(f"analysis_notes.{key} must be a list of non-empty strings")
    requirements = analysis_notes["additional_requirements"]
    if not isinstance(requirements, list):
        raise ValueError("analysis_notes.additional_requirements must be a list")
    seen_requirement_ids = set()
    for idx, requirement in enumerate(requirements):
        if not isinstance(requirement, dict) or set(requirement) != {"id", "text", "applies_to_phases"}:
            raise ValueError(
                f"analysis_notes.additional_requirements[{idx}] must contain exactly "
                "id, text, and applies_to_phases"
            )
        requirement_id = requirement.get("id")
        if not isinstance(requirement_id, str) or not requirement_id.strip():
            raise ValueError(f"analysis_notes.additional_requirements[{idx}].id must be non-empty")
        if requirement_id in seen_requirement_ids:
            raise ValueError(f"Duplicate analysis requirement id: {requirement_id}")
        seen_requirement_ids.add(requirement_id)
        if not isinstance(requirement.get("text"), str) or not requirement["text"].strip():
            raise ValueError(f"analysis_notes.additional_requirements[{idx}].text must be non-empty")
        phases = requirement.get("applies_to_phases")
        if not isinstance(phases, list) or not phases or any(
            str(phase) not in {str(value) for value in range(2, 13)} | {"cleanup"}
            for phase in phases
        ):
            raise ValueError(
                f"analysis_notes.additional_requirements[{idx}].applies_to_phases "
                "must contain Phase numbers 2-12 or cleanup"
            )

    if "debug" not in data:
        data["debug"] = False
    if "madspin" not in data:
        data["madspin"] = {"enabled": False}
    if not isinstance(data["madspin"], dict):
        raise ValueError("madspin must be an object when provided")
    data["madspin"]["enabled"] = bool(data["madspin"].get("enabled", False))
    if "execution" not in data:
        data["execution"] = {"mode": "local"}
    if not isinstance(data["execution"], dict):
        raise ValueError("execution must be an object")
    mode = data["execution"].get("mode", "local")
    if mode not in VALID_EXECUTION_MODES:
        raise ValueError(
            f"execution.mode must be one of {sorted(VALID_EXECUTION_MODES)}, got {mode!r}"
        )
    if mode == "local" and os.name == "nt":
        raise ValueError(
            "execution.mode='local' is invalid on native Windows; use 'wsl2' or 'ssh'"
        )
    data["execution"]["mode"] = mode
    if mode == "ssh" and not data["execution"].get("ssh_target"):
        raise ValueError("execution.ssh_target is required when execution.mode is 'ssh'")
    if "event_counts_locked" not in data:
        data["event_counts_locked"] = True
    if "locked_event_counts" not in data:
        data["locked_event_counts"] = (
            DEBUG_EVENT_COUNTS.copy() if data.get("debug") else NORMAL_EVENT_COUNTS.copy()
        )

    expected_counts = DEBUG_EVENT_COUNTS if data.get("debug") else NORMAL_EVENT_COUNTS
    if data["locked_event_counts"] != expected_counts:
        raise ValueError(
            "locked_event_counts do not match the selected debug mode. "
            f"Expected {expected_counts}, got {data['locked_event_counts']}"
        )
    if data["event_counts_locked"] is not True:
        raise ValueError("event_counts_locked must be true")

    # Resolve local paths only in local mode. SSH/WSL2 paths belong to the target.
    if mode == "local":
        data["madgraph_path"] = os.path.abspath(os.path.expanduser(data["madgraph_path"]))
        data["workdir"] = os.path.abspath(os.path.expanduser(data["workdir"]))
        if data.get("cutexperiment_path"):
            data["cutexperiment_path"] = os.path.abspath(
                os.path.expanduser(data["cutexperiment_path"])
            )
    return _dict_to_namespace(data)


def main():
    parser = argparse.ArgumentParser(description="Load and validate run_config.json")
    parser.add_argument("path", help="Path to run_config.json")
    args = parser.parse_args()

    try:
        config = load_run_config(args.path)
        print(json.dumps(config.__dict__, indent=2, default=lambda o: o.__dict__))
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

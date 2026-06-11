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
    if not isinstance(data["energy"], list):
        raise ValueError(f"energy must be a list, got {type(data['energy'])}")
    if not isinstance(data["luminosity"], list):
        raise ValueError(f"luminosity must be a list, got {type(data['luminosity'])}")
    if not isinstance(data["run_configurations"], list):
        raise ValueError(
            f"run_configurations must be a list, got {type(data['run_configurations'])}"
        )

    # Cross-check lengths
    if len(data["energy"]) != len(data["luminosity"]):
        raise ValueError(
            f"energy ({len(data['energy'])}) and luminosity ({len(data['luminosity'])}) "
            "lengths must match"
        )
    if len(data["run_configurations"]) != len(data["energy"]):
        raise ValueError(
            f"run_configurations ({len(data['run_configurations'])}) and energy "
            f"({len(data['energy'])}) lengths must match"
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

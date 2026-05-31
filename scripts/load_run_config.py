#!/usr/bin/env python3
"""
Load and validate the run configuration produced by Phase -1.

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
    "custom_card",
    "polarization",
    "debug",
    "algorithms",
    "cutexperiment_path",
    "auto_installed_mg5",
]


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

    with open(path) as f:
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

    # Resolve absolute paths for key directories
    data["madgraph_path"] = os.path.abspath(os.path.expanduser(data["madgraph_path"]))
    data["workdir"] = os.path.abspath(os.path.expanduser(data["workdir"]))
    if data.get("cutexperiment_path"):
        data["cutexperiment_path"] = os.path.abspath(
            os.path.expanduser(data["cutexperiment_path"])
        )
    if data.get("custom_card"):
        data["custom_card"] = os.path.abspath(os.path.expanduser(data["custom_card"]))

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

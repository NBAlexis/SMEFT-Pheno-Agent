#!/usr/bin/env python3
"""Compute displayed collider sqrt(s) from explicit MG5 beam energies.

MG5 event generation uses ebeam1/ebeam2 in GeV. This helper is only for
manuscript/report metadata so agents do not recompute sqrt(s) by hand.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Any, Dict, Iterable, List


VALID_COLLIDERS = {"ee", "pp", "mumu", "ep"}
GEV_TO_TEV = 1.0 / 1000.0


def _positive_float(value: Any, name: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be numeric, got {value!r}")
    if not math.isfinite(parsed) or parsed <= 0:
        raise ValueError(f"{name} must be positive and finite, got {value!r}")
    return parsed


def compute_sqrt_s(collider_type: str, ebeam1: Any, ebeam2: Any) -> Dict[str, Any]:
    """Return beam-energy and sqrt(s) metadata.

    Args:
        collider_type: one of ee, pp, mumu, ep.
        ebeam1: beam 1 energy in GeV.
        ebeam2: beam 2 energy in GeV.

    Returns:
        Dict with beam energies, sqrt_s_gev, sqrt_s_tev, and formula metadata.
    """
    collider = str(collider_type).strip().lower()
    if collider not in VALID_COLLIDERS:
        raise ValueError(f"collider_type must be one of {sorted(VALID_COLLIDERS)}, got {collider_type!r}")

    beam1 = _positive_float(ebeam1, "ebeam1")
    beam2 = _positive_float(ebeam2, "ebeam2")

    if collider == "ep":
        sqrt_s_gev = math.sqrt(4.0 * beam1 * beam2)
        formula = "sqrt_s_gev = sqrt(4 * ebeam1 * ebeam2)"
    else:
        sqrt_s_gev = beam1 + beam2
        formula = "sqrt_s_gev = ebeam1 + ebeam2"

    return {
        "collider_type": collider,
        "ebeam1_gev": beam1,
        "ebeam2_gev": beam2,
        "sqrt_s_gev": sqrt_s_gev,
        "sqrt_s_tev": sqrt_s_gev * GEV_TO_TEV,
        "gev_to_tev": GEV_TO_TEV,
        "formula": formula,
        "usage": "manuscript_metadata_only_not_mg5_runner_input",
    }


def records_from_run_config(path: str) -> List[Dict[str, Any]]:
    """Compute sqrt(s) metadata for every run_configurations entry."""
    with open(path, "r", encoding="utf-8-sig") as f:
        config = json.load(f)
    collider_type = config.get("collider_type")
    if not collider_type:
        raise ValueError("run_config.json must include collider_type")
    runs = config.get("run_configurations")
    if not isinstance(runs, list) or not runs:
        raise ValueError("run_config.json must include non-empty run_configurations")

    records = []
    for idx, run in enumerate(runs):
        if not isinstance(run, dict):
            raise ValueError(f"run_configurations[{idx}] must be an object")
        record = compute_sqrt_s(collider_type, run.get("ebeam1"), run.get("ebeam2"))
        record["run_index"] = idx
        record["run_dir"] = run.get("run_dir")
        record["luminosity_fb_inv"] = run.get("luminosity")
        records.append(record)
    return records


def _write_json(path: str, data: Any) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute sqrt(s) from ebeam1/ebeam2")
    parser.add_argument("--run-config", help="Read collider_type and run_configurations from run_config.json")
    parser.add_argument("--collider-type", choices=sorted(VALID_COLLIDERS))
    parser.add_argument("--ebeam1", type=float)
    parser.add_argument("--ebeam2", type=float)
    parser.add_argument("--json-out")
    args = parser.parse_args()

    try:
        if args.run_config:
            result: Any = records_from_run_config(args.run_config)
        else:
            if args.collider_type is None or args.ebeam1 is None or args.ebeam2 is None:
                raise ValueError("provide either --run-config or --collider-type, --ebeam1, and --ebeam2")
            result = compute_sqrt_s(args.collider_type, args.ebeam1, args.ebeam2)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.json_out:
        _write_json(args.json_out, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

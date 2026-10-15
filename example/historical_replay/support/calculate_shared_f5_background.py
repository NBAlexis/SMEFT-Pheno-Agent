#!/usr/bin/env python3
"""Calculate a selected shared-f5 background cross-section."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Any, Dict


MAX_ADDITIONAL_ANCHOR_ROUNDS = 3


def calculate_shared_f5_background(
    merged_cross_section_pb: float,
    loaded_lhco_event_count: int,
    passing_event_count: int,
    additional_anchor_f5_rounds: int,
) -> Dict[str, Any]:
    """Return the background estimate or state that another anchor round is required."""
    if isinstance(merged_cross_section_pb, bool) or not isinstance(
        merged_cross_section_pb, (int, float)
    ):
        raise ValueError("merged_cross_section_pb must be a finite positive number")
    merged_cross_section_pb = float(merged_cross_section_pb)
    if not math.isfinite(merged_cross_section_pb) or merged_cross_section_pb <= 0.0:
        raise ValueError("merged_cross_section_pb must be a finite positive number")
    if isinstance(loaded_lhco_event_count, bool) or not isinstance(loaded_lhco_event_count, int):
        raise ValueError("loaded_lhco_event_count must be a positive integer")
    if loaded_lhco_event_count <= 0:
        raise ValueError("loaded_lhco_event_count must be a positive integer")
    if isinstance(passing_event_count, bool) or not isinstance(passing_event_count, int):
        raise ValueError("passing_event_count must be a non-negative integer")
    if passing_event_count < 0 or passing_event_count > loaded_lhco_event_count:
        raise ValueError(
            "passing_event_count must be between zero and loaded_lhco_event_count"
        )
    if isinstance(additional_anchor_f5_rounds, bool) or not isinstance(
        additional_anchor_f5_rounds, int
    ):
        raise ValueError("additional_anchor_f5_rounds must be an integer in [0, 3]")
    if not 0 <= additional_anchor_f5_rounds <= MAX_ADDITIONAL_ANCHOR_ROUNDS:
        raise ValueError("additional_anchor_f5_rounds must be an integer in [0, 3]")

    if passing_event_count > 0:
        effective_count = float(passing_event_count)
        convention = "observed_events"
        status = "accepted"
    elif additional_anchor_f5_rounds < MAX_ADDITIONAL_ANCHOR_ROUNDS:
        return {
            "status": "additional_anchor_f5_required",
            "passing_event_count": 0,
            "effective_passing_event_count": None,
            "additional_anchor_f5_rounds": additional_anchor_f5_rounds,
            "convention": "unresolved_zero",
            "sigma0_after_cut_pb": None,
        }
    else:
        effective_count = 0.5
        convention = "half_event_after_three_zero_rounds"
        status = "accepted"

    return {
        "status": status,
        "passing_event_count": passing_event_count,
        "effective_passing_event_count": effective_count,
        "additional_anchor_f5_rounds": additional_anchor_f5_rounds,
        "convention": convention,
        "sigma0_after_cut_pb": (
            merged_cross_section_pb * effective_count / loaded_lhco_event_count
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Calculate one algorithm/threshold shared-f5 background estimate"
    )
    parser.add_argument("--input", required=True, help="Input JSON record")
    parser.add_argument("--output", required=True, help="Output JSON record")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8-sig") as handle:
            data = json.load(handle)
        result = calculate_shared_f5_background(
            data["merged_cross_section_pb"],
            data["loaded_lhco_event_count"],
            data["passing_event_count"],
            data["additional_anchor_f5_rounds"],
        )
        output_path = os.path.abspath(os.path.expanduser(args.output))
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2, sort_keys=True)
            handle.write("\n")
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

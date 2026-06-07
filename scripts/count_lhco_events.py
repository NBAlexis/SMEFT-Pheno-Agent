#!/usr/bin/env python3
"""Count events in an LHCO file using CutExperiment.

The loaded LHCO event count is the only valid denominator for selection
efficiencies in this workflow. Do not use planned MG5 nevents or banner event
counts for this purpose.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, Optional


VALID_CONTEXTS = {"mg5_output", "merged_output", "analysis_input"}


def _add_cutexperiment_path(cutexperiment_path: Optional[str]) -> None:
    if not cutexperiment_path:
        return
    path = os.path.abspath(os.path.expanduser(cutexperiment_path))
    if path not in sys.path:
        sys.path.insert(0, path)


def load_lhco_event_count(lhco_path: str, cutexperiment_path: Optional[str] = None) -> int:
    """Return CutExperiment LoadLHCOlympics(...).GetEventCount()."""
    _add_cutexperiment_path(cutexperiment_path)
    from Interfaces.LHCOlympics import LoadLHCOlympics  # type: ignore

    events = LoadLHCOlympics(lhco_path)
    return int(events.GetEventCount())


def count_lhco_events(
    lhco_path: str,
    requested_event_count: Optional[int] = None,
    dataset_id: Optional[str] = None,
    count_context: str = "analysis_input",
    cutexperiment_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Count one LHCO file and return a standard metadata record."""
    if count_context not in VALID_CONTEXTS:
        raise ValueError(
            f"count_context must be one of {sorted(VALID_CONTEXTS)}, got {count_context!r}"
        )

    abs_path = os.path.abspath(os.path.expanduser(lhco_path))
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"LHCO file not found: {abs_path}")

    loaded = load_lhco_event_count(abs_path, cutexperiment_path=cutexperiment_path)
    fraction = None
    if requested_event_count is not None:
        if requested_event_count <= 0:
            raise ValueError("requested_event_count must be positive when provided")
        fraction = loaded / float(requested_event_count)

    status = "ok"
    if loaded == 0:
        status = "zero_events"
    elif fraction is not None and fraction < 0.1:
        status = "below_recovery_floor"
    elif fraction is not None and fraction < 0.9:
        status = "accepted_with_warning"

    return {
        "dataset_id": dataset_id,
        "lhco_path": abs_path,
        "requested_event_count": requested_event_count,
        "loaded_lhco_event_count": loaded,
        "fraction": fraction,
        "count_source": "CutExperiment LoadLHCOlympics(...).GetEventCount()",
        "count_context": count_context,
        "status": status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Count LHCO events with CutExperiment")
    parser.add_argument("lhco_path")
    parser.add_argument("--requested-event-count", type=int, default=None)
    parser.add_argument("--dataset-id", default=None)
    parser.add_argument(
        "--count-context",
        default="analysis_input",
        choices=sorted(VALID_CONTEXTS),
    )
    parser.add_argument("--cutexperiment-path", default=None)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    try:
        record = count_lhco_events(
            args.lhco_path,
            requested_event_count=args.requested_event_count,
            dataset_id=args.dataset_id,
            count_context=args.count_context,
            cutexperiment_path=args.cutexperiment_path,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(record, indent=2, sort_keys=True)
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())


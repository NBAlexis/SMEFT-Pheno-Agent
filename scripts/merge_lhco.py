#!/usr/bin/env python3
"""Merge LHCO files with CutExperiment and write reproducible metadata."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any, Dict, Iterable, List, Optional

try:
    from .count_lhco_events import count_lhco_events
    from .extract_cross_section import extract_cross_section
except ImportError:  # Direct script execution.
    from count_lhco_events import count_lhco_events
    from extract_cross_section import extract_cross_section


def _add_cutexperiment_path(cutexperiment_path: Optional[str]) -> None:
    if not cutexperiment_path:
        return
    path = os.path.abspath(os.path.expanduser(cutexperiment_path))
    if path not in sys.path:
        sys.path.insert(0, path)


def _load_event_set(lhco_path: str, cutexperiment_path: Optional[str]):
    _add_cutexperiment_path(cutexperiment_path)
    from Interfaces.LHCOlympics import LoadLHCOlympics  # type: ignore

    return LoadLHCOlympics(lhco_path)


def _save_event_set(event_set, output_path: str) -> None:
    if hasattr(event_set, "SaveToLHCO"):
        event_set.SaveToLHCO(output_path)
        return
    raise RuntimeError("CutExperiment event set has no SaveToLHCO method")


def _read_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _source_records(
    lhco_paths: Iterable[str],
    banner_paths: Optional[Iterable[Optional[str]]],
    requested_event_count: Optional[int],
    cutexperiment_path: Optional[str],
) -> List[Dict[str, Any]]:
    banners = list(banner_paths or [])
    paths = list(lhco_paths)
    if banners and len(banners) != len(paths):
        raise ValueError("source_banners length must match source_lhco_paths")

    records = []
    for index, lhco in enumerate(paths):
        banner = banners[index] if banners else None
        count = count_lhco_events(
            lhco,
            requested_event_count=requested_event_count,
            dataset_id=f"source_{index}",
            count_context="mg5_output",
            cutexperiment_path=cutexperiment_path,
        )
        if count["loaded_lhco_event_count"] <= 0:
            raise ValueError(f"Refusing to merge empty LHCO: {lhco}")
        cross_section_pb = None
        if banner:
            cross_section_pb = extract_cross_section(banner)
        records.append({
            "index": index,
            "lhco_path": os.path.abspath(os.path.expanduser(lhco)),
            "banner_path": os.path.abspath(os.path.expanduser(banner)) if banner else None,
            "loaded_lhco_event_count": count["loaded_lhco_event_count"],
            "cross_section_pb": cross_section_pb,
            "count_record": count,
        })
    return records


def merge_lhco(
    source_lhco_paths: List[str],
    output_lhco_path: str,
    cutexperiment_path: Optional[str] = None,
    source_banner_paths: Optional[List[Optional[str]]] = None,
    requested_event_count: Optional[int] = None,
    metadata_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Merge parseable non-empty LHCO files and return metadata."""
    if not source_lhco_paths:
        raise ValueError("At least one source LHCO path is required")

    output_abs = os.path.abspath(os.path.expanduser(output_lhco_path))
    os.makedirs(os.path.dirname(output_abs), exist_ok=True)

    records = _source_records(
        source_lhco_paths,
        source_banner_paths,
        requested_event_count,
        cutexperiment_path,
    )

    merged = _load_event_set(records[0]["lhco_path"], cutexperiment_path)
    for rec in records[1:]:
        event_set = _load_event_set(rec["lhco_path"], cutexperiment_path)
        if not hasattr(merged, "AddEventSet"):
            raise RuntimeError("CutExperiment event set has no AddEventSet method")
        merged.AddEventSet(event_set)
    _save_event_set(merged, output_abs)

    merged_count_record = count_lhco_events(
        output_abs,
        requested_event_count=requested_event_count,
        dataset_id="merged",
        count_context="merged_output",
        cutexperiment_path=cutexperiment_path,
    )
    source_total = sum(int(r["loaded_lhco_event_count"]) for r in records)
    if int(merged_count_record["loaded_lhco_event_count"]) != source_total:
        raise RuntimeError(
            "Merged LHCO count mismatch: "
            f"{merged_count_record['loaded_lhco_event_count']} != {source_total}"
        )

    weighted_cross_section_pb = None
    if all(r["cross_section_pb"] is not None for r in records):
        weighted_cross_section_pb = sum(
            float(r["cross_section_pb"]) * int(r["loaded_lhco_event_count"])
            for r in records
        ) / float(source_total)

    metadata = {
        "output_lhco_path": output_abs,
        "requested_event_count": requested_event_count,
        "merged_loaded_lhco_event_count": merged_count_record["loaded_lhco_event_count"],
        "count_source": merged_count_record["count_source"],
        "source_count_sum": source_total,
        "source_banners_retained": [r["banner_path"] for r in records],
        "source_records": records,
        "merged_cross_section_pb": weighted_cross_section_pb,
        "cross_section_rule": (
            "loaded-LHCO-event-count-weighted average of source banner cross-sections"
        ),
    }

    if metadata_path:
        meta_abs = os.path.abspath(os.path.expanduser(metadata_path))
        os.makedirs(os.path.dirname(meta_abs), exist_ok=True)
        with open(meta_abs, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, sort_keys=True)
            f.write("\n")

    return metadata


def main() -> int:
    parser = argparse.ArgumentParser(description="Merge LHCO files with CutExperiment")
    parser.add_argument("--config", help="JSON config with source_lhco_paths/output_lhco_path")
    parser.add_argument("--output", help="Output LHCO path")
    parser.add_argument("--metadata", help="Output metadata JSON path")
    parser.add_argument("--cutexperiment-path", default=None)
    parser.add_argument("--requested-event-count", type=int, default=None)
    parser.add_argument("--source", action="append", default=[], help="Source LHCO path")
    parser.add_argument("--banner", action="append", default=[], help="Source banner path")
    args = parser.parse_args()

    try:
        if args.config:
            cfg = _read_config(args.config)
            metadata = merge_lhco(
                cfg["source_lhco_paths"],
                cfg["output_lhco_path"],
                cutexperiment_path=cfg.get("cutexperiment_path", args.cutexperiment_path),
                source_banner_paths=cfg.get("source_banner_paths"),
                requested_event_count=cfg.get("requested_event_count", args.requested_event_count),
                metadata_path=cfg.get("metadata_path", args.metadata),
            )
        else:
            metadata = merge_lhco(
                args.source,
                args.output,
                cutexperiment_path=args.cutexperiment_path,
                source_banner_paths=args.banner or None,
                requested_event_count=args.requested_event_count,
                metadata_path=args.metadata,
            )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(json.dumps(metadata, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Archive runner-recorded MG5 process directories and order files."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import sys
from typing import Any, Dict, Iterable, Set, Tuple


LARGE_SUFFIXES = (".root", ".hepmc", ".hepmc.gz")


def _iter_objects(value: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _iter_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_objects(child)


def _runner_paths(run_root: str) -> Tuple[Set[str], Set[str]]:
    process_dirs: Set[str] = set()
    order_files: Set[str] = set()
    data_root = os.path.join(run_root, "data")
    if not os.path.isdir(data_root):
        return process_dirs, order_files
    for current, _, filenames in os.walk(data_root):
        for filename in filenames:
            if not filename.endswith(".json"):
                continue
            path = os.path.join(current, filename)
            try:
                with open(path, encoding="utf-8-sig") as handle:
                    data = json.load(handle)
            except (OSError, json.JSONDecodeError):
                continue
            for record in _iter_objects(data):
                process = record.get("broken_process_dir") or record.get("process_dir")
                order = record.get("order_file_path")
                if isinstance(process, str) and process.strip():
                    process_dirs.add(os.path.abspath(os.path.expanduser(process)))
                if isinstance(order, str) and order.strip():
                    order_files.add(os.path.abspath(os.path.expanduser(order)))
    return process_dirs, order_files


def _delete_large_files(process_dir: str) -> list[str]:
    deleted = []
    for current, _, filenames in os.walk(process_dir):
        for filename in filenames:
            if filename.lower().endswith(LARGE_SUFFIXES):
                path = os.path.abspath(os.path.join(current, filename))
                os.remove(path)
                deleted.append(path)
    return sorted(deleted)


def _archive_one(source: str, destination_dir: str, *, is_directory: bool) -> Tuple[str, bool]:
    destination = os.path.abspath(os.path.join(destination_dir, os.path.basename(source)))
    source = os.path.abspath(source)
    exists = os.path.isdir(source) if is_directory else os.path.isfile(source)
    if exists:
        if os.path.exists(destination) and source != destination:
            raise FileExistsError(
                f"Archive destination already exists; compare contents before retrying: {destination}"
            )
        if source != destination:
            shutil.move(source, destination)
        return destination, True
    destination_exists = (
        os.path.isdir(destination) if is_directory else os.path.isfile(destination)
    )
    if destination_exists:
        return destination, True
    return source, False


def archive_mg5_outputs(run_root: str, *, delete_large: bool = False) -> Dict[str, Any]:
    run_root = os.path.abspath(run_root)
    process_destination = os.path.join(run_root, "mg5_processes")
    order_destination = os.path.join(run_root, "orders")
    os.makedirs(process_destination, exist_ok=True)
    os.makedirs(order_destination, exist_ok=True)

    process_dirs, order_files = _runner_paths(run_root)
    if not process_dirs or not order_files:
        raise RuntimeError(
            "Runner JSON discovery found no process directories or no order files; "
            "inspect data/**/*.json before cleanup"
        )

    moved_process_dirs = []
    missing_process_dirs = []
    moved_order_files = []
    missing_order_files = []
    deleted_files = []

    for source in sorted(process_dirs):
        if delete_large and os.path.isdir(source):
            deleted_files.extend(_delete_large_files(source))
        archived, found = _archive_one(source, process_destination, is_directory=True)
        (moved_process_dirs if found else missing_process_dirs).append(archived)

    for source in sorted(order_files):
        archived, found = _archive_one(source, order_destination, is_directory=False)
        (moved_order_files if found else missing_order_files).append(archived)

    log = {
        "cleanup_time": dt.datetime.now(dt.timezone.utc).isoformat(),
        "destination_processes": os.path.abspath(process_destination),
        "destination_orders": os.path.abspath(order_destination),
        "expected_process_dirs": sorted(process_dirs),
        "moved_process_dirs": moved_process_dirs,
        "missing_process_dirs": missing_process_dirs,
        "expected_order_files": sorted(order_files),
        "moved_order_files": moved_order_files,
        "missing_order_files": missing_order_files,
        "deleted_files": deleted_files,
        "total_moved_dirs": len(moved_process_dirs),
        "total_moved_orders": len(moved_order_files),
    }
    log_path = os.path.join(process_destination, "cleanup_log.json")
    with open(log_path, "w", encoding="utf-8") as handle:
        json.dump(log, handle, indent=2, sort_keys=True)
        handle.write("\n")
    log["cleanup_log_path"] = os.path.abspath(log_path)

    if missing_process_dirs or missing_order_files:
        raise RuntimeError(
            f"Cleanup is incomplete; inspect {log_path}: "
            f"missing_process_dirs={missing_process_dirs}, missing_order_files={missing_order_files}"
        )
    return log


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Archive runner-recorded MG5 process directories and order files"
    )
    parser.add_argument("run_root", help="Single-run results/ or multi-run results/<run_dir>/")
    parser.add_argument(
        "--delete-large",
        action="store_true",
        help="Delete only .root, .hepmc, and .hepmc.gz files before moving process directories",
    )
    args = parser.parse_args()
    try:
        result = archive_mg5_outputs(args.run_root, delete_large=args.delete_large)
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Mechanically confirm an MG5 zero-cross-section result.

This checker is intentionally simple: a zero cross-section is accepted only
when the banner evidence is zero or missing, MG5 logs explicitly mention a
zero cross section, and the run directory contains no substantial LHE-like
event payload.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tarfile
from typing import Any, Dict, Iterable, List, Optional


ZERO_CROSS_RE = re.compile(r"zero\s*cross[\s-]*section", re.IGNORECASE)
DEFAULT_SMALL_LHE_BYTES = 4096


def _read_text(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except FileNotFoundError:
        return ""


def _log_matches(paths: Iterable[str]) -> List[str]:
    matches = []
    for path in paths:
        if path and ZERO_CROSS_RE.search(_read_text(path)):
            matches.append(os.path.abspath(path))
    return matches


def _tar_contains_lhe(path: str) -> bool:
    try:
        with tarfile.open(path, "r:*") as tar:
            return any(".lhe" in member.name.lower() for member in tar.getmembers())
    except (tarfile.TarError, OSError):
        return False


def _is_lhe_like(path: str) -> bool:
    name = os.path.basename(path).lower()
    if ".lhe" in name:
        return True
    if name.endswith((".tar", ".tar.gz", ".tgz")):
        return _tar_contains_lhe(path)
    return False


def _lhe_records(run_dir: Optional[str], small_lhe_bytes: int) -> List[Dict[str, Any]]:
    if not run_dir or not os.path.isdir(run_dir):
        return []
    records = []
    for root, _, files in os.walk(run_dir):
        for filename in files:
            path = os.path.join(root, filename)
            if not _is_lhe_like(path):
                continue
            size = os.path.getsize(path)
            records.append(
                {
                    "path": os.path.abspath(path),
                    "size_bytes": size,
                    "substantial": size > small_lhe_bytes,
                }
            )
    return records


def double_check_zero_cross_section(
    cross_section_pb: Optional[float],
    stdout_paths: Iterable[str],
    stderr_paths: Iterable[str],
    run_dir: Optional[str],
    *,
    banner_missing: bool = False,
    small_lhe_bytes: int = DEFAULT_SMALL_LHE_BYTES,
) -> Dict[str, Any]:
    """Return a mechanical zero-cross-section confirmation report."""
    stdout_paths = [p for p in stdout_paths if p]
    stderr_paths = [p for p in stderr_paths if p]
    log_paths = stdout_paths + stderr_paths
    log_matches = _log_matches(log_paths)
    lhe_files = _lhe_records(run_dir, small_lhe_bytes)
    substantial_lhe = [item for item in lhe_files if item["substantial"]]
    cross_section_is_zero = (
        cross_section_pb is not None and float(cross_section_pb) == 0.0
    )
    cross_section_zero_or_banner_missing = cross_section_is_zero or banner_missing
    no_substantial_lhe = not substantial_lhe
    confirmed = (
        cross_section_zero_or_banner_missing
        and bool(log_matches)
        and no_substantial_lhe
    )
    status = (
        "confirmed_zero_cross_section"
        if confirmed
        else "suspicious_zero_cross_section"
        if cross_section_zero_or_banner_missing
        else "not_zero_cross_section"
    )
    return {
        "status": status,
        "confirmed": confirmed,
        "cross_section_pb": cross_section_pb,
        "cross_section_is_zero": cross_section_is_zero,
        "banner_missing": banner_missing,
        "cross_section_zero_or_banner_missing": cross_section_zero_or_banner_missing,
        "zero_cross_section_log_matches": log_matches,
        "stdout_paths": [os.path.abspath(p) for p in stdout_paths],
        "stderr_paths": [os.path.abspath(p) for p in stderr_paths],
        "run_dir": os.path.abspath(run_dir) if run_dir else None,
        "small_lhe_bytes": small_lhe_bytes,
        "lhe_files": lhe_files,
        "substantial_lhe_files": substantial_lhe,
        "no_substantial_lhe": no_substantial_lhe,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Double-check an MG5 zero cross-section claim")
    parser.add_argument("--cross-section", type=float, help="Parsed banner cross-section in pb")
    parser.add_argument("--banner-missing", action="store_true", help="Treat a missing banner as the first zero-cross-section evidence")
    parser.add_argument("--stdout-log", action="append", default=[], help="MG5 stdout log path")
    parser.add_argument("--stderr-log", action="append", default=[], help="MG5 stderr log path")
    parser.add_argument("--run-dir", help="MG5 Events/run_* directory to inspect for LHE-like files")
    parser.add_argument("--small-lhe-bytes", type=int, default=DEFAULT_SMALL_LHE_BYTES)
    parser.add_argument("--json-output", help="Optional path to write the JSON report")
    args = parser.parse_args()

    report = double_check_zero_cross_section(
        args.cross_section,
        args.stdout_log,
        args.stderr_log,
        args.run_dir,
        banner_missing=args.banner_missing,
        small_lhe_bytes=args.small_lhe_bytes,
    )
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.json_output:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_output)), exist_ok=True)
        with open(args.json_output, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    print(text)
    if report["cross_section_zero_or_banner_missing"] and not report["confirmed"]:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Extract a conservative MG5 weighted-order bound from generated diagrams.

MG5 writes diagram coupling orders into each subprocess ``matrix1.ps`` file,
for example ``(NP=0, QCD=1, QED=3)``. This helper reads those labels from one
or more process folders, reads coupling-order hierarchies from the UFO model's
``coupling_orders.py``, and returns the maximum weighted order

    weighted = sum(order[name] * hierarchy[name])

across all diagrams it can parse.

Use this before SM+NP process creation when a process may lose SM diagrams due
to coupling-order hierarchy choices. If this script fails, inspect the MG5
process folders and UFO model manually and record the equivalent value.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, Iterable, List


ORDER_LABEL_RE = re.compile(r"\(([^()]*\b[A-Za-z_]\w*\s*=\s*\d+[^()]*)\)")
ORDER_PAIR_RE = re.compile(r"\b([A-Za-z_]\w*)\s*=\s*(\d+)\b")
COUPLING_ORDER_RE = re.compile(
    r"CouplingOrder\(\s*name\s*=\s*['\"]([^'\"]+)['\"](?P<body>.*?)\)",
    re.S,
)
HIERARCHY_RE = re.compile(r"hierarchy\s*=\s*(-?\d+)")


def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _read_subprocess_names(process_dir: str) -> List[str]:
    subproc_path = os.path.join(process_dir, "SubProcesses", "subproc.mg")
    if not os.path.exists(subproc_path):
        raise FileNotFoundError(f"Missing SubProcesses/subproc.mg under {process_dir}")
    names = []
    for line in _read_text(subproc_path).splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            names.append(stripped)
    if not names:
        raise ValueError(f"No subprocess names found in {subproc_path}")
    return names


def _parse_hierarchies(model_dir: str) -> Dict[str, int]:
    path = os.path.join(model_dir, "coupling_orders.py")
    if not os.path.exists(path):
        raise FileNotFoundError(f"Missing coupling_orders.py under {model_dir}")
    text = _read_text(path)
    hierarchies: Dict[str, int] = {}
    for match in COUPLING_ORDER_RE.finditer(text):
        name = match.group(1)
        hierarchy_match = HIERARCHY_RE.search(match.group("body"))
        if hierarchy_match:
            hierarchies[name] = int(hierarchy_match.group(1))
    if not hierarchies:
        raise ValueError(f"No CouplingOrder hierarchy entries found in {path}")
    return hierarchies


def _parse_matrix_orders(matrix_path: str) -> List[Dict[str, int]]:
    text = _read_text(matrix_path)
    records: List[Dict[str, int]] = []
    for label_match in ORDER_LABEL_RE.finditer(text):
        pairs = {
            key: int(value)
            for key, value in ORDER_PAIR_RE.findall(label_match.group(1))
        }
        if pairs:
            records.append(pairs)
    return records


def _iter_matrix_paths(process_dirs: Iterable[str]) -> Iterable[str]:
    for process_dir in process_dirs:
        for subproc in _read_subprocess_names(process_dir):
            matrix_path = os.path.join(process_dir, "SubProcesses", subproc, "matrix1.ps")
            if os.path.exists(matrix_path):
                yield os.path.abspath(matrix_path)


def extract_weighted_order(model_dir: str, process_dirs: Iterable[str]) -> Dict[str, Any]:
    model_dir = os.path.abspath(model_dir)
    coupling_orders_path = os.path.join(model_dir, "coupling_orders.py")
    hierarchies = _parse_hierarchies(model_dir)
    diagrams: List[Dict[str, Any]] = []
    missing_hierarchies: Dict[str, set] = {}

    for matrix_path in _iter_matrix_paths(process_dirs):
        for orders in _parse_matrix_orders(matrix_path):
            weighted = 0
            for name, value in orders.items():
                if name not in hierarchies:
                    missing_hierarchies.setdefault(name, set()).add(matrix_path)
                    continue
                weighted += value * hierarchies[name]
            diagrams.append({
                "matrix_path": matrix_path,
                "orders": orders,
                "weighted": weighted,
            })

    if not diagrams:
        raise ValueError("No diagram order labels found in supplied process folders")
    if missing_hierarchies:
        missing_details = "; ".join(
            f"{name} in {', '.join(sorted(paths))}"
            for name, paths in sorted(missing_hierarchies.items())
        )
        raise ValueError(
            "Missing coupling-order hierarchies for: "
            + ", ".join(sorted(missing_hierarchies))
            + f". Model hierarchy file: {coupling_orders_path}. Diagram files: "
            + missing_details
        )

    max_weighted = max(item["weighted"] for item in diagrams)
    max_diagrams = [item for item in diagrams if item["weighted"] == max_weighted]
    return {
        "schema_version": "1.0",
        "model_dir": model_dir,
        "process_dirs": [os.path.abspath(p) for p in process_dirs],
        "hierarchies": hierarchies,
        "max_weighted_order": int(max_weighted),
        "diagram_count": len(diagrams),
        "max_diagram_count": len(max_diagrams),
        "max_diagram_examples": max_diagrams[:3],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract conservative MG5 WEIGHTED order")
    parser.add_argument("--model-dir", required=True)
    parser.add_argument("--process-dir", action="append", required=True)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    try:
        result = extract_weighted_order(args.model_dir, args.process_dir)
    except Exception as exc:
        print(f"Error: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, sort_keys=True)
            f.write("\n")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

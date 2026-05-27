#!/usr/bin/env python3
"""
Parse Block anoinputs from an MG5 param_card.dat.

Handles case-insensitive Block matching and scan syntax retention.
Returns a dict mapping LHA index → coefficient value.

Usage:
    python parse_param_card.py <param_card_path>

Output (JSON):
    {"1": 1.0e-12, "2": 0.0, "3": 0.0, ...}

Exit codes:
    0  success
    1  file not found
    2  Block anoinputs not found
"""
import json
import sys
import os


def parse_anoinputs(param_card_path, scan_default=1.0e-12):
    """Parse Block anoinputs from an MG5 param_card.dat.

    Handles:
    - Case-insensitive Block matching (MG5 may rewrite BLOCK in uppercase)
    - scan:[...] syntax retained after MG5 scan
    - Block boundary detection (prevents leaking into Block mass, etc.)

    Args:
        param_card_path: path to param_card.dat
        scan_default: default value when scan syntax is detected

    Returns:
        dict mapping LHA index (str) → coefficient value (float)

    Raises:
        ValueError: if Block anoinputs is not found
    """
    coefficients = {}
    in_block = False
    found = False

    with open(param_card_path) as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            # Case-insensitive Block matching
            if stripped.lower().startswith("block"):
                in_block = stripped.lower().startswith("block anoinputs")
                if in_block:
                    found = True
                continue

            if not in_block:
                continue

            parts = stripped.split()
            if len(parts) >= 2:
                idx, val = parts[0], parts[1]
                # Handle scan syntax: scan:[v1,v2,...]
                if val.lower().startswith("scan:"):
                    coefficients[idx] = float(scan_default)
                else:
                    coefficients[idx] = float(val)

    if not found:
        raise ValueError(f"Block anoinputs not found in {param_card_path}")

    return coefficients


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <param_card_path> [scan_default]", file=sys.stderr)
        sys.exit(1)

    param_card_path = sys.argv[1]
    scan_default = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0e-12

    if not os.path.exists(param_card_path):
        print(f"Error: file not found: {param_card_path}", file=sys.stderr)
        sys.exit(1)

    try:
        coeffs = parse_anoinputs(param_card_path, scan_default)
        print(json.dumps(coeffs))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

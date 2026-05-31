#!/usr/bin/env python3
"""
Parse coefficient Block from an MG5 param_card.dat.

Supports custom Block names (e.g., anoinputs, dim6, dim8, aqgc).
Auto-detects the coefficient block if not specified.

Handles case-insensitive Block matching and scan syntax retention.
Returns a dict mapping LHA index → coefficient value.

Usage:
    python parse_param_card.py <param_card_path> [--block BLOCK_NAME]

Output (JSON):
    {"block_name": "anoinputs", "coefficients": {"1": 1.0e-12, "2": 0.0, ...}}

Exit codes:
    0  success
    1  file not found
    2  no coefficient block found
"""
import argparse
import json
import sys
import os


# Known non-coefficient blocks — excluded from auto-detection
NON_COEFF_BLOCKS = {
    "mass", "sminputs", "yukawa", "ckm", "decay",
    "qnumbers", "mgincoming", "mgdecay",
    "mzpole", "mwpole", "sin2theta", "vd", "vu",
    "msoft", "nmssmrun", "spinfo", "modsel",
    "frblock"  # FeynRules parameters (not anomalous couplings)
}


def _find_coefficient_block(param_card_path):
    """Scan param_card for candidate coefficient blocks."""
    candidates = []
    with open(param_card_path) as f:
        for line in f:
            stripped = line.strip()
            if stripped.lower().startswith("block"):
                parts = stripped.split()
                if len(parts) >= 2:
                    block_name = parts[1].lower().rstrip("#")
                    if block_name not in NON_COEFF_BLOCKS:
                        candidates.append(block_name)
    return candidates


def parse_coefficients(param_card_path, block_name=None, scan_default=1.0e-12):
    """Parse a coefficient Block from an MG5 param_card.dat.

    Handles:
    - Case-insensitive Block matching (MG5 may rewrite BLOCK in uppercase)
    - scan:[...] syntax retained after MG5 scan
    - Block boundary detection (prevents leaking into Block mass, etc.)

    Args:
        param_card_path: path to param_card.dat
        block_name: coefficient Block name (e.g., 'anoinputs', 'dim8').
                    If None, auto-detects from param_card.
        scan_default: default value when scan syntax is detected

    Returns:
        dict with keys:
            'block_name': str, the detected block name
            'coefficients': dict mapping LHA index (str) → coefficient value (float)

    Raises:
        ValueError: if no coefficient block is found
    """
    if block_name is None:
        candidates = _find_coefficient_block(param_card_path)
        if not candidates:
            raise ValueError(f"No coefficient block found in {param_card_path}")
        block_name = candidates[0]
    else:
        block_name = block_name.lower()

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
                parts = stripped.split()
                current_block = parts[1].lower().rstrip("#") if len(parts) >= 2 else ""
                in_block = (current_block == block_name)
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
                    try:
                        coefficients[idx] = float(val)
                    except ValueError:
                        # Malformed line — skip
                        continue

    if not found:
        raise ValueError(f"Block {block_name} not found in {param_card_path}")

    return {"block_name": block_name, "coefficients": coefficients}


# Backward-compatible alias
parse_anoinputs = parse_coefficients


def main():
    parser = argparse.ArgumentParser(description="Parse coefficient block from MG5 param_card.dat")
    parser.add_argument("param_card_path", help="Path to param_card.dat")
    parser.add_argument("--block", default=None,
                        help="Coefficient Block name (e.g., anoinputs, dim8). Auto-detected if omitted.")
    parser.add_argument("--scan-default", type=float, default=1.0e-12,
                        help="Default value when scan syntax is detected")
    args = parser.parse_args()

    if not os.path.exists(args.param_card_path):
        print(f"Error: file not found: {args.param_card_path}", file=sys.stderr)
        sys.exit(1)

    try:
        result = parse_coefficients(args.param_card_path, block_name=args.block, scan_default=args.scan_default)
        print(json.dumps(result))
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

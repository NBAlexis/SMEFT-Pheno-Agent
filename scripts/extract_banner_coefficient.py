#!/usr/bin/env python3
"""
Extract the scanned coefficient value from an MG5 banner file.

MG5 records the parameter values used in each run within the banner.
This script parses the banner to find the value of a specific anoinputs index.

Usage:
    python extract_banner_coefficient.py <banner_path> <anoinputs_index>

Output:
    The coefficient value as a float (e.g., 2.184408e-11)

Exit codes:
    0  success
    1  file not found
    2  coefficient not found in banner
"""
import re
import sys
import os


def extract_banner_coefficient(banner_path, anoinputs_idx):
    """Extract the value of a specific anoinputs coefficient from an MG5 banner.

    MG5 banners record the parameter values in the BLOCK ANOINPUTS section
    in LHA format:
        ## INFORMATION FOR ANOINPUTS
        BLOCK ANOINPUTS #
              1 0.000000e+00 # fgt0
              2 1.000000e-12 # fgt1

    Args:
        banner_path: path to the banner file
        anoinputs_idx: LHA index (e.g., 1, 2, 3) or string

    Returns:
        float: the coefficient value

    Raises:
        ValueError: if the coefficient is not found in the banner
    """
    in_block = False
    idx_str = str(anoinputs_idx)
    # Match: optional spaces, index, spaces, value (scientific notation), optional comment
    pattern = re.compile(rf"^\s*{idx_str}\s+([\d.eE+-]+)")

    with open(banner_path) as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("!"):
                continue
            if "INFORMATION FOR ANOINPUTS" in stripped:
                in_block = True
                continue
            if in_block:
                if stripped.lower().startswith("block anoinputs"):
                    continue
                # Exit block on next BLOCK header or DECAY
                if stripped.lower().startswith("block") or stripped.lower().startswith("decay"):
                    in_block = False
                    continue
                m = pattern.match(line)
                if m:
                    return float(m.group(1))

    raise ValueError(
        f"anoinputs {anoinputs_idx} not found in banner {banner_path}"
    )


def main():
    if len(sys.argv) < 3:
        print(
            f"Usage: {sys.argv[0]} <banner_path> <anoinputs_index>",
            file=sys.stderr
        )
        sys.exit(1)

    banner_path = sys.argv[1]
    anoinputs_idx = sys.argv[2]

    if not os.path.exists(banner_path):
        print(f"Error: file not found: {banner_path}", file=sys.stderr)
        sys.exit(1)

    try:
        val = extract_banner_coefficient(banner_path, anoinputs_idx)
        print(val)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Extract cross-section in pb from an MG5_aMC banner file.

Supports both MG5_aMC v3.x and older banner formats.
Raises ValueError if no cross-section line is found.

Usage:
    python extract_cross_section.py <banner_path>

Exit codes:
    0  success — prints cross-section in pb
    1  file not found
    2  parse error (no cross-section line found)
"""
import re
import sys
import os


def extract_cross_section(banner_path):
    """Extract cross-section in pb from an MG5 banner file.

    Supports both MG5_aMC v3.x and older banner formats.
    Raises ValueError if no cross-section line is found.
    """
    with open(banner_path) as f:
        for line in f:
            # Primary: MG5_aMC v3.x format
            m = re.search(r"Integrated weight \(pb\)\s*:\s*([\d.eE+-]+)", line)
            if m:
                return float(m.group(1))
            # Fallback: older format with uncertainty
            m = re.search(r"([\d.eE+-]+)\s*\+/-\s*([\d.eE+-]+)\s*pb", line)
            if m:
                return float(m.group(1))
    raise ValueError(f"No cross-section found in {banner_path}")


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <banner_path>", file=sys.stderr)
        sys.exit(1)

    banner_path = sys.argv[1]
    if not os.path.exists(banner_path):
        print(f"Error: file not found: {banner_path}", file=sys.stderr)
        sys.exit(1)

    try:
        cs = extract_cross_section(banner_path)
        print(cs)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

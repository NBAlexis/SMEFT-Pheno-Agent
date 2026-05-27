#!/usr/bin/env python3
"""
Run a MadGraph5 order file and check the return code.

Tries ./bin/mg5_aMC first, falls back to ./bin/mg5.
On failure, prints stdout/stderr and exits with error.

Usage:
    python run_mg5.py <mg5path> <order_filename>

Example:
    python run_mg5.py /opt/MG5_aMC_v3_5_6 order_p1_20260525_01.txt

Exit codes:
    0  success
    1  mg5_aMC not found
    2  MG5 failed (non-zero exit code)
"""
import subprocess
import sys
import os


def run_mg5(mg5path, order_filename):
    """Run MG5 with an order file, trying mg5_aMC then mg5.

    Args:
        mg5path: absolute path to MG5 installation
        order_filename: order file name (must exist under mg5path/)

    Returns:
        subprocess.CompletedProcess

    Raises:
        RuntimeError: if MG5 binary not found or execution fails
    """
    order_path = os.path.join(mg5path, order_filename)
    if not os.path.exists(order_path):
        raise RuntimeError(f"Order file not found: {order_path}")

    binaries = ["./bin/mg5_aMC", "./bin/mg5"]
    for binary in binaries:
        bin_path = os.path.join(mg5path, binary)
        if os.path.exists(bin_path):
            result = subprocess.run(
                [binary, order_filename],
                cwd=mg5path,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise RuntimeError(
                    f"MG5 failed with exit code {result.returncode}\n"
                    f"STDOUT:\n{result.stdout}\n"
                    f"STDERR:\n{result.stderr}"
                )
            return result

    raise RuntimeError(
        f"No MG5 binary found in {mg5path}/bin/ (tried mg5_aMC, mg5)"
    )


def main():
    if len(sys.argv) < 3:
        print(
            f"Usage: {sys.argv[0]} <mg5path> <order_filename>",
            file=sys.stderr
        )
        sys.exit(1)

    mg5path = sys.argv[1]
    order_filename = sys.argv[2]

    try:
        run_mg5(mg5path, order_filename)
        print("MG5 completed successfully")
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

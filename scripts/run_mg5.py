#!/usr/bin/env python3
"""
Run a MadGraph5 order file, check the return code, and track internal step timings.

Workflow agents should normally call run_mg5_config.py rather than hand-writing
order files. This lower-level helper documents the direct MG5 convention for
debugging and for maintaining the config runner:

1. Write the order file directly under the MG5 installation directory.
2. Invoke MG5 from that directory as `./bin/mg5_aMC order_file.txt`; if that
   binary is absent, fall back to `./bin/mg5 order_file.txt`.
3. A minimal process-creation order is:
      import model MODEL_NAME
      generate PROCESS [NP=0 | NP>0]
      output PROCESS_FOLDER
4. A launch order starts with `launch PROCESS_FOLDER`, then MG5 run-card and
   param-card settings, and ends with the final confirmation line `0`.

Tries ./bin/mg5_aMC first, falls back to ./bin/mg5.
Parses MG5 stdout in real time to detect stage boundaries:
  - MadGraph (event generation / parton level)
  - Pythia8  (parton shower)
  - Delphes  (detector simulation)

Usage:
    python run_mg5.py <mg5path> <order_filename>

Example:
    python run_mg5.py /opt/MG5_aMC_v3_5_6 order_file.txt

Exit codes:
    0  success
    1  mg5_aMC not found
    2  MG5 failed (non-zero exit code)
"""
import re
import subprocess
import sys
import os
import time

# MG5 stage markers (matched against stdout lines)
STAGE_MARKERS = {
    "pythia8": re.compile(r"Running\s+Pythia8?", re.IGNORECASE),
    "delphes": re.compile(r"Running\s+Delphes", re.IGNORECASE),
}


class MG5RunError(RuntimeError):
    """MG5 failed after producing a structured execution result."""

    def __init__(self, message, result):
        super().__init__(message)
        self.result = result


def run_mg5(mg5path, order_filename, timing_tracker=None):
    """Run MG5 with an order file, trying mg5_aMC then mg5.

    Args:
        mg5path: absolute path to MG5 installation
        order_filename: order file name (must exist under mg5path/)
        timing_tracker: optional TimingTracker instance from timing_tracker.py

    Returns:
        dict: {
            "stdout": str,
            "stderr": str,
            "returncode": int,
            "mg5_steps": {
                "madgraph": {"start": float, "end": float, "duration_sec": float},
                "pythia8":  {...} or None,
                "delphes":  {...} or None,
            }
        }

    Raises:
        RuntimeError: if MG5 binary not found or execution fails
    """
    order_path = os.path.join(mg5path, order_filename)
    if not os.path.exists(order_path):
        raise RuntimeError(f"Order file not found: {order_path}")

    binaries = ["./bin/mg5_aMC", "./bin/mg5"]
    binary = None
    for b in binaries:
        if os.path.exists(os.path.join(mg5path, b)):
            binary = b
            break

    if binary is None:
        raise RuntimeError(
            f"No MG5 binary found in {mg5path}/bin/ (tried mg5_aMC, mg5)"
        )

    # --- Real-time execution with stage parsing ---
    proc = subprocess.Popen(
        [binary, order_filename],
        cwd=mg5path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,  # line-buffered
    )

    stdout_lines = []
    stderr_lines = []

    # Timing state
    mg5_start = time.time()
    steps = {
        "madgraph": {"start": mg5_start, "end": None, "duration_sec": None},
        "pythia8": None,
        "delphes": None,
    }
    current_step = "madgraph"

    def _record_step_end(step_name, end_t):
        if steps[step_name] is not None and steps[step_name]["end"] is None:
            steps[step_name]["end"] = end_t
            steps[step_name]["duration_sec"] = round(end_t - steps[step_name]["start"], 2)

    def _parse_line(line, timestamp):
        nonlocal current_step
        # Check for stage transitions
        if STAGE_MARKERS["pythia8"].search(line):
            if current_step == "madgraph":
                _record_step_end("madgraph", timestamp)
            steps["pythia8"] = {"start": timestamp, "end": None, "duration_sec": None}
            current_step = "pythia8"
            return
        if STAGE_MARKERS["delphes"].search(line):
            if current_step == "madgraph":
                _record_step_end("madgraph", timestamp)
            elif current_step == "pythia8":
                _record_step_end("pythia8", timestamp)
            steps["delphes"] = {"start": timestamp, "end": None, "duration_sec": None}
            current_step = "delphes"
            return

    # Read stdout line-by-line
    try:
        for line in proc.stdout:
            now = time.time()
            stdout_lines.append(line)
            _parse_line(line, now)
            # Print progress indicator for long-running stages
            if current_step in ("madgraph", "pythia8", "delphes"):
                # Keep output visible but don't flood
                if any(k in line for k in ("Generating", "Storing", "Running", "progress", "%")):
                    print(line, end="", flush=True)
    except Exception as e:
        proc.kill()
        raise RuntimeError(f"Error reading MG5 stdout: {e}")

    # Read stderr
    try:
        for line in proc.stderr:
            stderr_lines.append(line)
    except Exception:
        pass

    returncode = proc.wait()
    end_t = time.time()

    # Finalize current step
    if current_step and steps[current_step] is not None:
        _record_step_end(current_step, end_t)

    stdout = "".join(stdout_lines)
    stderr = "".join(stderr_lines)

    # Record in timing tracker if provided
    if timing_tracker is not None:
        for step_name, rec in steps.items():
            if rec is not None and rec["duration_sec"] is not None:
                timing_tracker.record_mg5_step(
                    step_name, rec["start"], rec["end"]
                )

    result = {
        "stdout": stdout,
        "stderr": stderr,
        "returncode": returncode,
        "mg5_steps": steps,
    }

    if returncode != 0:
        raise MG5RunError(
            f"MG5 failed with exit code {returncode}\n"
            f"STDOUT (last 3000 chars):\n{stdout[-3000:]}\n"
            f"STDERR:\n{stderr}",
            result,
        )

    return result


def print_mg5_steps(steps):
    """Pretty-print MG5 step timings."""
    print("\n  MG5 Step Timings:")
    print("  " + "-" * 50)
    for name in ("madgraph", "pythia8", "delphes"):
        rec = steps.get(name)
        if rec is None or rec.get("duration_sec") is None:
            continue
        dur = rec["duration_sec"]
        if dur < 60:
            dur_str = f"{dur:.1f}s"
        elif dur < 3600:
            dur_str = f"{dur/60:.1f}m"
        else:
            dur_str = f"{dur/3600:.1f}h"
        print(f"    {name:<12} {dur_str:>10}")
    print("  " + "-" * 50)


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
        result = run_mg5(mg5path, order_filename)
        print("MG5 completed successfully")
        print_mg5_steps(result["mg5_steps"])
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

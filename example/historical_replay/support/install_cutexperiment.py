#!/usr/bin/env python3
"""Clone or validate CutExperiment for the SMEFT-ML workflow.

Usage:
    python install_cutexperiment.py <target_dir>

Exit codes:
    0  success
    1  git not found
    2  clone failed
    3  target exists but is not usable
    4  validation failed
"""

import argparse
import os
import shutil
import subprocess
import sys


REPO_URL = "https://gitee.com/NBAlexis/CutExperiment.git"
def _run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def validate_cutexperiment(path):
    """Return (ok, message) for a candidate CutExperiment directory."""
    if not os.path.isdir(path):
        return False, f"directory does not exist: {path}"

    candidate_files = []
    metadata_files = {"setup.py", "pyproject.toml", "README.md", "requirements.txt"}
    top_level = set(os.listdir(path))
    if metadata_files & top_level:
        return True, "ok"

    for root, _, files in os.walk(path):
        for name in files:
            if name.endswith(".py"):
                candidate_files.append(os.path.join(root, name))
        if candidate_files:
            break

    if not candidate_files:
        return False, "no Python files found; repository does not look usable"

    return True, "ok"


def main():
    parser = argparse.ArgumentParser(description="Clone or validate CutExperiment")
    parser.add_argument("target_dir", help="Directory where CutExperiment should live")
    parser.add_argument(
        "--repo",
        default=REPO_URL,
        help=f"Git repository URL (default: {REPO_URL})",
    )
    parser.add_argument(
        "--pull",
        action="store_true",
        help="If target exists and is a git repository, run git pull before validation",
    )
    args = parser.parse_args()

    target = os.path.abspath(os.path.expanduser(args.target_dir))
    parent = os.path.dirname(target)

    if os.path.exists(target):
        if not os.path.isdir(target):
            print(f"ERROR: target exists but is not a directory: {target}", file=sys.stderr)
            sys.exit(3)
        if os.path.isdir(os.path.join(target, ".git")) and args.pull:
            if shutil.which("git") is None:
                print("ERROR: git is required for --pull but was not found.", file=sys.stderr)
                sys.exit(1)
            result = _run(["git", "pull", "--ff-only"], cwd=target)
            if result.returncode != 0:
                print(f"ERROR: git pull failed:\n{result.stderr}", file=sys.stderr)
                sys.exit(3)
    else:
        if shutil.which("git") is None:
            print("ERROR: git is required to clone CutExperiment but was not found.", file=sys.stderr)
            sys.exit(1)
        os.makedirs(parent, exist_ok=True)
        result = _run(["git", "clone", args.repo, target])
        if result.returncode != 0:
            print(f"ERROR: git clone failed:\n{result.stderr}", file=sys.stderr)
            sys.exit(2)

    ok, message = validate_cutexperiment(target)
    if not ok:
        print(f"ERROR: CutExperiment validation failed: {message}", file=sys.stderr)
        sys.exit(4)

    print(f"CutExperiment path: {target}")


if __name__ == "__main__":
    main()

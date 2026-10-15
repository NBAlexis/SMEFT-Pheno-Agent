#!/usr/bin/env python3
"""
Convert Delphes ROOT output to LHCO format, auto-detecting the jet branch.

Detects which jet branch exists in the ROOT file (Jet, GenJet, FatJet) and
invokes root2lhco with the correct flags. Validates the output.

Usage:
    python convert_root_to_lhco.py <mg5path> <process_folder> <run_folder>

Example:
    python convert_root_to_lhco.py /opt/MG5_aMC_v3_5_6 \
        ep_em_to_a_jj_p6_20260525_01 run_01

The script reads the delphes_card.dat to determine the jet branch name,
then runs root2lhco and validates the output LHCO file.

Exit codes:
    0  success
    1  input file not found
    2  root2lhco failed
    3  LHCO output invalid (empty or too small)
    4  root2lhco log shows errors
"""
import re
import subprocess
import sys
import os


def detect_jet_branch(delphes_card_path):
    """Detect jet branch name from Delphes card.

    Returns:
        str or None: 'Jet', 'GenJet', 'FatJet', or None if not found
    """
    branch_pattern = re.compile(
        r"add\s+Branch\s+\S+/jets\s+(\S+)\s+Jet"
    )

    branches = []
    with open(delphes_card_path) as f:
        for line in f:
            m = branch_pattern.search(line)
            if m:
                branches.append(m.group(1))

    if "Jet" in branches:
        return "Jet"
    if "GenJet" in branches:
        return "GenJet"
    if "FatJet" in branches:
        return "FatJet"
    return None


def convert_root_to_lhco(mg5path, process_folder, run_folder):
    """Convert ROOT to LHCO with auto jet-branch detection.

    Args:
        mg5path: absolute path to MG5 installation
        process_folder: process directory name
        run_folder: run_XX folder name

    Returns:
        str: path to the generated .lhco file

    Raises:
        RuntimeError: on any failure
    """
    root_file = os.path.join(
        mg5path, process_folder, "Events", run_folder,
        "tag_1_delphes_events.root"
    )
    lhco_file = os.path.join(
        mg5path, process_folder, "Events", run_folder,
        f"{run_folder}.lhco"
    )
    log_file = os.path.join(
        mg5path, process_folder, "Events", run_folder, "root2lhco.log"
    )
    delphes_card = os.path.join(
        mg5path, process_folder, "Cards", "delphes_card.dat"
    )

    # Reuse an already-converted LHCO when the ROOT has been removed: a
    # storage watcher or an interrupted postprocess may have converted this
    # run earlier. The downstream count helper fully validates the LHCO.
    if (not os.path.exists(root_file) and os.path.exists(log_file)
            and os.path.exists(lhco_file) and os.path.getsize(lhco_file) > 0):
        return lhco_file

    if not os.path.exists(root_file):
        raise RuntimeError(f"ROOT file not found: {root_file}")
    if not os.path.exists(delphes_card):
        raise RuntimeError(
            f"Delphes card not found: {delphes_card}\nROOT input: {root_file}"
        )

    jet_branch = detect_jet_branch(delphes_card)

    # CRITICAL: root2lhco uses argv[1] as input file AFTER scanning argv[2+]
    # for --jet-branch. So --jet-branch MUST come last.
    cmd = ["./root2lhco",
        f"../{process_folder}/Events/{run_folder}/tag_1_delphes_events.root",
        f"../{process_folder}/Events/{run_folder}/{run_folder}.lhco"
    ]
    if jet_branch and jet_branch != "Jet":
        cmd.append(f"--jet-branch={jet_branch}")

    # Run root2lhco from Delphes directory
    delphes_dir = os.path.join(mg5path, "Delphes")
    log_path = os.path.join(
        mg5path, process_folder, "Events", run_folder, "root2lhco.log"
    )

    def diagnostic_context(log_content="", return_code=None):
        command = " ".join(cmd)
        details = (
            f"ROOT input: {root_file}\n"
            f"Delphes card: {delphes_card}\n"
            f"Detected jet branch: {jet_branch or 'default Jet'}\n"
            f"Command: {command}\n"
            f"Return code: {return_code if return_code is not None else 'not available'}\n"
            f"Log: {log_path}"
        )
        if log_content:
            details += f"\nLog excerpt:\n{log_content[:2000]}"
        return details

    with open(log_path, "w") as log_f:
        result = subprocess.run(
            cmd,
            cwd=delphes_dir,
            stdout=log_f,
            stderr=subprocess.STDOUT,
            text=True
        )

    # Check return code
    if result.returncode != 0:
        with open(log_path) as f:
            log_content = f.read()
        raise RuntimeError(
            f"root2lhco failed (exit {result.returncode}).\n"
            f"{diagnostic_context(log_content, result.returncode)}"
        )

    # Validate LHCO output
    if not os.path.exists(lhco_file):
        raise RuntimeError(
            f"root2lhco ran but LHCO file not created: {lhco_file}\n"
            f"{diagnostic_context(return_code=result.returncode)}"
        )

    lhco_size = os.path.getsize(lhco_file)
    root_size = os.path.getsize(root_file)

    if lhco_size == 0:
        raise RuntimeError(
            f"LHCO file is empty: {lhco_file}\n"
            f"{diagnostic_context(return_code=result.returncode)}"
        )

    # Check LHCO has actual event data (not just header)
    with open(lhco_file) as f:
        lines = f.readlines()
    if len(lines) <= 1:
        with open(log_path) as f:
            log_content = f.read()
        raise RuntimeError(
            f"LHCO file has no events (only {len(lines)} line(s)).\n"
            f"{diagnostic_context(log_content, result.returncode)}"
        )

    # Check root2lhco log for errors
    with open(log_path) as f:
        log_content = f.read()
    if "contains 0 events" in log_content or "Error" in log_content or "Cannot find tree" in log_content:
        raise RuntimeError(
            f"root2lhco log indicates failure.\n{diagnostic_context(log_content, result.returncode)}"
        )

    # If LHCO is tiny but ROOT is large, root2lhco failed silently
    if lhco_size < 1024 and root_size > 1024 * 1024:
        raise RuntimeError(
            f"LHCO file suspiciously small ({lhco_size} B) while ROOT is large "
            f"({root_size / 1024 / 1024:.1f} MB). root2lhco likely failed.\n"
            f"{diagnostic_context(log_content, result.returncode)}"
        )

    return lhco_file


def main():
    if len(sys.argv) < 4:
        print(
            f"Usage: {sys.argv[0]} <mg5path> <process_folder> <run_folder>",
            file=sys.stderr
        )
        sys.exit(1)

    mg5path = sys.argv[1]
    process_folder = sys.argv[2]
    run_folder = sys.argv[3]

    try:
        lhco_path = convert_root_to_lhco(mg5path, process_folder, run_folder)
        print(f"LHCO created: {lhco_path}")
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()

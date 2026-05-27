#!/usr/bin/env python3
"""
Copy a Delphes detector card and all its dependencies into an MG5 process directory.

Resolves source/include statements in the .tcl card to locate dependency folders
under {mg5path}/Delphes/cards/ and copies them alongside the card.

Usage:
    python setup_delphes_card.py <mg5path> <delphes_card_name> <process_folder>

Example:
    python setup_delphes_card.py /opt/MG5_aMC_v3_5_6 delphes_card_CEPC.tcl \
        ep_em_to_a_jj_p1_20260525_01_NP

Exit codes:
    0  success
    1  card not found
    2  process folder not found
"""
import re
import shutil
import sys
import os


def setup_delphes_card(mg5path, delphes_card, process_folder):
    """Copy Delphes card and dependencies into process directory.

    Args:
        mg5path: absolute path to MG5 installation
        delphes_card: .tcl card filename (e.g., delphes_card_CEPC.tcl)
        process_folder: process directory name under mg5path

    Returns:
        str: path to the copied card
    """
    src_card = os.path.join(mg5path, "Delphes", "cards", delphes_card)
    if not os.path.exists(src_card):
        raise FileNotFoundError(f"Delphes card not found: {src_card}")

    proc_dir = os.path.join(mg5path, process_folder)
    cards_dir = os.path.join(proc_dir, "Cards")
    os.makedirs(cards_dir, exist_ok=True)

    dst_card = os.path.join(cards_dir, "delphes_card.dat")
    shutil.copy2(src_card, dst_card)

    # Resolve dependencies
    dep_pattern = re.compile(r"(?:source|include)\s+(\S+)")
    cards_root = os.path.join(mg5path, "Delphes", "cards")
    copied_deps = set()

    with open(src_card) as f:
        for line in f:
            m = dep_pattern.search(line)
            if m:
                dep_path = m.group(1)
                # Dependency may be relative to cards/ directory
                dep_full = os.path.normpath(os.path.join(cards_root, dep_path))
                if os.path.exists(dep_full):
                    # Preserve relative directory structure under Cards/
                    rel_path = os.path.relpath(dep_full, cards_root)
                    dst_dep = os.path.join(cards_dir, rel_path)
                    if dep_full not in copied_deps:
                        os.makedirs(os.path.dirname(dst_dep), exist_ok=True)
                        if os.path.isdir(dep_full):
                            if os.path.exists(dst_dep):
                                shutil.rmtree(dst_dep)
                            shutil.copytree(dep_full, dst_dep)
                        else:
                            shutil.copy2(dep_full, dst_dep)
                        copied_deps.add(dep_full)

    return dst_card


def main():
    if len(sys.argv) < 4:
        print(
            f"Usage: {sys.argv[0]} <mg5path> <delphes_card_name> <process_folder>",
            file=sys.stderr
        )
        sys.exit(1)

    mg5path = sys.argv[1]
    delphes_card = sys.argv[2]
    process_folder = sys.argv[3]

    if not os.path.exists(os.path.join(mg5path, process_folder)):
        print(
            f"Error: process folder not found: {os.path.join(mg5path, process_folder)}",
            file=sys.stderr
        )
        sys.exit(2)

    try:
        dst = setup_delphes_card(mg5path, delphes_card, process_folder)
        print(f"Copied to: {dst}")
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

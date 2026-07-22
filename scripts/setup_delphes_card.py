#!/usr/bin/env python3
"""
Copy a Delphes detector card and all its dependencies into an MG5 process directory.

Recursively resolves source/include statements in the .tcl card and all nested
 dependency files to locate dependency folders under {mg5path}/Delphes/cards/
 and copies them alongside the card.

Usage:
    python setup_delphes_card.py <mg5path> <delphes_card_name> <process_folder>

Example:
    python setup_delphes_card.py /opt/MG5_aMC_v3_5_6 delphes_card_CEPC.tcl \
        ep_em_to_a_jj_p3_20260525_01_NP

Exit codes:
    0  success
    1  card not found
    2  process folder not found
"""
import re
import shutil
import sys
import os


def _is_within(path, root):
    return os.path.commonpath([os.path.abspath(path), os.path.abspath(root)]) == os.path.abspath(root)


def collect_dependencies(tcl_file, cards_root, collected, missing=None):
    """Recursively collect all source/include dependencies of a .tcl file.

    Args:
        tcl_file: absolute path to the .tcl file to scan
        cards_root: absolute path to the Delphes cards/ root directory
        collected: set of absolute paths already collected (modified in-place)
        missing: list receiving unresolved dependency records

    Returns:
        set: updated collected paths
    """
    if missing is None:
        missing = []
    cards_root = os.path.realpath(cards_root)

    dep_pattern = re.compile(
        r"^\s*(?:source|include)\s+(?:\"([^\"]+)\"|'([^']+)'|\{([^}]+)\}|(\S+))"
    )

    if not os.path.exists(tcl_file):
        return collected

    # Resolve to canonical path to avoid double-processing symlinks
    tcl_file = os.path.realpath(tcl_file)

    if tcl_file in collected:
        return collected
    collected.add(tcl_file)

    with open(tcl_file) as f:
        for line in f:
            m = dep_pattern.search(line)
            if m:
                dep_path = next(group for group in m.groups() if group)
                # Dependency paths in Delphes cards are relative to cards_root
                dep_full = os.path.normpath(os.path.join(cards_root, dep_path))
                alt_full = os.path.normpath(
                    os.path.join(os.path.dirname(tcl_file), dep_path)
                )
                candidates = [path for path in (dep_full, alt_full) if _is_within(path, cards_root)]
                existing = next((path for path in candidates if os.path.exists(path)), None)
                if existing:
                    dep_full = existing
                    if dep_full not in collected:
                        if os.path.isdir(dep_full):
                            collected.add(dep_full)
                        else:
                            # Recursively scan .tcl files for nested dependencies
                            collect_dependencies(dep_full, cards_root, collected, missing)
                else:
                    missing.append({
                        "referenced_from": tcl_file,
                        "dependency": dep_path,
                        "cards_root_path": dep_full,
                        "referencing_file_path": alt_full,
                        "outside_cards_root": not candidates,
                    })

    return collected


def _sanitize_execution_path(card_path):
    """Remove comment lines inside Tcl { } blocks in ExecutionPath.

    Delphes cards sometimes contain commented-out modules inside
    `set ExecutionPath { ... }` using `# ModuleName`. In Tcl brace
    quoting, `#` is literal text, not a comment, so Delphes tries to
    load a module named `#` and fails.
    """
    with open(card_path) as f:
        lines = f.readlines()

    in_execution_path = False
    fixed = []
    removed = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("set ExecutionPath"):
            in_execution_path = True
        if in_execution_path and stripped == "}":
            in_execution_path = False
        if in_execution_path and stripped.startswith("#"):
            removed += 1
            continue
        fixed.append(line)

    if removed:
        with open(card_path, "w") as f:
            f.writelines(fixed)


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

    # Sanitize ExecutionPath: remove comment lines inside { } blocks
    # Tcl treats '#' as literal text inside braces, causing Delphes to
    # error with "module '#' is specified in ExecutionPath but not configured"
    _sanitize_execution_path(dst_card)

    # Recursively resolve all dependencies
    cards_root = os.path.realpath(os.path.join(mg5path, "Delphes", "cards"))
    copied_deps = set()

    missing = []
    deps = collect_dependencies(src_card, cards_root, set(), missing)
    if missing:
        details = "\n".join(
            f"- {item['referenced_from']}: {item['dependency']!r}; tried "
            f"{item['cards_root_path']} and {item['referencing_file_path']}"
            + ("; dependency resolves outside Delphes/cards" if item["outside_cards_root"] else "")
            for item in missing
        )
        raise FileNotFoundError(
            "Unresolved Delphes card dependencies:\n" + details
        )
    # Don't copy the card itself (already copied as delphes_card.dat)
    deps.discard(os.path.realpath(src_card))

    for dep_full in deps:
        rel_path = os.path.relpath(dep_full, cards_root)
        dst_dep = os.path.join(cards_dir, rel_path)
        if not _is_within(dst_dep, cards_dir):
            raise RuntimeError(
                f"Delphes dependency resolves outside the cards tree: {dep_full} "
                f"relative to {cards_root}"
            )
        if dep_full not in copied_deps:
            os.makedirs(os.path.dirname(dst_dep), exist_ok=True)
            if os.path.isdir(dep_full):
                if os.path.exists(dst_dep):
                    shutil.rmtree(dst_dep)
                shutil.copytree(dep_full, dst_dep)
            else:
                shutil.copy2(dep_full, dst_dep)
            copied_deps.add(dep_full)

    missing_copies = []
    for dep_full in sorted(copied_deps):
        rel_path = os.path.relpath(dep_full, cards_root)
        dst_dep = os.path.join(cards_dir, rel_path)
        if not os.path.exists(dst_dep):
            missing_copies.append(f"{dep_full} -> {dst_dep}")
    if missing_copies:
        raise RuntimeError(
            "Delphes dependencies were resolved but not copied:\n- "
            + "\n- ".join(missing_copies)
        )

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
    except (FileNotFoundError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

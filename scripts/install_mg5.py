#!/usr/bin/env python3
"""
Automatically install MadGraph5_aMC@NLO with Pythia8, LHAPDF6, and Delphes.

The download URL and extracted directory name must be provided by the caller
(typically the LLM/skill after parsing https://launchpad.net/mg5amcnlo).
This script does NOT scrape launchpad — it only handles download, extraction,
compilation, verification, and environment setup.

Usage:
    python install_mg5.py <install_dir> --url <download_url> --name <extracted_dir_name>

Arguments:
    install_dir        Directory where MG5 will be extracted (created if missing)
    --url              Direct download URL for the MG5 tarball
    --name             Name of the top-level directory inside the tarball
                       (e.g. MG5_aMC_v3_5_15)

Exit codes:
    0  success
    1  missing system dependency
    2  download failed
    3  MG5 install command failed
    4  verification failed

Example:
    python install_mg5.py ~/MG5_aMC \
        --url "https://launchpad.net/mg5amcnlo/3.0/3.7.x/+download/LTS_MG5aMC_v3.5.15.tgz" \
        --name MG5_aMC_v3_5_15
    # Result: ~/MG5_aMC/MG5_aMC_v3_5_15/
"""
import argparse
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile


SYSTEM_DEPS = [
    ("gcc", "build-essential"),
    ("gfortran", "gfortran"),
    ("python3", "python3"),
    ("curl", "curl"),
]


def check_system_deps():
    """Check that required system binaries are available."""
    missing = []
    for binary, apt_name in SYSTEM_DEPS:
        if shutil.which(binary) is None:
            missing.append((binary, apt_name))

    # Check libboost separately (no single binary)
    boost_ok = False
    for check_cmd in [
        "dpkg -l | grep -q libboost-all-dev",
        "ldconfig -p | grep -q libboost",
    ]:
        result = subprocess.run(check_cmd, shell=True, capture_output=True)
        if result.returncode == 0:
            boost_ok = True
            break
    if not boost_ok:
        missing.append(("libboost", "libboost-all-dev"))

    if missing:
        print("ERROR: Missing system dependencies:", file=sys.stderr)
        for binary, apt_name in missing:
            print(f"  - {binary} (install: sudo apt-get install {apt_name})", file=sys.stderr)
        print("\nRun the following and retry:", file=sys.stderr)
        pkgs = " ".join(sorted(set(apt for _, apt in missing)))
        print(f"  sudo apt-get update && sudo apt-get install -y {pkgs}", file=sys.stderr)
        sys.exit(1)


def download_mg5(url, dest_path):
    """Download MG5 tarball, following redirects."""
    print(f"Downloading MG5 from {url} ...")
    result = subprocess.run(
        ["curl", "-L", "-o", dest_path, url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: Download failed:\n{result.stderr}", file=sys.stderr)
        sys.exit(2)

    size_mb = os.path.getsize(dest_path) / (1024 * 1024)
    print(f"Downloaded: {dest_path} ({size_mb:.1f} MB)")


def extract_mg5(tar_path, extract_dir):
    """Extract tarball to target directory."""
    print(f"Extracting to {extract_dir} ...")
    os.makedirs(extract_dir, exist_ok=True)
    with tarfile.open(tar_path, "r:gz") as tar:
        tar.extractall(path=extract_dir)


def run_mg5_install(mg5path, command):
    """Run a single MG5 install command."""
    order_file = os.path.join(mg5path, "install_order.txt")
    with open(order_file, "w") as f:
        f.write(f"{command}\n")

    print(f"Running: {command} (this may take 5-20 minutes) ...")
    result = subprocess.run(
        ["./bin/mg5_aMC", "install_order.txt"],
        cwd=mg5path,
        capture_output=True,
        text=True,
    )

    log_file = os.path.join(mg5path, f"install_{command.replace(' ', '_')}.log")
    with open(log_file, "w") as f:
        f.write(result.stdout)
        f.write(result.stderr)

    if result.returncode != 0:
        print(f"ERROR: '{command}' failed with exit code {result.returncode}", file=sys.stderr)
        print(f"Log saved to: {log_file}", file=sys.stderr)
        print(f"STDERR:\n{result.stderr[:2000]}", file=sys.stderr)
        sys.exit(3)

    print(f"  {command} completed successfully.")


def verify_installation(mg5path):
    """Verify all required components exist."""
    checks = [
        ("MG5 binary", os.path.join(mg5path, "bin", "mg5_aMC")),
        ("Pythia8", os.path.join(mg5path, "HEPTools", "pythia8", "lib", "libpythia8.so")),
        ("LHAPDF6", os.path.join(mg5path, "HEPTools", "lhapdf6_py3", "bin", "lhapdf-config")),
        ("Delphes cards", os.path.join(mg5path, "Delphes", "cards", "delphes_card_default.dat")),
    ]

    missing = []
    for name, path in checks:
        if not os.path.exists(path):
            missing.append((name, path))

    if missing:
        print("ERROR: Verification failed — components missing after install:", file=sys.stderr)
        for name, path in missing:
            print(f"  - {name}: {path}", file=sys.stderr)
        sys.exit(4)

    print("All components verified.")


def print_env_info(mg5path):
    """Print current environment variables and recommended export commands.

    The script does NOT modify any environment variable — neither the current
    Python process (os.environ) nor ~/.bashrc. The LLM/skill inspects the
    output and decides what action to take.
    """
    bin_dir = os.path.join(mg5path, "HEPTools", "bin")
    lib_dir = os.path.join(mg5path, "HEPTools", "lib")

    current_path = os.environ.get("PATH", "")
    current_ld = os.environ.get("LD_LIBRARY_PATH", "")

    print("\n--- Environment Report (script did NOT modify anything) ---")
    print(f"Current PATH:\n  {current_path}")
    print(f"Current LD_LIBRARY_PATH:\n  {current_ld}")
    print(f"\nRecommended additions (if not already present):")
    print(f'  export PATH="{bin_dir}:$PATH"  # MG5_auto_install_PATH')
    print(f'  export LD_LIBRARY_PATH="{lib_dir}:$LD_LIBRARY_PATH"  # MG5_auto_install_LD_LIBRARY_PATH')
    print("\nThe LLM/skill should inspect the current values and decide:")
    print("  1. Whether to set them for the current session")
    print("  2. Whether to append them to ~/.bashrc for persistence")
    print("-----------------------------------------------------------")


def main():
    parser = argparse.ArgumentParser(description="Install MG5 with Pythia8, LHAPDF6, and Delphes")
    parser.add_argument("install_dir", help="Directory where MG5 will be extracted")
    parser.add_argument("--url", required=True, help="Direct download URL for the MG5 tarball")
    parser.add_argument("--name", required=True,
                        help="Name of the top-level directory inside the tarball (e.g. MG5_aMC_v3_5_15)")
    args = parser.parse_args()

    install_dir = os.path.abspath(args.install_dir)
    url = args.url
    extracted_name = args.name
    mg5path = os.path.join(install_dir, extracted_name)

    # 1. Check system deps
    check_system_deps()

    # 2. Skip if already installed
    if os.path.exists(os.path.join(mg5path, "bin", "mg5_aMC")):
        print(f"MG5 already exists at {mg5path}")
        verify_installation(mg5path)
        print_env_info(mg5path)
        print(f"\nMadGraph5 path: {mg5path}")
        return

    # 3. Download
    with tempfile.TemporaryDirectory() as tmpdir:
        tar_path = os.path.join(tmpdir, "mg5.tar.gz")
        download_mg5(url, tar_path)

        # 4. Extract
        extract_mg5(tar_path, install_dir)

    # 5. Install MG5 internal dependencies
    for cmd in ["install pythia8", "install lhapdf6", "install delphes"]:
        run_mg5_install(mg5path, cmd)

    # 6. Verify
    verify_installation(mg5path)

    # 7. Print environment info for LLM inspection (script does NOT modify anything)
    print_env_info(mg5path)

    print(f"\nInstallation complete.")
    print(f"MadGraph5 path: {mg5path}")


if __name__ == "__main__":
    main()

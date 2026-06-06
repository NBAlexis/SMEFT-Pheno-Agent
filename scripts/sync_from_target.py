#!/usr/bin/env python3
"""Copy workflow files or directories from the execution target to local disk.

Use this when the selected MG5 target lacks a local tool, for example when
LaTeX is unavailable inside WSL2/SSH but available in the agent's local control
environment for Phase 10 manuscript compilation.
"""

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path
from typing import Optional

from remote_exec import _load_execution


def run_checked(args, *, stdout=None) -> None:
    proc = subprocess.run(args, stdout=stdout, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed with exit code {proc.returncode}: {args}")


def extract_tar_to_local(stream, source_name: str, destination: Path) -> None:
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(fileobj=stream, mode="r|*") as tar:
        tar.extractall(destination.parent)
    extracted = destination.parent / source_name
    if extracted != destination:
        if destination.exists():
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()
        extracted.replace(destination)


def copy_local(source: str, destination: Path) -> None:
    source_path = Path(source).expanduser().resolve()
    destination = destination.expanduser().resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if source_path.is_dir():
        shutil.copytree(source_path, destination, dirs_exist_ok=True)
    else:
        shutil.copy2(source_path, destination)


def tar_command(source: str) -> tuple[str, str]:
    if not source.startswith("/"):
        raise ValueError(f"source path must be absolute on the execution target: {source}")
    clean = source.rstrip("/")
    parent = os.path.dirname(clean) or "/"
    name = os.path.basename(clean)
    command = (
        f"test -e {shlex.quote(clean)} && "
        f"tar -C {shlex.quote(parent)} -cf - {shlex.quote(name)}"
    )
    return command, name


def ssh_args(target: str, port: Optional[int], command: str) -> list:
    if not target:
        raise ValueError("execution.ssh_target is required for ssh sync")
    args = ["ssh"]
    if port:
        args.extend(["-p", str(port)])
    args.extend([target, command])
    return args


def copy_ssh(source: str, destination: Path, target: str, port: Optional[int]) -> None:
    command, name = tar_command(source)
    args = ssh_args(target, port, command)
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    try:
        if proc.stdout is None:
            raise RuntimeError("failed to capture ssh stdout")
        extract_tar_to_local(proc.stdout, name, destination)
    finally:
        rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"ssh tar command failed with exit code {rc}")


def copy_wsl(source: str, destination: Path, distro: Optional[str]) -> None:
    wsl = shutil.which("wsl.exe") or shutil.which("wsl")
    if not wsl:
        raise RuntimeError("wsl.exe was not found; WSL2 sync is unavailable")
    command, name = tar_command(source)
    args = [wsl]
    if distro:
        args.extend(["-d", distro])
    args.extend(["--", "bash", "-lc", command])
    proc = subprocess.Popen(args, stdout=subprocess.PIPE)
    try:
        if proc.stdout is None:
            raise RuntimeError("failed to capture WSL stdout")
        extract_tar_to_local(proc.stdout, name, destination)
    finally:
        rc = proc.wait()
    if rc != 0:
        raise RuntimeError(f"WSL tar command failed with exit code {rc}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync a target file/directory to local disk")
    parser.add_argument("--config", required=True, help="Local control run_config.json")
    parser.add_argument("source", help="Absolute source path on the selected execution target")
    parser.add_argument("destination", help="Local destination path")
    args = parser.parse_args()

    execution = _load_execution(args.config)
    mode = execution.get("mode", "local")
    destination = Path(args.destination)

    if mode == "local":
        if os.name == "nt":
            raise RuntimeError("Native Windows execution is invalid for this workflow; use execution.mode=wsl2 or ssh")
        copy_local(args.source, destination)
    elif mode == "ssh":
        copy_ssh(args.source, destination, execution.get("ssh_target"), execution.get("ssh_port"))
    elif mode == "wsl2":
        copy_wsl(args.source, destination, execution.get("wsl_distro"))
    else:
        raise ValueError(f"Unsupported execution mode: {mode!r}")

    print(f"Synced {args.source} -> {destination.resolve()} ({mode})")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

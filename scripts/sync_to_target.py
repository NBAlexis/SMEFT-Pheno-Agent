#!/usr/bin/env python3
"""Copy local workflow files or directories to the configured execution target.

Use this for deterministic transfers that an agent would otherwise improvise,
such as copying the local control run_config.json to an SSH/WSL2 workdir or
copying a bundled UFO model into the target MadGraph models directory.
"""

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Optional

from remote_exec import _load_execution


def run_checked(args, *, stdin=None) -> None:
    proc = subprocess.run(args, stdin=stdin, check=False)
    if proc.returncode != 0:
        raise RuntimeError(f"command failed with exit code {proc.returncode}: {args}")


def make_tar(source: Path) -> Path:
    tmp = tempfile.NamedTemporaryFile(prefix="smeft_sync_", suffix=".tar", delete=False)
    tmp.close()
    tar_path = Path(tmp.name)
    with tarfile.open(tar_path, "w") as tar:
        tar.add(source, arcname=source.name)
    return tar_path


def ensure_abs_target(target: str) -> None:
    if not target.startswith("/"):
        raise ValueError(f"target path must be absolute on the execution target: {target}")


def copy_local(source: Path, target: str) -> None:
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    if source.is_dir():
        shutil.copytree(source, target_path, dirs_exist_ok=True)
    else:
        shutil.copy2(source, target_path)


def ssh_base_args(target: str, port: Optional[int]) -> list:
    if not target:
        raise ValueError("execution.ssh_target is required for ssh sync")
    args = ["ssh"]
    if port:
        args.extend(["-p", str(port)])
    args.append(target)
    return args


def extract_tar_command(target_path: str, source_name: str) -> str:
    parent = os.path.dirname(target_path.rstrip("/")) or "/"
    final_name = os.path.basename(target_path.rstrip("/"))
    quoted_parent = shlex.quote(parent)
    quoted_source = shlex.quote(source_name)
    quoted_final = shlex.quote(final_name)
    command = f"mkdir -p {quoted_parent} && tar -xf - -C {quoted_parent}"
    if final_name != source_name:
        command += f" && mv -T {quoted_parent}/{quoted_source} {quoted_parent}/{quoted_final}"
    return command


def copy_ssh(source: Path, target_path: str, ssh_target: str, port: Optional[int]) -> None:
    ensure_abs_target(target_path)
    tar_path = make_tar(source)
    try:
        command = extract_tar_command(target_path, source.name)
        args = ssh_base_args(ssh_target, port)
        args.append(command)
        with open(tar_path, "rb") as f:
            run_checked(args, stdin=f)
    finally:
        tar_path.unlink(missing_ok=True)


def copy_wsl(source: Path, target_path: str, distro: Optional[str]) -> None:
    ensure_abs_target(target_path)
    wsl = shutil.which("wsl.exe") or shutil.which("wsl")
    if not wsl:
        raise RuntimeError("wsl.exe was not found; WSL2 sync is unavailable")
    tar_path = make_tar(source)
    try:
        command = extract_tar_command(target_path, source.name)
        args = [wsl]
        if distro:
            args.extend(["-d", distro])
        args.extend(["--", "bash", "-lc", command])
        with open(tar_path, "rb") as f:
            run_checked(args, stdin=f)
    finally:
        tar_path.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync a local file/directory to the workflow execution target")
    parser.add_argument("--config", required=True, help="Local control run_config.json")
    parser.add_argument("source", help="Local source file or directory")
    parser.add_argument("target", help="Absolute destination path on the selected execution target")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    if not source.exists():
        raise FileNotFoundError(source)

    execution = _load_execution(args.config)
    mode = execution.get("mode", "local")
    if mode == "local":
        if os.name == "nt":
            raise RuntimeError("Native Windows execution is invalid for this workflow; use execution.mode=wsl2 or ssh")
        copy_local(source, args.target)
    elif mode == "ssh":
        copy_ssh(source, args.target, execution.get("ssh_target"), execution.get("ssh_port"))
    elif mode == "wsl2":
        copy_wsl(source, args.target, execution.get("wsl_distro"))
    else:
        raise ValueError(f"Unsupported execution mode: {mode!r}")

    print(f"Synced {source} -> {args.target} ({mode})")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

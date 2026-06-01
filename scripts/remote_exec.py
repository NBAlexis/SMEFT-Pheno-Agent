#!/usr/bin/env python3
"""Run workflow commands locally, over SSH, or inside WSL2.

The SMEFT workflow treats command execution as a target property, not as an
ad-hoc command prefix. Use this helper whenever `run_config.json` contains an
`execution` block with mode `ssh` or `wsl2`.
"""

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional


VALID_MODES = {"local", "ssh", "wsl2"}


def _load_execution(config_path: Optional[str]) -> Dict[str, Any]:
    if not config_path:
        return {"mode": "local"}
    with open(config_path, encoding="utf-8-sig") as f:
        data = json.load(f)
    execution = data.get("execution") or {"mode": "local"}
    if execution.get("mode") not in VALID_MODES:
        raise ValueError(f"Unsupported execution mode: {execution.get('mode')!r}")
    return execution


def _shell_join(command: List[str]) -> str:
    if len(command) == 1:
        return command[0]
    return " ".join(shlex.quote(part) for part in command)


def _with_cwd(command: str, cwd: Optional[str]) -> str:
    if not cwd:
        return command
    return f"cd {shlex.quote(cwd)} && {command}"


def run_local(command_parts: List[str], cwd: Optional[str]) -> int:
    if len(command_parts) == 1:
        return subprocess.run(command_parts[0], cwd=cwd, shell=True).returncode
    return subprocess.run(command_parts, cwd=cwd).returncode


def run_ssh(target: str, port: Optional[int], command: str, cwd: Optional[str]) -> int:
    if not target:
        raise ValueError("execution.ssh_target is required for ssh mode")
    remote_command = _with_cwd(command, cwd)
    args = ["ssh"]
    if port:
        args.extend(["-p", str(port)])
    args.extend([target, remote_command])
    return subprocess.run(args).returncode


def run_wsl(distro: Optional[str], command: str, cwd: Optional[str]) -> int:
    wsl = shutil.which("wsl.exe") or shutil.which("wsl")
    if not wsl:
        raise RuntimeError("wsl.exe was not found; WSL2 execution is unavailable")
    wsl_command = _with_cwd(command, cwd)
    args = [wsl]
    if distro:
        args.extend(["-d", distro])
    args.extend(["--", "bash", "-lc", wsl_command])
    return subprocess.run(args).returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a command on a workflow execution target")
    parser.add_argument("--config", help="Path to run_config.json")
    parser.add_argument("--mode", choices=sorted(VALID_MODES), help="Override execution mode")
    parser.add_argument("--ssh-target", help="Override SSH target, e.g. user@server")
    parser.add_argument("--ssh-port", type=int, help="Override SSH port")
    parser.add_argument("--wsl-distro", help="Override WSL distro name")
    parser.add_argument("--cwd", help="Working directory on the selected target")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command after --")
    args = parser.parse_args()

    command_parts = args.command
    if command_parts and command_parts[0] == "--":
        command_parts = command_parts[1:]
    if not command_parts:
        parser.error("command is required; pass it after --")

    execution = _load_execution(args.config)
    mode = args.mode or execution.get("mode", "local")
    if mode == "local":
        return run_local(command_parts, args.cwd)
    command = _shell_join(command_parts)
    if mode == "ssh":
        target = args.ssh_target or execution.get("ssh_target")
        port = args.ssh_port if args.ssh_port is not None else execution.get("ssh_port")
        return run_ssh(target, port, command, args.cwd)
    if mode == "wsl2":
        distro = args.wsl_distro or execution.get("wsl_distro")
        return run_wsl(distro, command, args.cwd)
    raise ValueError(f"Unsupported execution mode: {mode!r}")


if __name__ == "__main__":
    sys.exit(main())

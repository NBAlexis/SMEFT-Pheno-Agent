#!/usr/bin/env python3
"""Start and inspect durable long-running workflow commands.

This helper prevents agents from treating the current interactive session as a
runtime limit. It records PID/status/log files under a job directory and uses
the same local/SSH/WSL2 target model as remote_exec.py.
"""

import argparse
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from typing import List, Optional

from remote_exec import _load_execution, _shell_join, run_ssh, run_wsl


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def safe_name(name: str) -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in name)
    if not cleaned:
        raise ValueError("job name must contain at least one safe character")
    return cleaned


def job_paths(job_dir: str, name: str) -> dict:
    name = safe_name(name)
    return {
        "dir": job_dir,
        "pid": os.path.join(job_dir, f"{name}.pid"),
        "meta": os.path.join(job_dir, f"{name}.json"),
        "stdout": os.path.join(job_dir, f"{name}.out.log"),
        "stderr": os.path.join(job_dir, f"{name}.err.log"),
        "exitcode": os.path.join(job_dir, f"{name}.exitcode"),
        "started": os.path.join(job_dir, f"{name}.started_at"),
        "finished": os.path.join(job_dir, f"{name}.finished_at"),
        "script": os.path.join(job_dir, f"{name}.sh"),
        "runner": os.path.join(job_dir, f"{name}_runner.py"),
    }


def read_pid(pid_path: str) -> Optional[int]:
    try:
        with open(pid_path, encoding="utf-8") as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return None


def local_running(pid: int) -> bool:
    try:
        if os.name == "nt":
            result = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True,
                text=True,
                check=False,
            )
            return str(pid) in result.stdout
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def start_local(command_parts: List[str], cwd: Optional[str], job_dir: str, name: str) -> int:
    if os.name == "nt":
        raise RuntimeError(
            "Native Windows execution is not supported for this workflow. "
            "Use execution.mode=wsl2 or execution.mode=ssh for long MG5/Delphes jobs."
        )
    job_dir = os.path.abspath(job_dir)
    paths = job_paths(job_dir, name)
    os.makedirs(job_dir, exist_ok=True)
    runner = f"""#!/usr/bin/env python3
import subprocess
from datetime import datetime, timezone

command = {json.dumps(command_parts)}
cwd = {cwd!r}
stdout_path = {json.dumps(paths["stdout"])}
stderr_path = {json.dumps(paths["stderr"])}
exitcode_path = {json.dumps(paths["exitcode"])}
finished_path = {json.dumps(paths["finished"])}

with open(stdout_path, "ab") as stdout, open(stderr_path, "ab") as stderr:
    if len(command) == 1:
        proc = subprocess.run(command[0], shell=True, cwd=cwd, stdout=stdout, stderr=stderr)
    else:
        proc = subprocess.run(command, cwd=cwd, stdout=stdout, stderr=stderr)

with open(exitcode_path, "w", encoding="utf-8") as f:
    f.write(str(proc.returncode))
with open(finished_path, "w", encoding="utf-8") as f:
    f.write(datetime.now(timezone.utc).isoformat())
"""
    with open(paths["runner"], "w", encoding="utf-8") as f:
        f.write(runner)
    kwargs = {
        "cwd": job_dir,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "stdin": subprocess.DEVNULL,
        "start_new_session": True,
    }
    proc = subprocess.Popen([sys.executable, paths["runner"]], **kwargs)
    pid = proc.pid
    meta = {
        "name": name,
        "mode": "local",
        "cwd": cwd,
        "command": command_parts,
        "pid": pid,
        "started_at": utc_now(),
        "stdout": paths["stdout"],
        "stderr": paths["stderr"],
        "runner": paths["runner"],
    }
    with open(paths["pid"], "w", encoding="utf-8") as f:
        f.write(str(pid))
    with open(paths["started"], "w", encoding="utf-8") as f:
        f.write(meta["started_at"])
    with open(paths["meta"], "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(json.dumps(meta, indent=2))
    return 0


def remote_start_command(command: str, cwd: Optional[str], paths: dict, name: str, mode: str) -> str:
    cd_line = f"cd {shlex.quote(cwd)}" if cwd else "cd ."
    script = f"""#!/usr/bin/env bash
set +e
{cd_line}
date -Is > {shlex.quote(paths["started"])}
(
  {command}
) > {shlex.quote(paths["stdout"])} 2> {shlex.quote(paths["stderr"])}
rc=$?
echo "$rc" > {shlex.quote(paths["exitcode"])}
date -Is > {shlex.quote(paths["finished"])}
exit "$rc"
"""
    meta = json.dumps({
        "name": name,
        "mode": mode,
        "cwd": cwd,
        "command": command,
        "stdout": paths["stdout"],
        "stderr": paths["stderr"],
    })
    return (
        f"mkdir -p {shlex.quote(paths['dir'])} && "
        f"printf %s {shlex.quote(script)} > {shlex.quote(paths['script'])} && "
        f"chmod +x {shlex.quote(paths['script'])} && "
        f"printf %s {shlex.quote(meta)} > {shlex.quote(paths['meta'])} && "
        f"nohup bash {shlex.quote(paths['script'])} >/dev/null 2>&1 < /dev/null & "
        f"echo $! > {shlex.quote(paths['pid'])} && "
        f"echo started {shlex.quote(name)} pid=$(cat {shlex.quote(paths['pid'])})"
    )


def start_remote(execution: dict, command_parts: List[str], cwd: Optional[str], job_dir: str, name: str) -> int:
    paths = job_paths(job_dir, name)
    command = _shell_join(command_parts)
    mode = execution.get("mode")
    command_line = remote_start_command(command, cwd, paths, name, mode)
    if mode == "ssh":
        return run_ssh(execution.get("ssh_target"), execution.get("ssh_port"), command_line, None)
    if mode == "wsl2":
        return run_wsl(execution.get("wsl_distro"), command_line, None)
    raise ValueError(f"Unsupported remote durable mode: {mode!r}")


def status_local(job_dir: str, name: str) -> int:
    if os.name == "nt":
        raise RuntimeError(
            "Native Windows execution is not supported for this workflow. "
            "Use execution.mode=wsl2 or execution.mode=ssh for long MG5/Delphes jobs."
        )
    paths = job_paths(job_dir, name)
    pid = read_pid(paths["pid"])
    exitcode = None
    if os.path.exists(paths["exitcode"]):
        with open(paths["exitcode"], encoding="utf-8") as f:
            exitcode = f.read().strip()
    running = bool(pid and local_running(pid))
    status = "running" if running else ("completed" if exitcode is not None else "unknown")
    print(json.dumps({"name": name, "pid": pid, "status": status, "exitcode": exitcode}, indent=2))
    return 0


def remote_status_command(paths: dict, name: str) -> str:
    quoted_pid = shlex.quote(paths["pid"])
    quoted_exit = shlex.quote(paths["exitcode"])
    return (
        f"pid=$(cat {quoted_pid} 2>/dev/null || true); "
        "if [ -n \"$pid\" ] && kill -0 \"$pid\" 2>/dev/null; then "
        f"printf '{{\"name\":\"{name}\",\"pid\":%s,\"status\":\"running\"}}\\n' \"$pid\"; "
        f"elif [ -f {quoted_exit} ]; then "
        f"rc=$(cat {quoted_exit}); "
        f"printf '{{\"name\":\"{name}\",\"pid\":%s,\"status\":\"completed\",\"exitcode\":%s}}\\n' \"${{pid:-null}}\" \"$rc\"; "
        "else "
        f"printf '{{\"name\":\"{name}\",\"pid\":%s,\"status\":\"unknown\"}}\\n' \"${{pid:-null}}\"; "
        "fi"
    )


def status_remote(execution: dict, job_dir: str, name: str) -> int:
    paths = job_paths(job_dir, name)
    command_line = remote_status_command(paths, name)
    mode = execution.get("mode")
    if mode == "ssh":
        return run_ssh(execution.get("ssh_target"), execution.get("ssh_port"), command_line, None)
    if mode == "wsl2":
        return run_wsl(execution.get("wsl_distro"), command_line, None)
    raise ValueError(f"Unsupported remote durable mode: {mode!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Durable long-running command runner")
    sub = parser.add_subparsers(dest="action", required=True)

    def add_common(p):
        p.add_argument("--config", help="Path to run_config.json")
        p.add_argument("--job-dir", required=True, help="Directory for PID/log/status files")
        p.add_argument("--name", required=True, help="Stable job name, e.g. phase6_scan")

    start = sub.add_parser("start", help="Start a durable command")
    add_common(start)
    start.add_argument("--cwd", help="Working directory on the selected target")
    start.add_argument("command", nargs=argparse.REMAINDER, help="Command after --")

    status = sub.add_parser("status", help="Show durable command status")
    add_common(status)

    args = parser.parse_args()
    args.name = safe_name(args.name)
    execution = _load_execution(args.config)
    mode = execution.get("mode", "local")

    if args.action == "start":
        command_parts = args.command
        if command_parts and command_parts[0] == "--":
            command_parts = command_parts[1:]
        if not command_parts:
            parser.error("start requires a command after --")
        if mode == "local":
            return start_local(command_parts, args.cwd, args.job_dir, args.name)
        return start_remote(execution, command_parts, args.cwd, args.job_dir, args.name)

    if args.action == "status":
        if mode == "local":
            return status_local(args.job_dir, args.name)
        return status_remote(execution, args.job_dir, args.name)

    raise ValueError(args.action)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

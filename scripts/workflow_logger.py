#!/usr/bin/env python3
"""Global workflow logger for phase- and step-level operation tracking.

The log file lives at `results/workflow.log` (or `results/{RUN_DIR}/workflow.log`
in multi-run mode). Each line is a JSON record.

Usage in a phase:
    from scripts.workflow_logger import WorkflowLogger
    logger = WorkflowLogger(config.workdir, run_dir)

    # Phase boundary
    logger.phase_start("6")
    # ... do work ...
    logger.phase_complete("6")

    # Step-level (every significant operation)
    logger.step("6", "mg5_launch", "started", inputs={"operator": "fS0", "nevents": 10000})
    # ... run MG5 ...
    logger.step("6", "mg5_launch", "completed",
                outputs={"returncode": 0, "runs_created": ["run_01", "run_02"]},
                duration_ms=45000)

Resume logic (called in Phase 2):
    last_completed = logger.last_completed_phase()
"""

import functools
import json
import os
import platform
import socket
import subprocess
import sys
import time
import traceback
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Generator, Optional


def _skill_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_skill_version(skill_root: str) -> Optional[str]:
    version_path = os.path.join(skill_root, "VERSION")
    try:
        with open(version_path, "r", encoding="utf-8") as f:
            version = f.read().strip()
        return version or None
    except OSError:
        return None


def _read_skill_commit(skill_root: str) -> Dict[str, Optional[str]]:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=skill_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=5,
        )
    except Exception:
        return {"skill_commit": None, "skill_commit_source": "unavailable"}

    commit = (result.stdout or "").strip()
    if result.returncode == 0 and commit:
        return {"skill_commit": commit, "skill_commit_source": "git"}
    return {"skill_commit": None, "skill_commit_source": "unavailable"}


def _read_objective_sha256(workdir: str) -> Optional[str]:
    path = os.path.join(workdir, "results", "research_contract.json")
    try:
        with open(path, "r", encoding="utf-8-sig") as handle:
            value = json.load(handle).get("objective_sha256")
        return value if isinstance(value, str) and value else None
    except (OSError, ValueError, json.JSONDecodeError):
        return None


class WorkflowLogger:
    """Append-only logger for workflow events."""

    def __init__(self, workdir: str, run_dir: Optional[str] = None):
        self.workdir = workdir
        self.run_dir = run_dir
        self.skill_root = _skill_root()
        self.skill_version = _read_skill_version(self.skill_root)
        self.skill_commit_info = _read_skill_commit(self.skill_root)
        self.objective_sha256 = _read_objective_sha256(workdir)
        self.log_path = self._log_path(workdir, run_dir)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        open(self.log_path, "a", encoding="utf-8").close()
        self._step_start_times: Dict[str, float] = {}
        self._sequence = 0

    @staticmethod
    def _log_path(workdir: str, run_dir: Optional[str]) -> str:
        if run_dir:
            return os.path.join(workdir, "results", run_dir, "workflow.log")
        return os.path.join(workdir, "results", "workflow.log")

    def _append(self, record: Dict[str, Any]) -> None:
        self._sequence += 1
        record.setdefault("schema_version", "1.1")
        record.setdefault("sequence", self._sequence)
        record.setdefault("pid", os.getpid())
        record.setdefault("cwd", os.getcwd())
        record.setdefault("workdir", self.workdir)
        record.setdefault("log_path", self.log_path)
        record.setdefault("skill_version", self.skill_version)
        record.setdefault("skill_commit", self.skill_commit_info["skill_commit"])
        record.setdefault("skill_commit_source", self.skill_commit_info["skill_commit_source"])
        record.setdefault("objective_sha256", self.objective_sha256)
        if self.run_dir:
            record.setdefault("run_dir", self.run_dir)
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def meta(self, event: str, message: str = "", details: Optional[Dict[str, Any]] = None) -> None:
        record = {"level": "meta", "event": event, "message": message}
        if details is not None:
            record["details"] = details
        self._append(record)

    def runtime_context(self) -> Dict[str, Any]:
        return {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python": sys.version,
            "python_executable": sys.executable,
            "argv": sys.argv,
            "environment": {
                "PATH": os.environ.get("PATH", ""),
                "PYTHONPATH": os.environ.get("PYTHONPATH", ""),
                "VIRTUAL_ENV": os.environ.get("VIRTUAL_ENV", ""),
            },
        }

    def assert_ready(self) -> None:
        """Verify workflow.log exists, is writable, and no stray shell artifact exists."""
        self.meta("logger_ready", "workflow log initialized", details=self.runtime_context())
        if not os.path.exists(self.log_path):
            raise RuntimeError(f"workflow.log was not created: {self.log_path}")
        bad_names = ("EOF", "!")
        candidate_dirs = [self.workdir, os.path.join(self.workdir, "results")]
        if self.run_dir:
            candidate_dirs.append(os.path.join(self.workdir, "results", self.run_dir))
        found = []
        for directory in candidate_dirs:
            for name in bad_names:
                path = os.path.join(directory, name)
                if os.path.exists(path):
                    found.append(path)
        if found:
            self.meta(
                "logging_anomaly",
                "Stray shell artifact detected; do not use heredoc or shell clobber/redirection for workflow files: "
                + ", ".join(found),
                details={"paths": found, "forbidden_names": list(bad_names)},
            )

    # ------------------------------------------------------------------
    # Phase-level (coarse-grained, for checkpoint / resume)
    # ------------------------------------------------------------------

    def phase_start(self, phase: str, message: str = "", details: Optional[Dict[str, Any]] = None) -> None:
        latest = self.latest_phase_event(phase)
        if latest == "started":
            self.meta(
                "logging_anomaly",
                f"Phase {phase} was started again before a completion/failure record",
                details={"phase": phase, "latest_phase_event": latest},
            )
        record = {"level": "phase", "phase": phase, "event": "started", "message": message}
        if details is not None:
            record["details"] = details
        self._append(record)

    def phase_complete(self, phase: str, message: str = "", details: Optional[Dict[str, Any]] = None) -> None:
        if not self.has_completed_step_records(phase):
            self.meta(
                "phase_completion_blocked",
                f"Phase {phase} has no completed step record",
                details={"phase": phase},
            )
            raise RuntimeError(f"Phase {phase} cannot complete without a completed step record")
        delivery_report = self._audit_phase_deliverables(phase)
        if delivery_report.get("status") == "FAIL":
            failure_summary = [
                {
                    "path": item.get("rel_path", item.get("path")),
                    "failure_code": item.get("failure_code"),
                    "failure_reason": item.get("failure_reason", item.get("error")),
                }
                for item in delivery_report.get("failures") or []
            ]
            self.meta(
                "phase_completion_blocked",
                f"Phase {phase} deliverables did not pass",
                details={"phase": phase, "failures": failure_summary},
            )
            raise RuntimeError(
                f"Phase {phase} deliverables did not pass: "
                + json.dumps(failure_summary, ensure_ascii=False)
            )
        self.meta(
            "phase_delivery_check",
            f"Phase {phase} deliverables passed",
            details={"phase": phase, "status": delivery_report.get("status")},
        )
        record = {"level": "phase", "phase": phase, "event": "completed", "message": message}
        if details is not None:
            record["details"] = details
        self._append(record)

    def _audit_phase_deliverables(self, phase: str) -> Dict[str, Any]:
        script = os.path.join(self.skill_root, "scripts", "audit_expected_outputs.py")
        command = [sys.executable, script, self.workdir, "--phase", str(phase)]
        if self.run_dir:
            command.extend(["--run-dir", self.run_dir])
        result = subprocess.run(
            command,
            cwd=self.skill_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=300,
        )
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                "Phase deliverable checker did not return JSON: "
                f"returncode={result.returncode}, stderr={result.stderr.strip()}"
            ) from exc
        if result.returncode not in {0, 2}:
            raise RuntimeError(
                "Phase deliverable checker could not run: "
                f"returncode={result.returncode}, stderr={result.stderr.strip()}"
            )
        return report

    def phase_fail(self, phase: str, error: str, details: Optional[Dict[str, Any]] = None) -> None:
        run_root = os.path.dirname(self.log_path)
        evidence_path = os.path.join(run_root, "failures", f"phase{phase}_failure.json")
        try:
            with open(evidence_path, "r", encoding="utf-8-sig") as handle:
                evidence = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(
                f"phase_fail requires valid structured evidence at {evidence_path}"
            ) from exc
        required = (
            "technical_cause",
            "affected_deliverables",
            "attempts",
            "evidence_paths",
            "why_no_remaining_method_can_preserve_the_contract",
        )
        missing = [key for key in required if evidence.get(key) in (None, "", [], {})]
        bad_attempts = []
        attempt_fields = (
            "command_or_code_path",
            "change_tested",
            "return_code",
            "stdout_path",
            "stderr_path",
        )
        for index, attempt in enumerate(evidence.get("attempts") or []):
            if not isinstance(attempt, dict) or any(key not in attempt for key in attempt_fields):
                bad_attempts.append(index)
        if missing or bad_attempts:
            raise RuntimeError(
                f"Invalid phase_fail evidence at {evidence_path}: "
                f"missing={missing}, bad_attempt_indexes={bad_attempts}"
            )
        record = {"level": "phase", "phase": phase, "event": "failed", "error": error}
        record["failure_evidence"] = evidence_path
        if details is not None:
            record["details"] = details
        self._append(record)

    # ------------------------------------------------------------------
    # Step-level (fine-grained, for debugging and auditing)
    # ------------------------------------------------------------------

    def step(self, phase: str, step_name: str, event: str,
             inputs: Optional[Dict[str, Any]] = None,
             outputs: Optional[Dict[str, Any]] = None,
             duration_ms: Optional[float] = None,
             error: Optional[str] = None) -> None:
        """Log a single step event.

        event: "started" | "completed" | "failed" | "skipped" | "retry"
        """
        record: Dict[str, Any] = {
            "level": "step",
            "phase": phase,
            "step": step_name,
            "event": event,
        }
        if inputs is not None:
            record["inputs"] = inputs
        if outputs is not None:
            record["outputs"] = outputs
        if duration_ms is not None:
            record["duration_ms"] = duration_ms
        if error is not None:
            record["error"] = error
        self._append(record)

    def step_start(self, phase: str, step_name: str, inputs: Optional[Dict[str, Any]] = None) -> None:
        """Record step start and remember the time for auto-duration on complete."""
        key = f"{phase}:{step_name}"
        self._step_start_times[key] = time.perf_counter()
        self.step(phase, step_name, "started", inputs=inputs)

    def step_complete(self, phase: str, step_name: str,
                      outputs: Optional[Dict[str, Any]] = None) -> None:
        """Record step completion with auto-computed duration."""
        key = f"{phase}:{step_name}"
        start = self._step_start_times.pop(key, None)
        duration_ms = round((time.perf_counter() - start) * 1000, 1) if start else None
        self.step(phase, step_name, "completed", outputs=outputs, duration_ms=duration_ms)

    def step_fail(self, phase: str, step_name: str, error: str,
                  outputs: Optional[Dict[str, Any]] = None) -> None:
        """Record step failure with auto-computed duration."""
        key = f"{phase}:{step_name}"
        start = self._step_start_times.pop(key, None)
        duration_ms = round((time.perf_counter() - start) * 1000, 1) if start else None
        self.step(phase, step_name, "failed", outputs=outputs, duration_ms=duration_ms, error=error)

    def step_retry(self, phase: str, step_name: str, attempt: int, reason: str) -> None:
        """Record a retry attempt (used by Phase 4 infinite retry, etc.)."""
        self.step(phase, step_name, "retry", inputs={"attempt": attempt, "reason": reason})

    # ------------------------------------------------------------------
    # Resume helpers
    # ------------------------------------------------------------------

    def _read_records(self):
        if not os.path.exists(self.log_path):
            return
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in reversed(f.readlines()):
                line = line.strip()
                if line:
                    yield json.loads(line)

    def last_completed_phase(self) -> Optional[str]:
        for record in self._read_records():
            if record.get("level") == "phase" and record.get("event") == "completed":
                return str(record.get("phase"))
        return None

    def last_completed_phase_record(self) -> Optional[Dict[str, Any]]:
        for record in self._read_records():
            if record.get("level") == "phase" and record.get("event") == "completed":
                return record
        return None

    def latest_phase_event(self, phase: str) -> Optional[str]:
        for record in self._read_records():
            if record.get("level") == "phase" and str(record.get("phase")) == str(phase):
                return str(record.get("event"))
        return None

    def has_step_records(self, phase: str) -> bool:
        for record in self._read_records():
            if record.get("level") == "step" and str(record.get("phase")) == str(phase):
                return True
        return False

    def has_completed_step_records(self, phase: str) -> bool:
        for record in self._read_records():
            if (
                record.get("level") == "step"
                and str(record.get("phase")) == str(phase)
                and record.get("event") == "completed"
            ):
                return True
        return False

    def is_phase_completed(self, phase: str) -> bool:
        for record in self._read_records():
            if (record.get("level") == "phase" and
                record.get("phase") == phase and
                record.get("event") == "completed"):
                return True
            if (record.get("level") == "phase" and
                record.get("phase") == phase and
                record.get("event") == "started"):
                return False
        return False

    def get_resume_phase(self) -> Optional[str]:
        completed = self.last_completed_phase_record()
        if completed is None:
            return None
        last = str(completed.get("phase"))
        if str(last).lower() == "cleanup":
            return "11"
        try:
            phase_number = int(last)
        except ValueError:
            return None
        if phase_number == 11:
            version = str(completed.get("skill_version", ""))
            try:
                version_parts = tuple(int(part) for part in version.split("."))
            except ValueError:
                version_parts = ()
            if not version_parts:
                replay_steps = {
                    "freeze_replay_inputs",
                    "generate_replay_entrypoint",
                    "validate_replay_package",
                }
                has_replay_step = any(
                    record.get("step") in replay_steps
                    for record in self.get_phase_steps("11")
                )
                return "12" if has_replay_step else "11"
            if version_parts and version_parts < (0, 25):
                return "11"
            return "12"
        if phase_number >= 12:
            return "12"
        return str(phase_number + 1)

    def get_phase_steps(self, phase: str) -> list:
        """Return all step-level records for a given phase (oldest first)."""
        steps = []
        for record in self._read_records():
            if record.get("level") == "step" and str(record.get("phase")) == phase:
                steps.append(record)
        steps.reverse()
        return steps


# ------------------------------------------------------------------
# Mandatory logging primitives — zero bare operations
# ------------------------------------------------------------------

class _WorkflowStepContext:
    """Context manager that auto-logs step start / complete / fail.

    Usage:
        with _WorkflowStepContext(logger, "3", "test_coeff_fS0",
                                  inputs={"c": 1e-12}) as step:
            result = run_mg5(...)
            step.set_outputs({"sigma": sigma})

    On normal exit: logs 'completed' with outputs.
    On exception: logs 'failed' with error text, then re-raises.
    """

    def __init__(
        self,
        logger: WorkflowLogger,
        phase: str,
        step_name: str,
        inputs: Optional[Dict[str, Any]] = None,
    ):
        self.logger = logger
        self.phase = phase
        self.step_name = step_name
        self.inputs = inputs
        self._outputs: Optional[Dict[str, Any]] = None

    def __enter__(self) -> "_WorkflowStepContext":
        self.logger.step_start(self.phase, self.step_name, inputs=self.inputs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is not None:
            self.logger.step_fail(
                self.phase,
                self.step_name,
                error=f"{exc_type.__name__}: {exc_val}",
                outputs={
                    "exception_type": exc_type.__name__,
                    "traceback": "".join(traceback.format_exception(exc_type, exc_val, exc_tb)),
                },
            )
        else:
            self.logger.step_complete(
                self.phase, self.step_name, outputs=self._outputs
            )
        return False  # do not swallow exceptions

    def set_outputs(self, outputs: Dict[str, Any]) -> None:
        """Record outputs to be logged on successful completion."""
        self._outputs = outputs


@contextmanager
def workflow_step(
    logger: WorkflowLogger,
    phase: str,
    step_name: str,
    inputs: Optional[Dict[str, Any]] = None,
) -> Generator[_WorkflowStepContext, None, None]:
    """Context manager that guarantees step-level logging.

    **This is the primary mechanism for zero-bare-operations compliance.**
    Any filesystem operation, subprocess call, download, install, or
    validation check must be wrapped by this context manager (or by
    ``@logged_step``).  Bare ``subprocess.run`` / ``os.makedirs`` /
    ``shutil.copy`` without logging is a skill violation.

    Example — wrapping a subprocess call::

        with workflow_step(logger, "2", "setup_venv",
                           inputs={"venv_dir": venv_dir}):
            subprocess.run([sys.executable, "-m", "venv", venv_dir],
                           check=True)

    Example — capturing outputs::

        with workflow_step(logger, "3", "test_coeff_fS0",
                           inputs={"c": 1e-12}) as step:
            run_mg5(...)
            sigma = extract_cross_section(...)
            step.set_outputs({"sigma": sigma})

    Example — exception auto-logged as 'failed'::

        with workflow_step(logger, "2", "validate_madgraph5",
                           inputs={"mg5path": mg5path}):
            if not os.path.exists(mg5path):
                raise RuntimeError("MG5 not found")
    """
    ctx = _WorkflowStepContext(logger, phase, step_name, inputs)
    with ctx:
        yield ctx


def run_logged_subprocess(
    logger: WorkflowLogger,
    phase: str,
    step_name: str,
    command,
    cwd: Optional[str] = None,
    stdout_path: Optional[str] = None,
    stderr_path: Optional[str] = None,
    check: bool = True,
    inputs: Optional[Dict[str, Any]] = None,
):
    """Run a subprocess and log enough detail for bug reports.

    Prefer this helper over bare ``subprocess.run`` whenever a workflow command
    may fail, produce external logs, or create files used by later phases.
    """
    command_list = list(command)
    merged_inputs = dict(inputs or {})
    merged_inputs.update({
        "command": command_list,
        "cwd": cwd,
        "stdout_path": stdout_path,
        "stderr_path": stderr_path,
    })
    logger.step_start(phase, step_name, inputs=merged_inputs)
    start_t = time.perf_counter()
    stdout_f = open(stdout_path, "a", encoding="utf-8") if stdout_path else subprocess.PIPE
    stderr_f = open(stderr_path, "a", encoding="utf-8") if stderr_path else subprocess.PIPE
    try:
        result = subprocess.run(
            command_list,
            cwd=cwd,
            stdout=stdout_f,
            stderr=stderr_f,
            text=True,
            check=False,
        )
    finally:
        if stdout_path:
            stdout_f.close()
        if stderr_path:
            stderr_f.close()

    duration_ms = round((time.perf_counter() - start_t) * 1000, 1)
    outputs = {
        "returncode": result.returncode,
        "duration_ms": duration_ms,
        "stdout_path": stdout_path,
        "stderr_path": stderr_path,
    }
    if not stdout_path:
        outputs["stdout_tail"] = (result.stdout or "")[-4000:]
    if not stderr_path:
        outputs["stderr_tail"] = (result.stderr or "")[-4000:]

    if result.returncode == 0:
        logger.step_complete(phase, step_name, outputs=outputs)
        return result

    logger.step_fail(
        phase,
        step_name,
        error=f"subprocess exited with return code {result.returncode}",
        outputs=outputs,
    )
    if check:
        raise RuntimeError(
            f"{step_name} failed with return code {result.returncode}: {command_list}"
        )
    return result


def logged_step(
    phase: str,
    step_name: Optional[str] = None,
    inputs_fn=None,
):
    """Decorator that auto-logs step start / complete / fail around a function.

    The decorated function **must** accept a ``logger: WorkflowLogger``
    keyword argument (or a positional argument of type ``WorkflowLogger``).
    If no logger is found, the function runs silently (degraded mode).

    The return value of the decorated function is used as ``outputs`` if it
    is a ``dict``; otherwise outputs are omitted.

    Example::

        @logged_step("2", "setup_venv")
        def setup_venv(venv_dir: str, *, logger: WorkflowLogger):
            subprocess.run([sys.executable, "-m", "venv", venv_dir],
                           check=True)
            python_bin = os.path.join(venv_dir, "bin", "python")
            return {"venv_dir": venv_dir, "python_bin": python_bin}

    Example with dynamic inputs::

        @logged_step("2", "validate_model",
                     inputs_fn=lambda model, **kw: {"model": model})
        def validate_model(model: str, *, logger: WorkflowLogger):
            exists = os.path.exists(f"models/{model}")
            return {"exists": exists}
    """
    def decorator(func):
        actual_step_name = step_name or func.__name__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Locate logger in args or kwargs
            logger = kwargs.get("logger")
            if logger is None:
                for arg in args:
                    if isinstance(arg, WorkflowLogger):
                        logger = arg
                        break

            inputs = inputs_fn(*args, **kwargs) if inputs_fn else None

            if logger is None:
                # Degraded mode — log to stderr so the violation is visible
                print(
                    f"[WORKFLOW WARNING] {actual_step_name} executed without "
                    f"a WorkflowLogger. Pass logger=... to enable step-level "
                    f"logging.",
                    file=sys.stderr,
                )
                return func(*args, **kwargs)

            logger.step_start(phase, actual_step_name, inputs=inputs)
            try:
                result = func(*args, **kwargs)
                outputs = result if isinstance(result, dict) else None
                logger.step_complete(phase, actual_step_name, outputs=outputs)
                return result
            except Exception as e:
                logger.step_fail(
                    phase,
                    actual_step_name,
                    error=f"{type(e).__name__}: {e}",
                    outputs={
                        "exception_type": type(e).__name__,
                        "traceback": traceback.format_exc(),
                    },
                )
                raise

        return wrapper

    return decorator


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query workflow.log")
    parser.add_argument("workdir", help="Working directory")
    parser.add_argument("run_dir", nargs="?", default=None)
    parser.add_argument("--last", action="store_true", help="Last completed phase")
    parser.add_argument("--resume", action="store_true", help="Phase to resume from")
    parser.add_argument("--steps", metavar="PHASE", help="List all steps for a phase")
    parser.add_argument("--has-steps", metavar="PHASE", help="Print true if a phase has step records")
    parser.add_argument("--touch", action="store_true", help="Create and validate workflow.log")
    parser.add_argument("--start", metavar="PHASE", help="Append a phase-start record")
    parser.add_argument("--complete", metavar="PHASE", help="Append a phase-complete record")
    parser.add_argument("--fail", nargs=2, metavar=("PHASE", "ERROR"), help="Append a phase-fail record")
    args = parser.parse_args()

    logger = WorkflowLogger(args.workdir, args.run_dir)
    if args.touch:
        logger.assert_ready()
        print(logger.log_path)
    elif args.start:
        logger.assert_ready()
        logger.phase_start(args.start)
        print(logger.log_path)
    elif args.complete:
        logger.phase_complete(args.complete)
        print(logger.log_path)
    elif args.fail:
        logger.phase_fail(args.fail[0], args.fail[1])
        print(logger.log_path)
    elif args.last:
        print(logger.last_completed_phase() or "None")
    elif args.resume:
        print(logger.get_resume_phase() or "None")
    elif args.steps:
        for rec in logger.get_phase_steps(args.steps):
            print(json.dumps(rec, ensure_ascii=False, default=str))
    elif args.has_steps:
        print("true" if logger.has_step_records(args.has_steps) else "false")
    else:
        if os.path.exists(logger.log_path):
            with open(logger.log_path) as f:
                print(f.read().strip())
        else:
            print("No workflow.log found.")


if __name__ == "__main__":
    main()

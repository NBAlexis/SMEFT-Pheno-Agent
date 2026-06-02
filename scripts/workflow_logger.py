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
import sys
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Dict, Generator, Optional


class WorkflowLogger:
    """Append-only logger for workflow events."""

    def __init__(self, workdir: str, run_dir: Optional[str] = None):
        self.workdir = workdir
        self.run_dir = run_dir
        self.log_path = self._log_path(workdir, run_dir)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        open(self.log_path, "a", encoding="utf-8").close()
        self._step_start_times: Dict[str, float] = {}

    @staticmethod
    def _log_path(workdir: str, run_dir: Optional[str]) -> str:
        if run_dir:
            return os.path.join(workdir, "results", run_dir, "workflow.log")
        return os.path.join(workdir, "results", "workflow.log")

    def _append(self, record: Dict[str, Any]) -> None:
        record["timestamp"] = datetime.now(timezone.utc).isoformat()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def meta(self, event: str, message: str = "") -> None:
        self._append({"level": "meta", "event": event, "message": message})

    def assert_ready(self) -> None:
        """Verify workflow.log exists, is writable, and no stray EOF file exists."""
        self.meta("logger_ready", "workflow log initialized")
        if not os.path.exists(self.log_path):
            raise RuntimeError(f"workflow.log was not created: {self.log_path}")
        eof_candidates = [
            os.path.join(self.workdir, "EOF"),
            os.path.join(self.workdir, "results", "EOF"),
        ]
        if self.run_dir:
            eof_candidates.append(os.path.join(self.workdir, "results", self.run_dir, "EOF"))
        found = [path for path in eof_candidates if os.path.exists(path)]
        if found:
            self.meta(
                "logging_anomaly",
                "Stray EOF file detected; do not use heredoc/shell EOF redirection for workflow files: "
                + ", ".join(found),
            )

    # ------------------------------------------------------------------
    # Phase-level (coarse-grained, for checkpoint / resume)
    # ------------------------------------------------------------------

    def phase_start(self, phase: str, message: str = "") -> None:
        self._append({"level": "phase", "phase": phase, "event": "started", "message": message})

    def phase_complete(self, phase: str, message: str = "") -> None:
        self._append({"level": "phase", "phase": phase, "event": "completed", "message": message})

    def phase_fail(self, phase: str, error: str) -> None:
        self._append({"level": "phase", "phase": phase, "event": "failed", "error": error})

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
        last = self.last_completed_phase()
        if last is None:
            return None
        if str(last).lower() == "cleanup":
            return "11"
        try:
            phase_number = int(last)
        except ValueError:
            return None
        if phase_number >= 11:
            return "11"
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
                self.phase, self.step_name, error=str(exc_val)
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
                logger.step_fail(phase, actual_step_name, error=str(e))
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
    else:
        if os.path.exists(logger.log_path):
            with open(logger.log_path) as f:
                print(f.read().strip())
        else:
            print("No workflow.log found.")


if __name__ == "__main__":
    main()

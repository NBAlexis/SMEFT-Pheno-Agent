#!/usr/bin/env python3
"""Global workflow logger for phase- and step-level operation tracking.

The log file lives at `results/workflow.log` (or `results/{RUN_DIR}/workflow.log`
in multi-run mode). Each line is a JSON record.

Usage in a phase:
    from scripts.workflow_logger import WorkflowLogger
    logger = WorkflowLogger(config.workdir, run_dir)

    # Phase boundary
    logger.phase_start("4")
    # ... do work ...
    logger.phase_complete("4")

    # Step-level (every significant operation)
    logger.step("4", "mg5_launch", "started", inputs={"operator": "fS0", "nevents": 10000})
    # ... run MG5 ...
    logger.step("4", "mg5_launch", "completed",
                outputs={"returncode": 0, "runs_created": ["run_01", "run_02"]},
                duration_ms=45000)

Resume logic (called in Phase 0):
    last_completed = logger.last_completed_phase()
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class WorkflowLogger:
    """Append-only logger for workflow events."""

    def __init__(self, workdir: str, run_dir: Optional[str] = None):
        self.log_path = self._log_path(workdir, run_dir)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
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
        if last == "-1":
            return "0"
        return str(int(last) + 1)

    def get_phase_steps(self, phase: str) -> list:
        """Return all step-level records for a given phase (oldest first)."""
        steps = []
        for record in self._read_records():
            if record.get("level") == "step" and str(record.get("phase")) == phase:
                steps.append(record)
        steps.reverse()
        return steps


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Query workflow.log")
    parser.add_argument("workdir", help="Working directory")
    parser.add_argument("run_dir", nargs="?", default=None)
    parser.add_argument("--last", action="store_true", help="Last completed phase")
    parser.add_argument("--resume", action="store_true", help="Phase to resume from")
    parser.add_argument("--steps", metavar="PHASE", help="List all steps for a phase")
    args = parser.parse_args()

    logger = WorkflowLogger(args.workdir, args.run_dir)
    if args.last:
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

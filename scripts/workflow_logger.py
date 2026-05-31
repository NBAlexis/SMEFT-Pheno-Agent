#!/usr/bin/env python3
"""Global workflow logger for phase-level checkpointing and resume.

The log file lives at `results/workflow.log` (or `results/{RUN_DIR}/workflow.log`
in multi-run mode). Each line is a JSON record with:
    {"timestamp": "ISO8601", "phase": "N", "event": "started|completed|failed", "message": "..."}

Resume logic (called in Phase 0):
    from scripts.workflow_logger import WorkflowLogger
    logger = WorkflowLogger(workdir, run_dir)
    last_completed = logger.last_completed_phase()  # e.g. "4"
    if last_completed:
        next_phase = str(int(last_completed) + 1)
        # resume from next_phase instead of starting at Phase 1
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional


class WorkflowLogger:
    """Append-only logger for workflow phase events."""

    def __init__(self, workdir: str, run_dir: Optional[str] = None):
        self.log_path = self._log_path(workdir, run_dir)
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    @staticmethod
    def _log_path(workdir: str, run_dir: Optional[str]) -> str:
        if run_dir:
            return os.path.join(workdir, "results", run_dir, "workflow.log")
        return os.path.join(workdir, "results", "workflow.log")

    def log(self, phase: str, event: str, message: str = "") -> None:
        """Append a log record.  event must be one of started, completed, failed."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": phase,
            "event": event,
            "message": message,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def _read_records(self):
        """Yield records from newest to oldest."""
        if not os.path.exists(self.log_path):
            return
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in reversed(f.readlines()):
                line = line.strip()
                if line:
                    yield json.loads(line)

    def last_completed_phase(self) -> Optional[str]:
        """Return the phase number (as string) of the most recent 'completed' event."""
        for record in self._read_records():
            if record.get("event") == "completed":
                return str(record.get("phase"))
        return None

    def is_phase_completed(self, phase: str) -> bool:
        """Check whether the given phase has a 'completed' record."""
        for record in self._read_records():
            if record.get("phase") == phase and record.get("event") == "completed":
                return True
            # if we see a 'started' for this phase without a preceding completed,
            # the phase was interrupted
            if record.get("phase") == phase and record.get("event") == "started":
                return False
        return False

    def get_resume_phase(self) -> Optional[str]:
        """Return the phase to resume from, or None if workflow has not started.

        If Phase -1 is completed but Phase 0 is not, returns "0".
        If Phase 4 is the last completed, returns "5".
        If no phases completed, returns None (start from Phase -1 or 0).
        """
        last = self.last_completed_phase()
        if last is None:
            return None
        # Phase -1 → resume from Phase 0
        if last == "-1":
            return "0"
        return str(int(last) + 1)


def main():
    """CLI: python scripts/workflow_logger.py <workdir> [run_dir] [--last|--resume]"""
    import argparse
    parser = argparse.ArgumentParser(description="Query workflow.log for resume info")
    parser.add_argument("workdir", help="Working directory")
    parser.add_argument("run_dir", nargs="?", default=None, help="Run subdirectory (e.g. E10_L1000)")
    parser.add_argument("--last", action="store_true", help="Print last completed phase")
    parser.add_argument("--resume", action="store_true", help="Print phase to resume from")
    args = parser.parse_args()

    logger = WorkflowLogger(args.workdir, args.run_dir)
    if args.last:
        phase = logger.last_completed_phase()
        print(phase if phase else "None")
    elif args.resume:
        phase = logger.get_resume_phase()
        print(phase if phase else "None")
    else:
        # dump log
        if os.path.exists(logger.log_path):
            with open(logger.log_path) as f:
                print(f.read().strip())
        else:
            print("No workflow.log found.")


if __name__ == "__main__":
    main()

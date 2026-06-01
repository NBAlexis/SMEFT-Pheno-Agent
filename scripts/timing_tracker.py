#!/usr/bin/env python3
"""
Track execution timing across workflow phases and MG5 internal steps.

Records start/end times for each phase and sub-step, then reports
a summary table with durations and cumulative progress.

Usage as context manager:
    with timing_tracker.phase_timer("Phase 4: Scan"):
        # ... run phase 4 ...

Usage for MG5 sub-steps (integrated into run_mg5):
    timing_tracker.record_mg5_step("madgraph", start_t, end_t)
    timing_tracker.record_mg5_step("pythia8", start_t, end_t)
    timing_tracker.record_mg5_step("delphes", start_t, end_t)

Report:
    timing_tracker.print_report()

Persistent log:
    timing_tracker.save_log("results/timing_log.json")
"""
import json
import sys
import time
from collections import OrderedDict
from contextlib import contextmanager
from datetime import datetime


class TimingTracker:
    """Tracks phase-level and MG5 sub-step timings."""

    PHASE_ORDER = [
        "Phase 1: Input Collection",
        "Phase 2: Environment",
        "Phase 3: Validation",
        "Phase 4: Range Estimation",
        "Phase 5: Pure Samples",
        "Phase 6: Coefficient Scan",
        "Phase 7: ML Training",
        "Phase 8: Selection Optimization",
        "Phase 9: Constraints",
        "Phase 10: Report",
        "Cleanup",
        "Phase 11: Audit",
    ]

    def __init__(self, log_path=None):
        self.phases = OrderedDict()
        self.current_phase = None
        self.mg5_steps = OrderedDict()  # phase -> {madgraph: t, pythia8: t, delphes: t}
        self.log_path = log_path
        self._start_time = time.time()

    # ------------------------------------------------------------------
    # Phase-level tracking
    # ------------------------------------------------------------------

    @contextmanager
    def phase_timer(self, phase_name):
        """Context manager: record duration of a phase block."""
        self.start_phase(phase_name)
        try:
            yield
        finally:
            self.end_phase(phase_name)

    def start_phase(self, phase_name):
        """Mark the start of a phase."""
        now = time.time()
        self.current_phase = phase_name
        self.phases[phase_name] = {
            "start": now,
            "end": None,
            "duration_sec": None,
            "status": "running",
        }
        self._print_progress(phase_name, now)

    def end_phase(self, phase_name):
        """Mark the end of a phase."""
        now = time.time()
        rec = self.phases.get(phase_name)
        if rec is None:
            return
        rec["end"] = now
        rec["duration_sec"] = round(now - rec["start"], 2)
        rec["status"] = "done"
        if self.current_phase == phase_name:
            self.current_phase = None

    def fail_phase(self, phase_name, reason=""):
        """Mark a phase as failed."""
        now = time.time()
        rec = self.phases.get(phase_name)
        if rec:
            rec["end"] = now
            rec["duration_sec"] = round(now - rec["start"], 2)
            rec["status"] = "failed"
            rec["reason"] = reason

    # ------------------------------------------------------------------
    # MG5 sub-step tracking
    # ------------------------------------------------------------------

    def record_mg5_step(self, step_name, start_t, end_t, phase_name=None):
        """Record timing for an MG5 internal step.

        step_name: one of "madgraph", "pythia8", "delphes", "other"
        """
        phase = phase_name or self.current_phase or "unknown"
        if phase not in self.mg5_steps:
            self.mg5_steps[phase] = OrderedDict()
        self.mg5_steps[phase][step_name] = {
            "start": start_t,
            "end": end_t,
            "duration_sec": round(end_t - start_t, 2),
        }

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def _fmt_duration(self, sec):
        if sec is None:
            return "—"
        if sec < 60:
            return f"{sec:.1f}s"
        if sec < 3600:
            return f"{sec/60:.1f}m"
        return f"{sec/3600:.1f}h"

    def _print_progress(self, phase_name, now):
        """Print a single-line progress banner."""
        elapsed = now - self._start_time
        elapsed_str = self._fmt_duration(elapsed)
        # Count completed phases
        completed = sum(1 for p in self.phases.values() if p["status"] == "done")
        total = len(self.PHASE_ORDER)
        print(
            f"\n[{'='*60}]\n"
            f"  >>> NOW RUNNING: {phase_name}\n"
            f"  >>> Elapsed so far: {elapsed_str}  |  Completed: {completed}/{total} phases\n"
            f"[{'='*60}]\n",
            flush=True,
        )

    def print_report(self):
        """Print a formatted timing summary table."""
        print("\n" + "=" * 80)
        print("  TIMING SUMMARY")
        print("=" * 80)

        # Phase table
        print("\n  {:<40} {:>12} {:>12} {:>10}".format(
            "Phase", "Start", "Duration", "Status"
        ))
        print("  " + "-" * 78)

        for name in self.PHASE_ORDER:
            rec = self.phases.get(name)
            if rec is None:
                continue
            start_dt = datetime.fromtimestamp(rec["start"]).strftime("%H:%M:%S")
            dur = self._fmt_duration(rec["duration_sec"])
            status = rec["status"]
            marker = "  "
            if status == "running":
                marker = "▶ "
            elif status == "failed":
                marker = "✗ "
            print(f"  {marker}{name:<38} {start_dt:>12} {dur:>12} {status:>10}")

        # MG5 sub-step breakdown
        if self.mg5_steps:
            print("\n  MG5 Step Breakdown (per phase)")
            print("  " + "-" * 78)
            for phase, steps in self.mg5_steps.items():
                for step_name, rec in steps.items():
                    dur = self._fmt_duration(rec["duration_sec"])
                    print(f"    └─ {phase}: {step_name:<12} {dur:>12}")

        total = time.time() - self._start_time
        print("\n  " + "-" * 78)
        print(f"  TOTAL ELAPSED: {self._fmt_duration(total)}")
        print("=" * 80 + "\n")

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def to_dict(self):
        """Serialize timing data to a dict."""
        return {
            "phases": {k: v for k, v in self.phases.items()},
            "mg5_steps": {k: {sk: sv for sk, sv in v.items()}
                          for k, v in self.mg5_steps.items()},
            "total_elapsed_sec": round(time.time() - self._start_time, 2),
            "timestamp": datetime.now().isoformat(),
        }

    def save_log(self, path):
        """Save timing data to JSON."""
        data = self.to_dict()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"Timing log saved to: {path}")


# Global singleton for convenience
_timing = None


def get_tracker(log_path=None):
    """Get or create the global TimingTracker instance."""
    global _timing
    if _timing is None:
        _timing = TimingTracker(log_path=log_path)
    return _timing


# Convenience exports matching the usage patterns above
phase_timer = lambda name: get_tracker().phase_timer(name)
start_phase = lambda name: get_tracker().start_phase(name)
end_phase = lambda name: get_tracker().end_phase(name)
record_mg5_step = lambda step, s, e, p=None: get_tracker().record_mg5_step(step, s, e, p)
print_report = lambda: get_tracker().print_report()
save_log = lambda path: get_tracker().save_log(path)


if __name__ == "__main__":
    # Demo
    tracker = TimingTracker()
    with tracker.phase_timer("Phase 3: Validation"):
        time.sleep(0.1)
    with tracker.phase_timer("Phase 4: Range"):
        time.sleep(0.05)
        tracker.record_mg5_step("madgraph", time.time() - 0.04, time.time() - 0.01)
    tracker.print_report()

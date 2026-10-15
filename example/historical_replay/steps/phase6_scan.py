#!/usr/bin/env python3
"""Phase 6 driver: SM+NP coefficient scans (11 points per claimed operator).

Unattended full-core mode: operator scans run concurrently (each scan is
internally sequential over its 11 MG5 scan runs). The event-count recovery
orchestrator runs sequentially per operator afterwards because it updates the
shared aggregate event_count_recovery.json with read-modify-write semantics.
"""
import json
import os
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

WORKDIR = os.environ.get("SMEFT_WORKDIR", "/mnt/e/SMEFT-Pheno-Agent-GLM-test")
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")
PYTHON = os.path.join(WORKDIR, "venv", "bin", "python")
RUNNER = os.path.join(SKILL_RUNTIME, "scripts", "run_mg5_config.py")
RECOVERY = os.path.join(SKILL_RUNTIME, "scripts", "recover_lhco_count.py")
WEIGHTED = os.path.join(SKILL_RUNTIME, "scripts", "extract_weighted_order.py")
SCAN_WORKERS = 6
STAGGLE_SECONDS = 600
MIN_AVAILABLE_MB = 3500
MAX_RETRIES = 5
SCAN_LABELS = [f"f{i}" for i in range(11)]

sys.path.insert(0, SKILL_RUNTIME)
from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, workflow_step, run_logged_subprocess

_LOG_LOCK = threading.Lock()
_PROGRESS_LOCK = threading.Lock()


class LockedLogger:
    def __init__(self, logger):
        self._logger = logger

    def __getattr__(self, name):
        target = getattr(self._logger, name)
        if callable(target):
            def wrapped(*args, **kwargs):
                with _LOG_LOCK:
                    return target(*args, **kwargs)
            return wrapped
        return target


def read_json(path):
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)


def mem_available_mb():
    with open("/proc/meminfo", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    return 0


def wait_for_memory():
    while mem_available_mb() < MIN_AVAILABLE_MB:
        time.sleep(60)


def process_dirs_from_result(result_path, mg5path):
    """Collect every existing process dir referenced by a runner/recovery JSON.

    Accepts both a plain runner result (root process_folder) and an
    event-count-recovery summary, which stores no process_folder itself but
    points at the per-attempt result JSONs via recovery_attempt_result_jsons.
    """
    found = []

    def scan(obj):
        if isinstance(obj, dict):
            folder = obj.get("process_folder")
            if isinstance(folder, str) and folder:
                path = os.path.join(mg5path, folder)
                if os.path.isdir(path) and path not in found:
                    found.append(path)
            for value in obj.values():
                scan(value)
        elif isinstance(obj, list):
            for value in obj:
                scan(value)

    paths_to_scan = [result_path]
    try:
        summary = read_json(result_path)
    except Exception:
        summary = {}
    for extra in summary.get("recovery_attempt_result_jsons") or []:
        if isinstance(extra, str) and os.path.exists(extra):
            paths_to_scan.append(extra)
    for path in paths_to_scan:
        try:
            scan(read_json(path))
        except Exception:
            continue
    if not found:
        raise RuntimeError(f"No process_folder found in {result_path}")
    return sorted(found)


class Phase6State:
    def __init__(self, progress_path, progress):
        self.progress_path = progress_path
        self.progress = progress

    def set(self, op_key, status=None, labels=None):
        with _PROGRESS_LOCK:
            if status is not None:
                self.progress["operators"][op_key]["status"] = status
            if labels is not None:
                self.progress["operators"][op_key]["completed_labels"] = labels
            write_json(self.progress_path, self.progress)


def run_operator_scan(op_key, context, logger):
    """Initial 11-point scan for one operator, with retry. Returns scan_cfg."""
    config, claim, c_scan, weighted, dirs = context
    phase6_dir, logs_dir, jobs_dir, manifest_path, state = dirs
    run_cfg = config.run_configurations[0]
    nev_scan = int(config.locked_event_counts.nev_scan)

    manifest = read_json(manifest_path)
    manifest[op_key]["weighted_order_guard"] = {
        "max_weighted_order": weighted["max_weighted_order"],
        "status": "pass",
        "sm_result_json": "results/data/phase4/sm_baseline_result.json",
        "np_result_json": f"results/data/phase5/np_{op_key}_result.json",
        "weighted_order_json": f"results/data/phase6/{op_key}_weighted_order.json",
    }
    with _PROGRESS_LOCK:
        write_json(manifest_path, manifest)

    result_path = os.path.join(phase6_dir, f"{op_key}_scan_result.json")
    attempt = 0
    while True:
        attempt += 1
        state.set(op_key, status="running" if attempt == 1 else "failed_retrying")
        scan_cfg = {
            "mg5path": config.madgraph_path,
            "model": claim["model"],
            "process": config.process,
            "madspin": {"enabled": bool(config.madspin.enabled)},
            "process_mode": "scan",
            "operator": op_key,
            "target_coefficient": {"index": int(claim["anoinput_idx"])},
            "c_scan": c_scan,
            "weighted_order": int(weighted["max_weighted_order"]),
            "run_label": run_cfg.run_dir,
            "ebeam1": run_cfg.ebeam1,
            "ebeam2": run_cfg.ebeam2,
            "nevents": nev_scan,
            "delphes_card": config.delphes_card,
            "cutexperiment_path": config.cutexperiment_path,
            "output_prefix": f"np_{op_key}",
            "output_dir": phase6_dir,
            "log_dir": logs_dir,
            "result_json": result_path,
            # bound Pythia burst memory per launch (VM panic mitigation):
            # 6 workers x nb_core 2 = 12 shower jobs peak instead of 120
            "nb_core": 2,
        }
        write_json(os.path.join(phase6_dir, f"{op_key}_runner.json"), scan_cfg)
        wait_for_memory()
        proc = run_logged_subprocess(
            logger, "6", f"run_scan_{op_key}_attempt{attempt}",
            [PYTHON, RUNNER, os.path.join(phase6_dir, f"{op_key}_runner.json")],
            cwd=SKILL_RUNTIME,
            stdout_path=os.path.join(jobs_dir, f"phase6_{op_key}_a{attempt}.stdout"),
            stderr_path=os.path.join(jobs_dir, f"phase6_{op_key}_a{attempt}.stderr"),
            check=False,
        )
        if proc.returncode == 0:
            return scan_cfg
        if attempt >= MAX_RETRIES:
            raise RuntimeError(
                f"scan for {op_key} failed after {attempt} attempts; see "
                f"{jobs_dir}/phase6_{op_key}_a{attempt}.stderr")
        time.sleep(60)


def main():
    config = load_run_config(RUN_CONFIG)
    raw_logger = WorkflowLogger(WORKDIR, None)
    logger = LockedLogger(raw_logger)
    run_root = os.path.join(WORKDIR, "results")
    phase3_dir = os.path.join(run_root, "data", "phase3")
    phase4_dir = os.path.join(run_root, "data", "phase4")
    phase5_dir = os.path.join(run_root, "data", "phase5")
    phase6_dir = os.path.join(run_root, "data", "phase6")
    logs_dir = os.path.join(phase6_dir, "logs")
    jobs_dir = os.path.join(run_root, "jobs")
    for directory in (phase6_dir, logs_dir):
        os.makedirs(directory, exist_ok=True)
    logger.phase_start("6")

    operator_claims = read_json(os.path.join(phase3_dir, "operator_claims.json"))
    coefficient_ranges = read_json(os.path.join(phase4_dir, "coefficient_ranges.json"))
    op_keys = sorted(operator_claims, key=lambda k: int(k.split("_")[1]))
    config_mg5 = config.madgraph_path
    sm_process_dirs = process_dirs_from_result(
        os.path.join(phase4_dir, "sm_baseline_result.json"), config_mg5)

    manifest_path = os.path.join(phase6_dir, "scan_manifest.json")
    progress_path = os.path.join(phase6_dir, "phase6_progress.json")

    if os.path.exists(manifest_path):
        manifest = read_json(manifest_path)
    else:
        manifest = {}
        for op_key in op_keys:
            claim = operator_claims[op_key]
            c_scan = float(coefficient_ranges["operators"][op_key]["c_scan"])
            c_text = f"{c_scan:.2g}"
            manifest[op_key] = {
                "model": claim["model"],
                "anoinput_idx": claim["anoinput_idx"],
                "c_scan": c_scan,
                "scan_expression": f"[-{c_text} + 0.2 * {c_text} * n for n in range(11)]",
                "point_count": 11,
                "labels": SCAN_LABELS,
            }
        write_json(manifest_path, manifest)

    if os.path.exists(progress_path):
        progress = read_json(progress_path)
    else:
        progress = {"operators": {}}
    for op in op_keys:
        progress["operators"].setdefault(op, {"status": "pending", "completed_labels": []})
    write_json(progress_path, progress)
    state = Phase6State(progress_path, progress)

    scan_cfgs = {}

    def process_dirs_from_unit(phase_dir, unit, mg5path):
        """Process dirs from the phase aggregate recovery metadata attempts."""
        aggregate = read_json(os.path.join(phase_dir, "event_count_recovery.json"))
        found = []
        for attempt in (aggregate.get("units", {}).get(unit, {})
                        .get("attempts") or []):
            result = attempt.get("result") if isinstance(attempt, dict) else {}
            folder = (result or {}).get("process_folder")
            if isinstance(folder, str) and folder:
                path = os.path.join(mg5path, folder)
                if os.path.isdir(path) and path not in found:
                    found.append(path)
        if not found:
            raise RuntimeError(f"No process_folder in aggregate unit {unit}")
        return sorted(found)

    # ---- normalize result filenames to the contract np_{op} names ----
    for op_key in op_keys:
        old_result = os.path.join(phase6_dir, f"{op_key}_scan_result.json")
        new_result = os.path.join(phase6_dir, f"np_{op_key}_scan_result.json")
        if os.path.exists(old_result) and not os.path.exists(new_result):
            import shutil
            shutil.copy2(old_result,
                         os.path.join(phase6_dir, f"np_{op_key}_scan_initial_result.json"))
            os.rename(old_result, new_result)
            raw_logger.meta("phase6_result_rename",
                            f"archived initial scan and renamed result to "
                            f"np_{op_key}_scan_result.json")
        old_runner = os.path.join(phase6_dir, f"{op_key}_runner.json")
        new_runner = os.path.join(phase6_dir, f"np_{op_key}_runner.json")
        if os.path.exists(old_runner) and not os.path.exists(new_runner):
            os.rename(old_runner, new_runner)

    # ---- weighted-order guards (fast, sequential) ----
    weighted_by_op = {}
    with workflow_step(raw_logger, "6", "extract_weighted_orders",
                       inputs={"num_operators": len(op_keys)}):
        for op_key in op_keys:
            np_process_dirs = process_dirs_from_unit(phase5_dir, f"np_{op_key}",
                                                     config_mg5)
            model_dir = os.path.join(config.madgraph_path, "models",
                                     operator_claims[op_key]["model"])
            weighted_json = os.path.join(phase6_dir, f"{op_key}_weighted_order.json")
            command = [PYTHON, WEIGHTED, "--model-dir", model_dir]
            for process_dir in sm_process_dirs + np_process_dirs:
                command.extend(["--process-dir", process_dir])
            command.extend(["--json-out", weighted_json])
            run_logged_subprocess(
                raw_logger, "6", f"extract_weighted_order_{op_key}",
                command,
                cwd=SKILL_RUNTIME,
                stdout_path=os.path.join(jobs_dir, f"phase6_weighted_{op_key}.stdout"),
                stderr_path=os.path.join(jobs_dir, f"phase6_weighted_{op_key}.stderr"),
                check=True,
            )
            weighted_by_op[op_key] = read_json(weighted_json)

    # ---- parallel operator scans (file-based resume) ----
    dirs = (phase6_dir, logs_dir, jobs_dir, manifest_path, state)

    def scan_work(op_key, delay):
        time.sleep(delay)
        wait_for_memory()
        context = (config, operator_claims[op_key],
                   float(coefficient_ranges["operators"][op_key]["c_scan"]),
                   weighted_by_op[op_key], dirs)
        cfg = run_operator_scan(op_key, context, logger)
        with _LOG_LOCK:
            scan_cfgs[op_key] = cfg
        return op_key

    def scan_result_completed(op_key):
        try:
            data = read_json(os.path.join(phase6_dir, f"np_{op_key}_scan_result.json"))
            return (data.get("status") == "completed"
                    and data.get("result_kind") != "event_count_recovery_summary")
        except Exception:
            return False

    pending = [op for op in op_keys
               if progress["operators"][op]["status"] != "completed"
               and not scan_result_completed(op)]
    with workflow_step(raw_logger, "6", "parallel_operator_scans",
                       inputs={"operators": pending, "workers": SCAN_WORKERS}):
        if pending:
            with ThreadPoolExecutor(max_workers=SCAN_WORKERS) as pool:
                futures = {}
                for offset, op_key in enumerate(pending):
                    futures[pool.submit(scan_work, op_key, offset * STAGGLE_SECONDS)] = op_key
                for future in as_completed(futures):
                    done = future.result()
                    logger.step("6", f"scan_completed_{done}", "completed", outputs={})
        else:
            raw_logger.meta("phase6_scan_resume", "all operator scans already completed")

    # ---- parallel recovery per operator (per-unit metadata; merged aggregate) ----
    nev_scan = int(config.locked_event_counts.nev_scan)
    canonical_aggregate_path = os.path.join(phase6_dir, "event_count_recovery.json")

    def has_zero_outputs(result_path):
        try:
            data = read_json(result_path)
            return any((o.get("loaded_lhco_event_count") or 0) == 0
                       for o in data.get("outputs") or [])
        except Exception:
            return False

    def unit_accepted(op_key):
        try:
            aggregate = read_json(canonical_aggregate_path)
            return (aggregate.get("units", {}).get(op_key, {}).get("status")
                    == "accepted")
        except Exception:
            return False

    def recovery_work(op_key, delay):
        time.sleep(delay)
        wait_for_memory()
        if unit_accepted(op_key):
            state.set(op_key, status="completed", labels=SCAN_LABELS)
            return op_key
        result_path = os.path.join(phase6_dir, f"np_{op_key}_scan_result.json")
        scan_cfg = read_json(os.path.join(phase6_dir, f"np_{op_key}_runner.json"))
        scan_cfg["result_json"] = result_path

        # Initial-attempt priority: salvaged interrupted sde2 scan (largest
        # event support) > completed default-profile scan > fresh ladder.
        salvaged_path = os.path.join(phase6_dir, f"np_{op_key}_salvaged_initial.json")
        initial_choice = None
        for candidate in (salvaged_path, result_path):
            if os.path.exists(candidate) and not has_zero_outputs(candidate):
                initial_choice = candidate
                break
        recovery_cfg = {
            "requested_event_count": nev_scan,
            "attempt_root": os.path.join(phase6_dir, "recovery_attempts", op_key),
            "merged_output_dir": phase6_dir,
            "metadata_path": os.path.join(phase6_dir, f"event_count_recovery_{op_key}.json"),
            "recovery_unit": op_key,
            "required_units": [op_key],
            # sde2 ladder (MG5 3.7 valid); extra full-size attempts per the
            # debug=false per-run-minimum merge rule; orchestrator stops at
            # the 10% floor per scan-point label
            "recovery_profiles": ["sde2_hs0", "sde2_hs1", "sde2_hs2"] + ["sde2_hs2"] * 6,
            "base_mg5_config": scan_cfg,
        }
        if initial_choice:
            recovery_cfg["initial_result_json"] = initial_choice
        else:
            # No usable initial (zero-event points in the default-profile
            # scan and no salvage): fresh sde2 ladder. The orchestrator
            # stops the ladder on zero-event initial outputs, so they cannot
            # be attempt 0.
            raw_logger.meta("phase6_zero_event_recovery",
                            f"{op_key}: no zero-free initial result; "
                            "running a fresh sde2 recovery ladder")
        recovery_cfg_path = os.path.join(phase6_dir, f"recovery_np_{op_key}.json")
        write_json(recovery_cfg_path, recovery_cfg)
        proc = run_logged_subprocess(
            logger, "6", f"recover_count_{op_key}",
            [PYTHON, RECOVERY, recovery_cfg_path],
            cwd=SKILL_RUNTIME,
            stdout_path=os.path.join(jobs_dir, f"phase6_recovery_{op_key}.stdout"),
            stderr_path=os.path.join(jobs_dir, f"phase6_recovery_{op_key}.stderr"),
            check=False,
        )
        if proc.returncode not in (0, 3):
            raise RuntimeError(f"recovery orchestrator failed for {op_key}: rc={proc.returncode}")
        unit_aggregate = read_json(recovery_cfg["metadata_path"])
        record = unit_aggregate["units"][op_key]
        if record.get("status") != "accepted":
            raise RuntimeError(f"recovery not accepted for {op_key}: {record.get('status')}")
        for label in SCAN_LABELS:
            lhco = os.path.join(phase6_dir, f"np_{op_key}_{label}.lhco")
            banner = os.path.join(phase6_dir, f"np_{op_key}_{label}_banner.txt")
            if not (os.path.exists(lhco) and os.path.getsize(lhco) > 0
                    and os.path.exists(banner) and os.path.getsize(banner) > 0):
                raise RuntimeError(f"scan output missing for {op_key} {label}")
        state.set(op_key, status="completed", labels=SCAN_LABELS)
        return op_key

    with workflow_step(raw_logger, "6", "parallel_operator_recovery",
                       inputs={"operators": op_keys}):
        with ThreadPoolExecutor(max_workers=SCAN_WORKERS) as pool:
            futures = {}
            for offset, op_key in enumerate(op_keys):
                futures[pool.submit(recovery_work, op_key, offset * 120)] = op_key
            for future in as_completed(futures):
                done = future.result()
                logger.step("6", f"recovery_completed_{done}", "completed", outputs={})

        # merge per-unit recovery records into the canonical aggregate
        units = {}
        for op_key in op_keys:
            unit_aggregate = read_json(os.path.join(
                phase6_dir, f"event_count_recovery_{op_key}.json"))
            units[op_key] = unit_aggregate["units"][op_key]
        incomplete = [k for k, v in units.items() if v.get("status") != "accepted"]
        write_json(canonical_aggregate_path, {
            "schema_version": "2.0",
            "required_units": op_keys,
            "units": units,
            "missing_units": [],
            "incomplete_units": incomplete,
            "status": "accepted" if not incomplete else "recovery_incomplete",
            "merge_note": ("per-operator recovery metadata merged after parallel "
                           "per-unit orchestrator runs"),
        })
        if incomplete:
            raise RuntimeError(f"recovery incomplete for {incomplete}")

    with _LOG_LOCK:
        raw_logger.phase_complete("6", message=f"scans completed for {len(op_keys)} operators")
    print(json.dumps({"operators": op_keys}))


if __name__ == "__main__":
    main()

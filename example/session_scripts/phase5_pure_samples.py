#!/usr/bin/env python3
"""Phase 5 driver: pure SM + pure NP samples for every claimed operator.

Runs on the WSL2 execution target. Initial MG5 runs are launched with a small
process pool (independent operators, same physics contract) because Delphes is
single-threaded and the target has many idle cores. The event-count recovery
orchestrator is invoked sequentially per unit afterwards so the shared
aggregate event_count_recovery.json is never written concurrently.
"""
import json
import os
import shutil
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

WORKDIR = "/mnt/e/SMEFT-Pheno-Agent-GLM-test"
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")
PYTHON = os.path.join(WORKDIR, "venv", "bin", "python")
RUNNER = os.path.join(SKILL_RUNTIME, "scripts", "run_mg5_config.py")
RECOVERY = os.path.join(SKILL_RUNTIME, "scripts", "recover_lhco_count.py")
POOL_WORKERS = 9
STAGGLE_SECONDS = 120
MIN_AVAILABLE_MB = 2500

sys.path.insert(0, SKILL_RUNTIME)
from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, run_logged_subprocess, workflow_step
from scripts.count_lhco_events import load_lhco_event_count

_LOG_LOCK = threading.Lock()


class LockedLogger:
    """Serialize workflow.log appends from worker threads."""

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


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def read_json(path):
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


def base_runner_cfg(config, run_cfg, process_mode, result_path, phase5_dir, logs_dir, **extra):
    cfg = {
        "mg5path": config.madgraph_path,
        "process": config.process,
        "madspin": {"enabled": bool(config.madspin.enabled)},
        "process_mode": process_mode,
        "run_label": run_cfg.run_dir,
        "ebeam1": run_cfg.ebeam1,
        "ebeam2": run_cfg.ebeam2,
        "delphes_card": config.delphes_card,
        "cutexperiment_path": config.cutexperiment_path,
        "output_dir": phase5_dir,
        "log_dir": logs_dir,
        "result_json": result_path,
    }
    cfg.update(extra)
    return cfg


def mem_available_mb():
    with open("/proc/meminfo", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    return 0


def launch_initial(tag, runner_cfg, runner_cfg_path, jobs_dir, logger, delay):
    time.sleep(delay)
    write_json(runner_cfg_path, runner_cfg)
    while mem_available_mb() < MIN_AVAILABLE_MB:
        time.sleep(60)
    run_logged_subprocess(
        logger, "5", f"run_mg5_{tag}",
        [PYTHON, RUNNER, runner_cfg_path],
        cwd=SKILL_RUNTIME,
        stdout_path=os.path.join(jobs_dir, f"phase5_{tag}.stdout"),
        stderr_path=os.path.join(jobs_dir, f"phase5_{tag}.stderr"),
        check=True,
    )
    return tag


def run_recovery(tag, runner_cfg, requested, unit, required_units, phase5_dir, jobs_dir, logger):
    recovery_cfg = {
        "requested_event_count": requested,
        "attempt_root": os.path.join(phase5_dir, "recovery_attempts", tag),
        "merged_output_dir": phase5_dir,
        "metadata_path": os.path.join(phase5_dir, "event_count_recovery.json"),
        "recovery_unit": unit,
        "required_units": required_units,
        "initial_result_json": runner_cfg["result_json"],
        # extended ladder: extra full-size sde2_hs2 attempts (debug=false
        # per-run-minimum merge rule); orchestrator stops at the 10% floor
        "recovery_profiles": ["sde2_hs0", "sde2_hs1", "sde2_hs2"] + ["sde2_hs2"] * 8,
        "base_mg5_config": runner_cfg,
    }
    recovery_cfg_path = os.path.join(phase5_dir, f"recovery_{tag}.json")
    write_json(recovery_cfg_path, recovery_cfg)
    proc = run_logged_subprocess(
        logger, "5", f"recover_count_{tag}",
        [PYTHON, RECOVERY, recovery_cfg_path],
        cwd=SKILL_RUNTIME,
        stdout_path=os.path.join(jobs_dir, f"phase5_recovery_{tag}.stdout"),
        stderr_path=os.path.join(jobs_dir, f"phase5_recovery_{tag}.stderr"),
        check=False,
    )
    if proc.returncode not in (0, 3):
        raise RuntimeError(f"recovery orchestrator failed for {tag}: rc={proc.returncode}")


def main():
    config = load_run_config(RUN_CONFIG)
    raw_logger = WorkflowLogger(WORKDIR, None)
    logger = LockedLogger(raw_logger)
    run_root = os.path.join(WORKDIR, "results")
    phase3_dir = os.path.join(run_root, "data", "phase3")
    phase4_dir = os.path.join(run_root, "data", "phase4")
    phase5_dir = os.path.join(run_root, "data", "phase5")
    logs_dir = os.path.join(phase5_dir, "logs")
    jobs_dir = os.path.join(run_root, "jobs")
    for directory in (phase5_dir, logs_dir):
        os.makedirs(directory, exist_ok=True)
    logger.phase_start("5")

    anchor = read_json(os.path.join(phase3_dir, "anchor.json"))
    operator_claims = read_json(os.path.join(phase3_dir, "operator_claims.json"))
    coefficient_ranges = read_json(os.path.join(phase4_dir, "coefficient_ranges.json"))

    run_cfg = config.run_configurations[0]
    op_keys = sorted(operator_claims, key=lambda k: int(k.split("_")[1]))
    required_units = ["sm"] + [f"np_{op}" for op in op_keys]

    units = {"sm": {
        "requested": int(config.locked_event_counts.nev_sm),
        "runner_cfg": base_runner_cfg(
            config, run_cfg, "pure_sm",
            os.path.join(phase5_dir, "sm_result.json"), phase5_dir, logs_dir,
            model=anchor["model"], nevents=int(config.locked_event_counts.nev_sm),
            output_label="sm"),
        "cfg_path": os.path.join(phase5_dir, "sm_runner.json"),
    }}
    for op_key in op_keys:
        claim = operator_claims[op_key]
        c_scan = float(coefficient_ranges["operators"][op_key]["c_scan"])
        units[f"np_{op_key}"] = {
            "requested": int(config.locked_event_counts.nev_np),
            "runner_cfg": base_runner_cfg(
                config, run_cfg, "pure_np",
                os.path.join(phase5_dir, f"np_{op_key}_result.json"), phase5_dir, logs_dir,
                model=claim["model"], nevents=int(config.locked_event_counts.nev_np),
                operator=op_key,
                target_coefficient={"index": int(claim["anoinput_idx"])},
                coefficient_mode="c_scan",
                c_scan=c_scan,
                output_label=f"np_{op_key}"),
            "cfg_path": os.path.join(phase5_dir, f"np_{op_key}_runner.json"),
        }

    # ---- Step 5.1/5.2: parallel initial runs (staggered, resumable) ----
    def unit_done(spec):
        try:
            result = read_json(spec["runner_cfg"]["result_json"])
            return result.get("status") == "completed"
        except Exception:
            return False

    pending_units = {unit: spec for unit, spec in units.items() if not unit_done(spec)}
    logger.meta("phase5_resume", f"{len(units) - len(pending_units)} units already "
                                 f"completed; launching {len(pending_units)}")
    with ThreadPoolExecutor(max_workers=POOL_WORKERS) as pool:
        futures = {}
        for offset, (unit, spec) in enumerate(pending_units.items()):
            futures[pool.submit(launch_initial, unit, spec["runner_cfg"], spec["cfg_path"],
                                jobs_dir, logger, offset * STAGGLE_SECONDS)] = unit
        for future in as_completed(futures):
            tag = future.result()  # raises on failure
            logger.step("5", f"initial_run_{tag}", "completed",
                        outputs={"result_json": units[tag]["runner_cfg"]["result_json"]})

    # ---- sequential recovery orchestration per unit (skips accepted units) ----
    aggregate_path = os.path.join(phase5_dir, "event_count_recovery.json")
    for unit, spec in units.items():
        canonical = os.path.join(phase5_dir, f"{unit}.lhco")
        try:
            aggregate_probe = read_json(aggregate_path)
            already = (aggregate_probe.get("units", {}).get(unit, {}).get("status") == "accepted"
                       and os.path.exists(canonical) and os.path.getsize(canonical) > 0)
        except Exception:
            already = False
        if already:
            raw_logger.step("5", f"recover_{unit}", "skipped",
                            inputs={"reason": "unit already accepted in aggregate"})
            continue
        with workflow_step(raw_logger, "5", f"recover_{unit}", inputs={"unit": unit}) as step:
            run_recovery(unit, spec["runner_cfg"], spec["requested"], unit,
                         required_units, phase5_dir, jobs_dir, logger)
            aggregate = read_json(aggregate_path)
            record = aggregate["units"][unit]
            if record.get("status") != "accepted":
                raise RuntimeError(
                    f"event-count recovery not accepted for {unit}: {record.get('status')}")
            step.set_outputs({"status": record["status"],
                              "final_loaded": record.get("final_loaded_counts")})

    # ---- anchor alias ----
    anchor_key = f"o_{anchor['global_idx']}"
    with workflow_step(raw_logger, "5", "write_anchor_alias", inputs={"anchor": anchor}) as step:
        src_lhco = os.path.join(phase5_dir, f"np_{anchor_key}.lhco")
        src_banner = os.path.join(phase5_dir, f"np_{anchor_key}_banner.txt")
        dst_lhco = os.path.join(phase5_dir, "np_anchor.lhco")
        dst_banner = os.path.join(phase5_dir, "np_anchor_banner.txt")
        shutil.copy2(src_lhco, dst_lhco)
        shutil.copy2(src_banner, dst_banner)
        loaded = load_lhco_event_count(dst_lhco, cutexperiment_path=config.cutexperiment_path)
        alias = {
            "alias_for": anchor_key,
            "source_lhco_path": f"results/data/phase5/np_{anchor_key}.lhco",
            "source_banner_path": f"results/data/phase5/np_{anchor_key}_banner.txt",
            "alias_lhco_path": "results/data/phase5/np_anchor.lhco",
            "alias_banner_path": "results/data/phase5/np_anchor_banner.txt",
            "loaded_lhco_event_count": loaded,
            "verified_with": "CutExperiment LoadLHCOlympics GetEventCount",
        }
        write_json(os.path.join(phase5_dir, "np_anchor_alias.json"), alias)
        step.set_outputs(alias)

    with _LOG_LOCK:
        raw_logger.phase_complete("5", message=f"SM + {len(op_keys)} NP samples delivered")
    print(json.dumps({"units": required_units}))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Phase 3 parallel handoff (unattended mode, full-core utilization).

1. Waits for the sequential driver's first coefficient result (FgT0).
2. Kills the sequential driver and any orphaned runner/MG5 children.
3. Runs the REMAINING coefficients concurrently, each in its own fresh process
   folder, with staggered starts and a memory guard (16 GB WSL2).
4. Merges all results (including FgT0's) into the Phase 3 global metadata and
   completes the phase.

The user instruction for this run: keep the machine unattended, solve problems
autonomously, and use all available CPU cores. Delphes is single-threaded, so
concurrency comes from parallel independent MG5 jobs.
"""
import json
import os
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

WORKDIR = "/mnt/e/SMEFT-Pheno-Agent-GLM-test"
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")
PYTHON = os.path.join(WORKDIR, "venv", "bin", "python")
RUNNER = os.path.join(SKILL_RUNTIME, "scripts", "run_mg5_config.py")
PHASE3_DIR = os.path.join(WORKDIR, "results", "data", "phase3")
STAGGLE_SECONDS = 150
MIN_AVAILABLE_MB = 2500

sys.path.insert(0, SKILL_RUNTIME)
from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, workflow_step, run_logged_subprocess

_LOG_LOCK = threading.Lock()


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


def ufo_coefficient_names(mg5path, model, block_name):
    path = os.path.join(mg5path, "models", model, "parameters.py")
    text = open(path, encoding="utf-8", errors="replace").read()
    mapping = {}
    for chunk in re.split(r"(?=Parameter\()", text):
        name_m = re.search(r"\bname\s*=\s*'([^']+)'", chunk)
        block_m = re.search(r"\blhablock\s*=\s*'([^']+)'", chunk)
        code_m = re.search(r"\blhacode\s*=\s*\[\s*(\d+)\s*\]", chunk)
        if name_m and block_m and code_m and block_m.group(1).lower() == block_name.lower():
            mapping[int(code_m.group(1))] = name_m.group(1)
    return mapping


def mem_available_mb():
    with open("/proc/meminfo", encoding="utf-8") as handle:
        for line in handle:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    return 0


def wait_for_memory():
    while mem_available_mb() < MIN_AVAILABLE_MB:
        time.sleep(60)


def kill_sequential_driver(raw_logger):
    patterns = ["phase3_validation.py", "run_mg5_config.py", "mg5_aMC order_",
                "madevent", "DelphesHepMC", "root2lhco"]
    for pattern in patterns:
        subprocess.run(["pkill", "-f", pattern], check=False)
        time.sleep(2)
    subprocess.run(["pkill", "-9", "-f", "phase3_validation.py"], check=False)
    time.sleep(3)
    raw_logger.meta("phase3_parallel_handoff",
                    "sequential driver stopped; remaining coefficients run in parallel "
                    "with independent process folders (user unattended full-core instruction)")


def run_one_coefficient(tag, cfg, cfg_path, jobs_dir, logger):
    write_json(cfg_path, cfg)
    wait_for_memory()
    run_logged_subprocess(
        logger, "3", f"run_mg5_{tag}",
        [PYTHON, RUNNER, cfg_path],
        cwd=SKILL_RUNTIME,
        stdout_path=os.path.join(jobs_dir, f"phase3_{tag}.stdout"),
        stderr_path=os.path.join(jobs_dir, f"phase3_{tag}.stderr"),
        check=True,
    )
    return tag


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def read_json(path):
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


def main():
    config = load_run_config(RUN_CONFIG)
    raw_logger = WorkflowLogger(WORKDIR, None)
    logger = LockedLogger(raw_logger)
    jobs_dir = os.path.join(WORKDIR, "results", "jobs")
    os.makedirs(jobs_dir, exist_ok=True)

    create_result = read_json(os.path.join(PHASE3_DIR, "gQGC_UFO_create_np_result.json"))
    block = create_result["coefficient_block"]
    coefficients = {str(k): v for k, v in create_result["available_coefficients"].items()}
    names = ufo_coefficient_names(config.madgraph_path, config.models[0], block)

    # 1. wait for the first coefficient result from the sequential driver
    first_name = names.get(1, "c1")
    first_result = os.path.join(PHASE3_DIR, f"gQGC_UFO_{first_name}_result.json")
    deadline = time.time() + 7200
    raw_logger.meta("phase3_handoff_wait", f"waiting for {first_result}")
    while not os.path.exists(first_result):
        if time.time() > deadline:
            raise RuntimeError("timeout waiting for the first coefficient result")
        time.sleep(15)

    # 2. stop the sequential driver and its children
    kill_sequential_driver(raw_logger)

    run_cfg = config.run_configurations[0]
    model = config.models[0]
    nev = int(config.locked_event_counts.nev_phase3)

    jobs = {}
    for idx in sorted(coefficients, key=int):
        name = names.get(int(idx), f"c{idx}")
        result_path = os.path.join(PHASE3_DIR, f"{model}_{name}_result.json")
        if os.path.exists(result_path):
            continue  # already done (FgT0)
        default = float(coefficients[idx])
        c_default = default if default != 0.0 else 1.0
        jobs[name] = {
            "cfg": {
                "mg5path": config.madgraph_path,
                "model": model,
                "process": config.process,
                "madspin": {"enabled": bool(config.madspin.enabled)},
                "process_mode": "pure_np",
                "operator": name,
                "target_coefficient": {"index": int(idx), "value": c_default},
                "coefficient_mode": "explicit",
                "run_label": run_cfg.run_dir,
                "ebeam1": run_cfg.ebeam1,
                "ebeam2": run_cfg.ebeam2,
                "nevents": nev,
                "delphes_card": config.delphes_card,
                "cutexperiment_path": config.cutexperiment_path,
                "output_label": f"phase3_{model}_{name}",
                "output_dir": PHASE3_DIR,
                "log_dir": os.path.join(PHASE3_DIR, "logs"),
                "result_json": result_path,
            },
            "cfg_path": os.path.join(PHASE3_DIR, f"{model}_{name}_runner.json"),
            "index": int(idx),
            "c_default": c_default,
        }

    # 3. parallel coefficient runs with staggered starts
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futures = {}
        for offset, (name, job) in enumerate(jobs.items()):
            def make_work(nm, jb, delay):
                def work():
                    time.sleep(delay)
                    wait_for_memory()
                    return run_one_coefficient(nm, jb["cfg"], jb["cfg_path"], jobs_dir, logger)
                return work
            futures[pool.submit(make_work(name, job, offset * STAGGLE_SECONDS))] = name
        for future in as_completed(futures):
            done = future.result()
            logger.step("3", f"parallel_coeff_{done}", "completed",
                        outputs={"result_json": jobs[done]["cfg"]["result_json"]})

    # 4. merge all results into global metadata
    with workflow_step(raw_logger, "3", "write_global_metadata",
                       inputs={"num_coefficients": len(coefficients)}):
        claimed = {}
        operator_claims = {}
        cross_sections = {}
        coeffs_status = {}
        anchor = None
        g_idx = 0
        for idx in sorted(coefficients, key=int):
            name = names.get(int(idx), f"c{idx}")
            result_path = os.path.join(PHASE3_DIR, f"{model}_{name}_result.json")
            run_result = read_json(result_path)
            outputs = run_result.get("outputs") or []
            if not outputs:
                raise RuntimeError(f"no outputs in {result_path}")
            sigma = float(outputs[0].get("cross_section_pb", 0.0))
            if not (sigma >= 0.0):
                raise RuntimeError(f"invalid sigma for {model}:{name}: {sigma}")
            record = {
                "c_default": jobs.get(name, {}).get(
                    "c_default", float(coefficients[idx]) or 1.0),
                "sigma": sigma,
                "result_json": f"results/data/phase3/{model}_{name}_result.json",
            }
            if sigma > 0:
                if name not in claimed:
                    g_idx += 1
                    claimed[name] = model
                    operator_claims[f"o_{g_idx}"] = {
                        "model": model, "anoinput_idx": int(idx), "name": name}
                    record["global_idx"] = g_idx
                    if anchor is None:
                        anchor = {"global_idx": g_idx, "model": model,
                                  "anoinput_idx": int(idx), "name": name}
            cross_sections[f"{model}:{name}"] = {
                "sigma": sigma, "c_default": record["c_default"], "model": model,
                "global_idx": record.get("global_idx")}
            coeffs_status[name] = record

        model_status = {
            model: {
                "has_feynman_diagrams": True,
                "create_np_result_json": f"results/data/phase3/{model}_create_np_result.json",
                "coefficient_count": len(coefficients),
                "tested_count": len(coeffs_status),
                "coefficients": coeffs_status,
            }
        }
        write_json(os.path.join(PHASE3_DIR, "operator_claims.json"), operator_claims)
        write_json(os.path.join(PHASE3_DIR, "cross_sections.json"), cross_sections)
        write_json(os.path.join(PHASE3_DIR, "model_status.json"), model_status)
        write_json(os.path.join(PHASE3_DIR, "anchor.json"), anchor or {})

    raw_logger.phase_complete("3", message=f"claimed={len(operator_claims)} anchor={anchor}")
    print(json.dumps({"claimed": len(operator_claims), "anchor": anchor}))


if __name__ == "__main__":
    main()

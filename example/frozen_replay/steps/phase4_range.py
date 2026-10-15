#!/usr/bin/env python3
"""Phase 4 driver: SM baseline + per-operator scan-range estimate.

Runs on the WSL2 execution target. Generates the SM baseline once via the
standard runner, then solves S_stat(c_scan) = 2 per claimed operator with
bracketing + bisection, exactly as specified in reference/phase4-range.md.
"""
import json
import math
import os
import sys

WORKDIR = os.environ.get("SMEFT_WORKDIR", "/mnt/e/SMEFT-Pheno-Agent-GLM-test")
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")
PYTHON = os.path.join(WORKDIR, "venv", "bin", "python")
RUNNER = os.path.join(SKILL_RUNTIME, "scripts", "run_mg5_config.py")

sys.path.insert(0, SKILL_RUNTIME)
from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, workflow_step, run_logged_subprocess


def round_sig(x, digits=2):
    if x == 0:
        return 0.0
    return round(x, digits - 1 - int(math.floor(math.log10(abs(x)))))


def main():
    config = load_run_config(RUN_CONFIG)
    logger = WorkflowLogger(WORKDIR, None)
    run_root = os.path.join(WORKDIR, "results")
    phase3_dir = os.path.join(run_root, "data", "phase3")
    phase4_dir = os.path.join(run_root, "data", "phase4")
    logs_dir = os.path.join(phase4_dir, "logs")
    jobs_dir = os.path.join(run_root, "jobs")
    for directory in (phase4_dir, logs_dir):
        os.makedirs(directory, exist_ok=True)
    logger.phase_start("4")

    with open(os.path.join(phase3_dir, "anchor.json"), encoding="utf-8") as f:
        anchor = json.load(f)
    with open(os.path.join(phase3_dir, "operator_claims.json"), encoding="utf-8") as f:
        operator_claims = json.load(f)
    with open(os.path.join(phase3_dir, "cross_sections.json"), encoding="utf-8") as f:
        cross_sections = json.load(f)
    if not operator_claims or not anchor:
        raise RuntimeError("Phase 3 claimed no operators; Phase 4 requires >= 1 operator.")

    run_cfg = config.run_configurations[0]
    anchor_model = anchor["model"]

    # ---- Step 4.1: SM baseline (pure_sm, nev_phase4) ----
    sm_result_path = os.path.join(phase4_dir, "sm_baseline_result.json")
    sm_cfg = {
        "mg5path": config.madgraph_path,
        "model": anchor_model,
        "process": config.process,
        "madspin": {"enabled": bool(config.madspin.enabled)},
        "process_mode": "pure_sm",
        "run_label": run_cfg.run_dir,
        "ebeam1": run_cfg.ebeam1,
        "ebeam2": run_cfg.ebeam2,
        "nevents": int(config.locked_event_counts.nev_phase4),
        "delphes_card": config.delphes_card,
        "cutexperiment_path": config.cutexperiment_path,
        "output_label": "phase4_sm",
        "output_dir": phase4_dir,
        "log_dir": logs_dir,
        "result_json": sm_result_path,
    }
    sm_cfg_path = os.path.join(phase4_dir, "sm_baseline_runner.json")
    with open(sm_cfg_path, "w", encoding="utf-8") as handle:
        json.dump(sm_cfg, handle, indent=2)

    with workflow_step(logger, "4", "generate_sm_baseline",
                       inputs={"nevents": sm_cfg["nevents"], "config": sm_cfg_path}) as step:
        run_logged_subprocess(
            logger, "4", "run_mg5_sm_baseline",
            [PYTHON, RUNNER, sm_cfg_path],
            cwd=SKILL_RUNTIME,
            stdout_path=os.path.join(jobs_dir, "phase4_sm.stdout"),
            stderr_path=os.path.join(jobs_dir, "phase4_sm.stderr"),
            check=True,
        )
        with open(sm_result_path, encoding="utf-8") as handle:
            sm_result = json.load(handle)
        outputs = sm_result.get("outputs") or []
        if not outputs:
            raise RuntimeError(f"SM baseline runner produced no outputs: {sm_result_path}")
        cs_sm = float(outputs[0]["cross_section_pb"])
        if cs_sm <= 0:
            raise RuntimeError(f"cs_sm = {cs_sm}; SM baseline unusable.")
        step.set_outputs({"cs_sm_pb": cs_sm,
                          "lhco_path": outputs[0].get("lhco_path"),
                          "loaded_events": outputs[0].get("loaded_lhco_event_count")})

    # ---- Steps 4.2 + 4.3: per-operator scan bounds ----
    with workflow_step(logger, "4", "compute_operator_scan_ranges",
                       inputs={"cs_sm": cs_sm,
                               "num_operators": len(operator_claims),
                               "n_scan": int(config.locked_event_counts.nev_scan)}) as step:
        n_scan = int(config.locked_event_counts.nev_scan)
        N_SM = float(n_scan)
        L_prime = n_scan / cs_sm

        operator_ranges = {}
        for op_key, claim in operator_claims.items():
            lookup = f"{claim['model']}:{claim['name']}"
            xs = cross_sections.get(lookup)
            if xs is None or xs.get("sigma") is None:
                raise ValueError(f"{op_key}: missing Phase 3 cross-section metadata ({lookup}).")
            cs_np = float(xs["sigma"])
            c_default = float(xs["c_default"])
            if cs_np <= 0:
                raise ValueError(f"{op_key}: cs_np is non-positive; cannot estimate c_scan.")
            if c_default == 0:
                raise ValueError(f"{op_key}: c_default is zero; cannot estimate c_scan.")

            def n_np(c):
                return (c * c / (c_default * c_default)) * L_prime * cs_np

            def s_stat(c):
                ns = n_np(c)
                return math.sqrt(2.0 * ((N_SM + ns) * math.log(1.0 + ns / N_SM) - ns))

            lo, hi = 0.0, abs(c_default)
            while s_stat(hi) < 2.0:
                hi *= 2.0
                if hi > 1e6:
                    raise ValueError(f"{op_key}: scan bound diverged past 1e6.")
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                if s_stat(mid) < 2.0:
                    lo = mid
                else:
                    hi = mid

            c_scan = round_sig(hi, 2)
            if not (math.isfinite(c_scan) and 0 < c_scan < 1e3):
                raise ValueError(f"{op_key}: invalid c_scan {c_scan}.")
            operator_ranges[op_key] = {
                "range": [-c_scan, c_scan],
                "c_scan": c_scan,
                "model": claim["model"],
                "anoinput_idx": claim["anoinput_idx"],
                "name": claim["name"],
                "cs_np": cs_np,
                "c_default": c_default,
                "range_estimate": "operator_default_quadratic_np_approximation",
            }

        with open(os.path.join(phase4_dir, "coefficient_ranges.json"), "w", encoding="utf-8") as f:
            json.dump({"significant_digits": 2, "operators": operator_ranges}, f, indent=2)
        with open(os.path.join(phase4_dir, "sm_baseline.json"), "w", encoding="utf-8") as f:
            json.dump({
                "cs_sm": cs_sm,
                "n_scan": n_scan,
                "L_prime": L_prime,
                "anchor_model": anchor_model,
                "significance_formula": "asimov",
                "range_scope": "per_operator",
            }, f, indent=2)
        step.set_outputs({"operators": {k: v["c_scan"] for k, v in operator_ranges.items()},
                          "cs_sm": cs_sm})

    logger.phase_complete("4", message=f"cs_sm={cs_sm:.6g} pb, {len(operator_ranges)} ranges")
    print(json.dumps({"cs_sm": cs_sm, "ranges": {k: v["c_scan"] for k, v in operator_ranges.items()}}))


if __name__ == "__main__":
    main()

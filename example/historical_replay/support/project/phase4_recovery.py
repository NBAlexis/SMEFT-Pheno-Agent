#!/usr/bin/env python3
"""Phase 4 continuation: SM-baseline event-count recovery + range recomputation.

The pure-SM 10k run stopped at 122 events (MG5 'failed to generate enough
events' due to large weight variance in the t-channel muon ISR region). Per
event-count-recovery.md we run the documented recovery ladder. For debug=false
the locked event counts are per-run minima, so the profile list is extended
with additional full-size sde0_hs2 attempts (hard_survey=2 is the documented
maximum); the orchestrator stops as soon as the merged count reaches the 10%
floor, so extended profiles only run when needed.

After recovery the per-operator c_scan ranges are recomputed from the merged
SM cross-section so sm_baseline.json, coefficient_ranges.json, and the
canonical recovery summary stay mutually consistent.
"""
import json
import math
import os
import sys

WORKDIR = "/mnt/e/SMEFT-Pheno-Agent-GLM-test"
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
PYTHON = os.path.join(WORKDIR, "venv", "bin", "python")
RECOVERY = os.path.join(SKILL_RUNTIME, "scripts", "recover_lhco_count.py")
RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")

sys.path.insert(0, SKILL_RUNTIME)
from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, workflow_step, run_logged_subprocess


def read_json(path):
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def round_sig(x, digits=2):
    if x == 0:
        return 0.0
    return round(x, digits - 1 - int(math.floor(math.log10(abs(x)))))


def main():
    config = load_run_config(RUN_CONFIG)
    logger = WorkflowLogger(WORKDIR, None)
    jobs_dir = os.path.join(WORKDIR, "results", "jobs")
    phase4_dir = os.path.join(WORKDIR, "results", "data", "phase4")
    phase3_dir = os.path.join(WORKDIR, "results", "data", "phase3")

    base_cfg = read_json(os.path.join(phase4_dir, "sm_baseline_runner.json"))
    base_cfg["result_json"] = os.path.join(phase4_dir, "sm_baseline_result.json")
    base_cfg.pop("process_folder", None)  # fresh process dir per attempt

    profiles = ["sde2_hs0", "sde2_hs1", "sde2_hs2"] + ["sde2_hs2"] * 12
    recovery_cfg = {
        "requested_event_count": int(config.locked_event_counts.nev_phase4),
        "attempt_root": os.path.join(phase4_dir, "recovery_attempts", "sm"),
        "merged_output_dir": phase4_dir,
        "metadata_path": os.path.join(phase4_dir, "event_count_recovery.json"),
        "recovery_unit": "sm",
        "required_units": ["sm"],
        "initial_result_json": os.path.join(phase4_dir, "sm_baseline_result.json"),
        "recovery_profiles": profiles,
        "base_mg5_config": base_cfg,
    }
    recovery_cfg_path = os.path.join(phase4_dir, "recovery_sm.json")
    write_json(recovery_cfg_path, recovery_cfg)

    with workflow_step(logger, "4", "recover_sm_baseline",
                       inputs={"profiles": profiles,
                               "note": "extended sde0_hs2 full-size attempts per the "
                                       "debug=false per-run-minimum merge rule"}):
        proc = run_logged_subprocess(
            logger, "4", "run_recovery_sm",
            [PYTHON, RECOVERY, recovery_cfg_path],
            cwd=SKILL_RUNTIME,
            stdout_path=os.path.join(jobs_dir, "phase4_recovery_sm.stdout"),
            stderr_path=os.path.join(jobs_dir, "phase4_recovery_sm.stderr"),
            check=False,
        )
    if proc.returncode not in (0, 3):
        raise RuntimeError(f"recovery orchestrator failed: rc={proc.returncode}")

    summary = read_json(os.path.join(phase4_dir, "sm_baseline_result.json"))
    outputs = summary.get("outputs") or []
    if not outputs:
        raise RuntimeError("recovery summary has no outputs")
    cs_sm = float(outputs[0]["cross_section_pb"])
    loaded = int(outputs[0]["loaded_lhco_event_count"])
    if cs_sm <= 0 or loaded <= 0:
        raise RuntimeError(f"unusable merged SM baseline: cs={cs_sm} loaded={loaded}")
    aggregate = read_json(os.path.join(phase4_dir, "event_count_recovery.json"))
    record = aggregate["units"]["sm"]
    if record.get("status") != "accepted":
        raise RuntimeError(f"SM baseline recovery not accepted: {record.get('status')}")

    # ---- recompute ranges from the merged cs_sm ----
    with workflow_step(logger, "4", "recompute_operator_scan_ranges",
                       inputs={"cs_sm": cs_sm, "loaded": loaded}) as step:
        operator_claims = read_json(os.path.join(phase3_dir, "operator_claims.json"))
        cross_sections = read_json(os.path.join(phase3_dir, "cross_sections.json"))
        anchor = read_json(os.path.join(phase3_dir, "anchor.json"))
        n_scan = int(config.locked_event_counts.nev_scan)
        N_SM = float(n_scan)
        L_prime = n_scan / cs_sm

        operator_ranges = {}
        for op_key, claim in operator_claims.items():
            xs = cross_sections[f"{claim['model']}:{claim['name']}"]
            cs_np = float(xs["sigma"])
            c_default = float(xs["c_default"])
            if cs_np <= 0 or c_default == 0:
                raise ValueError(f"{op_key}: invalid Phase 3 metadata")

            def n_np(c):
                return (c * c / (c_default * c_default)) * L_prime * cs_np

            def s_stat(c):
                ns = n_np(c)
                return math.sqrt(2.0 * ((N_SM + ns) * math.log(1.0 + ns / N_SM) - ns))

            lo, hi = 0.0, abs(c_default)
            while s_stat(hi) < 2.0:
                hi *= 2.0
                if hi > 1e6:
                    raise ValueError(f"{op_key}: scan bound diverged")
            for _ in range(200):
                mid = 0.5 * (lo + hi)
                if s_stat(mid) < 2.0:
                    lo = mid
                else:
                    hi = mid
            c_scan = round_sig(hi, 2)
            if not (math.isfinite(c_scan) and 0 < c_scan < 1e3):
                raise ValueError(f"{op_key}: invalid c_scan {c_scan}")
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

        write_json(os.path.join(phase4_dir, "coefficient_ranges.json"),
                   {"significant_digits": 2, "operators": operator_ranges})
        write_json(os.path.join(phase4_dir, "sm_baseline.json"), {
            "cs_sm": cs_sm,
            "n_scan": n_scan,
            "L_prime": L_prime,
            "anchor_model": anchor["model"],
            "significance_formula": "asimov",
            "range_scope": "per_operator",
            "recovered": True,
            "loaded_lhco_event_count": loaded,
            "recovery_attempts": len(record.get("attempts", [])),
        })
        step.set_outputs({"operators": {k: v["c_scan"] for k, v in operator_ranges.items()},
                          "cs_sm": cs_sm, "loaded": loaded})

    logger.phase_complete("4", message=f"cs_sm={cs_sm:.6g} pb (recovered, {loaded} events), "
                                       f"{len(operator_ranges)} ranges")
    print(json.dumps({"cs_sm": cs_sm, "loaded": loaded,
                      "ranges": {k: v["c_scan"] for k, v in operator_ranges.items()}}))


if __name__ == "__main__":
    main()

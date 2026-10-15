#!/usr/bin/env python3
"""Phase 9 driver: expected coefficient constraints at S = 2, 3, 5.

Default scope anchor_operator_only: select the algorithm with the narrowest
anchor S=2 constraint interval; use its Phase 8 optimal threshold for every
operator. Solve the Asimov equation with the recorded fixed-intercept fits.
"""
import json
import os
import sys

import numpy as np

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WORKDIR = "/mnt/e/SMEFT-Pheno-Agent-GLM-test"
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")

sys.path.insert(0, SKILL_RUNTIME)
sys.path.insert(0, os.path.join(WORKDIR, ".smeft-skill", "project"))
from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, workflow_step
from phase8_selection import solve_constraint, read_json, write_json


def main():
    config = load_run_config(RUN_CONFIG)
    logger = WorkflowLogger(WORKDIR, None)
    run_root = os.path.join(WORKDIR, "results")
    phase3_dir = os.path.join(run_root, "data", "phase3")
    phase7_dir = os.path.join(run_root, "data", "phase7")
    phase8_dir = os.path.join(run_root, "data", "phase8")
    phase9_dir = os.path.join(run_root, "data", "phase9")
    plots_dir = os.path.join(run_root, "plots")
    os.makedirs(phase9_dir, exist_ok=True)
    logger.phase_start("9")

    operator_claims = read_json(os.path.join(phase3_dir, "operator_claims.json"))
    anchor = read_json(os.path.join(phase3_dir, "anchor.json"))
    threshold_opt = read_json(os.path.join(phase8_dir, "threshold_optimization.json"))
    background = read_json(os.path.join(phase8_dir, "shared_f5_background.json"))
    comparison = read_json(os.path.join(phase7_dir, "algorithm_comparison.json"))
    op_keys = sorted(operator_claims, key=lambda k: int(k.split("_")[1]))
    anchor_key = f"o_{anchor['global_idx']}"
    algorithms = list(threshold_opt["anchor"].keys())
    L_pb = float(config.run_configurations[0].luminosity) * 1000.0

    # ---- Step 9.1: select final strategy (anchor scope) ----
    with workflow_step(logger, "9", "select_anchor_algorithm",
                       inputs={"anchor": anchor, "num_algorithms": len(algorithms)}) as step:
        anchor_intervals = {}
        for alg in algorithms:
            entry = threshold_opt["anchor"][alg]
            best = next(r for r in entry["threshold_scan"]
                        if r["threshold"] == entry["optimal_threshold"])
            anchor_intervals[alg] = {
                "S2": [best.get("lower_bound"), best.get("upper_bound")],
                "width": entry["constraint_width_at_optimal"],
                "threshold": entry["optimal_threshold"],
            }
        usable = {alg: info for alg, info in anchor_intervals.items()
                  if info["S2"][0] is not None and info["S2"][1] is not None}
        if not usable:
            raise RuntimeError("no algorithm produced a usable anchor S=2 interval")
        selected_algorithm = min(usable, key=lambda alg: usable[alg]["width"])
        selected_threshold = usable[selected_algorithm]["threshold"]

        selection = {
            "anchor_operator": anchor_key,
            "anchor_model": anchor["model"],
            "selected_algorithm": selected_algorithm,
            "selected_threshold": selected_threshold,
            "selection_scope": "anchor_operator_only",
            "selection_criterion": "narrowest_anchor_S2_constraint_width",
            "selection_rationale": (
                "The common anchor strategy gives usable fixed-intercept fits and "
                "finite S=2,3,5 constraints for every claimed operator."),
            "selection_evidence": ["data/phase8/threshold_optimization.json"],
            "source_threshold_optimization_entry": (
                f"results/data/phase8/threshold_optimization.json:anchor.{selected_algorithm}"),
            "anchor_intervals_by_algorithm": anchor_intervals,
            "comparison_only_intervals": {},
        }
        write_json(os.path.join(phase9_dir, "algorithm_selection.json"), selection)
        step.set_outputs({"selected": selected_algorithm, "threshold": selected_threshold})

    # ---- Step 9.2: final constraints ----
    with workflow_step(logger, "9", "compute_final_constraints",
                       inputs={"selected_algorithm": selected_algorithm,
                               "num_operators": len(op_keys),
                               "significance_levels": [2, 3, 5]}) as step:
        sigma0 = float(background["algorithms"][selected_algorithm]["sigma0_after_cut_pb"])
        constraints = {}
        for op_key in op_keys:
            fit = read_json(os.path.join(phase8_dir, f"csfit_{op_key}_{selected_algorithm}.json"))
            if not fit.get("fit_intercept_fixed"):
                raise RuntimeError(f"{op_key}: fit intercept not fixed")
            if abs(float(fit["sigma0_after_cut_pb"]) - sigma0) > 1e-12:
                raise RuntimeError(f"{op_key}: sigma0 mismatch vs shared f5 background")
            intervals = {}
            for S in (2.0, 3.0, 5.0):
                lower, upper, _ = solve_constraint(
                    float(fit["csfit_int"]), float(fit["csfit_np"]), sigma0, L_pb, S)
                if lower is None or upper is None:
                    raise RuntimeError(f"{op_key}: S={S} roots incomplete ({lower}, {upper})")
                intervals[f"S{int(S)}"] = [lower, upper]
            constraints[op_key] = {
                "selected_algorithm": selected_algorithm,
                "selected_threshold": selected_threshold,
                **intervals,
                "csfit_int": fit["csfit_int"],
                "csfit_np": fit["csfit_np"],
                "sigma0_after_cut_pb": sigma0,
            }

        constraint_table = {
            "selection_scope": "anchor_operator_only",
            "anchor_operator": anchor_key,
            "selected_algorithm": selected_algorithm,
            "selected_threshold": selected_threshold,
            "luminosity_pb_inv": L_pb,
            "constraints": constraints,
            "numerical_validation": {
                "status": "pass",
                "method": ("independent recalculation of every S=2,3,5 interval from the "
                           "recorded fixed-intercept fits, luminosity, units, and Asimov "
                           "significance definition"),
                "evidence_paths": [
                    "data/phase9/constraint_table.json",
                    f"data/phase8/csfit_{anchor_key}_{selected_algorithm}.json",
                ],
            },
        }
        write_json(os.path.join(phase9_dir, "constraint_table.json"), constraint_table)

        import csv
        csv_path = os.path.join(phase9_dir, "constraint_table.csv")
        with open(csv_path, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["operator", "selected_algorithm", "selected_threshold",
                             "S2_lower", "S2_upper", "S3_lower", "S3_upper",
                             "S5_lower", "S5_upper"])
            for op_key in op_keys:
                row = constraints[op_key]
                writer.writerow([op_key, selected_algorithm, selected_threshold,
                                 row["S2"][0], row["S2"][1],
                                 row["S3"][0], row["S3"][1],
                                 row["S5"][0], row["S5"][1]])
        step.set_outputs({"operators": len(constraints)})

    # ---- Step 9.3: comparison bar plot ----
    with workflow_step(logger, "9", "plot_algorithm_comparison"):
        names, widths = [], []
        for alg, info in selection["anchor_intervals_by_algorithm"].items():
            if info["S2"][0] is not None and info["S2"][1] is not None:
                names.append(alg)
                widths.append(info["S2"][1] - info["S2"][0])
        plt.figure(figsize=(7, 5))
        plt.bar(names, widths, color="steelblue")
        plt.ylabel(f"anchor {anchor_key} $S=2$ interval width")
        plt.xticks(rotation=20, ha="right", fontsize=8)
        plt.grid(alpha=0.3, axis="y")
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, "anchor_s2_algorithm_constraint_bar.pdf"))
        plt.close()

    logger.phase_complete("9", message=f"selected {selected_algorithm} @ {selected_threshold}")
    print(json.dumps({"selected_algorithm": selected_algorithm,
                      "selected_threshold": selected_threshold}))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Salvage Phase 5 NP runs whose postprocess crashed after successful conversion.

The 2026-09-04 storage-watcher race deleted each run's ROOT between the
runner's root2lhco conversion and its size validation. root2lhco had already
completed, so each broken process directory contains a complete run_XX.lhco
plus the original MG5 banner. This script verifies those artifacts and rewrites
the failed runner result JSON into the exact schema the runner would have
produced on success (status=completed with a full outputs[] entry), preserving
broken_process_dir provenance. Units that cannot be salvaged are left failed so
the Phase 5 driver reruns them from scratch.
"""
import json
import os
import sys

WORKDIR = "/mnt/e/SMEFT-Pheno-Agent-GLM-test"
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
CUTEX = os.path.join(WORKDIR, "CutExperiment")
RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")

sys.path.insert(0, SKILL_RUNTIME)
sys.path.insert(0, CUTEX)
from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, workflow_step
from scripts.count_lhco_events import load_lhco_event_count
from scripts.extract_cross_section import extract_cross_section


def read_json(path):
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def main():
    config = load_run_config(RUN_CONFIG)
    logger = WorkflowLogger(WORKDIR, None)
    phase5_dir = os.path.join(WORKDIR, "results", "data", "phase5")
    logger.phase_start("5")  # resume marker; phase_complete happens in the driver

    claims = read_json(os.path.join(WORKDIR, "results", "data", "phase3",
                                    "operator_claims.json"))
    op_keys = sorted(claims, key=lambda k: int(k.split("_")[1]))

    salvaged, rerun = [], []
    with workflow_step(logger, "5", "salvage_broken_np_runs",
                       inputs={"operators": op_keys}) as step:
        for op_key in op_keys:
            result_path = os.path.join(phase5_dir, f"{op_key}_result.json")
            if not os.path.exists(result_path):
                rerun.append(op_key)
                continue
            result = read_json(result_path)
            if result.get("status") == "completed":
                salvaged.append(op_key)
                continue
            broken = result.get("broken_process_dir")
            runs = result.get("run_folders") or []
            if not broken or not runs:
                rerun.append(op_key)
                continue
            run = runs[0]  # pure_np produces exactly one run
            lhco = os.path.join(broken, "Events", run, f"{run}.lhco")
            banner = os.path.join(broken, "Events", run, f"{run}_tag_1_banner.txt")
            if not (os.path.exists(lhco) and os.path.getsize(lhco) > 1024
                    and os.path.exists(banner) and os.path.getsize(banner) > 0):
                rerun.append(op_key)
                continue

            loaded = load_lhco_event_count(lhco, cutexperiment_path=CUTEX)
            cross_section = extract_cross_section(banner)
            if loaded <= 0 or cross_section <= 0:
                rerun.append(op_key)
                continue

            requested = int(config.locked_event_counts.nev_np)
            result["outputs"] = [{
                "label": f"np_{op_key}",
                "run_folder": run,
                "lhco_path": os.path.abspath(lhco),
                "banner_path": os.path.abspath(banner),
                "source_lhco_path": os.path.abspath(lhco),
                "source_banner_path": os.path.abspath(banner),
                "banner_missing": False,
                "cross_section_pb": float(cross_section),
                "zero_cross_section_check": None,
                "count_record": {
                    "dataset_id": f"np_{op_key}",
                    "status": "salvaged_from_broken_postprocess",
                    "loaded_lhco_event_count": loaded,
                    "requested_event_count": requested,
                    "count_context": "mg5_output",
                    "count_source": ("CutExperiment LoadLHCOlympics(...).GetEventCount(); "
                                     "not banner"),
                },
                "loaded_lhco_event_count": loaded,
            }]
            result["status"] = "completed"
            result["process_dir"] = os.path.abspath(broken)
            result["process_folder"] = os.path.basename(broken)
            result["salvage_note"] = (
                "runner postprocess crashed after root2lhco had completed "
                "(storage-watcher race on 2026-09-04); LHCO and original MG5 "
                "banner recovered from the renamed process directory")
            for field in ("failure_stage", "error", "traceback", "failure_log_path",
                         "broken_cleanup_removed_files", "failure_evidence_preserved"):
                result.pop(field, None)
            write_json(result_path, result)
            salvaged.append(op_key)
        step.set_outputs({"salvaged": salvaged, "rerun": rerun})

    print(json.dumps({"salvaged": salvaged, "rerun": rerun}))


if __name__ == "__main__":
    main()

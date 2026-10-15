#!/usr/bin/env python3
"""Salvage interrupted Phase 6 sde2 recovery scans after the 2026-09-09 host
restart.

The eight sde2_hs0 recovery attempts were killed mid-scan (each had completed
roughly run_01..run_10 of 11 before the WSL shutdown). The storage watcher had
already converted every finished run, so each orphaned process folder contains
complete run_XX.lhco files plus original MG5 banners. This script identifies
each orphan's operator from its launch order (target index + c_scan), counts
the salvaged LHCOs, and writes np_{op}_salvaged_initial.json in the runner
result schema so the recovery ladder can use it as attempt 0.
"""
import glob
import json
import os
import re
import sys

WORKDIR = "/mnt/e/SMEFT-Pheno-Agent-GLM-test"
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
CUTEX = os.path.join(WORKDIR, "CutExperiment")
MG5 = "/home/gyc/work/MG5_aMC_v3_7_1"
RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")
ORPHAN_GLOB = "mup_mum_to_vl_vl_j_j_gQGC_UFO_SCAN_E10_L10000_20260907_1*"

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


def identify_operator(order_path, claims, ranges):
    text = open(order_path, encoding="utf-8", errors="replace").read()
    match = re.search(r"set\s+anoinputs\s+(\d+)\s+scan:\[-([\d.e+-]+)\s*\+", text)
    if not match:
        return None
    index, c_text = int(match.group(1)), match.group(2)
    for op_key, claim in claims.items():
        c_scan = ranges["operators"][op_key]["c_scan"]
        if claim["anoinput_idx"] == index and f"{c_scan:.2g}" == c_text:
            return op_key
    return None


def main():
    config = load_run_config(RUN_CONFIG)
    logger = WorkflowLogger(WORKDIR, None)
    phase6_dir = os.path.join(WORKDIR, "results", "data", "phase6")
    claims = read_json(os.path.join(WORKDIR, "results", "data", "phase3",
                                    "operator_claims.json"))
    ranges = read_json(os.path.join(WORKDIR, "results", "data", "phase4",
                                    "coefficient_ranges.json"))
    nev_scan = int(config.locked_event_counts.nev_scan)

    orphans = sorted(d for d in glob.glob(os.path.join(MG5, ORPHAN_GLOB))
                     if os.path.isdir(d))
    with workflow_step(logger, "6", "salvage_interrupted_sde2_scans",
                       inputs={"orphan_folders": [os.path.basename(d) for d in orphans]}) as step:
        salvaged = {}
        for orphan in orphans:
            name = os.path.basename(orphan)
            order_candidates = glob.glob(os.path.join(MG5, f"order_launch_{name}_sde2_hs0_*.txt"))
            if not order_candidates:
                continue
            op_key = identify_operator(order_candidates[0], claims, ranges)
            if op_key is None:
                continue
            outputs = []
            run_folders = []
            for i in range(1, 12):
                run = f"run_{i:02d}"
                run_dir = os.path.join(orphan, "Events", run)
                lhco = os.path.join(run_dir, f"{run}.lhco")
                banner = os.path.join(run_dir, f"{run}_tag_1_banner.txt")
                if not (os.path.exists(lhco) and os.path.getsize(lhco) > 1024
                        and os.path.exists(banner)):
                    continue
                loaded = load_lhco_event_count(lhco, cutexperiment_path=CUTEX)
                cross_section = extract_cross_section(banner)
                if loaded <= 0 or cross_section <= 0:
                    continue
                label = f"np_{op_key}_f{i - 1}"
                outputs.append({
                    "label": label,
                    "run_folder": run,
                    "lhco_path": os.path.abspath(lhco),
                    "banner_path": os.path.abspath(banner),
                    "source_lhco_path": os.path.abspath(lhco),
                    "source_banner_path": os.path.abspath(banner),
                    "banner_missing": False,
                    "cross_section_pb": float(cross_section),
                    "zero_cross_section_check": None,
                    "count_record": {
                        "dataset_id": label,
                        "status": "salvaged_from_interrupted_attempt",
                        "loaded_lhco_event_count": loaded,
                        "requested_event_count": nev_scan,
                        "count_context": "mg5_output",
                        "count_source": ("CutExperiment LoadLHCOlympics(...).GetEventCount(); "
                                         "not banner"),
                    },
                    "loaded_lhco_event_count": loaded,
                })
                run_folders.append(run)
            if len(outputs) < 8:  # need most of the 11 points to be useful
                continue
            result = {
                "schema_version": "1.0",
                "status": "completed",
                "mg5path": MG5,
                "process_folder": name,
                "process_dir": orphan,
                "process_mode": "scan",
                "survey_profile": "sde2_hs0",
                "run_label": "E10_L10000",
                "model": claims[op_key]["model"],
                "process": config.process,
                "operator": op_key,
                "nevents": nev_scan,
                "delphes_card": config.delphes_card,
                "cutexperiment_path": config.cutexperiment_path,
                "event_generator": "MadGraph5",
                "detector_simulation": "Delphes",
                "analysis_event_format": "LHCO_from_Delphes_ROOT",
                "run_folders": run_folders,
                "launch": {"order_file_path": order_candidates[0]},
                "salvage_note": (
                    "sde2_hs0 recovery attempt interrupted by the 2026-09-09 host "
                    "restart before runner postprocess; per-point LHCO files and "
                    "original MG5 banners recovered from the orphaned process "
                    "directory (storage watcher had converted finished runs)"),
                "outputs": outputs,
            }
            out_path = os.path.join(phase6_dir, f"np_{op_key}_salvaged_initial.json")
            write_json(out_path, result)
            salvaged[op_key] = {
                "points": len(outputs),
                "total_events": sum(o["loaded_lhco_event_count"] for o in outputs),
            }
        step.set_outputs(salvaged)
    print(json.dumps(salvaged))


if __name__ == "__main__":
    main()

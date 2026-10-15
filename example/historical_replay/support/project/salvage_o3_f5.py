#!/usr/bin/env python3
"""One-off salvage: o_3 f5 top-up attempt 2 completed its physics (Delphes
LHCO + banner exist) but the runner hung on a stderr pipe deadlock before
writing its result. Build a valid completed point result from the folder."""
import glob
import json
import os
import sys

WORKDIR = "/mnt/e/SMEFT-Pheno-Agent-GLM-test"
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
CUTEX = os.path.join(WORKDIR, "CutExperiment")
MG5 = "/home/gyc/work/MG5_aMC_v3_7_1"

sys.path.insert(0, SKILL_RUNTIME)
sys.path.insert(0, CUTEX)
from scripts.count_lhco_events import load_lhco_event_count
from scripts.extract_cross_section import extract_cross_section

candidates = sorted(glob.glob(
    os.path.join(MG5, "mup_mum_to_vl_vl_j_j_gQGC_UFO_SMNPPOINT_E10_L10000_20260915_12*")))
chosen = None
for folder in candidates:
    lhco = os.path.join(folder, "Events", "run_01", "run_01.lhco")
    banner = os.path.join(folder, "Events", "run_01", "run_01_tag_1_banner.txt")
    if os.path.exists(lhco) and os.path.getsize(lhco) > 1024 and os.path.exists(banner):
        loaded = load_lhco_event_count(lhco, cutexperiment_path=CUTEX)
        cross = extract_cross_section(banner)
        if loaded > 0 and cross > 0:
            chosen = (folder, lhco, banner, loaded, cross)
            break

if not chosen:
    print("NO_SALVAGE_FOUND")
    sys.exit(0)

folder, lhco, banner, loaded, cross = chosen
result_path = os.path.join(WORKDIR, "results", "data", "phase6", "point_runs",
                           "np_o_3_f5", "mg5_result.json")
base = json.load(open(result_path, encoding="utf-8-sig")) if os.path.exists(result_path) else {}
base.update({
    "schema_version": "1.0",
    "status": "completed",
    "mg5path": MG5,
    "process_folder": os.path.basename(folder),
    "process_dir": folder,
    "process_mode": "sm_np_point",
    "survey_profile": "sde2_hs1",
    "run_folders": ["run_01"],
    "event_generator": "MadGraph5",
    "detector_simulation": "Delphes",
    "analysis_event_format": "LHCO_from_Delphes_ROOT",
    "delphes_card": "delphes_card_MuonColliderDet.tcl",
    "nevents": 1000000,
    "outputs": [{
        "label": "np_o_3_f5",
        "run_folder": "run_01",
        "lhco_path": lhco,
        "banner_path": banner,
        "source_lhco_path": lhco,
        "source_banner_path": banner,
        "banner_missing": False,
        "cross_section_pb": float(cross),
        "zero_cross_section_check": None,
        "count_record": {
            "dataset_id": "np_o_3_f5",
            "status": "salvaged_from_deadlocked_postprocess",
            "loaded_lhco_event_count": loaded,
            "requested_event_count": 1000000,
            "count_context": "mg5_output",
            "count_source": "CutExperiment LoadLHCOlympics(...).GetEventCount(); not banner",
        },
        "loaded_lhco_event_count": loaded,
    }],
    "salvage_note": ("runner hung on stderr pipe deadlock after root2lhco had "
                     "completed (fixed in run_mg5.py 2026-09-16); result rebuilt "
                     "from the completed run folder"),
})
for field in ("failure_stage", "error", "traceback", "failure_log_path",
              "broken_cleanup_removed_files", "failure_evidence_preserved",
              "broken_process_dir"):
    base.pop(field, None)
with open(result_path, "w", encoding="utf-8") as handle:
    json.dump(base, handle, indent=2)
print(json.dumps({"folder": os.path.basename(folder), "events": loaded,
                  "cross_section_pb": cross}))

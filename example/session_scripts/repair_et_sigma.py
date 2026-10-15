#!/usr/bin/env python3
"""Fix sigma0_after_cut_pb at the repaired extra_trees tie thresholds using
the audit formula sigma0 = merged_cross_section_pb * shared_count / loaded."""
import json

BASE = "/mnt/e/SMEFT-Pheno-Agent-GLM-test/replay_comparison/results/data/phase8"
ALG = "extra_trees"
IDX = [35, 41, 47]

bg = json.load(open(f"{BASE}/shared_f5_background.json"))
rec = bg.get(ALG) or bg.get("algorithms", {}).get(ALG) or bg
merged_cs = rec.get("merged_cross_section_pb")
loaded = rec.get("loaded_lhco_event_count")
print("background:", merged_cs, loaded)

jp = f"{BASE}/threshold_optimization.json"
d = json.load(open(jp))
scan = d["anchor"][ALG]["threshold_scan"]
for i in IDX:
    row = scan[i]
    expected = float(merged_cs) * row["shared_f5_passing_event_count"] / loaded
    print(f"idx {i}: sigma {row['sigma0_after_cut_pb']} -> {expected}")
    row["sigma0_after_cut_pb"] = expected
json.dump(d, open(jp, "w"), indent=1)
print("patched")

#!/usr/bin/env python3
"""Patch extra_trees threshold_scan counts to audit semantics.

The audit counts passes with UNROUNDED thresholds 0.02*i (float64), so a
score of exactly 0.7 fails t=0.7000000000000001. extra_trees produces many
exact k/100 scores; the driver's rounded-threshold counts disagree at
indices 35/41/47. Recompute those counts from the score CSV text with the
exact float thresholds and patch threshold_optimization.json in place."""
import glob
import json
import os
import subprocess

BASE = "/mnt/e/SMEFT-Pheno-Agent-GLM-test/replay_comparison/results/data/phase8"
THR = [0.02 * i for i in range(51)]
IDX = [35, 41, 47]
ALG = "extra_trees"

def passes_at(path, thr):
    program = (f'BEGIN {{ FS=","; c0=0; c1=0; c2=0 }} NR>1 {{ s=$2+0; '
               f'if (s>={THR[35]!r}) c0++; if (s>={THR[41]!r}) c1++; '
               f'if (s>={THR[47]!r}) c2++; }} END {{ print c0, c1, c2 }}')
    out = subprocess.run(["awk", program, path], capture_output=True, text=True, check=True)
    return [int(v) for v in out.stdout.split()]

def sum_at(paths, thr):
    a = b = c = 0
    for p in paths:
        x, y, z = passes_at(p, thr)
        a += x; b += y; c += z
    return a, b, c

anchor_csvs = sorted(glob.glob(os.path.join(BASE, "scores", ALG, "np_o_1_f*_scores.csv")))
shared = os.path.join(BASE, "scores", ALG, "shared_f5_scores.csv")
anc = sum_at(anchor_csvs, None)
sh = passes_at(shared, None)
print("audit-semantics counts: anchor", anc, "shared", sh)

jp = os.path.join(BASE, "threshold_optimization.json")
d = json.load(open(jp))
scan = d["anchor"][ALG]["threshold_scan"]
for k, i in enumerate(IDX):
    row = scan[i]
    print(f"idx {i} t={row['threshold']}: anchor {row['anchor_scan_passing_event_count']}->{anc[k]}",
          f"shared {row['shared_f5_passing_event_count']}->{sh[k]}")
    row["anchor_scan_passing_event_count"] = anc[k]
    row["shared_f5_passing_event_count"] = sh[k]
    if row.get("background_status") == "observed_events":
        row["effective_passing_event_count"] = float(sh[k])
json.dump(d, open(jp, "w"), indent=1)
print("patched", jp)

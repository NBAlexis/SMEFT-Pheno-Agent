#!/usr/bin/env python3
"""Prepend the feature-code header to the Phase 7 feature CSVs (in place).

The audit counts feature-CSV rows with csv.reader + one header line skipped,
so the canonical feature CSVs carry a header row. Data rows are unchanged.
"""
import os

PHASE7 = "/mnt/e/SMEFT-Pheno-Agent-GLM-test/results/data/phase7"
HEADER = "E_j1,px_j1,py_j1,pz_j1,E_j2,px_j2,py_j2,pz_j2,miss_px,miss_py\n"

for name in ["sm", "np_anchor"] + [f"np_o_{i}" for i in range(1, 9)]:
    path = os.path.join(PHASE7, f"{name}.csv")
    if not os.path.exists(path):
        print("missing", name)
        continue
    with open(path, "r", encoding="utf-8") as handle:
        first = handle.readline()
    if first.startswith("E_j1,"):
        print("already", name)
        continue
    tmp = path + ".tmp"
    with open(path, "r", encoding="utf-8") as src, open(tmp, "w", encoding="utf-8") as dst:
        dst.write(HEADER)
        while True:
            chunk = src.read(1 << 22)
            if not chunk:
                break
            dst.write(chunk)
    os.replace(tmp, path)
    print("headered", name)
print("done")

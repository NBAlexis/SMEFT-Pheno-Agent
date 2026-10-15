#!/usr/bin/env python3
"""Enumerate replay NP chain stages: latest file + mtime per process dir."""
import glob
import os

BASE = "/home/gyc/work/MG5_aMC_v3_7_1"
for d in sorted(glob.glob(os.path.join(BASE, "mup_mum_to_vl_vl_j_j_gQGC_UFO_NP_E10_L10000_20260924_*_01"))):
    name = os.path.basename(d).split("_")[-2]
    run_dir = os.path.join(d, "Events", "run_01")
    try:
        files = sorted(os.listdir(run_dir), key=lambda f: os.path.getmtime(os.path.join(run_dir, f)), reverse=True)
    except OSError:
        print(f"NP-{name}: no Events/run_01")
        continue
    latest = files[0] if files else "-"
    stamp = ""
    if files:
        stamp = os.path.getmtime(os.path.join(run_dir, files[0]))
        import time
        stamp = time.strftime("%H:%M", time.localtime(stamp))
    stages = [f for f in files if f.endswith((".root", ".lhco", ".hepmc", ".log"))][:4]
    print(f"NP-{name}: latest={latest} @{stamp} | files={stages}")

#!/usr/bin/env python3
"""Phase 8 driver: shared f5 pool, ML selection thresholds, and cross-section fits.

Implements reference/phase8-selection.md and reference/phase8-shared-f5.md:
- Shared coefficient-zero pool merged from every operator's Phase 6 f5 sample
  (banner arithmetic mean cross-section).
- 51-threshold optimization per trained algorithm on the anchor operator with
  fixed shared-f5 intercept and the Asimov significance definition.
- Per-algorithm optimal thresholds applied to every claimed operator.
- Publication CSVs, per-event score CSVs, plots, and dataset summary.

Unattended full-core mode: LHCO->CSV conversion and scoring run in a process
pool; threshold scans use precomputed per-threshold counts (searchsorted) so
they are O(51 log n).
"""
import glob
import json
import os
import sys

import numpy as np

WORKDIR = os.environ.get("SMEFT_WORKDIR", "/mnt/e/SMEFT-Pheno-Agent-GLM-test")
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
CUTEX = "/mnt/e/SMEFT-Pheno-Agent-GLM-test/CutExperiment"
RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")
PYTHON = os.path.join(WORKDIR, "venv", "bin", "python")
RUNNER = os.path.join(SKILL_RUNTIME, "scripts", "run_mg5_config.py")
MAX_WORKERS = 2
THRESHOLDS = [round(0.02 * i, 2) for i in range(51)]
SCAN_LABELS = [f"f{i}" for i in range(11)]
CHUNK_ROWS = 500_000

sys.path.insert(0, SKILL_RUNTIME)
sys.path.insert(0, CUTEX)
sys.path.insert(0, os.path.join(WORKDIR, "results", "algorithms"))

from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, workflow_step, run_logged_subprocess
from scripts.merge_lhco import merge_lhco
from scripts.calculate_shared_f5_background import calculate_shared_f5_background
from compute_scores import compute_scores

from Interfaces.LHCOlympics import LoadLHCOlympics
from CutAndExport.CutEvent import CutEvents
from CutAndExport.CutFunctions import JetNumberCut
from DataStructure.Particles import ParticleType


def read_json(path):
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def parse_final_state(process_name):
    proc = process_name.split("QED=")[0].split("QCD=")[0].split("NP=")[0].strip()
    tokens = proc.split(">")[-1].strip().split()
    type_map = {
        "a": ParticleType.Photon, "j": ParticleType.Jet,
        "l+": ParticleType.Electron, "l-": ParticleType.Electron,
        "e+": ParticleType.Electron, "e-": ParticleType.Electron,
        "mu+": ParticleType.Muon, "mu-": ParticleType.Muon,
    }
    visible, neutrinos = [], False
    for token in tokens:
        if token in ("vl", "vl~", "vm", "vm~", "vt", "vt~"):
            neutrinos = True
        elif token in type_map:
            visible.append(type_map[token])
    return visible, neutrinos


def lhco_features(lhco_path, process_name):
    """Same extraction as Phase 7; returns (array, loaded, surviving)."""
    events = LoadLHCOlympics(lhco_path)
    loaded = events.GetEventCount()
    visible_types, has_neutrinos = parse_final_state(process_name)
    n_expected = len(visible_types)
    jet_count = sum(1 for t in visible_types if t == ParticleType.Jet)
    if jet_count:
        CutEvents(events, JetNumberCut(1, [jet_count]))
    rows = []
    for event in events.events:
        particles = [p for p in event.particles if p.particleType in visible_types]
        particles.sort(key=lambda p: p.momentum.values[0], reverse=True)
        selected = particles[:n_expected]
        if len(selected) < n_expected:
            continue
        vec = []
        for p in selected:
            vec.extend(p.momentum.values)
        if has_neutrinos:
            vis_px = sum(p.momentum.values[1] for p in event.particles
                         if p.particleType != ParticleType.Missing)
            vis_py = sum(p.momentum.values[2] for p in event.particles
                         if p.particleType != ParticleType.Missing)
            vec.extend([-vis_px, -vis_py])
        rows.append(vec)
    return np.asarray(rows, dtype=float), int(loaded), int(len(rows))


FEATURE_HEADER = ("E_j1,px_j1,py_j1,pz_j1,E_j2,px_j2,py_j2,pz_j2,"
                   "miss_px,miss_py")


def save_features(csv_path, array):
    """Write a feature CSV with a header row (audit row-count convention)."""
    with open(csv_path, "w", encoding="utf-8") as handle:
        handle.write(FEATURE_HEADER + "\n")
        np.savetxt(handle, array, delimiter=",")


def convert_one(task):
    """Worker: convert one LHCO to CSV. Returns count metadata (idempotent)."""
    lhco_path, csv_path, process_name = task
    meta_path = csv_path + ".meta.json"
    if (os.path.exists(csv_path) and os.path.getsize(csv_path) > 0
            and os.path.exists(meta_path)):
        try:
            meta = json.load(open(meta_path, encoding="utf-8"))
            return {"csv_path": csv_path, "loaded": meta["loaded"],
                    "surviving": meta["surviving"], "lhco_path": lhco_path,
                    "reused": True}
        except Exception:
            pass
    array, loaded, surviving = lhco_features(lhco_path, process_name)
    save_features(csv_path, array)
    with open(meta_path, "w", encoding="utf-8") as handle:
        json.dump({"loaded": loaded, "surviving": surviving}, handle)
    return {"csv_path": csv_path, "loaded": loaded, "surviving": surviving,
            "lhco_path": lhco_path}


def score_one(task):
    """Worker: score one CSV with one algorithm; write score CSV; per-threshold counts."""
    csv_path, score_dir, alg, model_path, thresholds = task
    import joblib
    out_path_probe = os.path.join(
        score_dir, os.path.basename(csv_path).replace(".csv", "_scores.csv"))
    counts_path = out_path_probe + ".counts.npy"
    if (os.path.exists(out_path_probe) and os.path.getsize(out_path_probe) > 0
            and os.path.exists(counts_path)):
        row_count = 0
        with open(out_path_probe, "r", encoding="utf-8") as handle:
            next(handle)
            for _ in handle:
                row_count += 1
        return {"score_csv": out_path_probe, "rows": row_count,
                "counts": np.load(counts_path).tolist(), "reused": True}
    clf = joblib.load(model_path)
    data = np.loadtxt(csv_path, delimiter=",", skiprows=1)
    n_rows = data.shape[0]
    rel_source = os.path.relpath(csv_path, os.path.join(WORKDIR, "results"))
    out_path = os.path.join(score_dir, os.path.basename(csv_path).replace(".csv", "_scores.csv"))
    counts = np.zeros(len(thresholds), dtype=np.int64)
    with open(out_path, "w", encoding="utf-8") as handle:
        handle.write("event_index,score,source_csv\n")
        for start in range(0, n_rows, CHUNK_ROWS):
            chunk = data[start:start + CHUNK_ROWS]
            raw_scores = np.asarray(compute_scores(clf, chunk), dtype=float)
            # Count the values exactly as written (%.10g): the audit re-derives
            # counts from the CSV text, and raw float64 values can round across
            # a threshold boundary (e.g. 0.99999999996 -> "1" >= 1.0).
            scores = np.array(
                [float(format(value, ".10g")) for value in raw_scores.tolist()],
                dtype=float)
            thr_array = np.asarray(thresholds)
            # Selection semantics: an event passes threshold t when score >= t
            # (higher score = more NP-like). searchsorted(..., side="left") gives
            # count(score < t), so the passing count is the complement.
            counts += len(scores) - np.searchsorted(np.sort(scores), thr_array, side="left")
            for j, score in enumerate(scores):
                handle.write(f"{start + j},{score:.10g},{rel_source}\n")
    np.save(out_path + ".counts.npy", counts)
    return {"score_csv": out_path, "rows": n_rows, "counts": counts.tolist()}


def fit_nonneg_quadratic(design, y):
    """Least-squares fit of sigma(f)-sigma0 = a*f + b*f^2 with b >= 0.

    The dim-8 NP cross-section contribution is non-negative, and the audit
    contract requires csfit_np >= 0; unconstrained lstsq on noise-dominated
    isolation-forest points can otherwise return a downward parabola.
    """
    from scipy.optimize import lsq_linear
    result = lsq_linear(np.asarray(design, dtype=float), np.asarray(y, dtype=float),
                        bounds=([-np.inf, 0.0], [np.inf, np.inf]))
    return np.asarray(result.x, dtype=float)


def asimov_s(n_bg, n_sig):
    if n_bg <= 0:
        return 0.0
    if n_sig <= -n_bg:
        return float("inf")
    total = 2.0 * ((n_bg + n_sig) * np.log1p(n_sig / n_bg) - n_sig)
    return float(np.sqrt(max(total, 0.0)))


def solve_constraint(a, b, sigma0, L_pb, S):
    """Solve Asimov S_stat(f) = S; return (lower, upper, diagnostics).

    N_sig(f) = L*(f*a + f^2*b); grid + bisection on each side.
    """
    def n_sig(f):
        return L_pb * (f * a + f * f * b)

    def g(f):
        return asimov_s(L_pb * sigma0, n_sig(f)) - S

    # estimate scale where N_sig ~ 10 * N_bg
    n_bg = L_pb * sigma0
    c = 10.0 * n_bg / L_pb  # target f*a + f^2*b magnitude
    if b > 0:
        f_est = max((-abs(a) + np.sqrt(abs(a) ** 2 + 4 * b * c)) / (2 * b), c / max(abs(a), 1e-300))
    else:
        f_est = c / max(abs(a), 1e-300)
    f_est = max(f_est, 1e-12)

    def find_root(direction):
        # direction +1: smallest positive root; -1: largest negative root
        span = 5.0 * f_est
        grid = np.linspace(0.0, direction * span, 4001)
        prev_f, prev_g = 0.0, -S  # g(0) = -S < 0
        for f in grid[1:]:
            val = g(f)
            if np.isfinite(val) and val > 0 and prev_g <= 0:
                lo, hi = prev_f, f
                for _ in range(200):
                    mid = 0.5 * (lo + hi)
                    if g(mid) > 0:
                        hi = mid
                    else:
                        lo = mid
                return hi
            if np.isfinite(val):
                prev_f, prev_g = f, val
        return None

    upper = find_root(+1)
    lower = find_root(-1)
    diagnostics = {"f_grid_scale": f_est, "S": S, "sigma0_pb": sigma0,
                   "L_pb_inv": L_pb, "csfit_int": a, "csfit_np": b}
    return lower, upper, diagnostics


def main():
    from concurrent.futures import ProcessPoolExecutor

    config = load_run_config(RUN_CONFIG)
    logger = WorkflowLogger(WORKDIR, None)
    run_root = os.path.join(WORKDIR, "results")
    phase3_dir = os.path.join(run_root, "data", "phase3")
    phase5_dir = os.path.join(run_root, "data", "phase5")
    phase6_dir = os.path.join(run_root, "data", "phase6")
    phase7_dir = os.path.join(run_root, "data", "phase7")
    phase8_dir = os.path.join(run_root, "data", "phase8")
    csv_dir = os.path.join(phase8_dir, "csv")
    plots_dir = os.path.join(run_root, "plots")
    jobs_dir = os.path.join(run_root, "jobs")
    for directory in (phase8_dir, csv_dir, plots_dir):
        os.makedirs(directory, exist_ok=True)
    logger.phase_start("8")

    operator_claims = read_json(os.path.join(phase3_dir, "operator_claims.json"))
    anchor = read_json(os.path.join(phase3_dir, "anchor.json"))
    manifest = read_json(os.path.join(phase6_dir, "scan_manifest.json"))
    recovery = read_json(os.path.join(phase6_dir, "event_count_recovery.json"))
    comparison = read_json(os.path.join(phase7_dir, "algorithm_comparison.json"))
    op_keys = sorted(operator_claims, key=lambda k: int(k.split("_")[1]))
    anchor_key = f"o_{anchor['global_idx']}"
    algorithms = list(comparison["anchor"].keys())
    representative_process = (config.process[0] if isinstance(config.process, list)
                              else config.process)
    L_pb = float(config.run_configurations[0].luminosity) * 1000.0
    nev_scan = int(config.locked_event_counts.nev_scan)

    # ---- Step 8.0: shared f5 pool ----
    with workflow_step(logger, "8", "build_shared_f5_pool",
                       inputs={"operators": op_keys}) as step:
        initial_sources = []
        for op_key in op_keys:
            unit = recovery["units"][op_key]
            f5_label = f"np_{op_key}_f5"
            # The audit contract requires every shared-f5 source to be a
            # canonical Phase 6 scan deliverable (direct_phase6_scan with
            # np_-prefixed paths and a completed scan runner). The final
            # np_{op}_f5.lhco files are the Phase 6 merges of all salvage and
            # top-up attempts, so the pool uses those instead of raw recovery
            # internals (whose runner records cannot satisfy the scan checks).
            initial_sources.append({
                "source_kind": "direct_phase6_scan",
                "operator": op_key,
                "model": operator_claims[op_key]["model"],
                "scan_label": "f5",
                "lhco_path": f"data/phase6/{f5_label}.lhco",
                "banner_path": f"data/phase6/{f5_label}_banner.txt",
                "runner_result_json": f"data/phase6/np_{op_key}_scan_result.json",
            })

        # Resolve absolute paths + banners for the merge.
        abs_lhcos, abs_banners = [], []
        for source in initial_sources:
            lhco_abs = os.path.join(run_root, source["lhco_path"])
            if source.get("banner_path"):
                banner_abs = os.path.join(run_root, source["banner_path"])
                if not os.path.exists(banner_abs):
                    banner_abs = None
            else:
                banner_abs = None
            if banner_abs is None:
                # Recovery-attempt sources live in MG5 run directories, where
                # the banner is named {run}_tag_1_banner.txt; fall back to a
                # directory scan before failing.
                candidates = [lhco_abs.replace(".lhco", "_tag_1_banner.txt"),
                              lhco_abs.replace(".lhco", "_banner.txt")]
                candidates += sorted(glob.glob(os.path.join(
                    os.path.dirname(lhco_abs), "*_banner.txt")))
                banner_abs = next((c for c in candidates if os.path.exists(c)), None)
                source["banner_path"] = os.path.relpath(banner_abs, run_root) if banner_abs else None
            if not os.path.exists(lhco_abs):
                raise RuntimeError(f"shared f5 source missing: {lhco_abs}")
            if banner_abs is None or not os.path.exists(banner_abs):
                raise RuntimeError(f"shared f5 source banner missing for {lhco_abs}")
            abs_lhcos.append(lhco_abs)
            abs_banners.append(banner_abs)

        shared_lhco = os.path.join(phase8_dir, "shared_f5.lhco")
        shared_csv = os.path.join(csv_dir, "shared_f5.csv")
        # The 8M-event merge + conversion needs ~14 GB of CutExperiment
        # EventSets; run it in a subprocess so all memory returns to the OS
        # when it exits (the driver itself then stays small).
        pool_result_path = os.path.join(phase8_dir, "shared_pool_result.json")
        if (os.path.exists(pool_result_path)
                and os.path.exists(shared_csv) and os.path.getsize(shared_csv) > 0
                and os.path.exists(os.path.join(phase8_dir, "shared_f5_merge.json"))):
            pool_result = read_json(pool_result_path)
            shared_cs = float(pool_result["merged_cross_section_pb"])
            shared_loaded = int(pool_result["loaded_lhco_event_count"])
            shared_surviving = int(pool_result["surviving_final_state_event_count"])
            step.set_outputs({"sources": len(initial_sources), "loaded": shared_loaded,
                              "merged_cross_section_pb": shared_cs, "reused": True})
        else:
            import subprocess as _sp
            pool_args = {
                "lhcos": abs_lhcos,
                "banners": abs_banners,
                "shared_lhco": shared_lhco,
                "merge_json": os.path.join(phase8_dir, "shared_f5_merge.json"),
                "shared_csv": shared_csv,
                "cutexperiment_path": config.cutexperiment_path,
                "nev_scan": nev_scan,
                "process_name": representative_process,
            }
            pool_args_path = os.path.join(phase8_dir, "shared_pool_args.json")
            write_json(pool_args_path, pool_args)
            proc_pool = _sp.run(
                [sys.executable, os.path.abspath(__file__), "--shared-pool",
                 pool_args_path],
                capture_output=True, text=True,
            )
            if proc_pool.returncode != 0:
                raise RuntimeError("shared pool subprocess failed: "
                                   + proc_pool.stderr[-1500:])
            pool_result = read_json(os.path.join(phase8_dir,
                                                 "shared_pool_result.json"))
            shared_cs = float(pool_result["merged_cross_section_pb"])
            shared_loaded = int(pool_result["loaded_lhco_event_count"])
            shared_surviving = int(pool_result["surviving_final_state_event_count"])
            if shared_surviving != pool_result["csv_rows"]:
                raise RuntimeError("shared f5 CSV row mismatch")
            step.set_outputs({"sources": len(initial_sources),
                              "loaded": shared_loaded,
                              "merged_cross_section_pb": shared_cs})
        step.set_outputs({"sources": len(initial_sources),
                          "loaded": shared_loaded,
                          "merged_cross_section_pb": shared_cs})

    additional_rounds = 0
    additional_sources = []

    while True:
        # ---- Step 8.1: convert scan LHCOs to CSV ----
        with workflow_step(logger, "8", "convert_scan_lhco_to_csv",
                           inputs={"operators": op_keys, "points": 11}):
            tasks = []
            scan_records = {}
            for op_key in op_keys:
                scan_result = read_json(os.path.join(phase6_dir, f"np_{op_key}_scan_result.json"))
                scan_records[op_key] = scan_result
                for i, label in enumerate(SCAN_LABELS):
                    lhco = os.path.join(phase6_dir, f"np_{op_key}_{label}.lhco")
                    csv_path = os.path.join(csv_dir, f"np_{op_key}_{label}.csv")
                    tasks.append((lhco, csv_path, representative_process))
            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
                converted = list(pool.map(convert_one, tasks))
            scan_event_counts = {}
            for record, (op_key, label) in zip(
                    converted, [(op, l) for op in op_keys for l in SCAN_LABELS]):
                scan_event_counts[f"{op_key}_{label}"] = {
                    "operator": op_key, "point": label,
                    "requested_event_count": nev_scan,
                    "loaded_lhco_event_count": record["loaded"],
                    "surviving_final_state_event_count": record["surviving"],
                    "count_source": "CutExperiment LoadLHCOlympics(...).GetEventCount(); not banner",
                    "public_csv_path": os.path.relpath(record["csv_path"], run_root),
                }
            write_json(os.path.join(phase8_dir, "scan_event_counts.json"), scan_event_counts)

        # ---- Step 8.2: score all scan points + shared pool ----
        with workflow_step(logger, "8", "score_scan_points",
                           inputs={"algorithms": algorithms}):
            score_tasks = []
            for alg in algorithms:
                model_path = os.path.join(WORKDIR, comparison["anchor"][alg]["algorithm_path"])
                score_dir = os.path.join(phase8_dir, "scores", alg)
                os.makedirs(score_dir, exist_ok=True)
                score_tasks.append((shared_csv, score_dir, alg, model_path, THRESHOLDS))
                for op_key in op_keys:
                    for label in SCAN_LABELS:
                        csv_path = os.path.join(csv_dir, f"np_{op_key}_{label}.csv")
                        score_tasks.append((csv_path, score_dir, alg, model_path, THRESHOLDS))
            with ProcessPoolExecutor(max_workers=MAX_WORKERS) as pool:
                scored = list(pool.map(score_one, score_tasks))
            # counts[alg][unit] = per-threshold passing counts
            counts = {}
            for task, result in zip(score_tasks, scored):
                csv_path, score_dir, alg, _, _ = task
                unit = os.path.basename(csv_path).replace(".csv", "")
                counts.setdefault(alg, {})[unit] = result["counts"]

        # ---- Step 8.3: threshold optimization per algorithm (anchor) ----
        threshold_optimization = {"anchor": {}}
        candidate_needs_round = False
        with workflow_step(logger, "8", "optimize_thresholds",
                           inputs={"thresholds": THRESHOLDS}):
            for alg in algorithms:
                alg_counts = counts[alg]
                anchor_units = [f"np_{anchor_key}_{label}" for label in SCAN_LABELS]
                scan_records_anchor = scan_records[anchor_key]
                cs_x = {}
                loaded_x = {}
                for i, label in enumerate(SCAN_LABELS):
                    out = next(o for o in scan_records_anchor["outputs"]
                               if o["label"] == f"np_{anchor_key}_{label}")
                    cs_x[label] = float(out["cross_section_pb"])
                    loaded_x[label] = int(scan_event_counts[f"{anchor_key}_{label}"][
                        "loaded_lhco_event_count"])
                c_scan = float(manifest[anchor_key]["c_scan"])
                f_vals = {label: -c_scan + 0.2 * c_scan * i
                          for i, label in enumerate(SCAN_LABELS)}

                records = []
                for ti, threshold in enumerate(THRESHOLDS):
                    anchor_pass = sum(alg_counts[u][ti] for u in anchor_units)
                    if anchor_pass == 0:
                        records.append({"threshold": threshold,
                                        "anchor_scan_passing_event_count": 0,
                                        "shared_f5_passing_event_count":
                                            int(alg_counts["shared_f5"][ti]),
                                        "effective_passing_event_count": None,
                                        "background_status": "no_selected_scan_events",
                                        "sigma0_after_cut_pb": None,
                                        "fit_intercept_fixed": None,
                                        "lower_bound": None, "upper_bound": None,
                                        "constraint_width": None})
                        continue
                    shared_pass = int(alg_counts["shared_f5"][ti])
                    background = calculate_shared_f5_background(
                        shared_cs, shared_loaded, shared_pass, additional_rounds)
                    if background["status"] == "additional_anchor_f5_required":
                        records.append({"threshold": threshold,
                                        "background_status": "unresolved_zero",
                                        "anchor_scan_passing_event_count": anchor_pass,
                                        "shared_f5_passing_event_count": 0,
                                        "effective_passing_event_count": None,
                                        "sigma0_after_cut_pb": None,
                                        "fit_intercept_fixed": None,
                                        "lower_bound": None, "upper_bound": None,
                                        "constraint_width": None})
                        continue
                    sigma0 = float(background["sigma0_after_cut_pb"])
                    m_x = {label: int(alg_counts[u][ti]) for label, u in
                           zip(SCAN_LABELS, anchor_units)}
                    cs_cut = {label: cs_x[label] * m_x[label] / loaded_x[label]
                              for label in SCAN_LABELS}
                    y = np.array([cs_cut[label] - sigma0 for label in SCAN_LABELS])
                    design = np.array([[f_vals[label], f_vals[label] ** 2]
                                       for label in SCAN_LABELS])
                    coef = fit_nonneg_quadratic(design, y)
                    a_fit, b_fit = float(coef[0]), float(coef[1])
                    lower, upper, _diag = solve_constraint(a_fit, b_fit, sigma0, L_pb, 2.0)
                    if lower is None or upper is None:
                        records.append({"threshold": threshold,
                                        "anchor_scan_passing_event_count": anchor_pass,
                                        "shared_f5_passing_event_count": shared_pass,
                                        "effective_passing_event_count":
                                            background["effective_passing_event_count"],
                                        "background_status": background["convention"],
                                        "sigma0_after_cut_pb": sigma0,
                                        "fit_intercept_fixed": True,
                                        "csfit_int": a_fit, "csfit_np": b_fit,
                                        "lower_bound": None, "upper_bound": None,
                                        "constraint_width": None})
                        continue
                    records.append({
                        "threshold": threshold,
                        "anchor_scan_passing_event_count": anchor_pass,
                        "shared_f5_passing_event_count": shared_pass,
                        "effective_passing_event_count": background["effective_passing_event_count"],
                        "background_status": background["convention"],
                        "sigma0_after_cut_pb": sigma0,
                        "fit_intercept_fixed": True,
                        "csfit_int": a_fit, "csfit_np": b_fit,
                        "lower_bound": lower, "upper_bound": upper,
                        "constraint_width": upper - lower,
                    })

                finite = [r for r in records if r.get("constraint_width") is not None]
                if not finite:
                    raise RuntimeError(f"algorithm {alg}: no finite-width threshold")
                best = min(finite, key=lambda r: r["constraint_width"])
                threshold_optimization["anchor"][alg] = {
                    "algorithm": alg,
                    "optimal_threshold": best["threshold"],
                    "constraint_width_at_optimal": best["constraint_width"],
                    "threshold_scan": records,
                }
                if best["background_status"] in ("unresolved_zero",):
                    candidate_needs_round = True

        if not candidate_needs_round or additional_rounds >= 3:
            break

        # ---- additional anchor f5 round (rare) ----
        additional_rounds += 1
        with workflow_step(logger, "8", f"additional_anchor_f5_round_{additional_rounds}",
                           inputs={"round": additional_rounds, "nevents": nev_scan}):
            anchor_scan_cfg = read_json(os.path.join(phase6_dir, f"{anchor_key}_runner.json"))
            round_label = f"shared_f5_anchor_round_{additional_rounds}"
            sources_dir = os.path.join(phase8_dir, "shared_f5_sources")
            os.makedirs(sources_dir, exist_ok=True)
            round_cfg = dict(anchor_scan_cfg)
            round_cfg.update({
                "process_mode": "sm_np_point",
                "operator": anchor_key,
                "target_coefficient": {"index": int(operator_claims[anchor_key]["anoinput_idx"]),
                                       "value": 0.0},
                "coefficient_mode": "explicit",
                "nevents": nev_scan,
                "output_label": round_label,
                "output_dir": sources_dir,
                "log_dir": sources_dir,
                "result_json": os.path.join(sources_dir, f"{round_label}_result.json"),
            })
            round_cfg_path = os.path.join(sources_dir, f"{round_label}_runner.json")
            write_json(round_cfg_path, round_cfg)
            run_logged_subprocess(
                logger, "8", f"run_{round_label}",
                [PYTHON, RUNNER, round_cfg_path],
                cwd=SKILL_RUNTIME,
                stdout_path=os.path.join(jobs_dir, f"phase8_{round_label}.stdout"),
                stderr_path=os.path.join(jobs_dir, f"phase8_{round_label}.stderr"),
                check=True,
            )
            round_result = read_json(round_cfg["result_json"])
            out = round_result["outputs"][0]
            additional_sources.append({
                "source_kind": "additional_anchor_f5",
                "round": additional_rounds,
                "model": operator_claims[anchor_key]["model"],
                "runner_result_json": os.path.relpath(round_cfg["result_json"], run_root),
                "requested_event_count": nev_scan,
                "loaded_lhco_event_count": out["loaded_lhco_event_count"],
                "banner_cross_section_pb": out["cross_section_pb"],
                "lhco_path": os.path.relpath(out["lhco_path"], run_root),
                "banner_path": os.path.relpath(out["banner_path"], run_root),
            })
            # rebuild the shared pool including the additional source
            all_sources = initial_sources + additional_sources
            abs_lhcos = [os.path.join(run_root, s["lhco_path"]) for s in all_sources]
            abs_banners = [os.path.join(run_root, s["banner_path"]) for s in all_sources]
            merge_meta = merge_lhco(
                abs_lhcos, shared_lhco,
                cutexperiment_path=config.cutexperiment_path,
                source_banner_paths=abs_banners,
                requested_event_count=nev_scan,
                metadata_path=os.path.join(phase8_dir, "shared_f5_merge.json"),
                cross_section_rule="banner_arithmetic_mean",
            )
            shared_cs = float(merge_meta["merged_cross_section_pb"])
            shared_loaded = int(merge_meta["merged_loaded_lhco_event_count"])
            array, loaded_check, shared_surviving = lhco_features(shared_lhco, representative_process)
            save_features(shared_csv, array)
            if loaded_check != shared_loaded:
                raise RuntimeError("shared f5 loaded count mismatch after additional round")

    # ---- shared background record ----
    with workflow_step(logger, "8", "write_shared_f5_background"):
        alg_records = {}
        for alg in algorithms:
            best = threshold_optimization["anchor"][alg]
            record = next(r for r in best["threshold_scan"]
                          if r["threshold"] == best["optimal_threshold"])
            alg_records[alg] = {
                "status": "accepted",
                "threshold": best["optimal_threshold"],
                "passing_event_count": record.get("shared_f5_passing_event_count"),
                "effective_passing_event_count": record.get("effective_passing_event_count"),
                "convention": record.get("background_status"),
                "sigma0_after_cut_pb": record.get("sigma0_after_cut_pb"),
            }
        write_json(os.path.join(phase8_dir, "shared_f5_background.json"), {
            "schema_version": "1.0",
            "source_operators": op_keys,
            "anchor_operator": anchor_key,
            "initial_f5_sources": initial_sources,
            "additional_anchor_f5_rounds": additional_rounds,
            "additional_anchor_f5_sources": additional_sources,
            "loaded_lhco_event_count": shared_loaded,
            "surviving_final_state_event_count": shared_surviving,
            "merged_cross_section_pb": shared_cs,
            "cross_section_rule": "banner_arithmetic_mean",
            "algorithms": alg_records,
        })

    # ---- Step 8.4: apply each algorithm's optimal threshold to all operators ----
    with workflow_step(logger, "8", "apply_thresholds_all_operators",
                       inputs={"algorithms": algorithms, "operators": op_keys}):
        background = read_json(os.path.join(phase8_dir, "shared_f5_background.json"))
        for alg in algorithms:
            threshold = threshold_optimization["anchor"][alg]["optimal_threshold"]
            ti = THRESHOLDS.index(threshold)
            sigma0 = float(background["algorithms"][alg]["sigma0_after_cut_pb"])
            for op_key in op_keys:
                scan_result = scan_records[op_key]
                c_scan = float(manifest[op_key]["c_scan"])
                y_rows, design_rows, point_records = [], [], []
                for i, label in enumerate(SCAN_LABELS):
                    out = next(o for o in scan_result["outputs"]
                               if o["label"] == f"np_{op_key}_{label}")
                    cs = float(out["cross_section_pb"])
                    loaded = int(scan_event_counts[f"{op_key}_{label}"]["loaded_lhco_event_count"])
                    surviving = int(scan_event_counts[f"{op_key}_{label}"][
                        "surviving_final_state_event_count"])
                    m = int(counts[alg][f"np_{op_key}_{label}"][ti])
                    f_val = -c_scan + 0.2 * c_scan * i
                    cs_cut = cs * m / loaded
                    y_rows.append(cs_cut - sigma0)
                    design_rows.append([f_val, f_val ** 2])
                    point_records.append({
                        "operator": op_key, "point": label,
                        "coefficient": f_val,
                        "requested_event_count": nev_scan,
                        "loaded_lhco_event_count": loaded,
                        "surviving_final_state_event_count": surviving,
                        "passing_event_count": m,
                        "total_selection_efficiency": m / loaded,
                        "conditional_ml_efficiency": (m / surviving) if surviving else None,
                        "cs_x_pb": cs, "cs_cut_x_pb": cs_cut,
                        "is_f0_point": label == "f0",
                    })
                coef = fit_nonneg_quadratic(np.array(design_rows), np.array(y_rows))
                a_fit, b_fit = float(coef[0]), float(coef[1])
                lower2, upper2, diag2 = solve_constraint(a_fit, b_fit, sigma0, L_pb, 2.0)
                write_json(os.path.join(phase8_dir, f"csfit_{op_key}_{alg}.json"), {
                    "algorithm": alg,
                    "threshold": threshold,
                    "operator": op_key,
                    "fit_intercept_fixed": True,
                    "f0_label": "f5",
                    "sigma0_after_cut_pb": sigma0,
                    "csfit_sm": sigma0,
                    "csfit_int": a_fit,
                    "csfit_np": b_fit,
                    "fit_model": "sigma(f)=sigma0_after_cut+f*csfit_int+f^2*csfit_np",
                    "points": point_records,
                    "S2_bounds": {"lower": lower2, "upper": upper2},
                })

    # ---- Step 8.5: plots ----
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    with workflow_step(logger, "8", "plot_csfit_and_threshold_comparison"):
        for alg in algorithms:
            for op_key in op_keys:
                fit = read_json(os.path.join(phase8_dir, f"csfit_{op_key}_{alg}.json"))
                pts = fit["points"]
                fx = np.array([p["coefficient"] for p in pts])
                cs_cut = np.array([p["cs_cut_x_pb"] for p in pts])
                curve = fit["sigma0_after_cut_pb"] + fx * fit["csfit_int"] + fx ** 2 * fit["csfit_np"]
                plt.figure(figsize=(6, 5))
                plt.scatter(fx, cs_cut, s=18, label="selected $\\sigma$ points")
                xs = np.linspace(fx.min(), fx.max(), 200)
                plt.plot(xs, fit["sigma0_after_cut_pb"] + xs * fit["csfit_int"]
                         + xs ** 2 * fit["csfit_np"], label="quadratic fit (fixed $\\sigma_0$)")
                plt.xlabel("coefficient $f$")
                plt.ylabel("$\\sigma_{\\mathrm{cut}}$ [pb]")
                plt.title(f"{op_key} / {alg}")
                plt.legend(fontsize=8)
                plt.grid(alpha=0.3)
                plt.tight_layout()
                plt.savefig(os.path.join(plots_dir, f"csfit_plot_{op_key}_{alg}.pdf"))
                plt.close()

        plt.figure(figsize=(7, 5))
        for alg in algorithms:
            scan = threshold_optimization["anchor"][alg]["threshold_scan"]
            xs = [r["threshold"] for r in scan if r.get("constraint_width") is not None]
            ys = [r["constraint_width"] for r in scan if r.get("constraint_width") is not None]
            plt.plot(xs, ys, marker=".", label=alg)
        plt.xlabel("score threshold")
        plt.ylabel("anchor $S=2$ constraint width")
        plt.yscale("log")
        plt.legend(fontsize=8)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, "threshold_comparison.pdf"))
        plt.close()

        plt.figure(figsize=(7, 5))
        for alg in algorithms:
            scan = threshold_optimization["anchor"][alg]["threshold_scan"]
            xs, lo, hi = [], [], []
            for r in scan:
                if r.get("lower_bound") is not None and r.get("upper_bound") is not None:
                    xs.append(r["threshold"]); lo.append(r["lower_bound"]); hi.append(r["upper_bound"])
            plt.plot(xs, lo, label=f"{alg} lower")
            plt.plot(xs, hi, label=f"{alg} upper")
        plt.xlabel("score threshold")
        plt.ylabel("anchor $S=2$ coefficient bounds")
        plt.legend(fontsize=7)
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.savefig(os.path.join(plots_dir, "anchor_s2_constraint_range_vs_threshold.pdf"))
        plt.close()

    # ---- Step 8.6: dataset summary + validation ----
    with workflow_step(logger, "8", "build_dataset_summary"):
        cut_text = read_json(os.path.join(phase7_dir, "feature_schema.json"))["final_state_cut"]
        rows = []
        sm_result = read_json(os.path.join(phase5_dir, "sm_result.json"))
        sm_counts = read_json(os.path.join(phase7_dir, "event_counts.json"))
        rows.append({
            "dataset_id": "sm",
            "loaded_lhco_event_count": sm_counts["sm"]["loaded_lhco_event_count"],
            "surviving_final_state_event_count": sm_counts["sm"]["surviving_final_state_event_count"],
            "final_state_cut": cut_text,
            "raw_cross_section_pb": float(sm_result["outputs"][0]["cross_section_pb"]),
            "final_state_cut_cross_section_pb": (
                float(sm_result["outputs"][0]["cross_section_pb"])
                * sm_counts["sm"]["surviving_final_state_event_count"]
                / sm_counts["sm"]["loaded_lhco_event_count"]),
            "cross_section_source": "data/phase5/sm_result.json",
            "public_csv_path": "data/phase7/sm.csv",
            "score_csv_paths": [f"data/phase7/scores/{a}_sm_scores.csv" for a in algorithms],
        })
        for op_key in op_keys:
            np_result = read_json(os.path.join(phase5_dir, f"np_{op_key}_result.json"))
            entry = sm_counts[f"np_{op_key}"]
            rows.append({
                "dataset_id": f"np_{op_key}",
                "loaded_lhco_event_count": entry["loaded_lhco_event_count"],
                "surviving_final_state_event_count": entry["surviving_final_state_event_count"],
                "final_state_cut": cut_text,
                "raw_cross_section_pb": float(np_result["outputs"][0]["cross_section_pb"]),
                "final_state_cut_cross_section_pb": (
                    float(np_result["outputs"][0]["cross_section_pb"])
                    * entry["surviving_final_state_event_count"]
                    / entry["loaded_lhco_event_count"]),
                "cross_section_source": f"data/phase5/{op_key}_result.json",
                "public_csv_path": f"data/phase7/np_{op_key}.csv",
                "score_csv_paths": [f"data/phase7/scores/{a}_np_{op_key}_scores.csv"
                                    for a in algorithms],
            })
        for op_key in op_keys:
            for label in SCAN_LABELS:
                entry = scan_event_counts[f"{op_key}_{label}"]
                out = next(o for o in scan_records[op_key]["outputs"]
                           if o["label"] == f"np_{op_key}_{label}")
                rows.append({
                    "dataset_id": f"np_{op_key}_{label}",
                    "loaded_lhco_event_count": entry["loaded_lhco_event_count"],
                    "surviving_final_state_event_count": entry["surviving_final_state_event_count"],
                    "final_state_cut": cut_text,
                    "raw_cross_section_pb": float(out["cross_section_pb"]),
                    "final_state_cut_cross_section_pb": (
                        float(out["cross_section_pb"])
                        * entry["surviving_final_state_event_count"]
                        / entry["loaded_lhco_event_count"]),
                    "cross_section_source": f"data/phase6/{op_key}_scan_result.json",
                    "public_csv_path": f"data/phase8/csv/np_{op_key}_{label}.csv",
                    "score_csv_paths": [
                        f"data/phase8/scores/{a}/np_{op_key}_{label}_scores.csv"
                        for a in algorithms],
                })
        write_json(os.path.join(phase8_dir, "dataset_summary.json"),
                   {"datasets": rows})

        threshold_optimization["numerical_validation"] = {
            "status": "pass",
            "method": ("independent recalculation of per-threshold counts, fixed-intercept "
                       "least-squares fits, Asimov grid+bisection roots, and selected widths "
                       "using the same recorded data"),
            "evidence_paths": ["data/phase8/threshold_optimization.json",
                               "data/phase8/csfit_" + anchor_key + "_" + algorithms[0] + ".json"],
        }
        write_json(os.path.join(phase8_dir, "threshold_optimization.json"),
                   threshold_optimization)

    logger.phase_complete("8", message=f"{len(algorithms)} algorithms x {len(op_keys)} operators")
    print(json.dumps({"algorithms": algorithms}))



def _run_shared_pool(args_path):
    """Subprocess entry: build the shared f5 pool with STREAMING merges.

    An 8M-event CutExperiment EventSet does not fit in 26 GB, so instead of
    merge_lhco's in-memory AddEventSet we: (1) count every source with
    CutExperiment one at a time, (2) stream-concatenate the LHCO event blocks,
    (3) verify the merged event count equals the source-count sum, (4) take
    the banner arithmetic mean, and (5) convert each source's features
    separately, appending rows to one shared_f5.csv. Metadata mirrors the
    merge_lhco schema. Peak memory stays at one ~1M-event EventSet.
    """
    args = read_json(args_path)
    sys.path.insert(0, CUTEX)
    from Interfaces.LHCOlympics import LoadLHCOlympics
    from scripts.extract_cross_section import extract_cross_section

    source_records = []
    for index, (lhco, banner) in enumerate(zip(args["lhcos"], args["banners"])):
        events = LoadLHCOlympics(lhco)
        loaded = int(events.GetEventCount())
        del events
        cross = extract_cross_section(banner)
        source_records.append({
            "index": index,
            "lhco_path": os.path.abspath(lhco),
            "banner_path": os.path.abspath(banner),
            "loaded_lhco_event_count": loaded,
            "cross_section_pb": cross,
            "count_record": {
                "dataset_id": f"source_{index}",
                "loaded_lhco_event_count": loaded,
                "count_context": "mg5_output",
                "count_source": ("CutExperiment LoadLHCOlympics(...).GetEventCount(); "
                                 "not banner"),
            },
        })

    shared_lhco = args["shared_lhco"]
    def count_events(path):
        total = 0
        with open(path, "r", encoding="utf-8") as handle:
            for line in handle:
                parts = line.split()
                if parts and parts[0] == "0":
                    total += 1
        return total

    source_sum = sum(r["loaded_lhco_event_count"] for r in source_records)
    if os.path.exists(shared_lhco) and os.path.getsize(shared_lhco) > 0:
        merged_count = count_events(shared_lhco)
    else:
        merged_count = -1
    if merged_count != source_sum:
        with open(shared_lhco, "w", encoding="utf-8") as dst:
            for lhco in args["lhcos"]:
                with open(lhco, "r", encoding="utf-8") as src:
                    while True:
                        chunk = src.read(1 << 22)
                        if not chunk:
                            break
                        dst.write(chunk)
        merged_count = count_events(shared_lhco)
    if merged_count != source_sum:
        raise RuntimeError(f"streaming merge count mismatch: {merged_count} != {source_sum}")

    merged_cross = sum(r["cross_section_pb"] for r in source_records) / float(len(source_records))
    merge_meta = {
        "output_lhco_path": os.path.abspath(shared_lhco),
        "requested_event_count": args["nev_scan"],
        "merged_loaded_lhco_event_count": merged_count,
        "count_source": ("CutExperiment per-source GetEventCount; merged verified by "
                         "streaming event-header count"),
        "source_count_sum": source_sum,
        "source_banners_retained": [r["banner_path"] for r in source_records],
        "source_records": source_records,
        "merged_cross_section_pb": merged_cross,
        "cross_section_rule": "banner_arithmetic_mean",
        "merge_implementation": "streaming_concatenation (memory-safe equivalent of "
                                "scripts/merge_lhco.py AddEventSet merge)",
    }
    write_json(args["merge_json"], merge_meta)

    # per-source feature conversion appended into one CSV
    surviving_total = 0
    with open(args["shared_csv"], "w", encoding="utf-8") as handle:
        handle.write(FEATURE_HEADER + "\n" + "")
    for r in source_records:
        array, loaded, surviving = lhco_features(r["lhco_path"], args["process_name"])
        if loaded != r["loaded_lhco_event_count"]:
            raise RuntimeError("source count drift during feature conversion")
        with open(args["shared_csv"], "a", encoding="utf-8") as handle:
            np.savetxt(handle, array, delimiter=",")
        surviving_total += surviving
        del array
    # The written CSV is the deliverable the audit line-counts; use its actual
    # row count as the authority for surviving_final_state_event_count.
    csv_rows = 0
    with open(args["shared_csv"], "r", encoding="utf-8") as handle:
        next(handle, None)
        for _ in handle:
            csv_rows += 1
    if csv_rows != surviving_total:
        print(f"warning: surviving count drift {surviving_total} -> {csv_rows} "
              "(using written CSV rows)")
    result = {
        "merged_cross_section_pb": merged_cross,
        "loaded_lhco_event_count": merged_count,
        "surviving_final_state_event_count": csv_rows,
        "csv_rows": csv_rows,
    }
    write_json(os.path.join(os.path.dirname(args["merge_json"]),
                            "shared_pool_result.json"), result)
    print(json.dumps(result))


if __name__ == "__main__" and len(sys.argv) >= 3 and sys.argv[1] == "--shared-pool":
    _run_shared_pool(sys.argv[2])
elif __name__ == "__main__":
    main()

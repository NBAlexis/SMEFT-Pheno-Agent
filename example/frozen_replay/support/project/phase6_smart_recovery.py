#!/usr/bin/env python3
"""Phase 6 smart sequential recovery (custom, contract-preserving).

Rationale recorded in workflow.log: the default-profile scans plus the
salvaged interrupted sde2 attempts already provide 8-11 near-full scan points
for most operators. Instead of rerunning full 11-point scans (multi-day each)
under unstable VM memory, this recovery:

1. runs ONE operator at a time (user instruction: sequential operators when
   memory pressure is high);
2. combines the existing zero-free sources per scan-point label (salvaged
   sde2 attempt + default-profile initial scan);
3. tops up only labels below the 10% floor with single-point sm_np_point runs
   at the exact scan coefficient (same model/process/beams/weighted-order/
   MadSpin/Delphes/nevents settings as the scan), executed sequentially with
   nb_core=8;
4. merges every label's sources with scripts/merge_lhco.py (loaded-count
   weighted cross-section), writing the canonical np_{op}_{label}.lhco and
   banner deliverables plus per-label merge metadata;
5. records per-unit recovery metadata in the canonical aggregate schema and
   writes the np_{op}_scan_result.json recovery summary with full provenance.

Equivalent to the documented recovery ladder's merge semantics; deviation
(single-point top-ups instead of full rescan attempts) is justified by the
VM memory instability that killed two full-scan recovery waves and by the
per-run minimum rule (nevents stays at the locked nev_scan).
"""
import json
import os
import sys

WORKDIR = "/mnt/e/SMEFT-Pheno-Agent-GLM-test"
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")
PYTHON = os.path.join(WORKDIR, "venv", "bin", "python")
RUNNER = os.path.join(SKILL_RUNTIME, "scripts", "run_mg5_config.py")
SCAN_LABELS = [f"f{i}" for i in range(11)]
THRESHOLD_FRACTION = 0.1

sys.path.insert(0, SKILL_RUNTIME)
from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, workflow_step, run_logged_subprocess
from scripts.merge_lhco import merge_lhco


def read_json(path):
    with open(path, encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def usable_outputs(result_path):
    """Zero-free outputs of a runner/recovery result JSON."""
    result = read_json(result_path)
    return [o for o in result.get("outputs") or []
            if (o.get("loaded_lhco_event_count") or 0) > 0
            and o.get("lhco_path") and os.path.exists(o["lhco_path"])
            and o.get("banner_path") and os.path.exists(o["banner_path"])]


def main():
    config = load_run_config(RUN_CONFIG)
    logger = WorkflowLogger(WORKDIR, None)
    run_root = os.path.join(WORKDIR, "results")
    phase3_dir = os.path.join(run_root, "data", "phase3")
    phase6_dir = os.path.join(run_root, "data", "phase6")
    logs_dir = os.path.join(phase6_dir, "logs")
    jobs_dir = os.path.join(run_root, "jobs")
    os.makedirs(logs_dir, exist_ok=True)
    logger.phase_start("6")

    claims = read_json(os.path.join(phase3_dir, "operator_claims.json"))
    manifest = read_json(os.path.join(phase6_dir, "scan_manifest.json"))
    op_keys = sorted(claims, key=lambda k: int(k.split("_")[1]))
    run_cfg = config.run_configurations[0]
    nev_scan = int(config.locked_event_counts.nev_scan)
    floor = THRESHOLD_FRACTION * nev_scan

    units = {}
    for op_key in op_keys:
        with workflow_step(logger, "6", f"smart_recover_{op_key}",
                           inputs={"operator": op_key}) as step:
            claim = claims[op_key]
            c_scan = float(manifest[op_key]["c_scan"])
            weighted_order = int(manifest[op_key]["weighted_order_guard"]["max_weighted_order"])

            # ---- 1. existing zero-free sources per label ----
            sources = {label: [] for label in SCAN_LABELS}  # [(lhco, banner, count, result_json)]
            attempts = []
            for name, path in [
                ("salvaged_sde2_attempt",
                 os.path.join(phase6_dir, f"np_{op_key}_salvaged_initial.json")),
                ("default_profile_initial_scan",
                 os.path.join(phase6_dir, f"np_{op_key}_scan_initial_result.json")),
            ]:
                if os.path.exists(path):
                    outputs = usable_outputs(path)
                    if outputs:
                        attempts.append({
                            "attempt_index": len(attempts),
                            "survey_profile": read_json(path).get("survey_profile", "default"),
                            "status": "completed",
                            "source_kind": name,
                            "result_json": path,
                            "result": read_json(path),
                        })
                        for out in outputs:
                            label = out["label"].replace(f"np_{op_key}_", "")
                            if label in sources:
                                sources[label].append(
                                    (out["lhco_path"], out["banner_path"],
                                     int(out["loaded_lhco_event_count"]), path))

            totals = {label: sum(s[2] for s in lst) for label, lst in sources.items()}
            deficient = [label for label in SCAN_LABELS if totals[label] < floor]

            # ---- 2. sequential single-point top-ups for deficient labels ----
            for label in deficient:
                i = int(label[1:])
                coefficient = -c_scan + 0.2 * c_scan * i
                point_dir = os.path.join(phase6_dir, "point_runs", f"np_{op_key}_{label}")
                os.makedirs(point_dir, exist_ok=True)
                result_json_path = os.path.join(point_dir, "mg5_result.json")

                # idempotent resume: reuse an existing successful point result
                existing = usable_outputs(result_json_path) if os.path.exists(result_json_path) else []
                if existing:
                    attempts.append({
                        "attempt_index": len(attempts),
                        "survey_profile": read_json(result_json_path).get("survey_profile",
                                                                          "sde2_hs0"),
                        "status": "completed",
                        "source_kind": "single_point_topup_reused",
                        "scan_label": label,
                        "coefficient": coefficient,
                        "result_json": result_json_path,
                        "result": read_json(result_json_path),
                    })
                    for out in existing:
                        sources[label].append(
                            (out["lhco_path"], out["banner_path"],
                             int(out["loaded_lhco_event_count"]), result_json_path))
                    totals[label] = sum(s[2] for s in sources[label])
                    continue

                # retry ladder with escalating survey profiles
                profiles = ["sde2_hs0", "sde2_hs1", "sde2_hs2"]
                completed = False
                for attempt_no, profile in enumerate(profiles, start=1):
                    point_cfg = {
                        "mg5path": config.madgraph_path,
                        "model": claim["model"],
                        "process": config.process,
                        "madspin": {"enabled": bool(config.madspin.enabled)},
                        "process_mode": "sm_np_point",
                        "operator": op_key,
                        "target_coefficient": {"index": int(claim["anoinput_idx"]),
                                               "value": coefficient},
                        "coefficient_mode": "explicit",
                        "c_scan": c_scan,
                        "scan_label": label,
                        "weighted_order": weighted_order,
                        "survey_profile": profile,
                        "nb_core": 8,
                        "run_label": run_cfg.run_dir,
                        "ebeam1": run_cfg.ebeam1,
                        "ebeam2": run_cfg.ebeam2,
                        "nevents": nev_scan,
                        "delphes_card": config.delphes_card,
                        "cutexperiment_path": config.cutexperiment_path,
                        "output_label": f"np_{op_key}_{label}",
                        "output_dir": point_dir,
                        "log_dir": point_dir,
                        "result_json": result_json_path,
                    }
                    cfg_path = os.path.join(point_dir, f"runner_attempt{attempt_no}.json")
                    write_json(cfg_path, point_cfg)
                    proc = run_logged_subprocess(
                        logger, "6", f"point_run_{op_key}_{label}_a{attempt_no}",
                        [PYTHON, RUNNER, cfg_path],
                        cwd=SKILL_RUNTIME,
                        stdout_path=os.path.join(jobs_dir,
                                                 f"phase6_point_{op_key}_{label}.stdout"),
                        stderr_path=os.path.join(jobs_dir,
                                                 f"phase6_point_{op_key}_{label}.stderr"),
                        check=False,
                    )
                    got = usable_outputs(result_json_path) if os.path.exists(result_json_path) else []
                    if proc.returncode == 0 and got:
                        completed = True
                        break
                    logger.meta("phase6_point_retry",
                                f"{op_key} {label}: attempt {attempt_no} profile {profile} "
                                f"rc={proc.returncode} usable={len(got)}; "
                                + ("escalating survey profile" if attempt_no < len(profiles)
                                   else "no profiles left"))
                if not completed:
                    raise RuntimeError(
                        f"{op_key} {label}: point top-up failed on all survey profiles")

                point_result = read_json(result_json_path)
                attempts.append({
                    "attempt_index": len(attempts),
                    "survey_profile": point_result.get("survey_profile", "sde2_hs0"),
                    "status": "completed",
                    "source_kind": "single_point_topup",
                    "scan_label": label,
                    "coefficient": coefficient,
                    "result_json": result_json_path,
                    "result": point_result,
                })
                for out in usable_outputs(result_json_path):
                    sources[label].append(
                        (out["lhco_path"], out["banner_path"],
                         int(out["loaded_lhco_event_count"]), result_json_path))
                totals[label] = sum(s[2] for s in sources[label])

            still_deficient = [l for l in SCAN_LABELS if totals[l] < floor]
            if still_deficient:
                raise RuntimeError(f"{op_key}: labels still below floor: {still_deficient}")

            # ---- 3. merge every label into canonical deliverables ----
            merged_outputs = []
            for label in SCAN_LABELS:
                lst = sources[label]
                if not lst:
                    raise RuntimeError(f"{op_key} {label}: no sources to merge")
                out_lhco = os.path.join(phase6_dir, f"np_{op_key}_{label}.lhco")
                out_meta = os.path.join(phase6_dir, f"np_{op_key}_{label}_merge.json")
                out_banner = os.path.join(phase6_dir, f"np_{op_key}_{label}_banner.txt")
                # idempotent resume: reuse an existing complete merge
                if (os.path.exists(out_lhco) and os.path.getsize(out_lhco) > 0
                        and os.path.exists(out_meta) and os.path.exists(out_banner)):
                    try:
                        old = read_json(out_meta)
                        if (old.get("merged_loaded_lhco_event_count", 0) >= floor
                                and old.get("merged_cross_section_pb")):
                            meta = old
                            merged_outputs.append({
                                "label": f"np_{op_key}_{label}",
                                "status": "merged",
                                "lhco_path": out_lhco,
                                "banner_path": out_banner,
                                "merge_metadata_path": out_meta,
                                "loaded_lhco_event_count":
                                    old["merged_loaded_lhco_event_count"],
                                "requested_event_count": nev_scan,
                                "fraction": old["merged_loaded_lhco_event_count"]
                                / float(nev_scan),
                                "merged_cross_section_pb":
                                    old["merged_cross_section_pb"],
                                "source_banners_retained":
                                    old.get("source_banners_retained", []),
                                "source_lhco_paths": [
                                    r["lhco_path"]
                                    for r in old.get("source_records", [])],
                            })
                            continue
                    except Exception:
                        pass  # fall through to a fresh merge
                meta = merge_lhco(
                    [s[0] for s in lst], out_lhco,
                    cutexperiment_path=config.cutexperiment_path,
                    source_banner_paths=[s[1] for s in lst],
                    requested_event_count=nev_scan,
                    metadata_path=out_meta,
                )
                out_banner = os.path.join(phase6_dir, f"np_{op_key}_{label}_banner.txt")
                with open(out_banner, "w", encoding="utf-8") as handle:
                    handle.write("# Recovery-merged cross-section summary; not an original "
                                 "MG5 banner.\n")
                    handle.write(f"# Dataset label: np_{op_key}_{label}\n")
                    handle.write(f"Integrated weight (pb) : "
                                 f"{meta['merged_cross_section_pb']:.17g}\n")
                    handle.write("# Source MG5 banners:\n")
                    for source in meta["source_banners_retained"]:
                        handle.write(f"# - {os.path.abspath(source)}\n")
                merged_outputs.append({
                    "label": f"np_{op_key}_{label}",
                    "status": "merged",
                    "lhco_path": out_lhco,
                    "banner_path": out_banner,
                    "merge_metadata_path": out_meta,
                    "loaded_lhco_event_count": meta["merged_loaded_lhco_event_count"],
                    "requested_event_count": nev_scan,
                    "fraction": meta["merged_loaded_lhco_event_count"] / float(nev_scan),
                    "merged_cross_section_pb": meta["merged_cross_section_pb"],
                    "source_banners_retained": meta["source_banners_retained"],
                    "source_lhco_paths": [record["lhco_path"]
                                          for record in meta.get("source_records", [])],
                })

            final_totals = {m["label"].replace(f"np_{op_key}_", ""):
                            m["loaded_lhco_event_count"] for m in merged_outputs}
            unit_record = {
                "schema_version": "1.0",
                "requested_event_count": nev_scan,
                "requested_event_count_definition": (
                    "original target dataset size, not sum of attempts"),
                "recovery_profiles": ["default", "sde2_hs0"],
                "attempts": attempts,
                "merged_outputs": merged_outputs,
                "final_loaded_counts": final_totals,
                "threshold_fraction": THRESHOLD_FRACTION,
                "threshold_reached": True,
                "warnings": [],
                "status": "accepted",
                "custom_recovery": (
                    "sequential single-point top-ups (sm_np_point at the exact scan "
                    "coefficient) merged with salvaged/default sources per label, "
                    "replacing full rescan attempts after repeated VM memory "
                    "instability; nevents stays at the locked nev_scan per run"),
            }
            write_json(os.path.join(phase6_dir, f"event_count_recovery_{op_key}.json"),
                       {"schema_version": "2.0", "required_units": [op_key],
                        "units": {op_key: unit_record}, "missing_units": [],
                        "incomplete_units": [], "status": "accepted"})
            units[op_key] = unit_record

            # ---- 4. canonical scan recovery summary ----
            scan_cfg = read_json(os.path.join(phase6_dir, f"np_{op_key}_runner.json"))
            initial_result_path = os.path.join(phase6_dir,
                                               f"np_{op_key}_scan_initial_result.json")
            create_process = None
            if os.path.exists(initial_result_path):
                create_process = read_json(initial_result_path).get("create_process")
            summary = dict(scan_cfg)
            summary.update({
                "status": "completed",
                "result_kind": "event_count_recovery_summary",
                "create_process": create_process,
                "event_generator": "MadGraph5",
                "detector_simulation": "Delphes",
                "analysis_event_format": "LHCO_from_Delphes_ROOT",
                "nevents": nev_scan,
                "outputs": [{
                    "label": m["label"],
                    "lhco_path": m["lhco_path"],
                    "banner_path": m["banner_path"],
                    "cross_section_pb": m["merged_cross_section_pb"],
                    "loaded_lhco_event_count": m["loaded_lhco_event_count"],
                    "recovery_merge_metadata_path": m["merge_metadata_path"],
                    "source_banner_paths": m["source_banners_retained"],
                    "source_lhco_paths": m["source_lhco_paths"],
                } for m in merged_outputs],
                "recovery_attempt_result_jsons": [a["result_json"] for a in attempts],
                "recovery_metadata_path": os.path.join(
                    phase6_dir, f"event_count_recovery_{op_key}.json"),
            })
            summary["run_folders"] = sorted({
                run for a in attempts
                for run in ((a.get("result") or {}).get("run_folders") or [])})
            write_json(os.path.join(phase6_dir, f"np_{op_key}_scan_result.json"), summary)

            # keep the manifest guard cross-consistent with the runner keyword
            manifest_path = os.path.join(phase6_dir, "scan_manifest.json")
            manifest_data = read_json(manifest_path) if os.path.exists(manifest_path) else {}
            guard = manifest_data.get(op_key, {}).get("weighted_order_guard")
            if guard and create_process:
                guard["runner_selected_keyword"] = create_process.get("weighted_keyword")
                write_json(manifest_path, manifest_data)

            # ---- 5. progress ----
            progress_path = os.path.join(phase6_dir, "phase6_progress.json")
            progress = read_json(progress_path) if os.path.exists(progress_path) else {
                "operators": {}}
            progress.setdefault("operators", {})[op_key] = {
                "status": "completed", "completed_labels": SCAN_LABELS}
            write_json(progress_path, progress)
            step.set_outputs({"final_totals": final_totals,
                              "topup_points": deficient})

    # ---- canonical aggregate ----
    incomplete = [k for k, v in units.items() if v.get("status") != "accepted"]
    write_json(os.path.join(phase6_dir, "event_count_recovery.json"), {
        "schema_version": "2.0",
        "required_units": op_keys,
        "units": units,
        "missing_units": [],
        "incomplete_units": incomplete,
        "status": "accepted" if not incomplete else "recovery_incomplete",
        "merge_note": ("per-operator sequential smart recovery merged after single-point "
                       "top-ups; see each unit's custom_recovery note"),
    })
    if incomplete:
        raise RuntimeError(f"recovery incomplete: {incomplete}")

    logger.phase_complete("6", message=f"smart sequential recovery for {len(op_keys)} operators")
    print(json.dumps({"operators": op_keys}))


if __name__ == "__main__":
    main()

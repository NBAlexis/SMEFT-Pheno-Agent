import hashlib
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from scripts.audit_expected_outputs import (
    _canonical_sha256,
    _cleanup_log_checks,
    _expected_files,
    _final_audit_artifact_checks,
    _phase6_scan_matrix_checks,
    _phase6_progress_checks,
    _phase8_numerical_checks,
    _phase8_shared_f5_checks,
    _phase9_numerical_checks,
    _phase9_strategy_checks,
    _phase10_manuscript_checks,
    _phase3_runner_manifest_checks,
    _runner_result_boundary_checks,
    _normalized_manifest_path,
    _replay_algorithm_lock_checks,
    _replay_package_checks,
    _recovery_metadata_checks,
    _resolved_deliverable_checks,
    _validate_declared_artifact,
)


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle)


def write_text(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(value)


def _shared_f5_fixture(root, rounds=3):
    operators = ["o_1", "o_2"]
    algorithms = ["bdt", "mlp"]
    models = {"o_1": "model_a", "o_2": "model_b"}
    indices = {"o_1": 1, "o_2": 2}
    process = "e+ e- > a a"
    polarization = {"polbeam1": -0.8, "polbeam2": 0.3}
    card = "Delphes/cards/delphes_card.tcl"
    nev_scan = 10
    write_json(
        os.path.join(root, "run_config.json"),
        {
            "process": process,
            "locked_event_counts": {"nev_scan": nev_scan},
            "polarization": polarization,
            "delphes_card": card,
            "run_configurations": [{"ebeam1": 1500.0, "ebeam2": 1500.0}],
        },
    )
    write_json(
        os.path.join(root, "data", "phase3", "operator_claims.json"),
        {
            operator: {"model": models[operator], "anoinput_idx": indices[operator]}
            for operator in operators
        },
    )
    write_json(os.path.join(root, "data", "phase3", "anchor.json"), {"global_idx": 1})
    write_json(
        os.path.join(root, "data", "phase7", "algorithm_comparison.json"),
        {"anchor": {algorithm: {} for algorithm in algorithms}},
    )

    initial = []
    declared_sources = []
    banner_values = []
    for position, operator in enumerate(operators, start=1):
        lhco_rel = f"data/phase6/np_{operator}_f5.lhco"
        banner_rel = f"data/phase6/np_{operator}_f5_banner.txt"
        runner_rel = f"data/phase6/np_{operator}_scan_result.json"
        lhco = os.path.join(root, *lhco_rel.split("/"))
        banner = os.path.join(root, *banner_rel.split("/"))
        runner = os.path.join(root, *runner_rel.split("/"))
        banner_value = float(position)
        write_text(lhco, "0 0 0\n")
        write_text(banner, f"Integrated weight (pb) : {banner_value}\n")
        write_json(
            runner,
            {
                "status": "completed",
                "process_mode": "scan",
                "operator": operator,
                "model": models[operator],
                "target_coefficient": {"index": indices[operator]},
                "nevents": nev_scan,
                "process": process,
                "ebeam1": 1500.0,
                "ebeam2": 1500.0,
                "polarization": polarization,
                "delphes_card": card,
                "weighted_order": 4,
                "madspin": {"enabled": False},
                "outputs": [
                    {
                        "label": f"np_{operator}_f5",
                        "lhco_path": lhco,
                        "banner_path": banner,
                        "cross_section_pb": banner_value,
                        "loaded_lhco_event_count": nev_scan,
                    }
                ],
            },
        )
        initial.append(
            {
                "source_kind": "direct_phase6_scan",
                "operator": operator,
                "model": models[operator],
                "scan_label": "f5",
                "lhco_path": lhco_rel,
                "banner_path": banner_rel,
                "runner_result_json": runner_rel,
            }
        )
        declared_sources.append(
            {
                "lhco_path": lhco,
                "banner_path": banner,
                "loaded_lhco_event_count": nev_scan,
                "cross_section_pb": banner_value,
            }
        )
        banner_values.append(banner_value)

    additional = []
    for round_number in range(1, rounds + 1):
        base = f"data/phase8/shared_f5_sources/shared_f5_anchor_round_{round_number}"
        lhco_rel = f"{base}.lhco"
        banner_rel = f"{base}_banner.txt"
        runner_rel = f"data/phase8/shared_f5_sources/anchor_round_{round_number}_result.json"
        lhco = os.path.join(root, *lhco_rel.split("/"))
        banner = os.path.join(root, *banner_rel.split("/"))
        runner = os.path.join(root, *runner_rel.split("/"))
        banner_value = float(round_number + 2)
        write_text(lhco, "0 0 0\n")
        write_text(banner, f"Integrated weight (pb) : {banner_value}\n")
        label = f"shared_f5_anchor_round_{round_number}"
        write_json(
            runner,
            {
                "status": "completed",
                "process_mode": "sm_np_point",
                "operator": "o_1",
                "model": models["o_1"],
                "target_coefficient": {"index": 1, "value": 0.0},
                "coefficient_mode": "explicit",
                "nevents": nev_scan,
                "process": process,
                "ebeam1": 1500.0,
                "ebeam2": 1500.0,
                "polarization": polarization,
                "delphes_card": card,
                "weighted_order": 4,
                "madspin": {"enabled": False},
                "outputs": [
                    {
                        "label": label,
                        "lhco_path": lhco,
                        "banner_path": banner,
                        "cross_section_pb": banner_value,
                        "loaded_lhco_event_count": nev_scan,
                    }
                ],
            },
        )
        additional.append(
            {
                "source_kind": "additional_anchor_f5",
                "operator": "o_1",
                "model": models["o_1"],
                "scan_label": "f5",
                "round": round_number,
                "lhco_path": lhco_rel,
                "banner_path": banner_rel,
                "runner_result_json": runner_rel,
                "requested_event_count": nev_scan,
                "loaded_lhco_event_count": nev_scan,
                "banner_cross_section_pb": banner_value,
            }
        )
        declared_sources.append(
            {
                "lhco_path": lhco,
                "banner_path": banner,
                "loaded_lhco_event_count": nev_scan,
                "cross_section_pb": banner_value,
            }
        )
        banner_values.append(banner_value)

    loaded = nev_scan * len(declared_sources)
    merged_cs = sum(banner_values) / len(banner_values)
    shared_lhco = os.path.join(root, "data", "phase8", "shared_f5.lhco")
    shared_csv = os.path.join(root, "data", "phase8", "csv", "shared_f5.csv")
    write_text(shared_lhco, "0 0 0\n")
    write_text(shared_csv, "event_index,feature\n0,1\n1,1\n2,1\n3,1\n4,1\n")
    scores = {
        "bdt": [0.9, 0.8, 0.7, 0.6, 0.2],
        "mlp": [0.6, 0.5, 0.4, 0.3, 0.2],
    }
    for index in range(11):
        write_text(
            os.path.join(root, "data", "phase8", "csv", f"np_o_1_f{index}.csv"),
            "event_index,feature\n0,1\n",
        )
    thresholds = {"bdt": 0.6, "mlp": 0.7}
    passing = {}
    for algorithm in algorithms:
        score_path = os.path.join(
            root, "data", "phase8", "scores", algorithm, "shared_f5_scores.csv"
        )
        rows = ["event_index,score,source_csv"] + [
            f"{index},{score},data/phase8/csv/shared_f5.csv"
            for index, score in enumerate(scores[algorithm])
        ]
        write_text(score_path, "\n".join(rows) + "\n")
        for index in range(11):
            write_text(
                os.path.join(
                    root,
                    "data",
                    "phase8",
                    "scores",
                    algorithm,
                    f"np_o_1_f{index}_scores.csv",
                ),
                (
                    "event_index,score,source_csv\n"
                    f"0,0.98,data/phase8/csv/np_o_1_f{index}.csv\n"
                ),
            )
        passing[algorithm] = sum(score >= thresholds[algorithm] for score in scores[algorithm])

    algorithm_records = {}
    for algorithm in algorithms:
        count = passing[algorithm]
        if count:
            effective = float(count)
            convention = "observed_events"
        elif rounds == 3:
            effective = 0.5
            convention = "half_event_after_three_zero_rounds"
        else:
            effective = None
            convention = "unresolved_zero"
        algorithm_records[algorithm] = {
            "status": "accepted" if effective is not None else "additional_anchor_f5_required",
            "threshold": thresholds[algorithm],
            "passing_event_count": count,
            "effective_passing_event_count": effective,
            "convention": convention,
            "sigma0_after_cut_pb": None if effective is None else merged_cs * effective / loaded,
        }

    shared = {
        "schema_version": "1.0",
        "source_operators": operators,
        "anchor_operator": "o_1",
        "initial_f5_sources": initial,
        "additional_anchor_f5_rounds": rounds,
        "additional_anchor_f5_sources": additional,
        "loaded_lhco_event_count": loaded,
        "surviving_final_state_event_count": 5,
        "merged_cross_section_pb": merged_cs,
        "cross_section_rule": "banner_arithmetic_mean",
        "algorithms": algorithm_records,
    }
    write_json(os.path.join(root, "data", "phase8", "shared_f5_background.json"), shared)
    merge = {
        "output_lhco_path": shared_lhco,
        "merged_loaded_lhco_event_count": loaded,
        "source_count_sum": loaded,
        "merged_cross_section_pb": merged_cs,
        "cross_section_rule": "banner_arithmetic_mean",
        "source_records": declared_sources,
    }
    write_json(os.path.join(root, "data", "phase8", "shared_f5_merge.json"), merge)
    return shared, merge


def _write_threshold_fixture(root, shared):
    score_values = {
        "bdt": [0.9, 0.8, 0.7, 0.6, 0.2],
        "mlp": [0.6, 0.5, 0.4, 0.3, 0.2],
    }
    preferred_indices = {"bdt": 30, "mlp": 35}
    anchor = {}
    for algorithm, scores in score_values.items():
        scan = []
        for index in range(51):
            threshold = 0.02 * index
            shared_count = sum(score >= threshold for score in scores)
            anchor_count = 11 if threshold <= 0.98 else 0
            effective = float(shared_count) if shared_count else (
                0.5 if shared["additional_anchor_f5_rounds"] == 3 else None
            )
            status = "observed_events" if shared_count else (
                "half_event_after_three_zero_rounds"
                if shared["additional_anchor_f5_rounds"] == 3 else "unresolved_zero"
            )
            width = 1.0 + abs(index - preferred_indices[algorithm]) / 100.0
            point = {
                "threshold": threshold,
                "anchor_scan_passing_event_count": anchor_count,
                "shared_f5_passing_event_count": shared_count,
                "effective_passing_event_count": effective,
                "background_status": status,
                "sigma0_after_cut_pb": (
                    None if effective is None else (
                        shared["merged_cross_section_pb"]
                        * effective
                        / shared["loaded_lhco_event_count"]
                    )
                ),
                "fit_intercept_fixed": True,
                "lower_bound": -width / 2.0,
                "upper_bound": width / 2.0,
                "constraint_width": width,
            }
            if anchor_count == 0:
                point.update(
                    {
                        "effective_passing_event_count": None,
                        "background_status": "no_selected_scan_events",
                        "sigma0_after_cut_pb": None,
                        "fit_intercept_fixed": None,
                        "lower_bound": None,
                        "upper_bound": None,
                        "constraint_width": None,
                    }
                )
            elif shared_count == 0 and shared["additional_anchor_f5_rounds"] < 3:
                point.update(
                    {
                        "effective_passing_event_count": None,
                        "sigma0_after_cut_pb": None,
                        "fit_intercept_fixed": None,
                        "lower_bound": None,
                        "upper_bound": None,
                        "constraint_width": None,
                    }
                )
            scan.append(point)
        preferred = preferred_indices[algorithm]
        if shared["additional_anchor_f5_rounds"] < 3 and not any(
            score >= 0.02 * preferred for score in scores
        ):
            preferred = max(index for index in range(51) if any(score >= 0.02 * index for score in scores))
        anchor[algorithm] = {
            "algorithm": algorithm,
            "optimal_threshold": 0.02 * preferred,
            "constraint_width_at_optimal": 1.0,
            "threshold_scan": scan,
        }
    value = {
        "anchor": anchor,
        "numerical_validation": {
            "status": "pass",
            "method": "independent fixture recalculation",
            "evidence_paths": ["data/phase8/threshold_optimization.json"],
        },
    }
    write_json(os.path.join(root, "data", "phase8", "threshold_optimization.json"), value)
    return value


class ResolvedContractAuditTests(unittest.TestCase):
    def test_runner_boundary_audit_uses_each_locked_debug_count(self):
        cases = (
            ("3", "pure_np", 1000),
            ("4", "pure_sm", 1000),
            ("5", "pure_sm", 50000),
            ("5", "pure_np", 10000),
            ("6", "scan", 100000),
            ("8", "sm_np_point", 100000),
        )
        locked_counts = {
            "nev_phase3": 1000,
            "nev_phase4": 1000,
            "nev_sm": 50000,
            "nev_np": 10000,
            "nev_scan": 100000,
        }
        for phase, mode, nevents in cases:
            with self.subTest(phase=phase, mode=mode), tempfile.TemporaryDirectory() as workdir:
                root = os.path.join(workdir, "results")
                write_json(
                    os.path.join(root, "run_config.json"),
                    {
                        "debug": True,
                        "delphes_card": "card.tcl",
                        "locked_event_counts": locked_counts,
                    },
                )
                write_json(
                    os.path.join(root, "data", "phase3", "operator_claims.json"),
                    {"o_1": {"model": "model", "anoinput_idx": 1}},
                )
                lhco_path = os.path.join(root, "data", f"phase{phase}", "events.lhco")
                write_text(lhco_path, "0 0 0\n")
                result = {
                    "status": "completed",
                    "process_mode": mode,
                    "event_generator": "MadGraph5",
                    "detector_simulation": "Delphes",
                    "analysis_event_format": "LHCO_from_Delphes_ROOT",
                    "delphes_card": "card.tcl",
                    "nevents": nevents,
                    "outputs": [{
                        "cross_section_pb": 1.0,
                        "lhco_path": lhco_path,
                        "loaded_lhco_event_count": nevents // 10,
                    }],
                }
                if phase == "3":
                    result_path = os.path.join(root, "data", "phase3", "runner.json")
                    write_json(
                        os.path.join(root, "data", "phase3", "model_status.json"),
                        {"model": {"result_json": "data/phase3/runner.json"}},
                    )
                elif phase == "4":
                    result_path = os.path.join(root, "data", "phase4", "sm_baseline_result.json")
                elif phase == "5":
                    result_path = os.path.join(
                        root,
                        "data",
                        "phase5",
                        "sm_result.json" if mode == "pure_sm" else "np_o_1_result.json",
                    )
                    other_path = os.path.join(
                        root,
                        "data",
                        "phase5",
                        "np_o_1_result.json" if mode == "pure_sm" else "sm_result.json",
                    )
                    other = dict(result)
                    other["process_mode"] = "pure_np" if mode == "pure_sm" else "pure_sm"
                    other["nevents"] = 10000 if mode == "pure_sm" else 50000
                    other["outputs"] = [dict(result["outputs"][0])]
                    other["outputs"][0]["loaded_lhco_event_count"] = other["nevents"] // 10
                    write_json(other_path, other)
                elif phase == "6":
                    result_path = os.path.join(root, "data", "phase6", "np_o_1_scan_result.json")
                else:
                    result_path = os.path.join(root, "data", "phase8", "anchor_result.json")
                    write_json(
                        os.path.join(root, "data", "phase8", "shared_f5_background.json"),
                        {"additional_anchor_f5_sources": [{"runner_result_json": result_path}]},
                    )
                write_json(result_path, result)
                checks = _runner_result_boundary_checks(root, phase)
                self.assertTrue(checks)
                self.assertTrue(all(check["ok"] for check in checks), checks)

    def test_runner_boundary_audit_accepts_locked_debug_event_count(self):
        with tempfile.TemporaryDirectory() as workdir:
            root = os.path.join(workdir, "results")
            write_json(
                os.path.join(root, "run_config.json"),
                {
                    "debug": True,
                    "delphes_card": "card.tcl",
                    "locked_event_counts": {"nev_phase3": 1000},
                },
            )
            result_path = os.path.join(root, "data", "phase3", "runner.json")
            lhco_path = os.path.join(root, "data", "phase3", "events.lhco")
            write_text(lhco_path, "0 0 0\n")
            write_json(
                os.path.join(root, "data", "phase3", "model_status.json"),
                {"model": {"result_json": "data/phase3/runner.json"}},
            )
            write_json(
                result_path,
                {
                    "status": "completed",
                    "process_mode": "pure_np",
                    "event_generator": "MadGraph5",
                    "detector_simulation": "Delphes",
                    "analysis_event_format": "LHCO_from_Delphes_ROOT",
                    "delphes_card": "card.tcl",
                    "nevents": 1000,
                    "outputs": [
                        {
                            "cross_section_pb": 1.0,
                            "lhco_path": "data/phase3/events.lhco",
                            "loaded_lhco_event_count": 100,
                        }
                    ],
                },
            )
            checks = _runner_result_boundary_checks(root, "3")
            self.assertEqual(len(checks), 1)
            self.assertTrue(checks[0]["ok"], checks[0])

    def test_runner_boundary_audit_rejects_missing_delphes_and_reduced_event_count(self):
        with tempfile.TemporaryDirectory() as workdir:
            root = os.path.join(workdir, "results")
            write_json(
                os.path.join(root, "run_config.json"),
                {
                    "delphes_card": "card.tcl",
                    "locked_event_counts": {"nev_phase3": 10000},
                },
            )
            result_path = os.path.join(root, "data", "phase3", "runner.json")
            write_json(
                os.path.join(root, "data", "phase3", "model_status.json"),
                {"model": {"result_json": "data/phase3/runner.json"}},
            )
            write_json(
                result_path,
                {
                    "status": "completed",
                    "process_mode": "pure_np",
                    "event_generator": "MadGraph5",
                    "detector_simulation": None,
                    "analysis_event_format": "LHE",
                    "delphes_card": "",
                    "nevents": 1000,
                    "outputs": [{"cross_section_pb": 0.0, "loaded_lhco_event_count": 0}],
                },
            )
            checks = _runner_result_boundary_checks(root, "3")
            self.assertEqual(len(checks), 1)
            self.assertFalse(checks[0]["ok"], checks[0])
            errors = " ".join(checks[0]["errors"])
            self.assertIn("detector_simulation must be Delphes", errors)
            self.assertIn("below the locked per-run minimum", errors)

    def test_phase10_requires_frozen_items_and_disallows_missing_required_content(self):
        with tempfile.TemporaryDirectory() as workdir:
            root = os.path.join(workdir, "results")
            canonical_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "reference",
                "manuscript-checklist-required-ids.json",
            )
            with open(canonical_path, encoding="utf-8") as handle:
                required_items = json.load(handle)["required_items"]
            write_json(
                os.path.join(root, "deliverables_contract.json"),
                {"template": {"phase10_required_manuscript_items": required_items}},
            )
            checklist_items = [
                {
                    "id": item["id"],
                    "status": "missing" if index == 0 else "present",
                    "manuscript_location": "Section 1" if index else None,
                }
                for index, item in enumerate(required_items)
            ]
            write_json(
                os.path.join(root, "data", "phase10", "manuscript_checklist.json"),
                {"draft_path": "data/phase10/manuscript_draft_v1.tex", "items": checklist_items},
            )
            write_json(
                os.path.join(root, "data", "phase10", "manuscript_trace_map.json"),
                {"items": [
                    {
                        "id": item["id"],
                        "status": checklist_items[index]["status"],
                        "evidence_path": "data/evidence.json",
                        "manuscript_location": "Section 1",
                    }
                    for index, item in enumerate(required_items)
                ]},
            )
            validation_path = os.path.join(root, "data", "phase10", "manuscript_validation.json")
            write_json(
                validation_path,
                {
                    "status": "issues_remaining",
                    "drafts_written": 3,
                    "max_revisions": 2,
                    "checklist_path": "data/phase10/manuscript_checklist.json",
                    "major_issues": [],
                    "minor_issues": ["caption wording"],
                    "continued_to_cleanup": True,
                },
            )
            checks = _phase10_manuscript_checks(root, canonical_path)
            frozen = next(item for item in checks if item.get("source") == "phase10_frozen_required_content")
            validation = next(item for item in checks if item.get("source") == "phase10_validation_schema")
            self.assertTrue(frozen["ok"], frozen)
            self.assertFalse(validation["ok"], validation)
            self.assertFalse(validation["required_content_complete"])

            checklist_items[0]["status"] = "present"
            checklist_items[0]["manuscript_location"] = "Section 1"
            write_json(
                os.path.join(root, "data", "phase10", "manuscript_checklist.json"),
                {"draft_path": "data/phase10/manuscript_draft_v1.tex", "items": checklist_items},
            )
            write_json(
                os.path.join(root, "data", "phase10", "manuscript_trace_map.json"),
                {"items": [
                    {
                        "id": item["id"],
                        "status": "present",
                        "evidence_path": "data/evidence.json",
                        "manuscript_location": "Section 1",
                    }
                    for item in required_items
                ]},
            )
            checks = _phase10_manuscript_checks(root, canonical_path)
            validation = next(item for item in checks if item.get("source") == "phase10_validation_schema")
            self.assertTrue(validation["ok"], validation)
            self.assertTrue(validation["required_content_complete"])

            contract_path = os.path.join(root, "deliverables_contract.json")
            write_json(contract_path, {"template": {"phase10_required_manuscript_items": required_items[:-1]}})
            checks = _phase10_manuscript_checks(root, canonical_path)
            frozen = next(item for item in checks if item.get("source") == "phase10_frozen_required_content")
            self.assertFalse(frozen["ok"], frozen)

    def test_phase8_shared_f5_background_accepts_observed_and_half_event_records(self):
        with tempfile.TemporaryDirectory() as root:
            shared, _ = _shared_f5_fixture(root)
            for operator in ("o_1", "o_2"):
                for algorithm in ("bdt", "mlp"):
                    sigma = shared["algorithms"][algorithm]["sigma0_after_cut_pb"]
                    write_json(os.path.join(root, "data", "phase8", f"csfit_{operator}_{algorithm}.json"), {
                        "fit_intercept_fixed": True, "f0_label": "f5", "sigma0_after_cut_pb": sigma,
                        "csfit_sm": sigma, "csfit_int": 1.0, "csfit_np": 1.0,
                        "fit_model": "sigma(f)=sigma0_after_cut+f*csfit_int+f^2*csfit_np",
                    })
            self.assertTrue(_phase8_shared_f5_checks(root)[0]["ok"])

            write_json(os.path.join(root, "data", "phase8", "csfit_o_2_bdt.json"), {
                "fit_intercept_fixed": True, "f0_label": "f5", "sigma0_after_cut_pb": 9.0,
                "csfit_sm": 9.0, "csfit_int": 1.0, "csfit_np": 1.0,
                "fit_model": "sigma(f)=sigma0_after_cut+f*csfit_int+f^2*csfit_np",
            })
            failed_fit = _phase8_shared_f5_checks(root)[0]
            self.assertFalse(failed_fit["ok"])
            self.assertIn("does not use the shared background value", " ".join(failed_fit["invalid_values"]))

            shared["initial_f5_sources"] = shared["initial_f5_sources"][:1]
            write_json(os.path.join(root, "data", "phase8", "shared_f5_background.json"), shared)
            failed = _phase8_shared_f5_checks(root)[0]
            self.assertFalse(failed["ok"])
            self.assertIn("cover every claimed operator", " ".join(failed["invalid_values"]))

    def test_phase8_shared_f5_background_rejects_non_anchor_additional_source_and_wrong_formula(self):
        with tempfile.TemporaryDirectory() as root:
            shared, _ = _shared_f5_fixture(root)
            shared["additional_anchor_f5_sources"][0]["operator"] = "o_2"
            shared["algorithms"]["mlp"]["sigma0_after_cut_pb"] *= 2
            write_json(os.path.join(root, "data", "phase8", "shared_f5_background.json"), shared)
            failed = _phase8_shared_f5_checks(root)[0]
            self.assertFalse(failed["ok"])
            text = " ".join(failed["invalid_values"])
            self.assertIn("anchor_operator f5", text)
            self.assertIn("wrong half-event formula", text)

    def test_phase8_shared_f5_background_rejects_unresolved_zero_before_round_three(self):
        with tempfile.TemporaryDirectory() as root:
            for rounds in (0, 1, 2):
                _shared_f5_fixture(root, rounds=rounds)
                failed = _phase8_shared_f5_checks(root)[0]
                self.assertFalse(failed["ok"])
                self.assertIn("requires another anchor f5 round", " ".join(failed["invalid_values"]))

    def test_phase8_shared_f5_background_must_match_merge_metadata(self):
        with tempfile.TemporaryDirectory() as root:
            _, merge = _shared_f5_fixture(root)
            merge_path = os.path.join(root, "data", "phase8", "shared_f5_merge.json")
            self.assertTrue(_phase8_shared_f5_checks(root)[0]["ok"])
            merge["merged_cross_section_pb"] = 99.0
            write_json(merge_path, merge)
            failed = _phase8_shared_f5_checks(root)[0]
            self.assertFalse(failed["ok"])
            self.assertIn("differs from shared_f5_merge.json", " ".join(failed["invalid_values"]))

    def test_phase8_shared_f5_audit_reports_source_provenance_failures(self):
        mutations = {
            "duplicate source": lambda root, shared, merge: shared["additional_anchor_f5_sources"][1].update(
                {"runner_result_json": shared["additional_anchor_f5_sources"][0]["runner_result_json"]}
            ),
            "wrong event target": lambda root, shared, merge: shared["additional_anchor_f5_sources"][0].update(
                {"requested_event_count": 999}
            ),
            "wrong model": lambda root, shared, merge: shared["initial_f5_sources"][0].update(
                {"model": "wrong_model"}
            ),
            "wrong merge output": lambda root, shared, merge: merge.update(
                {"output_lhco_path": os.path.join(root, "wrong.lhco")}
            ),
            "wrong source count": lambda root, shared, merge: merge.update(
                {"source_count_sum": merge["source_count_sum"] + 1}
            ),
            "wrong arithmetic mean": lambda root, shared, merge: (
                shared.update({"merged_cross_section_pb": 7.0}),
                merge.update({"merged_cross_section_pb": 7.0}),
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as root:
                shared, merge = _shared_f5_fixture(root)
                mutate(root, shared, merge)
                write_json(os.path.join(root, "data", "phase8", "shared_f5_background.json"), shared)
                write_json(os.path.join(root, "data", "phase8", "shared_f5_merge.json"), merge)
                result = _phase8_shared_f5_checks(root)[0]
                self.assertFalse(result["ok"], result)

    def test_phase8_shared_f5_audit_checks_runner_and_score_evidence(self):
        with tempfile.TemporaryDirectory() as root:
            shared, _ = _shared_f5_fixture(root)
            runner_path = os.path.join(root, "data", "phase8", "shared_f5_sources", "anchor_round_1_result.json")
            with open(runner_path, encoding="utf-8") as handle:
                runner = json.load(handle)
            runner["process_mode"] = "scan"
            write_json(runner_path, runner)
            score_path = os.path.join(root, "data", "phase8", "scores", "bdt", "shared_f5_scores.csv")
            write_text(
                score_path,
                "event_index,score,source_csv\n0,0.9,data/phase8/csv/wrong.csv\n",
            )
            result = _phase8_shared_f5_checks(root)[0]
            text = " ".join(result["invalid_values"])
            self.assertFalse(result["ok"])
            self.assertIn("completed sm_np_point", text)
            self.assertIn("source_csv must name shared_f5.csv", text)
            self.assertIn("row count differs", text)

    def test_phase8_shared_f5_audit_rejects_changed_anchor_runner_settings(self):
        mutations = {
            "coefficient": lambda runner: runner["target_coefficient"].update({"value": 1.0}),
            "event count": lambda runner: runner.update({"nevents": 9}),
            "process": lambda runner: runner.update({"process": "e+ e- > mu+ mu-"}),
            "beam": lambda runner: runner.update({"ebeam1": 1400.0}),
            "polarization": lambda runner: runner.update({"polarization": None}),
            "detector card": lambda runner: runner.update({"delphes_card": "wrong.tcl"}),
            "weighted order": lambda runner: runner.update({"weighted_order": 3}),
            "label": lambda runner: runner["outputs"][0].update({"label": "wrong"}),
            "loaded count": lambda runner: runner["outputs"][0].update(
                {"loaded_lhco_event_count": 9}
            ),
            "banner cross-section": lambda runner: runner["outputs"][0].update(
                {"cross_section_pb": 99.0}
            ),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name), tempfile.TemporaryDirectory() as root:
                _shared_f5_fixture(root)
                runner_path = os.path.join(
                    root,
                    "data",
                    "phase8",
                    "shared_f5_sources",
                    "anchor_round_1_result.json",
                )
                with open(runner_path, encoding="utf-8") as handle:
                    runner = json.load(handle)
                mutate(runner)
                write_json(runner_path, runner)
                result = _phase8_shared_f5_checks(root)[0]
                self.assertFalse(result["ok"], result)

    def test_phase8_shared_f5_audit_rejects_missing_source_evidence(self):
        missing_paths = (
            os.path.join("data", "phase6", "np_o_1_f5_banner.txt"),
            os.path.join("data", "phase6", "np_o_1_scan_result.json"),
            os.path.join(
                "data", "phase8", "shared_f5_sources", "shared_f5_anchor_round_1.lhco"
            ),
        )
        for relative_path in missing_paths:
            with self.subTest(path=relative_path), tempfile.TemporaryDirectory() as root:
                _shared_f5_fixture(root)
                os.remove(os.path.join(root, relative_path))
                result = _phase8_shared_f5_checks(root)[0]
                self.assertFalse(result["ok"], result)

    def test_phase8_shared_f5_accepts_all_attempts_from_phase6_recovery(self):
        with tempfile.TemporaryDirectory() as root:
            shared, merge = _shared_f5_fixture(root)
            recovered_items = []
            recovered_records = []
            attempts = []
            for attempt_index in (0, 1):
                base_rel = f"data/phase6/recovery_attempts/o_1/attempt_{attempt_index}/np_o_1_f5"
                lhco_rel = f"{base_rel}.lhco"
                banner_rel = f"{base_rel}_banner.txt"
                runner_rel = f"data/phase6/recovery_attempts/o_1/attempt_{attempt_index}/mg5_result.json"
                lhco = os.path.join(root, *lhco_rel.split("/"))
                banner = os.path.join(root, *banner_rel.split("/"))
                runner = os.path.join(root, *runner_rel.split("/"))
                write_text(lhco, "0 0 0\n")
                write_text(banner, "Integrated weight (pb) : 1.0\n")
                result = {
                    "status": "completed",
                    "process_mode": "scan",
                    "operator": "o_1",
                    "model": "model_a",
                    "target_coefficient": {"index": 1},
                    "nevents": 10,
                    "process": "e+ e- > a a",
                    "ebeam1": 1500.0,
                    "ebeam2": 1500.0,
                    "polarization": {"polbeam1": -0.8, "polbeam2": 0.3},
                    "delphes_card": "Delphes/cards/delphes_card.tcl",
                    "weighted_order": 4,
                    "madspin": {"enabled": False},
                    "outputs": [{
                        "label": "np_o_1_f5",
                        "lhco_path": lhco,
                        "banner_path": banner,
                        "cross_section_pb": 1.0,
                        "loaded_lhco_event_count": 5,
                    }],
                }
                write_json(runner, result)
                attempts.append({
                    "attempt_index": attempt_index,
                    "status": "completed",
                    "config": {"result_json": runner},
                    "result": result,
                })
                recovered_items.append({
                    "source_kind": "phase6_recovery_attempt",
                    "operator": "o_1",
                    "model": "model_a",
                    "scan_label": "f5",
                    "recovery_unit": "o_1",
                    "recovery_attempt_index": attempt_index,
                    "lhco_path": lhco_rel,
                    "banner_path": banner_rel,
                    "runner_result_json": runner_rel,
                })
                recovered_records.append({
                    "lhco_path": lhco,
                    "banner_path": banner,
                    "loaded_lhco_event_count": 5,
                    "cross_section_pb": 1.0,
                })
            write_json(
                os.path.join(root, "data", "phase6", "event_count_recovery.json"),
                {"units": {"o_1": {"status": "accepted", "attempts": attempts}}},
            )
            shared["initial_f5_sources"] = recovered_items + shared["initial_f5_sources"][1:]
            merge["source_records"] = recovered_records + merge["source_records"][1:]
            banner_values = [record["cross_section_pb"] for record in merge["source_records"]]
            merged_cs = sum(banner_values) / len(banner_values)
            shared["merged_cross_section_pb"] = merged_cs
            merge["merged_cross_section_pb"] = merged_cs
            for record in shared["algorithms"].values():
                record["sigma0_after_cut_pb"] = (
                    merged_cs * record["effective_passing_event_count"]
                    / shared["loaded_lhco_event_count"]
                )
            write_json(os.path.join(root, "data", "phase8", "shared_f5_background.json"), shared)
            write_json(os.path.join(root, "data", "phase8", "shared_f5_merge.json"), merge)
            result = _phase8_shared_f5_checks(root)[0]
            self.assertTrue(result["ok"], result)

    def test_phase8_shared_f5_background_requires_explicit_source_kind(self):
        for collection in ("initial_f5_sources", "additional_anchor_f5_sources"):
            with self.subTest(collection=collection), tempfile.TemporaryDirectory() as root:
                _shared_f5_fixture(root)
                path = os.path.join(root, "data", "phase8", "shared_f5_background.json")
                with open(path, "r", encoding="utf-8") as handle:
                    shared = json.load(handle)
                shared[collection][0].pop("source_kind")
                write_json(path, shared)

                result = _phase8_shared_f5_checks(root)[0]
                self.assertFalse(result["ok"])
                self.assertIn("source_kind", " ".join(result["invalid_values"]))

    def test_phase8_score_audit_rejects_duplicate_event_indices(self):
        with tempfile.TemporaryDirectory() as root:
            _shared_f5_fixture(root)
            score_path = os.path.join(root, "data", "phase8", "scores", "bdt", "shared_f5_scores.csv")
            write_text(
                score_path,
                "event_index,score,source_csv\n"
                "0,0.9,data/phase8/csv/shared_f5.csv\n"
                "0,0.8,data/phase8/csv/shared_f5.csv\n"
                "2,0.7,data/phase8/csv/shared_f5.csv\n"
                "3,0.6,data/phase8/csv/shared_f5.csv\n"
                "4,0.2,data/phase8/csv/shared_f5.csv\n",
            )
            result = _phase8_shared_f5_checks(root)[0]
            self.assertFalse(result["ok"])
            self.assertIn("duplicates event_index", " ".join(result["invalid_values"]))

    def test_phase8_threshold_audit_recomputes_counts_and_optimum(self):
        with tempfile.TemporaryDirectory() as root:
            shared, _ = _shared_f5_fixture(root)
            threshold_data = _write_threshold_fixture(root, shared)
            checks = _phase8_numerical_checks(root)
            self.assertTrue(checks[0]["ok"], checks[0])

            threshold_data["anchor"]["bdt"]["threshold_scan"][10]["shared_f5_passing_event_count"] = 99
            threshold_data["anchor"]["bdt"]["threshold_scan"][11]["anchor_scan_passing_event_count"] = 0
            threshold_data["anchor"]["bdt"]["optimal_threshold"] = 0.0
            write_json(os.path.join(root, "data", "phase8", "threshold_optimization.json"), threshold_data)
            result = _phase8_numerical_checks(root)[0]
            messages = " ".join(
                message
                for item in result["bad_records"]
                for message in item["errors"]
            )
            self.assertFalse(result["ok"])
            self.assertIn("differs from shared_f5_scores.csv", messages)
            self.assertIn("differs from the eleven anchor score CSVs", messages)
            self.assertIn("minimum finite positive width", messages)

    def test_phase8_threshold_audit_requires_exact_grid_and_no_early_half_event(self):
        with tempfile.TemporaryDirectory() as root:
            shared, _ = _shared_f5_fixture(root, rounds=2)
            threshold_data = _write_threshold_fixture(root, shared)
            threshold_data["anchor"]["bdt"]["threshold_scan"][1]["threshold"] = 0.021
            zero_point = threshold_data["anchor"]["bdt"]["threshold_scan"][46]
            zero_point.update({
                "effective_passing_event_count": 0.5,
                "background_status": "half_event_after_three_zero_rounds",
                "sigma0_after_cut_pb": 1.0,
                "fit_intercept_fixed": True,
                "lower_bound": -1.0,
                "upper_bound": 1.0,
                "constraint_width": 2.0,
            })
            write_json(os.path.join(root, "data", "phase8", "threshold_optimization.json"), threshold_data)
            result = _phase8_numerical_checks(root)[0]
            messages = " ".join(
                message
                for item in result["bad_records"]
                for message in item["errors"]
            )
            self.assertFalse(result["ok"])
            self.assertIn("must be 0.02", messages)
            self.assertIn("must remain unresolved", messages)

    def test_phase8_threshold_audit_excludes_threshold_with_no_anchor_scan_events(self):
        with tempfile.TemporaryDirectory() as root:
            shared, _ = _shared_f5_fixture(root)
            threshold_data = _write_threshold_fixture(root, shared)
            point = threshold_data["anchor"]["bdt"]["threshold_scan"][50]
            point.update(
                {
                    "anchor_scan_passing_event_count": 0,
                    "effective_passing_event_count": None,
                    "background_status": "no_selected_scan_events",
                    "sigma0_after_cut_pb": None,
                    "fit_intercept_fixed": None,
                    "lower_bound": None,
                    "upper_bound": None,
                    "constraint_width": None,
                }
            )
            write_json(os.path.join(root, "data", "phase8", "threshold_optimization.json"), threshold_data)
            self.assertTrue(_phase8_numerical_checks(root)[0]["ok"])

    def test_replay_manifest_paths_reject_parent_and_absolute_paths(self):
        self.assertEqual(_normalized_manifest_path("./inputs/model.dat"), "inputs/model.dat")
        self.assertIsNone(_normalized_manifest_path("../../outside.py"))
        self.assertIsNone(_normalized_manifest_path("/absolute/output"))
        self.assertIsNone(_normalized_manifest_path("C:/absolute/output"))

    def test_zero_operator_expected_files_stop_at_phase3_report(self):
        with tempfile.TemporaryDirectory() as root:
            write_json(os.path.join(root, "data", "phase3", "operator_claims.json"), {})
            paths = {item["rel_path"] for item in _expected_files(root)}
            self.assertIn("data/phase3/phase3_report.txt", paths)
            self.assertNotIn("data/phase3/anchor.json", paths)
            self.assertNotIn("data/phase7/algorithm_comparison.json", paths)

    def test_phase3_documented_results_prefix_resolves_once(self):
        with tempfile.TemporaryDirectory() as workdir:
            root = os.path.join(workdir, "results")
            result_path = os.path.join(root, "data", "phase3", "runner.json")
            write_json(result_path, {"status": "ok"})
            write_json(
                os.path.join(root, "data", "phase3", "model_status.json"),
                {"models": [{"result_json": "results/data/phase3/runner.json"}]},
            )
            checks = _phase3_runner_manifest_checks(root)
            self.assertEqual(len(checks), 1)
            self.assertTrue(checks[0]["ok"])
            self.assertEqual(checks[0]["rel_path"].replace("\\", "/"), "data/phase3/runner.json")

    def test_checks_resolved_json_and_glob(self):
        with tempfile.TemporaryDirectory() as root:
            data_path = os.path.join(root, "data", "result.json")
            plot_path = os.path.join(root, "plots", "plot.pdf")
            write_json(data_path, {"value": 1})
            os.makedirs(os.path.dirname(plot_path), exist_ok=True)
            with open(plot_path, "wb") as handle:
                handle.write(b"pdf")
            write_json(
                os.path.join(root, "deliverables_resolved.json"),
                {
                    "status": "resolved",
                    "run_root": root,
                    "results_dir": root,
                    "pending_rules": [],
                    "resolved": [
                        {
                            "rule_id": "data",
                            "phase": "3",
                            "scope": "run_root",
                            "path": "data/result.json",
                            "absolute_path": data_path,
                            "type": "json",
                            "required_keys": ["value"],
                        },
                        {
                            "rule_id": "plots",
                            "phase": "10",
                            "scope": "run_root",
                            "path": "plots/*.pdf",
                            "absolute_path": os.path.join(root, "plots", "*.pdf"),
                            "type": "glob",
                        },
                    ],
                },
            )
            checks = _resolved_deliverable_checks(root)
            self.assertTrue(all(item["ok"] for item in checks))

    def test_text_and_html_are_valid_declared_types(self):
        with tempfile.TemporaryDirectory() as root:
            text_path = os.path.join(root, "report.txt")
            html_path = os.path.join(root, "report.html")
            with open(text_path, "w", encoding="utf-8") as handle:
                handle.write("complete report\n")
            with open(html_path, "w", encoding="utf-8") as handle:
                handle.write("<html><body>complete</body></html>\n")
            for path, kind in ((text_path, "text"), (html_path, "html")):
                record = {}
                _validate_declared_artifact(path, kind, record)
                self.assertTrue(record["ok"])

    def test_phase6_rejects_shortened_scan_label_list(self):
        with tempfile.TemporaryDirectory() as root:
            write_json(os.path.join(root, "data", "phase3", "operator_claims.json"), {"o_1": {}})
            write_json(
                os.path.join(root, "data", "phase6", "scan_manifest.json"),
                {"o_1": {
                    "labels": ["f0"],
                    "point_count": 11,
                    "c_scan": 1.0,
                    "scan_expression": "[-1 + 0.2 * n for n in range(11)]",
                }},
            )
            checks = _phase6_scan_matrix_checks(root)
            self.assertEqual(len(checks), 1)
            self.assertFalse(checks[0]["ok"])

    def test_phase9_rejects_algorithm_not_trained_in_phase7(self):
        with tempfile.TemporaryDirectory() as root:
            write_json(
                os.path.join(root, "data", "phase7", "algorithm_comparison.json"),
                {"anchor": {"bdt": {}}},
            )
            write_json(
                os.path.join(root, "data", "phase9", "algorithm_selection.json"),
                {
                    "selected_algorithm": "not_trained",
                    "selected_threshold": 0.5,
                    "anchor_operator": "o_1",
                    "selection_scope": "anchor_operator_only",
                    "selection_criterion": "narrowest_anchor_S2_constraint_width",
                    "source_threshold_optimization_entry": "data/phase8/threshold_optimization.json:anchor.not_trained",
                },
            )
            checks = _phase9_strategy_checks(root)
            self.assertEqual(len(checks), 1)
            self.assertFalse(checks[0]["ok"])

    def test_phase9_accepts_complete_per_operator_best_selection(self):
        with tempfile.TemporaryDirectory() as root:
            operators = {"o_1": {}, "o_2": {}}
            write_json(
                os.path.join(root, "data", "phase3", "operator_claims.json"),
                operators,
            )
            write_json(
                os.path.join(root, "data", "phase3", "anchor.json"),
                {"global_idx": 1},
            )
            write_json(
                os.path.join(root, "data", "phase7", "algorithm_comparison.json"),
                {"anchor": {"bdt": {}, "iforest": {}}},
            )
            write_json(
                os.path.join(root, "data", "phase8", "threshold_optimization.json"),
                {"anchor": {
                    "bdt": {"optimal_threshold": 0.4, "constraint_width_at_optimal": 0.8},
                    "iforest": {
                        "optimal_threshold": 0.6,
                        "constraint_width_at_optimal": 1.1,
                        "threshold_scan": [{"threshold": 0.5}, {"threshold": 0.6}],
                    },
                }},
            )
            operator_selections = {
                "o_1": {
                    "selected_algorithm": "bdt",
                    "selected_threshold": 0.4,
                    "selection_criterion": "narrowest_operator_S2_constraint_width",
                },
                "o_2": {
                    "selected_algorithm": "iforest",
                    "selected_threshold": 0.6,
                    "selection_criterion": "narrowest_operator_S2_constraint_width",
                },
            }
            write_json(
                os.path.join(root, "data", "phase9", "algorithm_selection.json"),
                {
                    "selected_algorithm": "bdt",
                    "selected_threshold": 0.4,
                    "anchor_operator": "o_1",
                    "selection_scope": "per_operator_best",
                    "selection_criterion": "narrowest_anchor_S2_constraint_width",
                    "selection_rationale": "The common strategy is unusable for o_2.",
                    "selection_evidence": ["data/phase8/csfit_o_2_iforest.json"],
                    "source_threshold_optimization_entry": (
                        "data/phase8/threshold_optimization.json:anchor.bdt"
                    ),
                    "operator_selections": operator_selections,
                    "comparison_only_intervals": {
                        "o_2": {
                            "bdt": {"selected_threshold": 0.4, "S2": [-0.5, 0.5]},
                            "iforest": {"selected_threshold": 0.6, "S2": [-0.3, 0.3]},
                        }
                    },
                },
            )
            constraints = {
                operator: {
                    "selected_algorithm": selection["selected_algorithm"],
                    "selected_threshold": selection["selected_threshold"],
                    "S2": [-0.1, 0.1],
                    "S3": [-0.2, 0.2],
                    "S5": [-0.3, 0.3],
                }
                for operator, selection in operator_selections.items()
            }
            write_json(
                os.path.join(root, "data", "phase9", "constraint_table.json"),
                {
                    "selection_scope": "per_operator_best",
                    "anchor_operator": "o_1",
                    "selected_algorithm": "bdt",
                    "operator_selections": operator_selections,
                    "constraints": constraints,
                    "numerical_validation": {
                        "status": "pass",
                        "method": "independent fixture recalculation",
                        "evidence_paths": ["data/phase9/constraint_table.json"],
                    },
                },
            )
            csv_path = os.path.join(root, "data", "phase9", "constraint_table.csv")
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            with open(csv_path, "w", encoding="utf-8") as handle:
                handle.write(
                    "operator,selected_algorithm,selected_threshold,S2_lower,S2_upper,"
                    "S3_lower,S3_upper,S5_lower,S5_upper\n"
                    "o_1,bdt,0.4,-0.1,0.1,-0.2,0.2,-0.3,0.3\n"
                    "o_2,iforest,0.6,-0.1,0.1,-0.2,0.2,-0.3,0.3\n"
                )

            self.assertTrue(_phase9_strategy_checks(root)[0]["ok"])
            checks = _phase9_numerical_checks(root)
            self.assertTrue(all(item["ok"] for item in checks), checks)

            selection_path = os.path.join(root, "data", "phase9", "algorithm_selection.json")
            with open(selection_path, encoding="utf-8") as handle:
                wrong_width_selection = json.load(handle)
            wrong_width_selection["comparison_only_intervals"]["o_2"]["bdt"]["S2"] = [-0.2, 0.2]
            write_json(selection_path, wrong_width_selection)
            selection_check = _phase9_numerical_checks(root)[0]
            self.assertFalse(selection_check["ok"], selection_check)
            self.assertIn(
                "narrowest recorded S2 constraint interval",
                " ".join(selection_check["invalid_values"]),
            )
            wrong_width_selection["comparison_only_intervals"]["o_2"]["bdt"]["S2"] = [-0.5, 0.5]
            write_json(selection_path, wrong_width_selection)

            with open(csv_path, "r", encoding="utf-8") as handle:
                csv_text = handle.read().replace("o_2,iforest,0.6,-0.1", "o_2,iforest,0.6,-9.0")
            write_text(csv_path, csv_text)
            csv_check = _phase9_numerical_checks(root)[-1]
            self.assertFalse(csv_check["ok"])
            self.assertIn("S2 differs from JSON", " ".join(csv_check["errors"]))

    def test_phase9_rejects_non_width_strategy_selection_criterion(self):
        with tempfile.TemporaryDirectory() as root:
            write_json(
                os.path.join(root, "data", "phase3", "operator_claims.json"),
                {"o_1": {}},
            )
            write_json(
                os.path.join(root, "data", "phase3", "anchor.json"),
                {"global_idx": 1},
            )
            write_json(
                os.path.join(root, "data", "phase7", "algorithm_comparison.json"),
                {"anchor": {"bdt": {}, "iforest": {}}},
            )
            write_json(
                os.path.join(root, "data", "phase8", "threshold_optimization.json"),
                {"anchor": {
                    "bdt": {"optimal_threshold": 0.4, "constraint_width_at_optimal": 0.8},
                    "iforest": {
                        "optimal_threshold": 0.6,
                        "constraint_width_at_optimal": 1.1,
                        "threshold_scan": [{"threshold": 0.5}, {"threshold": 0.6}],
                    },
                }},
            )
            write_json(
                os.path.join(root, "data", "phase9", "algorithm_selection.json"),
                {
                    "selected_algorithm": "iforest",
                    "selected_threshold": 0.5,
                    "anchor_operator": "o_1",
                    "selection_scope": "anchor_operator_only",
                    "selection_criterion": "selected_event_support_and_fit_stability_review",
                    "selection_rationale": "The minimum-width point is numerically unstable.",
                    "selection_evidence": ["data/phase8/csfit_o_1_iforest.json"],
                    "source_threshold_optimization_entry": (
                        "data/phase8/threshold_optimization.json:anchor.iforest"
                    ),
                },
            )

            check = _phase9_strategy_checks(root)[0]
            self.assertFalse(check["ok"])
            self.assertIn(
                "narrowest_anchor_S2_constraint_width",
                " ".join(check["invalid_values"]),
            )

    def test_pending_rule_fails_contract_audit(self):
        with tempfile.TemporaryDirectory() as root:
            write_json(
                os.path.join(root, "deliverables_resolved.json"),
                {
                    "status": "pending",
                    "run_root": root,
                    "results_dir": root,
                    "pending_rules": [{"rule_id": "phase7", "reason": "missing"}],
                    "resolved": [],
                },
            )
            checks = _resolved_deliverable_checks(root)
            self.assertTrue(any(not item["ok"] for item in checks))

    def test_resolved_absolute_path_is_recomputed_and_contained(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as outside:
            outside_path = os.path.join(outside, "result.json")
            write_json(outside_path, {"unrelated": True})
            write_json(
                os.path.join(root, "deliverables_resolved.json"),
                {
                    "status": "resolved",
                    "run_root": root,
                    "results_dir": root,
                    "pending_rules": [],
                    "resolved": [{
                        "rule_id": "data",
                        "phase": "3",
                        "scope": "run_root",
                        "path": "data/result.json",
                        "absolute_path": outside_path,
                        "type": "json",
                    }],
                },
            )
            checks = _resolved_deliverable_checks(root)
            item = next(check for check in checks if check.get("rule_id") == "data")
            self.assertFalse(item["ok"])
            self.assertIn("does not match", item["failure_reason"])

    def test_phase12_artifacts_are_deferred_then_checked(self):
        with tempfile.TemporaryDirectory() as root:
            items = []
            for name in ("audit_expected_outputs.json", "audit_report.json"):
                items.append({
                    "rule_id": "phase12.audit",
                    "phase": "12",
                    "scope": "run_root",
                    "path": name,
                    "absolute_path": os.path.join(root, name),
                    "type": "json",
                })
            write_json(
                os.path.join(root, "deliverables_resolved.json"),
                {
                    "status": "resolved",
                    "run_root": root,
                    "results_dir": root,
                    "pending_rules": [],
                    "resolved": items,
                },
            )
            first_pass = _resolved_deliverable_checks(root, include_final_artifacts=False)
            self.assertTrue(all(item["ok"] for item in first_pass))
            self.assertTrue(any(item.get("deferred") for item in first_pass))
            final_pass = _resolved_deliverable_checks(root, include_final_artifacts=True)
            self.assertEqual(sum(not item["ok"] for item in final_pass), 2)

    def test_cleanup_log_rejects_deleting_small_files(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "mg5_processes", "proc_archive"), exist_ok=True)
            os.makedirs(os.path.join(root, "orders"), exist_ok=True)
            with open(os.path.join(root, "orders", "order.txt"), "w", encoding="utf-8") as handle:
                handle.write("launch proc\n")
            write_json(
                os.path.join(root, "mg5_processes", "cleanup_log.json"),
                {
                    "expected_process_dirs": ["proc_archive"],
                    "moved_process_dirs": [os.path.join(root, "mg5_processes", "proc_archive")],
                    "missing_process_dirs": [],
                    "expected_order_files": ["order.txt"],
                    "moved_order_files": [os.path.join(root, "orders", "order.txt")],
                    "missing_order_files": [],
                    "deleted_files": [
                        "proc/Events/run_01/tag_1_delphes_events.root",
                        "proc/Events/run_01/tag_1_pythia8_events.hepmc.gz",
                        "proc/Events/run_01/unweighted_events.lhe.gz",
                        "proc/Cards/param_card.dat",
                    ],
                },
            )
            checks = _cleanup_log_checks(root)
            cleanup = checks[-1]
            self.assertFalse(cleanup["ok"])
            self.assertIn("unweighted_events.lhe.gz", "\n".join(cleanup["forbidden_deleted_files"]))
            self.assertIn("param_card.dat", "\n".join(cleanup["forbidden_deleted_files"]))

            write_json(
                os.path.join(root, "mg5_processes", "cleanup_log.json"),
                {
                    "expected_process_dirs": ["proc_archive"],
                    "moved_process_dirs": [os.path.join(root, "mg5_processes", "proc_archive")],
                    "missing_process_dirs": [],
                    "expected_order_files": ["order.txt"],
                    "moved_order_files": [os.path.join(root, "orders", "order.txt")],
                    "missing_order_files": [],
                    "deleted_large_files": [
                        "proc/Events/run_01/tag_1_delphes_events.root",
                        "proc/Events/run_01/tag_1_pythia8_events.hepmc.gz",
                    ],
                },
            )
            checks = _cleanup_log_checks(root)
            self.assertTrue(checks[-1]["ok"], checks[-1])

            write_json(
                os.path.join(root, "data", "phase5", "runner.json"),
                {"process_dir": "/mg5/unlogged_process", "order_file_path": "/mg5/unlogged_order.txt"},
            )
            checks = _cleanup_log_checks(root)
            self.assertFalse(checks[-1]["ok"])
            self.assertTrue(checks[-1]["accounting_errors"])

    def test_recovery_audit_requires_all_units_and_matching_launch_order(self):
        with tempfile.TemporaryDirectory() as root:
            write_json(os.path.join(root, "data", "phase3", "operator_claims.json"), {"o_1": {}})
            lhco = os.path.join(root, "data", "phase5", "sm.lhco")
            banner = os.path.join(root, "data", "phase5", "sm_banner.txt")
            order = os.path.join(root, "orders", "launch.txt")
            os.makedirs(os.path.dirname(lhco), exist_ok=True)
            with open(lhco, "w", encoding="utf-8") as handle:
                handle.write("event\n")
            with open(banner, "w", encoding="utf-8") as handle:
                handle.write("banner\n")
            os.makedirs(os.path.dirname(order), exist_ok=True)
            with open(order, "w", encoding="utf-8") as handle:
                handle.write("set sde_strategy = 0\nset hard_survey = 2\n")
            unit = {
                "status": "accepted",
                "requested_event_count": 100,
                "attempts": [{
                    "attempt_index": 0,
                    "survey_profile": "sde0_hs2",
                    "status": "completed",
                    "result": {"launch": {"order_file_path": order}},
                }],
                "merged_outputs": [{
                    "label": "sm",
                    "lhco_path": lhco,
                    "loaded_lhco_event_count": 10,
                    "requested_event_count": 100,
                    "source_banners_retained": [banner],
                    "merged_cross_section_pb": 1.0,
                }],
                "warnings": [{"fraction": 0.1}],
            }
            write_json(
                os.path.join(root, "data", "phase5", "event_count_recovery.json"),
                {
                    "required_units": ["sm", "np_o_1"],
                    "units": {"sm": unit},
                    "missing_units": ["np_o_1"],
                    "incomplete_units": [],
                    "status": "recovery_incomplete",
                },
            )
            checks = _recovery_metadata_checks(root)
            self.assertTrue(any(not item["ok"] for item in checks))

            unit_np = dict(unit)
            unit_np["merged_outputs"] = [dict(unit["merged_outputs"][0], label="np_o_1")]
            write_json(
                os.path.join(root, "data", "phase5", "event_count_recovery.json"),
                {
                    "required_units": ["sm", "np_o_1"],
                    "units": {"sm": unit, "np_o_1": unit_np},
                    "missing_units": [],
                    "incomplete_units": [],
                    "status": "accepted",
                },
            )
            checks = _recovery_metadata_checks(root)
            self.assertTrue(all(item["ok"] for item in checks), checks)

    def test_phase6_progress_requires_every_operator_completed(self):
        with tempfile.TemporaryDirectory() as root:
            write_json(os.path.join(root, "data", "phase3", "operator_claims.json"), {"o_1": {}, "o_2": {}})
            progress_path = os.path.join(root, "data", "phase6", "phase6_progress.json")
            write_json(progress_path, {"operators": {"o_1": {"status": "completed", "completed_labels": [f"f{i}" for i in range(11)]}}})
            self.assertFalse(_phase6_progress_checks(root)[0]["ok"])
            write_json(progress_path, {"operators": {
                key: {"status": "completed", "completed_labels": [f"f{i}" for i in range(11)]}
                for key in ("o_1", "o_2")
            }})
            self.assertTrue(_phase6_progress_checks(root)[0]["ok"])

    def test_final_audit_artifact_schemas(self):
        with tempfile.TemporaryDirectory() as root:
            write_json(os.path.join(root, "audit_expected_outputs.json"), {
                "status": "PASS",
                "checks": [],
                "failures": [],
                "warnings": [],
                "expected_count": 0,
            })
            categories = {
                key: {"passed": 1, "failed": 0, "details": []}
                for key in (
                    "research_contract",
                    "deliverables_contract",
                    "file_existence",
                    "numerical_sanity",
                    "cross_phase_consistency",
                )
            }
            write_json(os.path.join(root, "audit_report.json"), {
                "status": "PASS",
                "checks": categories,
                "abort_reasons": [],
                "warnings": [],
                "manuscript_validation_status": "pass",
            })
            self.assertTrue(all(item["ok"] for item in _final_audit_artifact_checks(root)))

    def test_replay_algorithm_lock_matches_actual_run(self):
        with tempfile.TemporaryDirectory() as root:
            replay_root = os.path.join(root, "replay")
            step_path = os.path.join(replay_root, "steps", "phase7.py")
            os.makedirs(os.path.dirname(step_path), exist_ok=True)
            with open(step_path, "w", encoding="utf-8") as handle:
                handle.write("print('train')\n")
            with open(step_path, "rb") as handle:
                step_sha = hashlib.sha256(handle.read()).hexdigest()
            write_json(
                os.path.join(root, "data", "phase7", "algorithm_comparison.json"),
                {"anchor": {"bdt": {}}},
            )
            write_json(
                os.path.join(root, "data", "phase7", "algorithm_descriptions.json"),
                {"algorithms": {"bdt": {
                    "hyperparameters": {"depth": 3},
                    "score_definition": "predict_proba[:, 1]",
                }}},
            )
            write_json(
                os.path.join(root, "data", "phase9", "algorithm_selection.json"),
                {
                    "selected_algorithm": "bdt",
                    "selection_scope": "anchor_operator_only",
                    "selection_criterion": "narrowest_anchor_S2_constraint_width",
                    "selection_rationale": "The common strategy is adequate.",
                    "selection_evidence": ["data/phase8/threshold_optimization.json"],
                },
            )
            lock = {
                "trained_algorithms": [{
                    "key": "bdt",
                    "implementation": "example.BDT",
                    "hyperparameters": {"depth": 3},
                    "score_definition": "predict_proba[:, 1]",
                    "model_output": "algorithms/anchor_bdt.pkl",
                }],
                "production_algorithm": "bdt",
                "selection_scope": "anchor_operator_only",
                "operator_selections": {},
                "selection_provenance": {
                    "selection_method": "narrowest_anchor_S2_constraint_width",
                    "selection_rationale": "The common strategy is adequate.",
                    "selection_evidence": ["data/phase8/threshold_optimization.json"],
                    "source": "data/phase9/algorithm_selection.json",
                },
                "packaged_files": {"steps/phase7.py": step_sha},
            }
            lock["lock_sha256"] = _canonical_sha256(lock)
            write_json(
                os.path.join(replay_root, "replay_manifest.json"),
                {
                    "algorithm_lock": lock,
                    "steps": [{
                        "phase": "7",
                        "command": ["python", "steps/phase7.py"],
                        "sha256": {"steps/phase7.py": step_sha},
                    }],
                },
            )
            checks = _replay_algorithm_lock_checks(root)
            self.assertEqual(len(checks), 1)
            self.assertTrue(checks[0]["ok"], checks[0])

            with open(os.path.join(replay_root, "replay_manifest.json"), encoding="utf-8") as handle:
                manifest = json.load(handle)
            manifest["algorithm_lock"].pop("selection_scope")
            manifest["algorithm_lock"]["lock_sha256"] = _canonical_sha256(
                {
                    key: value for key, value in manifest["algorithm_lock"].items()
                    if key != "lock_sha256"
                }
            )
            write_json(os.path.join(replay_root, "replay_manifest.json"), manifest)
            self.assertFalse(_replay_algorithm_lock_checks(root)[0]["ok"])

    def test_replay_package_static_checks_require_real_files_and_checksums(self):
        with tempfile.TemporaryDirectory() as root:
            replay_root = os.path.join(root, "replay")
            os.makedirs(replay_root, exist_ok=True)
            for name in (
                "run_config.json",
                "research_contract.json",
                "deliverables_contract.json",
                "contract_lock.json",
            ):
                value = {"name": name}
                write_json(os.path.join(root, name), value)
                write_json(os.path.join(replay_root, name), value)
            output = "data/phase2/environment_manifest.json"
            with open(os.path.join(replay_root, "data_files_report.md"), "w", encoding="utf-8") as handle:
                handle.write(
                    "# Replay usage\n\n"
                    "Run `./replay.sh`. After completion, results are stored below "
                    "`replayed-results/data/`.\n"
                )
            with open(os.path.join(replay_root, "replay.sh"), "w", encoding="utf-8") as handle:
                handle.write("#!/usr/bin/env bash\nset -euo pipefail\nexit 99\n")
            step_hashes = {}
            for phase in range(2, 10):
                rel = f"steps/phase{phase}.py"
                path = os.path.join(replay_root, rel)
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(f"print('phase {phase}')\n")
                with open(path, "rb") as handle:
                    step_hashes[rel] = hashlib.sha256(handle.read()).hexdigest()

            def file_sha(rel):
                with open(os.path.join(replay_root, rel), "rb") as handle:
                    return hashlib.sha256(handle.read()).hexdigest()

            manifest = {
                "schema_version": "1.0",
                "entrypoint": "replay.sh",
                "phase_order": [str(phase) for phase in range(2, 10)],
                "default_output": "replayed-results",
                "report": "data_files_report.md",
                "source_inputs": [],
                "external_dependencies": [
                    {
                        "name": name,
                        "path": f"/opt/{name}",
                        "version": "test",
                        "sha256": None,
                        "checksum_unavailable_reason": "fake test dependency",
                    }
                    for name in (
                        "MadGraph5_aMC@NLO",
                        "Pythia8",
                        "Delphes",
                        "root2lhco",
                        "CutExperiment",
                        "Python",
                    )
                ],
                "steps": [
                    {
                        "phase": str(phase),
                        "command": ["python", f"steps/phase{phase}.py"],
                        "inputs": ["run_config.json"],
                        "outputs": [output] if phase == 2 else [],
                        "sha256": {f"steps/phase{phase}.py": step_hashes[f"steps/phase{phase}.py"]},
                    }
                    for phase in range(2, 10)
                ],
            }
            manifest["package_sha256"] = {
                rel: file_sha(rel)
                for rel in (
                    "replay.sh",
                    "run_config.json",
                    "research_contract.json",
                    "deliverables_contract.json",
                    "contract_lock.json",
                    "data_files_report.md",
                    *step_hashes.keys(),
                )
            }
            write_json(os.path.join(replay_root, "replay_manifest.json"), manifest)
            resolved = {
                "pending_rules": [],
                "resolved": [{"phase": "2", "path": output}],
            }
            with patch("scripts.audit_expected_outputs.resolve_contract", return_value=resolved):
                checks = _replay_package_checks(root)
            self.assertTrue(checks[0]["ok"], checks[0])

            unlisted = os.path.join(replay_root, "support", "unlisted.py")
            os.makedirs(os.path.dirname(unlisted), exist_ok=True)
            with open(unlisted, "w", encoding="utf-8") as handle:
                handle.write("print('unlisted')\n")
            with patch("scripts.audit_expected_outputs.resolve_contract", return_value=resolved):
                checks = _replay_package_checks(root)
            self.assertFalse(checks[0]["ok"])
            self.assertTrue(any("unlisted.py" in value for value in checks[0]["package_checksum_errors"]))
            os.remove(unlisted)

            manifest["steps"][0]["sha256"]["steps/phase2.py"] = "0" * 64
            write_json(os.path.join(replay_root, "replay_manifest.json"), manifest)
            with patch("scripts.audit_expected_outputs.resolve_contract", return_value=resolved):
                checks = _replay_package_checks(root)
            self.assertFalse(checks[0]["ok"])
            self.assertTrue(checks[0]["checksum_errors"])


if __name__ == "__main__":
    unittest.main()

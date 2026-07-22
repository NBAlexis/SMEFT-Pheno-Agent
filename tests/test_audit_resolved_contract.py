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
    _phase9_strategy_checks,
    _phase3_runner_manifest_checks,
    _replay_algorithm_lock_checks,
    _replay_package_checks,
    _resolved_deliverable_checks,
    _validate_declared_artifact,
)


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle)


class ResolvedContractAuditTests(unittest.TestCase):
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
            write_json(
                os.path.join(root, "mg5_processes", "cleanup_log.json"),
                {
                    "expected_process_dirs": ["proc"],
                    "moved_process_dirs": ["mg5_processes/proc_archive"],
                    "missing_process_dirs": [],
                    "expected_order_files": ["order.txt"],
                    "moved_order_files": ["orders/order.txt"],
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
                    "expected_process_dirs": ["proc"],
                    "moved_process_dirs": ["mg5_processes/proc_archive"],
                    "missing_process_dirs": [],
                    "expected_order_files": ["order.txt"],
                    "moved_order_files": ["orders/order.txt"],
                    "missing_order_files": [],
                    "deleted_large_files": [
                        "proc/Events/run_01/tag_1_delphes_events.root",
                        "proc/Events/run_01/tag_1_pythia8_events.hepmc.gz",
                    ],
                },
            )
            checks = _cleanup_log_checks(root)
            self.assertTrue(checks[-1]["ok"], checks[-1])

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
                {"selected_algorithm": "bdt"},
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
                "selection_provenance": {
                    "selection_method": "narrowest_anchor_S2_interval",
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

    def test_replay_package_requires_bounded_monte_carlo_tolerances(self):
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
                handle.write(f"# Data files\n\n`{output}`\n")
            manifest = {
                "source_inputs": [],
                "steps": [
                    {
                        "phase": str(phase),
                        "command": ["python", f"steps/phase{phase}.py"],
                        "inputs": ["run_config.json"],
                        "outputs": [output] if phase == 2 else [],
                    }
                    for phase in range(2, 10)
                ],
                "monte_carlo_comparison": {
                    "production_inputs_exclude_reference_results": True,
                    "combined_standard_error_multiplier": 3.0,
                    "fallback_limits": {
                        "cross_sections": {"difference": "relative", "maximum": 0.10},
                        "auc_and_thresholds": {"difference": "absolute", "maximum": 0.05},
                        "fit_coefficients_and_constraint_endpoints": {"difference": "relative", "maximum": 0.20},
                    },
                },
            }
            write_json(os.path.join(replay_root, "replay_manifest.json"), manifest)
            resolved = {
                "pending_rules": [],
                "resolved": [{"phase": "2", "path": output}],
            }
            with patch("scripts.audit_expected_outputs.resolve_contract", return_value=resolved):
                checks = _replay_package_checks(root)
            self.assertTrue(checks[0]["ok"], checks[0])

            manifest["monte_carlo_comparison"]["fallback_limits"]["cross_sections"]["maximum"] = 0.5
            write_json(os.path.join(replay_root, "replay_manifest.json"), manifest)
            with patch("scripts.audit_expected_outputs.resolve_contract", return_value=resolved):
                checks = _replay_package_checks(root)
            self.assertFalse(checks[0]["ok"])


if __name__ == "__main__":
    unittest.main()

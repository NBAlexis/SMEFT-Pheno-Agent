import hashlib
import json
import os
import tempfile
import unittest

from scripts.audit_expected_outputs import (
    _canonical_sha256,
    _expected_files,
    _final_audit_artifact_checks,
    _phase3_runner_manifest_checks,
    _replay_algorithm_lock_checks,
    _resolved_deliverable_checks,
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
                    "random_seed": 7,
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
                    "random_seed": 7,
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


if __name__ == "__main__":
    unittest.main()

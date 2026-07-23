import copy
import json
import os
import shutil
import tempfile
import unittest

from scripts.research_contract import (
    FIXED_METHOD_REQUIREMENTS,
    _sha256,
    init_contracts,
    resolve_contract,
    verify_contracts,
)
from scripts.audit_expected_outputs import audit_phase_deliverables


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE = os.path.join(ROOT, "reference", "deliverables-contract-template.json")


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle)


def base_config(workdir):
    return {
        "version": "1.0",
        "collected_at": "2026-01-01T00:00:00Z",
        "execution": {"mode": "ssh", "ssh_target": "old-host"},
        "madgraph_path": "/old/MG5",
        "cutexperiment_path": "/old/CutExperiment",
        "workdir": workdir,
        "process": "e+ e- > a a",
        "collider_type": "ee",
        "process_validation": {"status": "ok"},
        "madspin": {"enabled": False},
        "models": ["AQGCm_UFO"],
        "energy": [10.0],
        "ebeam_electron": None,
        "ebeam_proton": None,
        "luminosity": [1000.0],
        "delphes_card": "/old/cards/delphes_card_CEPC.tcl",
        "polarization": None,
        "algorithms": ["bdt", "mlp"],
        "analysis_notes": {
            "focused_operators": [],
            "manuscript_preferences": [],
            "additional_requirements": [],
        },
        "debug": False,
        "event_counts_locked": True,
        "locked_event_counts": {
            "nev_phase3": 10000,
            "nev_phase4": 10000,
            "nev_sm": 500000,
            "nev_np": 100000,
            "nev_scan": 1000000,
        },
        "run_configurations": [
            {
                "energy": 10.0,
                "luminosity": 1000.0,
                "ebeam1": 5000.0,
                "ebeam2": 5000.0,
                "run_dir": "E10_L1000",
            }
        ],
    }


class ResearchContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.results = os.path.join(self.temp.name, "results")
        self.mg5 = os.path.join(self.temp.name, "MG5")
        model_dir = os.path.join(self.mg5, "models", "AQGCm_UFO")
        card_dir = os.path.join(self.mg5, "Delphes", "cards")
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(card_dir, exist_ok=True)
        with open(os.path.join(model_dir, "parameters.py"), "w", encoding="utf-8") as handle:
            handle.write("MODEL = 'AQGCm_UFO'\n")
        with open(os.path.join(card_dir, "delphes_card_CEPC.tcl"), "w", encoding="utf-8") as handle:
            handle.write("set DetectorName CEPC\n")
        self.config_path = os.path.join(self.results, "run_config.json")
        self.config = base_config(self.temp.name)
        self.config["madgraph_path"] = self.mg5
        self.config["delphes_card"] = "delphes_card_CEPC.tcl"
        write_json(self.config_path, self.config)
        init_contracts(self.config_path, self.results, TEMPLATE)

    def tearDown(self):
        self.temp.cleanup()

    def test_init_is_idempotent_but_does_not_overwrite_different_contract(self):
        report = init_contracts(self.config_path, self.results, TEMPLATE)
        self.assertEqual(report["research_contract_action"], "unchanged")
        contract_path = os.path.join(self.results, "research_contract.json")
        with open(contract_path, encoding="utf-8") as handle:
            contract = json.load(handle)
        contract["objective"]["process"] = "changed"
        write_json(contract_path, contract)
        with self.assertRaises(ValueError):
            init_contracts(self.config_path, self.results, TEMPLATE)

    def test_scientific_drift_is_rejected(self):
        changed = copy.deepcopy(self.config)
        changed["luminosity"] = [2000.0]
        changed["run_configurations"][0]["luminosity"] = 2000.0
        write_json(self.config_path, changed)
        report = verify_contracts(self.config_path, self.results)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("scientific objective" in item for item in report["errors"]))

    def test_debug_mode_and_its_reduced_counts_are_frozen(self):
        debug_results = os.path.join(self.temp.name, "debug-results")
        debug_config_path = os.path.join(debug_results, "run_config.json")
        debug_config = copy.deepcopy(self.config)
        debug_config["debug"] = True
        debug_config["locked_event_counts"] = {
            "nev_phase3": 1000,
            "nev_phase4": 1000,
            "nev_sm": 50000,
            "nev_np": 10000,
            "nev_scan": 100000,
        }
        write_json(debug_config_path, debug_config)
        init_contracts(debug_config_path, debug_results, TEMPLATE)
        self.assertEqual(verify_contracts(debug_config_path, debug_results)["status"], "ok")

        changed = copy.deepcopy(debug_config)
        changed["debug"] = False
        changed["locked_event_counts"] = {
            "nev_phase3": 10000,
            "nev_phase4": 10000,
            "nev_sm": 500000,
            "nev_np": 100000,
            "nev_scan": 1000000,
        }
        write_json(debug_config_path, changed)
        report = verify_contracts(debug_config_path, debug_results)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("scientific objective" in item for item in report["errors"]))

    def test_technical_path_migration_is_allowed(self):
        changed = copy.deepcopy(self.config)
        new_mg5 = os.path.join(self.temp.name, "migrated", "MG5")
        shutil.copytree(self.mg5, new_mg5)
        changed["execution"] = {"mode": "wsl2", "wsl_distro": "Ubuntu"}
        changed["madgraph_path"] = new_mg5
        changed["cutexperiment_path"] = "/new/CutExperiment"
        changed["workdir"] = "/new/workdir"
        changed["delphes_card"] = os.path.join(
            new_mg5, "Delphes", "cards", "delphes_card_CEPC.tcl"
        )
        changed["run_configurations"][0]["run_dir"] = "renamed-run"
        write_json(self.config_path, changed)
        self.assertEqual(verify_contracts(self.config_path, self.results)["status"], "ok")

    def test_algorithm_change_is_not_research_objective_drift(self):
        changed = copy.deepcopy(self.config)
        changed["algorithms"] = ["different", "technical", "set"]
        write_json(self.config_path, changed)
        self.assertEqual(verify_contracts(self.config_path, self.results)["status"], "ok")

    def test_fixed_method_boundaries_and_phase10_items_are_frozen(self):
        with open(os.path.join(self.results, "research_contract.json"), encoding="utf-8") as handle:
            research = json.load(handle)
        self.assertEqual(
            research["objective"]["fixed_method_requirements"],
            FIXED_METHOD_REQUIREMENTS,
        )
        with open(os.path.join(self.results, "deliverables_contract.json"), encoding="utf-8") as handle:
            deliverables = json.load(handle)
        frozen_items = deliverables["template"]["phase10_required_manuscript_items"]
        with open(
            os.path.join(ROOT, "reference", "manuscript-checklist-required-ids.json"),
            encoding="utf-8",
        ) as handle:
            canonical_items = json.load(handle)["required_items"]
        self.assertEqual(frozen_items, canonical_items)

        research["objective"]["fixed_method_requirements"][
            "machine_learning_event_selection"
        ] = "traditional cuts allowed"
        research["objective_sha256"] = _sha256(research["objective"])
        write_json(os.path.join(self.results, "research_contract.json"), research)
        self.assertEqual(
            verify_contracts(self.config_path, self.results)["status"],
            "error",
        )

    def test_model_or_card_content_drift_is_rejected(self):
        model_file = os.path.join(self.mg5, "models", "AQGCm_UFO", "parameters.py")
        with open(model_file, "a", encoding="utf-8") as handle:
            handle.write("DRIFT = True\n")
        report = verify_contracts(self.config_path, self.results)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("scientific objective" in item for item in report["errors"]))

    def test_deliverables_template_tamper_is_rejected(self):
        path = os.path.join(self.results, "deliverables_contract.json")
        with open(path, encoding="utf-8") as handle:
            contract = json.load(handle)
        contract["template"]["rules"].pop()
        contract["template_sha256"] = _sha256(contract["template"])
        write_json(path, contract)
        report = verify_contracts(self.config_path, self.results)
        self.assertEqual(report["status"], "error")
        self.assertTrue(any("different deliverables" in item for item in report["errors"]))

    def test_resolve_expands_dynamic_dimensions_and_format(self):
        root = self.results
        write_json(
            os.path.join(root, "data", "phase3", "operator_claims.json"),
            {"o_1": {}, "o_2": {}},
        )
        write_json(
            os.path.join(root, "data", "phase3", "model_status.json"),
            {"models": [{"result_json": "results/data/phase3/results/model_a.json"}]},
        )
        write_json(
            os.path.join(root, "data", "phase6", "scan_manifest.json"),
            {"o_1": {"labels": ["f0", "f1"]}, "o_2": {"labels": ["f0"]}},
        )
        write_json(
            os.path.join(root, "data", "phase7", "algorithm_comparison.json"),
            {"anchor": {"bdt": {}, "mlp": {}}},
        )
        write_json(
            os.path.join(root, "data", "phase10", "manuscript_build_environment.json"),
            {"pdf_required": True},
        )
        write_json(
            os.path.join(root, "data", "phase10", "manuscript_evidence.json"),
            {"figures": {"feynman_diagrams": [{"missing_reason": "not retained"}]}},
        )
        write_json(
            os.path.join(root, "replay", "replay_manifest.json"),
            {
                "steps": [
                    {
                        "command": ["python", "steps/phase2.py"],
                        "sha256": {"support/report.py": "abc"},
                    }
                ]
            },
        )
        report = resolve_contract(self.config_path, root, self.results)
        paths = {item["path"] for item in report["resolved"]}
        self.assertIn("data/phase6/np_o_1_f1.lhco", paths)
        self.assertIn("data/phase8/scores/mlp/np_o_2_f0_scores.csv", paths)
        self.assertIn("data/phase8/shared_f5_background.json", paths)
        self.assertIn("data/phase8/scores/mlp/shared_f5_scores.csv", paths)
        self.assertIn("data/phase8/csfit_o_2_bdt.json", paths)
        self.assertIn("data/phase3/results/model_a.json", paths)
        self.assertNotIn("results/data/phase3/results/model_a.json", paths)
        self.assertIn("replay/steps/phase2.py", paths)
        self.assertIn("replay/support/report.py", paths)
        self.assertIn("manuscript.pdf", paths)
        self.assertNotIn("manuscript.html", paths)
        fit_item = next(
            item for item in report["resolved"]
            if item["path"] == "data/phase8/csfit_o_1_bdt.json"
        )
        self.assertIn("fit_intercept_fixed", fit_item["required_keys"])
        self.assertEqual(report["status"], "resolved")

    def test_missing_manifests_keep_rules_pending(self):
        report = resolve_contract(self.config_path, self.results, self.results)
        self.assertEqual(report["status"], "pending")
        pending_ids = {item["rule_id"] for item in report["pending_rules"]}
        self.assertIn("phase5.per-operator", pending_ids)
        self.assertIn("phase10.pdf", pending_ids)

    def test_zero_operator_result_excludes_downstream_contract(self):
        write_json(
            os.path.join(self.results, "data", "phase3", "operator_claims.json"),
            {},
        )
        write_json(
            os.path.join(self.results, "data", "phase3", "model_status.json"),
            {},
        )
        report = resolve_contract(self.config_path, self.results, self.results)
        paths = {item["path"] for item in report["resolved"]}
        excluded_ids = {item["rule_id"] for item in report["excluded_rules"]}
        self.assertIn("data/phase3/phase3_report.txt", paths)
        self.assertNotIn("data/phase3/anchor.json", paths)
        self.assertIn("phase4.ranges", excluded_ids)
        self.assertIn("phase12.audit", excluded_ids)
        self.assertEqual(report["status"], "resolved")

    def test_phase2_audit_resolves_only_phase2_rules(self):
        with open(os.path.join(self.results, "research_contract.json"), encoding="utf-8") as handle:
            objective_sha256 = json.load(handle)["objective_sha256"]
        with open(os.path.join(self.results, "workflow.log"), "w", encoding="utf-8") as handle:
            json.dump({
                "level": "step",
                "phase": "2",
                "event": "completed",
                "objective_sha256": objective_sha256,
            }, handle)
            handle.write("\n")
        write_json(
            os.path.join(self.results, "data", "phase2", "environment_manifest.json"),
            {"status": "ok"},
        )
        report = audit_phase_deliverables(self.temp.name, "2")
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertFalse(any(
            check.get("phase") not in (None, "2")
            for check in report["checks"]
        ))

    def test_phase3_audit_passes_with_minimal_fake_deliverables(self):
        write_json(
            os.path.join(self.results, "data", "phase3", "operator_claims.json"),
            {
                "o_1": {
                    "model": "AQGCm_UFO",
                    "anoinput_idx": 1,
                    "name": "fM0",
                }
            },
        )
        write_json(
            os.path.join(self.results, "data", "phase3", "cross_sections.json"),
            {
                "AQGCm_UFO:fM0": {
                    "sigma": 1.23e-3,
                    "global_idx": 1,
                }
            },
        )
        write_json(
            os.path.join(self.results, "data", "phase3", "model_status.json"),
            {
                "AQGCm_UFO": {
                    "has_feynman_diagrams": True,
                    "coefficient_count": 1,
                    "tested_count": 1,
                    "create_np_result_json": "results/data/phase3/results/AQGCm_UFO_create_np.json",
                    "coefficients": {
                        "fM0": {
                            "c_default": 0.0,
                            "sigma": 1.23e-3,
                            "result_json": "results/data/phase3/results/AQGCm_UFO_fM0.json",
                            "global_idx": 1,
                        }
                    },
                }
            },
        )
        write_json(
            os.path.join(self.results, "data", "phase3", "anchor.json"),
            {
                "global_idx": 1,
                "model": "AQGCm_UFO",
                "anoinput_idx": 1,
                "name": "fM0",
            },
        )
        write_json(
            os.path.join(self.results, "data", "phase3", "results", "AQGCm_UFO_create_np.json"),
            {
                "status": "completed",
                "process_mode": "create_np",
                "event_generator": "MadGraph5",
            },
        )
        phase3_lhco = os.path.join(
            self.results, "data", "phase3", "results", "AQGCm_UFO_fM0.lhco"
        )
        os.makedirs(os.path.dirname(phase3_lhco), exist_ok=True)
        with open(phase3_lhco, "w", encoding="utf-8") as handle:
            handle.write("0 1 0 0 0 0 0 0 0 0 0\n")
        write_json(
            os.path.join(self.results, "data", "phase3", "results", "AQGCm_UFO_fM0.json"),
            {
                "status": "completed",
                "process_mode": "pure_np",
                "event_generator": "MadGraph5",
                "detector_simulation": "Delphes",
                "analysis_event_format": "LHCO_from_Delphes_ROOT",
                "delphes_card": "delphes_card_CEPC.tcl",
                "nevents": 10000,
                "outputs": [{
                    "cross_section_pb": 1.23e-3,
                    "lhco_path": phase3_lhco,
                    "loaded_lhco_event_count": 1000,
                }],
            },
        )
        report = audit_phase_deliverables(self.temp.name, "3")
        self.assertEqual(report["status"], "PASS", report["failures"])
        self.assertTrue(any(
            check.get("source") == "phase3_complete_coefficient_loop"
            for check in report["checks"]
        ))


if __name__ == "__main__":
    unittest.main()

import copy
import json
import os
import shutil
import tempfile
import unittest

from scripts.research_contract import (
    _sha256,
    init_contracts,
    resolve_contract,
    verify_contracts,
)


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
        "analysis_notes": "Use the full operator set",
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
        self.assertIn("data/phase8/csfit_o_2_bdt.json", paths)
        self.assertIn("data/phase3/results/model_a.json", paths)
        self.assertNotIn("results/data/phase3/results/model_a.json", paths)
        self.assertIn("replay/steps/phase2.py", paths)
        self.assertIn("replay/support/report.py", paths)
        self.assertIn("manuscript.pdf", paths)
        self.assertNotIn("manuscript.html", paths)
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


if __name__ == "__main__":
    unittest.main()

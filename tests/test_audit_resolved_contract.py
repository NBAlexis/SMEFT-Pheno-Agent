import json
import os
import tempfile
import unittest

from scripts.audit_expected_outputs import _resolved_deliverable_checks


def write_json(path, value):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(value, handle)


class ResolvedContractAuditTests(unittest.TestCase):
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
                    "pending_rules": [],
                    "resolved": [
                        {
                            "rule_id": "data",
                            "path": "data/result.json",
                            "absolute_path": data_path,
                            "type": "json",
                        },
                        {
                            "rule_id": "plots",
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
                    "pending_rules": [{"rule_id": "phase7", "reason": "missing"}],
                    "resolved": [],
                },
            )
            checks = _resolved_deliverable_checks(root)
            self.assertFalse(checks[0]["ok"])


if __name__ == "__main__":
    unittest.main()

import json
import os
import tempfile
import unittest

from scripts.workflow_logger import WorkflowLogger


class WorkflowLoggerPhaseGateTests(unittest.TestCase):
    def test_failed_step_does_not_allow_phase_completion(self):
        with tempfile.TemporaryDirectory() as workdir:
            logger = WorkflowLogger(workdir)
            logger._audit_phase_deliverables = lambda phase: {"status": "PASS"}
            logger.step_fail("3", "coefficient_loop", "failed")
            with self.assertRaises(RuntimeError):
                logger.phase_complete("3")
            self.assertFalse(logger.is_phase_completed("3"))

    def test_failed_delivery_check_does_not_write_completed_record(self):
        with tempfile.TemporaryDirectory() as workdir:
            logger = WorkflowLogger(workdir)
            logger.step_complete("3", "coefficient_loop")
            logger._audit_phase_deliverables = lambda phase: {
                "status": "FAIL",
                "failures": [{
                    "rel_path": "data/phase3/model_status.json",
                    "failure_code": "missing",
                    "failure_reason": "missing",
                }],
            }
            with self.assertRaises(RuntimeError):
                logger.phase_complete("3")
            self.assertFalse(logger.is_phase_completed("3"))

    def test_completed_step_and_passing_delivery_check_allow_completion(self):
        with tempfile.TemporaryDirectory() as workdir:
            logger = WorkflowLogger(workdir)
            logger.step_complete("3", "coefficient_loop")
            logger._audit_phase_deliverables = lambda phase: {"status": "PASS"}
            logger.phase_complete("3")
            self.assertTrue(logger.is_phase_completed("3"))
            with open(logger.log_path, "r", encoding="utf-8") as handle:
                records = [json.loads(line) for line in handle if line.strip()]
            self.assertTrue(any(
                record.get("level") == "phase" and record.get("event") == "completed"
                for record in records
            ))

    def test_phase_fail_requires_structured_failure_evidence(self):
        with tempfile.TemporaryDirectory() as workdir:
            logger = WorkflowLogger(workdir)
            with self.assertRaises(RuntimeError):
                logger.phase_fail("6", "conversion failed")
            evidence_path = os.path.join(
                workdir, "results", "failures", "phase6_failure.json"
            )
            os.makedirs(os.path.dirname(evidence_path), exist_ok=True)
            with open(evidence_path, "w", encoding="utf-8") as handle:
                json.dump({
                    "technical_cause": "converter cannot read the source format",
                    "affected_deliverables": ["data/phase6/np_o_1_f0.lhco"],
                    "attempts": [{
                        "command_or_code_path": "scripts/convert_root_to_lhco.py",
                        "change_tested": "repaired input branch mapping",
                        "return_code": 1,
                        "stdout_path": "logs/stdout.txt",
                        "stderr_path": "logs/stderr.txt",
                    }],
                    "evidence_paths": ["logs/stderr.txt"],
                    "why_no_remaining_method_can_preserve_the_contract": "all available converters reject the required source file",
                }, handle)
            logger.phase_fail("6", "conversion failed")
            self.assertEqual(logger.latest_phase_event("6"), "failed")


if __name__ == "__main__":
    unittest.main()

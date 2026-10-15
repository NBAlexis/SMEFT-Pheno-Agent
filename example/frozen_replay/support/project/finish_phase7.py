#!/usr/bin/env python3
"""Phase 7 finisher: verify the audit passes, then record phase completion.

The Phase 7 driver already produced every artifact and step record; only the
feature-CSV header convention blocked phase_complete. After the in-place
header fix, this script re-runs the delivery audit and completes the phase.
"""
import json
import subprocess
import sys

WORKDIR = "/mnt/e/SMEFT-Pheno-Agent-GLM-test"
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill") if False else "/mnt/e/SMEFT-Pheno-Agent-GLM-test/.smeft-skill"
sys.path.insert(0, SKILL_RUNTIME)
from scripts.workflow_logger import WorkflowLogger

import os

logger = WorkflowLogger(WORKDIR, None)
proc = subprocess.run(
    ["/mnt/e/SMEFT-Pheno-Agent-GLM-test/venv/bin/python",
     os.path.join(SKILL_RUNTIME, "scripts", "audit_expected_outputs.py"),
     WORKDIR, "--phase", "7"],
    cwd=SKILL_RUNTIME, capture_output=True, text=True, timeout=600,
)
try:
    report = json.loads(proc.stdout)
except json.JSONDecodeError:
    raise RuntimeError(f"audit did not return JSON: rc={proc.returncode} "
                       f"stderr={proc.stderr[-800:]}")
failures = report.get("failures") or []
if failures:
    print(json.dumps(failures[:5], indent=1)[:2000])
    raise RuntimeError(f"phase 7 audit still failing: {len(failures)} items")
logger.phase_complete("7", message="ML training delivered (header fix applied)")
print("PHASE7_COMPLETED")

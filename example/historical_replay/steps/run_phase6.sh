#!/usr/bin/env bash
set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${SMEFT_PYTHON:-/mnt/e/SMEFT-Pheno-Agent-GLM-test/venv/bin/python}"
"$PYTHON" "$DIR/phase6_scan.py"
scan_rc=$?
"$PYTHON" "$DIR/phase6_smart_recovery.py"
rc=$?
if [[ $rc -ne 0 && $scan_rc -ne 0 ]]; then exit 1; fi
exit $rc

#!/usr/bin/env python3
"""Manifest-driven output audit for the SMEFT-ML workflow."""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from typing import Any, Dict, Iterable, List, Optional


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def _result_root(workdir: str, run_dir: Optional[str]) -> str:
    if run_dir:
        return os.path.join(workdir, "results", run_dir)
    return os.path.join(workdir, "results")


def _exists_nonempty(path: str) -> Dict[str, Any]:
    return {
        "path": path,
        "exists": os.path.exists(path),
        "size": os.path.getsize(path) if os.path.exists(path) else 0,
        "ok": os.path.exists(path) and os.path.getsize(path) > 0,
    }


def _operators(root: str) -> List[str]:
    claims_path = os.path.join(root, "data", "phase3", "operator_claims.json")
    if not os.path.exists(claims_path):
        return []
    claims = _load_json(claims_path)
    return sorted(claims.keys(), key=lambda k: int(str(k).split("_")[-1]))


def _scan_labels(root: str, operators: Iterable[str]) -> Dict[str, List[str]]:
    manifest_path = os.path.join(root, "data", "phase6", "scan_manifest.json")
    manifest = _load_json(manifest_path) if os.path.exists(manifest_path) else {}
    labels = {}
    for op in operators:
        op_manifest = manifest.get(op, {})
        labels[op] = list(op_manifest.get("labels") or [f"f{i}" for i in range(11)])
    return labels


def _algorithm_names(root: str) -> List[str]:
    path = os.path.join(root, "data", "phase7", "algorithm_comparison.json")
    if not os.path.exists(path):
        return []
    data = _load_json(path)
    return sorted((data.get("anchor") or {}).keys())


def _expected_files(root: str) -> List[Dict[str, Any]]:
    expected: List[Dict[str, Any]] = []
    operators = _operators(root)
    scan_labels = _scan_labels(root, operators)
    algorithms = _algorithm_names(root)

    fixed = [
        ("data/phase3/operator_claims.json", "abort"),
        ("data/phase3/cross_sections.json", "abort"),
        ("data/phase3/anchor.json", "abort"),
        ("data/phase4/coefficient_ranges.json", "abort"),
        ("data/phase4/sm_baseline.json", "abort"),
        ("data/phase5/sm.lhco", "abort"),
        ("data/phase5/np_anchor.lhco", "abort"),
        ("data/phase5/event_count_recovery.json", "abort"),
        ("data/phase6/event_count_recovery.json", "abort"),
        ("data/phase6/scan_manifest.json", "abort"),
        ("data/phase7/sm.csv", "abort"),
        ("data/phase7/np_anchor.csv", "abort"),
        ("data/phase7/event_counts.json", "abort"),
        ("data/phase7/algorithm_comparison.json", "abort"),
        ("data/phase8/threshold_optimization.json", "abort"),
        ("data/phase8/scan_event_counts.json", "abort"),
        ("data/phase9/constraint_table.json", "abort"),
    ]
    for rel, severity in fixed:
        expected.append({"rel_path": rel, "severity": severity, "source": "fixed"})

    for op in operators:
        expected.append({"rel_path": f"data/phase5/np_{op}.lhco", "severity": "abort", "source": "operator_claims"})
        expected.append({"rel_path": f"data/phase7/np_{op}.csv", "severity": "abort", "source": "operator_claims"})
        for label in scan_labels.get(op, []):
            expected.append({"rel_path": f"data/phase6/np_{op}_{label}.lhco", "severity": "abort", "source": "scan_manifest"})
            expected.append({"rel_path": f"data/phase8/csv/np_{op}_{label}.csv", "severity": "abort", "source": "scan_manifest"})
            for alg in algorithms:
                expected.append({
                    "rel_path": f"data/phase8/scores/{alg}/np_{op}_{label}_scores.csv",
                    "severity": "abort",
                    "source": "algorithm_comparison+scan_manifest",
                })
        for alg in algorithms:
            expected.append({"rel_path": f"data/phase8/csfit_{op}_{alg}.json", "severity": "abort", "source": "algorithm_comparison"})

    for alg in algorithms:
        expected.append({"rel_path": f"data/phase7/scores/{alg}_sm_scores.csv", "severity": "abort", "source": "algorithm_comparison"})
        for op in operators:
            expected.append({"rel_path": f"data/phase7/scores/{alg}_np_{op}_scores.csv", "severity": "abort", "source": "algorithm_comparison+operator_claims"})
        expected.append({"rel_path": f"algorithms/anchor_{alg}.pkl", "severity": "abort", "source": "algorithm_comparison"})

    return expected


def _recovery_metadata_checks(root: str) -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []
    for phase in ("phase5", "phase6"):
        rel_path = os.path.join("data", phase, "event_count_recovery.json")
        path = os.path.join(root, rel_path)
        if not os.path.exists(path):
            continue
        try:
            data = _load_json(path)
        except Exception as exc:
            checks.append({
                "rel_path": rel_path,
                "severity": "abort",
                "source": "recovery_metadata",
                "path": path,
                "ok": False,
                "error": f"Could not parse recovery metadata: {exc}",
            })
            continue

        status = data.get("status")
        if status not in {"accepted", "zero_event_failure", "exhausted_recovery_red_flag"}:
            checks.append({
                "rel_path": rel_path,
                "severity": "abort",
                "source": "recovery_metadata",
                "path": path,
                "ok": False,
                "error": f"Unexpected recovery status: {status!r}",
            })

        if status == "accepted":
            merged_outputs = data.get("merged_outputs")
            if not isinstance(merged_outputs, list) or not merged_outputs:
                checks.append({
                    "rel_path": rel_path,
                    "severity": "abort",
                    "source": "recovery_metadata",
                    "path": path,
                    "ok": False,
                    "error": "accepted recovery metadata has no merged_outputs",
                })
                continue
            for item in merged_outputs:
                label = item.get("label", "<missing>")
                lhco_path = item.get("lhco_path")
                count = int(item.get("loaded_lhco_event_count", 0))
                requested = int(item.get("requested_event_count", data.get("requested_event_count", 0)) or 0)
                source_banners = item.get("source_banners_retained") or []
                merged_cross_section = item.get("merged_cross_section_pb")
                ok = True
                errors = []
                if not lhco_path or not os.path.exists(lhco_path):
                    ok = False
                    errors.append("merged LHCO path missing")
                if count <= 0:
                    ok = False
                    errors.append("merged loaded count is not positive")
                if requested > 0 and count < 0.1 * requested:
                    ok = False
                    errors.append("merged loaded count is below 10% requested")
                missing_banners = [p for p in source_banners if p and not os.path.exists(p)]
                if missing_banners:
                    ok = False
                    errors.append(f"missing source banners: {missing_banners}")
                if len(source_banners) > 1 and merged_cross_section is None:
                    ok = False
                    errors.append("missing merged cross-section for multi-attempt merge")
                checks.append({
                    "rel_path": f"{rel_path}:{label}",
                    "severity": "abort",
                    "source": "recovery_metadata",
                    "path": path,
                    "ok": ok,
                    "errors": errors,
                })

            for warning in data.get("warnings", []):
                fraction = warning.get("fraction")
                if fraction is None or not (0.1 <= float(fraction) < 0.9):
                    checks.append({
                        "rel_path": rel_path,
                        "severity": "abort",
                        "source": "recovery_metadata",
                        "path": path,
                        "ok": False,
                        "error": f"Invalid warning fraction: {warning}",
                    })

        if status == "zero_event_failure" and not data.get("zero_event_failure"):
            checks.append({
                "rel_path": rel_path,
                "severity": "abort",
                "source": "recovery_metadata",
                "path": path,
                "ok": False,
                "error": "zero_event_failure status missing zero_event_failure details",
            })
    return checks


def audit_expected_outputs(workdir: str, run_dir: Optional[str] = None) -> Dict[str, Any]:
    root = _result_root(os.path.abspath(os.path.expanduser(workdir)), run_dir)
    expected = _expected_files(root)
    checks = []
    for item in expected:
        path = os.path.join(root, item["rel_path"])
        rec = dict(item)
        rec.update(_exists_nonempty(path))
        checks.append(rec)
    checks.extend(_recovery_metadata_checks(root))

    manuscript_candidates = [
        os.path.join(root, "manuscript.pdf"),
        os.path.join(root, "manuscript.html"),
    ]
    manuscript_ok = any(os.path.exists(p) and os.path.getsize(p) > 0 for p in manuscript_candidates)
    checks.append({
        "rel_path": "manuscript.pdf or manuscript.html",
        "severity": "abort",
        "source": "phase10",
        "path": manuscript_candidates,
        "exists": manuscript_ok,
        "size": None,
        "ok": manuscript_ok,
    })

    failures = [c for c in checks if not c["ok"] and c["severity"] == "abort"]
    warnings = [c for c in checks if not c["ok"] and c["severity"] == "warn"]
    return {
        "schema_version": "1.0",
        "root": root,
        "status": "FAIL" if failures else ("WARN" if warnings else "PASS"),
        "checks": checks,
        "failures": failures,
        "warnings": warnings,
        "expected_count": len(checks),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit expected workflow outputs")
    parser.add_argument("workdir")
    parser.add_argument("--run-dir", default=None)
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args()

    report = audit_expected_outputs(args.workdir, run_dir=args.run_dir)
    if args.json_out:
        os.makedirs(os.path.dirname(os.path.abspath(args.json_out)), exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, sort_keys=True)
            f.write("\n")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] in {"PASS", "WARN"} else 2


if __name__ == "__main__":
    sys.exit(main())

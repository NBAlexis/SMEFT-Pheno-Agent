#!/usr/bin/env python3
"""Create, verify, and expand the frozen research deliverables contract."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from itertools import product
from typing import Any, Dict, Iterable, List, Optional, Tuple


RESEARCH_CONTRACT_NAME = "research_contract.json"
DELIVERABLES_CONTRACT_NAME = "deliverables_contract.json"
RESOLVED_DELIVERABLES_NAME = "deliverables_resolved.json"


def _load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8-sig") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected a JSON object: {path}")
    return data


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _write_json(path: str, value: Any) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")


def _write_immutable(path: str, value: Any) -> str:
    if os.path.exists(path):
        existing = _load_json(path)
        if existing != value:
            raise ValueError(
                f"Refusing to overwrite an existing frozen contract with different content: {path}"
            )
        return "unchanged"
    _write_json(path, value)
    return "created"


def _card_identity(value: Any) -> Any:
    if value is None:
        return None
    normalized = str(value).replace("\\", "/").rstrip("/")
    return normalized.rsplit("/", 1)[-1]


def _run_objective(run: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "energy": run.get("energy"),
        "luminosity": run.get("luminosity"),
        "ebeam1": run.get("ebeam1"),
        "ebeam2": run.get("ebeam2"),
    }


def research_objective(config: Dict[str, Any]) -> Dict[str, Any]:
    """Project run_config onto scientific choices, excluding technical locations."""
    algorithms = config.get("algorithms")
    algorithm_strategy = {
        "requested": algorithms,
        "selection_rule": (
            "train_exact_requested_set"
            if algorithms
            else "use_phase7_standard_algorithm_set"
        ),
    }
    return {
        "process": config.get("process"),
        "collider_type": config.get("collider_type"),
        "process_validation": config.get("process_validation"),
        "madspin": config.get("madspin", {"enabled": False}),
        "models": config.get("models"),
        "energy": config.get("energy"),
        "ebeam_electron": config.get("ebeam_electron"),
        "ebeam_proton": config.get("ebeam_proton"),
        "luminosity": config.get("luminosity"),
        "run_configurations": [
            _run_objective(run) for run in config.get("run_configurations", [])
        ],
        "detector_card_identity": config.get(
            "delphes_card_identity", _card_identity(config.get("delphes_card"))
        ),
        "polarization": config.get("polarization"),
        "algorithm_strategy": algorithm_strategy,
        "analysis_notes": config.get("analysis_notes"),
        "debug": bool(config.get("debug", False)),
        "event_counts_locked": config.get("event_counts_locked"),
        "locked_event_counts": config.get("locked_event_counts"),
        "significance_strategy": {
            "levels": [2, 3, 5],
            "final_algorithm_rule": "narrowest_anchor_S2_interval",
        },
        "output_strategy": {
            "numerical_phases": [2, 3, 4, 5, 6, 7, 8, 9],
            "manuscript": "publication_style_with_pdf_when_latex_is_usable",
            "replay": "one_command_ordered_numerical_reproduction",
            "audit": "expanded_deliverables_and_cross_phase_consistency",
        },
    }


def _research_contract(config: Dict[str, Any]) -> Dict[str, Any]:
    objective = research_objective(config)
    return {
        "schema_version": "1.0",
        "contract_kind": "automated-smeft-ml-pheno-research-objective",
        "objective": objective,
        "objective_sha256": _sha256(objective),
        "mutable_technical_fields": [
            "execution",
            "madgraph_path",
            "cutexperiment_path",
            "workdir",
            "auto_installed_mg5",
            "collected_at",
            "run_configurations[*].run_dir",
            "host paths, virtual environments, schedulers, and implementation scripts",
        ],
    }


def _deliverables_contract(
    template: Dict[str, Any], objective_sha256: str
) -> Dict[str, Any]:
    return {
        "schema_version": "1.0",
        "contract_kind": "automated-smeft-ml-pheno-frozen-deliverables",
        "research_objective_sha256": objective_sha256,
        "template_sha256": _sha256(template),
        "template": template,
    }


def default_template_path() -> str:
    return os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "reference",
            "deliverables-contract-template.json",
        )
    )


def init_contracts(
    run_config_path: str,
    results_dir: Optional[str] = None,
    template_path: Optional[str] = None,
) -> Dict[str, Any]:
    config = _load_json(run_config_path)
    if config.get("version") != "1.0":
        raise ValueError("run_config.json version must be '1.0'")
    results_dir = os.path.abspath(
        results_dir or os.path.dirname(os.path.abspath(run_config_path))
    )
    template = _load_json(template_path or default_template_path())
    research = _research_contract(config)
    research["deliverables_template_sha256"] = _sha256(template)
    deliverables = _deliverables_contract(template, research["objective_sha256"])
    research_path = os.path.join(results_dir, RESEARCH_CONTRACT_NAME)
    deliverables_path = os.path.join(results_dir, DELIVERABLES_CONTRACT_NAME)
    return {
        "status": "ok",
        "research_contract": research_path,
        "research_contract_action": _write_immutable(research_path, research),
        "deliverables_contract": deliverables_path,
        "deliverables_contract_action": _write_immutable(
            deliverables_path, deliverables
        ),
        "objective_sha256": research["objective_sha256"],
        "template_sha256": deliverables["template_sha256"],
    }


def verify_contracts(
    run_config_path: str,
    results_dir: Optional[str] = None,
) -> Dict[str, Any]:
    config = _load_json(run_config_path)
    results_dir = os.path.abspath(
        results_dir or os.path.dirname(os.path.abspath(run_config_path))
    )
    research_path = os.path.join(results_dir, RESEARCH_CONTRACT_NAME)
    deliverables_path = os.path.join(results_dir, DELIVERABLES_CONTRACT_NAME)
    research = _load_json(research_path)
    deliverables = _load_json(deliverables_path)

    expected_objective = research_objective(config)
    errors: List[str] = []
    if research.get("schema_version") != "1.0" or research.get("contract_kind") != (
        "automated-smeft-ml-pheno-research-objective"
    ):
        errors.append("research_contract.json identity or schema is invalid")
    if deliverables.get("schema_version") != "1.0" or deliverables.get(
        "contract_kind"
    ) != "automated-smeft-ml-pheno-frozen-deliverables":
        errors.append("deliverables_contract.json identity or schema is invalid")
    stored_objective = research.get("objective")
    stored_objective_hash = research.get("objective_sha256")
    expected_objective_hash = _sha256(expected_objective)
    if stored_objective_hash != _sha256(stored_objective):
        errors.append("research_contract.json objective hash is invalid")
    if expected_objective != stored_objective:
        errors.append("run_config.json scientific objective differs from the frozen contract")
    template = deliverables.get("template")
    if deliverables.get("template_sha256") != _sha256(template):
        errors.append("deliverables_contract.json template hash is invalid")
    if research.get("deliverables_template_sha256") != deliverables.get(
        "template_sha256"
    ):
        errors.append("research contract is bound to a different deliverables template")
    if deliverables.get("research_objective_sha256") != stored_objective_hash:
        errors.append("deliverables contract is bound to a different research objective")

    return {
        "status": "ok" if not errors else "error",
        "errors": errors,
        "research_contract": research_path,
        "deliverables_contract": deliverables_path,
        "expected_objective_sha256": expected_objective_hash,
        "frozen_objective_sha256": stored_objective_hash,
        "template_sha256": deliverables.get("template_sha256"),
    }


def _iter_json_objects(value: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for nested in value.values():
            yield from _iter_json_objects(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _iter_json_objects(nested)


def _operators(run_root: str) -> Optional[List[str]]:
    path = os.path.join(run_root, "data", "phase3", "operator_claims.json")
    if not os.path.exists(path):
        return None
    def sort_key(value: str) -> Tuple[int, str]:
        try:
            return int(str(value).rsplit("_", 1)[-1]), str(value)
        except ValueError:
            return sys.maxsize, str(value)

    return sorted(_load_json(path).keys(), key=sort_key)


def _scan_labels(
    run_root: str, operators: Optional[List[str]]
) -> Optional[Dict[str, List[str]]]:
    path = os.path.join(run_root, "data", "phase6", "scan_manifest.json")
    if operators is None or not os.path.exists(path):
        return None
    manifest = _load_json(path)
    labels: Dict[str, List[str]] = {}
    for operator in operators:
        record = manifest.get(operator)
        if not isinstance(record, dict) or not isinstance(record.get("labels"), list):
            return None
        labels[operator] = [str(label) for label in record["labels"]]
    return labels


def _algorithms(run_root: str) -> Optional[List[str]]:
    path = os.path.join(run_root, "data", "phase7", "algorithm_comparison.json")
    if not os.path.exists(path):
        return None
    anchor = _load_json(path).get("anchor")
    if not isinstance(anchor, dict):
        return None
    return sorted(anchor.keys())


def _phase3_runner_results(run_root: str) -> Optional[List[str]]:
    path = os.path.join(run_root, "data", "phase3", "model_status.json")
    if not os.path.exists(path):
        return None
    values = set()
    for record in _iter_json_objects(_load_json(path)):
        for key in (
            "create_np_result_json",
            "result_json",
            "result_json_path",
            "runner_result_json",
        ):
            value = record.get(key)
            if isinstance(value, str) and value:
                full = value if os.path.isabs(value) else os.path.join(run_root, value)
                try:
                    value = os.path.relpath(full, run_root)
                except ValueError:
                    pass
                values.add(value.replace("\\", "/"))
    return sorted(values)


def _replay_files(run_root: str) -> Optional[List[str]]:
    replay_root = os.path.join(run_root, "replay")
    path = os.path.join(replay_root, "replay_manifest.json")
    if not os.path.exists(path):
        return None
    manifest = _load_json(path)
    values = set()
    for record in _iter_json_objects(manifest):
        checksums = record.get("sha256")
        if isinstance(checksums, dict):
            values.update(key for key in checksums if isinstance(key, str))
        command = record.get("command")
        if isinstance(command, list):
            for token in command:
                if isinstance(token, str) and (
                    "/" in token or token.endswith((".py", ".sh"))
                ):
                    values.add(token)
    normalized = []
    for value in sorted(values):
        if os.path.isabs(value) or value.startswith("-"):
            continue
        rel = value.replace("\\", "/").lstrip("./")
        if rel in {"replay.sh", "data_files_report.md"}:
            continue
        if rel.startswith(("steps/", "support/")):
            normalized.append(f"replay/{rel}")
    return sorted(set(normalized))


def _pdf_required(run_root: str) -> Optional[bool]:
    path = os.path.join(
        run_root, "data", "phase10", "manuscript_build_environment.json"
    )
    if not os.path.exists(path):
        return None
    value = _load_json(path).get("pdf_required")
    return bool(value) if isinstance(value, bool) else None


def _selector_rows(
    selector: str,
    operators: Optional[List[str]],
    labels: Optional[Dict[str, List[str]]],
    algorithms: Optional[List[str]],
    runner_results: Optional[List[str]],
    replay_files: Optional[List[str]],
) -> Tuple[Optional[List[Dict[str, str]]], Optional[str]]:
    if selector == "fixed":
        return [{}], None
    if selector == "operator":
        if operators is None:
            return None, "operator_claims.json is not available"
        return [{"operator": op} for op in operators], None
    if selector == "phase3_runner_result":
        if runner_results is None:
            return None, "model_status.json is not available"
        return [{"phase3_runner_result": value} for value in runner_results], None
    if selector == "replay_file":
        if replay_files is None:
            return None, "replay_manifest.json is not available"
        return [{"replay_file": value} for value in replay_files], None
    if selector in {"operator_scan_label", "operator_scan_label_algorithm"}:
        if operators is None or labels is None:
            return None, "operator or scan-label manifest is not available"
        rows = [
            {"operator": op, "scan_label": label}
            for op in operators
            for label in labels.get(op, [])
        ]
        if selector == "operator_scan_label":
            return rows, None
        if algorithms is None:
            return None, "algorithm_comparison.json is not available"
        return [dict(row, algorithm=alg) for row in rows for alg in algorithms], None
    if selector == "algorithm":
        if algorithms is None:
            return None, "algorithm_comparison.json is not available"
        return [{"algorithm": alg} for alg in algorithms], None
    if selector == "operator_algorithm":
        if operators is None or algorithms is None:
            return None, "operator or algorithm manifest is not available"
        return [
            {"operator": op, "algorithm": alg}
            for op, alg in product(operators, algorithms)
        ], None
    return None, f"unknown selector: {selector}"


def _condition_state(
    condition: Optional[str], operators: Optional[List[str]], pdf_required: Optional[bool]
) -> Tuple[Optional[bool], Optional[str]]:
    if not condition:
        return True, None
    if condition == "at_least_one_claimed_operator":
        if operators is None:
            return None, "operator_claims.json is not available"
        return bool(operators), None
    if condition == "no_claimed_operator":
        if operators is None:
            return None, "operator_claims.json is not available"
        return not operators, None
    if condition == "pdf_required":
        if pdf_required is None:
            return None, "manuscript format decision is not available"
        return pdf_required, None
    if condition == "not_pdf_required":
        if pdf_required is None:
            return None, "manuscript format decision is not available"
        return not pdf_required, None
    if condition == "at_least_one_claimed_operator_and_pdf_required":
        if operators is None:
            return None, "operator_claims.json is not available"
        if not operators:
            return False, None
        if pdf_required is None:
            return None, "manuscript format decision is not available"
        return pdf_required, None
    if condition == "at_least_one_claimed_operator_and_not_pdf_required":
        if operators is None:
            return None, "operator_claims.json is not available"
        if not operators:
            return False, None
        if pdf_required is None:
            return None, "manuscript format decision is not available"
        return not pdf_required, None
    return None, f"unknown condition: {condition}"


def resolve_contract(
    run_config_path: str,
    run_root: Optional[str] = None,
    results_dir: Optional[str] = None,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    results_dir = os.path.abspath(
        results_dir or os.path.dirname(os.path.abspath(run_config_path))
    )
    verification = verify_contracts(run_config_path, results_dir)
    if verification["status"] != "ok":
        raise ValueError("; ".join(verification["errors"]))
    config = _load_json(run_config_path)
    if run_root is None:
        run_configs = config.get("run_configurations") or []
        if len(run_configs) > 1:
            raise ValueError("--run-root is required for a multi-run configuration")
        run_root = results_dir
    run_root = os.path.abspath(run_root)
    contract = _load_json(os.path.join(results_dir, DELIVERABLES_CONTRACT_NAME))
    template = contract["template"]

    operators = _operators(run_root)
    labels = _scan_labels(run_root, operators)
    algorithms = _algorithms(run_root)
    runner_results = _phase3_runner_results(run_root)
    replay_files = _replay_files(run_root)
    pdf_required = _pdf_required(run_root)

    resolved: List[Dict[str, Any]] = []
    pending: List[Dict[str, Any]] = []
    excluded: List[Dict[str, Any]] = []
    for rule in template.get("rules", []):
        condition, condition_reason = _condition_state(
            rule.get("condition"), operators, pdf_required
        )
        if condition is False:
            excluded.append({"rule_id": rule.get("id"), "reason": "condition is false"})
            continue
        if condition is None:
            pending.append({"rule_id": rule.get("id"), "reason": condition_reason})
            continue
        rows, selector_reason = _selector_rows(
            rule.get("selector", "fixed"),
            operators,
            labels,
            algorithms,
            runner_results,
            replay_files,
        )
        if rows is None:
            pending.append({"rule_id": rule.get("id"), "reason": selector_reason})
            continue
        for row in rows:
            for item in rule.get("items", []):
                rel_path = item["path"].format(**row).replace("\\", "/")
                base = results_dir if rule.get("scope") == "global_results" else run_root
                absolute_path = os.path.abspath(os.path.join(base, rel_path))
                resolved.append(
                    {
                        "rule_id": rule.get("id"),
                        "phase": rule.get("phase"),
                        "scope": rule.get("scope"),
                        "path": rel_path,
                        "absolute_path": absolute_path,
                        "type": item.get("type", "file"),
                        "dimensions": row,
                    }
                )

    report = {
        "schema_version": "1.0",
        "contract_kind": "automated-smeft-ml-pheno-resolved-deliverables",
        "research_objective_sha256": verification["frozen_objective_sha256"],
        "deliverables_template_sha256": verification["template_sha256"],
        "run_root": run_root,
        "status": "resolved" if not pending else "pending",
        "resolved": resolved,
        "pending_rules": pending,
        "excluded_rules": excluded,
        "counts": {
            "resolved_items": len(resolved),
            "pending_rules": len(pending),
            "excluded_rules": len(excluded),
        },
    }
    output_path = output_path or os.path.join(run_root, RESOLVED_DELIVERABLES_NAME)
    _write_json(output_path, report)
    report["output_path"] = os.path.abspath(output_path)
    return report


def _print_and_status(report: Dict[str, Any]) -> int:
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if report.get("status") in {"ok", "resolved", "pending"} else 2


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Manage the immutable research and deliverables contracts"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("run_config")
    init_parser.add_argument("--results-dir")
    init_parser.add_argument("--template")

    verify_parser = subparsers.add_parser("verify")
    verify_parser.add_argument("run_config")
    verify_parser.add_argument("--results-dir")

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("run_config")
    resolve_parser.add_argument("--results-dir")
    resolve_parser.add_argument("--run-root")
    resolve_parser.add_argument("--output")

    args = parser.parse_args()
    try:
        if args.command == "init":
            report = init_contracts(args.run_config, args.results_dir, args.template)
        elif args.command == "verify":
            report = verify_contracts(args.run_config, args.results_dir)
        else:
            report = resolve_contract(
                args.run_config, args.run_root, args.results_dir, args.output
            )
        return _print_and_status(report)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

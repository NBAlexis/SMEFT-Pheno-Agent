#!/usr/bin/env python3
"""Phase 3 driver: operator sensitivity validation across all configured models.

Runs on the WSL2 execution target. Uses the standard runner
(scripts/run_mg5_config.py) for every MG5 job: create_np once per model, then
one pure_np run per coefficient with the locked nev_phase3 event count.
"""
import json
import os
import re
import sys

WORKDIR = "/mnt/e/SMEFT-Pheno-Agent-GLM-test"
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")
PYTHON = os.path.join(WORKDIR, "venv", "bin", "python")
RUNNER = os.path.join(SKILL_RUNTIME, "scripts", "run_mg5_config.py")

sys.path.insert(0, SKILL_RUNTIME)
from scripts.load_run_config import load_run_config
from scripts.workflow_logger import WorkflowLogger, workflow_step, run_logged_subprocess


def ufo_coefficient_names(mg5path, model, block_name):
    """Map LHA code (int) -> UFO parameter name for the coefficient block."""
    path = os.path.join(mg5path, "models", model, "parameters.py")
    text = open(path, encoding="utf-8", errors="replace").read()
    mapping = {}
    for chunk in re.split(r"(?=Parameter\()", text):
        name_match = re.search(r"\bname\s*=\s*'([^']+)'", chunk)
        block_match = re.search(r"\blhablock\s*=\s*'([^']+)'", chunk)
        code_match = re.search(r"\blhacode\s*=\s*\[\s*(\d+)\s*\]", chunk)
        if name_match and block_match and code_match:
            if block_match.group(1).lower() == block_name.lower():
                mapping[int(code_match.group(1))] = name_match.group(1)
    return mapping


def looks_like_no_diagram(payload):
    """Detect MG5 no-Feynman-diagram evidence in a failed runner manifest."""
    if not isinstance(payload, dict):
        return False
    texts = [str(payload.get("error") or ""), str(payload.get("traceback") or "")]
    create = payload.get("create_process") or {}
    texts.append(str(create.get("stdout_tail") or ""))
    texts.append(str(create.get("stderr_tail") or ""))
    joined = "\n".join(texts).lower()
    return ("nodiagram" in joined) or ("no diagram" in joined)


def main():
    config = load_run_config(RUN_CONFIG)
    logger = WorkflowLogger(WORKDIR, None)  # single-run mode
    run_root = os.path.join(WORKDIR, "results")
    phase3_dir = os.path.join(run_root, "data", "phase3")
    logs_dir = os.path.join(phase3_dir, "logs")
    jobs_dir = os.path.join(run_root, "jobs")
    for directory in (phase3_dir, logs_dir, jobs_dir):
        os.makedirs(directory, exist_ok=True)
    logger.phase_start("3")

    run_cfg = config.run_configurations[0]
    claimed = {}
    operator_claims = {}
    cross_sections = {}
    model_status = {}
    anchor = None
    g_idx = 0

    for model in config.models:
        entry = {
            "has_feynman_diagrams": False,
            "create_np_result_json": f"results/data/phase3/{model}_create_np_result.json",
        }

        # ---- Step 3.1.1: create the NP process and discover coefficients ----
        create_result_path = os.path.join(phase3_dir, f"{model}_create_np_result.json")
        create_cfg = {
            "mg5path": config.madgraph_path,
            "model": model,
            "process": config.process,
            "process_mode": "create_np",
            "log_dir": logs_dir,
            "result_json": create_result_path,
        }
        create_cfg_path = os.path.join(phase3_dir, f"{model}_create_np.json")
        with open(create_cfg_path, "w", encoding="utf-8") as handle:
            json.dump(create_cfg, handle, indent=2)

        with workflow_step(logger, "3", f"create_np_{model}",
                           inputs={"config": create_cfg_path}) as step:
            proc = run_logged_subprocess(
                logger, "3", f"run_create_np_{model}",
                [PYTHON, RUNNER, create_cfg_path],
                cwd=SKILL_RUNTIME,
                stdout_path=os.path.join(jobs_dir, f"phase3_create_np_{model}.stdout"),
                stderr_path=os.path.join(jobs_dir, f"phase3_create_np_{model}.stderr"),
                check=False,
            )
            create_result = None
            if os.path.exists(create_result_path):
                with open(create_result_path, encoding="utf-8") as handle:
                    create_result = json.load(handle)

            if proc.returncode != 0:
                if create_result is not None and looks_like_no_diagram(create_result):
                    entry["has_feynman_diagrams"] = False
                    entry["no_diagram_reason"] = str(create_result.get("error") or "")[:4000]
                    entry["create_stdout_path"] = (create_result.get("create_process") or {}).get("stdout_path")
                    entry["create_stderr_path"] = (create_result.get("create_process") or {}).get("stderr_path")
                    model_status[model] = entry
                    step.set_outputs({"status": "no_feynman_diagrams",
                                      "reason": entry["no_diagram_reason"][:500]})
                    continue
                # Not a no-diagram case: real technical failure.
                raise RuntimeError(
                    f"create_np failed for {model}; see {create_result_path} and "
                    f"{jobs_dir}/phase3_create_np_{model}.stderr"
                )

            if not create_result or create_result.get("status") != "completed":
                raise RuntimeError(f"create_np result invalid for {model}: {create_result_path}")

            entry["has_feynman_diagrams"] = True
            step.set_outputs({"status": "completed",
                              "coefficients": create_result.get("available_coefficients")})

        block = create_result["coefficient_block"]
        coefficients = {str(k): v for k, v in create_result["available_coefficients"].items()}
        names = ufo_coefficient_names(config.madgraph_path, model, block)
        sorted_idx = sorted(coefficients, key=lambda value: int(value))
        coeffs_status = {}
        shared_process_folder = None

        # ---- Step 3.1.3: test every coefficient individually ----
        for idx in sorted_idx:
            name = names.get(int(idx), f"c{idx}")
            default = float(coefficients[idx])
            c_default = default if default != 0.0 else 1.0
            result_path = os.path.join(phase3_dir, f"{model}_{name}_result.json")
            run_one = {
                "mg5path": config.madgraph_path,
                "model": model,
                "process": config.process,
                "madspin": {"enabled": bool(config.madspin.enabled)},
                "process_mode": "pure_np",
                "operator": name,
                "target_coefficient": {"index": int(idx), "value": c_default},
                "coefficient_mode": "explicit",
                "run_label": run_cfg.run_dir,
                "ebeam1": run_cfg.ebeam1,
                "ebeam2": run_cfg.ebeam2,
                "nevents": int(config.locked_event_counts.nev_phase3),
                "delphes_card": config.delphes_card,
                "cutexperiment_path": config.cutexperiment_path,
                "output_label": f"phase3_{model}_{name}",
                "output_dir": phase3_dir,
                "log_dir": logs_dir,
                "result_json": result_path,
            }
            if shared_process_folder:
                run_one["process_folder"] = shared_process_folder
            cfg_path = os.path.join(phase3_dir, f"{model}_{name}_runner.json")
            with open(cfg_path, "w", encoding="utf-8") as handle:
                json.dump(run_one, handle, indent=2)

            with workflow_step(logger, "3", f"test_coeff_{model}_{name}",
                               inputs={"c": c_default, "index": int(idx),
                                       "nevents": run_one["nevents"]}) as step:
                run_logged_subprocess(
                    logger, "3", f"run_mg5_{model}_{name}",
                    [PYTHON, RUNNER, cfg_path],
                    cwd=SKILL_RUNTIME,
                    stdout_path=os.path.join(jobs_dir, f"phase3_{model}_{name}.stdout"),
                    stderr_path=os.path.join(jobs_dir, f"phase3_{model}_{name}.stderr"),
                    check=True,
                )
                with open(result_path, encoding="utf-8") as handle:
                    run_result = json.load(handle)
                if not shared_process_folder:
                    shared_process_folder = run_result["process_folder"]
                outputs = run_result.get("outputs") or []
                if not outputs:
                    raise RuntimeError(f"Runner produced no outputs for {model}:{name}")
                sigma = float(outputs[0].get("cross_section_pb"))
                if not (sigma >= 0.0):
                    raise RuntimeError(f"Invalid sigma for {model}:{name}: {sigma}")

                coeff_record = {
                    "c_default": c_default,
                    "sigma": sigma,
                    "result_json": f"results/data/phase3/{model}_{name}_result.json",
                }
                if sigma > 0:
                    if name not in claimed:
                        g_idx += 1
                        claimed[name] = model
                        operator_claims[f"o_{g_idx}"] = {
                            "model": model,
                            "anoinput_idx": int(idx),
                            "name": name,
                        }
                        coeff_record["global_idx"] = g_idx
                        if anchor is None:
                            anchor = {
                                "global_idx": g_idx,
                                "model": model,
                                "anoinput_idx": int(idx),
                                "name": name,
                            }
                    else:
                        coeff_record["global_idx"] = int(
                            operator_claims[
                                next(key for key, value in operator_claims.items()
                                     if value["name"] == name)
                            ]["global_idx"]
                        )
                        coeff_record["duplicate_of_earlier_model"] = claimed[name]

                cross_sections[f"{model}:{name}"] = {
                    "sigma": sigma,
                    "c_default": c_default,
                    "model": model,
                    "global_idx": coeff_record.get("global_idx"),
                }
                coeffs_status[name] = coeff_record
                step.set_outputs({"sigma": sigma, "claimed": name in claimed})

        entry["coefficient_count"] = len(sorted_idx)
        entry["tested_count"] = len(coeffs_status)
        entry["coefficients"] = coeffs_status
        model_status[model] = entry

    # ---- Step 3.2: write global metadata ----
    with workflow_step(logger, "3", "write_global_metadata",
                       inputs={"num_claimed": len(operator_claims),
                               "num_tested": len(cross_sections)}):
        with open(os.path.join(phase3_dir, "operator_claims.json"), "w", encoding="utf-8") as f:
            json.dump(operator_claims, f, indent=2)
        with open(os.path.join(phase3_dir, "cross_sections.json"), "w", encoding="utf-8") as f:
            json.dump(cross_sections, f, indent=2)
        with open(os.path.join(phase3_dir, "model_status.json"), "w", encoding="utf-8") as f:
            json.dump(model_status, f, indent=2)
        with open(os.path.join(phase3_dir, "anchor.json"), "w", encoding="utf-8") as f:
            json.dump(anchor if anchor else {}, f, indent=2)

    logger.phase_complete("3", message=f"claimed={len(operator_claims)} anchor={anchor}")
    print(json.dumps({"claimed": len(operator_claims), "anchor": anchor}))


if __name__ == "__main__":
    main()

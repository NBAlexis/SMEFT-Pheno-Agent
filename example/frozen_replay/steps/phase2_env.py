#!/usr/bin/env python3
"""Phase 2 driver: environment validation. Runs on the WSL2 execution target."""

import json
import os
import platform
import socket
import subprocess
import sys
from datetime import datetime, timezone

WORKDIR = os.environ.get("SMEFT_WORKDIR", "/mnt/e/SMEFT-Pheno-Agent-GLM-test")
SKILL_RUNTIME = os.path.join(WORKDIR, ".smeft-skill")
JOBS_DIR = os.path.join(WORKDIR, "results", "jobs")

sys.path.insert(0, SKILL_RUNTIME)
from scripts.load_run_config import load_run_config, NORMAL_EVENT_COUNTS, DEBUG_EVENT_COUNTS
from scripts.workflow_logger import WorkflowLogger, workflow_step, run_logged_subprocess

RUN_CONFIG = os.path.join(WORKDIR, "results", "run_config.json")


def probe(command, cwd=None, timeout=120):
    """Run a probe command, return dict with command, returncode, stdout tail."""
    result = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, check=False, timeout=timeout
    )
    return {
        "command": command,
        "cwd": cwd,
        "returncode": result.returncode,
        "stdout_tail": (result.stdout or "").strip()[-2000:],
        "stderr_tail": (result.stderr or "").strip()[-2000:],
    }


def main():
    os.makedirs(JOBS_DIR, exist_ok=True)

    config = load_run_config(RUN_CONFIG)
    run_dir = None  # single run_configurations entry -> single-run mode
    logger = WorkflowLogger(WORKDIR, run_dir)
    resume_phase = logger.get_resume_phase()
    logger.assert_ready()
    logger.phase_start("2", details={"resume_phase": resume_phase})

    # Step 1: validate run_config + frozen contracts on the target
    with workflow_step(logger, "2", "validate_run_config",
                       inputs={"run_config": RUN_CONFIG, "execution_mode": config.execution.mode}) as step:
        contract_files = {
            "run_config.json": RUN_CONFIG,
            "research_contract.json": os.path.join(WORKDIR, "results", "research_contract.json"),
            "deliverables_contract.json": os.path.join(WORKDIR, "results", "deliverables_contract.json"),
            "contract_lock.json": os.path.join(WORKDIR, "results", "contract_lock.json"),
        }
        missing = [p for p in contract_files.values() if not os.path.isfile(p)]
        if missing:
            raise RuntimeError(f"Phase 1 contract files missing on target: {missing}")
        verify = run_logged_subprocess(
            logger, "2", "research_contract_verify",
            [sys.executable, os.path.join(SKILL_RUNTIME, "scripts", "research_contract.py"),
             "verify", RUN_CONFIG],
            cwd=SKILL_RUNTIME,
            stdout_path=os.path.join(JOBS_DIR, "phase2_contract_verify.stdout"),
            stderr_path=os.path.join(JOBS_DIR, "phase2_contract_verify.stderr"),
        )
        verify_payload = json.loads(
            open(os.path.join(JOBS_DIR, "phase2_contract_verify.stdout"), encoding="utf-8").read()
        )
        if verify_payload.get("status") != "ok":
            raise RuntimeError(f"research_contract verify failed: {verify_payload}")
        step.set_outputs({"contract_status": verify_payload.get("status"),
                          "target_contract_files": contract_files,
                          "verify_returncode": verify.returncode})

    # Step 2: validate models on the target MG5 installation
    with workflow_step(logger, "2", "validate_models", inputs={"models": config.models}) as step:
        model_report = []
        for model in config.models:
            model_path = os.path.join(config.madgraph_path, "models", model)
            present = os.path.isdir(model_path)
            model_report.append({"name": model, "path": model_path, "exists_on_target": present})
            if not present:
                raise RuntimeError(f"Model {model} missing at {model_path}")
        step.set_outputs({"model_report": model_report})

    # Step 3: validate physics inputs and locked event counts
    with workflow_step(logger, "2", "validate_physics_inputs",
                       inputs={"run_configurations": [dict(r.__dict__) for r in config.run_configurations],
                               "luminosity": config.luminosity}) as step:
        assert config.event_counts_locked is True
        expected = DEBUG_EVENT_COUNTS if config.debug else NORMAL_EVENT_COUNTS
        assert dict(config.locked_event_counts.__dict__) == expected, config.locked_event_counts
        assert len(config.energy) == len(config.luminosity)
        for run_cfg in config.run_configurations:
            assert float(run_cfg.ebeam1) > 0 and float(run_cfg.ebeam2) > 0
            assert float(run_cfg.luminosity) > 0
        step.set_outputs({"locked_event_counts": dict(config.locked_event_counts.__dict__),
                          "debug": config.debug, "checks": "passed"})

    # Step 4: create the workflow virtual environment
    venv_dir = os.path.join(WORKDIR, "venv")
    venv_python = os.path.join(venv_dir, "bin", "python")
    with open(os.environ["SMEFT_TOOLCHAIN_LOCK"], encoding="utf-8") as handle:
        toolchain_lock = json.load(handle)
    pinned_packages = [f"{name}=={version}" for name, version
                       in toolchain_lock["packages"].items()]
    with workflow_step(logger, "2", "setup_venv", inputs={"venv_dir": venv_dir}):
        if not os.path.exists(venv_python):
            run_logged_subprocess(
                logger, "2", "create_venv",
                [sys.executable, "-m", "venv", venv_dir],
                cwd=WORKDIR,
                stdout_path=os.path.join(JOBS_DIR, "phase2_venv_create.stdout"),
                stderr_path=os.path.join(JOBS_DIR, "phase2_venv_create.stderr"),
                check=True,
            )
        run_logged_subprocess(
            logger, "2", "install_venv_packages",
            [os.path.join(venv_dir, "bin", "pip"), "install",
             *pinned_packages],
            cwd=WORKDIR,
            stdout_path=os.path.join(JOBS_DIR, "phase2_pip_install.stdout"),
            stderr_path=os.path.join(JOBS_DIR, "phase2_pip_install.stderr"),
            check=True,
        )

    # Step 5: validate the Delphes card
    with workflow_step(logger, "2", "validate_delphes_card",
                       inputs={"delphes_card": config.delphes_card}) as step:
        card = config.delphes_card
        resolved = card if os.path.isabs(card) else os.path.join(
            config.madgraph_path, "Delphes", "cards", card)
        if not (os.path.isfile(resolved) and resolved.endswith((".tcl", ".dat"))):
            raise RuntimeError(f"Delphes card invalid: {resolved}")
        step.set_outputs({"resolved_path": resolved})

    # Step 6: create jobs/ and per-run result directories (single-run layout)
    with workflow_step(logger, "2", "setup_run_directories") as step:
        created = []
        for sub in ("data", "plots", "algorithms", "mg5_processes", "orders"):
            path = os.path.join(WORKDIR, "results", sub)
            os.makedirs(path, exist_ok=True)
            created.append(path)
        os.makedirs(os.path.join(WORKDIR, "results", "data", "phase2"), exist_ok=True)
        step.set_outputs({"created": created})

    # Step 7: toolchain probes
    with workflow_step(logger, "2", "probe_toolchain") as step:
        mg5_bin = os.path.join(config.madgraph_path, "bin", "mg5_aMC")
        if not os.path.exists(mg5_bin):
            mg5_bin = os.path.join(config.madgraph_path, "bin", "mg5")
        mg5_probe = probe([mg5_bin, "--version"], cwd=config.madgraph_path, timeout=300)
        cutex_probe = probe(
            ["git", "-C", config.cutexperiment_path, "rev-parse", "--short", "HEAD"],
            timeout=60,
        )
        venv_ver_probe = probe([venv_python, "--version"], timeout=60)
        venv_pkg_probe = probe(
            [venv_python, "-c",
             "import importlib.metadata as m; "
             "print({p: m.version(p) for p in "
             "['numpy','scipy','scikit-learn','joblib','matplotlib']})"],
            timeout=120,
        )
        step.set_outputs({
            "madgraph_version": mg5_probe["stdout_tail"],
            "madgraph_probe": mg5_probe,
            "cutexperiment_commit": cutex_probe["stdout_tail"] if cutex_probe["returncode"] == 0 else None,
            "cutexperiment_probe": cutex_probe,
            "venv_python": venv_python,
            "venv_python_version": venv_ver_probe["stdout_tail"],
            "venv_package_versions": venv_pkg_probe["stdout_tail"],
        })
        probes_snapshot = {
            "madgraph": mg5_probe, "cutexperiment": cutex_probe,
            "venv_python": venv_ver_probe, "venv_packages": venv_pkg_probe,
        }
        json.dump(probes_snapshot,
                  open(os.path.join(JOBS_DIR, "phase2_probes.json"), "w", encoding="utf-8"),
                  indent=2)

    # Step 8: write the environment manifest
    with workflow_step(logger, "2", "write_environment_manifest") as step:
        research_contract = json.load(
            open(os.path.join(WORKDIR, "results", "research_contract.json"), encoding="utf-8-sig"))
        deliverables_contract = json.load(
            open(os.path.join(WORKDIR, "results", "deliverables_contract.json"), encoding="utf-8-sig"))
        manifest = {
            "phase": 2,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "execution": dict(config.execution.__dict__),
            "platform": {
                "hostname": socket.gethostname(),
                "platform": platform.platform(),
                "python": sys.version,
                "driver_python_executable": sys.executable,
            },
            "madgraph": {
                "path": config.madgraph_path,
                "binary": mg5_bin,
                "version": mg5_probe["stdout_tail"],
                "probe_command": mg5_probe["command"],
                "probe_returncode": mg5_probe["returncode"],
            },
            "cutexperiment": {
                "path": config.cutexperiment_path,
                "git_commit": cutex_probe["stdout_tail"] if cutex_probe["returncode"] == 0 else None,
                "probe_command": cutex_probe["command"],
                "probe_returncode": cutex_probe["returncode"],
            },
            "delphes_card": {
                "config_value": config.delphes_card,
                "resolved_path": resolved,
            },
            "models": model_report,
            "venv": {
                "path": venv_dir,
                "python_path": venv_python,
                "python_version": venv_ver_probe["stdout_tail"],
                "package_versions": venv_pkg_probe["stdout_tail"],
                "package_probe_command": venv_pkg_probe["command"],
                "package_probe_returncode": venv_pkg_probe["returncode"],
            },
            "locked_event_count_mode": {
                "debug": config.debug,
                "event_counts_locked": config.event_counts_locked,
                "locked_event_counts": dict(config.locked_event_counts.__dict__),
            },
            "research_objective_sha256": research_contract.get("objective_sha256"),
            "deliverables_template_sha256": deliverables_contract.get("template_sha256"),
            "contract_verification": {
                "command": verify_payload.get("command") or "research_contract.py verify",
                "status": verify_payload.get("status"),
                "paths": list(contract_files.values()),
            },
            "run_directories": created,
            "single_run_mode": True,
        }
        manifest_path = os.path.join(WORKDIR, "results", "data", "phase2", "environment_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as handle:
            json.dump(manifest, handle, indent=2, ensure_ascii=False)
        step.set_outputs({"manifest_path": manifest_path})

    logger.phase_complete("2", message="environment validated")
    print("PHASE2_OK")


if __name__ == "__main__":
    main()

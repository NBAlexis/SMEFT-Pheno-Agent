import json
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.convert_root_to_lhco import convert_root_to_lhco, detect_jet_branch


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXTERNAL_TOOLS_CONFIG = ROOT / "tests" / "external_tools.json"


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def _strip_wsl2_prefix(value):
    if isinstance(value, str) and value.startswith("wsl2:"):
        return value[len("wsl2:"):]
    return value


def external_tool_config():
    path = Path(os.environ.get("SMEFT_EXTERNAL_TOOLS_CONFIG", DEFAULT_EXTERNAL_TOOLS_CONFIG))
    data = {}
    if path.exists():
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
    distro = os.environ.get("SMEFT_MG5_WSL_DISTRO") or data.get("wsl_distro")
    mg5_path = (
        os.environ.get("SMEFT_MG5_WSL_PATH")
        or _strip_wsl2_prefix(data.get("madgraph_path"))
    )
    cutexperiment_path = (
        os.environ.get("SMEFT_CUTEXPERIMENT_WSL_PATH")
        or _strip_wsl2_prefix(data.get("cutexperiment_path"))
    )
    return {
        "wsl_distro": distro,
        "madgraph_path": mg5_path,
        "cutexperiment_path": cutexperiment_path,
    }


def run_wsl_probe(command, distro, timeout):
    wsl = "wsl.exe" if shutil.which("wsl.exe") else "wsl"
    last = None
    command_variants = []
    if distro:
        command_variants.append([wsl, "-d", distro, "--", "bash", "-lc", command])
    command_variants.append([wsl, "--", "bash", "-lc", command])
    for cmd in command_variants:
        for _ in range(2):
            last = subprocess.run(
                cmd,
                cwd=str(ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False,
                check=False,
                timeout=timeout,
            )
            last.stdout = last.stdout.decode("utf-8", errors="replace")
            last.stderr = last.stderr.decode("utf-8", errors="replace")
            if last.returncode == 0:
                return last
        output = f"{last.stdout}\n{last.stderr}".replace("\x00", "") if last else ""
        if "WSL_E_DISTRO_NOT_FOUND" not in output:
            break
    return last


class Mg5DelphesMechanismTests(unittest.TestCase):
    def test_detect_jet_branch_prefers_standard_jet(self):
        with tempfile.TemporaryDirectory() as root:
            card = os.path.join(root, "card.tcl")
            write_text(
                card,
                "\n".join([
                    "add Branch Output/jets GenJet Jet",
                    "add Branch Output/jets FatJet Jet",
                    "add Branch Output/jets Jet Jet",
                ]),
            )
            self.assertEqual(detect_jet_branch(card), "Jet")

    def test_convert_root_to_lhco_constructs_expected_command(self):
        with tempfile.TemporaryDirectory() as mg5:
            process = "proc"
            run_folder = "run_01"
            process_root = os.path.join(mg5, process)
            root_dir = os.path.join(process_root, "Events", run_folder)
            cards_dir = os.path.join(process_root, "Cards")
            os.makedirs(root_dir, exist_ok=True)
            os.makedirs(cards_dir, exist_ok=True)
            write_text(
                os.path.join(cards_dir, "delphes_card.dat"),
                "add Branch Output/jets GenJet Jet\n",
            )
            write_text(os.path.join(root_dir, "tag_1_delphes_events.root"), "fake-root")

            def fake_run(cmd, cwd, stdout, stderr, text):
                self.assertEqual(cwd, os.path.join(mg5, "Delphes"))
                self.assertIn("--jet-branch=GenJet", cmd)
                lhco_rel = cmd[2]
                lhco_path = os.path.abspath(os.path.join(cwd, lhco_rel))
                write_text(lhco_path, "0 1 1 1 1 1\n1 1 1 1 1 1\n")
                stdout.write("ok\n")
                return subprocess.CompletedProcess(cmd, 0)

            with patch("scripts.convert_root_to_lhco.subprocess.run", side_effect=fake_run):
                lhco_path = convert_root_to_lhco(mg5, process, run_folder)

            self.assertTrue(lhco_path.endswith(f"{run_folder}.lhco"))
            self.assertTrue(os.path.exists(lhco_path))

    def test_convert_root_to_lhco_reports_root2lhco_failure_log(self):
        with tempfile.TemporaryDirectory() as mg5:
            process = "proc"
            run_folder = "run_01"
            root_dir = os.path.join(mg5, process, "Events", run_folder)
            cards_dir = os.path.join(mg5, process, "Cards")
            os.makedirs(root_dir, exist_ok=True)
            os.makedirs(cards_dir, exist_ok=True)
            write_text(os.path.join(cards_dir, "delphes_card.dat"), "add Branch Output/jets Jet Jet\n")
            write_text(os.path.join(root_dir, "tag_1_delphes_events.root"), "fake-root")

            def fake_run(cmd, cwd, stdout, stderr, text):
                stdout.write("Cannot find tree Delphes\n")
                return subprocess.CompletedProcess(cmd, 2)

            with patch("scripts.convert_root_to_lhco.subprocess.run", side_effect=fake_run):
                with self.assertRaises(RuntimeError) as ctx:
                    convert_root_to_lhco(mg5, process, run_folder)
            self.assertIn("root2lhco failed", str(ctx.exception))
            self.assertIn("Cannot find tree", str(ctx.exception))

    @unittest.skipUnless(
        shutil.which("wsl.exe") or shutil.which("wsl"),
        "WSL is required for the real MG5 smoke test",
    )
    def test_real_mg5_smoke_generation_is_short_and_optional(self):
        config = external_tool_config()
        distro = config["wsl_distro"]
        mg5_path = config["madgraph_path"]
        if not distro or not mg5_path:
            self.skipTest("Configure tests/external_tools.json or SMEFT_MG5_WSL_* to enable the smoke test")

        process = "smoke_ep_em_to_mu_mu"
        order_name = "smoke_order.txt"
        order_text = "\n".join([
            "import model sm",
            "generate e+ e- > mu+ mu-",
            f"output {process}",
        ]) + "\n"
        result = run_wsl_probe(
            (
                "set -euo pipefail; "
                f"cd {shlex.quote(mg5_path)}; "
                f"cat > {shlex.quote(order_name)} <<'EOF'\n{order_text}EOF\n"
                f"./bin/mg5_aMC {shlex.quote(order_name)}"
            ),
            distro,
            180,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

    @unittest.skipUnless(
        shutil.which("wsl.exe") or shutil.which("wsl"),
        "WSL is required for the real CutExperiment probe",
    )
    def test_real_cutexperiment_path_is_importable_in_wsl(self):
        config = external_tool_config()
        distro = config["wsl_distro"]
        cutexperiment_path = config["cutexperiment_path"]
        if not distro or not cutexperiment_path:
            self.skipTest("Configure tests/external_tools.json or SMEFT_CUTEXPERIMENT_WSL_PATH")
        command = (
            "set -euo pipefail; "
            f"test -d {shlex.quote(cutexperiment_path)}; "
            "python3 - <<'PY'\n"
            "import importlib.util, os, sys\n"
            f"sys.path.insert(0, {cutexperiment_path!r})\n"
            "spec = importlib.util.find_spec('Interfaces.LHCOlympics')\n"
            "if spec is None:\n"
            "    raise SystemExit('Interfaces.LHCOlympics not importable')\n"
            "print(spec.origin)\n"
            "PY"
        )
        result = run_wsl_probe(command, distro, 30)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()

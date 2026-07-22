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

            write_text(card, "add Branch Output/jets FatJet Jet\n")
            self.assertEqual(detect_jet_branch(card), "FatJet")
            write_text(card, "set NoJetBranch 1\n")
            self.assertIsNone(detect_jet_branch(card))

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
            self.assertIn("Detected jet branch: Jet", str(ctx.exception))
            self.assertIn("Command: ./root2lhco", str(ctx.exception))
            self.assertIn("Return code: 2", str(ctx.exception))
            self.assertIn("root2lhco.log", str(ctx.exception))

    def test_convert_root_to_lhco_missing_output_keeps_diagnostic_context(self):
        with tempfile.TemporaryDirectory() as mg5:
            process = "proc"
            run_folder = "run_01"
            root_dir = os.path.join(mg5, process, "Events", run_folder)
            cards_dir = os.path.join(mg5, process, "Cards")
            write_text(os.path.join(cards_dir, "delphes_card.dat"), "add Branch Output/jets GenJet Jet\n")
            root_path = os.path.join(root_dir, "tag_1_delphes_events.root")
            write_text(root_path, "fake-root")

            with patch(
                "scripts.convert_root_to_lhco.subprocess.run",
                return_value=subprocess.CompletedProcess(["./root2lhco"], 0),
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    convert_root_to_lhco(mg5, process, run_folder)

            message = str(ctx.exception)
            self.assertIn("LHCO file not created", message)
            self.assertIn(f"ROOT input: {root_path}", message)
            self.assertIn("Detected jet branch: GenJet", message)
            self.assertIn("--jet-branch=GenJet", message)
            self.assertIn("Return code: 0", message)

    def test_convert_root_to_lhco_reports_missing_inputs(self):
        with tempfile.TemporaryDirectory() as mg5:
            with self.assertRaisesRegex(RuntimeError, "ROOT file not found"):
                convert_root_to_lhco(mg5, "proc", "run_01")

            root_path = os.path.join(mg5, "proc", "Events", "run_01", "tag_1_delphes_events.root")
            write_text(root_path, "root")
            with self.assertRaises(RuntimeError) as ctx:
                convert_root_to_lhco(mg5, "proc", "run_01")
            self.assertIn("Delphes card not found", str(ctx.exception))
            self.assertIn(root_path, str(ctx.exception))

    def test_convert_root_to_lhco_rejects_empty_header_only_and_error_log_outputs(self):
        cases = [
            ("", "ok\n", "LHCO file is empty"),
            ("header only\n", "ok\n", "LHCO file has no events"),
            ("event one\nevent two\n", "contains 0 events\n", "root2lhco log indicates failure"),
        ]
        for lhco_text, log_text, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as mg5:
                process = "proc"
                run_folder = "run_01"
                root_dir = os.path.join(mg5, process, "Events", run_folder)
                cards_dir = os.path.join(mg5, process, "Cards")
                write_text(os.path.join(cards_dir, "delphes_card.dat"), "add Branch Output/jets Jet Jet\n")
                write_text(os.path.join(root_dir, "tag_1_delphes_events.root"), "root")

                def fake_run(cmd, cwd, stdout, stderr, text):
                    write_text(os.path.abspath(os.path.join(cwd, cmd[2])), lhco_text)
                    stdout.write(log_text)
                    return subprocess.CompletedProcess(cmd, 0)

                with patch("scripts.convert_root_to_lhco.subprocess.run", side_effect=fake_run):
                    with self.assertRaises(RuntimeError) as ctx:
                        convert_root_to_lhco(mg5, process, run_folder)
                self.assertIn(expected, str(ctx.exception))
                self.assertIn("root2lhco.log", str(ctx.exception))

    def test_convert_root_to_lhco_rejects_tiny_output_for_large_root(self):
        with tempfile.TemporaryDirectory() as mg5:
            process = "proc"
            run_folder = "run_01"
            root_dir = os.path.join(mg5, process, "Events", run_folder)
            cards_dir = os.path.join(mg5, process, "Cards")
            write_text(os.path.join(cards_dir, "delphes_card.dat"), "add Branch Output/jets Jet Jet\n")
            write_text(os.path.join(root_dir, "tag_1_delphes_events.root"), "x" * (1024 * 1024 + 1))

            def fake_run(cmd, cwd, stdout, stderr, text):
                write_text(os.path.abspath(os.path.join(cwd, cmd[2])), "event one\nevent two\n")
                stdout.write("ok\n")
                return subprocess.CompletedProcess(cmd, 0)

            with patch("scripts.convert_root_to_lhco.subprocess.run", side_effect=fake_run):
                with self.assertRaisesRegex(RuntimeError, "suspiciously small"):
                    convert_root_to_lhco(mg5, process, run_folder)

    @unittest.skipUnless(
        shutil.which("wsl.exe") or shutil.which("wsl"),
        "WSL is required for the real Delphes-card copy test",
    )
    def test_real_muon_collider_card_dependencies_copy_in_wsl(self):
        config = external_tool_config()
        distro = config["wsl_distro"]
        mg5_path = config["madgraph_path"]
        if not distro or not mg5_path:
            self.skipTest("Configure tests/external_tools.json or SMEFT_MG5_WSL_* to enable the card test")

        script_path = "/mnt/" + str(ROOT / "scripts" / "setup_delphes_card.py").replace(":", "", 1).replace("\\", "/").lower()
        test_root = f"/tmp/smeft_delphes_card_test_{os.getpid()}"
        command = (
            "set -euo pipefail; "
            f"test {shlex.quote(test_root)} != /; rm -rf -- {shlex.quote(test_root)}; "
            f"mkdir -p {shlex.quote(test_root + '/Delphes')} {shlex.quote(test_root + '/proc')}; "
            f"ln -s {shlex.quote(mg5_path + '/Delphes/cards')} {shlex.quote(test_root + '/Delphes/cards')}; "
            f"python3 {shlex.quote(script_path)} {shlex.quote(test_root)} delphes_card_MuonColliderDet.tcl proc; "
            f"test -s {shlex.quote(test_root + '/proc/Cards/delphes_card.dat')}; "
            f"test -d {shlex.quote(test_root + '/proc/Cards/MuonCollider')}; "
            "for f in MuonColliderDet_JetReco.tcl MuonColliderDet_JetSmearing.tcl "
            "MuonColliderDet_JetFlavorAssociation.tcl MuonColliderDet_BTagging.tcl "
            f"MuonColliderDet_TauTagging.tcl; do test -s {shlex.quote(test_root + '/proc/Cards/MuonCollider')}/\"$f\"; done; "
            f"rm -rf -- {shlex.quote(test_root)}"
        )
        result = run_wsl_probe(command, distro, 30)
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )

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

        smoke_root = f"/tmp/smeft_mg5_smoke_{os.getpid()}"
        process = f"{smoke_root}/process"
        order_name = f"{smoke_root}/order.txt"
        order_text = "\n".join([
            "import model sm",
            "generate e+ e- > mu+ mu-",
            f"output {process}",
        ]) + "\n"
        result = run_wsl_probe(
            (
                "set -euo pipefail; "
                f"test {shlex.quote(smoke_root)} != /; rm -rf -- {shlex.quote(smoke_root)}; "
                f"mkdir -p {shlex.quote(smoke_root)}; trap 'rm -rf -- {shlex.quote(smoke_root)}' EXIT; "
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

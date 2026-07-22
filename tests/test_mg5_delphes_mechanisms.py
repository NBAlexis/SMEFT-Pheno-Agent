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


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


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

    @unittest.skipUnless(
        shutil.which("wsl.exe") or shutil.which("wsl"),
        "WSL is required for the real MG5 smoke test",
    )
    def test_real_mg5_smoke_generation_is_short_and_optional(self):
        distro = os.environ.get("SMEFT_MG5_WSL_DISTRO")
        mg5_path = os.environ.get("SMEFT_MG5_WSL_PATH")
        if not distro or not mg5_path:
            self.skipTest("Set SMEFT_MG5_WSL_DISTRO and SMEFT_MG5_WSL_PATH to enable the smoke test")

        process = "smoke_ep_em_to_mu_mu"
        order_name = "smoke_order.txt"
        order_text = "\n".join([
            "import model sm",
            "generate e+ e- > mu+ mu-",
            f"output {process}",
        ]) + "\n"
        cmd = [
            "wsl.exe" if shutil.which("wsl.exe") else "wsl",
            "-d",
            distro,
            "--",
            "bash",
            "-lc",
            (
                "set -euo pipefail; "
                f"cd {shlex.quote(mg5_path)}; "
                f"cat > {shlex.quote(order_name)} <<'EOF'\n{order_text}EOF\n"
                f"./bin/mg5_aMC {shlex.quote(order_name)}"
            ),
        ]
        result = subprocess.run(
            cmd,
            cwd=str(ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
            timeout=180,
        )
        self.assertEqual(
            result.returncode,
            0,
            msg=f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}",
        )


if __name__ == "__main__":
    unittest.main()

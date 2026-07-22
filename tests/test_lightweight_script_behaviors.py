import os
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.beam_energy import compute_sqrt_s
from scripts.count_lhco_events import count_lhco_events
from scripts.extract_cross_section import extract_cross_section
from scripts.extract_weighted_order import extract_weighted_order
from scripts.merge_lhco import merge_lhco
from scripts.normalize_process_name import normalize_process_name
from scripts.parse_param_card import parse_coefficients
from scripts.run_mg5 import run_mg5
from scripts.run_mg5_config import _process_order_lines, validate_config
from scripts.setup_delphes_card import setup_delphes_card


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


class LightweightScriptBehaviorTests(unittest.TestCase):
    def test_small_parsers_accept_representative_mg5_text(self):
        with tempfile.TemporaryDirectory() as root:
            banner = os.path.join(root, "run_banner.txt")
            write_text(banner, "Integrated weight (pb) : 1.25e-03\n")
            self.assertAlmostEqual(extract_cross_section(banner), 1.25e-3)

            param_card = os.path.join(root, "param_card.dat")
            write_text(
                param_card,
                "\n".join([
                    "Block mass",
                    "  25 1.250000e+02 # h",
                    "Block anoinputs",
                    "  1 scan:[-1e-12,0,1e-12] # fM0",
                    "  2 0.0 # fM1",
                    "Block yukawa",
                    "  6 1.0",
                ]),
            )
            parsed = parse_coefficients(param_card, scan_default=9.0)
            self.assertEqual(parsed["block_name"], "anoinputs")
            self.assertEqual(parsed["coefficients"], {"1": 9.0, "2": 0.0})

    def test_mg5_order_helpers_validate_without_starting_mg5(self):
        lines = _process_order_lines(
            ["e+ e- > a a", "e+ e- > z a"],
            process_mode="sm_np",
            weighted_order=4,
            weighted_keyword="WEIGHTED",
        )
        self.assertEqual(lines[0], "generate e+ e- > a a WEIGHTED=4")
        self.assertEqual(lines[1], "add process e+ e- > z a WEIGHTED=4")

        cfg = {
            "mg5path": "/unused",
            "model": "AQGCm_UFO",
            "process": "e+ e- > a a",
            "process_mode": "scan",
            "nevents": 100,
            "ebeam1": 1500.0,
            "ebeam2": 1500.0,
            "c_scan": 1.0,
            "target_coefficient": {"index": 1},
            "output_labels": [f"f{i}" for i in range(11)],
        }
        validate_config(cfg)
        cfg["output_labels"] = ["f0"]
        with self.assertRaises(ValueError):
            validate_config(cfg)

    def test_setup_delphes_card_copies_dependencies_and_sanitizes_execution_path(self):
        with tempfile.TemporaryDirectory() as mg5:
            cards = os.path.join(mg5, "Delphes", "cards")
            process = "proc"
            os.makedirs(os.path.join(mg5, process), exist_ok=True)
            write_text(
                os.path.join(cards, "main.tcl"),
                "\n".join([
                    "source modules/common.tcl",
                    "set ExecutionPath {",
                    "# CommentedModule",
                    "RealModule",
                    "}",
                ]),
            )
            write_text(os.path.join(cards, "modules", "common.tcl"), "set X 1\n")

            copied = setup_delphes_card(mg5, "main.tcl", process)
            self.assertTrue(os.path.exists(copied))
            self.assertTrue(
                os.path.exists(os.path.join(mg5, process, "Cards", "modules", "common.tcl"))
            )
            with open(copied, "r", encoding="utf-8") as handle:
                text = handle.read()
            self.assertNotIn("# CommentedModule", text)
            self.assertIn("RealModule", text)

    def test_weighted_order_extraction_uses_fake_process_files(self):
        with tempfile.TemporaryDirectory() as root:
            model = os.path.join(root, "model")
            process = os.path.join(root, "proc")
            write_text(
                os.path.join(model, "coupling_orders.py"),
                "\n".join([
                    "NP = CouplingOrder(name = 'NP', hierarchy = 2)",
                    "QED = CouplingOrder(name = 'QED', hierarchy = 1)",
                ]),
            )
            write_text(os.path.join(process, "SubProcesses", "subproc.mg"), "P0_aa\n")
            write_text(
                os.path.join(process, "SubProcesses", "P0_aa", "matrix1.ps"),
                "diagram label (NP=2, QED=1)\n",
            )
            result = extract_weighted_order(model, [process])
            self.assertEqual(result["max_weighted_order"], 5)
            self.assertEqual(result["diagram_count"], 1)

    def test_fast_pure_python_helpers(self):
        self.assertEqual(normalize_process_name("e+ e- > a a"), "ep_em_to_a_a")
        ee = compute_sqrt_s("ee", 1500, 1500)
        self.assertEqual(ee["sqrt_s_gev"], 3000.0)
        ep = compute_sqrt_s("ep", 60, 7000)
        self.assertAlmostEqual(ep["sqrt_s_gev"], (4 * 60 * 7000) ** 0.5)

    def test_run_mg5_fails_fast_when_binary_is_absent(self):
        with tempfile.TemporaryDirectory() as mg5:
            write_text(os.path.join(mg5, "order.txt"), "quit\n")
            with self.assertRaises(RuntimeError) as ctx:
                run_mg5(mg5, "order.txt")
            self.assertIn("No MG5 binary", str(ctx.exception))

    def test_run_mg5_parses_stage_markers_from_fake_process(self):
        class FakePipe:
            def __init__(self, lines):
                self._lines = lines

            def __iter__(self):
                return iter(self._lines)

        class FakeProcess:
            def __init__(self):
                self.stdout = FakePipe([
                    "Generating subprocesses\n",
                    "Running Pythia8\n",
                    "Running Delphes\n",
                ])
                self.stderr = FakePipe([])

            def wait(self):
                return 0

            def kill(self):
                return None

        with tempfile.TemporaryDirectory() as mg5:
            write_text(os.path.join(mg5, "order.txt"), "quit\n")
            write_text(os.path.join(mg5, "bin", "mg5_aMC"), "fake\n")
            with patch("scripts.run_mg5.subprocess.Popen", return_value=FakeProcess()):
                with patch("scripts.run_mg5.print"):
                    result = run_mg5(mg5, "order.txt")
            self.assertEqual(result["returncode"], 0)
            self.assertIsNotNone(result["mg5_steps"]["madgraph"]["duration_sec"])
            self.assertIsNotNone(result["mg5_steps"]["pythia8"]["duration_sec"])
            self.assertIsNotNone(result["mg5_steps"]["delphes"]["duration_sec"])

    def test_cutexperiment_count_and_merge_use_fake_lhco_interface(self):
        with tempfile.TemporaryDirectory() as root:
            fake_ce = os.path.join(root, "CutExperiment")
            write_text(os.path.join(fake_ce, "Interfaces", "__init__.py"), "")
            write_text(
                os.path.join(fake_ce, "Interfaces", "LHCOlympics.py"),
                "\n".join([
                    "class EventSet:",
                    "    def __init__(self, path):",
                    "        with open(path, encoding='utf-8') as handle:",
                    "            self.events = [line for line in handle if line.strip()]",
                    "    def GetEventCount(self):",
                    "        return len(self.events)",
                    "    def AddEventSet(self, other):",
                    "        self.events.extend(other.events)",
                    "    def SaveToLHCO(self, path):",
                    "        with open(path, 'w', encoding='utf-8') as handle:",
                    "            handle.writelines(self.events)",
                    "def LoadLHCOlympics(path):",
                    "    return EventSet(path)",
                ]),
            )
            first = os.path.join(root, "first.lhco")
            second = os.path.join(root, "second.lhco")
            first_banner = os.path.join(root, "first_banner.txt")
            second_banner = os.path.join(root, "second_banner.txt")
            write_text(first, "a\nb\n")
            write_text(second, "c\n")
            write_text(first_banner, "Integrated weight (pb) : 2.0\n")
            write_text(second_banner, "Integrated weight (pb) : 5.0\n")

            for name in list(sys.modules):
                if name == "Interfaces" or name.startswith("Interfaces."):
                    sys.modules.pop(name)
            record = count_lhco_events(first, requested_event_count=4, cutexperiment_path=fake_ce)
            self.assertEqual(record["loaded_lhco_event_count"], 2)
            self.assertEqual(record["status"], "accepted_with_warning")

            output = os.path.join(root, "merged", "out.lhco")
            metadata = merge_lhco(
                [first, second],
                output,
                cutexperiment_path=fake_ce,
                source_banner_paths=[first_banner, second_banner],
                requested_event_count=4,
            )
            self.assertEqual(metadata["merged_loaded_lhco_event_count"], 3)
            self.assertAlmostEqual(metadata["merged_cross_section_pb"], 3.0)


if __name__ == "__main__":
    unittest.main()

import json
import os
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from scripts.beam_energy import compute_sqrt_s
from scripts.archive_mg5_outputs import archive_mg5_outputs
from scripts.count_lhco_events import count_lhco_events
import scripts.calculate_shared_f5_background as shared_f5_module
from scripts.calculate_shared_f5_background import calculate_shared_f5_background
from scripts.double_check_zero_cross_section import double_check_zero_cross_section
from scripts.durable_exec import (
    existing_job_files,
    job_paths,
    remote_start_command,
    remote_status_command,
    safe_name,
)
from scripts.extract_cross_section import extract_cross_section
from scripts.extract_weighted_order import extract_weighted_order
from scripts.install_cutexperiment import validate_cutexperiment
from scripts.install_mg5 import verify_installation
from scripts.load_run_config import load_run_config
from scripts.merge_lhco import merge_lhco
from scripts.normalize_process_name import normalize_process_name
from scripts.parse_param_card import parse_coefficients
from scripts.read_results import get_anchor_model, get_c_scan, get_operator_c_scan, get_cs_sm
import scripts.recover_lhco_count as recover_module
import scripts.run_mg5_config as mg5_config_module
from scripts.run_mg5 import run_mg5
from scripts.run_mg5_config import (
    _beam_lines,
    _cleanup_candidates,
    _coefficient_lines,
    _create_process,
    _labels_for_runs,
    _launch_process,
    _mark_process_dir_broken,
    _process_order_lines,
    _remove_large_intermediates,
    validate_config,
)
from scripts.setup_delphes_card import setup_delphes_card
from scripts.timing_tracker import TimingTracker


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


class LightweightScriptBehaviorTests(unittest.TestCase):
    def test_shared_f5_background_uses_observed_count(self):
        result = calculate_shared_f5_background(2.0, 100, 4, 0)
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(result["convention"], "observed_events")
        self.assertEqual(result["effective_passing_event_count"], 4.0)
        self.assertAlmostEqual(result["sigma0_after_cut_pb"], 0.08)

    def test_shared_f5_background_requires_three_anchor_rounds_for_zero(self):
        for rounds in (0, 1, 2):
            result = calculate_shared_f5_background(2.0, 100, 0, rounds)
            self.assertEqual(result["status"], "additional_anchor_f5_required")
            self.assertIsNone(result["sigma0_after_cut_pb"])
            self.assertIsNone(result["effective_passing_event_count"])

    def test_shared_f5_background_uses_half_event_after_three_rounds(self):
        result = calculate_shared_f5_background(2.0, 100, 0, 3)
        self.assertEqual(result["convention"], "half_event_after_three_zero_rounds")
        self.assertEqual(result["passing_event_count"], 0)
        self.assertEqual(result["effective_passing_event_count"], 0.5)
        self.assertAlmostEqual(result["sigma0_after_cut_pb"], 0.01)

    def test_shared_f5_background_rejects_invalid_counts(self):
        with self.assertRaisesRegex(ValueError, "positive integer"):
            calculate_shared_f5_background(1.0, 0, 0, 0)
        with self.assertRaisesRegex(ValueError, "between zero"):
            calculate_shared_f5_background(1.0, 10, 11, 0)
        with self.assertRaisesRegex(ValueError, r"in \[0, 3\]"):
            calculate_shared_f5_background(1.0, 10, 0, 4)

    def test_shared_f5_background_cli_writes_json(self):
        with tempfile.TemporaryDirectory() as root:
            input_path = os.path.join(root, "input.json")
            output_path = os.path.join(root, "nested", "output.json")
            with open(input_path, "w", encoding="utf-8") as handle:
                json.dump({
                    "merged_cross_section_pb": 2.0,
                    "loaded_lhco_event_count": 100,
                    "passing_event_count": 0,
                    "additional_anchor_f5_rounds": 3,
                }, handle)
            with patch.object(sys, "argv", ["calculate_shared_f5_background.py", "--input", input_path, "--output", output_path]):
                with patch("builtins.print"):
                    self.assertEqual(shared_f5_module.main(), 0)
            with open(output_path, encoding="utf-8") as handle:
                self.assertEqual(json.load(handle)["sigma0_after_cut_pb"], 0.01)

    def test_archive_mg5_outputs_moves_small_files_and_only_deletes_large_files(self):
        with tempfile.TemporaryDirectory() as root:
            run_root = os.path.join(root, "results")
            process = os.path.join(root, "MG5", "proc")
            order = os.path.join(root, "MG5", "order.txt")
            write_text(os.path.join(process, "Events", "run_01", "events.root"), "large\n")
            write_text(os.path.join(process, "Events", "run_01", "events.hepmc.gz"), "large\n")
            write_text(os.path.join(process, "Events", "run_01", "events.lhe.gz"), "keep\n")
            write_text(os.path.join(process, "Cards", "param_card.dat"), "keep\n")
            write_text(order, "launch proc\n")
            write_text(
                os.path.join(run_root, "data", "phase5", "runner.json"),
                json.dumps({"process_dir": process, "launch": {"order_file_path": order}}),
            )

            result = archive_mg5_outputs(run_root, delete_large=True)

            archived = os.path.join(run_root, "mg5_processes", "proc")
            self.assertTrue(os.path.isfile(os.path.join(archived, "Events", "run_01", "events.lhe.gz")))
            self.assertTrue(os.path.isfile(os.path.join(archived, "Cards", "param_card.dat")))
            self.assertFalse(os.path.exists(os.path.join(archived, "Events", "run_01", "events.root")))
            self.assertFalse(os.path.exists(os.path.join(archived, "Events", "run_01", "events.hepmc.gz")))
            self.assertTrue(os.path.isfile(os.path.join(run_root, "orders", "order.txt")))
            self.assertEqual(len(result["deleted_files"]), 2)
            self.assertEqual(result["missing_process_dirs"], [])
            self.assertEqual(result["missing_order_files"], [])

    def test_small_parsers_accept_representative_mg5_text(self):
        with tempfile.TemporaryDirectory() as root:
            banner = os.path.join(root, "run_banner.txt")
            write_text(banner, "Integrated weight (pb) : 1.25e-03\n")
            self.assertAlmostEqual(extract_cross_section(banner), 1.25e-3)

            infinite_banner = os.path.join(root, "infinite_banner.txt")
            write_text(infinite_banner, "Integrated weight (pb) : 1e999\n")
            with self.assertRaisesRegex(ValueError, "must be finite"):
                extract_cross_section(infinite_banner)

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

    def test_weighted_keyword_fallback_preserves_partial_process_directory(self):
        with tempfile.TemporaryDirectory() as mg5path:
            calls = []

            def fake_run(_cfg, stem, root, _order_name):
                calls.append(stem)
                if len(calls) == 1:
                    os.makedirs(os.path.join(root, "weighted_proc"), exist_ok=True)
                    raise RuntimeError("InvalidCmd: WEIGHTED is not recognized")
                return ({"stdout": "2 diagrams\n", "stderr": "", "returncode": 0}, {})

            cfg = {
                "mg5path": mg5path,
                "model": "toy_model",
                "process": "e+ e- > a a",
                "process_mode": "sm_np",
                "weighted_order": 3,
            }
            with patch.object(mg5_config_module, "_run_mg5_with_recorded_logs", side_effect=fake_run):
                created = _create_process(cfg, "weighted_proc")

            self.assertEqual(calls, ["create_weighted_proc_WEIGHTED", "create_weighted_proc_Weighted"])
            self.assertEqual(created["weighted_keyword"], "Weighted")
            self.assertTrue(created["weighted_attempts"][0]["broken_process_dir"])
            self.assertFalse(os.path.exists(os.path.join(mg5path, "weighted_proc")))

    def test_weighted_keyword_does_not_retry_non_syntax_failure(self):
        with tempfile.TemporaryDirectory() as mg5path:
            cfg = {
                "mg5path": mg5path,
                "model": "toy_model",
                "process": "e+ e- > a a",
                "process_mode": "sm_np",
                "weighted_order": 3,
            }
            with patch.object(
                mg5_config_module,
                "_run_mg5_with_recorded_logs",
                side_effect=RuntimeError("Delphes card file is missing"),
            ) as run:
                with self.assertRaisesRegex(RuntimeError, "all weighted-order syntaxes"):
                    _create_process(cfg, "weighted_proc")
            self.assertEqual(run.call_count, 1)

    def test_mg5_config_value_helpers_validate_without_starting_mg5(self):
        cfg = {
            "mg5path": "/unused",
            "model": "AQGCm_UFO",
            "process": "e+ e- > a a",
            "process_mode": "scan",
            "delphes_card": "delphes_card.dat",
            "nevents": 100,
            "ebeam1": 1500.0,
            "ebeam2": 1500.0,
            "c_scan": 1.0,
            "target_coefficient": {"index": 1},
            "output_labels": [f"f{i}" for i in range(11)],
        }
        validate_config(cfg)
        missing_card = dict(cfg)
        missing_card.pop("delphes_card")
        with self.assertRaisesRegex(ValueError, "undetected LHE events"):
            validate_config(missing_card)
        validate_config({
            "mg5path": "/unused",
            "model": "AQGCm_UFO",
            "process": "e+ e- > a a",
            "process_mode": "create_np",
        })
        cfg["output_labels"] = ["f0"]
        with self.assertRaises(ValueError):
            validate_config(cfg)

        parsed = {"block_name": "anoinputs", "coefficients": {"1": 0.0, "2": 1.0}}
        launch_cfg = {
            "process_mode": "scan",
            "target_coefficient": {"index": 2},
            "c_scan": 3.0,
            "ebeam1": 1500,
            "ebeam2": 1500,
            "polarization": {"polbeam1": -0.8, "polbeam2": 0.3},
        }
        self.assertEqual(
            _coefficient_lines(launch_cfg, parsed),
            ["set anoinputs 1 0.0", "set anoinputs 2 scan:[-3.0 + 0.2 * 3.0 * n for n in range(11)]"],
        )
        self.assertEqual(
            _beam_lines(launch_cfg),
            ["set ebeam1 = 1500", "set ebeam2 = 1500", "set polbeam1 = -0.8", "set polbeam2 = 0.3"],
        )
        point_cfg = {
            "mg5path": "/unused",
            "model": "AQGCm_UFO",
            "process": "e+ e- > a a",
            "process_mode": "sm_np_point",
            "delphes_card": "delphes_card.dat",
            "nevents": 100,
            "ebeam1": 1500.0,
            "ebeam2": 1500.0,
            "operator": "o_1",
            "coefficient_mode": "explicit",
            "target_coefficient": {"index": 2, "value": 0.0},
            "output_label": "shared_f5_anchor_round_1",
        }
        validate_config(point_cfg)
        self.assertEqual(
            _coefficient_lines(point_cfg, parsed),
            ["set anoinputs 1 0.0", "set anoinputs 2 0.0"],
        )
        self.assertEqual(
            _labels_for_runs(point_cfg, 1),
            ["shared_f5_anchor_round_1"],
        )
        point_cfg["output_labels"] = ["one", "two"]
        with self.assertRaisesRegex(ValueError, "exactly 1"):
            validate_config(point_cfg)
        point_cfg["output_labels"] = ["one"]
        point_cfg["coefficient_mode"] = "default"
        with self.assertRaisesRegex(ValueError, "requires coefficient_mode='explicit'"):
            validate_config(point_cfg)
        point_cfg["coefficient_mode"] = "explicit"
        point_cfg["target_coefficient"]["value"] = float("nan")
        with self.assertRaisesRegex(ValueError, "finite number"):
            validate_config(point_cfg)
        self.assertEqual(
            _labels_for_runs({"process_mode": "scan", "operator": "o_1"}, 3),
            ["np_o_1_f0", "np_o_1_f1", "np_o_1_f2"],
        )

    def test_setup_delphes_card_copies_dependencies_and_sanitizes_execution_path(self):
        with tempfile.TemporaryDirectory() as mg5:
            cards = os.path.join(mg5, "Delphes", "cards")
            process = "proc"
            os.makedirs(os.path.join(mg5, process), exist_ok=True)
            write_text(
                os.path.join(cards, "main.tcl"),
                "\n".join([
                    "source modules/common.tcl",
                    "include \"modules/quoted file.tcl\"",
                    "set ExecutionPath {",
                    "# CommentedModule",
                    "RealModule",
                    "}",
                ]),
            )
            write_text(os.path.join(cards, "modules", "common.tcl"), "source nested/inner.tcl\n")
            write_text(os.path.join(cards, "modules", "nested", "inner.tcl"), "set INNER 1\n")
            write_text(os.path.join(cards, "modules", "quoted file.tcl"), "set QUOTED 1\n")

            copied = setup_delphes_card(mg5, "main.tcl", process)
            self.assertTrue(os.path.exists(copied))
            self.assertTrue(
                os.path.exists(os.path.join(mg5, process, "Cards", "modules", "common.tcl"))
            )
            self.assertTrue(
                os.path.exists(os.path.join(mg5, process, "Cards", "modules", "nested", "inner.tcl"))
            )
            self.assertTrue(
                os.path.exists(os.path.join(mg5, process, "Cards", "modules", "quoted file.tcl"))
            )
            with open(copied, "r", encoding="utf-8") as handle:
                text = handle.read()
            self.assertNotIn("# CommentedModule", text)
            self.assertIn("RealModule", text)

    def test_setup_delphes_card_reports_each_unresolved_dependency(self):
        with tempfile.TemporaryDirectory() as mg5:
            cards = os.path.join(mg5, "Delphes", "cards")
            process = "proc"
            os.makedirs(os.path.join(mg5, process), exist_ok=True)
            main_card = os.path.join(cards, "main.tcl")
            write_text(
                main_card,
                "# source ignored/commented.tcl\nsource MuonCollider/missing.tcl\n",
            )

            with self.assertRaises(FileNotFoundError) as ctx:
                setup_delphes_card(mg5, "main.tcl", process)

            message = str(ctx.exception)
            self.assertIn("Unresolved Delphes card dependencies", message)
            self.assertIn(main_card, message)
            self.assertIn("MuonCollider/missing.tcl", message)
            self.assertIn(os.path.join(cards, "MuonCollider", "missing.tcl"), message)
            self.assertNotIn("ignored/commented.tcl", message)

    def test_setup_delphes_card_reports_dynamic_tcl_dependency(self):
        with tempfile.TemporaryDirectory() as mg5:
            cards = os.path.join(mg5, "Delphes", "cards")
            process = "proc"
            os.makedirs(os.path.join(mg5, process), exist_ok=True)
            write_text(
                os.path.join(cards, "dynamic.tcl"),
                "source [file join $carddir modules helper.tcl]\n",
            )

            with self.assertRaises(FileNotFoundError) as caught:
                setup_delphes_card(mg5, "dynamic.tcl", process)

            message = str(caught.exception)
            self.assertIn("[file join $carddir modules helper.tcl]", message)
            self.assertIn("cannot safely evaluate", message)

    def test_setup_delphes_card_rejects_dependency_outside_cards_tree(self):
        with tempfile.TemporaryDirectory() as mg5:
            cards = os.path.join(mg5, "Delphes", "cards")
            process = "proc"
            os.makedirs(os.path.join(mg5, process), exist_ok=True)
            outside = os.path.join(mg5, "Delphes", "outside.tcl")
            write_text(outside, "set OUTSIDE 1\n")
            write_text(os.path.join(cards, "main.tcl"), "source ../outside.tcl\n")

            with self.assertRaises(FileNotFoundError) as ctx:
                setup_delphes_card(mg5, "main.tcl", process)

            self.assertIn("outside Delphes/cards", str(ctx.exception))
            self.assertFalse(os.path.exists(os.path.join(mg5, process, "outside.tcl")))

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

            write_text(
                os.path.join(process, "SubProcesses", "P0_aa", "matrix1.ps"),
                "diagram label (NP=2, QED=1, QCD=1)\n",
            )
            matrix_path = os.path.join(process, "SubProcesses", "P0_aa", "matrix1.ps")
            with self.assertRaises(ValueError) as ctx:
                extract_weighted_order(model, [process])
            message = str(ctx.exception)
            self.assertIn("Missing coupling-order hierarchies for: QCD", message)
            self.assertIn(os.path.join(model, "coupling_orders.py"), message)
            self.assertIn(matrix_path, message)

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
            self.assertEqual(
                metadata["cross_section_rule"],
                "loaded_event_count_weighted_average",
            )

            arithmetic_output = os.path.join(root, "merged", "arithmetic.lhco")
            arithmetic = merge_lhco(
                [first, second],
                arithmetic_output,
                cutexperiment_path=fake_ce,
                source_banner_paths=[first_banner, second_banner],
                requested_event_count=4,
                cross_section_rule="banner_arithmetic_mean",
            )
            self.assertAlmostEqual(arithmetic["merged_cross_section_pb"], 3.5)
            self.assertEqual(arithmetic["cross_section_rule"], "banner_arithmetic_mean")

            with self.assertRaisesRegex(ValueError, "cross_section_rule"):
                merge_lhco(
                    [first],
                    os.path.join(root, "merged", "invalid.lhco"),
                    cutexperiment_path=fake_ce,
                    source_banner_paths=[first_banner],
                    cross_section_rule="invalid",
                )

    def test_zero_cross_section_checker_requires_logs_and_no_substantial_lhe(self):
        with tempfile.TemporaryDirectory() as root:
            stdout_log = os.path.join(root, "stdout.log")
            run_dir = os.path.join(root, "run_01")
            write_text(stdout_log, "MG5 reports zero cross-section\n")
            write_text(os.path.join(run_dir, "events.lhe"), "tiny")
            confirmed = double_check_zero_cross_section(0.0, [stdout_log], [], run_dir)
            self.assertTrue(confirmed["confirmed"], confirmed)

            write_text(os.path.join(run_dir, "large.lhe"), "x" * 5000)
            suspicious = double_check_zero_cross_section(0.0, [stdout_log], [], run_dir)
            self.assertFalse(suspicious["confirmed"], suspicious)
            self.assertTrue(suspicious["substantial_lhe_files"])

            tar_path = os.path.join(run_dir, "events.tar.gz")
            inner = os.path.join(root, "events.lhe")
            write_text(inner, "tiny")
            with tarfile.open(tar_path, "w:gz") as tar:
                tar.add(inner, arcname="events.lhe")
            tar_report = double_check_zero_cross_section(0.0, [stdout_log], [], run_dir, small_lhe_bytes=10000)
            self.assertTrue(any(item["path"].endswith("events.tar.gz") for item in tar_report["lhe_files"]))

            huge_banner = os.path.join(root, "huge_banner.txt")
            write_text(huge_banner, "Integrated weight (pb) : 1.0e20\n")
            self.assertEqual(extract_cross_section(huge_banner), 1.0e20)
            huge_report = double_check_zero_cross_section(1.0e20, [stdout_log], [], run_dir)
            self.assertEqual(huge_report["status"], "not_zero_cross_section")
            self.assertFalse(huge_report["confirmed"])

    def test_install_and_read_result_helpers_on_fake_layouts(self):
        with tempfile.TemporaryDirectory() as root:
            mg5 = os.path.join(root, "MG5")
            write_text(os.path.join(mg5, "bin", "mg5_aMC"), "fake")
            write_text(os.path.join(mg5, "HEPTools", "pythia8", "lib", "libpythia8.so"), "fake")
            write_text(os.path.join(mg5, "HEPTools", "lhapdf6_py3", "bin", "lhapdf-config"), "fake")
            write_text(os.path.join(mg5, "Delphes", "cards", "card.tcl"), "fake")
            verify_installation(mg5)

            cutexp = os.path.join(root, "CutExperiment")
            write_text(os.path.join(cutexp, "README.md"), "# fake\n")
            self.assertEqual(validate_cutexperiment(cutexp), (True, "ok"))
            py_only_cutexp = os.path.join(root, "CutExperimentPyOnly")
            write_text(os.path.join(py_only_cutexp, "Interfaces", "LHCOlympics.py"), "class Event: pass\n")
            self.assertEqual(validate_cutexperiment(py_only_cutexp), (True, "ok"))
            empty_cutexp = os.path.join(root, "CutExperimentEmpty")
            os.makedirs(empty_cutexp)
            ok, message = validate_cutexperiment(empty_cutexp)
            self.assertFalse(ok)
            self.assertIn("no Python files", message)
            missing = os.path.join(root, "missing")
            ok, message = validate_cutexperiment(missing)
            self.assertFalse(ok)
            self.assertIn("does not exist", message)

            workdir = os.path.join(root, "work")
            write_text(os.path.join(workdir, "results", "data", "phase3", "anchor.json"), '{"model":"M","name":"fM0"}')
            write_text(
                os.path.join(workdir, "results", "data", "phase4", "coefficient_ranges.json"),
                '{"operators":{"o_1":{"c_scan":2.5}}}',
            )
            write_text(os.path.join(workdir, "results", "data", "phase4", "sm_baseline.json"), '{"cs_sm":1.2}')
            self.assertEqual(get_anchor_model(workdir), "M")
            self.assertEqual(get_operator_c_scan(workdir, "o_1"), 2.5)
            self.assertEqual(get_cs_sm(workdir), 1.2)
            with self.assertRaises(ValueError):
                get_c_scan(workdir)

    def test_durable_exec_command_builders_and_timing_tracker(self):
        self.assertEqual(safe_name("phase 6/scan"), "phase_6_scan")
        with self.assertRaises(ValueError):
            safe_name("")
        paths = job_paths("/tmp/jobs", "phase 6")
        command = remote_start_command("python run.py", "/tmp/work dir", paths, "phase_6", "wsl2")
        self.assertIn("mkdir -p /tmp/jobs", command)
        self.assertIn("/tmp/work dir", command)
        self.assertIn("nohup bash", command)
        self.assertIn("( nohup bash", command)
        self.assertIn("pid=$!", command)
        self.assertIn("already has status files", command)
        status_command = remote_status_command(paths, "phase_6")
        self.assertIn('"status":"running"', status_command)
        self.assertIn("status=completed", status_command)
        self.assertIn("status=failed", status_command)

        with tempfile.TemporaryDirectory() as job_dir:
            local_paths = job_paths(job_dir, "phase_6")
            write_text(local_paths["stdout"], "previous run\n")
            self.assertEqual(existing_job_files(local_paths), [local_paths["stdout"]])

        tracker = TimingTracker()
        with patch("scripts.timing_tracker.print"):
            tracker.start_phase("Phase 3: Validation")
            tracker.record_mg5_step("madgraph", 1.0, 2.5)
            tracker.end_phase("Phase 3: Validation")
        data = tracker.to_dict()
        self.assertEqual(data["phases"]["Phase 3: Validation"]["status"], "done")
        self.assertEqual(data["mg5_steps"]["Phase 3: Validation"]["madgraph"]["duration_sec"], 1.5)

    def test_cleanup_only_deletes_root_and_hepmc_large_files(self):
        with tempfile.TemporaryDirectory() as root:
            process = os.path.join(root, "proc")
            run = os.path.join(process, "Events", "run_01")
            root_file = os.path.join(run, "tag_1_delphes_events.root")
            hepmc_file = os.path.join(run, "tag_1_pythia8_events.hepmc.gz")
            lhe_file = os.path.join(run, "unweighted_events.lhe.gz")
            banner_file = os.path.join(run, "run_01_tag_1_banner.txt")
            order_file = os.path.join(process, "Cards", "run_card.dat")
            for path in (root_file, hepmc_file, lhe_file, banner_file, order_file):
                write_text(path, "payload\n")

            self.assertEqual(
                set(_cleanup_candidates(root, "proc", ["run_01"])),
                {os.path.abspath(root_file), os.path.abspath(hepmc_file)},
            )
            removed = _remove_large_intermediates(process)
            self.assertEqual(set(removed), {os.path.abspath(root_file), os.path.abspath(hepmc_file)})
            self.assertFalse(os.path.exists(root_file))
            self.assertFalse(os.path.exists(hepmc_file))
            self.assertTrue(os.path.exists(lhe_file))
            self.assertTrue(os.path.exists(banner_file))
            self.assertTrue(os.path.exists(order_file))

    def test_marking_failed_process_preserves_root_and_hepmc_evidence(self):
        with tempfile.TemporaryDirectory() as root:
            process = os.path.join(root, "proc")
            root_file = os.path.join(process, "Events", "run_01", "events.root")
            hepmc_file = os.path.join(process, "Events", "run_01", "events.hepmc.gz")
            write_text(root_file, "root evidence\n")
            write_text(hepmc_file, "hepmc evidence\n")

            broken, removed = _mark_process_dir_broken(process)

            self.assertEqual(removed, [])
            self.assertFalse(os.path.exists(process))
            self.assertTrue(os.path.exists(os.path.join(broken, "Events", "run_01", "events.root")))
            self.assertTrue(os.path.exists(os.path.join(broken, "Events", "run_01", "events.hepmc.gz")))

    def test_sde_survey_profile_is_written_to_launch_order(self):
        with tempfile.TemporaryDirectory() as mg5:
            process_folder = "proc"
            events_dir = os.path.join(mg5, process_folder, "Events")
            os.makedirs(events_dir, exist_ok=True)
            cfg = {
                "mg5path": mg5,
                "process_mode": "pure_np",
                "nevents": 10,
                "ebeam1": 120,
                "ebeam2": 120,
                "survey_profile": "sde0_hs2",
                "launch_order_filename": "launch_order.txt",
                "log_dir": os.path.join(mg5, "logs"),
            }

            def fake_run(_mg5path, _order_name):
                os.makedirs(os.path.join(events_dir, "run_01"), exist_ok=True)
                return {"returncode": 0, "stdout": "ok", "stderr": "", "mg5_steps": {}}

            with patch("scripts.run_mg5_config.run_mg5", side_effect=fake_run):
                result, runs = _launch_process(cfg, process_folder, {"block_name": "anoinputs", "coefficients": {}})

            self.assertEqual(runs, ["run_01"])
            self.assertEqual(result["survey_profile"], "sde0_hs2")
            with open(os.path.join(mg5, "launch_order.txt"), encoding="utf-8") as handle:
                order = handle.read()
            self.assertIn("set sde_strategy = 0", order)
            self.assertIn("set hard_survey = 2", order)

    def test_sm_np_point_launches_one_explicit_zero_coefficient_run(self):
        with tempfile.TemporaryDirectory() as mg5:
            process_folder = "proc"
            events_dir = os.path.join(mg5, process_folder, "Events")
            os.makedirs(events_dir, exist_ok=True)
            cfg = {
                "mg5path": mg5,
                "process_mode": "sm_np_point",
                "nevents": 10,
                "ebeam1": 120,
                "ebeam2": 120,
                "coefficient_mode": "explicit",
                "target_coefficient": {"index": 2, "value": 0.0},
                "launch_order_filename": "point_order.txt",
                "log_dir": os.path.join(mg5, "logs"),
            }

            def fake_run(_mg5path, _order_name):
                os.makedirs(os.path.join(events_dir, "run_01"), exist_ok=True)
                return {"returncode": 0, "stdout": "ok", "stderr": "", "mg5_steps": {}}

            parsed = {"block_name": "anoinputs", "coefficients": {"1": 2.0, "2": 3.0}}
            with patch("scripts.run_mg5_config.run_mg5", side_effect=fake_run):
                _, runs = _launch_process(cfg, process_folder, parsed)

            self.assertEqual(runs, ["run_01"])
            with open(os.path.join(mg5, "point_order.txt"), encoding="utf-8") as handle:
                order = handle.read()
            self.assertIn("set anoinputs 1 0.0", order)
            self.assertIn("set anoinputs 2 0.0", order)

    def test_load_run_config_validates_core_schema_and_defaults(self):
        with tempfile.TemporaryDirectory() as root:
            config_path = os.path.join(root, "run_config.json")
            base = {
                "version": "1.0",
                "madgraph_path": "wsl2:/opt/MG5",
                "workdir": "wsl2:/work",
                "process": ["e+ e- > mu+ mu-"],
                "models": ["sm"],
                "energy": [240],
                "luminosity": [5.0],
                "delphes_card": "cards/card.tcl",
                "run_configurations": [{"ebeam1": 120, "ebeam2": 120}],
                "execution": {"mode": "wsl2", "wsl_distro": "Ubuntu-22.04"},
                "polarization": {"polbeam1": -0.8, "polbeam2": 0.3},
                "debug": True,
            }
            write_text(config_path, json.dumps(base))
            cfg = load_run_config(config_path)
            self.assertEqual(cfg.models, ["sm"])
            self.assertEqual(cfg.execution.mode, "wsl2")
            self.assertEqual(cfg.locked_event_counts.nev_scan, 100000)
            self.assertEqual(cfg.analysis_notes.focused_operators, [])
            self.assertAlmostEqual(cfg.polarization.polbeam1, -0.8)

            non_boolean_debug = dict(base)
            non_boolean_debug["debug"] = "true"
            write_text(config_path, json.dumps(non_boolean_debug))
            with self.assertRaisesRegex(ValueError, "debug must be a boolean"):
                load_run_config(config_path)

            normal = dict(base)
            normal.pop("debug")
            write_text(config_path, json.dumps(normal))
            normal_cfg = load_run_config(config_path)
            self.assertFalse(normal_cfg.debug)
            self.assertEqual(normal_cfg.locked_event_counts.nev_scan, 1000000)

            reduced = dict(base)
            reduced["locked_event_counts"] = {
                "nev_phase3": 1000,
                "nev_phase4": 1000,
                "nev_sm": 50000,
                "nev_np": 10000,
                "nev_scan": 100000,
            }
            write_text(config_path, json.dumps(reduced))
            self.assertEqual(load_run_config(config_path).locked_event_counts.nev_sm, 50000)

            too_small = dict(base)
            too_small["locked_event_counts"] = dict(reduced["locked_event_counts"])
            too_small["locked_event_counts"]["nev_scan"] = 99999
            write_text(config_path, json.dumps(too_small))
            with self.assertRaisesRegex(ValueError, "selected debug mode"):
                load_run_config(config_path)

            scientific_with_debug_counts = dict(reduced)
            scientific_with_debug_counts["debug"] = False
            write_text(config_path, json.dumps(scientific_with_debug_counts))
            with self.assertRaisesRegex(ValueError, "selected debug mode"):
                load_run_config(config_path)

            broken = dict(base)
            broken["luminosity"] = [5.0, 10.0]
            write_text(config_path, json.dumps(broken))
            with self.assertRaisesRegex(ValueError, "lengths must match"):
                load_run_config(config_path)

            ep = dict(base)
            ep.update({
                "collider_type": "ep",
                "energy": None,
                "ebeam_electron": [60],
                "ebeam_proton": [7000],
                "run_configurations": [{"ebeam1": 60, "ebeam2": 7000}],
            })
            write_text(config_path, json.dumps(ep))
            self.assertEqual(load_run_config(config_path).collider_type, "ep")

    def test_recover_lhco_count_accepts_short_fake_attempts_and_records_failures(self):
        with tempfile.TemporaryDirectory() as root:
            source_lhco = os.path.join(root, "source.lhco")
            write_text(source_lhco, "fake lhco\n")
            source_banner = os.path.join(root, "banner.txt")
            write_text(source_banner, "Integrated weight (pb) 1.0\n")
            recovery_lhco = os.path.join(root, "recovery.lhco")
            write_text(recovery_lhco, "recovery lhco\n")
            config = {
                "base_mg5_config": {
                    "process_mode": "pure_np",
                    "operator": "o_1",
                    "process_folder": os.path.join(root, "proc"),
                    "result_json": os.path.join(root, "merged", "np_o_1_result.json"),
                },
                "requested_event_count": 100,
                "recovery_profiles": ["default", "sde0_hs0"],
                "attempt_root": os.path.join(root, "attempts"),
                "merged_output_dir": os.path.join(root, "merged"),
                "metadata_path": os.path.join(root, "metadata.json"),
            }

            initial_result_json = os.path.join(root, "initial_result.json")
            write_text(
                initial_result_json,
                json.dumps({
                    "survey_profile": "default",
                    "outputs": [{
                        "label": "np_o_1",
                        "lhco_path": recovery_lhco,
                        "banner_path": source_banner,
                        "loaded_lhco_event_count": 3,
                    }],
                }),
            )
            config["initial_result_json"] = initial_result_json

            executed_profiles = []

            def fake_run(cfg):
                executed_profiles.append(cfg["survey_profile"])
                count = 8
                return {
                    "outputs": [{
                        "label": "np_o_1",
                        "lhco_path": source_lhco,
                        "banner_path": source_banner,
                        "loaded_lhco_event_count": count,
                    }]
                }

            merged_sources = []

            def fake_merge(sources, output_lhco, **kwargs):
                merged_sources.extend(sources)
                write_text(output_lhco, "merged\n")
                write_text(kwargs["metadata_path"], "{}\n")
                return {
                    "merged_loaded_lhco_event_count": 11,
                    "merged_cross_section_pb": 1.0,
                    "source_banners_retained": kwargs["source_banner_paths"],
                }

            with patch.object(recover_module, "run_from_config", side_effect=fake_run), patch.object(
                recover_module, "merge_lhco", side_effect=fake_merge
            ):
                metadata = recover_module.recover_lhco_count(config)

            self.assertEqual(metadata["status"], "accepted")
            self.assertEqual(metadata["final_loaded_counts"], {"np_o_1": 11})
            self.assertEqual(len(metadata["attempts"]), 2)
            self.assertEqual(metadata["attempts"][0]["result_json"], initial_result_json)
            self.assertEqual(executed_profiles, ["sde0_hs0"])
            self.assertEqual(merged_sources, [recovery_lhco, source_lhco])
            with open(config["base_mg5_config"]["result_json"], encoding="utf-8") as handle:
                canonical = json.load(handle)
            self.assertEqual(canonical["result_kind"], "event_count_recovery_summary")
            self.assertEqual(canonical["outputs"][0]["loaded_lhco_event_count"], 11)
            with open(canonical["outputs"][0]["banner_path"], encoding="utf-8") as handle:
                self.assertIn("not an original MG5 banner", handle.read())

            zero_config = dict(config)
            zero_config["metadata_path"] = os.path.join(root, "zero.json")
            zero_config.pop("initial_result_json")

            def fake_zero(_cfg):
                return {
                    "outputs": [{
                        "label": "np_o_1",
                        "lhco_path": source_lhco,
                        "banner_path": source_banner,
                        "loaded_lhco_event_count": 0,
                        "count_record": {"status": "zero_events"},
                    }]
                }

            with patch.object(recover_module, "run_from_config", side_effect=fake_zero):
                zero_metadata = recover_module.recover_lhco_count(zero_config)
            self.assertEqual(zero_metadata["status"], "zero_event_failure")
            self.assertIn("zero_event_failure", zero_metadata)

    def test_recovery_units_update_one_phase_file_without_overwriting(self):
        with tempfile.TemporaryDirectory() as root:
            source_lhco = os.path.join(root, "source.lhco")
            source_banner = os.path.join(root, "banner.txt")
            write_text(source_lhco, "event\n")
            write_text(source_banner, "Integrated weight (pb) : 1.0\n")
            metadata_path = os.path.join(root, "event_count_recovery.json")

            def fake_run(cfg):
                return {"outputs": [{
                    "label": cfg["output_label"],
                    "lhco_path": source_lhco,
                    "banner_path": source_banner,
                    "loaded_lhco_event_count": 10,
                }]}

            def fake_merge(_sources, output_lhco, **kwargs):
                write_text(output_lhco, "merged\n")
                write_text(kwargs["metadata_path"], "{}\n")
                return {
                    "merged_loaded_lhco_event_count": 10,
                    "merged_cross_section_pb": 1.0,
                    "source_banners_retained": kwargs["source_banner_paths"],
                }

            with patch.object(recover_module, "run_from_config", side_effect=fake_run), patch.object(
                recover_module, "merge_lhco", side_effect=fake_merge
            ):
                for unit in ("sm", "np_o_1"):
                    recover_module.recover_lhco_count({
                        "base_mg5_config": {
                            "process_mode": "pure_sm" if unit == "sm" else "pure_np",
                            "operator": "o_1",
                            "output_label": unit,
                        },
                        "requested_event_count": 100,
                        "recovery_profiles": ["default"],
                        "attempt_root": os.path.join(root, "attempts", unit),
                        "merged_output_dir": os.path.join(root, "merged", unit),
                        "metadata_path": metadata_path,
                        "recovery_unit": unit,
                        "required_units": ["sm", "np_o_1"],
                    })

            with open(metadata_path, encoding="utf-8") as handle:
                aggregate = json.load(handle)
            self.assertEqual(aggregate["status"], "accepted")
            self.assertEqual(set(aggregate["units"]), {"sm", "np_o_1"})
            self.assertEqual(aggregate["missing_units"], [])


if __name__ == "__main__":
    unittest.main()

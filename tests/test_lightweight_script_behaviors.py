import json
import os
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

from scripts.beam_energy import compute_sqrt_s
from scripts.count_lhco_events import count_lhco_events
from scripts.double_check_zero_cross_section import double_check_zero_cross_section
from scripts.durable_exec import job_paths, remote_start_command, remote_status_command, safe_name
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
from scripts.run_mg5 import run_mg5
from scripts.run_mg5_config import _beam_lines, _coefficient_lines, _labels_for_runs, _process_order_lines, validate_config
from scripts.setup_delphes_card import setup_delphes_card
from scripts.timing_tracker import TimingTracker


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
        status_command = remote_status_command(paths, "phase_6")
        self.assertIn('"status":"running"', status_command)
        self.assertIn('"status":"completed"', status_command)

        tracker = TimingTracker()
        with patch("scripts.timing_tracker.print"):
            tracker.start_phase("Phase 3: Validation")
            tracker.record_mg5_step("madgraph", 1.0, 2.5)
            tracker.end_phase("Phase 3: Validation")
        data = tracker.to_dict()
        self.assertEqual(data["phases"]["Phase 3: Validation"]["status"], "done")
        self.assertEqual(data["mg5_steps"]["Phase 3: Validation"]["madgraph"]["duration_sec"], 1.5)

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
            config = {
                "base_mg5_config": {
                    "process_mode": "pure_np",
                    "operator": "o_1",
                    "process_folder": os.path.join(root, "proc"),
                },
                "requested_event_count": 100,
                "recovery_profiles": ["default", "sde0_hs0"],
                "attempt_root": os.path.join(root, "attempts"),
                "merged_output_dir": os.path.join(root, "merged"),
                "metadata_path": os.path.join(root, "metadata.json"),
            }

            def fake_run(cfg):
                count = 3 if cfg["survey_profile"] == "default" else 8
                return {
                    "outputs": [{
                        "label": "np_o_1",
                        "lhco_path": source_lhco,
                        "banner_path": source_banner,
                        "loaded_lhco_event_count": count,
                    }]
                }

            def fake_merge(sources, output_lhco, **kwargs):
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

            zero_config = dict(config)
            zero_config["metadata_path"] = os.path.join(root, "zero.json")

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


if __name__ == "__main__":
    unittest.main()

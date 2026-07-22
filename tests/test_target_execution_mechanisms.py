import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import remote_exec
from scripts import sync_from_target
from scripts import sync_to_target


class TargetExecutionMechanismTests(unittest.TestCase):
    def test_remote_exec_quotes_cwd_and_arguments_for_wsl(self):
        calls = []

        def fake_run(args):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0)

        with patch("scripts.remote_exec.shutil.which", return_value="wsl.exe"):
            with patch("scripts.remote_exec.subprocess.run", side_effect=fake_run):
                rc = remote_exec.run_wsl(
                    "Ubuntu-22.04",
                    remote_exec._shell_join(["python", "script with space.py", "--flag", "a b"]),
                    "/home/user/work dir",
                )
        self.assertEqual(rc, 0)
        self.assertEqual(calls[0][:3], ["wsl.exe", "-d", "Ubuntu-22.04"])
        self.assertEqual(calls[0][3:6], ["--", "bash", "-lc"])
        command = calls[0][6]
        self.assertIn("cd '/home/user/work dir' &&", command)
        self.assertIn("'script with space.py'", command)
        self.assertIn("'a b'", command)

    def test_remote_exec_builds_ssh_command_with_port_and_cwd(self):
        calls = []

        def fake_run(args):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0)

        with patch("scripts.remote_exec.subprocess.run", side_effect=fake_run):
            rc = remote_exec.run_ssh("user@example", 2222, "python job.py", "/tmp/run")
        self.assertEqual(rc, 0)
        self.assertEqual(calls[0], ["ssh", "-p", "2222", "user@example", "cd /tmp/run && python job.py"])

    def test_sync_to_target_rejects_relative_target_and_builds_extract_command(self):
        with self.assertRaises(ValueError):
            sync_to_target.ensure_abs_target("relative/path")
        command = sync_to_target.extract_tar_command("/tmp/final name", "source dir")
        self.assertIn("mkdir -p /tmp", command)
        self.assertIn("tar -xf - -C /tmp", command)
        self.assertIn("mv -T /tmp/'source dir' /tmp/'final name'", command)

    def test_sync_from_target_rejects_relative_source_and_builds_tar_command(self):
        with self.assertRaises(ValueError):
            sync_from_target.tar_command("relative/path")
        command, name = sync_from_target.tar_command("/tmp/source dir")
        self.assertEqual(name, "source dir")
        self.assertIn("test -e '/tmp/source dir'", command)
        self.assertIn("tar -C /tmp -cf - 'source dir'", command)

    def test_sync_wsl_invocation_uses_distro_and_streaming_tar(self):
        calls = []

        def fake_run(args, stdin=None, check=False):
            calls.append((args, stdin is not None, check))
            return subprocess.CompletedProcess(args, 0)

        with patch("scripts.sync_to_target.shutil.which", return_value="wsl.exe"):
            with patch("scripts.sync_to_target.make_tar") as make_tar:
                with patch("scripts.sync_to_target.run_checked", side_effect=fake_run):
                    class FakeTar:
                        def __init__(self):
                            self.name = "payload.tar"

                        def unlink(self, missing_ok=False):
                            return None

                        def __fspath__(self):
                            return __file__

                    make_tar.return_value = FakeTar()
                    sync_to_target.copy_wsl(Path(__file__), "/tmp/target.py", "Ubuntu-22.04")
        self.assertEqual(calls[0][0][:3], ["wsl.exe", "-d", "Ubuntu-22.04"])
        self.assertEqual(calls[0][0][3:6], ["--", "bash", "-lc"])
        self.assertTrue(calls[0][1])


if __name__ == "__main__":
    unittest.main()

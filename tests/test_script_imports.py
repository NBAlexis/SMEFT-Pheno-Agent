import importlib
import pkgutil
import subprocess
import sys
import unittest
from pathlib import Path

import scripts


ROOT = Path(__file__).resolve().parents[1]


class ScriptImportTests(unittest.TestCase):
    def test_every_bundled_script_is_importable_as_a_package_module(self):
        modules = [item.name for item in pkgutil.iter_modules(scripts.__path__)]
        for name in modules:
            with self.subTest(module=name):
                importlib.import_module(f"scripts.{name}")

    def test_argparse_scripts_have_fast_help(self):
        for script_path in sorted((ROOT / "scripts").glob("*.py")):
            text = script_path.read_text(encoding="utf-8", errors="replace")
            if "argparse.ArgumentParser" not in text:
                continue
            with self.subTest(script=script_path.name):
                result = subprocess.run(
                    [sys.executable, str(script_path), "--help"],
                    cwd=str(ROOT),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False,
                    timeout=5,
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    result.stderr or result.stdout,
                )
                self.assertIn("usage", result.stdout.lower())


if __name__ == "__main__":
    unittest.main()

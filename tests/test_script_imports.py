import importlib
import pkgutil
import unittest

import scripts


class ScriptImportTests(unittest.TestCase):
    def test_every_bundled_script_is_importable_as_a_package_module(self):
        modules = [item.name for item in pkgutil.iter_modules(scripts.__path__)]
        for name in modules:
            with self.subTest(module=name):
                importlib.import_module(f"scripts.{name}")


if __name__ == "__main__":
    unittest.main()

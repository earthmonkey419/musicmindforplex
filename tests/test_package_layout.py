"""Checks for module paths used by the web command dispatcher."""

import ast
import importlib.util
import unittest
from pathlib import Path

from musicmind.commands import MODULES
from musicmind.paths import FPCALC, PROJECT_ROOT


class PackageLayoutTests(unittest.TestCase):
    def test_registered_commands_are_importable_modules(self):
        for name, module in MODULES.items():
            with self.subTest(command=name):
                self.assertIsNotNone(importlib.util.find_spec(module))

    def test_web_command_references_are_registered(self):
        tree = ast.parse((PROJECT_ROOT / "web" / "app.py").read_text())
        references = {
            node.slice.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Subscript)
            and isinstance(node.value, ast.Name)
            and node.value.id == "MODULES"
            and isinstance(node.slice, ast.Constant)
            and isinstance(node.slice.value, str)
        }
        self.assertTrue(references)
        self.assertFalse(references - MODULES.keys())

    def test_shared_assets_resolve_from_repository_root(self):
        self.assertEqual(PROJECT_ROOT / "bin" / "fpcalc", FPCALC)
        self.assertTrue(FPCALC.is_file())
        self.assertTrue((PROJECT_ROOT / "config.example.py").is_file())


if __name__ == "__main__":
    unittest.main()

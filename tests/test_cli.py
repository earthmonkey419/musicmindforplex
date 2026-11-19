"""Regression tests for the installed CLI and pre-reorganization commands."""

import contextlib
import importlib
import io
import os
import sqlite3
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

from musicmind_cli import cli


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_db_init_creates_schema_without_importing_plex(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            database = Path(temp_dir) / "musicmind.db"
            config = types.ModuleType("config")
            config.DB_PATH = str(database)

            old_path = list(sys.path)
            output = io.StringIO()
            try:
                with patch.dict(sys.modules, {"config": config, "plexapi": None}):
                    with contextlib.redirect_stdout(output):
                        cli.main(["db", "init"])
                        cli.main(["db", "init"])
            finally:
                sys.path[:] = old_path

            self.assertTrue(database.is_file())
            self.assertIn("Database ready", output.getvalue())
            with contextlib.closing(sqlite3.connect(database)) as conn:
                tables = {
                    row[0]
                    for row in conn.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                }
            self.assertTrue(
                {"tracks", "track_tags", "artist_meta", "track_audio_features", "query_log"}
                <= tables
            )

    def test_legacy_auth_script_name_imports_the_relocated_module(self):
        legacy = importlib.import_module("auth")
        current = importlib.import_module("musicmind.plex.auth")
        self.assertIs(legacy, current)

    def test_installed_paths_use_the_user_config_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_root = Path(temp_dir)
            (config_root / "config.py").write_text(
                f"BASE_DIR = {str(config_root)!r}\n", encoding="utf-8"
            )
            env = os.environ.copy()
            env["PYTHONPATH"] = str(PROJECT_ROOT)
            result = subprocess.run(
                [
                    sys.executable,
                    "-c",
                    "from musicmind.paths import PROJECT_ROOT, FPCALC, MODELS_DIR; "
                    "assert PROJECT_ROOT == __import__('pathlib').Path.cwd(); "
                    "assert FPCALC == PROJECT_ROOT / 'bin' / 'fpcalc'; "
                    "assert MODELS_DIR == PROJECT_ROOT / 'models'",
                ],
                cwd=config_root,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)



if __name__ == "__main__":
    unittest.main()

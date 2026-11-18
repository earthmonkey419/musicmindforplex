"""Paths shared by package modules and command entry points."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FPCALC = PROJECT_ROOT / "bin" / "fpcalc"
MODELS_DIR = PROJECT_ROOT / "models"

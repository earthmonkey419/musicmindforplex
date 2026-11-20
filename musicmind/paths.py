"""Shared paths rooted at the active MusicMind configuration directory."""

from pathlib import Path

try:
    from config import BASE_DIR as _CONFIG_ROOT
except (ImportError, AttributeError):
    _CONFIG_ROOT = None

PROJECT_ROOT = (
    Path(_CONFIG_ROOT).expanduser().resolve()
    if _CONFIG_ROOT
    else Path(__file__).resolve().parent.parent
)
FPCALC = PROJECT_ROOT / "bin" / "fpcalc"
MODELS_DIR = PROJECT_ROOT / "models"

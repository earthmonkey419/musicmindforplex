"""Backward-compatible entry point for :mod:`musicmind.config_check`."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("musicmind.config_check", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("musicmind.config_check")

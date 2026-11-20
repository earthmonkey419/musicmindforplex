"""Backward-compatible entry point for :mod:`musicmind.view_logs`."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("musicmind.view_logs", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("musicmind.view_logs")

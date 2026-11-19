"""Backward-compatible entry point for :mod:`musicmind.ingest`."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("musicmind.ingest", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("musicmind.ingest")

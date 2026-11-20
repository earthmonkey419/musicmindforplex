"""Backward-compatible entry point for :mod:`musicmind.enrichment.resolve_recording_mbids`."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("musicmind.enrichment.resolve_recording_mbids", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("musicmind.enrichment.resolve_recording_mbids")

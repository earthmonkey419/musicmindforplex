"""Backward-compatible entry point for :mod:`musicmind.enrichment.restore_real_artist_from_va_results`."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("musicmind.enrichment.restore_real_artist_from_va_results", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("musicmind.enrichment.restore_real_artist_from_va_results")

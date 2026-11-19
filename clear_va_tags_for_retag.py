"""Backward-compatible entry point for :mod:`musicmind.enrichment.clear_va_tags_for_retag`."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("musicmind.enrichment.clear_va_tags_for_retag", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("musicmind.enrichment.clear_va_tags_for_retag")

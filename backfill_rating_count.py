"""Backward-compatible entry point for :mod:`musicmind.db.backfill_rating_count`."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("musicmind.db.backfill_rating_count", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("musicmind.db.backfill_rating_count")

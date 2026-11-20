"""Backward-compatible entry point for :mod:`musicmind.db.fix_track_number_artist_prefix`."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("musicmind.db.fix_track_number_artist_prefix", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("musicmind.db.fix_track_number_artist_prefix")

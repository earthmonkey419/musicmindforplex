"""Backward-compatible entry point for :mod:`musicmind.plex.tag_tracks`."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("musicmind.plex.tag_tracks", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("musicmind.plex.tag_tracks")

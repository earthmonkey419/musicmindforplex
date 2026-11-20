"""Backward-compatible entry point for :mod:`musicmind.migrations.migrate_v2_to_v3`."""

if __name__ == "__main__":
    from runpy import run_module

    run_module("musicmind.migrations.migrate_v2_to_v3", run_name="__main__")
else:
    import importlib
    import sys

    sys.modules[__name__] = importlib.import_module("musicmind.migrations.migrate_v2_to_v3")

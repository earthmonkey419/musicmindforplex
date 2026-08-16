"""
Shared config validation. Import and call check_config(...) with the
names of the values a script actually needs, right after importing
them from config.py. Exits with one friendly message instead of
letting an unedited config.py cause a wall of raw tracebacks.
"""

import os

PLACEHOLDERS = {
    "PLEX_URL":   "YOUR_NAS_IP",
    "PLEX_TOKEN": "YOUR_PLEX_TOKEN",
    "OPENAI_KEY": "YOUR_OPENAI_API_KEY",
}

# The database filename every install used before the v3 rebrand.
# If a fresh v3 install ever finds this sitting next to a *missing*
# musicmind.db, that almost always means an existing v2 database is
# about to get silently orphaned by a brand-new empty one -- not a
# fresh install, an unmigrated upgrade.
OLD_DB_NAME = "plex_music_brain.db"
NEW_DB_NAME = "musicmind.db"


def _check_for_unmigrated_db():
    """Refuses to let a script silently create a fresh musicmind.db
    when an unmigrated v2 database is sitting right there. Real
    installs only ever hit this if config.py's DB_PATH says
    musicmind.db but that file doesn't exist yet, AND the old v2
    filename does -- exactly the state migrate_v2_to_v3.py exists
    to fix. A normal fresh install never has plex_music_brain.db
    sitting around at all, so this never fires for it."""
    try:
        from config import DB_PATH, BASE_DIR
    except ImportError:
        return  # config.py doesn't even define these; not our problem here

    if os.path.basename(DB_PATH) != NEW_DB_NAME:
        return  # this install already uses a custom/non-default DB_PATH
    if os.path.exists(DB_PATH):
        return  # already migrated (or already has a real musicmind.db)

    old_db_path = os.path.join(BASE_DIR, OLD_DB_NAME)
    if os.path.exists(old_db_path):
        print("=" * 60)
        print("Unmigrated v2 database found.")
        print("=" * 60)
        print(f"config.py points at {NEW_DB_NAME}, but that file doesn't")
        print(f"exist yet -- and {OLD_DB_NAME} does, right next to it.")
        print()
        print("This looks like an upgrade from v2, not a fresh install.")
        print("Continuing would create a new, empty database and make")
        print("your real library data (tags, listening history,")
        print("enrichment) look like it's gone -- it isn't, it just")
        print("hasn't been migrated to the new filename yet.")
        print()
        print("Run this first:")
        print("    python3.12 migrate_v2_to_v3.py")
        print("=" * 60)
        raise SystemExit(1)


def check_config(**values):
    """
    Usage: check_config(PLEX_URL=PLEX_URL, PLEX_TOKEN=PLEX_TOKEN)
    Checks each named value against its known placeholder and against
    being blank. Exits with a single clear message if anything's unset.
    """
    _check_for_unmigrated_db()

    missing = []
    for name, value in values.items():
        placeholder = PLACEHOLDERS.get(name)
        if not value or (placeholder and placeholder.lower() in str(value).lower()):
            missing.append(name)
    if missing:
        print("=" * 60)
        print("Configuration not set up yet.")
        print("=" * 60)
        print(f"Missing or still-default: {', '.join(missing)}")
        print()
        print("Edit config.py and fill these in before running this script.")
        print("(If you haven't yet: cp config.example.py config.py)")
        print("See the README for where to get your Plex token and")
        print("OpenAI API key.")
        print("=" * 60)
        raise SystemExit(1)

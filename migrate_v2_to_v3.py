#!/usr/bin/env python3
"""
MusicMind v2 -> v3 database migration.

v3 renamed the default database filename from `plex_music_brain.db`
to `musicmind.db` (matching the app's own rebrand). Existing v2
installs have their own `config.py` (gitignored, never touched by
`git pull`) still pointing at the old filename -- this script brings
an existing install's real database file and config.py in line with
the new convention.

Safe to run more than once: if DB_PATH already resolves to a file
that exists, this exits immediately with no changes made.

Usage:
    python3.12 migrate_v2_to_v3.py           # do the migration
    python3.12 migrate_v2_to_v3.py --dry-run # show what would happen, change nothing
"""

import os
import re
import shutil
import sys
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.py")
NEW_DB_NAME = "musicmind.db"


def fail(msg):
    print(f"\n❌ {msg}")
    sys.exit(1)


def read_current_db_path():
    """Reads the real, current DB_PATH out of config.py without
    importing it (avoids side effects from any other top-level code
    config.py might have)."""
    if not os.path.exists(CONFIG_PATH):
        fail(f"No config.py found at {CONFIG_PATH}. Nothing to migrate.")

    with open(CONFIG_PATH) as f:
        content = f.read()

    match = re.search(r'^DB_PATH\s*=\s*(.+)$', content, re.MULTILINE)
    if not match:
        fail("Could not find a DB_PATH line in config.py. "
             "This doesn't look like a standard install -- stopping "
             "rather than guessing.")

    # DB_PATH is normally os.path.join(BASE_DIR, "something.db").
    # Extract just the filename portion so we don't have to eval
    # arbitrary code from config.py.
    filename_match = re.search(r'["\']([^"\']+\.db)["\']', match.group(1))
    if not filename_match:
        fail(f"Found DB_PATH but couldn't parse a .db filename from it: "
             f"{match.group(1).strip()!r}. Stopping rather than guessing.")

    return content, match.group(0), filename_match.group(1)


def main():
    dry_run = "--dry-run" in sys.argv

    print("MusicMind v2 -> v3 Database Migration")
    print("=" * 40)
    if dry_run:
        print("(dry run -- no changes will be made)\n")

    content, db_path_line, current_db_name = read_current_db_path()
    current_db_path = os.path.join(BASE_DIR, current_db_name)
    new_db_path = os.path.join(BASE_DIR, NEW_DB_NAME)

    print(f"Current DB_PATH filename: {current_db_name}")
    print(f"Target DB_PATH filename:  {NEW_DB_NAME}")

    # --- Idempotency check ---
    if current_db_name == NEW_DB_NAME:
        print("\n✅ Already migrated -- config.py already points at "
              f"{NEW_DB_NAME}. Nothing to do.")
        return

    if os.path.exists(new_db_path):
        fail(f"{NEW_DB_NAME} already exists at {new_db_path}, but "
             f"config.py still points at {current_db_name}. This is an "
             f"unexpected state -- stopping rather than guessing which "
             f"file is the real one. Check both files manually before "
             f"re-running.")

    if not os.path.exists(current_db_path):
        fail(f"config.py points at {current_db_name}, but that file "
             f"doesn't exist at {current_db_path}. Nothing to migrate "
             f"-- check DB_PATH in config.py is correct.")

    # --- Sanity check: does this look like a real MusicMind DB? ---
    try:
        conn = sqlite3.connect(current_db_path, timeout=10)
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        conn.close()
    except sqlite3.Error as e:
        fail(f"Could not open {current_db_path} as a SQLite database: {e}")

    if "tracks" not in tables:
        fail(f"{current_db_path} doesn't have a 'tracks' table -- this "
             f"doesn't look like a real MusicMind database. Stopping "
             f"rather than renaming something that might not be ours.")

    print(f"\nFound valid database with {len(tables)} tables at "
          f"{current_db_path}.")

    if dry_run:
        print(f"\nWould rename:")
        print(f"  {current_db_path} -> {new_db_path}")
        for suffix in ("-wal", "-shm"):
            side = current_db_path + suffix
            if os.path.exists(side):
                print(f"  {side} -> {new_db_path + suffix}")
        print(f"\nWould update config.py's DB_PATH to point at "
              f"{NEW_DB_NAME}, after backing it up.")
        print("\n(dry run complete -- nothing was changed)")
        return

    # --- Back up config.py before touching anything ---
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    config_backup = f"{CONFIG_PATH}.pre-v3-migration-{timestamp}.bak"
    shutil.copy(CONFIG_PATH, config_backup)
    print(f"\nBacked up config.py -> {config_backup}")

    # --- Rename the DB file and its WAL/SHM companions if present ---
    os.rename(current_db_path, new_db_path)
    print(f"Renamed {current_db_name} -> {NEW_DB_NAME}")

    for suffix in ("-wal", "-shm"):
        old_side = current_db_path + suffix
        new_side = new_db_path + suffix
        if os.path.exists(old_side):
            os.rename(old_side, new_side)
            print(f"Renamed {current_db_name}{suffix} -> {NEW_DB_NAME}{suffix}")

    # --- Update config.py's DB_PATH line ---
    assert content.count(db_path_line) == 1, (
        "DB_PATH line pattern matched more than once in config.py -- "
        "refusing to guess which one to replace. Database file has "
        "already been renamed above; update config.py's DB_PATH "
        "manually to finish."
    )
    new_db_path_line = f'DB_PATH = os.path.join(BASE_DIR, "{NEW_DB_NAME}")'
    new_content = content.replace(db_path_line, new_db_path_line)

    with open(CONFIG_PATH, "w") as f:
        f.write(new_content)
    print(f"Updated config.py: DB_PATH now points at {NEW_DB_NAME}")

    # --- Verify ---
    import py_compile
    try:
        py_compile.compile(CONFIG_PATH, doraise=True)
    except py_compile.PyCompileError as e:
        fail(f"config.py failed to compile after the edit: {e}\n"
             f"Restore from backup: cp {config_backup} {CONFIG_PATH}")

    print("\n✅ Migration complete.")
    print(f"   Database:  {new_db_path}")
    print(f"   config.py: {CONFIG_PATH} (backup at {config_backup})")
    print("\nRestart the app (pm2 restart plex-music-brain, or your "
          "equivalent) to pick up the change.")


if __name__ == "__main__":
    main()

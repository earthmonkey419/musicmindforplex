#!/usr/bin/env python3.12
"""
restore_real_artist_from_va_results.py

Restores tracks.real_artist from va_results.chosen_artist for tracks that
were previously resolved (HIGH confidence, real chosen_artist) but have
since regressed to an empty real_artist — the same failure shape as the
2026-09-06 is_instrumental mass-reset (a re-ingest upsert that didn't
carry forward previously-computed columns).

Safe to re-run: only touches rows where real_artist IS NULL OR ''.
Only restores HIGH-confidence va_results rows with a non-empty
chosen_artist (REVIEW/no-match rows are intentionally left alone).

Usage:
    python3.12 restore_real_artist_from_va_results.py --test   # dry run, no writes
    python3.12 restore_real_artist_from_va_results.py --run    # actually writes
"""

import sqlite3
import shutil
import sys
import argparse
from datetime import datetime

DB_PATH = "/volume1/homes/earthmonkey/plex_music_brain/musicmind.db"


def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--test", action="store_true", help="Preview only, no writes")
    mode.add_argument("--run", action="store_true", help="Actually write changes")
    args = parser.parse_args()

    dry_run = args.test

    if not dry_run:
        backup_path = f"{DB_PATH}.bak-real_artist"
        print(f"Backing up DB to {backup_path} ...")
        shutil.copy(DB_PATH, backup_path)
        print("Backup complete.")

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")
    cur = conn.cursor()

    # Candidates: HIGH confidence, real chosen_artist, tracks row still empty
    cur.execute(
        """
        SELECT t.rating_key, t.title, v.chosen_artist, v.analyzed_at
        FROM va_results v
        JOIN tracks t ON t.rating_key = v.rating_key
        WHERE v.confidence = 'HIGH'
          AND v.chosen_artist IS NOT NULL
          AND v.chosen_artist != ''
          AND (t.real_artist IS NULL OR t.real_artist = '')
        """
    )
    candidates = cur.fetchall()

    print(f"Found {len(candidates)} regressed rows to restore.")

    if dry_run:
        print("\n--- DRY RUN: first 20 rows that would be restored ---")
        for rating_key, title, chosen_artist, analyzed_at in candidates[:20]:
            print(f"  {rating_key} | {title!r} -> real_artist = {chosen_artist!r} (resolved {analyzed_at})")
        if len(candidates) > 20:
            print(f"  ... and {len(candidates) - 20} more")
        print("\nNo changes written. Re-run with --run to apply.")
        conn.close()
        return

    updated = 0
    skipped = 0
    for rating_key, title, chosen_artist, analyzed_at in candidates:
        cur.execute(
            """
            UPDATE tracks
            SET real_artist = ?
            WHERE rating_key = ?
              AND (real_artist IS NULL OR real_artist = '')
            """,
            (chosen_artist, rating_key),
        )
        if cur.rowcount > 0:
            updated += 1
        else:
            skipped += 1
        conn.commit()

    conn.close()

    print(f"\nDone at {datetime.now().isoformat(timespec='seconds')}")
    print(f"  Matched in va_results: {len(candidates)}")
    print(f"  Actually updated:      {updated}")
    print(f"  Skipped (already set): {skipped}")


if __name__ == "__main__":
    main()

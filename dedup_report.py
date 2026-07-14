#!/usr/bin/env python3.12
"""
MusicMind for Plex - Duplicate Detection via Acoustic Fingerprint

Read-only report. Two tracks sharing an identical Chromaprint
fingerprint are the same recording, regardless of filename, path,
bitrate, or metadata spelling differences — a measured answer to the
duplicates problem instead of fuzzy title/artist matching.

Requires fingerprint_tracks.py to have been run first (reads from
track_fingerprints; does not compute anything itself).

Usage:
    python3.12 dedup_report.py
"""
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH


def main():
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")

    total_fp = conn.execute(
        "SELECT COUNT(*) FROM track_fingerprints WHERE error IS NULL"
    ).fetchone()[0]

    dupe_groups = conn.execute("""
        SELECT fingerprint, COUNT(*) as cnt
        FROM track_fingerprints
        WHERE error IS NULL
        GROUP BY fingerprint
        HAVING COUNT(*) > 1
        ORDER BY cnt DESC
    """).fetchall()

    print("MusicMind for Plex - Duplicate Detection Report")
    print("=" * 50)
    print(f"Fingerprinted tracks: {total_fp}")
    print(f"Duplicate groups found: {len(dupe_groups)}\n")

    if not dupe_groups:
        print("No duplicates found among fingerprinted tracks.")
        conn.close()
        return

    total_dupe_tracks = 0
    total_wasted = 0

    for fingerprint, cnt in dupe_groups:
        rows = conn.execute("""
            SELECT tf.rating_key, t.title, t.artist, t.album, tf.fp_duration
            FROM track_fingerprints tf
            JOIN tracks t ON t.rating_key = tf.rating_key
            WHERE tf.fingerprint = ?
            ORDER BY t.title
        """, (fingerprint,)).fetchall()

        print(f"--- {cnt} copies (fingerprint {fingerprint[:20]}...) ---")
        for rk, title, artist, album, dur in rows:
            print(f"  [{rk}] {title} — {artist}  ({album})  {dur:.1f}s")
        print()

        total_dupe_tracks += cnt
        total_wasted += (cnt - 1)  # cnt-1 are the "extra" copies per group

    print("=" * 50)
    print(f"Total tracks involved in duplicates: {total_dupe_tracks}")
    print(f"Extra copies (cnt-1 per group): {total_wasted}")
    print("=" * 50)

    conn.close()


if __name__ == "__main__":
    main()

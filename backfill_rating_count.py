#!/usr/bin/env python3.12
"""
One-off backfill: populates rating_count for every existing track.

Why this exists: musicmind_ingest.py's incremental ingest only ever
touches tracks added to Plex since the last recorded ingest timestamp
— correct and efficient for its normal job, but it means adding a
NEW column (rating_count) to an already-ingested library never gets
backfilled by routine syncing. Every existing track was ingested long
before this column existed, so incremental ingest skips all of them
forever, and rating_count stays NULL indefinitely without this.

Safe to re-run — only ever UPDATEs rating_count for a rating_key
that already exists in tracks; never touches any other column, never
inserts new rows.

Usage:
    python3.12 backfill_rating_count.py
"""
import sys, os, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PLEX_URL, PLEX_TOKEN, MUSIC_LIB, DB_PATH


def main():
    from plexapi.server import PlexServer
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    music = plex.library.section(MUSIC_LIB)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout=60000")

    updated = 0
    checked = 0
    print("Walking library and backfilling rating_count...\n")

    for artist in music.searchArtists():
        for album in artist.albums():
            for track in album.tracks():
                checked += 1
                conn.execute(
                    "UPDATE tracks SET rating_count = ? WHERE rating_key = ?",
                    (track.ratingCount, str(track.ratingKey))
                )
                if track.ratingCount is not None:
                    updated += 1
                if checked % 1000 == 0:
                    conn.commit()
                    print(f"  {checked} checked, {updated} with real rating_count so far...")

    conn.commit()
    conn.close()
    print(f"\nDone. {checked} tracks checked, {updated} had a real rating_count value.")


if __name__ == "__main__":
    main()

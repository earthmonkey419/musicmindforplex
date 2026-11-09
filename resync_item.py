#!/usr/bin/env python3
"""
MusicMind for Plex - Targeted Resync
Re-pulls one artist/album's metadata from Plex into SQLite without a
full incremental or full-library ingest. For fixing a single corrected
album/track without waiting on the next scheduled sync.

Usage:
    python3.12 resync_item.py --artist "Some Artist" --album "Some Album" --test
    python3.12 resync_item.py --artist "Some Artist" --album "Some Album" --run
"""

import argparse
import sqlite3
from plexapi.server import PlexServer
from config import PLEX_URL, PLEX_TOKEN, MUSIC_LIB, DB_PATH
from config_check import check_config

check_config(PLEX_URL=PLEX_URL, PLEX_TOKEN=PLEX_TOKEN)


def resync(artist_name, album_name, run=False):
    server = PlexServer(PLEX_URL, PLEX_TOKEN)
    music = server.library.section(MUSIC_LIB)

    matches = music.search(artist_name, libtype="artist")
    if not matches:
        print(f"No artist found matching '{artist_name}'")
        return

    artist = matches[0]
    if len(matches) > 1:
        print(f"Multiple artists matched '{artist_name}', using: {artist.title}")

    try:
        album = artist.album(album_name)
    except Exception:
        print(f"No album '{album_name}' found under artist '{artist.title}'")
        return

    genre = None
    if artist.genres:
        genre = artist.genres[0].tag

    tracks = album.tracks()
    print(f"Found {len(tracks)} track(s) in '{artist.title} — {album.title}'")

    rows = []
    for track in tracks:
        last_played = track.lastViewedAt.isoformat() if track.lastViewedAt else None
        added_at = track.addedAt.isoformat() if track.addedAt else None
        updated_at = track.updatedAt.isoformat() if track.updatedAt else None

        row = (
            str(track.ratingKey),
            track.title,
            artist.title,
            album.title,
            genre,
            album.year,
            track.duration,
            track.viewCount or 0,
            last_played,
            track.userRating,
            added_at,
            updated_at,
        )
        rows.append(row)
        print(f"  [{track.ratingKey}] {track.title!r}  artist={artist.title!r}  album={album.title!r}  year={album.year}")

    if not run:
        print("\n--test mode: no changes written. Re-run with --run to apply.")
        return

    conn = sqlite3.connect(DB_PATH)
    conn.executemany("""
        INSERT OR REPLACE INTO tracks
            (rating_key, title, artist, album, genre, year,
             duration_ms, play_count, last_played, user_rating,
             added_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, rows)
    conn.commit()
    conn.close()
    print(f"\nUpdated {len(rows)} row(s) in {DB_PATH}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resync one artist/album's metadata from Plex")
    parser.add_argument("--artist", required=True)
    parser.add_argument("--album", required=True)
    parser.add_argument("--run", action="store_true", help="Actually write to the DB (default is dry run)")
    args = parser.parse_args()

    resync(args.artist, args.album, run=args.run)

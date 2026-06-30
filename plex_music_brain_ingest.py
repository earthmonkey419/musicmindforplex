#!/usr/bin/env python3
"""
MusicMind for Plex - Library Ingest
Pulls all tracks from Plex Music library and stores in SQLite.
Run nightly to keep the database fresh.
"""

import sqlite3
import os
from datetime import datetime
from plexapi.server import PlexServer
from config import PLEX_URL, PLEX_TOKEN, MUSIC_LIB, DB_PATH

MUSIC_LIBRARY = "Music"

def get_last_ingest(conn):
    try:
        row = conn.execute("SELECT value FROM meta WHERE key='last_ingest'").fetchone()
        return row[0] if row else None
    except:
        return None

def set_last_ingest(conn, ts):
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute("INSERT OR REPLACE INTO meta (key, value) VALUES ('last_ingest', ?)", (ts,))
    conn.commit()

def init_db(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            rating_key   TEXT PRIMARY KEY,
            title        TEXT,
            artist       TEXT,
            album        TEXT,
            genre        TEXT,
            year         INTEGER,
            duration_ms  INTEGER,
            play_count   INTEGER DEFAULT 0,
            last_played  TEXT,
            user_rating  REAL,
            added_at     TEXT,
            updated_at   TEXT
        )
    """)
    conn.commit()
    print(f"Database ready: {DB_PATH}\n")

def ingest(conn, plex):
    music = plex.library.section(MUSIC_LIBRARY)
    artists = music.searchArtists()
    last_ingest = get_last_ingest(conn)
    if last_ingest:
        print(f"Incremental ingest since {last_ingest}\n")
    else:
        print("No previous ingest found. Running full ingest.\n")
    total_artists = len(artists)
    print(f"Found {total_artists} artists. Starting ingest...\n")

    inserted = 0
    skipped = 0
    now = datetime.now().isoformat()

    for i, artist in enumerate(artists, 1):
        for album in artist.albums():
            for track in album.tracks():
                # Skip tracks with no title AND no artist
                if not track.title and not artist.title:
                    skipped += 1
                    continue

                # Incremental skip — only process tracks added since last ingest
                if last_ingest and track.addedAt:
                    if track.addedAt.isoformat() <= last_ingest:
                        skipped += 1
                        continue

                genre = None
                if artist.genres:
                    genre = artist.genres[0].tag

                last_played = None
                if track.lastViewedAt:
                    last_played = track.lastViewedAt.isoformat()

                added_at = None
                if track.addedAt:
                    added_at = track.addedAt.isoformat()

                conn.execute("""
                    INSERT OR REPLACE INTO tracks
                        (rating_key, title, artist, album, genre, year,
                         duration_ms, play_count, last_played, user_rating,
                         added_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
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
                    now
                ))
                inserted += 1

                if inserted % 500 == 0:
                    conn.commit()
                    print(f"  {inserted} tracks ingested... (artist {i}/{total_artists})")

    conn.commit()
    set_last_ingest(conn, now)
    print(f"\nDone. {inserted} tracks ingested, {skipped} skipped.")
    print(f"Database: {DB_PATH}")

def main():
    print("MusicMind for Plex - Library Ingest")
    print("=" * 40)
    print(f"Connecting to Plex...")
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    print(f"Connected to: {plex.friendlyName}\n")

    conn = sqlite3.connect(DB_PATH, timeout=30)
    init_db(conn)
    ingest(conn, plex)
    conn.close()

if __name__ == "__main__":
    main()

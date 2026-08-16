#!/usr/bin/env python3
"""
MusicMind for Plex - Write AI Genres to Plex
Snapshots current genres, then appends top AI tags to each track in Plex.
Run with --test first to preview, then --run to apply.
"""

import sqlite3
import sys
import time
from datetime import datetime
from plexapi.server import PlexServer
from config import DB_PATH, PLEX_URL, PLEX_TOKEN

TOP_TAGS   = 3

# Tags too generic to be useful as Plex genres
EXCLUDE_TAGS = {
    'music', 'rock', 'pop', 'song', 'audio', 'track', 'album', 'artist',
    'vocals', 'guitar', 'drums', 'bass', 'piano', 'instrumental', 'live',
    'remix', 'cover', 'acoustic', 'bands', 'vocal', 'classic', 'original',
    'alternative', 'indie', 'dance', 'electronic', 'hip-hop', 'jazz', 'soul',
    'funk', 'reggae', 'blues', 'folk', 'country', 'classical', 'rap'
}

def get_top_tags(conn, rating_key):
    rows = conn.execute("""
        SELECT tag FROM track_tags
        WHERE rating_key = ?
        ORDER BY rowid ASC
    """, (rating_key,)).fetchall()
    tags = []
    for row in rows:
        tag = row[0].strip().lower()
        if tag and tag not in EXCLUDE_TAGS and len(tags) < TOP_TAGS:
            tags.append(tag)
    return tags

def snapshot_genres(conn, plex):
    print("Snapshotting current Plex genres...")
    already = conn.execute("SELECT COUNT(*) FROM genre_snapshot").fetchone()[0]
    if already > 0:
        print(f"  Snapshot already exists ({already} records). Skipping.\n")
        return

    music   = plex.library.section("Music")
    artists = music.searchArtists()
    count   = 0
    now     = datetime.now().isoformat()

    for artist in artists:
        for album in artist.albums():
            for track in album.tracks():
                genres = [g.tag for g in track.genres]
                for genre in genres:
                    conn.execute("""
                        INSERT INTO genre_snapshot (rating_key, genre, snapped_at)
                        VALUES (?, ?, ?)
                    """, (str(track.ratingKey), genre, now))
                count += 1
                if count % 500 == 0:
                    conn.commit()
                    print(f"  {count} tracks snapshotted...")

    conn.commit()
    print(f"  Snapshot complete: {count} tracks.\n")

def test_mode(conn, plex):
    print("TEST MODE — previewing first 10 tracks\n")
    rows = conn.execute("""
        SELECT rating_key, title, artist FROM tracks
        WHERE genres_written = 0
          AND title IS NOT NULL
          AND artist IS NOT NULL
          AND artist != ''
        LIMIT 10
    """).fetchall()

    for rating_key, title, artist in rows:
        tags = get_top_tags(conn, rating_key)
        if not tags:
            print(f"  {artist} - {title}: no tags found")
            continue
        try:
            track = plex.fetchItem(int(rating_key))
            current = [g.tag for g in track.genres]
            print(f"  {artist} - {title}")
            print(f"    Current : {current}")
            print(f"    Adding  : {tags}")
        except Exception as e:
            print(f"  {artist} - {title}: error — {e}")

    print("\nRun with --run to apply to all tracks.")

def run_mode(conn, plex):
    rows = conn.execute("""
        SELECT rating_key, title, artist FROM tracks
        WHERE genres_written = 0
          AND title IS NOT NULL
          AND artist IS NOT NULL
          AND artist != ''
    """).fetchall()

    total   = len(rows)
    done    = 0
    skipped = 0
    now     = datetime.now().isoformat()

    print(f"Writing genres to {total} tracks...\n")

    for rating_key, title, artist in rows:
        tags = get_top_tags(conn, rating_key)
        if not tags:
            conn.execute("UPDATE tracks SET genres_written = 1 WHERE rating_key = ?", (rating_key,))
            skipped += 1
            done += 1
            continue

        try:
            track = plex.fetchItem(int(rating_key))
            for tag in tags:
                track.addGenre(tag)
            conn.execute("UPDATE tracks SET genres_written = 1 WHERE rating_key = ?", (rating_key,))
            done += 1
            if done % 100 == 0:
                conn.commit()
                print(f"  {done}/{total} tracks updated ({skipped} skipped)")
            time.sleep(0.05)
        except Exception as e:
            print(f"  Error on {artist} - {title}: {e}")
            done += 1

    conn.commit()
    print(f"\nDone. {done} tracks processed, {skipped} skipped (no tags).")

def revert_mode(conn, plex):
    print("REVERT MODE — restoring original genres from snapshot\n")
    rows = conn.execute("""
        SELECT DISTINCT rating_key FROM genre_snapshot
    """).fetchall()

    total = len(rows)
    done  = 0

    for (rating_key,) in rows:
        try:
            track = plex.fetchItem(int(rating_key))
            # Remove all current genres
            for g in track.genres:
                track.removeGenre(g.tag)
            # Restore snapshot genres
            original = [r[0] for r in conn.execute(
                "SELECT genre FROM genre_snapshot WHERE rating_key = ?", (rating_key,)
            ).fetchall()]
            for g in original:
                track.addGenre(g)
            conn.execute("UPDATE tracks SET genres_written = 0 WHERE rating_key = ?", (rating_key,))
            done += 1
            if done % 100 == 0:
                print(f"  {done}/{total} reverted")
            time.sleep(0.05)
        except Exception as e:
            print(f"  Error on {rating_key}: {e}")

    conn.commit()
    print(f"\nDone. {done} tracks reverted.")

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else '--test'

    print("MusicMind for Plex - Write AI Genres to Plex")
    print("=" * 50)
    print(f"Mode: {mode}\n")

    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS genre_snapshot (
            rating_key  TEXT,
            genre       TEXT,
            snapped_at  TEXT
        )
    """)
    conn.commit()
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)

    if mode == '--test':
        snapshot_genres(conn, plex)
        test_mode(conn, plex)
    elif mode == '--run':
        snapshot_genres(conn, plex)
        run_mode(conn, plex)
    elif mode == '--revert':
        revert_mode(conn, plex)
    else:
        print("Usage: write_genres_to_plex.py [--test|--run|--revert]")

    conn.close()

if __name__ == "__main__":
    main()

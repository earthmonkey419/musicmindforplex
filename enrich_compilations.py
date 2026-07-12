#!/usr/bin/env python3
"""
MusicMind for Plex - Compilation Track Enrichment
Reads TPE1 (track artist) from ID3 tags for Various Artists tracks
and stores real artist in tracks.real_artist field.
"""

import sqlite3
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.mp4 import MP4
from plexapi.server import PlexServer
from config import DB_PATH, PLEX_URL, PLEX_TOKEN

# --- Path translation (Plex host paths -> local paths) -----------------
# Needed when Plex runs on a different OS/machine than MusicMind
# (e.g. Plex on Windows + MusicMind in WSL or Docker). Configure
# PATH_MAP in config.py; longest prefix wins; backslashes converted.
try:
    from config import PATH_MAP
except ImportError:
    PATH_MAP = {}

def translate_path(p):
    if not p:
        return p
    for src in sorted(PATH_MAP, key=len, reverse=True):
        if p.startswith(src):
            p = PATH_MAP[src] + p[len(src):]
            break
    if "\\" in p:
        p = p.replace("\\", "/")
    return p


BATCH_SIZE = 100

def get_file_path(plex, rating_key):
    try:
        track = plex.fetchItem(int(rating_key))
        return translate_path(track.media[0].parts[0].file)
    except:
        return None

def read_real_artist(path):
    try:
        if path.endswith('.mp3'):
            tags = ID3(path)
            tpe1 = tags.get('TPE1')
            return str(tpe1) if tpe1 else None
        elif path.endswith('.flac'):
            tags = FLAC(path)
            artist = tags.get('artist')
            return artist[0] if artist else None
        elif path.endswith(('.m4a', '.mp4', '.aac')):
            tags = MP4(path)
            artist = tags.get('\xa9ART')
            return artist[0] if artist else None
    except Exception as e:
        return None
    return None

def main():
    print("MusicMind for Plex - Compilation Enrichment")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH, timeout=30)
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)

    # Get all compilation tracks not yet enriched
    rows = conn.execute("""
        SELECT rating_key, title, album
        FROM tracks
        WHERE (LOWER(artist) IN ('various artists', 'va', 'various', 'v/a')
           OR artist LIKE 'Various%')
          AND real_artist IS NULL
        ORDER BY album, title
    """).fetchall()

    total = len(rows)
    print(f"Compilation tracks to enrich: {total}\n")

    done = 0
    found = 0
    not_found = 0

    for rating_key, title, album in rows:
        path = get_file_path(plex, rating_key)
        if not path:
            not_found += 1
            done += 1
            continue

        real_artist = read_real_artist(path)

        if real_artist and real_artist.lower() not in ('various artists', 'va', 'various', 'v/a'):
            conn.execute(
                "UPDATE tracks SET real_artist = ? WHERE rating_key = ?",
                (real_artist, rating_key)
            )
            found += 1
        else:
            not_found += 1

        done += 1
        if done % BATCH_SIZE == 0:
            conn.commit()
            print(f"  {done}/{total} processed ({found} artists found)")

    conn.commit()
    print(f"\nDone. {done} tracks processed.")
    print(f"  Real artist found : {found}")
    print(f"  Not found         : {not_found}")

    # Show sample results
    print("\n=== Sample Results ===")
    for row in conn.execute("""
        SELECT title, album, real_artist
        FROM tracks
        WHERE real_artist IS NOT NULL
        LIMIT 15
    """):
        print(f"  {row[2]:25s}  {row[0]} / {row[1]}")

    conn.close()

if __name__ == "__main__":
    main()

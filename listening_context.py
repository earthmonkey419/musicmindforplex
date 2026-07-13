#!/usr/bin/env python3
"""
MusicMind for Plex - Listening Context Analysis
Builds context-aware playlists from Last.fm scrobble history:
  1. Your Afternoon  - what you play 1-5pm
  2. Weekend Flow    - what you play Saturday/Sunday
  3. Often Together  - tracks that appear in the same listening session
"""

import sqlite3
from datetime import datetime
from plexapi.server import PlexServer
from config import DB_PATH, PLEX_URL, PLEX_TOKEN
from config_check import check_config
check_config(PLEX_URL=PLEX_URL, PLEX_TOKEN=PLEX_TOKEN)

SESSION_GAP = 1800  # 30 minutes in seconds

def init_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS track_sessions (
            session_id  INTEGER,
            rating_key  TEXT,
            timestamp   INTEGER
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_sessions_rk
        ON track_sessions(rating_key)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS track_cooccurrence (
            rating_key_a  TEXT,
            rating_key_b  TEXT,
            count         INTEGER DEFAULT 1,
            PRIMARY KEY (rating_key_a, rating_key_b)
        )
    """)
    conn.commit()
    print("Tables ready.\n")

def build_sessions(conn):
    print("Building listening sessions...")
    conn.execute("DELETE FROM track_sessions")
    conn.execute("DELETE FROM track_cooccurrence")
    conn.commit()

    rows = conn.execute("""
        SELECT rating_key, timestamp
        FROM lastfm_scrobbles
        WHERE matched = 1
        ORDER BY timestamp ASC
    """).fetchall()

    session_id   = 0
    last_ts      = None
    sessions     = []
    current      = []

    for rating_key, ts in rows:
        if last_ts and (ts - last_ts) > SESSION_GAP:
            if current:
                sessions.append((session_id, current[:]))
            session_id += 1
            current = []
        current.append((rating_key, ts))
        last_ts = ts

    if current:
        sessions.append((session_id, current))

    print(f"Found {len(sessions)} listening sessions.\n")

    # Insert into track_sessions
    for sid, tracks in sessions:
        for rk, ts in tracks:
            conn.execute(
                "INSERT INTO track_sessions (session_id, rating_key, timestamp) VALUES (?,?,?)",
                (sid, rk, ts)
            )
    conn.commit()

    # Load album lookup
    album_lookup = dict(conn.execute("SELECT rating_key, album FROM tracks WHERE rating_key IS NOT NULL").fetchall())

    # Build co-occurrence counts
    print("Building co-occurrence matrix...")
    done = 0
    for sid, tracks in sessions:
        keys = list(set(rk for rk, ts in tracks))
        for i in range(len(keys)):
            for j in range(i+1, len(keys)):
                # Skip same-album pairs
                if album_lookup.get(keys[i]) and album_lookup.get(keys[i]) == album_lookup.get(keys[j]):
                    continue
                a, b = sorted([keys[i], keys[j]])
                conn.execute("""
                    INSERT INTO track_cooccurrence (rating_key_a, rating_key_b, count)
                    VALUES (?, ?, 1)
                    ON CONFLICT(rating_key_a, rating_key_b)
                    DO UPDATE SET count = count + 1
                """, (a, b))
        done += 1
        if done % 1000 == 0:
            conn.commit()
            print(f"  {done}/{len(sessions)} sessions processed")

    conn.commit()
    total_pairs = conn.execute("SELECT COUNT(*) FROM track_cooccurrence").fetchone()[0]
    print(f"Co-occurrence matrix built: {total_pairs} track pairs.\n")

def get_afternoon_tracks(conn, limit=30):
    return conn.execute("""
        SELECT t.rating_key, t.title, t.artist, COUNT(*) as afternoon_plays
        FROM lastfm_scrobbles s
        JOIN tracks t ON s.rating_key = t.rating_key
        WHERE CAST(strftime('%H', datetime(s.timestamp, 'unixepoch', 'localtime')) AS INTEGER) BETWEEN 13 AND 17
        GROUP BY s.rating_key
        ORDER BY afternoon_plays DESC
        LIMIT ?
    """, (limit,)).fetchall()

def get_weekend_tracks(conn, limit=30):
    return conn.execute("""
        SELECT t.rating_key, t.title, t.artist, COUNT(*) as weekend_plays
        FROM lastfm_scrobbles s
        JOIN tracks t ON s.rating_key = t.rating_key
        WHERE strftime('%w', datetime(s.timestamp, 'unixepoch', 'localtime')) IN ('0', '6')
        GROUP BY s.rating_key
        ORDER BY weekend_plays DESC
        LIMIT ?
    """, (limit,)).fetchall()

def get_often_together_tracks(conn, limit=30):
    # Find the most co-occurred pairs, then build a playlist
    # from the most connected tracks
    pairs = conn.execute("""
        SELECT rating_key_a, rating_key_b, count
        FROM track_cooccurrence
        ORDER BY count DESC
        LIMIT 200
    """).fetchall()

    # Score each track by total co-occurrence count
    scores = {}
    for a, b, count in pairs:
        scores[a] = scores.get(a, 0) + count
        scores[b] = scores.get(b, 0) + count

    top_keys = sorted(scores, key=scores.get, reverse=True)[:limit]

    results = []
    for rk in top_keys:
        row = conn.execute(
            "SELECT rating_key, title, artist FROM tracks WHERE rating_key = ?", (rk,)
        ).fetchone()
        if row:
            results.append(row)

    return results

def create_plex_playlist(name, rating_keys):
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    tracks = []
    for rk in rating_keys:
        try:
            tracks.append(plex.fetchItem(int(rk)))
        except Exception as e:
            print(f"  Warning: could not fetch {rk}: {e}")

    if not tracks:
        print(f"  No tracks fetched for '{name}'")
        return 0

    for pl in plex.playlists():
        if pl.title == name:
            pl.delete()

    plex.createPlaylist(name, items=tracks)
    return len(tracks)

def main():
    print("MusicMind for Plex - Listening Context Analysis")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH, timeout=30)
    init_tables(conn)
    build_sessions(conn)

    print("=" * 50)
    print("Generating context playlists...\n")

    # 1. Your Afternoon
    print("1. Your Afternoon (1-5pm)...")
    afternoon = get_afternoon_tracks(conn)
    for row in afternoon[:5]:
        print(f"   {row[3]}x  {row[2]} - {row[1]}")
    count = create_plex_playlist("🌞 Your Afternoon", [r[0] for r in afternoon])
    print(f"   → Created in Plex with {count} tracks\n")

    # 2. Weekend Flow
    print("2. Weekend Flow (Sat/Sun)...")
    weekend = get_weekend_tracks(conn)
    for row in weekend[:5]:
        print(f"   {row[3]}x  {row[2]} - {row[1]}")
    count = create_plex_playlist("🎉 Weekend Flow", [r[0] for r in weekend])
    print(f"   → Created in Plex with {count} tracks\n")

    # 3. Often Together
    print("3. Often Played Together...")
    together = get_often_together_tracks(conn)
    for row in together[:5]:
        print(f"   {row[2]} - {row[1]}")
    count = create_plex_playlist("🔗 Often Together", [r[0] for r in together])
    print(f"   → Created in Plex with {count} tracks\n")

    conn.close()
    print("Done. Check Plexamp for your new playlists.")

if __name__ == "__main__":
    main()

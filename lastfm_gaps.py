#!/usr/bin/env python3
"""
MusicMind for Plex - Last.fm Gap Analysis
Finds artists you scrobble heavily but don't have in Plex.
Categorizes them via OpenAI into actionable buckets.
"""

import sqlite3
import json
import time
from openai import OpenAI
from config import DB_PATH, OPENAI_KEY
from config_check import check_config
check_config(OPENAI_KEY=OPENAI_KEY)

MIN_SCROBBLES = 50
BATCH_SIZE    = 20

client = OpenAI(api_key=OPENAI_KEY)

def init_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS artist_gaps (
            artist          TEXT PRIMARY KEY,
            scrobbles       INTEGER,
            category        TEXT,
            categorized_at  TEXT
        )
    """)
    conn.commit()

def cleanup_acquired(conn):
    """Remove artists from gap list who are now in the library."""
    # Build set of all known artists from library (exact + real_artist)
    known = set()
    for row in conn.execute("""
        SELECT DISTINCT COALESCE(real_artist, artist) FROM tracks
        WHERE artist IS NOT NULL AND artist != ''
    """).fetchall():
        if row[0]:
            known.add(row[0].lower().strip())

    # Get all gap artists
    gaps = conn.execute("SELECT artist FROM artist_gaps").fetchall()
    deleted = 0
    for (gap_artist,) in gaps:
        ga = gap_artist.lower().strip()
        # Exact match OR gap artist is contained in a library artist OR vice versa
        match = any(
            ga == k or ga in k or k in ga
            for k in known
        )
        if match:
            conn.execute("DELETE FROM artist_gaps WHERE artist = ?", (gap_artist,))
            deleted += 1

    conn.commit()
    if deleted:
        print(f"Removed {deleted} artists now in library.\n")

def get_gap_artists(conn):
    return conn.execute("""
        SELECT 
            s.artist,
            COUNT(*) as scrobbles
        FROM lastfm_scrobbles s
        WHERE s.artist NOT IN (
            SELECT DISTINCT artist FROM tracks
            WHERE artist IS NOT NULL AND artist != ''
        )
        GROUP BY s.artist
        HAVING scrobbles >= ?
        ORDER BY scrobbles DESC
    """, (MIN_SCROBBLES,)).fetchall()

def get_uncategorized(conn, artists):
    existing = set(row[0] for row in conn.execute("SELECT artist FROM artist_gaps"))
    return [a for a in artists if a[0] not in existing]

def categorize_batch(batch):
    artist_list = "\n".join(f"{i+1}. {a[0]}" for i, a in enumerate(batch))
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[{
            "role": "user",
            "content": f"""Categorize each musician/artist/sound below into exactly one category:

- worth_acquiring: Real music artists worth adding to a personal music library (bands, singers, composers of popular/rock/jazz/world/folk/electronic music etc)
- classical: Classical composers or classical performers
- ambient_meditation: Ambient, sleep sounds, nature sounds, meditation, mantras, relaxation, white noise, yoga music
- unknown: Cannot determine what this is

Respond ONLY with a JSON array, one entry per artist in order.
Format: [{{"artist": "name", "category": "category"}}, ...]

Artists:
{artist_list}"""
        }]
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)

def run_categorization(conn, artists):
    uncategorized = get_uncategorized(conn, artists)
    total = len(uncategorized)

    if total == 0:
        print("All artists already categorized.")
        return

    print(f"Categorizing {total} artists in batches of {BATCH_SIZE}...\n")
    done = 0

    for i in range(0, total, BATCH_SIZE):
        batch = uncategorized[i:i+BATCH_SIZE]
        try:
            results = categorize_batch(batch)
            from datetime import datetime
            now = datetime.now().isoformat()
            for j, result in enumerate(results):
                if j >= len(batch):
                    break
                artist, scrobbles = batch[j]
                category = result.get('category', 'unknown')
                conn.execute("""
                    INSERT OR REPLACE INTO artist_gaps (artist, scrobbles, category, categorized_at)
                    VALUES (?, ?, ?, ?)
                """, (artist, scrobbles, category, now))
            conn.commit()
            done += len(batch)
            print(f"  {done}/{total} categorized")
            time.sleep(0.5)
        except Exception as e:
            print(f"  Batch failed: {e}")
            time.sleep(2)

def print_report(conn):
    print("\n" + "=" * 50)
    print("LAST.FM GAP REPORT")
    print("=" * 50)

    categories = [
        ('worth_acquiring',    '🎵 Worth Acquiring'),
        ('classical',          '🎼 Classical'),
        ('ambient_meditation', '🧘 Ambient / Meditation'),
        ('unknown',            '❓ Unknown'),
    ]

    for cat_key, cat_label in categories:
        rows = conn.execute("""
            SELECT artist, scrobbles FROM artist_gaps
            WHERE category = ?
            ORDER BY scrobbles DESC
        """, (cat_key,)).fetchall()

        if not rows:
            continue

        print(f"\n{cat_label} ({len(rows)} artists):")
        for artist, scrobbles in rows:
            print(f"  {scrobbles:5d}x  {artist}")

def main():
    print("MusicMind for Plex - Last.fm Gap Analysis")
    print("=" * 40)

    conn = sqlite3.connect(DB_PATH, timeout=30)
    init_table(conn)

    print(f"Finding artists with {MIN_SCROBBLES}+ scrobbles not in Plex...\n")
    cleanup_acquired(conn)
    artists = get_gap_artists(conn)
    print(f"Found {len(artists)} gap artists.\n")

    run_categorization(conn, artists)
    print_report(conn)
    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()

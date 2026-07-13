#!/usr/bin/env python3
"""
MusicMind for Plex - AI Track Tagger
Sends track metadata to OpenAI gpt-4o-mini and stores rich genre/mood tags.
"""

import sqlite3
import json
import time
from openai import OpenAI
from config import DB_PATH, OPENAI_KEY
from config_check import check_config
check_config(OPENAI_KEY=OPENAI_KEY)

BATCH_SIZE = 20

client = OpenAI(api_key=OPENAI_KEY)

def init_tags_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS track_tags (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            rating_key  TEXT NOT NULL,
            tag         TEXT NOT NULL,
            source      TEXT DEFAULT 'openai',
            created_at  TEXT DEFAULT (datetime('now')),
            UNIQUE(rating_key, tag)
        )
    """)
    conn.commit()

def get_untagged_tracks(conn):
    return conn.execute("""
        SELECT t.rating_key, t.title, t.artist, t.album, t.genre
        FROM tracks t
        LEFT JOIN track_tags tt ON t.rating_key = tt.rating_key
        WHERE tt.rating_key IS NULL
          AND (t.title IS NOT NULL OR t.artist IS NOT NULL)
        ORDER BY t.artist, t.album
    """).fetchall()

def build_prompt(batch):
    lines = []
    for i, (rating_key, title, artist, album, genre) in enumerate(batch, 1):
        lines.append(f"{i}. Artist: {artist} | Album: {album} | Track: {title} | Plex Genre: {genre or 'unknown'}")

    return f"""You are a music expert. For each track below, return 4-6 specific genre, subgenre, mood, or style tags.
Be specific — avoid broad tags like "Pop" or "Rock". Prefer tags like "psychedelic soul", "bossa nova", "lo-fi hip-hop", "post-punk", "balearic", "cosmic disco", "singer-songwriter 70s", etc.

Respond ONLY with a JSON array. Each element corresponds to the track at that position (1-based).
Format: [{{"tags": ["tag1", "tag2", "tag3"]}}, ...]

Tracks:
{chr(10).join(lines)}"""

def tag_batch(conn, batch):
    prompt = build_prompt(batch)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    raw = response.choices[0].message.content.strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    results = json.loads(raw)

    for i, (rating_key, title, artist, album, genre) in enumerate(batch):
        if i >= len(results):
            break
        tags = results[i].get("tags", [])
        for tag in tags:
            tag = tag.strip().lower()
            if tag:
                conn.execute("""
                    INSERT OR IGNORE INTO track_tags (rating_key, tag, source)
                    VALUES (?, ?, 'openai')
                """, (rating_key, tag))
    conn.commit()

def main():
    print("MusicMind for Plex - AI Track Tagger")
    print("=" * 40)

    conn = sqlite3.connect(DB_PATH, timeout=30)
    init_tags_table(conn)

    tracks = get_untagged_tracks(conn)
    total = len(tracks)
    print(f"Tracks to tag: {total}")

    if total == 0:
        print("All tracks already tagged!")
        conn.close()
        return

    tagged = 0
    batch_num = 0

    for i in range(0, total, BATCH_SIZE):
        batch = tracks[i:i + BATCH_SIZE]
        batch_num += 1

        try:
            tag_batch(conn, batch)
            tagged += len(batch)
            print(f"  Batch {batch_num}: {tagged}/{total} tracks tagged")
            time.sleep(0.5)  # Be polite to the API
        except Exception as e:
            print(f"  Batch {batch_num} failed: {e}")
            time.sleep(2)
            continue

    print(f"\nDone. {tagged} tracks tagged.")
    conn.close()

if __name__ == "__main__":
    main()

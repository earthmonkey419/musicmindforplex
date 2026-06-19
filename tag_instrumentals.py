#!/usr/bin/env python3
"""
Plex Music Brain - Instrumental Tagger
Uses OpenAI to determine if tracks are instrumental (no lead vocals).
Skips tracks already tagged via title heuristics.
"""

import sqlite3
import json
import time
from openai import OpenAI
from config import DB_PATH, OPENAI_KEY

BATCH_SIZE = 20
client = OpenAI(api_key=OPENAI_KEY)

def get_untagged_tracks(conn):
    return conn.execute("""
        SELECT rating_key, title, COALESCE(real_artist, artist) as artist, album
        FROM tracks
        WHERE is_instrumental IS NULL
          AND title IS NOT NULL
          AND artist IS NOT NULL
          AND artist != ''
          AND LOWER(artist) NOT IN ('various artists', 'va')
        ORDER BY artist, album
    """).fetchall()

def classify_batch(batch):
    lines = []
    for i, (rk, title, artist, album) in enumerate(batch, 1):
        lines.append(f"{i}. Artist: {artist} | Track: {title}")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.1,
        messages=[{
            "role": "user",
            "content": f"""For each track below, determine if it is instrumental (no lead vocals).

Answer based on your knowledge of the artist and track title.
- Pure instrumental = true
- Has lead vocals = false
- Unsure = null

Respond ONLY with a JSON array in order.
Format: [{{"instrumental": true}}, {{"instrumental": false}}, {{"instrumental": null}}, ...]

Tracks:
{chr(10).join(lines)}"""
        }]
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)

def main():
    print("Plex Music Brain - Instrumental Tagger")
    print("=" * 40)

    conn = sqlite3.connect(DB_PATH, timeout=30)
    tracks = get_untagged_tracks(conn)
    total = len(tracks)
    print(f"Tracks to classify: {total}\n")

    if total == 0:
        print("All tracks already classified!")
        conn.close()
        return

    done = 0
    instrumental = 0
    vocal = 0
    unknown = 0

    for i in range(0, total, BATCH_SIZE):
        batch = tracks[i:i+BATCH_SIZE]
        try:
            results = classify_batch(batch)
            for j, result in enumerate(results):
                if j >= len(batch):
                    break
                rating_key = batch[j][0]
                val = result.get('instrumental')
                if val is True:
                    conn.execute("UPDATE tracks SET is_instrumental = 1 WHERE rating_key = ?", (rating_key,))
                    instrumental += 1
                elif val is False:
                    conn.execute("UPDATE tracks SET is_instrumental = 0 WHERE rating_key = ?", (rating_key,))
                    vocal += 1
                else:
                    conn.execute("UPDATE tracks SET is_instrumental = NULL WHERE rating_key = ?", (rating_key,))
                    unknown += 1
            conn.commit()
            done += len(batch)
            if done % 500 == 0 or done == total:
                print(f"  {done}/{total} — instrumental: {instrumental}, vocal: {vocal}, unknown: {unknown}")
            time.sleep(0.5)
        except Exception as e:
            print(f"  Batch failed: {e}")
            time.sleep(2)

    print(f"\nDone.")
    print(f"  Instrumental : {instrumental}")
    print(f"  Vocal        : {vocal}")
    print(f"  Unknown      : {unknown}")
    conn.close()

if __name__ == "__main__":
    main()

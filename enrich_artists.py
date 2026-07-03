#!/usr/bin/env python3
"""
MusicMind for Plex - Artist Metadata Enrichment
Enriches artist records with gender, country, era, and group type via OpenAI.
"""

import sqlite3
import json
import sys
import time
from openai import OpenAI
from datetime import datetime
from config import DB_PATH, OPENAI_KEY

BATCH_SIZE = 20

client = OpenAI(api_key=OPENAI_KEY)

def init_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS artist_meta (
            artist        TEXT PRIMARY KEY,
            gender        TEXT,
            country       TEXT,
            era           TEXT,
            group_type    TEXT,
            active_since  INTEGER,
            enriched_at   TEXT
        )
    """)
    conn.commit()
    print("Table ready.\n")

def get_unenriched_artists(conn):
    """
    Returns list of (artist, mbid) tuples needing OpenAI enrichment.
    Includes brand-new artists (mbid=None) and MusicBrainz-matched
    artists still missing an era value (mbid populated).
    """
    return [(row[0], row[1]) for row in conn.execute("""
        SELECT DISTINCT COALESCE(t.real_artist, t.artist) as effective_artist, am.mbid
        FROM tracks t
        LEFT JOIN artist_meta am ON am.artist = COALESCE(t.real_artist, t.artist)
        WHERE COALESCE(t.real_artist, t.artist) IS NOT NULL
          AND COALESCE(t.real_artist, t.artist) != ''
          AND (am.artist IS NULL OR am.era IS NULL)
        ORDER BY effective_artist
    """).fetchall()]

def enrich_batch(batch):
    """batch is a list of (artist, mbid) tuples."""
    lines = []
    for i, (artist, mbid) in enumerate(batch):
        if mbid:
            lines.append(f"{i+1}. {artist} [MusicBrainz ID: {mbid}]")
        else:
            lines.append(f"{i+1}. {artist}")
    artist_list = "\n".join(lines)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=[{
            "role": "user",
            "content": f"""For each musician/artist/band below, return metadata.
Some entries include a MusicBrainz ID in brackets — use it to identify the
specific correct artist and improve accuracy if you recognize it, but every
artist still needs a full response regardless.

Fields:
- gender: "female", "male", "mixed" (band with multiple genders), "unknown"
- country: 2-letter ISO country code (e.g. "US", "UK", "BR", "FR") or "unknown"
- era: primary decade of activity — "50s", "60s", "70s", "80s", "90s", "00s", "10s", "20s", or "unknown"
- group_type: "solo", "duo", "band", "orchestra", "dj", "unknown"
- active_since: year as integer, or null if unknown

Respond ONLY with a JSON array, one object per artist in order.
Format: [{{"artist": "name", "gender": "...", "country": "...", "era": "...", "group_type": "...", "active_since": null}}, ...]

Artists:
{artist_list}"""
        }]
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)

def main():
    test_mode = "--test" in sys.argv
    limit = None
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])

    print("MusicMind for Plex - Artist Metadata Enrichment")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH, timeout=30)
    init_table(conn)

    artists = get_unenriched_artists(conn)
    total = len(artists)

    if test_mode:
        artists = artists[:limit or 10]
        total = len(artists)
        print("=" * 50)
        print("DRY RUN — nothing will be written to the database")
        print("=" * 50)
    elif limit:
        artists = artists[:limit]
        total = len(artists)
        print(f"LIMITED RUN — processing only {total} artists\n")

    print(f"Artists to enrich: {total}\n")

    if total == 0:
        print("All artists already enriched!")
        conn.close()
        return

    done = 0
    now = datetime.now().isoformat()

    for i in range(0, total, BATCH_SIZE):
        batch = artists[i:i+BATCH_SIZE]
        try:
            results = enrich_batch(batch)
            for j, result in enumerate(results):
                if j >= len(batch):
                    break
                artist_name = batch[j][0]

                if test_mode:
                    print(f"  ✅ WOULD ENRICH: {artist_name}")
                    print(f"       gender:       {result.get('gender', 'unknown')}")
                    print(f"       country:      {result.get('country', 'unknown')}")
                    print(f"       era:          {result.get('era', 'unknown')}")
                    print(f"       group_type:   {result.get('group_type', 'unknown')}")
                    print(f"       active_since: {result.get('active_since')}")
                    continue

                # Create a full row only if one doesn't already exist
                # (no-op if MusicBrainz already wrote a row for this artist)
                conn.execute("""
                    INSERT OR IGNORE INTO artist_meta
                        (artist, gender, country, era, group_type, active_since, enriched_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    artist_name,
                    result.get('gender', 'unknown'),
                    result.get('country', 'unknown'),
                    result.get('era', 'unknown'),
                    result.get('group_type', 'unknown'),
                    result.get('active_since'),
                    now
                ))
                # Always fill in era/group_type/active_since — never touches
                # gender/country/mbid, so MusicBrainz data is preserved.
                conn.execute("""
                    UPDATE artist_meta
                    SET era = ?, group_type = ?, active_since = ?, enriched_at = ?
                    WHERE artist = ?
                """, (
                    result.get('era', 'unknown'),
                    result.get('group_type', 'unknown'),
                    result.get('active_since'),
                    now,
                    artist_name
                ))

            if not test_mode:
                conn.commit()
                done += len(batch)
                print(f"  {done}/{total} artists enriched")
            else:
                done += len(batch)

            time.sleep(0.5)
        except Exception as e:
            print(f"  Batch failed: {e}")
            time.sleep(2)

    if test_mode:
        print("\n" + "=" * 50)
        print(f"DRY RUN COMPLETE — {done} artists checked")
        print("Nothing was written to the database.")
        print("=" * 50)
        conn.close()
        return

    print(f"\nDone. Enriched {done} artists.")

    # Quick summary
    print("\n=== Summary ===")
    for label, field, val in [
        ("Female artists",  "gender",     "female"),
        ("Male artists",    "gender",     "male"),
        ("Mixed bands",     "gender",     "mixed"),
        ("US artists",      "country",    "US"),
        ("UK artists",      "country",    "UK"),
        ("Solo artists",    "group_type", "solo"),
        ("Bands",           "group_type", "band"),
    ]:
        count = conn.execute(
            f"SELECT COUNT(*) FROM artist_meta WHERE {field} = ?", (val,)
        ).fetchone()[0]
        print(f"  {label:20s}  {count}")

    conn.close()

if __name__ == "__main__":
    main()

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

# Found real (August 2026): several confirmed, real mismatches between
# how Last.fm reports an artist name and how it's actually stored in
# the library -- none of these are "different artists," they're the
# exact same artist written slightly differently:
#   - Case ("Nvdes" vs "NVDES", "Galt Macdermot" vs "Galt MacDermot")
#   - "and" vs "&" ("Jonathan Richman And..." vs "...& The Modern Lovers")
#   - Smart/curly quotes vs straight ones -- confirmed with "Howlin' Wolf"
#     (library uses U+2019, a real, different character from the
#     ordinary U+0027 apostrophe, genuinely invisible to the eye)
#   - Various Unicode hyphens/dashes vs a plain ASCII hyphen --
#     confirmed with "The B‐52s" (library uses U+2010, not U+002D)
# Deliberately does NOT try to fix genuine artist aliases (e.g. "Mos
# Def" vs "Yasiin Bey" -- literally different names for the same
# person) or word-spacing differences ("Colourfield" vs "Colour
# Field") -- no safe, general normalization bridges those without
# real risk of new false matches elsewhere; they're a separate,
# harder problem, not a formatting bug.
def normalize_artist_name(name):
    if not name:
        return ''
    name = name.replace('\u2018', "'").replace('\u2019', "'")  # curly single quotes
    name = name.replace('\u201c', '"').replace('\u201d', '"')  # curly double quotes
    for dash in ('\u2010', '\u2011', '\u2012', '\u2013', '\u2014', '\u2212'):
        name = name.replace(dash, '-')  # various Unicode hyphens/dashes
    name = name.lower().strip()
    name = ' '.join(name.split())  # collapse repeated whitespace
    name = name.replace(' and ', ' & ')
    return name


# Found real (August 2026): normalize_artist_name() alone still
# missed a real, confirmed case -- "The B-52's" (scrobble, WITH an
# apostrophe) vs the library's actual "The B‐52s" (confirmed via
# direct inspection -- genuinely NO apostrophe at all, not just a
# different quote style). Normalizing curly-vs-straight quotes
# doesn't help when one side has no apostrophe whatsoever. This goes
# further specifically for matching purposes -- stripping apostrophes
# and hyphens out entirely, not just normalizing their style. Kept
# separate from normalize_artist_name() itself, which stays available
# for anywhere punctuation might still matter (e.g. display).
def normalize_for_matching(name):
    name = normalize_artist_name(name)
    name = name.replace("'", '').replace('-', '')
    name = ' '.join(name.split())
    return name

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
    known = set()
    for row in conn.execute("""
        SELECT DISTINCT COALESCE(real_artist, artist) FROM tracks
        WHERE artist IS NOT NULL AND artist != ''
    """).fetchall():
        if row[0]:
            known.add(normalize_for_matching(row[0]))

    gaps = conn.execute("SELECT artist FROM artist_gaps").fetchall()
    deleted = 0
    for (gap_artist,) in gaps:
        ga = normalize_for_matching(gap_artist)
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
    # Found real (August 2026): this used to be a pure SQL NOT IN
    # query, checked via SQLite's default (case-sensitive, Unicode-
    # unaware) string comparison -- a genuinely different, weaker
    # match than cleanup_acquired()'s own Python-side fuzzy check
    # just above. That inconsistency was the real root cause behind
    # several confirmed false gaps. Now shares the exact same
    # normalize_artist_name() + fuzzy substring logic as
    # cleanup_acquired(), so both paths can never drift apart again.
    known = set()
    for row in conn.execute("""
        SELECT DISTINCT COALESCE(real_artist, artist) FROM tracks
        WHERE COALESCE(real_artist, artist) IS NOT NULL
          AND COALESCE(real_artist, artist) != ''
    """).fetchall():
        if row[0]:
            known.add(normalize_for_matching(row[0]))

    scrobble_counts = conn.execute("""
        SELECT artist, COUNT(*) as scrobbles
        FROM lastfm_scrobbles
        GROUP BY artist
        HAVING scrobbles >= ?
        ORDER BY scrobbles DESC
    """, (MIN_SCROBBLES,)).fetchall()

    gaps = []
    for artist, scrobbles in scrobble_counts:
        na = normalize_for_matching(artist)
        if not any(na == k or na in k or k in na for k in known):
            gaps.append((artist, scrobbles))
    return gaps

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

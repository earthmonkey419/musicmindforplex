#!/usr/bin/env python3
"""
MusicMind for Plex - MusicBrainz Artist Enrichment

Looks up each unenriched artist against the MusicBrainz API to get
accurate country, gender, and era data (replacing OpenAI guesses with
real recorded data where available). Artists MusicBrainz can't
confidently match are logged to mb_unmatched_artists for the OpenAI
fallback (enrich_artists.py) to handle.

No API key required — MusicBrainz only requires a descriptive
User-Agent and a max of 1 request/second.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqlite3
import time
import urllib.request
import urllib.parse
import json
from datetime import datetime
from config import DB_PATH

MB_BASE = "https://musicbrainz.org/ws/2"
USER_AGENT = "MusicMindForPlex/1.0 (https://github.com/earthmonkey419/musicmindforplex)"
CONFIDENCE_THRESHOLD = 85
REQUEST_DELAY = 1.1  # seconds, slightly over the 1 req/sec limit for safety


def init_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS artist_meta (
            artist        TEXT PRIMARY KEY,
            gender        TEXT,
            country       TEXT,
            era           TEXT,
            group_type    TEXT,
            active_since  INTEGER,
            mbid          TEXT,
            enriched_at   TEXT
        )
    """)
    try:
        conn.execute("ALTER TABLE artist_meta ADD COLUMN mbid TEXT")
    except Exception:
        pass  # column already exists (or table just created with it)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS mb_unmatched_artists (
            artist        TEXT PRIMARY KEY,
            best_score    INTEGER,
            checked_at    TEXT
        )
    """)
    conn.commit()


# Placeholder/non-artist strings that should never be sent to MusicBrainz —
# loose-query fuzzy matching can otherwise match these to unrelated real
# artists with high confidence, corrupting artist_meta with a wrong mbid.
PLACEHOLDER_ARTISTS = ('Various Artists', 'VA', 'Unknown Artist', 'Unknown')


def get_unenriched_artists(conn):
    """
    Returns artists still needing MusicBrainz lookup — either brand-new
    artists with no artist_meta row at all, or existing artists (e.g.
    from earlier OpenAI-only enrichment) that don't yet have an mbid.
    Skips anything already logged as unmatched, and skips known
    placeholder/non-artist strings entirely.
    """
    placeholders = ",".join("?" for _ in PLACEHOLDER_ARTISTS)
    return [row[0] for row in conn.execute(f"""
        SELECT DISTINCT COALESCE(t.real_artist, t.artist) as effective_artist
        FROM tracks t
        LEFT JOIN artist_meta am ON am.artist = COALESCE(t.real_artist, t.artist)
        WHERE COALESCE(t.real_artist, t.artist) IS NOT NULL
          AND COALESCE(t.real_artist, t.artist) != ''
          AND (am.artist IS NULL OR am.mbid IS NULL)
          AND COALESCE(t.real_artist, t.artist) NOT IN (SELECT artist FROM mb_unmatched_artists)
          AND COALESCE(t.real_artist, t.artist) NOT IN ({placeholders})
        ORDER BY effective_artist
    """, PLACEHOLDER_ARTISTS).fetchall()]


def mb_request(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


# MusicBrainz's own "Various Artists" catch-all entity — a stable, permanent
# MBID. This entity has dozens of multilingual aliases and can match almost
# any obscure/ambiguous query with a misleadingly high relevance score. It
# should never be accepted as a real artist match, regardless of score.
MB_VARIOUS_ARTISTS_ID = "89ad4ac3-39f7-470e-963a-56509c546377"


def search_artist(name):
    """Search MusicBrainz for an artist name. Returns best match dict or None."""
    query = urllib.parse.quote(name)
    url = f"{MB_BASE}/artist?query={query}&fmt=json&limit=5"
    try:
        data = mb_request(url)
    except Exception as e:
        print(f"  ⚠️ Search error for '{name}': {e}")
        return None

    artists = data.get("artists", [])
    # Exclude MusicBrainz's "Various Artists" catch-all — never a real match
    artists = [a for a in artists if a.get("id") != MB_VARIOUS_ARTISTS_ID]
    if not artists:
        return None

    best = max(artists, key=lambda a: a.get("score", 0))
    return best


def lookup_artist(mbid):
    """Fetch full artist details by MBID. Returns dict."""
    url = f"{MB_BASE}/artist/{mbid}?fmt=json"
    try:
        return mb_request(url)
    except Exception as e:
        print(f"  ⚠️ Lookup error for {mbid}: {e}")
        return None


def year_to_era(year):
    """Convert a year like 1978 to a decade string like '70s'."""
    if not year:
        return None
    try:
        y = int(str(year)[:4])
    except (ValueError, TypeError):
        return None
    decade = (y % 100) // 10 * 10
    return f"{decade}s"


def enrich(conn, test_mode=False, limit=None):
    init_tables(conn)
    artists = get_unenriched_artists(conn)
    total = len(artists)

    if test_mode:
        artists = artists[:limit or 10]
        total = len(artists)
        print("=" * 40)
        print("DRY RUN — nothing will be written to the database")
        print("=" * 40)
    elif limit:
        artists = artists[:limit]
        total = len(artists)
        print(f"LIMITED RUN — processing only {total} artists\n")

    print(f"MusicMind for Plex - MusicBrainz Artist Enrichment")
    print("=" * 40)
    print(f"Found {total} {'test ' if test_mode else ''}artists to check.\n")

    matched = 0
    unmatched = 0

    for i, artist in enumerate(artists, 1):
        result = search_artist(artist)
        time.sleep(REQUEST_DELAY)

        score = result.get("score", 0) if result else 0

        if not result or score < CONFIDENCE_THRESHOLD:
            unmatched += 1
            if test_mode:
                print(f"  ⚠️ WOULD SKIP (low confidence): {artist} (score: {score})")
            else:
                conn.execute("""
                    INSERT OR REPLACE INTO mb_unmatched_artists (artist, best_score, checked_at)
                    VALUES (?, ?, ?)
                """, (artist, score, datetime.now().isoformat()))
                conn.commit()
                print(f"  ⚠️ SKIPPED (low confidence): {artist} (score: {score})")
            continue

        mbid = result.get("id")
        details = lookup_artist(mbid)
        time.sleep(REQUEST_DELAY)

        if not details:
            unmatched += 1
            if test_mode:
                print(f"  ⚠️ WOULD SKIP (lookup failed): {artist}")
            else:
                conn.execute("""
                    INSERT OR REPLACE INTO mb_unmatched_artists (artist, best_score, checked_at)
                    VALUES (?, ?, ?)
                """, (artist, score, datetime.now().isoformat()))
                conn.commit()
            continue

        country = None
        area = details.get("area")
        if area:
            country = area.get("name")

        gender = details.get("gender")  # only present for type: Person
        if gender:
            # MusicBrainz's API returns "Male"/"Female" capitalized —
            # normalize to lowercase to match the convention used
            # elsewhere in artist_meta (the OpenAI fallback writes
            # lowercase 'male'/'female'). Without this, gender was
            # effectively split into two separate, uncombined
            # categories in the stats charts.
            gender = gender.lower()
        # Note: era intentionally NOT set here — MusicBrainz has no reliable
        # "primary decade of activity" field. Era is left to the OpenAI
        # fallback (enrich_artists.py), which is better suited to that
        # interpretive judgment than raw MusicBrainz data.

        matched += 1

        if test_mode:
            print(f"  ✅ WOULD MATCH: {artist}")
            print(f"       mbid:    {mbid}")
            print(f"       score:   {score}")
            print(f"       country: {country}")
            print(f"       gender:  {gender}")
        else:
            conn.execute("""
                INSERT OR REPLACE INTO artist_meta
                    (artist, gender, country, mbid, enriched_at)
                VALUES (?, ?, ?, ?, ?)
            """, (artist, gender, country, mbid, datetime.now().isoformat()))
            conn.commit()

            if i % 25 == 0:
                print(f"  {i}/{total} checked... ({matched} matched, {unmatched} unmatched)")

    if test_mode:
        print("\n" + "=" * 40)
        print(f"DRY RUN COMPLETE — {matched} would match, {unmatched} would be unmatched")
        print("Nothing was written to the database.")
        print("=" * 40)
    else:
        print(f"\nDone. {matched} artists enriched via MusicBrainz, {unmatched} unmatched (fallback to AI).")
        print(f"Database: {DB_PATH}")


def main():
    test_mode = "--test" in sys.argv
    limit = None
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])
    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")
    enrich(conn, test_mode=test_mode, limit=limit)
    conn.close()


if __name__ == "__main__":
    main()

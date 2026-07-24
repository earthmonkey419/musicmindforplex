#!/usr/bin/env python3
"""
MusicMind for Plex - Last.fm Sync
Pulls full scrobble history and loved tracks from Last.fm.
Matches to local tracks table by artist+title.
First run: pulls everything (~111K scrobbles, 10-15 min)
Subsequent runs: only pulls new scrobbles since last sync.
"""

import sqlite3
import urllib.request
import json
import time
from datetime import datetime
from config import DB_PATH, LASTFM_KEY, LASTFM_USER

API_KEY  = LASTFM_KEY
USERNAME = LASTFM_USER
API_BASE = "http://ws.audioscrobbler.com/2.0/"

def init_tables(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lastfm_scrobbles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   INTEGER NOT NULL,
            artist      TEXT,
            title       TEXT,
            album       TEXT,
            rating_key  TEXT,
            matched     INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_scrobbles_timestamp
        ON lastfm_scrobbles(timestamp)
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_scrobbles_artist_title
        ON lastfm_scrobbles(artist, title)
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lastfm_loved (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp   INTEGER,
            artist      TEXT,
            title       TEXT,
            rating_key  TEXT,
            matched     INTEGER DEFAULT 0
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS lastfm_meta (
            key         TEXT PRIMARY KEY,
            value       TEXT
        )
    """)
    conn.commit()
    print("Tables ready.\n")

def api_call(params):
    params['api_key'] = API_KEY
    params['format']  = 'json'
    query = '&'.join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
    url = f"{API_BASE}?{query}"
    for attempt in range(3):
        try:
            data = json.loads(urllib.request.urlopen(url, timeout=10).read())
            return data
        except Exception as e:
            print(f"  API error (attempt {attempt+1}): {e}")
            time.sleep(2)
    return None

def get_last_sync(conn):
    row = conn.execute("SELECT value FROM lastfm_meta WHERE key='last_sync'").fetchone()
    return int(row[0]) if row else None

def set_last_sync(conn, ts):
    conn.execute("INSERT OR REPLACE INTO lastfm_meta (key, value) VALUES ('last_sync', ?)", (str(ts),))
    conn.commit()

import re

def normalize_title(title):
    """
    Strips COSMETIC-ONLY title differences that represent the SAME
    underlying recording -- remaster tags and feature credits --
    used only as a fallback when exact matching fails. Deliberately
    does NOT touch anything that could represent a genuinely
    DIFFERENT recording of the song: Live, Acoustic, Demo, Remix,
    Radio Edit, Extended Mix, Instrumental, Alternate Take, etc. all
    stay completely untouched -- conflating those would be a real
    correctness regression, not an improvement.

    Found real (July 2026): Last.fm and a locally-stored track can
    each carry cosmetic info the other lacks, in EITHER direction --
    "Birdmad Girl - 2006 Remaster" (scrobble) vs "Birdmad Girl"
    (library), and "My Mind Is" (scrobble) vs "My Mind Is (feat.
    Oliver Tree)" (library). Stripping from both sides before
    comparing handles both directions with one mechanism.
    """
    t = title
    # Remaster tags: "- 2006 Remaster", "(2006 Remastered)",
    # "- Remastered 2011", "(Remaster)"
    t = re.sub(r'\s*[-–—]\s*\d{4}\s*Remaster(ed)?\s*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s*\(\s*\d{4}\s*Remaster(ed)?\s*\)\s*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s*[-–—]\s*Remaster(ed)?(\s+\d{4})?\s*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s*\(\s*Remaster(ed)?(\s+\d{4})?\s*\)\s*$', '', t, flags=re.IGNORECASE)
    # Feature credits: "(feat. X)", "(ft. X)", "(featuring X)", same with []
    t = re.sub(r'\s*[\(\[]\s*(feat\.|ft\.|featuring)\s+[^\)\]]+[\)\]]\s*$', '', t, flags=re.IGNORECASE)
    return t.strip()


def match_track(conn, artist, title):
    """
    Tries an EXACT match first (highest confidence, unchanged
    behavior). Falls back to a cosmetic-normalized match only if
    that fails -- see normalize_title() for exactly what's considered
    "cosmetic" vs. a genuinely different recording.

    Also now matches against COALESCE(real_artist, artist) instead of
    the raw artist column -- closes the same class of gap found and
    fixed for AI tagging earlier this session (a VA-resolved track's
    real artist name living in a separate column nobody was reading).

    Known, accepted limitation: if a library genuinely contains
    multiple different official versions that normalize to the same
    title (e.g. two different guest-feature releases of the same
    song), the first match found wins -- rare enough not to be worth
    the added complexity of resolving right now.
    """
    row = conn.execute("""
        SELECT rating_key FROM tracks
        WHERE LOWER(COALESCE(real_artist, artist)) = LOWER(?)
          AND LOWER(title) = LOWER(?)
        LIMIT 1
    """, (artist, title)).fetchone()
    if row:
        return row[0]

    # Deliberately does NOT bail early just because the query side has
    # nothing to strip -- found a real bug here during testing: the
    # extra cosmetic info can live on EITHER side (a feature credit
    # might only be on the LIBRARY's stored title, e.g. "My Mind Is"
    # scrobbled vs. "My Mind Is (feat. Oliver Tree)" stored locally).
    # Always normalizes both sides and compares.
    normalized_query = normalize_title(title)
    if not normalized_query:
        return None

    candidates = conn.execute("""
        SELECT rating_key, title FROM tracks
        WHERE LOWER(COALESCE(real_artist, artist)) = LOWER(?)
    """, (artist,)).fetchall()

    for rk, candidate_title in candidates:
        if candidate_title and normalize_title(candidate_title).lower() == normalized_query.lower():
            return rk

    return None

def rematch_unmatched_scrobbles(conn):
    """
    One-off/periodic re-match pass -- sync_scrobbles() only ever
    attempts to match each scrobble ONCE, at the exact moment it's
    first synced from Last.fm. If the corresponding track gets added
    to the library LATER (a very normal thing -- libraries grow over
    time), that scrobble stays permanently marked unmatched forever,
    with no retry, even once the track genuinely exists locally.

    Found real (July 2026): confirmed via a real example (Tim
    Buckley's "Gypsy Woman") where artist/title matched the local
    library BYTE-FOR-BYTE, yet stayed unmatched -- every scrobble
    from an album the library didn't yet contain at sync time was
    permanently stuck, while scrobbles from an album already owned
    at that time matched correctly. Not a string-matching bug at all;
    a timing/staleness bug in the same family as several others this
    session (incremental processes that never retroactively revisit
    already-processed data once conditions change).

    Batches by DISTINCT (artist, title) rather than re-matching every
    individual scrobble row -- a song scrobbled 50 times only needs
    ONE match_track() call, then a single UPDATE applies the result
    to every row sharing that exact pair. Safe to re-run anytime;
    only ever touches rows that genuinely newly match.

    Returns (pairs_rematched, rows_updated, pairs_checked).
    """
    distinct_unmatched = conn.execute("""
        SELECT DISTINCT artist, title FROM lastfm_scrobbles WHERE matched = 0
    """).fetchall()

    total_pairs = len(distinct_unmatched)
    if total_pairs > 200:
        # Found real (July 2026): a large first-time backlog clear
        # produced zero output for long enough to look like a silent
        # hang, even though it was genuinely working the whole time
        # (confirmed via ps aux CPU time climbing). Only print progress
        # for a genuinely large backlog -- routine ongoing syncs should
        # stay quiet, matching the function's normal cheap/fast case.
        print(f"  Checking {total_pairs} previously-unmatched tracks against the current library...")

    pairs_rematched = 0
    rows_updated = 0
    for i, (artist, title) in enumerate(distinct_unmatched, 1):
        if total_pairs > 200 and i % 500 == 0:
            print(f"    {i}/{total_pairs} checked ({pairs_rematched} rematched so far)")
        rk = match_track(conn, artist, title)
        if rk:
            cursor = conn.execute("""
                UPDATE lastfm_scrobbles SET rating_key = ?, matched = 1
                WHERE artist = ? AND title = ? AND matched = 0
            """, (rk, artist, title))
            rows_updated += cursor.rowcount
            pairs_rematched += 1

    conn.commit()
    return pairs_rematched, rows_updated, len(distinct_unmatched)


def sync_scrobbles(conn):
    import urllib.parse

    last_sync = get_last_sync(conn)
    if last_sync:
        print(f"Last sync: {datetime.fromtimestamp(last_sync).strftime('%Y-%m-%d %H:%M')}")
        print("Pulling new scrobbles since last sync...\n")
    else:
        print("First run — pulling full scrobble history (~111K scrobbles)...\n")

    page        = 1
    total_pages = 1
    inserted    = 0
    matched     = 0
    newest_ts   = 0

    while page <= total_pages:
        params = {
            'method':   'user.getrecenttracks',
            'user':     USERNAME,
            'limit':    200,
            'page':     page,
            'extended': 0,
        }
        if last_sync:
            params['from'] = last_sync + 1

        data = api_call(params)
        if not data or 'recenttracks' not in data:
            print(f"  Page {page} failed, skipping.")
            page += 1
            continue

        tracks     = data['recenttracks']['track']
        attr       = data['recenttracks']['@attr']
        total_pages = int(attr['totalPages'])

        if page == 1:
            print(f"Total pages: {total_pages} ({int(attr.get('total',0))} scrobbles)\n")

        for track in tracks:
            # Skip currently playing track (no timestamp)
            if 'date' not in track:
                continue

            ts     = int(track['date']['uts'])
            artist = track['artist']['#text']
            title  = track['name']
            album  = track['album']['#text']

            if ts > newest_ts:
                newest_ts = ts

            rk = match_track(conn, artist, title)

            conn.execute("""
                INSERT INTO lastfm_scrobbles (timestamp, artist, title, album, rating_key, matched)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (ts, artist, title, album, rk, 1 if rk else 0))

            inserted += 1
            if rk:
                matched += 1

        conn.commit()

        if page % 50 == 0 or page == total_pages:
            print(f"  Page {page}/{total_pages} — {inserted} scrobbles inserted ({matched} matched)")

        page += 1
        time.sleep(0.25)  # Be polite to Last.fm API

    if newest_ts:
        set_last_sync(conn, newest_ts)

    print(f"\nScrobbles done. {inserted} inserted, {matched} matched to local tracks.")
    return inserted, matched

def sync_loved(conn):
    import urllib.parse
    print("\nPulling loved tracks...")

    # Clear existing loved tracks and re-pull fresh
    conn.execute("DELETE FROM lastfm_loved")
    conn.commit()

    page        = 1
    total_pages = 1
    inserted    = 0
    matched     = 0

    while page <= total_pages:
        data = api_call({
            'method': 'user.getlovedtracks',
            'user':   USERNAME,
            'limit':  200,
            'page':   page,
        })

        if not data or 'lovedtracks' not in data:
            page += 1
            continue

        tracks      = data['lovedtracks']['track']
        total_pages = int(data['lovedtracks']['@attr']['totalPages'])

        for track in tracks:
            ts     = int(track['date']['uts']) if 'date' in track else 0
            artist = track['artist']['name']
            title  = track['name']
            rk     = match_track(conn, artist, title)

            conn.execute("""
                INSERT INTO lastfm_loved (timestamp, artist, title, rating_key, matched)
                VALUES (?, ?, ?, ?, ?)
            """, (ts, artist, title, rk, 1 if rk else 0))

            inserted += 1
            if rk:
                matched += 1

        conn.commit()
        page += 1
        time.sleep(0.25)

    print(f"Loved tracks done. {inserted} pulled, {matched} matched to local tracks.")
    return inserted, matched

def update_play_counts(conn):
    print("\nUpdating play counts from scrobble history...")
    conn.execute("""
        UPDATE tracks
        SET play_count = (
            SELECT COUNT(*) FROM lastfm_scrobbles
            WHERE lastfm_scrobbles.rating_key = tracks.rating_key
        )
        WHERE rating_key IN (SELECT DISTINCT rating_key FROM lastfm_scrobbles WHERE rating_key IS NOT NULL)
    """)
    conn.commit()
    updated = conn.execute("SELECT COUNT(*) FROM tracks WHERE play_count > 0").fetchone()[0]
    print(f"Updated play counts for {updated} tracks.")

def update_loved_ratings(conn):
    print("\nUpdating ratings for loved tracks...")
    conn.execute("""
        UPDATE tracks
        SET user_rating = 10
        WHERE rating_key IN (
            SELECT rating_key FROM lastfm_loved
            WHERE rating_key IS NOT NULL
        )
    """)
    conn.commit()
    updated = conn.execute("SELECT COUNT(*) FROM tracks WHERE user_rating = 10").fetchone()[0]
    print(f"Set 5-star rating for {updated} loved tracks.")

def print_stats(conn):
    print("\n=== Last.fm Sync Stats ===")

    total_scrobbles = conn.execute("SELECT COUNT(*) FROM lastfm_scrobbles").fetchone()[0]
    matched_scrobbles = conn.execute("SELECT COUNT(*) FROM lastfm_scrobbles WHERE matched=1").fetchone()[0]
    print(f"Total scrobbles : {total_scrobbles}")
    print(f"Matched         : {matched_scrobbles} ({matched_scrobbles*100//total_scrobbles if total_scrobbles else 0}%)")

    print("\nTop 10 most played:")
    for row in conn.execute("""
        SELECT artist, title, COUNT(*) as plays
        FROM lastfm_scrobbles
        GROUP BY artist, title
        ORDER BY plays DESC
        LIMIT 10
    """):
        print(f"  {row[2]:4d}x  {row[0]} - {row[1]}")

    print("\nListening by year:")
    for row in conn.execute("""
        SELECT strftime('%Y', datetime(timestamp, 'unixepoch')) as year, COUNT(*) as plays
        FROM lastfm_scrobbles
        GROUP BY year
        ORDER BY year
    """):
        print(f"  {row[0]}  {row[1]:6d} plays")

def main():
    import urllib.parse
    print("MusicMind for Plex - Last.fm Sync")
    print("=" * 40)

    if not LASTFM_KEY or not LASTFM_USER:
        print("Last.fm credentials not set in config.py — skipping.")
        print("(This is optional. Set LASTFM_KEY and LASTFM_USER to enable.)")
        return

    conn = sqlite3.connect(DB_PATH, timeout=30)
    init_tables(conn)
    sync_scrobbles(conn)
    sync_loved(conn)

    # Runs automatically every sync now, not just as a one-off manual
    # fix -- found real (July 2026): sync_scrobbles() only ever
    # attempts each scrobble ONCE, at the moment it's first synced.
    # A scrobble stays permanently "unmatched" forever if the track
    # gets added to the library later, unless something re-attempts
    # it. Cheap on ongoing runs (only checks scrobbles still marked
    # unmatched, batched by distinct artist/title pair) -- the real
    # cost is only on the FIRST run clearing an existing backlog.
    print("\nRe-checking previously unmatched scrobbles against the current library...")
    pairs_rematched, rows_updated, pairs_checked = rematch_unmatched_scrobbles(conn)
    print(f"Rematched {rows_updated} scrobbles ({pairs_rematched} distinct tracks) "
          f"out of {pairs_checked} previously-unmatched tracks checked.")

    update_play_counts(conn)
    update_loved_ratings(conn)
    print_stats(conn)
    conn.close()
    print("\nDone.")

if __name__ == "__main__":
    main()

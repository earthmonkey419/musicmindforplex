#!/usr/bin/env python3.12
"""
MusicMind for Plex - Recording MusicBrainz ID Backfill

Populates track_fingerprints.recording_mbid for tracks with a known
artist, identifying the specific RECORDING (not resolving the artist,
which is already known) via AcoustID. The column has existed in the
schema since fingerprint_tracks.py was built, but was never populated
for anything outside va_resolve.py's own artist-resolution flow.

Reuses already-stored fingerprints -- no audio re-decode needed at
all, since fingerprint_tracks.py already computed and stored them.
Two phases:
  1. Free backfill from va_results.recording_mbid where a VA-resolved
     track already has this data -- zero API calls needed.
  2. Fresh AcoustID lookups for every other fingerprinted track still
     missing a recording_mbid, using the exact same SCORE_FLOOR and
     rate-limit conventions already proven in va_resolve.py.

Usage:
    python3.12 resolve_recording_mbids.py --dry-run   # report only
    python3.12 resolve_recording_mbids.py --limit 50  # small test run
    python3.12 resolve_recording_mbids.py             # full run
"""
import sys
import os
import time
import sqlite3
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH

try:
    from config import ACOUSTID_KEY
except ImportError:
    ACOUSTID_KEY = ""

SCORE_FLOOR = 0.90


def backfill_from_va_results(conn, dry_run=False):
    """
    Phase 1: free backfill. Any track already resolved via
    va_resolve.py has a recording_mbid sitting in va_results --
    copy it into track_fingerprints if that row doesn't have one yet.
    Zero API calls, zero cost.
    """
    rows = conn.execute("""
        SELECT va.rating_key, va.recording_mbid
        FROM va_results va
        JOIN track_fingerprints tf ON tf.rating_key = va.rating_key
        WHERE va.recording_mbid IS NOT NULL
          AND tf.recording_mbid IS NULL
    """).fetchall()

    print(f"Phase 1: {len(rows)} tracks can be backfilled for free from va_results.\n")

    if dry_run or not rows:
        return len(rows)

    conn.executemany(
        "UPDATE track_fingerprints SET recording_mbid = ? WHERE rating_key = ?",
        [(mbid, rk) for rk, mbid in rows]
    )
    conn.commit()
    return len(rows)


def get_recording_mbid(fingerprint, duration, api_key):
    """
    Looks up an already-known-artist track's stored fingerprint
    against AcoustID purely to identify the specific recording --
    NOT to resolve who the artist is (already known, unlike
    va_resolve.py's job). Takes the top-scoring result's first
    recording ID, same SCORE_FLOOR convention already proven there.
    Returns (recording_mbid_or_None, status_string).
    """
    try:
        r = requests.post("https://api.acoustid.org/v2/lookup", data={
            "client": api_key, "meta": "recordings",
            "duration": int(duration),
            "fingerprint": fingerprint,
        }, timeout=30).json()
    except Exception as e:
        return None, f"request_error:{e}"

    if r.get("status") != "ok" or not r.get("results"):
        return None, "no_results"

    top = max(r["results"], key=lambda x: x.get("score", 0))
    if top.get("score", 0) < SCORE_FLOOR:
        return None, f"low_score:{top.get('score'):.2f}"

    recs = top.get("recordings") or []
    if not recs:
        return None, "no_recordings"

    return recs[0].get("id"), None


def get_needing_lookup(conn, limit=None):
    """
    Phase 2 candidates: tracks with a real, usable stored fingerprint
    but still no recording_mbid (after Phase 1's free backfill).
    """
    query = """
        SELECT rating_key, fingerprint, fp_duration
        FROM track_fingerprints
        WHERE fingerprint IS NOT NULL
          AND fp_duration IS NOT NULL
          AND recording_mbid IS NULL
        ORDER BY rating_key
    """
    if limit:
        query += f" LIMIT {int(limit)}"
    return conn.execute(query).fetchall()


def main():
    dry_run = "--dry-run" in sys.argv
    limit = None
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])

    print("MusicMind for Plex - Recording MusicBrainz ID Backfill")
    print("=" * 55)

    if not ACOUSTID_KEY:
        print("AcoustID key not set in config.py — skipping.")
        print("(Get a free key at https://acoustid.org/ and set ACOUSTID_KEY.)")
        return

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")

    backfilled = backfill_from_va_results(conn, dry_run=dry_run)

    rows = get_needing_lookup(conn, limit=limit)
    total = len(rows)
    print(f"Phase 2: {total} tracks need a fresh AcoustID lookup.\n")

    if dry_run:
        print("DRY RUN — nothing written to the database.")
        conn.close()
        return

    if total == 0:
        print("Nothing to do.")
        conn.close()
        return

    resolved = 0
    counts = {}
    start = time.time()

    for i, (rk, fingerprint, duration) in enumerate(rows, 1):
        mbid, status = get_recording_mbid(fingerprint, duration, ACOUSTID_KEY)

        if mbid:
            conn.execute(
                "UPDATE track_fingerprints SET recording_mbid = ? WHERE rating_key = ?",
                (mbid, rk)
            )
            conn.commit()
            resolved += 1
        else:
            counts[status] = counts.get(status, 0) + 1

        if total > 200 and i % 500 == 0:
            elapsed = time.time() - start
            eta_m = (elapsed / i) * (total - i) / 60
            print(f"  {i}/{total} checked ({resolved} resolved so far) — ETA {eta_m:.1f}m")

        time.sleep(0.4)  # stay under AcoustID's 3 req/s rate limit

    conn.close()

    print(f"\nDone. Backfilled {backfilled} for free, resolved {resolved}/{total} via fresh lookup.")
    if counts:
        print("Not resolved:", ", ".join(f"{k}={v}" for k, v in counts.items()))


if __name__ == "__main__":
    main()

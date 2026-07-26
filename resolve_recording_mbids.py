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

# Found real (July 2026): recording_mbid alone can't distinguish
# "never checked" from "checked, genuinely no match" -- both leave it
# NULL, meaning every future run re-queries AcoustID for tracks that
# already got a real, final answer, forever. This status column
# records that answer. Only DEFINITIVE outcomes go here -- AcoustID
# genuinely has no match, or its best match scored too low to trust.
# Deliberately NOT applied to transient failures (a network hiccup,
# a local DB lock) -- those represent bad luck, not a real answer,
# and should still be retried on the next run.
DEFINITIVE_STATUSES = {"no_results", "no_recordings"}


def is_definitive(status):
    """low_score:0.87 etc. are also definitive -- AcoustID DID
    return a real answer, it just wasn't confident enough to trust."""
    if status in DEFINITIVE_STATUSES:
        return True
    if status and status.startswith("low_score:"):
        return True
    return False


RECHECK_AFTER_DAYS = 180  # AcoustID's crowdsourced database keeps
# growing -- a genuine "no match" today isn't necessarily a "no
# match" forever. Old enough that this doesn't waste API calls
# re-asking the same question too often, short enough that a real,
# newly-available match doesn't sit undiscovered for years.


def init_status_column(conn):
    try:
        conn.execute("ALTER TABLE track_fingerprints ADD COLUMN mbid_check_status TEXT")
    except Exception:
        pass  # column already exists
    try:
        conn.execute("ALTER TABLE track_fingerprints ADD COLUMN mbid_checked_at TEXT")
    except Exception:
        pass  # column already exists


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
    query = f"""
        SELECT rating_key, fingerprint, fp_duration
        FROM track_fingerprints
        WHERE fingerprint IS NOT NULL
          AND fp_duration IS NOT NULL
          AND recording_mbid IS NULL
          AND (
              mbid_check_status IS NULL
              OR mbid_checked_at < datetime('now', '-{RECHECK_AFTER_DAYS} days')
          )
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
    init_status_column(conn)

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
            # Found real (July 2026): this write had zero exception
            # handling -- a genuine "database is locked" error here
            # (plausible on a real production night with multiple
            # deploys, restarts, and other scripts running) crashed
            # the entire script immediately, discarding all progress
            # on whatever tracks were still left to check. The
            # connection's own 60s timeout + busy_timeout already
            # absorbs most transient contention; if it STILL fails
            # after that, it's a genuinely persistent lock -- catch
            # it, log it for this one track, and keep going instead
            # of losing the whole remaining run over it.
            try:
                conn.execute(
                    "UPDATE track_fingerprints SET recording_mbid = ? WHERE rating_key = ?",
                    (mbid, rk)
                )
                conn.commit()
                resolved += 1
            except Exception as e:
                print(f"  ⚠️  DB write failed for rating_key {rk}: {e} — continuing with the rest")
                counts[f"db_error"] = counts.get("db_error", 0) + 1
        else:
            counts[status] = counts.get(status, 0) + 1
            if is_definitive(status):
                try:
                    conn.execute(
                        "UPDATE track_fingerprints SET mbid_check_status = ?, mbid_checked_at = datetime('now') WHERE rating_key = ?",
                        (status, rk)
                    )
                    conn.commit()
                except Exception as e:
                    print(f"  ⚠️  Status write failed for rating_key {rk}: {e} — will just get rechecked next run")
            # transient failures (request_error, etc.) deliberately
            # leave mbid_check_status untouched, so this track stays
            # eligible for a fresh lookup on the next run

        # Found real (July 2026): every-500 was a long, genuinely
        # anxiety-inducing silence on a real run -- at the ~0.4s/track
        # rate-limit pace, 500 tracks is well over 3 minutes of zero
        # visible output, easy to mistake for a hang. Every 25 gives
        # a real heartbeat (roughly every 10 seconds) without being
        # spammy, so it's always clear something is actively moving.
        if total > 20 and i % 25 == 0:
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

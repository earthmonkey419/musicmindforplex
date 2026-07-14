#!/usr/bin/env python3.12
"""
MusicMind for Plex - Acoustic Fingerprinting

Computes a Chromaprint fingerprint for every track that doesn't have
one yet, storing it in track_fingerprints. This is the identity layer
for v3's gatekeeper pipeline: fingerprint FIRST (cheap, ~1s, local,
no rate limit) establishes which tracks are audio-identical, before
any expensive analysis (Synapse, VI) or resolution (AcoustID lookup,
va_resolve.py) runs.

Deliberately does NOT call the AcoustID API — that's a separate,
rate-limited concern handled by va_resolve.py (artist resolution) and
a future dedup report (GROUP BY fingerprint). Raw fingerprint
computation here is fast and unconstrained; keeping it separate from
AcoustID means this step never has to wait on a 3 req/s ceiling.

Usage:
    python3.12 fingerprint_tracks.py              # full run, resumable
    python3.12 fingerprint_tracks.py --limit 30   # test on a sample first
"""
import sys
import os
import json
import time
import sqlite3
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PLEX_URL, PLEX_TOKEN, DB_PATH
from config_check import check_config
check_config(PLEX_URL=PLEX_URL, PLEX_TOKEN=PLEX_TOKEN)

try:
    from config import PATH_MAP
except ImportError:
    PATH_MAP = {}

from plexapi.server import PlexServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FPCALC = os.path.join(BASE_DIR, "bin", "fpcalc")


def translate_path(p):
    """Translate a Plex-reported path to a locally-readable one via PATH_MAP."""
    if not p:
        return p
    for src in sorted(PATH_MAP, key=len, reverse=True):
        if p.startswith(src):
            p = PATH_MAP[src] + p[len(src):]
            break
    if "\\" in p:
        p = p.replace("\\", "/")
    return p


def init_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS track_fingerprints (
            rating_key      TEXT PRIMARY KEY,
            fingerprint     TEXT,
            fp_duration     REAL,
            acoustid        TEXT,
            recording_mbid  TEXT,
            error           TEXT,
            fp_at           TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()


def get_unfingerprinted(conn):
    rows = conn.execute("""
        SELECT rating_key, title FROM tracks
        WHERE rating_key NOT IN (
            SELECT rating_key FROM track_fingerprints WHERE error IS NULL
        )
        ORDER BY rating_key
    """).fetchall()
    return rows


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    print("MusicMind for Plex - Acoustic Fingerprinting")
    print("=" * 50)
    print("Connecting to Plex...")
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    print(f"Connected to: {plex.friendlyName}\n")

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")
    init_table(conn)

    rows = get_unfingerprinted(conn)
    if limit:
        rows = rows[:limit]
    total = len(rows)
    print(f"Tracks to fingerprint: {total}\n")
    if total == 0:
        print("Nothing to do — every track already has a fingerprint.")
        conn.close()
        return

    ok = 0
    errors = 0
    start = time.time()

    for i, (rk, title) in enumerate(rows, 1):
        try:
            try:
                item = plex.fetchItem(int(rk))
            except Exception:
                time.sleep(15)  # one retry on transient Plex hiccup
                item = plex.fetchItem(int(rk))

            filepath = translate_path(item.media[0].parts[0].file)

            result = subprocess.run(
                [FPCALC, "-json", filepath],
                capture_output=True, text=True, timeout=60
            )
            fp = json.loads(result.stdout)

            conn.execute("""
                INSERT OR REPLACE INTO track_fingerprints
                    (rating_key, fingerprint, fp_duration, error)
                VALUES (?,?,?,NULL)
            """, (rk, fp.get("fingerprint"), fp.get("duration")))
            conn.commit()
            ok += 1

            elapsed = time.time() - start
            eta_m = (elapsed / i) * (total - i) / 60
            print(f"[{i}/{total}] OK    {title}  (ETA {eta_m:.1f}m)")

        except Exception as e:
            conn.execute("""
                INSERT OR REPLACE INTO track_fingerprints (rating_key, error)
                VALUES (?,?)
            """, (rk, str(e)))
            conn.commit()
            errors += 1
            print(f"[{i}/{total}] ERROR {title}: {str(e)[:80]}")

    conn.close()
    print("\n" + "=" * 50)
    print(f"Done. {ok} fingerprinted, {errors} errors.")
    print("=" * 50)


if __name__ == "__main__":
    main()

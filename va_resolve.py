#!/usr/bin/env python3.12
"""
MusicMind for Plex - Various Artists Resolution (production)

Resolves "Various Artists" compilation tracks to their real performer
using acoustic fingerprinting (Chromaprint/fpcalc) + AcoustID lookup,
instead of unreliable title/artist text matching.

Design proven July 9, 2026 (va_test.py, 28/30 = 93% accuracy on a
random sample of real compilation tracks). This is the production,
resumable, audit-tracked version, built on the same skeleton as
vi_reverify.py: busy_timeout, PATH_MAP-aware file reads, one retry on
transient Plex API errors, resumable via an audit table so it can be
safely interrupted and rerun.

Usage:
    python3.12 va_resolve.py              # full run, resumable
    python3.12 va_resolve.py --limit 30   # test on a small sample first
"""
import sys
import os
import json
import time
import sqlite3
import subprocess
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PLEX_URL, PLEX_TOKEN, DB_PATH, ACOUSTID_KEY

try:
    from config import PATH_MAP
except ImportError:
    PATH_MAP = {}

import requests
from plexapi.server import PlexServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FPCALC = os.path.join(BASE_DIR, "bin", "fpcalc")
SCORE_FLOOR = 0.90
PLACEHOLDER_ARTISTS = ("Various Artists", "VA", "Unknown Artist")


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
        CREATE TABLE IF NOT EXISTS va_results (
            rating_key      TEXT PRIMARY KEY,
            title           TEXT,
            chosen_artist   TEXT,
            confidence      TEXT,
            votes_json      TEXT,
            acoustid        TEXT,
            recording_mbid  TEXT,
            fingerprint     TEXT,
            fp_duration     REAL,
            error           TEXT,
            analyzed_at     TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()


def resolve(fp_json, lib_title):
    """
    Looks up a fingerprint against AcoustID and picks the most likely
    real artist. Prefers plurality among recordings whose title matches
    the library's title exactly; falls back to overall plurality.
    Returns (artist_or_None, confidence_str, votes_dict, acoustid, mbid).
    """
    r = requests.post("https://api.acoustid.org/v2/lookup", data={
        "client": ACOUSTID_KEY, "meta": "recordings",
        "duration": int(fp_json["duration"]),
        "fingerprint": fp_json["fingerprint"],
    }, timeout=30).json()

    if r.get("status") != "ok" or not r.get("results"):
        return None, "no_results", None, None, None

    top = max(r["results"], key=lambda x: x.get("score", 0))
    if top.get("score", 0) < SCORE_FLOOR:
        return None, f"low_score:{top.get('score'):.2f}", None, top.get("id"), None

    recs = top.get("recordings") or []
    if not recs:
        return None, "no_recordings", None, top.get("id"), None

    votes = Counter()
    title_votes = Counter()
    lt = lib_title.strip().lower()
    mbid_by_artist = {}
    for rec in recs:
        artists = ", ".join(a["name"] for a in rec.get("artists", []) or [])
        if not artists:
            continue
        votes[artists] += 1
        mbid_by_artist.setdefault(artists, rec.get("id"))
        if rec.get("title", "").strip().lower() == lt:
            title_votes[artists] += 1

    if not votes:
        return None, "no_artists", None, top.get("id"), None

    pool = title_votes or votes
    chosen, count = pool.most_common(1)[0]
    confidence = "HIGH" if count / sum(pool.values()) > 0.5 else "REVIEW"
    return chosen, confidence, dict(votes), top.get("id"), mbid_by_artist.get(chosen)


def get_unresolved(conn):
    """
    Found real (July 2026): PLACEHOLDER_ARTISTS only recognized known
    text placeholders ("Various Artists", "VA", "Unknown Artist") --
    a track with a genuinely EMPTY or NULL artist field (confirmed
    real: 8 tracks, e.g. a malformed rip where the artist tag never
    got populated at all) was never eligible for VA resolution at
    all, regardless of how many times this script ran -- fell
    through a real crack between normal tagging (needs a real artist
    string) and this mechanism (needed one of a few specific known
    placeholder strings). Now also treats empty string and NULL as
    resolvable, using the same proven fingerprint-based mechanism
    rather than guessing from title text.
    """
    placeholders = ",".join("?" for _ in PLACEHOLDER_ARTISTS)
    rows = conn.execute(f"""
        SELECT rating_key, title FROM tracks
        WHERE (artist IN ({placeholders}) OR artist = '' OR artist IS NULL)
          AND rating_key NOT IN (SELECT rating_key FROM va_results)
        ORDER BY rating_key
    """, PLACEHOLDER_ARTISTS).fetchall()
    return rows


def main():
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    print("MusicMind for Plex - Various Artists Resolution")
    print("=" * 50)
    print("Connecting to Plex...")
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    print(f"Connected to: {plex.friendlyName}\n")

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")
    init_table(conn)

    rows = get_unresolved(conn)
    if limit:
        rows = rows[:limit]
    total = len(rows)
    print(f"Tracks to resolve: {total}\n")
    if total == 0:
        print("Nothing to do — all placeholder-artist tracks already resolved.")
        conn.close()
        return

    counts = Counter()
    start = time.time()

    for i, (rk, title) in enumerate(rows, 1):
        try:
            try:
                item = plex.fetchItem(int(rk))
            except Exception:
                time.sleep(15)  # one retry on transient Plex hiccup
                item = plex.fetchItem(int(rk))

            filepath = translate_path(item.media[0].parts[0].file)

            fp_raw = subprocess.run(
                [FPCALC, "-json", filepath],
                capture_output=True, text=True, timeout=60
            ).stdout
            fp = json.loads(fp_raw)

            artist, confidence, votes, acoustid, mbid = resolve(fp, title)

            conn.execute("""
                INSERT OR REPLACE INTO va_results
                    (rating_key, title, chosen_artist, confidence, votes_json,
                     acoustid, recording_mbid, fingerprint, fp_duration, error)
                VALUES (?,?,?,?,?,?,?,?,?,NULL)
            """, (rk, title, artist, confidence,
                  json.dumps(votes) if votes else None,
                  acoustid, mbid, fp.get("fingerprint"), fp.get("duration")))

            if artist and confidence == "HIGH":
                conn.execute(
                    "UPDATE tracks SET real_artist = ? WHERE rating_key = ?",
                    (artist, rk)
                )
            conn.commit()

            counts[confidence] += 1
            elapsed = time.time() - start
            eta_h = (elapsed / i) * (total - i) / 3600
            label = artist or "—"
            print(f"[{i}/{total}] {confidence:<14} {label}  |  {title}  (ETA {eta_h:.1f}h)")

        except Exception as e:
            conn.execute("""
                INSERT OR REPLACE INTO va_results (rating_key, title, error)
                VALUES (?,?,?)
            """, (rk, title, str(e)))
            conn.commit()
            counts["ERROR"] += 1
            print(f"[{i}/{total}] ERROR          {title}: {str(e)[:80]}")

        time.sleep(0.4)  # stay under AcoustID's 3 req/s rate limit

    conn.close()
    print("\n" + "=" * 50)
    print("Done.", " ".join(f"{k}={v}" for k, v in counts.items()))
    print("=" * 50)


if __name__ == "__main__":
    main()

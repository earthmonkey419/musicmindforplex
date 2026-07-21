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
import shutil
import tempfile

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
FFMPEG = shutil.which("ffmpeg")  # None if not installed — fallback becomes a graceful no-op


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


def run_fpcalc(filepath, timeout=60):
    """Runs fpcalc against a file, returning (fp_dict, error_str).
    error_str is None on success. Never raises — callers just check
    which of the two is set."""
    result = subprocess.run(
        [FPCALC, "-json", filepath],
        capture_output=True, text=True, timeout=timeout
    )
    if result.returncode != 0 or not result.stdout.strip():
        stderr_msg = result.stderr.strip() or "(no stderr output)"
        return None, f"fpcalc failed: {stderr_msg}"
    try:
        return json.loads(result.stdout), None
    except Exception as e:
        return None, f"fpcalc produced unparseable output: {e}"


def run_fpcalc_with_transcode_fallback(filepath, timeout=60):
    """Try fpcalc directly first (fast, works for the vast majority of
    files). If that fails, transcode through ffmpeg to a clean temp
    copy and retry once before giving up.

    Found July 2026: a small number of otherwise-valid MP3s (playable
    fine in Plex, valid ID3 tags, not actually corrupt) trip fpcalc's
    bundled strict decoder with "Invalid data found when processing
    input" / "Header missing" — a malformed frame deep in the audio
    stream that more forgiving players silently skip past. Confirmed
    via direct testing: a stream-copy re-mux does NOT fix this (same
    error), but a full re-encode through ffmpeg's libmp3lame encoder
    does — it has to fully decode the audio to write the new file,
    which is exactly the more-tolerant decode path Plex itself uses.

    Returns (fp_dict, error_str, used_fallback: bool).
    """
    fp, err = run_fpcalc(filepath, timeout)
    if fp is not None:
        return fp, None, False

    if not FFMPEG:
        # No ffmpeg available in this environment — can't attempt the
        # fallback, just return the original error.
        return None, err, False

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name

        transcode = subprocess.run(
            [FFMPEG, "-y", "-err_detect", "ignore_err",
             "-i", filepath, "-acodec", "libmp3lame", "-q:a", "2", tmp_path],
            capture_output=True, text=True, timeout=timeout
        )
        if transcode.returncode != 0 or not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
            return None, f"{err} (transcode fallback also failed: {transcode.stderr.strip()[-300:]})", False

        fp2, err2 = run_fpcalc(tmp_path, timeout)
        if fp2 is not None:
            return fp2, None, True
        return None, f"{err} (transcode fallback also failed: {err2})", False
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


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

            fp, fp_err, used_fallback = run_fpcalc_with_transcode_fallback(filepath)
            if fp is None:
                raise RuntimeError(fp_err)

            conn.execute("""
                INSERT OR REPLACE INTO track_fingerprints
                    (rating_key, fingerprint, fp_duration, error)
                VALUES (?,?,?,NULL)
            """, (rk, fp.get("fingerprint"), fp.get("duration")))
            conn.commit()
            ok += 1

            elapsed = time.time() - start
            eta_m = (elapsed / i) * (total - i) / 60
            fallback_flag = " [transcode fallback]" if used_fallback else ""
            print(f"[{i}/{total}] OK    {title}{fallback_flag}  (ETA {eta_m:.1f}m)")

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

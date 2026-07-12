#!/usr/bin/env python3
"""
MusicMind for Plex - Synapse: Sonic Similarity Audio Analysis

Analyzes real audio files via Essentia to extract tempo, key, and
danceability, storing results in track_audio_features. This is a
standalone script, deliberately NOT part of ingest.py or Full Sync —
full-library analysis takes days, not minutes, and must never block
setup for new users.

Modes:
  --count              Walk the library, print file format breakdown. No analysis.
  --estimate           Analyze 3-5 real sample tracks live, project total time. No writes.
  --limit N            Real run, but capped to N tracks. Safe for testing.
  (no flag)            Full real run. Resumable — skips already-analyzed tracks.

Requires: essentia (sudo python3.12 -m pip install essentia --break-system-packages)
NOTE: on Synology DSM, sudo pip installs often land with permissions
that block the normal user from reading them. If imports fail with a
namespace-package-looking error, check:
    sudo chown -R earthmonkey:users /path/to/site-packages/PACKAGE
    sudo chmod -R u+rX /path/to/site-packages/PACKAGE
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqlite3
import time
from collections import Counter
from datetime import datetime
from plexapi.server import PlexServer
from config import PLEX_URL, PLEX_TOKEN, MUSIC_LIB, DB_PATH

# --- Path translation (Plex host paths -> local paths) -----------------
# Needed when Plex runs on a different OS/machine than MusicMind
# (e.g. Plex on Windows + MusicMind in WSL or Docker). Configure
# PATH_MAP in config.py; longest prefix wins; backslashes converted.
try:
    from config import PATH_MAP
except ImportError:
    PATH_MAP = {}

def translate_path(p):
    if not p:
        return p
    for src in sorted(PATH_MAP, key=len, reverse=True):
        if p.startswith(src):
            p = PATH_MAP[src] + p[len(src):]
            break
    if "\\" in p:
        p = p.replace("\\", "/")
    return p


# Confirmed per-track timing from live testing on reference hardware —
# used only as a rough fallback label, NOT for real estimates. Real
# estimates should always come from --estimate's live sample, since
# hardware varies significantly.
REFERENCE_MP3_SECONDS  = 13.6
REFERENCE_FLAC_SECONDS = 22.3


def init_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS track_audio_features (
            rating_key    TEXT PRIMARY KEY,
            bpm           REAL,
            key           TEXT,
            scale         TEXT,
            key_strength  REAL,
            danceability  REAL,
            analyzed_at   TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS synapse_errors (
            rating_key    TEXT PRIMARY KEY,
            filepath      TEXT,
            error         TEXT,
            failed_at     TEXT
        )
    """)
    conn.commit()


def get_plex_tracks(plex):
    """Yields (rating_key, file_path) for every track with a real file."""
    music = plex.library.section(MUSIC_LIB)
    for artist in music.searchArtists():
        for album in artist.albums():
            for track in album.tracks():
                for media in track.media:
                    for part in media.parts:
                        if part.file:
                            yield str(track.ratingKey), translate_path(part.file)


def count_formats(plex):
    print("Walking library to count file formats...\n")
    formats = Counter()
    total = 0
    for rating_key, filepath in get_plex_tracks(plex):
        ext = filepath.lower().rsplit('.', 1)[-1] if '.' in filepath else 'unknown'
        formats[ext] += 1
        total += 1
        if total % 2000 == 0:
            print(f"  {total} files counted...")

    print(f"\n{'='*40}")
    print(f"Total files: {total}")
    print(f"{'='*40}")
    for fmt, n in formats.most_common():
        pct = (n / total) * 100 if total else 0
        print(f"  {fmt}: {n} ({pct:.1f}%)")
    print()
    return formats, total


ANALYSIS_TIMEOUT_SECONDS = 90  # generous — normal tracks take 8-25s;
                                # a file needing longer than this is
                                # treated as broken/hung, not slow.


# Realistic BPM range — anything outside this is almost certainly a
# beat-tracking failure (e.g. silence, pure noise, no rhythmic content
# at all), not a genuine tempo. Confirmed via real data: 11 tracks
# titled "[silence]" all produced an identical bogus 738 BPM reading.
MIN_REALISTIC_BPM = 40
MAX_REALISTIC_BPM = 250


def _analyze_one_impl(filepath, result_queue):
    """Runs in a separate process so a hanging file can be killed
    without taking down the whole batch job."""
    try:
        import essentia
        essentia.log.infoActive = False
        essentia.log.warningActive = False
        import essentia.standard as es

        audio = es.MonoLoader(filename=filepath)()

        rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
        bpm, beats, beats_confidence, _, beats_intervals = rhythm_extractor(audio)

        if not (MIN_REALISTIC_BPM <= bpm <= MAX_REALISTIC_BPM):
            raise ValueError(
                f"Implausible BPM ({bpm:.1f}) — likely no rhythmic content "
                f"in this file (e.g. silence, noise, spoken word). Flagged "
                f"for manual review rather than stored as valid data."
            )

        key_extractor = es.KeyExtractor()
        key, scale, key_strength = key_extractor(audio)

        danceability_extractor = es.Danceability()
        dance_value, dance_dfa = danceability_extractor(audio)

        result_queue.put(('ok', {
            'bpm': float(bpm),
            'key': key,
            'scale': scale,
            'key_strength': float(key_strength),
            'danceability': float(dance_value),
        }))
    except Exception as e:
        result_queue.put(('error', str(e)))


def analyze_one(filepath, timeout=ANALYSIS_TIMEOUT_SECONDS):
    """Analyzes one file with a hard timeout. A file that hangs (rather
    than cleanly erroring) will be forcibly killed after `timeout`
    seconds and reported as a failure — protects a multi-day unattended
    run from stalling forever on one bad file."""
    import multiprocessing

    result_queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=_analyze_one_impl, args=(filepath, result_queue))
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join(timeout=5)
        if proc.is_alive():
            proc.kill()
        raise TimeoutError(f"Analysis exceeded {timeout}s — file likely corrupt or unreadable")

    if result_queue.empty():
        raise RuntimeError("Analysis process exited without a result (crashed)")

    status, payload = result_queue.get()
    if status == 'error':
        raise RuntimeError(payload)
    return payload


def estimate(plex, samples_per_format=2, max_candidates_per_format=8):
    print("Running live estimate — analyzing real sample tracks on this hardware...\n")

    formats, total_files = count_formats(plex)
    if total_files == 0:
        print("No files found. Cannot estimate.")
        return

    # Collect several CANDIDATE files per top format, not just one —
    # so a single corrupted file doesn't wipe out that format's timing.
    top_formats = [f for f, _ in formats.most_common(3)]
    candidates = {f: [] for f in top_formats}

    for rating_key, filepath in get_plex_tracks(plex):
        ext = filepath.lower().rsplit('.', 1)[-1] if '.' in filepath else 'unknown'
        if ext in candidates and len(candidates[ext]) < max_candidates_per_format:
            candidates[ext].append(filepath)
        if all(len(v) >= max_candidates_per_format for v in candidates.values()):
            break

    if not any(candidates.values()):
        print("Could not find sample files to time. Cannot estimate.")
        return

    format_timings = {}
    for ext, filepaths in candidates.items():
        successes = 0
        print(f"Timing {ext} samples...")
        for filepath in filepaths:
            if successes >= samples_per_format:
                break
            try:
                t_start = time.time()
                analyze_one(filepath)
                elapsed = time.time() - t_start
                format_timings.setdefault(ext, []).append(elapsed)
                print(f"  {ext}: {elapsed:.1f}s  ({os.path.basename(filepath)})")
                successes += 1
            except Exception as e:
                print(f"  {ext}: FAILED ({os.path.basename(filepath)}) — {e} — retrying with another file...")
        if successes == 0:
            print(f"  {ext}: all {len(filepaths)} candidate samples failed — no timing available for this format")
        print()

    if not format_timings:
        print("All sample analyses failed for every format. Cannot estimate.")
        return

    # Weighted average based on actual format distribution in the library
    avg_per_format = {ext: sum(times) / len(times) for ext, times in format_timings.items()}
    fallback_avg = sum(avg_per_format.values()) / len(avg_per_format)

    weighted_total_seconds = 0
    for fmt, count in formats.items():
        per_track = avg_per_format.get(fmt, fallback_avg)
        weighted_total_seconds += per_track * count

    hours = weighted_total_seconds / 3600
    days = hours / 24

    print(f"{'='*40}")
    print("ESTIMATE (based on live timing on THIS hardware)")
    print(f"{'='*40}")
    for fmt, avg in avg_per_format.items():
        n = len(format_timings[fmt])
        print(f"  {fmt}: ~{avg:.1f}s/track (measured, {n} sample{'s' if n != 1 else ''})")
    unmeasured = [f for f in formats if f not in avg_per_format]
    if unmeasured:
        print(f"  (using fallback average for: {', '.join(unmeasured)} — no successful sample)")
    print(f"\nTotal files to analyze: {total_files}")
    print(f"Estimated total time: {hours:.1f} hours (~{days:.1f} days)")
    print("This is a one-time job. Safe to run in the background, resumable.")
    print(f"{'='*40}\n")


def get_unanalyzed_tracks(conn, plex, limit=None):
    already_done = set(row[0] for row in conn.execute(
        "SELECT rating_key FROM track_audio_features"
    ).fetchall())
    already_failed = set(row[0] for row in conn.execute(
        "SELECT rating_key FROM synapse_errors"
    ).fetchall())
    skip = already_done | already_failed

    to_process = []
    for rating_key, filepath in get_plex_tracks(plex):
        if rating_key in skip:
            continue
        to_process.append((rating_key, filepath))
        if limit and len(to_process) >= limit:
            break

    return to_process


def _write_with_retry(conn, sql, params, max_attempts=5, base_delay=0.5):
    """
    Executes a write, retrying with short backoff if SQLite reports
    "database is locked" — a transient error that happens when Full
    Sync (running every ~2 hours) is writing to the same database file
    at the same moment. This is NOT a permanent failure and should not
    be treated like genuine file corruption.

    Returns True if the write eventually succeeded, False if it never
    did after all retries (a real, rare case worth logging, but still
    distinct from "this audio file is broken").
    """
    for attempt in range(1, max_attempts + 1):
        try:
            conn.execute(sql, params)
            conn.commit()
            return True
        except sqlite3.OperationalError as e:
            if 'database is locked' in str(e).lower() and attempt < max_attempts:
                time.sleep(base_delay * attempt)  # gentle linear backoff
                continue
            return False
    return False


def run_analysis(conn, plex, limit=None):
    print("MusicMind for Plex - Synapse Audio Analysis")
    print("=" * 40)

    if limit:
        print(f"LIMITED RUN — processing at most {limit} tracks\n")

    tracks = get_unanalyzed_tracks(conn, plex, limit=limit)
    total = len(tracks)
    print(f"Tracks to analyze: {total}\n")

    if total == 0:
        print("All tracks already analyzed!")
        return

    done = 0
    failed = 0
    t_run_start = time.time()

    for rating_key, filepath in tracks:
        try:
            features = analyze_one(filepath)
        except Exception as e:
            failed += 1
            print(f"  ⚠️ Failed: {os.path.basename(filepath)} — {e}")
            _write_with_retry(conn, """
                INSERT OR REPLACE INTO synapse_errors
                    (rating_key, filepath, error, failed_at)
                VALUES (?, ?, ?, ?)
            """, (rating_key, filepath, str(e), datetime.now().isoformat()))
            continue

        # Analysis succeeded — the write itself can still transiently
        # fail if Full Sync (which runs every ~2 hours) happens to be
        # writing to the same SQLite file at this exact moment. This is
        # NOT a real analysis failure, so it gets a short retry rather
        # than being logged to synapse_errors like a genuine failure —
        # confirmed this exact collision permanently excluded several
        # legitimate, healthy tracks before this fix.
        write_ok = _write_with_retry(conn, """
            INSERT OR REPLACE INTO track_audio_features
                (rating_key, bpm, key, scale, key_strength, danceability, analyzed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            rating_key,
            features['bpm'],
            features['key'],
            features['scale'],
            features['key_strength'],
            features['danceability'],
            datetime.now().isoformat()
        ))

        if write_ok:
            done += 1
        else:
            failed += 1
            print(f"  ⚠️ Failed after retries: {os.path.basename(filepath)} — database still locked")
            _write_with_retry(conn, """
                INSERT OR REPLACE INTO synapse_errors
                    (rating_key, filepath, error, failed_at)
                VALUES (?, ?, ?, ?)
            """, (rating_key, filepath, "database is locked (persisted after retries)", datetime.now().isoformat()))
            continue

        if (done + failed) % 25 == 0:
            elapsed = time.time() - t_run_start
            avg = elapsed / (done + failed)
            remaining = total - (done + failed)
            eta_hours = (avg * remaining) / 3600
            print(f"  {done + failed}/{total} processed ({done} ok, {failed} failed) — ETA: {eta_hours:.1f}h remaining")

    print(f"\nDone. {done} tracks analyzed, {failed} failed.")
    print(f"Database: {DB_PATH}")


LOCK_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'synapse.lock')


def is_synapse_process_alive(pid):
    """
    Checks whether `pid` is genuinely still a running synapse_analyze.py
    process — not just whether SOME process exists at that PID number.

    Uses /proc/<pid> existence rather than os.kill(pid, 0), because the
    latter raises PermissionError (a subclass of OSError) when the
    target process is owned by a different user (e.g. started via
    `sudo` as root, while this check runs as a regular user via the
    web app) — which was previously being silently treated the same
    as "process doesn't exist," incorrectly allowing a second run to
    start alongside a genuinely still-active one.

    Also verifies the process's actual command line still mentions
    synapse_analyze.py — protects against a stale lock file pointing
    at a PID that has since been reassigned by the OS to a completely
    unrelated process, which would otherwise be misreported as "still
    running."
    """
    try:
        pid = int(pid)
    except (ValueError, TypeError):
        return False

    proc_dir = f'/proc/{pid}'
    if not os.path.exists(proc_dir):
        return False

    try:
        with open(f'{proc_dir}/cmdline', 'rb') as f:
            cmdline = f.read().decode('utf-8', errors='ignore')
        return 'synapse_analyze.py' in cmdline
    except (OSError, IOError):
        # Process existed a moment ago but is gone now (race condition) —
        # treat as not alive.
        return False


def acquire_lock():
    """Prevents two real analysis runs from executing simultaneously.
    Returns True if lock acquired, False if another run is genuinely
    still active."""
    if os.path.exists(LOCK_FILE):
        with open(LOCK_FILE) as f:
            old_pid = f.read().strip()
        if is_synapse_process_alive(old_pid):
            return False  # still alive — genuine conflict
        # stale lock, process is gone (or was never really Synapse) — safe to overwrite

    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))
    return True


def release_lock():
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)


def main():
    count_mode = "--count" in sys.argv
    estimate_mode = "--estimate" in sys.argv
    limit = None
    if "--limit" in sys.argv:
        idx = sys.argv.index("--limit")
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])

    print("Connecting to Plex...")
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    print(f"Connected to: {plex.friendlyName}\n")

    conn = sqlite3.connect(DB_PATH, timeout=30)
    init_table(conn)

    if count_mode:
        count_formats(plex)
    elif estimate_mode:
        estimate(plex)
    else:
        # Real analysis run — writes to the database. Lock to prevent
        # two simultaneous runs (e.g. one started via terminal, one via
        # the web UI) from duplicating work and competing for CPU.
        if not acquire_lock():
            print("❌ Another Synapse analysis run is already in progress.")
            print("   Check with: ps aux | grep synapse_analyze")
            conn.close()
            sys.exit(1)
        try:
            run_analysis(conn, plex, limit=limit)
        finally:
            release_lock()

    conn.close()


if __name__ == "__main__":
    main()

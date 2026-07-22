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
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "3")  # silence TF/CUDA noise (no GPU on this NAS; CPU fallback is expected and harmless)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqlite3
import time
from collections import Counter
from datetime import datetime
from plexapi.server import PlexServer
from config import PLEX_URL, PLEX_TOKEN, MUSIC_LIB, DB_PATH
from config_check import check_config
check_config(PLEX_URL=PLEX_URL, PLEX_TOKEN=PLEX_TOKEN)

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


# --- VI (voice/instrumental) — merged in July 2026 -----------------
# Previously a separate script (vi_reverify.py) that re-walked the
# entire Plex library and re-decoded every audio file AGAIN, purely
# to run one more classifier — genuinely redundant work against what
# this script already does per track. Merged the ORCHESTRATION layer
# (one Plex walk, one lock, one priority queue, one subprocess/timeout
# wrapper, one combined per-track worker) while deliberately keeping
# the audio DECODE separate for each analysis. Verified via direct
# testing (real click track at a known 120 BPM ground truth, in-memory
# array fed straight to the extractors — not a file round-trip) that
# sharing a single 16kHz decode between both analyses measurably
# degrades Synapse's own accuracy: BPM 120.03->110.24, key A minor->
# C minor, danceability 8.465->60.736. Not a theoretical concern —
# a real, confirmed regression avoided by keeping two loads.
VI_MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "models", "voice_instrumental-musicnn-msd-1.pb")
VI_THRESHOLD = 0.55

def _load_audio_with_transcode_fallback(filepath, sample_rate, MonoLoader):
    """Try loading directly first (fast, works for the vast majority of
    files). If essentia's MonoLoader fails, transcode through ffmpeg
    to a clean temp copy and retry once before giving up -- the exact
    same proven pattern from fingerprint_tracks.py's
    run_fpcalc_with_transcode_fallback(), confirmed there to recover
    9 of 11 real production failures (found July 2026: a full
    re-encode through ffmpeg's libmp3lame is what works -- a stream-
    copy re-mux does NOT fix these files, it has to fully decode the
    audio to write the new file, the same more-tolerant path Plex
    itself uses).

    Returns (audio_array, used_fallback: bool). Raises an error that
    ALWAYS states which stage actually failed (direct load / ffmpeg
    missing / transcode itself / retry after a successful transcode)
    -- found July 2026 that always re-raising just the original error
    made it impossible to tell from logs alone whether the fallback
    was ever actually attempted, let alone why it didn't help. That
    ambiguity is exactly what this fixes.
    """
    import shutil, subprocess, tempfile
    try:
        return MonoLoader(filename=filepath, sampleRate=sample_rate)(), False
    except Exception as first_err:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise RuntimeError(f"{first_err} (fallback not attempted: ffmpeg not found on PATH)")

        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                tmp_path = tmp.name
            transcode = subprocess.run(
                [ffmpeg, "-y", "-err_detect", "ignore_err",
                 "-i", filepath, "-acodec", "libmp3lame", "-q:a", "2", tmp_path],
                capture_output=True, text=True, timeout=60
            )
            if transcode.returncode != 0 or not os.path.exists(tmp_path) or os.path.getsize(tmp_path) == 0:
                stderr_tail = (transcode.stderr or "")[-300:]
                raise RuntimeError(f"{first_err} (transcode fallback also failed: {stderr_tail})")
            try:
                return MonoLoader(filename=tmp_path, sampleRate=sample_rate)(), True
            except Exception as retry_err:
                raise RuntimeError(f"{first_err} (transcode succeeded but retry still failed: {retry_err})")
        finally:
            if tmp_path and os.path.exists(tmp_path):
                os.remove(tmp_path)


def vi_model_available():
    """Whether the (deliberately never auto-downloaded, CC BY-NC-SA
    licensed) VI model file has actually been placed on disk. essentia
    itself is unconditionally required already (Synapse depends on it
    too) -- this is the ONLY thing that's genuinely optional here."""
    return os.path.exists(VI_MODEL)


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
    conn.execute("""
        CREATE TABLE IF NOT EXISTS vi_results (
            rating_key  TEXT PRIMARY KEY,
            title       TEXT, artist TEXT,
            old_tag     INTEGER,
            p_inst      REAL, p_voice REAL,
            verdict     TEXT,
            tag_changed INTEGER,
            error       TEXT,
            analyzed_at TEXT
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


def _analyze_one_impl(filepath, result_queue, needs_synapse, needs_vi):
    """Runs in a separate process so a hanging file can be killed
    without taking down the whole batch job. Does whichever of
    Synapse/VI this particular track actually still needs -- most
    tracks need both together (the common, efficient case this merge
    is for), but resuming a partially-migrated library means some
    tracks only need one or the other.

    Each analysis has its OWN try/except, independent of the other --
    a Synapse-specific failure (e.g. the implausible-BPM check below)
    doesn't prevent VI from still succeeding on the same file, and
    vice versa. They share this one subprocess/timeout wrapper, but
    their success/failure is otherwise fully independent.

    Puts a dict on the queue: {'synapse': (status, payload) or None,
    'vi': (status, payload) or None} -- None means "wasn't requested
    for this track," not "failed."
    """
    result = {'synapse': None, 'vi': None}

    import essentia
    essentia.log.infoActive = False
    essentia.log.warningActive = False
    import essentia.standard as es

    if needs_synapse:
        try:
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

            result['synapse'] = ('ok', {
                'bpm': float(bpm),
                'key': key,
                'scale': scale,
                'key_strength': float(key_strength),
                'danceability': float(dance_value),
            })
        except Exception as e:
            result['synapse'] = ('error', str(e))

    if needs_vi:
        try:
            import numpy as np
            from essentia.standard import MonoLoader, TensorflowPredictMusiCNN
            # Deliberately a SEPARATE decode at VI's own required rate
            # (16000Hz) -- confirmed via direct testing that sharing a
            # single decode with Synapse's extractors above measurably
            # degrades their accuracy. Small redundant cost, real
            # accuracy protected.
            vi_audio, _used_fallback = _load_audio_with_transcode_fallback(filepath, 16000, MonoLoader)
            model = TensorflowPredictMusiCNN(graphFilename=VI_MODEL, output="model/Sigmoid")
            preds = np.atleast_2d(model(vi_audio))
            if preds.size == 0:
                raise ValueError("track too short for any analysis window — no patches produced")
            p_inst, p_voice = (float(x) for x in np.mean(preds, axis=0))
            result['vi'] = ('ok', {'p_inst': p_inst, 'p_voice': p_voice})
        except Exception as e:
            result['vi'] = ('error', str(e))

    result_queue.put(result)


def analyze_one(filepath, needs_synapse=True, needs_vi=False, timeout=ANALYSIS_TIMEOUT_SECONDS):
    """Analyzes one file with a hard timeout, running whichever of
    Synapse/VI is requested. A file that hangs (rather than cleanly
    erroring) will be forcibly killed after `timeout` seconds —
    protects a multi-day unattended run from stalling forever on one
    bad file. The timeout applies to BOTH analyses together, since
    they share one subprocess.

    Always returns a dict {'synapse': (status, payload) or None,
    'vi': (status, payload) or None} -- does NOT raise on a per-
    analysis failure, since one can fail while the other succeeds.
    Callers inspect each key independently.
    """
    import multiprocessing

    result_queue = multiprocessing.Queue()
    proc = multiprocessing.Process(
        target=_analyze_one_impl,
        args=(filepath, result_queue, needs_synapse, needs_vi)
    )
    proc.start()
    proc.join(timeout=timeout)

    if proc.is_alive():
        proc.terminate()
        proc.join(timeout=5)
        if proc.is_alive():
            proc.kill()
        msg = f"Analysis exceeded {timeout}s — file likely corrupt or unreadable"
        return {
            'synapse': ('error', msg) if needs_synapse else None,
            'vi': ('error', msg) if needs_vi else None,
        }

    if result_queue.empty():
        msg = "Analysis process exited without a result (crashed)"
        return {
            'synapse': ('error', msg) if needs_synapse else None,
            'vi': ('error', msg) if needs_vi else None,
        }

    return result_queue.get()


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
            # estimate mode times Synapse only (needs_synapse=True is
            # the default) -- VI's cost is a separate, optional add-on,
            # not part of the core "how long will this take" estimate.
            t_start = time.time()
            result = analyze_one(filepath)
            elapsed = time.time() - t_start
            status, payload = result['synapse']
            if status == 'ok':
                format_timings.setdefault(ext, []).append(elapsed)
                print(f"  {ext}: {elapsed:.1f}s  ({os.path.basename(filepath)})")
                successes += 1
            else:
                print(f"  {ext}: FAILED ({os.path.basename(filepath)}) — {payload} — retrying with another file...")
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
    """
    Returns tracks needing EITHER Synapse or VI (or both) -- most
    tracks need both together in the common case, but resuming a
    partially-migrated library means some only need one.

    Simplification vs. the original standalone vi_reverify.py: that
    script prioritized "tagged-instrumental first, then NULL, then
    tagged-vocal" for its own runs. This merged version processes in
    Plex's natural walk order instead (matching Synapse's existing,
    proven convention) -- now that both analyses happen together per
    track in one pass, VI-specific prioritization matters less than
    it did as a standalone concern.

    Returns (rating_key, filepath, needs_synapse, needs_vi, title,
    artist, old_tag) tuples.
    """
    already_synapse_done = set(row[0] for row in conn.execute(
        "SELECT rating_key FROM track_audio_features"
    ).fetchall())
    already_synapse_failed = set(row[0] for row in conn.execute(
        "SELECT rating_key FROM synapse_errors"
    ).fetchall())
    synapse_skip = already_synapse_done | already_synapse_failed

    vi_available = vi_model_available()
    already_vi_done = set()
    if vi_available:
        already_vi_done = set(row[0] for row in conn.execute(
            "SELECT rating_key FROM vi_results"
        ).fetchall())

    track_meta = {row[0]: (row[1], row[2], row[3]) for row in conn.execute(
        "SELECT rating_key, title, COALESCE(real_artist, artist), is_instrumental FROM tracks"
    ).fetchall()}

    to_process = []
    for rating_key, filepath in get_plex_tracks(plex):
        needs_synapse = rating_key not in synapse_skip
        needs_vi = vi_available and rating_key not in already_vi_done
        if not needs_synapse and not needs_vi:
            continue
        title, artist, old_tag = track_meta.get(rating_key, (None, None, None))
        to_process.append((rating_key, filepath, needs_synapse, needs_vi, title, artist, old_tag))
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
    print("MusicMind for Plex - Synapse + VI Audio Analysis")
    print("=" * 40)

    vi_available = vi_model_available()
    print(f"VI (voice/instrumental) model: {'found — will run alongside Synapse' if vi_available else 'not found — Synapse only (see models/ in the repo README to enable VI)'}\n")

    if limit:
        print(f"LIMITED RUN — processing at most {limit} tracks\n")

    tracks = get_unanalyzed_tracks(conn, plex, limit=limit)
    total = len(tracks)
    print(f"Tracks to analyze: {total}\n")

    if total == 0:
        print("All tracks already analyzed!")
        return

    synapse_done = synapse_failed = 0
    vi_done = vi_failed = 0
    processed = 0
    t_run_start = time.time()

    for rating_key, filepath, needs_synapse, needs_vi, title, artist, old_tag in tracks:
        result = analyze_one(filepath, needs_synapse=needs_synapse, needs_vi=needs_vi)
        processed += 1

        # --- Synapse half — same retry/error-table logic as before,
        # just scoped to result['synapse'] instead of a bare exception.
        if needs_synapse:
            status, payload = result['synapse']
            if status == 'error':
                synapse_failed += 1
                print(f"  ⚠️ Synapse failed: {os.path.basename(filepath)} — {payload}")
                _write_with_retry(conn, """
                    INSERT OR REPLACE INTO synapse_errors
                        (rating_key, filepath, error, failed_at)
                    VALUES (?, ?, ?, ?)
                """, (rating_key, filepath, str(payload), datetime.now().isoformat()))
            else:
                write_ok = _write_with_retry(conn, """
                    INSERT OR REPLACE INTO track_audio_features
                        (rating_key, bpm, key, scale, key_strength, danceability, analyzed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    rating_key, payload['bpm'], payload['key'], payload['scale'],
                    payload['key_strength'], payload['danceability'], datetime.now().isoformat()
                ))
                if write_ok:
                    synapse_done += 1
                else:
                    synapse_failed += 1
                    print(f"  ⚠️ Synapse write failed after retries: {os.path.basename(filepath)} — database still locked")
                    _write_with_retry(conn, """
                        INSERT OR REPLACE INTO synapse_errors
                            (rating_key, filepath, error, failed_at)
                        VALUES (?, ?, ?, ?)
                    """, (rating_key, filepath, "database is locked (persisted after retries)", datetime.now().isoformat()))

        # --- VI half — mirrors vi_reverify.py's original verdict logic
        # (threshold comparison, is_instrumental flip, vi_results audit
        # row), just scoped to result['vi'] and reusing the SAME decode
        # already produced by _analyze_one_impl for this track.
        if needs_vi:
            status, payload = result['vi']
            verdict = "ERROR"; changed = 0; err = None
            p_inst = p_voice = None
            if status == 'ok':
                p_inst, p_voice = payload['p_inst'], payload['p_voice']
                if p_voice >= VI_THRESHOLD:
                    verdict = "VOICE"
                    if old_tag != 0:
                        _write_with_retry(conn, "UPDATE tracks SET is_instrumental = 0 WHERE rating_key = ?", (rating_key,))
                        changed = 1
                elif p_inst >= VI_THRESHOLD:
                    verdict = "INSTRUMENTAL"
                    if old_tag != 1:
                        _write_with_retry(conn, "UPDATE tracks SET is_instrumental = 1 WHERE rating_key = ?", (rating_key,))
                        changed = 1
                else:
                    verdict = "AMBIGUOUS"
                vi_done += 1
            else:
                err = str(payload)[:300]
                vi_failed += 1
                print(f"  ⚠️ VI failed: {os.path.basename(filepath)} — {err}")

            _write_with_retry(conn, """
                INSERT OR REPLACE INTO vi_results
                    (rating_key, title, artist, old_tag, p_inst, p_voice, verdict, tag_changed, error, analyzed_at)
                VALUES (?,?,?,?,?,?,?,?,?,datetime('now'))
            """, (rating_key, title, artist, old_tag, p_inst, p_voice, verdict, changed, err))

        if processed % 25 == 0:
            elapsed = time.time() - t_run_start
            avg = elapsed / processed
            remaining = total - processed
            eta_hours = (avg * remaining) / 3600
            print(f"  {processed}/{total} processed (synapse: {synapse_done} ok/{synapse_failed} failed, "
                  f"vi: {vi_done} ok/{vi_failed} failed) — ETA: {eta_hours:.1f}h remaining")

    print(f"\nDone. Synapse: {synapse_done} analyzed, {synapse_failed} failed."
          + (f" VI: {vi_done} analyzed, {vi_failed} failed." if vi_available else " VI: skipped (model not installed)."))
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

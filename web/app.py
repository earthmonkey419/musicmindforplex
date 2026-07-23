#!/usr/bin/env python3
"""
MusicMind for Plex - Flask Web UI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
from datetime import datetime
from brain import expand_prompt, classify_prompt, search_tracks, sequence_for_flow, create_playlist, PlexServer, PLEX_URL, PLEX_TOKEN, MUSIC_LIB, detect_instrumental_intent, extract_lastfm_dates, get_scrobbled_tracks_in_range, get_scrobbled_tracks_around_date, update_query_log_result_count, log_query, no_instrumental_data_exists, vi_capability_status, find_similar_by_track, find_similar_by_artist
from config import DB_PATH, BASE_DIR, LASTFM_KEY
try:
    from config import IS_MASTER
except ImportError:
    IS_MASTER = False  # not set in config.py — safe default

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', lastfm_enabled=bool(LASTFM_KEY), year=datetime.now().year,
                            vi_status=vi_capability_status())

@app.route('/onthisday', methods=['POST'])
def onthisday():
    """
    Zero-AI-cost complement to the typed lastfm: prefix. User picks a
    single date via a UI date picker; returns tracks scrobbled within
    an 8-day window centered on it (get_scrobbled_tracks_around_date
    already handles the window math). No OpenAI call involved at all —
    entirely deterministic, since the input is already an unambiguous
    ISO date, not natural language needing interpretation.
    """
    data = request.json
    target_date = data.get('date', '').strip()
    if not target_date:
        return jsonify({'error': 'No date provided'}), 400

    try:
        rating_keys = get_scrobbled_tracks_around_date(target_date, window_days=4)
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    filters = {
        **{
            'limit': int(data.get('limit', 30)),
            'max_per_artist': int(data.get('max_per_artist', 1)),
        },
        'lastfm_rating_keys': rating_keys,
    }

    tracks = search_tracks([], filters)

    if data.get('dj_ify'):
        tracks = sequence_for_flow(tracks)

    return jsonify({
        'tracks': tracks,
        'intent': 'lastfm_window',
        'search_term': f"{target_date} ± 4 days",
    })


@app.route('/based-on-search')
def based_on_search():
    """Autocomplete for the 'Based on:' box -- searches both track
    titles and artist names, clearly labeled by type, so the frontend
    knows which mode to use once the user picks a suggestion."""
    import sqlite3
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'results': []})

    conn = sqlite3.connect(DB_PATH)
    track_rows = conn.execute("""
        SELECT rating_key, title, COALESCE(real_artist, artist) as artist
        FROM tracks WHERE title LIKE ? LIMIT 8
    """, (f'%{q}%',)).fetchall()
    artist_rows = conn.execute("""
        SELECT DISTINCT COALESCE(real_artist, artist) as artist
        FROM tracks WHERE COALESCE(real_artist, artist) LIKE ? LIMIT 8
    """, (f'%{q}%',)).fetchall()
    conn.close()

    results = [{'type': 'track', 'rating_key': rk, 'label': f'{title} — {artist}'} for rk, title, artist in track_rows]
    results += [{'type': 'artist', 'value': a[0], 'label': f'{a[0]} (artist)'} for a in artist_rows]
    return jsonify({'results': results})


@app.route('/based-on', methods=['POST'])
def based_on():
    """The actual 'Based on:' results -- routes to track mode (local
    tag+Synapse blend, no AI) or artist mode (Last.fm real similarity
    data, AI only as a last-resort fallback) depending on what the
    user picked."""
    data = request.json
    seed_type = data.get('type')
    limit = int(data.get('limit', 30))
    max_per_artist = int(data.get('max_per_artist', 3))

    try:
        if seed_type == 'track':
            rating_key = data.get('rating_key')
            if not rating_key:
                return jsonify({'error': 'No track specified'}), 400
            results = find_similar_by_track(rating_key, limit=limit, max_per_artist=max_per_artist)
            # Found missing entirely (July 2026): the /based-on routes
            # were built after centralized logging and never wired
            # into it -- same class of gap as the original
            # title_search/artist_search issue, just for a brand new
            # code path. log_query() works standalone (no
            # classify_prompt needed), same pattern already used for
            # the lastfm: prefix path.
            log_id = log_query(prompt=f"[based-on:track] {data.get('seed_label', rating_key)}", intent='based_on_track')
            update_query_log_result_count(log_id, len(results), {'limit': limit, 'max_per_artist': max_per_artist})
            return jsonify({'tracks': results, 'mode': 'track'})
        elif seed_type == 'artist':
            artist = data.get('value')
            if not artist:
                return jsonify({'error': 'No artist specified'}), 400
            results, source = find_similar_by_artist(artist, limit=limit, max_per_artist=max_per_artist)
            log_id = log_query(prompt=f"[based-on:artist] {artist}", intent='based_on_artist')
            update_query_log_result_count(log_id, len(results), {'limit': limit, 'max_per_artist': max_per_artist, 'source': source})
            return jsonify({'tracks': results, 'mode': 'artist', 'source': source})
        else:
            return jsonify({'error': 'Unknown seed type'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/preview', methods=['POST'])
def preview():
    data = request.json
    prompt = data.get('prompt', '').strip()
    bucket_names = data.get('buckets') or None  # optional list of genre bucket names to narrow tag vocabulary
    strict_buckets = bool(bucket_names)  # confirmed default (July 2026): checking ANY bucket means strict genre-only vocabulary — proven 3/3 on production that this produces genuinely genre-coherent results, and lets the AI interpret the prompt's mood THROUGH the selected genre's own vocabulary rather than reaching for generic cross-genre mood words

    try:
        tags = []
        intent = 'mood'
        search_term = None
        detected_filters = {}
        classification = {}
        lastfm_rating_keys = None
        query_log_id = None

        # Explicit lastfm: prefix — bypasses normal mood/AI classification
        # entirely, since a date reference is unambiguous once flagged
        # this way and doesn't need the general-purpose classifier.
        # Logged directly (no OpenAI call happens on this path, so
        # there's no cost/token data — just makes the prompt visible
        # in query_log, same completeness goal as the classify-based
        # path below).
        if prompt.lower().startswith('lastfm:'):
            date_text = prompt[len('lastfm:'):].strip()
            dates = extract_lastfm_dates(date_text)
            lastfm_rating_keys = get_scrobbled_tracks_in_range(dates['start_date'], dates['end_date'])
            intent = 'lastfm_range'
            search_term = f"{dates['start_date']} to {dates['end_date']}"
            query_log_id = log_query(prompt=prompt, intent=intent)
        elif prompt:
            # Centralized logging (July 2026): classify_prompt() now
            # logs itself immediately on return — this is the ONE call
            # that runs for nearly every real prompt regardless of
            # eventual intent, closing the gap where title_search/
            # artist_search/filter_only prompts were never logged at
            # all (confirmed via two real examples: "Dance Dance",
            # "I love humanity"). expand_prompt() below, when it also
            # runs, appends onto this SAME row instead of creating a
            # duplicate — true combined cost across both API calls.
            classification, query_log_id = classify_prompt(prompt)
            intent      = classification.get('intent', 'mood')
            search_term = classification.get('title_search') or classification.get('artist_search')
            detected_filters = classification.get('filters', {}) or {}

            # Expand mood if there is a mood component
            mood = classification.get('mood')
            if mood and intent in ('mood', 'filter_only'):
                if intent == 'mood':
                    tags, query_log_id = expand_prompt(prompt, bucket_names, strict=strict_buckets, log_id=query_log_id)
                # for filter_only with no mood, skip expansion

        filters = {
            'unplayed':       data.get('unplayed', False),
            'genre':          data.get('genre') or None,
            'min_year':       int(data['min_year']) if data.get('min_year') else None,
            'max_year':       int(data['max_year']) if data.get('max_year') else None,
            'min_plays':      int(data['min_plays']) if data.get('min_plays') else detected_filters.get('min_plays'),
            'popularity_min': int(data['popularity_min']) if data.get('popularity_min') else detected_filters.get('popularity_min'),
            'max_plays':      int(data['max_plays']) if data.get('max_plays') else None,
            'limit':          int(data.get('limit', 30)),
            'max_per_artist': int(data.get('max_per_artist', 3)),
            'min_rating':     float(data['min_rating']) if data.get('min_rating') else None,
            'gender':         data.get('gender') or detected_filters.get('gender') or None,
            'country':        data.get('country') or detected_filters.get('country') or None,
            'era':            data.get('era') or detected_filters.get('era') or None,
            'instrumental':   1 if data.get('instrumental') else (detect_instrumental_intent(prompt) if prompt else None),
            'vocal_tolerance': float(data['vocal_tolerance']) if data.get('vocal_tolerance') else None,
            'bpm_min':        int(data['bpm_min']) if data.get('bpm_min') else None,
            'bpm_max':        int(data['bpm_max']) if data.get('bpm_max') else None,
            'danceability':   data.get('danceability') or None,
            'bucket_names':   bucket_names,
            'lastfm_rating_keys': lastfm_rating_keys,
            'title_search':   classification.get('title_search'),
            'artist_search':  classification.get('artist_search'),
            'year_search':    detected_filters.get('year') or (search_term if intent == 'year_search' else None),
            'intent':         intent,

        }
        tracks = search_tracks(tags, filters)
        update_query_log_result_count(query_log_id, len(tracks), filters)

        if data.get('dj_ify'):
            tracks = sequence_for_flow(tracks)

        response = {'tags': tags, 'tracks': tracks, 'intent': intent, 'search_term': search_term, 'detected_filters': detected_filters, 'dj_ified': bool(data.get('dj_ify'))}

        # Found via July 2026 fresh-install sanity check: checking
        # "Instrumental only" on an install with no VI data at all
        # (fresh v3-dev, model never downloaded) silently returned
        # zero results with no explanation. Distinguish that from
        # "genuinely nothing matches this specific query."
        if filters.get('instrumental') == 1 and len(tracks) == 0 and no_instrumental_data_exists():
            response['warning'] = ("No tracks have been analyzed for voice/instrumental content "
                                    "yet. Run VI verification from the Admin page (requires "
                                    "downloading the voice/instrumental model first — see the "
                                    "Admin page for the download link).")

        return jsonify(response)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create', methods=['POST'])
def create():
    data = request.json
    name = data.get('name', '').strip()
    rating_keys = data.get('rating_keys', [])
    prompt = data.get('prompt', '').strip() or None

    if not name:
        return jsonify({'error': 'No playlist name provided'}), 400
    if not rating_keys:
        return jsonify({'error': 'No tracks provided'}), 400

    try:
        count = create_playlist(name, rating_keys, prompt=prompt)
        return jsonify({'success': True, 'count': count, 'name': name})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

import subprocess
import threading

# Track running processes
running = {}

@app.route('/admin')
def admin():
    return render_template('admin.html', lastfm_enabled=bool(LASTFM_KEY), year=datetime.now().year)

@app.route('/run/synapse-full')
def run_synapse_full():
    """
    Dedicated route for Synapse's Full Run — genuinely different from
    every other script this app runs, since this one is expected to
    take DAYS, not seconds/minutes. Two important differences from the
    generic run_script() route:

    1. Uses start_new_session=True so the subprocess is fully detached
       from this Flask app's process group. If musicmind
       restarts (crash, manual restart, deploy), the analysis keeps
       running unaffected — previously, restarting the app silently
       killed the analysis too.

    2. Output goes to a log file, NOT a live SSE pipe. A pipe-based
       live stream assumes the browser tab (and the parent process)
       stays connected for the whole run, which isn't realistic for a
       multi-day job. Progress is checked via polling /synapse-status
       instead — see that route, which already reports analyzed count,
       error count, and seconds-since-last-write for stall detection.
    """
    if running.get('synapse_full_started_flag'):
        return jsonify({'error': 'Already started this session — check /synapse-status'}), 400

    lock_path = os.path.join(BASE_DIR, 'synapse.lock')
    if os.path.exists(lock_path):
        with open(lock_path) as f:
            existing_pid = f.read().strip()
        proc_dir = f'/proc/{existing_pid}'
        if os.path.exists(proc_dir):
            try:
                with open(f'{proc_dir}/cmdline', 'rb') as cf:
                    cmdline = cf.read().decode('utf-8', errors='ignore')
                if 'synapse_analyze.py' in cmdline:
                    return jsonify({'error': 'A Synapse run is already active'}), 400
            except (OSError, IOError):
                pass

    log_path = os.path.join(BASE_DIR, 'synapse_full_run.log')
    try:
        with open(log_path, 'a') as logfile:
            subprocess.Popen(
                ['python3.12', '-u', os.path.join(BASE_DIR, 'synapse_analyze.py')],
                stdout=logfile,
                stderr=subprocess.STDOUT,
                start_new_session=True,  # detach from this Flask process entirely
                cwd=BASE_DIR,
            )
        running['synapse_full_started_flag'] = True
        return jsonify({'message': 'Full analysis started. It will keep running even if the app restarts. Check /synapse-status for progress.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/synapse-full-log')
def synapse_full_log():
    """Returns the tail of the detached Full Run's log file, since its
    output no longer streams live to the browser."""
    log_path = os.path.join(BASE_DIR, 'synapse_full_run.log')
    if not os.path.exists(log_path):
        return jsonify({'log': '(no log yet — run has not started, or log file was cleared)'})
    try:
        with open(log_path, 'r', errors='ignore') as f:
            lines = f.readlines()
        tail = ''.join(lines[-100:])  # last 100 lines is plenty for a status check
        return jsonify({'log': tail})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/run/<script>')
def run_script(script):
    scripts = {
        'ingest':   os.path.join(BASE_DIR, 'musicmind_ingest.py'),
        'lastfm':   os.path.join(BASE_DIR, 'lastfm_sync.py') if LASTFM_KEY else None,
        'tagger':   os.path.join(BASE_DIR, 'plex_tag_tracks.py'),
        'context':  os.path.join(BASE_DIR, 'listening_context.py'),
        'mbenrich': os.path.join(BASE_DIR, 'mb_enrich_artists.py'),
        'aienrich': os.path.join(BASE_DIR, 'enrich_artists.py'),
        'synapse':  os.path.join(BASE_DIR, 'synapse_analyze.py'),
        'fingerprint':  os.path.join(BASE_DIR, 'fingerprint_tracks.py'),
        'copyforward':  os.path.join(BASE_DIR, 'copy_forward_analysis.py'),
        'dedup':        os.path.join(BASE_DIR, 'dedup_report.py'),
        'varesolve':    os.path.join(BASE_DIR, 'va_resolve.py'),
    }
    if script not in scripts:
        return jsonify({'error': 'Unknown script'}), 400
    if running.get(script):
        return jsonify({'error': 'Already running'}), 400

    def generate():
        running[script] = True
        try:
            proc = subprocess.Popen(
                ['python3.12', '-u', scripts[script]],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in proc.stdout:
                yield f"data: {line.rstrip()}\n\n"
            proc.wait()
            if proc.returncode == 0:
                yield "data: ✅ Done.\n\n"
            else:
                yield f"data: ❌ Error (exit code {proc.returncode})\n\n"
        except Exception as e:
            yield f"data: ❌ Exception: {e}\n\n"
        finally:
            running[script] = False
        yield "data: __DONE__\n\n"

    return app.response_class(generate(), mimetype='text/event-stream')


@app.route('/run/test/<test_id>')
def run_test(test_id):
    """
    Runs a predefined test command (script + args) and streams output.
    Separate from /run/<script> so Back Office's fixed script mapping
    is never at risk from test-specific argument handling.
    """
    test_scripts = {
        'mb_dry_run':     (os.path.join(BASE_DIR, 'mb_enrich_artists.py'), ['--test', '--limit', '3']),
        'mb_limited_run': (os.path.join(BASE_DIR, 'mb_enrich_artists.py'), ['--limit', '1']),
        'ai_dry_run':     (os.path.join(BASE_DIR, 'enrich_artists.py'),    ['--test', '--limit', '3']),
        'ai_limited_run': (os.path.join(BASE_DIR, 'enrich_artists.py'),    ['--limit', '1']),
    }
    if test_id not in test_scripts:
        return jsonify({'error': 'Unknown test'}), 400

    script_path, args = test_scripts[test_id]
    run_key = f"test_{test_id}"
    if running.get(run_key):
        return jsonify({'error': 'Already running'}), 400

    def generate():
        running[run_key] = True
        try:
            proc = subprocess.Popen(
                ['python3.12', '-u', script_path] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in proc.stdout:
                yield f"data: {line.rstrip()}\n\n"
            proc.wait()
            if proc.returncode == 0:
                yield "data: ✅ Test completed.\n\n"
            else:
                yield f"data: ❌ Error (exit code {proc.returncode})\n\n"
        except Exception as e:
            yield f"data: ❌ Exception: {e}\n\n"
        finally:
            running[run_key] = False
        yield "data: __DONE__\n\n"

    return app.response_class(generate(), mimetype='text/event-stream')


@app.route('/run/assertion/<assertion_id>')
def run_assertion(assertion_id):
    """
    Runs a predefined SQL-based assertion and returns instant pass/fail.
    Unlike test scripts, these check data invariants directly rather
    than executing a script.
    """
    import sqlite3

    assertions = {
        'mbid_has_country': {
            'label': 'Every artist with an mbid also has country set',
            'query': """
                SELECT COUNT(*) FROM artist_meta
                WHERE mbid IS NOT NULL
                  AND country IS NULL
            """,
            'expect_zero': True,
        },
        'no_null_era': {
            'label': 'No artist has a NULL era value',
            'query': "SELECT COUNT(*) FROM artist_meta WHERE era IS NULL",
            'expect_zero': True,
        },
        'unmatched_artists_not_in_meta': {
            'label': 'No artist appears in both artist_meta and mb_unmatched_artists',
            'query': """
                SELECT COUNT(*) FROM mb_unmatched_artists u
                JOIN artist_meta m ON m.artist = u.artist
                WHERE m.mbid IS NOT NULL
            """,
            'expect_zero': True,
        },
    }

    if assertion_id not in assertions:
        return jsonify({'error': 'Unknown assertion'}), 400

    a = assertions[assertion_id]
    try:
        conn = sqlite3.connect(DB_PATH)
        result = conn.execute(a['query']).fetchone()[0]
        conn.close()
        passed = (result == 0) if a['expect_zero'] else (result > 0)
        return jsonify({
            'label': a['label'],
            'pass': passed,
            'count': result,
        })
    except Exception as e:
        return jsonify({'label': a['label'], 'pass': False, 'error': str(e)}), 500


@app.route('/run/synapse-count')
def run_synapse_count():
    """Streams a full-library file format count. Read-only, no writes."""
    if running.get('synapse_count'):
        return jsonify({'error': 'Already running'}), 400

    def generate():
        running['synapse_count'] = True
        try:
            proc = subprocess.Popen(
                ['python3.12', '-u', os.path.join(BASE_DIR, 'synapse_analyze.py'), '--count'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in proc.stdout:
                yield f"data: {line.rstrip()}\n\n"
            proc.wait()
            if proc.returncode == 0:
                yield "data: ✅ Count complete.\n\n"
            else:
                yield f"data: ❌ Error (exit code {proc.returncode})\n\n"
        except Exception as e:
            yield f"data: ❌ Exception: {e}\n\n"
        finally:
            running['synapse_count'] = False
        yield "data: __DONE__\n\n"

    return app.response_class(generate(), mimetype='text/event-stream')


@app.route('/run/synapse-estimate')
def run_synapse_estimate():
    """Streams a live-sample time estimate. Analyzes a few real tracks
    on this hardware, no permanent writes to track_audio_features."""
    if running.get('synapse_estimate'):
        return jsonify({'error': 'Already running'}), 400

    def generate():
        running['synapse_estimate'] = True
        try:
            proc = subprocess.Popen(
                ['python3.12', '-u', os.path.join(BASE_DIR, 'synapse_analyze.py'), '--estimate'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in proc.stdout:
                yield f"data: {line.rstrip()}\n\n"
            proc.wait()
            if proc.returncode == 0:
                yield "data: ✅ Estimate complete.\n\n"
            else:
                yield f"data: ❌ Error (exit code {proc.returncode})\n\n"
        except Exception as e:
            yield f"data: ❌ Exception: {e}\n\n"
        finally:
            running['synapse_estimate'] = False
        yield "data: __DONE__\n\n"

    return app.response_class(generate(), mimetype='text/event-stream')


@app.route('/run/synapse-limited')
def run_synapse_limited():
    """Streams a real analysis run capped to a user-specified N tracks."""
    from flask import request
    n = request.args.get('n', '10')
    try:
        n = int(n)
        if n < 1 or n > 500:
            return jsonify({'error': 'N must be between 1 and 500'}), 400
    except ValueError:
        return jsonify({'error': 'N must be a number'}), 400

    if running.get('synapse_limited'):
        return jsonify({'error': 'Already running'}), 400

    def generate():
        running['synapse_limited'] = True
        try:
            proc = subprocess.Popen(
                ['python3.12', '-u', os.path.join(BASE_DIR, 'synapse_analyze.py'), '--limit', str(n)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in proc.stdout:
                yield f"data: {line.rstrip()}\n\n"
            proc.wait()
            if proc.returncode == 0:
                yield "data: ✅ Limited run complete.\n\n"
            else:
                yield f"data: ❌ Error (exit code {proc.returncode})\n\n"
        except Exception as e:
            yield f"data: ❌ Exception: {e}\n\n"
        finally:
            running['synapse_limited'] = False
        yield "data: __DONE__\n\n"

    return app.response_class(generate(), mimetype='text/event-stream')


@app.route('/synapse-status')
def synapse_status():
    """Plain status check — is a real run active, and how far along.
    No streaming, no long-lived connection — safe to poll anytime."""
    import sqlite3
    from datetime import datetime as _dt

    lock_path = os.path.join(BASE_DIR, 'synapse.lock')
    is_running = False
    if os.path.exists(lock_path):
        try:
            with open(lock_path) as f:
                pid = int(f.read().strip())
            proc_dir = f'/proc/{pid}'
            if os.path.exists(proc_dir):
                # Verify it's genuinely still synapse_analyze.py, not
                # just some unrelated process that happens to now have
                # this PID (can happen after the OS reassigns a freed
                # PID number) — checking existence alone isn't enough.
                try:
                    with open(f'{proc_dir}/cmdline', 'rb') as cf:
                        cmdline = cf.read().decode('utf-8', errors='ignore')
                    is_running = 'synapse_analyze.py' in cmdline
                except (OSError, IOError):
                    is_running = False
        except ValueError:
            is_running = False

    conn = sqlite3.connect(DB_PATH)
    analyzed = conn.execute("SELECT COUNT(*) FROM track_audio_features").fetchone()[0]
    synapse_error_count = conn.execute("SELECT COUNT(*) FROM synapse_errors").fetchone()[0]
    # VI errors live in a separate table (vi_results, verdict='ERROR')
    # -- since the July 2026 merge, this page needs to surface BOTH
    # failure sources, not just Synapse's. Found via a real run: the
    # Errors section showed nothing even while VI was actively
    # failing on real files (Bananarama, an Iggy Pop cluster).
    has_vi_results = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='vi_results'"
    ).fetchone() is not None
    vi_error_count = 0
    if has_vi_results:
        vi_error_count = conn.execute(
            "SELECT COUNT(*) FROM vi_results WHERE verdict = 'ERROR'"
        ).fetchone()[0]
    errors = synapse_error_count + vi_error_count
    last_write_row = conn.execute("SELECT MAX(analyzed_at) FROM track_audio_features").fetchone()
    conn.close()

    seconds_since_last_write = None
    last_write = last_write_row[0] if last_write_row else None
    if last_write:
        try:
            last_dt = _dt.fromisoformat(last_write)
            seconds_since_last_write = int((_dt.now() - last_dt).total_seconds())
        except ValueError:
            pass

    return jsonify({
        'running': is_running,
        'analyzed': analyzed,
        'errors': errors,
        'seconds_since_last_write': seconds_since_last_write,
    })


@app.route('/synapse-errors')
def synapse_errors_view():
    """Returns BOTH Synapse's and VI's error tables as one combined,
    labeled JSON list, for display on the Synapse page. Since the
    July 2026 VI+Synapse merge, a track can fail either analysis
    independently -- this needs to surface both, not just Synapse's,
    or VI failures (real ones: Bananarama, an Iggy Pop timeout
    cluster) are invisible here even though they're real, tracked
    data sitting in vi_results."""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)

    synapse_rows = conn.execute("""
        SELECT rating_key, filepath, error, failed_at
        FROM synapse_errors
        ORDER BY failed_at DESC
        LIMIT 200
    """).fetchall()

    has_vi_results = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='vi_results'"
    ).fetchone() is not None
    vi_rows = []
    if has_vi_results:
        vi_rows = conn.execute("""
            SELECT rating_key, title, artist, error, analyzed_at
            FROM vi_results
            WHERE verdict = 'ERROR'
            ORDER BY analyzed_at DESC
            LIMIT 200
        """).fetchall()
    conn.close()

    combined = [{
        'type':       'synapse',
        'rating_key': r[0],
        'label':      r[1].split('/')[-1] if r[1] else r[0],
        'error':      r[2],
        'at':         r[3],
    } for r in synapse_rows] + [{
        'type':       'vi',
        'rating_key': r[0],
        'label':      f"{r[2]} — {r[1]}" if r[1] or r[2] else r[0],
        'error':      r[3],
        'at':         r[4],
    } for r in vi_rows]

    combined.sort(key=lambda e: e['at'] or '', reverse=True)
    return jsonify(combined[:200])


@app.route('/synapse')
def synapse_page():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    total_tracks = conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
    analyzed = conn.execute("SELECT COUNT(*) FROM track_audio_features").fetchone()[0]
    conn.close()
    pct = round((analyzed / total_tracks * 100), 1) if total_tracks else 0
    return render_template('synapse.html', year=datetime.now().year,
                            synapse_analyzed=analyzed, synapse_total=total_tracks, synapse_pct=pct)


@app.route('/run/fullsync')
def run_fullsync():
    import subprocess
    import time
    from plexapi.server import PlexServer as PS
    if running.get('fullsync'):
        return jsonify({'error': 'Already running'}), 400
    def generate():
        running['fullsync'] = True
        try:
            # Step 1: Trigger Plex scan
            yield "data: 🔍 Triggering Plex library scan...\n\n"
            plex = PS(PLEX_URL, PLEX_TOKEN)
            music = plex.library.section(MUSIC_LIB)
            music.update()

            # Step 2: Poll until scan complete
            # NOTE: plex.library is a cached_data_property in plexapi —
            # re-calling plex.library.section(...) does NOT re-fetch
            # from the server after the first access, it just returns
            # the same cached object. That caused this loop to spin
            # forever on a stale .refreshing=True value even after
            # Plex had genuinely finished scanning (found July 2026).
            # music.reload() forces a real re-fetch of just this
            # object's own state, bypassing the cache correctly.
            yield "data: ⏳ Waiting for Plex scan to complete...\n\n"
            max_wait_iterations = 360  # 5s * 360 = 30 minutes safety cap
            waited = 0
            while True:
                time.sleep(5)
                waited += 1
                try:
                    music.reload()
                except Exception:
                    pass  # transient hiccup — try again next iteration
                if not music.refreshing:
                    break
                if waited >= max_wait_iterations:
                    yield "data: ⚠️ Scan wait exceeded 30 minutes — proceeding anyway (Plex may still be finishing in the background).\n\n"
                    break
                yield "data: ⏳ Still scanning...\n\n"
            yield "data: ✅ Plex scan complete.\n\n"

            # Steps 3-5: Run scripts in sequence
            scripts = [
                ('🔄 Syncing Plex Library...', os.path.join(BASE_DIR, 'musicmind_ingest.py')),
                ('🔗 Fingerprinting new tracks...', os.path.join(BASE_DIR, 'fingerprint_tracks.py')),
                ('♻️ Checking for known duplicates...', os.path.join(BASE_DIR, 'copy_forward_analysis.py')),
                ('🎵 Syncing Last.fm...', os.path.join(BASE_DIR, 'lastfm_sync.py')),
                ('🔍 Enriching artists (MusicBrainz)...', os.path.join(BASE_DIR, 'mb_enrich_artists.py')),
                ('🤖 Enriching artists (AI fallback)...', os.path.join(BASE_DIR, 'enrich_artists.py')),
                ('🏷️ Tagging new tracks...', os.path.join(BASE_DIR, 'plex_tag_tracks.py')),
                ('🧠 Analyzing audio (Synapse: BPM/key/danceability)...', os.path.join(BASE_DIR, 'synapse_analyze.py')),
            ]
            for label, script in scripts:
                yield f"data: {label}\n\n"
                proc = subprocess.Popen(
                    ['python3.12', '-u', script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1,
                    start_new_session=True,  # detach from this Flask worker — a step (e.g. a long Synapse run) now survives a pm2 restart of the parent app, matching the same protection the standalone /run/synapse-full button already had
                )
                for line in proc.stdout:
                    yield f"data: {line.rstrip()}\n\n"
                proc.wait()
                if proc.returncode != 0:
                    yield f"data: ❌ Error in {script}\n\n"
                    return

            yield "data: ✅ Full sync complete.\n\n"

        except Exception as e:
            yield f"data: ❌ Exception: {e}\n\n"
        finally:
            running['fullsync'] = False
        yield "data: __DONE__\n\n"

    return app.response_class(generate(), mimetype='text/event-stream')

@app.route('/run/gaps')
def run_gaps():
    import subprocess
    def generate():
        running['gaps'] = True
        try:
            proc = subprocess.Popen(
                ['python3.12', '-u', os.path.join(BASE_DIR, 'lastfm_gaps.py')],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            for line in proc.stdout:
                yield f"data: {line.rstrip()}\n\n"
            proc.wait()
            if proc.returncode == 0:
                yield "data: ✅ Done.\n\n"
            else:
                yield f"data: ❌ Error (exit code {proc.returncode})\n\n"
        except Exception as e:
            yield f"data: ❌ Exception: {e}\n\n"
        finally:
            running['gaps'] = False
        yield "data: __DONE__\n\n"
    return app.response_class(generate(), mimetype='text/event-stream')

@app.route('/query', methods=['POST'])
def query():
    import sqlite3
    sql = request.json.get('sql', '').strip()
    if not sql:
        return jsonify({'error': 'No query provided'}), 400
    # Safety — only allow SELECT
    if not sql.lower().startswith('select'):
        return jsonify({'error': 'Only SELECT queries allowed'}), 400
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(sql)
        rows = cur.fetchall()
        columns = [d[0] for d in cur.description] if cur.description else []
        conn.close()
        return jsonify({
            'columns': columns,
            'rows': [list(r) for r in rows],
            'count': len(rows)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/scan')
def scan():
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        music = plex.library.section(MUSIC_LIB)
        music.update()
        return jsonify({'success': True, 'message': 'Library scan triggered in Plex.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/playlists')
def playlists():
    import urllib.request, json
    try:
        # Fetch the server's own machine identifier so playlist links work
        # correctly regardless of which Plex server this instance connects
        # to. No auth token required for /identity.
        identity_req = urllib.request.Request(
            f"{PLEX_URL}/identity",
            headers={'Accept': 'application/json'}
        )
        identity_data = json.loads(urllib.request.urlopen(identity_req).read())
        machine_id = identity_data.get('MediaContainer', {}).get('machineIdentifier', '')

        req = urllib.request.Request(
            f"{PLEX_URL}/playlists?X-Plex-Token={PLEX_TOKEN}&playlistType=audio",
            headers={'Accept': 'application/json'}
        )
        data = json.loads(urllib.request.urlopen(req).read())
        items = data['MediaContainer'].get('Metadata', [])
        return jsonify({
            'machineId': machine_id,
            'playlists': [{
                'title':      p['title'],
                'key':        p['ratingKey'],
                'trackCount': p.get('leafCount', 0),
                'addedAt':    p.get('addedAt', 0),
            } for p in items]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/genres')
def genres():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute('''
        SELECT tag, COUNT(*) as cnt
        FROM track_tags
        GROUP BY tag
        ORDER BY cnt DESC
        LIMIT 200
    ''').fetchall()
    conn.close()
    return jsonify([{'tag': r[0], 'count': r[1]} for r in rows])

@app.route('/update')
def update():
    import subprocess
    import os

    # Get local git info
    git_info = {'is_git_repo': False}
    try:
        commit = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=BASE_DIR, stderr=subprocess.DEVNULL
        ).decode().strip()
        short = commit[:7]
        date = subprocess.check_output(
            ['git', 'log', '-1', '--format=%ci'],
            cwd=BASE_DIR, stderr=subprocess.DEVNULL
        ).decode().strip()[:10]
        message = subprocess.check_output(
            ['git', 'log', '-1', '--format=%s'],
            cwd=BASE_DIR, stderr=subprocess.DEVNULL
        ).decode().strip()
        branch = subprocess.check_output(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            cwd=BASE_DIR, stderr=subprocess.DEVNULL
        ).decode().strip()
        git_info = {
            'is_git_repo': True,
            'commit':  short,
            'date':    date,
            'message': message,
            'branch':  branch,
            'path':    BASE_DIR,
        }
    except:
        git_info = {
            'is_git_repo': False,
            'path': BASE_DIR,
        }

    return render_template('update.html', git=git_info, is_master=IS_MASTER, year=datetime.now().year)


@app.route('/check-update')
def check_update():
    import subprocess
    if IS_MASTER:
        return jsonify({'error': 'Updates are managed manually on this installation.'}), 400
    try:
        subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'],
            cwd=BASE_DIR, stderr=subprocess.DEVNULL
        )
    except Exception:
        return jsonify({'error': 'Not a git repository.', 'is_git_repo': False}), 200

    try:
        subprocess.check_call(
            ['git', 'fetch', 'origin'],
            cwd=BASE_DIR, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, timeout=30
        )
        local = subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=BASE_DIR
        ).decode().strip()
        remote = subprocess.check_output(
            ['git', 'rev-parse', 'origin/main'], cwd=BASE_DIR
        ).decode().strip()
        if local == remote:
            return jsonify({'up_to_date': True, 'local': local[:7]})
        message = subprocess.check_output(
            ['git', 'log', '-1', '--format=%s', 'origin/main'], cwd=BASE_DIR
        ).decode().strip()
        date = subprocess.check_output(
            ['git', 'log', '-1', '--format=%ci', 'origin/main'], cwd=BASE_DIR
        ).decode().strip()[:10]
        return jsonify({
            'up_to_date': False,
            'local': local[:7],
            'remote': remote[:7],
            'message': message,
            'date': date,
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Timed out reaching GitHub.'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 200


@app.route('/run/update')
def run_update():
    import subprocess
    if IS_MASTER:
        return jsonify({'error': 'Updates are managed manually on this installation.'}), 400
    if running.get('update'):
        return jsonify({'error': 'Already running'}), 400

    def generate():
        running['update'] = True
        try:
            status = subprocess.check_output(
                ['git', 'status', '--porcelain'], cwd=BASE_DIR
            ).decode().strip()
            if status:
                yield "data: Update cancelled: you have local file changes.\n\n"
                yield "data: Commit, stash, or discard them before updating.\n\n"
                yield "data: (git status --porcelain showed changes in:)\n\n"
                for line in status.splitlines():
                    yield f"data:   {line}\n\n"
                yield "data: __DONE__\n\n"
                return

            proc = subprocess.Popen(
                ['git', 'pull', 'origin', 'main'],
                cwd=BASE_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1
            )
            for line in proc.stdout:
                yield f"data: {line.rstrip()}\n\n"
            proc.wait()
            if proc.returncode == 0:
                yield "data: \n\n"
                yield "data: ✅ Update complete. Click 'Restart App' to load the new code.\n\n"
            else:
                yield f"data: ❌ git pull exited with code {proc.returncode}\n\n"
        except Exception as e:
            yield f"data: ❌ Exception: {e}\n\n"
        finally:
            running['update'] = False
        yield "data: __DONE__\n\n"

    return app.response_class(generate(), mimetype='text/event-stream')

@app.route('/tests')
def tests():
    return render_template('tests.html', year=datetime.now().year)

@app.route('/guide')
def guide():
    return render_template('guide.html', year=datetime.now().year)

@app.route('/playlist-audit')
def playlist_audit_page():
    return render_template('playlist_audit.html', year=datetime.now().year)


@app.route('/playlist-audit-data/<int:playlist_key>')
def playlist_audit_data(playlist_key):
    import sqlite3
    try:
        plex = PlexServer(PLEX_URL, PLEX_TOKEN)
        playlist = plex.fetchItem(playlist_key)
        items = playlist.items()
    except Exception as e:
        return jsonify({'error': f'Could not load playlist: {e}'}), 404

    rating_keys = [str(t.ratingKey) for t in items]

    conn = sqlite3.connect(DB_PATH)
    has_vi_results = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='vi_results'"
    ).fetchone() is not None

    data_by_key = {}
    if rating_keys:
        placeholders = ",".join("?" for _ in rating_keys)
        vi_select = "vi.p_voice, vi.verdict" if has_vi_results else "NULL, NULL"
        vi_join = "LEFT JOIN vi_results vi ON vi.rating_key = t.rating_key" if has_vi_results else ""
        rows = conn.execute(f"""
            SELECT t.rating_key, COALESCE(t.real_artist, t.artist) as artist,
                   taf.bpm, taf.danceability, {vi_select}
            FROM tracks t
            LEFT JOIN track_audio_features taf ON taf.rating_key = t.rating_key
            {vi_join}
            WHERE t.rating_key IN ({placeholders})
        """, rating_keys).fetchall()
        for row in rows:
            data_by_key[row[0]] = row
    conn.close()

    # Preserve the PLAYLIST's own track order, not SQL's arbitrary order —
    # the whole point of an audit is seeing the playlist as it actually is.
    tracks_out = []
    for t in items:
        rk = str(t.ratingKey)
        row = data_by_key.get(rk)
        tracks_out.append({
            'title':        t.title,
            'artist':       (row[1] if row else t.grandparentTitle) or t.grandparentTitle,
            'bpm':          round(row[2], 1) if row and row[2] is not None else None,
            'danceability': round(row[3], 2) if row and row[3] is not None else None,
            'p_voice':      round(row[4], 3) if row and row[4] is not None else None,
            'vi_verdict':   row[5] if row else None,
        })

    return jsonify({
        'title':   playlist.title,
        'summary': playlist.summary or None,  # the stored prompt, if this playlist was created after this feature shipped
        'tracks':  tracks_out,
    })


@app.route('/logs')
def logs():
    import sqlite3, json
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT id, timestamp, prompt, tags, filters, result_count,
               duration_ms, error, openai_request, openai_response,
               prompt_tokens, completion_tokens, cost_usd
        FROM query_log
        ORDER BY id DESC
        LIMIT 100
    """).fetchall()
    conn.close()
    entries = []
    for row in rows:
        entries.append({
            'id':                row[0],
            'timestamp':         row[1],
            'prompt':            row[2] or '',
            'tags':              json.loads(row[3] or '[]'),
            'filters':           json.loads(row[4] or '{}'),
            'result_count':      row[5] or 0,
            'duration_ms':       row[6] or 0,
            'error':             row[7],
            'openai_request':    row[8] or '',
            'openai_response':   row[9] or '',
            'prompt_tokens':     row[10] or 0,
            'completion_tokens': row[11] or 0,
            'cost_usd':          row[12] or 0,
        })
    return render_template('logs.html', entries=entries, year=datetime.now().year)

@app.route('/stats')
def stats():
    return render_template('stats.html', year=datetime.now().year)


@app.route('/export-csv')
def export_csv():
    """
    Dumps the enriched library data as a downloadable CSV -- AI tags,
    measured BPM/key/danceability, VI verdicts, play counts,
    real_artist. Data nobody else has, and exporting it makes the
    whole thing feel genuinely user-owned rather than locked inside
    a database only this app can read. From the July 2026 competitive
    positioning research (Music Manager for Plex comparison).
    """
    import sqlite3, csv, io

    conn = sqlite3.connect(DB_PATH)
    has_vi_results = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='vi_results'"
    ).fetchone() is not None

    vi_select = "vi.verdict, vi.p_voice, vi.p_inst" if has_vi_results else "NULL, NULL, NULL"
    vi_join = "LEFT JOIN vi_results vi ON vi.rating_key = t.rating_key" if has_vi_results else ""

    rows = conn.execute(f"""
        SELECT
            t.rating_key,
            t.title,
            COALESCE(t.real_artist, t.artist) as artist,
            t.album,
            t.genre,
            t.year,
            t.play_count,
            t.user_rating,
            t.rating_count,
            GROUP_CONCAT(DISTINCT tt.tag) as tags,
            taf.bpm,
            taf.key,
            taf.scale,
            taf.danceability,
            {vi_select}
        FROM tracks t
        LEFT JOIN track_tags tt ON tt.rating_key = t.rating_key
        LEFT JOIN track_audio_features taf ON taf.rating_key = t.rating_key
        {vi_join}
        GROUP BY t.rating_key
        ORDER BY t.artist, t.album, t.title
    """).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'rating_key', 'title', 'artist', 'album', 'genre', 'year',
        'play_count', 'user_rating', 'popularity_rating_count', 'tags',
        'bpm', 'key', 'scale', 'danceability',
        'vi_verdict', 'vi_p_voice', 'vi_p_inst'
    ])
    writer.writerows(rows)

    response = app.response_class(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=musicmind_library_export.csv'}
    )
    return response

@app.route('/stats/data')
def stats_data():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)

    # Tile row-count limits — configurable per-tile from the Stats page
    # (persisted client-side in localStorage, not the database, so a
    # future code sync can never silently revert someone's preference).
    genre_limit = request.args.get('genre_limit', 10, type=int)
    artist_limit = request.args.get('artist_limit', 10, type=int)
    country_limit = request.args.get('country_limit', 10, type=int)

    listening_by_year = conn.execute(
        "SELECT strftime('%Y', datetime(timestamp, 'unixepoch', 'localtime')) as year, COUNT(*) as plays FROM lastfm_scrobbles GROUP BY year ORDER BY year"
    ).fetchall()

    top_artists = conn.execute(
        "SELECT COALESCE(real_artist, artist) as artist, SUM(play_count) as plays FROM tracks WHERE play_count > 0 AND artist IS NOT NULL AND artist != '' AND LOWER(COALESCE(real_artist, artist)) NOT IN ('various artists', 'va') GROUP BY COALESCE(real_artist, artist) ORDER BY plays DESC LIMIT ?",
        (artist_limit,)
    ).fetchall()

    top_genres = conn.execute(
        "SELECT tag, COUNT(*) as cnt FROM track_tags GROUP BY tag ORDER BY cnt DESC LIMIT ?",
        (genre_limit,)
    ).fetchall()

    by_era = conn.execute(
        "SELECT era, COUNT(*) as cnt FROM artist_meta WHERE era != 'unknown' AND era IS NOT NULL GROUP BY era ORDER BY era"
    ).fetchall()

    by_country = conn.execute(
        "SELECT country, COUNT(*) as cnt FROM artist_meta WHERE country != 'unknown' AND country IS NOT NULL GROUP BY country ORDER BY cnt DESC LIMIT ?",
        (country_limit,)
    ).fetchall()

    by_gender = conn.execute(
        "SELECT gender, COUNT(*) as cnt FROM artist_meta WHERE gender IS NOT NULL GROUP BY gender ORDER BY cnt DESC"
    ).fetchall()

    total_tracks = conn.execute("SELECT COUNT(*) FROM tracks").fetchone()[0]
    total_artists = conn.execute("SELECT COUNT(DISTINCT COALESCE(real_artist, artist)) FROM tracks WHERE artist IS NOT NULL AND artist != ''").fetchone()[0]
    total_scrobbles = conn.execute("SELECT COUNT(*) FROM lastfm_scrobbles").fetchone()[0]
    total_instrumental = conn.execute("SELECT COUNT(*) FROM tracks WHERE is_instrumental = 1").fetchone()[0]

    conn.close()

    return jsonify({
        'listening_by_year': [{'year': r[0], 'plays': r[1]} for r in listening_by_year],
        'top_artists':       [{'artist': r[0], 'plays': r[1]} for r in top_artists],
        'top_genres':        [{'tag': r[0], 'cnt': r[1]} for r in top_genres],
        'by_era':            [{'era': r[0], 'cnt': r[1]} for r in by_era],
        'by_country':        [{'country': r[0], 'cnt': r[1]} for r in by_country],
        'by_gender':         [{'gender': r[0], 'cnt': r[1]} for r in by_gender],
        'stats': {
            'total_tracks':       total_tracks,
            'total_artists':      total_artists,
            'total_scrobbles':    total_scrobbles,
            'total_instrumental': total_instrumental,
        }
    })

@app.route('/db')
def db_console():
    return render_template('query.html', year=datetime.now().year)

@app.route('/gaps')
def gaps():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    buckets = []
    for cat_key, cat_label in [
        ('worth_acquiring',    '🎵 Worth Acquiring'),
        ('classical',          '🎼 Classical'),
        ('ambient_meditation', '🧘 Ambient / Meditation'),
        ('unknown',            '❓ Unknown'),
    ]:
        rows = conn.execute(
            "SELECT artist, scrobbles FROM artist_gaps WHERE category=? ORDER BY scrobbles DESC",
            (cat_key,)
        ).fetchall()
        buckets.append({
            'label': cat_label,
            'artists': [{'artist': r[0], 'scrobbles': r[1]} for r in rows]
        })
    conn.close()
    return render_template('gaps.html', buckets=buckets, year=datetime.now().year)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8787, debug=False)

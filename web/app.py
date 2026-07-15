#!/usr/bin/env python3
"""
MusicMind for Plex - Flask Web UI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
from datetime import datetime
from brain import expand_prompt, classify_prompt, search_tracks, sequence_for_flow, create_playlist, PlexServer, PLEX_URL, PLEX_TOKEN, MUSIC_LIB, detect_instrumental_intent, extract_lastfm_dates, get_scrobbled_tracks_in_range, get_scrobbled_tracks_around_date, update_query_log_result_count
from config import DB_PATH, BASE_DIR, LASTFM_KEY
try:
    from config import IS_MASTER
except ImportError:
    IS_MASTER = False  # not set in config.py — safe default

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', lastfm_enabled=bool(LASTFM_KEY), year=datetime.now().year)

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


@app.route('/preview', methods=['POST'])
def preview():
    data = request.json
    prompt = data.get('prompt', '').strip()

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
        if prompt.lower().startswith('lastfm:'):
            date_text = prompt[len('lastfm:'):].strip()
            dates = extract_lastfm_dates(date_text)
            lastfm_rating_keys = get_scrobbled_tracks_in_range(dates['start_date'], dates['end_date'])
            intent = 'lastfm_range'
            search_term = f"{dates['start_date']} to {dates['end_date']}"
        elif prompt:
            classification = classify_prompt(prompt)
            intent      = classification.get('intent', 'mood')
            search_term = classification.get('title_search') or classification.get('artist_search')
            detected_filters = classification.get('filters', {}) or {}

            # Expand mood if there is a mood component
            mood = classification.get('mood')
            if mood and intent in ('mood', 'filter_only'):
                if intent == 'mood':
                    tags, query_log_id = expand_prompt(prompt)
                # for filter_only with no mood, skip expansion

        filters = {
            'unplayed':       data.get('unplayed', False),
            'genre':          data.get('genre') or None,
            'min_year':       int(data['min_year']) if data.get('min_year') else None,
            'max_year':       int(data['max_year']) if data.get('max_year') else None,
            'min_plays':      int(data['min_plays']) if data.get('min_plays') else detected_filters.get('min_plays'),
            'max_plays':      int(data['max_plays']) if data.get('max_plays') else None,
            'limit':          int(data.get('limit', 30)),
            'max_per_artist': int(data.get('max_per_artist', 3)),
            'min_rating':     float(data['min_rating']) if data.get('min_rating') else None,
            'gender':         data.get('gender') or detected_filters.get('gender') or None,
            'country':        data.get('country') or detected_filters.get('country') or None,
            'era':            data.get('era') or detected_filters.get('era') or None,
            'instrumental':   1 if data.get('instrumental') else (detect_instrumental_intent(prompt) if prompt else None),
            'bpm_min':        int(data['bpm_min']) if data.get('bpm_min') else None,
            'bpm_max':        int(data['bpm_max']) if data.get('bpm_max') else None,
            'danceability':   data.get('danceability') or None,
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

        return jsonify({'tags': tags, 'tracks': tracks, 'intent': intent, 'search_term': search_term, 'detected_filters': detected_filters, 'dj_ified': bool(data.get('dj_ify'))})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/create', methods=['POST'])
def create():
    data = request.json
    name = data.get('name', '').strip()
    rating_keys = data.get('rating_keys', [])

    if not name:
        return jsonify({'error': 'No playlist name provided'}), 400
    if not rating_keys:
        return jsonify({'error': 'No tracks provided'}), 400

    try:
        count = create_playlist(name, rating_keys)
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
        'instrumental': os.path.join(BASE_DIR, 'tag_instrumentals.py'),
        'mbenrich': os.path.join(BASE_DIR, 'mb_enrich_artists.py'),
        'aienrich': os.path.join(BASE_DIR, 'enrich_artists.py'),
        'synapse':  os.path.join(BASE_DIR, 'synapse_analyze.py'),
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
    errors = conn.execute("SELECT COUNT(*) FROM synapse_errors").fetchone()[0]
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
    """Returns the current synapse_errors table as JSON, for display on the Synapse page."""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT rating_key, filepath, error, failed_at
        FROM synapse_errors
        ORDER BY failed_at DESC
        LIMIT 200
    """).fetchall()
    conn.close()
    return jsonify([{
        'rating_key': r[0],
        'filepath':   r[1],
        'error':      r[2],
        'failed_at':  r[3],
    } for r in rows])


@app.route('/synapse')
def synapse_page():
    return render_template('synapse.html', year=datetime.now().year)


@app.route('/run/fullsync')
def run_fullsync():
    import subprocess
    import time
    from plexapi.server import PlexServer as PS
    def generate():
        running['fullsync'] = True
        try:
            # Step 1: Trigger Plex scan
            yield "data: 🔍 Triggering Plex library scan...\n\n"
            plex = PS(PLEX_URL, PLEX_TOKEN)
            music = plex.library.section(MUSIC_LIB)
            music.update()

            # Step 2: Poll until scan complete
            yield "data: ⏳ Waiting for Plex scan to complete...\n\n"
            while True:
                time.sleep(5)
                music = plex.library.section(MUSIC_LIB)
                if not music.refreshing:
                    break
                yield "data: ⏳ Still scanning...\n\n"
            yield "data: ✅ Plex scan complete.\n\n"

            # Steps 3-5: Run scripts in sequence
            scripts = [
                ('🔄 Syncing Plex Library...', os.path.join(BASE_DIR, 'musicmind_ingest.py')),
                ('🔗 Fingerprinting new tracks...', os.path.join(BASE_DIR, 'fingerprint_tracks.py')),
                ('🎵 Syncing Last.fm...', os.path.join(BASE_DIR, 'lastfm_sync.py')),
                ('🔍 Enriching artists (MusicBrainz)...', os.path.join(BASE_DIR, 'mb_enrich_artists.py')),
                ('🤖 Enriching artists (AI fallback)...', os.path.join(BASE_DIR, 'enrich_artists.py')),
                ('🏷️ Tagging new tracks...', os.path.join(BASE_DIR, 'plex_tag_tracks.py')),
            ]
            for label, script in scripts:
                yield f"data: {label}\n\n"
                proc = subprocess.Popen(
                    ['python3.12', '-u', script],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
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

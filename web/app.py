#!/usr/bin/env python3
"""
Plex Music Brain - Flask Web UI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, request, jsonify
from brain import expand_prompt, search_tracks, create_playlist, PlexServer, PLEX_URL, PLEX_TOKEN, MUSIC_LIB, detect_instrumental_intent
from config import DB_PATH, BASE_DIR

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/preview', methods=['POST'])
def preview():
    data = request.json
    prompt = data.get('prompt', '').strip()

    try:
        tags = expand_prompt(prompt) if prompt else []
        filters = {
            'unplayed':       data.get('unplayed', False),
            'genre':          data.get('genre') or None,
            'min_year':       int(data['min_year']) if data.get('min_year') else None,
            'max_year':       int(data['max_year']) if data.get('max_year') else None,
            'min_plays':      int(data['min_plays']) if data.get('min_plays') else None,
            'max_plays':      int(data['max_plays']) if data.get('max_plays') else None,
            'limit':          int(data.get('limit', 30)),
            'max_per_artist': int(data.get('max_per_artist', 3)),
            'min_rating':     float(data['min_rating']) if data.get('min_rating') else None,
            'gender':         data.get('gender') or None,
            'country':        data.get('country') or None,
            'era':            data.get('era') or None,
            'instrumental':   1 if data.get('instrumental') else (detect_instrumental_intent(prompt) if prompt else None),

        }
        tracks = search_tracks(tags, filters)
        return jsonify({'tags': tags, 'tracks': tracks})

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
    return render_template('admin.html')

@app.route('/run/<script>')
def run_script(script):
    scripts = {
        'ingest':   os.path.join(BASE_DIR, 'plex_music_brain_ingest.py'),
        'lastfm':   os.path.join(BASE_DIR, 'lastfm_sync.py'),
        'tagger':   os.path.join(BASE_DIR, 'plex_tag_tracks.py'),
        'context':  os.path.join(BASE_DIR, 'listening_context.py'),
        'instrumental': os.path.join(BASE_DIR, 'tag_instrumentals.py'),
    }
    if script not in scripts:
        return jsonify({'error': 'Unknown script'}), 400
    if running.get(script):
        return jsonify({'error': 'Already running'}), 400

    def generate():
        running[script] = True
        try:
            proc = subprocess.Popen(
                ['python3.12', scripts[script]],
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
                ('🔄 Syncing Plex Library...', os.path.join(BASE_DIR, 'plex_music_brain_ingest.py')),
                ('🎵 Syncing Last.fm...', os.path.join(BASE_DIR, 'lastfm_sync.py')),
                ('🏷️ Tagging new tracks...', os.path.join(BASE_DIR, 'plex_tag_tracks.py')),
            ]
            for label, script in scripts:
                yield f"data: {label}\n\n"
                proc = subprocess.Popen(
                    ['python3.12', script],
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
                ['python3.12', os.path.join(BASE_DIR, 'lastfm_gaps.py')],
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

@app.route('/stats')
def stats():
    return render_template('stats.html')

@app.route('/stats/data')
def stats_data():
    import sqlite3
    conn = sqlite3.connect(DB_PATH)

    listening_by_year = conn.execute(
        "SELECT strftime('%Y', datetime(timestamp, 'unixepoch', 'localtime')) as year, COUNT(*) as plays FROM lastfm_scrobbles GROUP BY year ORDER BY year"
    ).fetchall()

    top_artists = conn.execute(
        "SELECT COALESCE(real_artist, artist) as artist, SUM(play_count) as plays FROM tracks WHERE play_count > 0 AND artist IS NOT NULL AND artist != '' AND LOWER(COALESCE(real_artist, artist)) NOT IN ('various artists', 'va') GROUP BY COALESCE(real_artist, artist) ORDER BY plays DESC LIMIT 10"
    ).fetchall()

    top_genres = conn.execute(
        "SELECT tag, COUNT(*) as cnt FROM track_tags GROUP BY tag ORDER BY cnt DESC LIMIT 10"
    ).fetchall()

    by_era = conn.execute(
        "SELECT era, COUNT(*) as cnt FROM artist_meta WHERE era != 'unknown' AND era IS NOT NULL GROUP BY era ORDER BY era"
    ).fetchall()

    by_country = conn.execute(
        "SELECT country, COUNT(*) as cnt FROM artist_meta WHERE country != 'unknown' AND country IS NOT NULL GROUP BY country ORDER BY cnt DESC LIMIT 10"
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
    return render_template('query.html')

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
    return render_template('gaps.html', buckets=buckets)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8787, debug=False)

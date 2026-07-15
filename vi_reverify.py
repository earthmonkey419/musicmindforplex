#!/usr/bin/env python3.12
"""Verify is_instrumental for the ENTIRE library via audio analysis.
Flips tags in both directions based on measured audio:
  p_voice >= 0.55 -> 0 (vocal)     p_inst >= 0.55 -> 1 (instrumental)
  0.45-0.55       -> AMBIGUOUS, tag left unchanged
Priority order: tagged-instrumental first, then NULL, then tagged-vocal.
Usage:
  python3.12 vi_reverify.py --dry-run --limit 20
  python3.12 vi_reverify.py                     # full run (resumable)
Audit table: vi_results

NOTE: requires models/voice_instrumental-musicnn-msd-1.pb, which is
CC BY-NC-SA licensed (essentia.upf.edu) and deliberately NOT committed
to this repo. Download it separately before running:
  https://essentia.upf.edu/models/classifiers/voice_instrumental/
"""
import sys, os, time, sqlite3
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import PLEX_URL, PLEX_TOKEN, DB_PATH

MODEL = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "models", "voice_instrumental-musicnn-msd-1.pb")
THRESHOLD = 0.55

def main():
    dry_run = "--dry-run" in sys.argv
    limit = None
    if "--limit" in sys.argv:
        limit = int(sys.argv[sys.argv.index("--limit") + 1])

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")
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

    rows = conn.execute("""
        SELECT t.rating_key, t.title, t.artist, t.is_instrumental FROM tracks t
        WHERE t.rating_key NOT IN (SELECT rating_key FROM vi_results)
        ORDER BY CASE
            WHEN t.is_instrumental = 1 THEN 0
            WHEN t.is_instrumental IS NULL THEN 1
            ELSE 2 END,
            t.artist, t.title
    """).fetchall()
    total = len(rows)
    if limit:
        rows = rows[:limit]
    print(f"Tracks remaining to verify: {total}")
    print(f"Processing {len(rows)} this run. dry_run={dry_run}\n")
    if not rows:
        return

    from plexapi.server import PlexServer
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)

    import numpy as np
    import essentia
    essentia.log.warningActive = False
    essentia.log.infoActive = False
    from essentia.standard import MonoLoader, TensorflowPredictMusiCNN
    model = TensorflowPredictMusiCNN(graphFilename=MODEL, output="model/Sigmoid")

    flipped_to_vocal = flipped_to_inst = confirmed = ambiguous = errors = 0
    t_start = time.time()
    for i, (rk, tt, ar, old_tag) in enumerate(rows, 1):
        err = None; p_inst = p_voice = None; verdict = "ERROR"; changed = 0
        try:
            item = plex.fetchItem(int(rk))
            fp = item.media[0].parts[0].file
            if not os.path.exists(fp):
                raise FileNotFoundError(fp)
            audio = MonoLoader(filename=fp, sampleRate=16000)()
            preds = np.atleast_2d(model(audio))
            if preds.size == 0:
                raise ValueError("track too short for any analysis window — no patches produced")
            p_inst, p_voice = (float(x) for x in np.mean(preds, axis=0))
            if p_voice >= THRESHOLD:
                verdict = "VOICE"
                if old_tag != 0:
                    if not dry_run:
                        conn.execute("UPDATE tracks SET is_instrumental = 0 WHERE rating_key = ?", (rk,))
                    changed = 1; flipped_to_vocal += 1
                else:
                    confirmed += 1
            elif p_inst >= THRESHOLD:
                verdict = "INSTRUMENTAL"
                if old_tag != 1:
                    if not dry_run:
                        conn.execute("UPDATE tracks SET is_instrumental = 1 WHERE rating_key = ?", (rk,))
                    changed = 1; flipped_to_inst += 1
                else:
                    confirmed += 1
            else:
                verdict = "AMBIGUOUS"; ambiguous += 1
        except Exception as e:
            err = str(e)[:300]; errors += 1
        conn.execute("""INSERT OR REPLACE INTO vi_results
            (rating_key, title, artist, old_tag, p_inst, p_voice, verdict, tag_changed, error, analyzed_at)
            VALUES (?,?,?,?,?,?,?,?,?,datetime('now'))""",
            (rk, tt, ar, old_tag, p_inst, p_voice, verdict, changed, err))
        conn.commit()
        elapsed = time.time() - t_start
        eta_h = (elapsed / i) * (len(rows) - i) / 3600
        flag = " *CHANGED*" if changed else ""
        print(f"[{i}/{len(rows)}] {verdict:12s} v={p_voice if p_voice is not None else -1:.3f} old={old_tag}  {tt} | {ar}{flag}  (ETA {eta_h:.1f}h)")

    print(f"\nDone. to_vocal={flipped_to_vocal} to_inst={flipped_to_inst} confirmed={confirmed} ambiguous={ambiguous} errors={errors}")
    if dry_run:
        print("DRY RUN — no tags were changed.")

if __name__ == "__main__":
    main()

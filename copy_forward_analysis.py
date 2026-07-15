#!/usr/bin/env python3.12
"""
MusicMind for Plex - Copy-Forward Analysis (gatekeeper skip-logic)

The actual payoff of fingerprinting: two tracks with an IDENTICAL
Chromaprint fingerprint are, provably, the same audio recording — so
if one has already been analyzed by Synapse (BPM/key/danceability)
or VI (voice/instrumental), the other doesn't need separate analysis.
Its results are copied, never guessed.

This closes the loop the original v3 design called for: fingerprint
FIRST (already automatic in Full Sync), then before Synapse/VI ever
touch a track's audio, check whether a fingerprint-identical track
has already been measured — if so, copy the measurement and skip the
expensive analysis entirely.

Quantified motivation: the original VI migration spent ~12.7 wasted
hours re-measuring audio it had already measured, driven by ~1,900
duplicate rows. Real compute saved, zero risk — a fingerprint match
IS proof of identical audio, so copying is never a guess.

Deliberately conservative: only copies when there's a PROVEN
fingerprint match to EXISTING real analysis data. Never invents
results. A track with no duplicate match is left untouched for
Synapse/VI to measure normally, same as today.

Covers BOTH tables independently (VI isn't merged into Synapse yet):
  - track_audio_features (Synapse: BPM/key/danceability)
  - vi_results (VI: voice/instrumental — only if vi_results exists;
    a fresh install that's never run vi_reverify.py simply has
    nothing to copy from yet, which is fine)

Usage:
    python3.12 copy_forward_analysis.py
"""
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH


def table_exists(conn, name):
    return conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)
    ).fetchone() is not None


def copy_forward_synapse(conn):
    """For any track with a fingerprint but no Synapse analysis yet,
    find another track sharing that exact fingerprint that DOES have
    analysis, and copy it over."""
    candidates = conn.execute("""
        SELECT tf.rating_key, tf.fingerprint
        FROM track_fingerprints tf
        WHERE tf.error IS NULL
          AND tf.rating_key NOT IN (SELECT rating_key FROM track_audio_features)
    """).fetchall()

    copied = 0
    for rating_key, fingerprint in candidates:
        source = conn.execute("""
            SELECT taf.bpm, taf.key, taf.scale, taf.key_strength, taf.danceability
            FROM track_audio_features taf
            JOIN track_fingerprints tf2 ON tf2.rating_key = taf.rating_key
            WHERE tf2.fingerprint = ? AND tf2.rating_key != ?
            LIMIT 1
        """, (fingerprint, rating_key)).fetchone()

        if source:
            bpm, key, scale, key_strength, danceability = source
            conn.execute("""
                INSERT OR REPLACE INTO track_audio_features
                    (rating_key, bpm, key, scale, key_strength, danceability, analyzed_at)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (rating_key, bpm, key, scale, key_strength, danceability))
            copied += 1

    conn.commit()
    return copied, len(candidates)


def copy_forward_vi(conn):
    """Same principle, for vi_results (voice/instrumental). Safe
    no-op if vi_results doesn't exist yet (e.g. vi_reverify.py has
    never been run on this install)."""
    if not table_exists(conn, 'vi_results'):
        return 0, 0, "vi_results table doesn't exist yet — skipped"

    candidates = conn.execute("""
        SELECT tf.rating_key, tf.fingerprint
        FROM track_fingerprints tf
        WHERE tf.error IS NULL
          AND tf.rating_key NOT IN (SELECT rating_key FROM vi_results)
    """).fetchall()

    copied = 0
    for rating_key, fingerprint in candidates:
        source = conn.execute("""
            SELECT vr.title, vr.artist, vr.p_inst, vr.p_voice, vr.verdict
            FROM vi_results vr
            JOIN track_fingerprints tf2 ON tf2.rating_key = vr.rating_key
            WHERE tf2.fingerprint = ? AND tf2.rating_key != ?
              AND vr.error IS NULL
            LIMIT 1
        """, (fingerprint, rating_key)).fetchone()

        if source:
            title, artist, p_inst, p_voice, verdict = source
            conn.execute("""
                INSERT OR REPLACE INTO vi_results
                    (rating_key, title, artist, old_tag, p_inst, p_voice,
                     verdict, tag_changed, error, analyzed_at)
                VALUES (?, ?, ?, NULL, ?, ?, ?, 0, NULL, datetime('now'))
            """, (rating_key, title, artist, p_inst, p_voice, verdict))
            copied += 1

    conn.commit()
    return copied, len(candidates), None


def main():
    print("MusicMind for Plex - Copy-Forward Analysis")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH, timeout=60)
    conn.execute("PRAGMA busy_timeout=60000")

    print("Checking Synapse data (BPM/key/danceability)...")
    syn_copied, syn_candidates = copy_forward_synapse(conn)
    print(f"  {syn_copied}/{syn_candidates} tracks matched an already-analyzed "
          f"duplicate — copied, no re-analysis needed.")

    print("\nChecking VI data (voice/instrumental)...")
    vi_copied, vi_candidates, vi_skip_reason = copy_forward_vi(conn)
    if vi_skip_reason:
        print(f"  {vi_skip_reason}")
    else:
        print(f"  {vi_copied}/{vi_candidates} tracks matched an already-analyzed "
              f"duplicate — copied, no re-analysis needed.")

    conn.close()
    print("\n" + "=" * 50)
    print(f"Done. Synapse: {syn_copied} copied. VI: {vi_copied} copied.")
    print("=" * 50)


if __name__ == "__main__":
    main()

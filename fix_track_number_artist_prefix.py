#!/usr/bin/env python3.12
"""
One-off cleanup: strips a leading "NN. " track-number prefix from
tracks.artist, where a compilation's file-tagging convention (e.g.
"01. Nick Nicely - Hilly Fields (1892).mp3") got split wrong,
dumping "01. Nick Nicely" into the artist field instead of correctly
separating the track number from the real artist name.

Found July 2026 via the "mbid_has_country" test failure: confirmed
via direct Plex file-path lookup that every affected track traces
back to exactly one release -- "V.A - Another Splash Of Colour - New
Psychedelia In Britain 1980-1985", spread across its own 3 CD
subfolders -- not scattered corruption across the library. Same
tagging convention split the SAME real artist into multiple separate
artist_meta rows depending on which track number happened to precede
their name (e.g. "01. Nick Nicely" and "06. Nick Nicely" as two
distinct rows for one real artist), fragmenting whatever gender/
country/era data either row had.

Safe, narrow pattern (^\d{1,3}\.\s) -- matches only a leading
number, period, and whitespace, which is not a pattern any real
artist name legitimately starts with (verified: no false positives
in the actual affected set, all 42 confirmed to trace to this one
release via real file paths first).

Strips the prefix from tracks.artist (the actual source of truth),
then deletes the now-orphaned artist_meta rows for the OLD malformed
names -- deliberately NOT attempting to merge conflicting old rows;
simpler and safer to let the next MusicBrainz enrichment run create
correct, fresh artist_meta entries under the now-clean names using
machinery that's already proven and trusted.

Usage:
    python3.12 fix_track_number_artist_prefix.py --dry-run   # report only
    python3.12 fix_track_number_artist_prefix.py             # actually fix
"""
import sys, os, re, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH

PREFIX_PATTERN = re.compile(r'^\d{1,3}\.\s+')


def main():
    dry_run = "--dry-run" in sys.argv

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout=60000")

    rows = conn.execute("SELECT rating_key, artist FROM tracks WHERE artist IS NOT NULL").fetchall()
    affected = [(rk, artist, PREFIX_PATTERN.sub('', artist)) for rk, artist in rows
                if PREFIX_PATTERN.match(artist)]

    print(f"Found {len(affected)} tracks with a leading track-number artist prefix.\n")

    if not affected:
        print("Nothing to do.")
        conn.close()
        return

    old_names = sorted(set(old for _, old, _ in affected))
    new_names = sorted(set(new for _, _, new in affected))
    print(f"{len(old_names)} distinct malformed names -> {len(new_names)} distinct real artist names")
    print()
    for rk, old, new in affected[:10]:
        print(f"  '{old}' -> '{new}'")
    if len(affected) > 10:
        print(f"  ... and {len(affected) - 10} more")

    if dry_run:
        print("\nDRY RUN — nothing changed.")
        conn.close()
        return

    for rk, old, new in affected:
        conn.execute("UPDATE tracks SET artist = ? WHERE rating_key = ?", (new, rk))

    placeholders = ",".join("?" for _ in old_names)
    cursor = conn.execute(
        f"DELETE FROM artist_meta WHERE artist IN ({placeholders})",
        old_names
    )
    deleted_meta_rows = cursor.rowcount

    conn.commit()
    conn.close()

    print(f"\nDone. Fixed {len(affected)} tracks' artist field.")
    print(f"Cleared {deleted_meta_rows} stale artist_meta rows for the old malformed names —")
    print("these will get correctly re-enriched under the real artist name on the next")
    print("MusicBrainz/AI enrichment run.")


if __name__ == "__main__":
    main()

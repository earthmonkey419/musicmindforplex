#!/usr/bin/env python3.12
"""
One-off cleanup: clears existing tags on VA-resolved tracks, so they
get re-tagged correctly with real artist context on the next
plex_tag_tracks.py run.

Why this exists: every track that was "Various Artists" at the time
AI tagging ran got tagged completely blind to its real artist — the
tagger only had the song title and compilation album name to work
with. Confirmed real and not rare: 4,363 tracks (~19% of the library)
fall into this category, some with genuinely wrong tags (The Sisters
of Mercy, a gothic rock band, tagged "jazz, r&b, soul" purely because
its track happened to be titled "Body and Soul").

Safe: only ever DELETEs from track_tags for tracks where real_artist
IS NOT NULL — never touches tracks, never touches any track that
hasn't actually been VA-resolved. Re-running is harmless (a
second run just finds nothing left to clear).

After running this, plex_tag_tracks.py's normal "untagged tracks"
query will naturally pick these tracks back up — and thanks to the
same-day fix to get_untagged_tracks(), will correctly use the
resolved real_artist this time instead of "Various Artists".

Usage:
    python3.12 clear_va_tags_for_retag.py           # actually clear
    python3.12 clear_va_tags_for_retag.py --dry-run  # just report the count
"""
import sys, os, sqlite3
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH


def main():
    dry_run = "--dry-run" in sys.argv

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA busy_timeout=60000")

    affected = conn.execute("""
        SELECT COUNT(DISTINCT tt.rating_key)
        FROM track_tags tt
        JOIN tracks t ON t.rating_key = tt.rating_key
        WHERE t.real_artist IS NOT NULL
    """).fetchone()[0]

    total_resolved = conn.execute(
        "SELECT COUNT(*) FROM tracks WHERE real_artist IS NOT NULL"
    ).fetchone()[0]

    print(f"VA-resolved tracks total: {total_resolved}")
    print(f"Of those, currently tagged (will be cleared): {affected}")

    if dry_run:
        print("\nDRY RUN — nothing changed.")
        conn.close()
        return

    if affected == 0:
        print("\nNothing to clear.")
        conn.close()
        return

    conn.execute("""
        DELETE FROM track_tags
        WHERE rating_key IN (
            SELECT rating_key FROM tracks WHERE real_artist IS NOT NULL
        )
    """)
    conn.commit()
    conn.close()

    print(f"\nDone. Cleared tags for {affected} tracks.")
    print("They'll be picked up and correctly re-tagged (using the real")
    print("artist name) the next time plex_tag_tracks.py runs — either")
    print("via the admin button or the next Full Sync.")


if __name__ == "__main__":
    main()

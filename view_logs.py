#!/usr/bin/env python3.12
"""
MusicMind for Plex - Query Log Viewer (CLI)

Quick command-line view into query_log, since the web /logs page
isn't always the fastest way to check what just happened.

Usage:
    python3.12 view_logs.py                # last 10 queries, summary view
    python3.12 view_logs.py --limit 25      # last 25
    python3.12 view_logs.py --id 42         # full detail on one entry
                                             #   (prompt, tags, filters,
                                             #    raw OpenAI request/response)
    python3.12 view_logs.py --analyze 42    # WHY did this query return what
                                             #   it did — per-tag live match
                                             #   counts, active filters, and
                                             #   a live re-run of the exact
                                             #   same search right now
"""
import sys
import os
import sqlite3
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DB_PATH
from brain import search_tracks


def show_summary(conn, limit):
    rows = conn.execute("""
        SELECT id, timestamp, prompt, result_count, cost_usd, duration_ms, error
        FROM query_log
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()

    if not rows:
        print("No query log entries yet.")
        return

    print(f"{'ID':<5} {'Time':<20} {'Results':<8} {'Cost':<9} {'ms':<7} Prompt")
    print("-" * 90)
    for rid, ts, prompt, result_count, cost, duration_ms, error in rows:
        rc = str(result_count) if result_count is not None else "—"
        cost_str = f"${cost:.5f}" if cost is not None else "—"
        dur = str(duration_ms) if duration_ms is not None else "—"
        prompt_short = (prompt or "")[:40]
        flag = " ❌" if error else ""
        print(f"{rid:<5} {ts:<20} {rc:<8} {cost_str:<9} {dur:<7} {prompt_short}{flag}")

    print(f"\n{len(rows)} entries shown. Use --id N for full detail on one.")


def show_detail(conn, entry_id):
    row = conn.execute("""
        SELECT id, timestamp, prompt, tags, filters, result_count,
               duration_ms, error, openai_request, openai_response,
               prompt_tokens, completion_tokens, cost_usd
        FROM query_log
        WHERE id = ?
    """, (entry_id,)).fetchone()

    if not row:
        print(f"No query_log entry with id={entry_id}")
        return

    (rid, ts, prompt, tags, filters, result_count, duration_ms,
     error, openai_request, openai_response, prompt_tokens,
     completion_tokens, cost_usd) = row

    print("=" * 70)
    print(f"Query Log #{rid}  ({ts})")
    print("=" * 70)
    print(f"Prompt:       {prompt}")
    print(f"Tags:         {tags}")
    print(f"Filters:      {filters}")
    print(f"Result count: {result_count}")
    print(f"Duration:     {duration_ms} ms")
    if error:
        print(f"Error:        {error}")
    print(f"API stats:    {prompt_tokens} prompt tokens, "
          f"{completion_tokens} completion tokens, ${cost_usd:.6f}" if cost_usd is not None else "API stats:    n/a")
    print("-" * 70)
    print("Request sent to OpenAI:")
    print(openai_request or "(none)")
    print("-" * 70)
    print("Raw response from OpenAI:")
    print(openai_response or "(none)")
    print("=" * 70)


def show_analysis(conn, entry_id):
    """
    Explains WHY a query returned what it did: how many tracks each
    stored tag matches right now (live, not at query time — the
    library may have changed since), what filters were active, and a
    live re-run of the exact same search to show the current real
    result count.
    """
    row = conn.execute("""
        SELECT prompt, tags, filters, result_count
        FROM query_log WHERE id = ?
    """, (entry_id,)).fetchone()

    if not row:
        print(f"No query_log entry with id={entry_id}")
        return

    prompt, tags_json, filters_json, logged_count = row
    tags = json.loads(tags_json) if tags_json else []
    filters = json.loads(filters_json) if filters_json else {}

    print("=" * 70)
    print(f"Analyzing Query Log #{entry_id}: \"{prompt}\"")
    print("=" * 70)
    print(f"Logged result count (at the time): {logged_count}")
    print()

    if tags:
        print(f"Tags used ({len(tags)}) — live match count in track_tags:")
        for tag in tags:
            count = conn.execute(
                "SELECT COUNT(*) FROM track_tags WHERE tag LIKE ?",
                (f"%{tag}%",)
            ).fetchone()[0]
            flag = "  ⚠️  no tracks have this tag" if count == 0 else ""
            print(f"  {tag:<20} {count:>6} tracks{flag}")
    else:
        print("No tags were used for this query (filter-only or a search")
        print("intent that never called the tag classifier, e.g. title/")
        print("artist/year search or a lastfm: date query).")
    print()

    active_filters = {k: v for k, v in filters.items() if v not in (None, False, "")}
    if active_filters:
        print("Active filters:")
        for k, v in active_filters.items():
            print(f"  {k}: {v}")
    else:
        print("No filters were active beyond defaults.")
    print()

    print("Re-running this exact search RIGHT NOW (live, current library)...")
    try:
        live_tracks = search_tracks(tags, filters)
        print(f"  -> {len(live_tracks)} tracks match today")
        if logged_count is not None and len(live_tracks) != logged_count:
            print(f"  (differs from the {logged_count} logged at query time —")
            print(f"   library has changed since, or this run predates the")
            print(f"   result_count fix and was never accurately logged)")
    except Exception as e:
        print(f"  -> search_tracks() raised an exception: {e}")
    print("=" * 70)


def main():
    conn = sqlite3.connect(DB_PATH)

    if "--analyze" in sys.argv:
        entry_id = int(sys.argv[sys.argv.index("--analyze") + 1])
        show_analysis(conn, entry_id)
    elif "--id" in sys.argv:
        entry_id = int(sys.argv[sys.argv.index("--id") + 1])
        show_detail(conn, entry_id)
    else:
        limit = 10
        if "--limit" in sys.argv:
            limit = int(sys.argv[sys.argv.index("--limit") + 1])
        show_summary(conn, limit)

    conn.close()


if __name__ == "__main__":
    main()

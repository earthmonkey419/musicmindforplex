#!/usr/bin/env python3
"""
MusicMind for Plex - Playlist Generator
Generates playlists from natural language prompts + rule flags.
"""

import sqlite3
import argparse
from plexapi.server import PlexServer

from config import PLEX_URL, PLEX_TOKEN, MUSIC_LIB as MUSIC_LIBRARY, DB_PATH


def get_tracks(conn, keywords, args):
    # Build tag matching query
    keyword_conditions = " OR ".join(["tt.tag LIKE ?" for _ in keywords])
    keyword_params = [f"%{kw.lower()}%" for kw in keywords]

    query = f"""
        SELECT 
            t.rating_key,
            t.title,
            t.artist,
            t.album,
            t.genre,
            t.year,
            t.play_count,
            t.user_rating,
            COUNT(DISTINCT tt.tag) as match_score
        FROM tracks t
        LEFT JOIN track_tags tt ON t.rating_key = tt.rating_key
        WHERE ({keyword_conditions})
    """
    params = keyword_params

    if args.unplayed:
        query += " AND t.play_count = 0"

    if args.genre:
        query += " AND LOWER(t.genre) LIKE ?"
        params.append(f"%{args.genre.lower()}%")

    if args.min_year:
        query += " AND t.year >= ?"
        params.append(args.min_year)

    if args.max_year:
        query += " AND t.year <= ?"
        params.append(args.max_year)

    if args.min_plays is not None:
        query += " AND t.play_count >= ?"
        params.append(args.min_plays)

    if args.max_plays is not None:
        query += " AND t.play_count <= ?"
        params.append(args.max_plays)

    query += """
        GROUP BY t.rating_key
        ORDER BY match_score DESC, t.play_count ASC
        LIMIT ?
    """
    params.append(args.limit)

    return conn.execute(query, params).fetchall()


def create_plex_playlist(plex, name, rating_keys):
    music = plex.library.section(MUSIC_LIBRARY)

    # Fetch track objects from Plex by rating key
    tracks = []
    for rk in rating_keys:
        try:
            track = plex.fetchItem(int(rk))
            tracks.append(track)
        except Exception as e:
            print(f"  Warning: could not fetch track {rk}: {e}")

    if not tracks:
        print("No tracks could be fetched from Plex.")
        return

    # Delete existing playlist with same name if it exists
    for pl in plex.playlists():
        if pl.title == name:
            pl.delete()
            print(f"  Deleted existing playlist: {name}")

    playlist = plex.createPlaylist(name, items=tracks)
    print(f"\nPlaylist '{playlist.title}' created in Plex with {len(tracks)} tracks.")


def main():
    parser = argparse.ArgumentParser(
        description="MusicMind for Plex - Playlist Generator"
    )
    parser.add_argument("prompt", help="Natural language mood/vibe prompt")
    parser.add_argument("--unplayed", action="store_true", help="Only unplayed tracks")
    parser.add_argument("--limit", type=int, default=30, help="Max tracks (default 30)")
    parser.add_argument("--name", type=str, help="Playlist name (default: prompt)")
    parser.add_argument("--genre", type=str, help="Filter by Plex genre")
    parser.add_argument("--min-year", type=int, help="Minimum year")
    parser.add_argument("--max-year", type=int, help="Maximum year")
    parser.add_argument("--min-plays", type=int, help="Minimum play count")
    parser.add_argument("--max-plays", type=int, help="Maximum play count")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without creating playlist"
    )
    args = parser.parse_args()

    playlist_name = args.name or args.prompt
    keywords = [w for w in args.prompt.lower().split() if len(w) > 2]

    print(f"MusicMind for Plex - Playlist Generator")
    print("=" * 40)
    print(f"Prompt   : {args.prompt}")
    print(f"Keywords : {keywords}")
    print(f"Limit    : {args.limit}")
    if args.unplayed:
        print(f"Filter   : unplayed only")
    if args.genre:
        print(f"Filter   : genre = {args.genre}")
    if args.min_year:
        print(f"Filter   : year >= {args.min_year}")
    if args.max_year:
        print(f"Filter   : year <= {args.max_year}")
    if args.min_plays:
        print(f"Filter   : min plays = {args.min_plays}")
    if args.max_plays is not None:
        print(f"Filter   : max plays = {args.max_plays}")
    print()

    conn = sqlite3.connect(DB_PATH)
    tracks = get_tracks(conn, keywords, args)
    conn.close()

    if not tracks:
        print("No tracks matched. Try different keywords or fewer filters.")
        return

    print(f"Matched {len(tracks)} tracks:\n")
    for i, row in enumerate(tracks, 1):
        (
            rating_key,
            title,
            artist,
            album,
            genre,
            year,
            play_count,
            user_rating,
            match_score,
        ) = row
        print(
            f"{i:3}. [{match_score} match] {artist} - {title} ({year or '?'}) | plays: {play_count}"
        )

    if args.dry_run:
        print("\n[Dry run — no playlist created]")
        return

    print()
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    rating_keys = [row[0] for row in tracks]
    create_plex_playlist(plex, playlist_name, rating_keys)


if __name__ == "__main__":
    main()

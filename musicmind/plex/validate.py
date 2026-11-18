#!/usr/bin/env python3
"""
MusicMind for Plex - Connection Test v2
Walks artist -> album -> tracks to get fully loaded metadata.
"""

from plexapi.server import PlexServer

from config import PLEX_URL, PLEX_TOKEN, MUSIC_LIB as MUSIC_LIBRARY


def main():
    print("Connecting to Plex...")
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)
    print(f"Connected to: {plex.friendlyName}\n")

    music = plex.library.section(MUSIC_LIBRARY)

    print("Fetching artists...")
    artists = music.searchArtists(limit=3)
    print(f"Found {len(artists)} artists (showing first 3)\n")

    count = 0
    for artist in artists:
        for album in artist.albums():
            for track in album.tracks():
                genres = (
                    ", ".join([g.tag for g in artist.genres])
                    if artist.genres
                    else "none"
                )
                print(f"{count + 1}. {track.title}")
                print(f"   Artist : {artist.title}")
                print(f"   Album  : {album.title}")
                print(f"   Genre  : {genres}")
                print(f"   Rating : {track.userRating}")
                print(f"   Plays  : {track.viewCount}")
                print()
                count += 1
                if count >= 50:
                    break
            if count >= 50:
                break
        if count >= 50:
            break


if __name__ == "__main__":
    main()

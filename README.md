# 🎵 MusicMind for Plex
*formerly Plex Music Brain*

> The AI-powered music companion Plex should have built.

MusicMind for Plex connects your Plex music library to OpenAI and Last.fm to generate intelligent playlists, enrich your library with specific genre tags, analyze your listening history, and surface gaps in your collection.

Type "late night psychedelic soul" and get a playlist. Filter by female artists from the 70s. Find out you have scrobbled Stereolab 247 times but don't own a single album. It all runs on your NAS — no subscriptions, no cloud, your data stays yours.

---

## What it does

- Natural language playlists — "quiet and watery", "garagy grungy rock", "sunny day driving with the windows down". OpenAI expands your prompt into specific music tags and scores your library against them.
- AI genre enrichment — your entire library gets tagged with specific subgenres (shoegaze, dance-punk, balearic, cosmic disco, etc). Tags are stored in the MusicMind database and power the playlist generator. **Plex is not touched.** Optionally, you can write these tags back into Plex to enrich the Plexamp genre browser — but this is entirely optional and fully revertable.
- Last.fm integration — your scrobble history drives real play counts, listening patterns, and loved track ratings. Plex play counts are unreliable; Last.fm is not.
- Listening context playlists — "Your Afternoon" (what you actually play 1-5pm), "Weekend Flow", and "Often Together" (tracks that appear in the same listening session, cross-artist, album pairs excluded).
- Library gap analysis — artists you have scrobbled 50+ times that are not in your library, categorized into Worth Acquiring, Classical, Ambient/Meditation, and Unknown.
- Compilation enrichment — recovers real artist names from ID3 tags for "Various Artists" tracks. 30% of most libraries are compilations; now they are first-class citizens.
- Metadata filters — filter by gender, country, era, genre, year, play count, rating. "Female artists from Brazil in the 70s" is a valid query.
- Admin panel — one-click Full Sync pipeline: Plex scan, ingest, Last.fm, AI tag new tracks. Live streaming output.
- DB query console — run any SELECT query against your music database directly from the browser.

---

## Requirements

- Synology NAS (tested on DS920+, DSM 7.x) or any Linux box running Plex
- Python 3.12
- Plex Media Server
- OpenAI API key (see [OpenAI pricing](https://openai.com/pricing) for current rates)
- Last.fm account + free API key
- PM2 (for running the web app as a service)

---

## Quick Start

1. Install dependencies

    sudo python3.12 -m pip install plexapi openai flask mutagen --break-system-packages

2. Configure

    cp config.example.py config.py
    # Edit config.py with your Plex token, OpenAI key, Last.fm key

3. Initial setup (run once, in order)

    python3.12 plex_music_brain_ingest.py
    python3.12 plex_tag_tracks.py
    python3.12 enrich_artists.py
    sudo python3.12 enrich_compilations.py
    python3.12 lastfm_sync.py
    python3.12 lastfm_gaps.py
    python3.12 listening_context.py
    # Optional — writes AI genres back into Plex (Plexamp genre browser)
    # Skip these if you don't want to modify your Plex metadata
    sudo python3.12 write_genres_to_plex.py --test   # preview only, nothing written
    sudo python3.12 write_genres_to_plex.py --run    # actually writes to Plex
    # To undo: sudo python3.12 write_genres_to_plex.py --revert

4. Start the web app

    sudo pm2 start python3.12 --name "plex-music-brain" -- ~/plex_music_brain/web/app.py
    sudo pm2 save

5. Open in browser

    http://YOUR_NAS_IP:8787

---

## Getting your Plex token

1. Open Plex in your browser and play any item
2. Click ... -> Get Info -> View XML
3. Copy the X-Plex-Token value from the URL

---

## Cost

OpenAI API costs vary depending on your library size and usage. Initial tagging of a large library typically costs a few dollars; ongoing costs for new tracks are minimal. Last.fm API and everything else is free. See [OpenAI pricing](https://openai.com/pricing) for current rates.

---

## Project Structure

plex_music_brain/
    config.py                    Your credentials (never commit this)
    config.example.py            Template — copy to config.py
    brain.py                     Core engine: prompt expansion, search, playlist creation
    plex_music_brain_ingest.py   Pulls library from Plex into SQLite
    plex_tag_tracks.py           AI tags tracks via OpenAI
    enrich_artists.py            Enriches artists with gender, country, era metadata
    enrich_compilations.py       Recovers real artists from ID3 tags
    lastfm_sync.py               Syncs Last.fm scrobble history
    lastfm_gaps.py               Gap analysis
    listening_context.py         Context-aware playlists
    write_genres_to_plex.py      Writes AI genres back to Plex
    plex_playlist.py             CLI playlist generator
    web/
        app.py                   Flask web app (port 8787)
        templates/               HTML pages
        static/                  CSS

---

## Full Documentation

See PLEX-MUSIC-BRAIN.md for complete documentation including all script flags, database schema, Task Scheduler setup, known issues, and PM2 reference.

---

## Roadmap

- MusicBrainz integration for higher accuracy metadata
- Ollama support for local AI tagging (no OpenAI cost)
- Summer/seasonal listening playlists
- Rediscovery playlist — tracks you loved but have not played in 2+ years
- Polling-based admin jobs (fix Cloudflare SSE timeout)
- Mobile-optimized UI

---

## License

MIT — see LICENSE

Built by @earthmonkey419 (https://github.com/earthmonkey419)
https://github.com/earthmonkey419/musicmindforplex

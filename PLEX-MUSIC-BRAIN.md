# Plex Music Brain

An AI-enhanced music companion for Plex. Generates playlists from natural language prompts, enriches your library with specific genre tags, analyzes your listening history, and surfaces gaps in your collection.

Built for a Synology NAS running Plex. Self-hosted, self-contained, no subscriptions.

---

## Features

- Natural language playlist generation — "late night psychedelic soul", "sunny day driving with the windows down"
- AI genre enrichment — 15,000+ tracks tagged with specific subgenres (shoegaze, dance-punk, balearic, etc) and written back to Plex
- Last.fm integration — 111K+ scrobbles driving real play counts and listening patterns
- Listening context playlists — Your Afternoon, Weekend Flow, Often Together (based on actual behavior)
- Metadata filters — gender, country, era, genre, year, play count, rating
- Compilation enrichment — real artist names recovered from ID3 tags for Various Artists tracks
- Library gap analysis — artists you scrobble heavily but don't own, categorized and prioritized
- Admin panel — one-click sync pipeline with live streaming output
- DB query console — run any SELECT query against your music database
- Remotely accessible — via Cloudflare Tunnel

---

## Architecture

Plex Library
     |
     v
plex_music_brain_ingest.py --> plex_music_brain.db (SQLite)
                                        |
                          +-------------+-------------+
                          |             |             |
               plex_tag_tracks.py  lastfm_sync.py  enrich_*.py
               (AI genre tags)    (scrobble data)  (metadata)
                          |             |             |
                          +-------------+-------------+
                                        |
                                     brain.py
                                  (core engine)
                                        |
                          +-------------+-------------+
                          |                           |
                     Flask Web UI              plex_playlist.py
                  (playlist generator,          (CLI interface)
                   admin panel, gaps,
                   DB console)
                          |
                          v
                    Plex Playlists

---

## Requirements

- Synology NAS (tested on DS920+, DSM 7.x)
- Python 3.12 (install via Synology Package Center)
- Plex Media Server running on the NAS
- OpenAI API key (gpt-4o-mini, ~$2 for initial tagging of 15K tracks)
- Last.fm account + API key (free at last.fm/api)
- Cloudflare account + tunnel (optional, for remote access)

---

## Installation

1. Install Python dependencies
   sudo python3.12 -m pip install plexapi openai flask mutagen --break-system-packages

2. Copy all scripts to ~/plex_music_brain/
   Copy web files to ~/plex_music_brain/web/

3. Edit ~/plex_music_brain/config.py with your credentials

4. Initial database setup (run in order):
   python3.12 ~/plex_music_brain/plex_music_brain_ingest.py
   python3.12 ~/plex_music_brain/plex_tag_tracks.py
   python3.12 ~/plex_music_brain/enrich_artists.py
   sudo python3.12 ~/plex_music_brain/enrich_compilations.py
   python3.12 ~/plex_music_brain/lastfm_sync.py
   python3.12 ~/plex_music_brain/lastfm_gaps.py
   python3.12 ~/plex_music_brain/listening_context.py
   sudo python3.12 ~/plex_music_brain/write_genres_to_plex.py --test
   sudo python3.12 ~/plex_music_brain/write_genres_to_plex.py --run

5. Start the web app
   sudo pm2 start python3.12 --name "plex-music-brain" -- ~/plex_music_brain/web/app.py
   sudo pm2 save

6. Access
   Local:  http://YOUR_NAS_IP:8787
   Remote: https://YOUR_TUNNEL_DOMAIN

---

## Configuration

All credentials and paths live in: ~/plex_music_brain/config.py

  PLEX_URL    = "http://YOUR_NAS_IP:32400"
  PLEX_TOKEN  = "your-plex-token"
  MUSIC_LIB   = "Music"
  DB_PATH     = "~/plex_music_brain.db"
  OPENAI_KEY  = "YOUR_OPENAI_API_KEY"
  LASTFM_KEY  = "your-lastfm-api-key"
  LASTFM_USER = "YOUR_LASTFM_USERNAME"

Getting your Plex token:
  1. Open Plex in browser, play any item
  2. Click ... -> Get Info -> View XML
  3. Copy X-Plex-Token value from the URL

---

## Scripts Reference

plex_music_brain_ingest.py
  Pulls all tracks from Plex into SQLite. Incremental after first run.
  Run: python3.12 ~/plex_music_brain/plex_music_brain_ingest.py

plex_tag_tracks.py
  AI-tags tracks via OpenAI gpt-4o-mini. Skips already-tagged tracks.
  Run: python3.12 ~/plex_music_brain/plex_tag_tracks.py

enrich_artists.py
  Enriches artists with gender, country, era, group_type via OpenAI.
  Run: python3.12 ~/plex_music_brain/enrich_artists.py

enrich_compilations.py
  Reads TPE1 ID3 tags from Various Artists tracks to recover real artist names.
  Run: sudo python3.12 ~/plex_music_brain/enrich_compilations.py

lastfm_sync.py
  Pulls scrobble history and loved tracks from Last.fm.
  First run: full history. Subsequent runs: incremental.
  Run: python3.12 ~/plex_music_brain/lastfm_sync.py

lastfm_gaps.py
  Finds artists with 50+ scrobbles not in Plex library. Categorizes into 4 buckets.
  Run: python3.12 ~/plex_music_brain/lastfm_gaps.py

listening_context.py
  Builds three behavior-based playlists from scrobble history.
  Run: python3.12 ~/plex_music_brain/listening_context.py

write_genres_to_plex.py
  Appends top 3 AI-derived genre tags to every track in Plex. Fully revertable.
  Run: sudo python3.12 ~/plex_music_brain/write_genres_to_plex.py --test
       sudo python3.12 ~/plex_music_brain/write_genres_to_plex.py --run
       sudo python3.12 ~/plex_music_brain/write_genres_to_plex.py --revert

plex_playlist.py
  CLI playlist generator.
  Run: python3.12 ~/plex_music_brain/plex_playlist.py "late night jazz" --dry-run
       python3.12 ~/plex_music_brain/plex_playlist.py "psychedelic soul" --unplayed --limit 25
  Flags: --unplayed --limit N --name "name" --genre "genre" --min-year --max-year
         --min-plays --max-plays --dry-run

---

## Web UI Guide

URL: http://YOUR_NAS_IP:8787 or https://YOUR_TUNNEL_DOMAIN

### Playlist Generator (/)

Prompt (optional):
  Natural language mood/vibe. Examples:
    "late night psychedelic soul"
    "sunny day driving with the windows down"
    "garagy grungy rock"
    "quiet and watery"
  OpenAI expands prompt into 10-15 specific tags, matched against track_tags.

Filters:
  Unplayed only    play_count = 0
  Genre            AI tag dropdown (100 most common tags)
  From/To year     album release year range
  Limit            max tracks returned (default 30)
  Max per artist   prevents one artist dominating (default 3)
  Min rating       Plex star rating (4 stars = user_rating >= 8)
  Gender           female / male / mixed
  Country          US / UK / BR / FR / JP / AU / IE / CA / SE / DE
  Era              50s through 20s

Flow:
  1. Type prompt and/or set filters
  2. Click Preview (or press Enter)
  3. Review scored track list
  4. Edit playlist name if desired
  5. Click Create in Plex

### Library Gaps (/gaps)
  Artists with 50+ Last.fm scrobbles not in your Plex library.
  Four collapsible buckets: Worth Acquiring, Classical, Ambient/Meditation, Unknown.

### Admin Panel (/admin)
  Full Sync               Complete pipeline: scan -> ingest -> Last.fm -> tag
  Scan Plex Library       Triggers Plex to scan for new files on disk
  Sync Plex Library       Ingests tracks into SQLite (incremental)
  Sync Last.fm            Pulls new scrobbles since last sync
  Tag New Tracks          AI tags any untagged tracks
  Refresh Context         Rebuilds Your Afternoon, Weekend Flow, Often Together
  Refresh Gap Analysis    Re-runs gap analysis, removes acquired artists

  Note: Use direct IP for long-running jobs — Cloudflare times out SSE after ~100s.

### DB Query Console (/db)
  Run any SELECT query. Click hints to load examples. Ctrl+Enter to run.

---

## Database Reference

Location: ~/plex_music_brain.db
Mode: WAL (allows concurrent reads/writes)

Tables:
  tracks              16,000+ rows  Core library
  track_tags          ~90K rows     AI genre/mood tags
  artist_meta         2,595 rows    gender/country/era/group_type
  lastfm_scrobbles    111,788 rows  Full listening history
  lastfm_loved        22 rows       Loved tracks
  lastfm_meta         1 row         Last sync timestamp
  artist_gaps         308 rows      Gap analysis results
  track_sessions      13,201 rows   Session-split scrobbles
  track_cooccurrence  21,505 rows   Cross-artist session pairs
  genre_snapshot      ~15K rows     Original Plex genres backup
  meta                1 row         Last ingest timestamp

tracks columns:
  rating_key, title, artist, real_artist, album, genre, year, duration_ms,
  play_count, last_played, user_rating, added_at, genres_written, updated_at

Useful queries (also available as hints in DB Console):
  Top played:
    SELECT artist, title, play_count FROM tracks
    ORDER BY play_count DESC LIMIT 20

  Genre breakdown:
    SELECT tag, COUNT(*) as cnt FROM track_tags
    GROUP BY tag ORDER BY cnt DESC LIMIT 30

  Female artists:
    SELECT DISTINCT COALESCE(real_artist, artist) as artist FROM tracks t
    JOIN artist_meta m ON m.artist = COALESCE(t.real_artist, t.artist)
    WHERE m.gender = "female" ORDER BY artist

  Listening by year:
    SELECT strftime("%Y", datetime(timestamp, "unixepoch", "localtime")) as year,
    COUNT(*) as plays FROM lastfm_scrobbles GROUP BY year ORDER BY year

  Gap artists worth acquiring:
    SELECT artist, scrobbles FROM artist_gaps
    WHERE category = "worth_acquiring" ORDER BY scrobbles DESC

---

## Task Scheduler

DSM -> Control Panel -> Task Scheduler -> Create -> Scheduled Task -> User-defined script

Settings:
  User: root
  Schedule: every 2 hours

Command:
  python3.12 ~/plex_music_brain/plex_music_brain_ingest.py >> ~/plex_music_brain/ingest.log 2>&1 && python3.12 ~/plex_music_brain/lastfm_sync.py >> ~/plex_music_brain/lastfm.log 2>&1 && python3.12 ~/plex_music_brain/plex_tag_tracks.py >> ~/plex_music_brain/tagger.log 2>&1 && python3.12 ~/plex_music_brain/listening_context.py >> ~/plex_music_brain/context.log 2>&1

Logs:
  ~/plex_music_brain/ingest.log
  ~/plex_music_brain/lastfm.log
  ~/plex_music_brain/tagger.log
  ~/plex_music_brain/context.log

---

## PM2 Reference

  sudo pm2 status                        check all processes
  sudo pm2 restart plex-music-brain      restart after code changes
  sudo pm2 logs plex-music-brain         view logs
  sudo pm2 stop plex-music-brain         stop
  sudo pm2 save                          persist after changes

PM2 runs as root — always use sudo.
Install dependencies for root python3.12:
  sudo python3.12 -m pip install flask plexapi openai mutagen --break-system-packages

---

## Known Issues and Workarounds

Cloudflare SSE timeout
  Long-running admin jobs time out through Cloudflare after ~100 seconds.
  Workaround: use direct IP http://YOUR_NAS_IP:8787/admin for long jobs.

Plex duplicate tracks
  Same track may appear with different rating_keys due to multiple library folders.
  Handled by GROUP BY artist, title in queries.

Various Artists metadata
  Plex rolls compilation tracks up as "Various Artists".
  Fixed by enrich_compilations.py which reads real artist from TPE1 ID3 tag.
  Queries use COALESCE(real_artist, artist) as effective artist.

Last.fm name mismatches
  Artist names differ between Last.fm and Plex (e.g. "Netta" vs "Netta Barzilai").
  Gap cleanup uses fuzzy matching (substring) to handle this.

Broad Plex genres
  Plex uses ~14 broad genre buckets. AI tags in track_tags are the richer source.
  Genre dropdown in UI uses AI tags, not Plex genres.

Ratings sparse
  Only a handful of tracks rated in Plex. Play count from Last.fm is more useful.

---

## Roadmap

- Public release + GitHub
- Summer/seasonal listening playlists
- MusicBrainz integration for higher accuracy metadata
- Ollama for local AI tagging (reduce OpenAI costs)
- Polling approach for admin jobs (fix Cloudflare SSE timeout properly)
- Rediscovery playlist — heavily played tracks not heard in 2+ years
- Mobile-optimized UI

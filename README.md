# 🎵 MusicMind for Plex
*formerly Plex Music Brain*

![MusicMind for Plex — Dig into your stacks.](assets/og-image.jpg)

> **⚠️ Upgrading from v2? You must run a migration script before starting v3, or the app will refuse to start against your existing database rather than risk creating an empty one by mistake. See [Upgrading from v2](#upgrading-from-v2) below.**

> The AI-enhanced music companion Plex should have built.

[![Support MusicMind](https://img.shields.io/badge/%E2%9D%A4%EF%B8%8F_Support-MusicMind-c56fa4?style=for-the-badge)](https://www.paypal.com/ncp/payment/THHJJDVQRH366)

MusicMind for Plex connects your Plex music library to real audio analysis (Essentia), MusicBrainz, OpenAI, and Last.fm to generate intelligent playlists, measure the actual musical properties of your files, enrich your library with specific genre tags, analyze your listening history, and surface gaps in your collection.

Type "late night psychedelic soul" and get a playlist. Ask for an upbeat running mix around 170 BPM — measured from the audio, not guessed. Find out you have scrobbled Stereolab 247 times but don't own a single album. It all runs on your NAS — no subscriptions, no cloud audio processing, your data stays yours.

---

## What it does

- Natural language playlists — "quiet and watery", "garagy grungy rock", "sunny day driving with the windows down". OpenAI expands your prompt into specific music tags and scores your library against them.
- **Synapse — real audio analysis.** Measures tempo (BPM), musical key, and danceability from the actual audio of every track using Essentia, the open-source audio analysis library from the Music Technology Group at Universitat Pompeu Fabra. Deterministic signal processing on your own hardware — no cloud, no guessing. Resumable background runs with time estimates measured on your machine.
- **BPM and Danceability filters** on the playlist generator — powered by Synapse's measured data.
- **DJ-ify** — optional deterministic tempo-arc sequencing that reorders a playlist for flow using measured BPM and key.
- **Last.fm date search** — `lastfm:` prompts plus an **On This Day** picker that rebuilds what you were listening to on any date in your scrobble history.
- **The Collection** — a stats dashboard for your library and listening history: by era, by country, top artists, top genres, listening history by year.
- AI genre enrichment — your entire library gets tagged with specific subgenres (shoegaze, dance-punk, balearic, cosmic disco, etc). Tags are stored in the MusicMind database and power the playlist generator. **Plex is not touched.** Optionally, you can write these tags back into Plex to enrich the Plexamp genre browser — entirely optional and fully revertable.
- MusicBrainz artist enrichment — artist country, type, and metadata from the open MusicBrainz database, with an OpenAI fallback for artists it can't confidently match.
- Last.fm integration — your scrobble history drives real play counts, listening patterns, and loved track ratings. Plex play counts are unreliable; Last.fm is not.
- Listening context playlists — "Your Afternoon" (what you actually play 1-5pm), "Weekend Flow", and "Often Together" (tracks that appear in the same listening session, cross-artist, album pairs excluded).
- Library gap analysis — artists you have scrobbled 50+ times that are not in your library, categorized into Worth Acquiring, Classical, Ambient/Meditation, and Unknown.
- Compilation enrichment — recovers real artist names from ID3 tags for "Various Artists" tracks. 30% of most libraries are compilations; now they are first-class citizens.
- Metadata filters — filter by gender, country, era, genre, year, play count, rating, instrumental-only. "Female artists from Brazil in the 70s" is a valid query.
- Admin panel — one-click Full Sync pipeline: Plex scan, ingest, Last.fm, AI tag new tracks, plus Synapse analysis controls. Live streaming output.
- DB query console — run any SELECT query against your music database directly from the browser.

---

## Requirements

- Synology NAS (tested on DS920+, DSM 7.x) or any Linux box running Plex
- Python 3.12
- Plex Media Server
- OpenAI API key (see [OpenAI pricing](https://openai.com/pricing) for current rates)
- Last.fm account + free API key
- Essentia (for Synapse audio analysis) — `pip install essentia`
- PM2 (for running the web app as a service)

---

## Docker / Portainer

Prefer not to install Python dependencies directly on your NAS? See
**[DOCKER.md](DOCKER.md)** for a Docker/Portainer install — two
variants (slim / full), no manual `pip install` step. The Quick
Start below is for a direct, native install instead.

---

## Quick Start

1. Install dependencies

    sudo python3.12 -m pip install plexapi openai flask mutagen essentia --break-system-packages

2. Configure

    cp config.example.py config.py
    # Edit config.py with your Plex token, OpenAI key, Last.fm key

3. Initial setup (run once, in order)

    python3.12 musicmind_ingest.py
    python3.12 plex_tag_tracks.py
    python3.12 mb_enrich_artists.py
    python3.12 enrich_artists.py
    sudo python3.12 enrich_compilations.py
    python3.12 lastfm_sync.py
    python3.12 lastfm_gaps.py
    python3.12 listening_context.py
    # Synapse audio analysis (BPM / key / danceability) — start with an estimate
    python3.12 synapse_analyze.py --estimate
    python3.12 synapse_analyze.py            # or run from the admin page
    # Optional — writes AI genres back into Plex (Plexamp genre browser)
    # Skip these if you don't want to modify your Plex metadata
    sudo python3.12 write_genres_to_plex.py --test   # preview only, nothing written
    sudo python3.12 write_genres_to_plex.py --run    # actually writes to Plex
    # To undo: sudo python3.12 write_genres_to_plex.py --revert

4. Start the web app

    sudo pm2 start python3.12 --name "musicmind" -- ~/musicmind/web/app.py
    sudo pm2 save

**Viewing logs**

    pm2 logs musicmind                          # live, everything the app outputs
    tail -f ~/.pm2/logs/musicmind-out.log        # same thing, direct file
    tail -f ~/.pm2/logs/musicmind-error.log      # errors only

    tail -f ~/musicmind/fullsync_live.log        # just the current Full Sync run —
                                                  # survives a dropped connection, so
                                                  # this keeps updating even if the
                                                  # admin page loses its connection

5. Open in browser

    http://YOUR_NAS_IP:8787

---

## Upgrading from v2

**Run this once, before starting v3, if you have an existing v2
install.** v3 renamed the default database filename
(`plex_music_brain.db` → `musicmind.db`) — your existing `config.py`
and database file still use the old name until you migrate them.

```bash
python3.12 migrate_v2_to_v3.py
```

This renames your real database file, updates `DB_PATH` in
`config.py`, and backs up `config.py` first. Safe to run more than
once — if it detects you're already migrated, it exits immediately
with no changes.

**If you skip this:** the app won't silently create a fresh, empty
database in place of your real one. It'll refuse to start and print
a message pointing you back to this script — your existing library
data (tags, listening history, enrichment) is never at risk, it just
won't be usable until the migration runs.

Fresh installs (native or Docker) never hit this — it's specifically
for existing installs upgrading in place.

---

## Getting your Plex token

1. Open Plex in your browser and play any item
2. Click ... -> Get Info -> View XML
3. Copy the X-Plex-Token value from the URL

---

## Cost

OpenAI API costs vary depending on your library size and usage. Initial tagging of a large library typically costs a few dollars; ongoing costs for new tracks are minimal. Synapse audio analysis, MusicBrainz enrichment, and Last.fm are completely free and run locally. See [OpenAI pricing](https://openai.com/pricing) for current rates.

---

## Project Structure

musicmind/
    config.py                    Your credentials (never commit this)
    config.example.py            Template — copy to config.py
    brain.py                     Core engine: prompt expansion, search, playlist creation
    musicmind_ingest.py          Pulls library from Plex into SQLite
    plex_tag_tracks.py           AI tags tracks via OpenAI
    synapse_analyze.py           Synapse: BPM / key / danceability from audio (Essentia)
    mb_enrich_artists.py         MusicBrainz artist enrichment
    enrich_artists.py            AI fallback artist enrichment (gender, country, era)
    enrich_compilations.py       Recovers real artists from ID3 tags
    tag_instrumentals.py         Instrumental tagging
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

See USER-MANUAL.md for complete documentation including all script flags, database schema, Task Scheduler setup, known issues, and PM2 reference. See CHANGELOG.md for release history.

---

## Roadmap

- Voice/instrumental detection measured from the actual audio (replacing text-based guessing — in progress)
- Acoustic fingerprinting: resolve "Various Artists" tracks to their real performers, plus rigorous duplicate detection
- Docker installation
- Ollama support for local AI tagging (no OpenAI cost)
- Rediscovery playlist — tracks you loved but have not played in 2+ years
- Mobile-optimized UI

---

## License

MIT — see LICENSE

Built by @earthmonkey419 (https://github.com/earthmonkey419)
https://github.com/earthmonkey419/musicmindforplex

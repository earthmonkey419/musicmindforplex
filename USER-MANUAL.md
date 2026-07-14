# MusicMind for Plex — User Manual

*The AI-enhanced music companion your Plex library deserves.*
*Dig into your stacks.*

---

## What is MusicMind for Plex?

MusicMind for Plex is a self-hosted web app that brings AI-enhanced music discovery to your Plex library. It runs on your NAS alongside Plex and gives you a natural language playlist generator, deep listening history analysis, library gap detection, and more — all from a browser.

You type "late night psychedelic soul" and get a playlist. You ask for "female Brazilian artists from the 1970s" and it filters your library intelligently. You find out you've scrobbled Stereolab 247 times but don't own a single album. Your data stays on your hardware.

**MusicMind for Plex is not affiliated with or endorsed by Plex. Plex is a trademark of Plex, Inc.**

---

## Getting Started

### Requirements

- Synology NAS or any Linux box running Plex Media Server
- Python 3.12
- Plex Media Server
- OpenAI API key — see [openai.com/pricing](https://openai.com/pricing) for current rates
- Last.fm account + free API key (optional, but unlocks listening history features)
- PM2 (Node.js process manager)

### Installation

**1. Install Python dependencies**
```bash
sudo python3.12 -m pip install plexapi openai flask mutagen --break-system-packages
```

**2. Clone the repo**
```bash
git clone https://github.com/earthmonkey419/musicmindforplex.git ~/musicmind
```

**3. Configure**
```bash
cp ~/musicmind/config.example.py ~/musicmind/config.py
# Edit config.py with your credentials
```

**4. Run initial setup (in order)**
```bash
python3.12 ~/musicmind/musicmind_ingest.py             # Pull library into database
python3.12 ~/musicmind/plex_tag_tracks.py              # AI-tag your tracks
python3.12 ~/musicmind/enrich_artists.py               # Artist metadata
sudo python3.12 ~/musicmind/enrich_compilations.py     # Fix Various Artists
python3.12 ~/musicmind/lastfm_sync.py                  # Sync Last.fm (if configured)
python3.12 ~/musicmind/lastfm_gaps.py                  # Gap analysis (if Last.fm)
python3.12 ~/musicmind/listening_context.py            # Context playlists (if Last.fm)
sudo python3.12 ~/musicmind/write_genres_to_plex.py --test   # Preview genre write
sudo python3.12 ~/musicmind/write_genres_to_plex.py --run    # Write genres to Plex
```

**5. Start the web app**
```bash
sudo pm2 start python3.12 --name "musicmind" -- ~/musicmind/web/app.py
sudo pm2 save
```

**6. Open in browser**
```
http://YOUR_NAS_IP:8787
```

### Getting Your Plex Token

1. Open Plex in your browser and play any item
2. Click **...** → **Get Info** → **View XML**
3. Copy the `X-Plex-Token` value from the URL

### Getting a Last.fm API Key

1. Go to [last.fm/api/account/create](https://www.last.fm/api/account/create)
2. Fill in the form — it's free
3. Copy your API key into `config.py`

---

## The Interface

### Navigation

The top navigation bar has links to all sections:

| Link | Page | What it does |
|---|---|---|
| 📋 Missing From Your Collection | /gaps | Artists you scrobble heavily but don't own |
| 📊 The Collection | /stats | Your library and listening history at a glance |
| ⚙️ Admin | /admin | Back Office — sync, tag, and maintain your library |
| 🗄️ DB Console | /db | The Ledger — run SQL queries on your music database |
| 📋 Logs | /logs | Query logs with full OpenAI API detail |
| 🔄 Update | /update | Version info and update tools |

### Playlist Sidebar

On the left side of the main page is a scrollable list of all your Plex music playlists. 

- **Sort** by Recent (default), A-Z, or Track count using the dropdown
- **Click any playlist** to open it in the Plex web player
- The sidebar **refreshes automatically** when you create a new playlist

---

## Generating Playlists

### The Prompt Box

Type anything into the prompt box and hit **Preview**. MusicMind analyzes your prompt and figures out what you want:

**Mood or vibe:**
> "late night psychedelic soul"
> "grandma's birthday party"
> "driving to the airport to pick up my friend"
> "a watery theme"
> "warm Sunday morning music"

MusicMind identifies 2-3 specific vibes in your prompt and generates a tightly focused set of music tags. It searches your library for tracks that match those tags and returns the best results.

**Title search:**
> "songs with ocean in the name"
> "tracks with love in the title"

MusicMind detects that you're looking for specific words in track titles and searches directly — no AI tag expansion needed.

**Artist search:**
> "tracks by Miles Davis"
> "songs by The Beatles"

Searches your library for tracks by that specific artist.

**Demographic or filter queries:**
> "female artists from the 1970s"
> "female Brazilian artists"
> "jazz from the 50s"

MusicMind detects gender, country, era, and genre in your prompt and applies them as filters automatically.

### Filters

Below the prompt box are filters you can set manually. These combine with your prompt:

| Filter | What it does |
|---|---|
| **Unplayed only** | Only return tracks with 0 plays |
| **Instrumental only** | Only return tracks classified as instrumental |
| **Genre** | Filter or boost by genre tag. Decades (50s, 60s, 70s...) search artist era. Genres search AI tags. |
| **From year / To year** | Restrict to tracks from a year range |
| **Limit** | Maximum number of tracks to return (default 30) |
| **Tracks per artist** | Cap how many tracks from any one artist appear (default 1) |
| **Min rating** | Minimum star rating |
| **Gender** | Filter by artist gender (female, male, mixed) |
| **Country** | Filter by artist country of origin |
| **Era** | Filter by artist era (50s through 90s, 00s, 10s, 20s) |

> **Tip:** Filters combine with your prompt. "late night jazz" + Gender=female + Era=60s will find late night jazz tracks from female artists of the 60s.

> **Tip:** The Genre dropdown has two sections — **Decades** at the top (which search by artist era) and **Genres** below (which search AI tags). Selecting "1950s" from Decades finds tracks from 50s artists, not just tracks tagged "1950s".

### Creating a Playlist

After previewing results you like, type a name in the playlist name box and click **Create in Plex**. The playlist appears in Plex and Plexamp immediately, and the sidebar refreshes automatically.

---

## Missing From Your Collection

*Navigate: 📋 Missing From Your Collection*

Shows artists you've scrobbled 50 or more times on Last.fm that aren't in your Plex library. Time to go digging.

Artists are grouped into categories:
- **Worth Acquiring** — mainstream and well-known artists
- **Classical** — classical composers and performers
- **Ambient / Meditation** — ambient, new age, meditation music
- **Unknown** — artists that couldn't be categorized

Click any category header to expand or collapse it. Artists are sorted by scrobble count — most played first.

*Requires Last.fm to be configured.*

---

## The Collection

*Navigate: 📊 The Collection*

Your library and listening history at a glance — six charts:

| Chart | What it shows |
|---|---|
| **Listening History by Year** | Your scrobble count per year — your musical life story |
| **Top 10 Artists** | Most played artists in your library |
| **Top Genres** | Your top AI genre tags by track count |
| **Library by Era** | How many tracks from each decade |
| **Library by Country** | Top 10 countries of origin in your library |
| **Artists by Gender** | Breakdown of female, male, mixed, and unknown artists |

Hero stats at the top show total tracks, artists, scrobbles, and instrumentals.

---

## Back Office (Admin)

*Navigate: ⚙️ Admin*

One-click maintenance jobs. Each streams live output so you can watch progress.

> **Note:** Long-running jobs (Full Sync, Tag New Tracks) may time out if accessed through a reverse proxy or Cloudflare tunnel. For long jobs, use the direct IP address: `http://YOUR_NAS_IP:8787/admin`

| Button | What it does |
|---|---|
| **⚡ Full Sync** | Complete pipeline: scan Plex → ingest → sync Last.fm → tag new tracks |
| **🔍 Scan Plex Library** | Tells Plex to scan for new or changed files on disk |
| **🔄 Sync Plex Library** | Pulls all tracks from Plex into the database. Safe to re-run. |
| **🎵 Sync Last.fm** | Pulls new scrobbles since last sync. Updates play counts and loved tracks. |
| **🏷️ Tag New Tracks** | AI-tags any untagged tracks via OpenAI. Skips already-tagged tracks. |
| **🔗 Refresh Context Playlists** | Rebuilds Your Afternoon, Weekend Flow, and Often Together playlists |
| **🎼 Tag Instrumentals** | Uses OpenAI to classify tracks as instrumental or vocal |
| **📋 Refresh Gap Analysis** | Re-runs gap analysis against current library |

*Last.fm buttons only appear if Last.fm is configured in config.py.*

---

## The Ledger (DB Console)

*Navigate: 🗄️ DB Console*

A direct SQL console for your music database. SELECT queries only — no destructive queries allowed.

Click any **Example Query** to load it, then press **Ctrl+Enter** or click **Run Query** to execute.

Useful for exploring your data:
- What tags does a specific artist have?
- Which tracks have the most plays?
- How many tracks by country?

---

## Query Logs

*Navigate: 📋 Logs*

Shows the last 100 preview requests with full detail. Click any entry to expand:

- **Expanded Tags** — what MusicMind searched for
- **API Stats** — prompt tokens, completion tokens, cost, duration
- **Request Sent to OpenAI** — the exact prompt sent to the AI
- **Raw Response from OpenAI** — what came back
- **Filters Applied** — what filters were active

Useful for understanding why a query returned unexpected results, or for seeing what the AI thinks your prompt means.

---

## Update

*Navigate: 🔄 Update*

Shows your current installation version and update options.

**If installed via git clone:**
- **Check for Updates** — compares your version to the latest on GitHub
- **Update Now** — runs `git pull` and restarts the app (streams output)
- **Restart App** — restarts without pulling

**If installed manually:**
Manual update instructions are shown with step-by-step guidance.

---

## Context Playlists

These playlists are created in Plex automatically when you run **Refresh Context Playlists**:

### 🌅 Your Afternoon
Tracks you actually listen to between 1pm and 5pm, based on your Last.fm scrobble history. Weighted by how often each track appears in that time window.

### 🌊 Weekend Flow
Tracks you listen to on Saturdays and Sundays. Captures your weekend listening personality.

### 🔗 Often Together
Tracks that frequently appear in the same listening session, cross-artist. Album pairs are excluded so this captures genuine cross-genre affinities — the tracks that feel right together even though they're by different artists.

*All context playlists require Last.fm to be configured.*

---

## AI Genre Enrichment

Running `plex_tag_tracks.py` (or **Tag New Tracks** in Back Office) AI-tags every track in your library with specific subgenre and mood tags using OpenAI gpt-4o-mini.

**These tags are stored in the MusicMind database only. Plex is not touched.**

The tags power the Genre dropdown, the playlist generator's tag matching, and The Collection's genre chart — all without modifying your Plex library at all.

### Optional: Write Genres Back to Plex

If you *also* want to enrich the Plexamp genre browser, you can optionally write the top 3 AI tags back into each track's Plex genre field:

```bash
sudo python3.12 write_genres_to_plex.py --test   # preview only — nothing written
sudo python3.12 write_genres_to_plex.py --run    # actually writes to Plex
```

This is **completely optional** and **fully revertable**:

```bash
sudo python3.12 write_genres_to_plex.py --revert
```

Most users will want to skip this step and let MusicMind use its own database tags without touching Plex metadata.

---

## Instrumental Detection

Running `tag_instrumentals.py` (or Tag Instrumentals in Back Office) classifies every track as instrumental or vocal using a two-phase approach:

1. **Title heuristics** — instant, free. Detects patterns like "(instrumental)", "(karaoke)", "(no vocals)"
2. **OpenAI classification** — sends artist + title to gpt-4o-mini for AI classification

Once classified, you can:
- Check **Instrumental only** in the filters to restrict results
- Include "instrumental" or "no vocals" in your prompt — MusicMind detects this automatically

---

## Various Artists / Compilations

Running `enrich_compilations.py` reads the real artist names from ID3 tags on compilation tracks and stores them in the database. This means tracks credited to "Various Artists" in Plex will show their real artist in MusicMind search results and filters.

About 30% of most music libraries are compilation tracks — this makes them first-class citizens.

---

## Last.fm Integration

If you configure Last.fm in `config.py`, MusicMind syncs your scrobble history to drive:

- Real play counts (more reliable than Plex's own play counting)
- The **Unplayed only** filter
- **Missing From Your Collection** gap analysis
- **Your Afternoon**, **Weekend Flow**, **Often Together** context playlists
- **Listening History by Year** chart in The Collection

Run `lastfm_sync.py` for the first time to pull your full history (this may take a while for large accounts). Subsequent syncs are incremental.

---

## Automatic Scheduling

Set up Task Scheduler (on Synology DSM) or cron to run the sync pipeline automatically:

```bash
# Runs every 2 hours — ingest, Last.fm sync, tag new tracks, context playlists
python3.12 /path/to/musicmind/musicmind_ingest.py >> ~/ingest.log 2>&1 && \
python3.12 /path/to/musicmind/lastfm_sync.py >> ~/lastfm.log 2>&1 && \
python3.12 /path/to/musicmind/plex_tag_tracks.py >> ~/tagger.log 2>&1 && \
python3.12 /path/to/musicmind/listening_context.py >> ~/context.log 2>&1
```

---

## Tips & Tricks

**Get better results with specific vibes**
"Quiet and watery ambient jazz" will return better results than "jazz" — the more specific your vibe, the more focused the tags MusicMind generates.

**Combine prompt with filters**
The prompt and filters work together. "Late night jazz" + Gender=female + Era=60s finds late night jazz from female artists of the 60s era.

**Use the Logs page to debug**
If a query returns unexpected results, check the Logs page. You can see exactly what MusicMind sent to OpenAI and what tags it got back. This tells you whether the issue is the prompt, the tags, or the library.

**Try decade filters**
Select a decade from the Genre dropdown (50s, 60s, 70s...) to browse music by era. These filter by artist era rather than release year, so a 1990 reissue of a 1950s album still counts as 50s.

**0 results?**
If you get 0 results, try removing filters one at a time. A very specific combination of filters and prompt may not match anything in your library — that's honest! The Missing From Your Collection page might tell you what to buy.

---

## Troubleshooting

**500 error on startup**
Check PM2 logs: `sudo pm2 logs musicmind --lines 20`
Usually a missing import or config error.

**Long-running jobs time out**
Use the direct IP address for admin jobs instead of a domain/tunnel URL:
`http://YOUR_NAS_IP:8787/admin`

**Various Artists still showing**
Run `enrich_compilations.py` with `sudo` — it needs filesystem access to read ID3 tags.

**0 tracks matched**
- Try removing filters
- Try a more specific mood prompt
- Check the Logs page to see what tags were generated
- Your library may genuinely not have matching tracks — check Missing From Your Collection

**Last.fm not syncing**
Check your `LASTFM_KEY` and `LASTFM_USER` in `config.py`. Test with:
```bash
python3.12 lastfm_sync.py
```

**Database locked error**
This usually resolves itself. WAL mode is enabled to handle concurrent access. If persistent, restart the app: `sudo pm2 restart musicmind`

---

## Credits & License

MusicMind for Plex is built and maintained by [@earthmonkey419](https://github.com/earthmonkey419).

MIT License — free to use, modify, and distribute.

GitHub: [github.com/earthmonkey419/musicmindforplex](https://github.com/earthmonkey419/musicmindforplex)
Showcase: [musicmind.vp-fun.com](https://musicmind.vp-fun.com)

Part of the [Verbena Projects](https://verbenaprojects.com) family · [vp-fun.com](https://vp-fun.com)

---

*MusicMind for Plex is not affiliated with or endorsed by Plex. Plex is a trademark of Plex, Inc.*

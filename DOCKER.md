# Running MusicMind for Plex with Docker

## Choosing slim vs. full

**Slim** (default): plain `essentia`. Synapse's core measurement —
real BPM, key, and danceability from the actual audio — works
immediately. Voice/Instrumental detection (VI) is unavailable.

**Full**: adds `essentia-tensorflow` (a genuinely large dependency —
real TensorFlow, hundreds of MB) so VI becomes capable. The actual
VI model file is *not* baked into either image — it's a CC BY-NC-SA
licensed file, downloaded automatically on first boot directly from
essentia.upf.edu (the original source) into a persistent volume,
never redistributed as part of this image.

If you're not sure, start with slim. Each variant is its own
independent Portainer stack with its own data volume, so testing
both side by side never risks cross-contaminating either one. If you
later want to move from slim to full and carry your existing
database over instead of starting fresh, that's a manual step (stop
the slim stack, point the full stack's `musicmind_full_data` volume
at the same underlying data) — not automatic with this setup, since
keeping the two fully isolated by default is safer for real testing.

## Quick start — Portainer

**Use the Repository method, not Web editor.** This compose file
builds its own image from the Dockerfile in this repo (`build:
context: .`) — that build needs the actual `Dockerfile`,
`requirements.txt`, and `docker-entrypoint.sh` files on disk, not
just the compose YAML's text. Pasting the compose file into
Portainer's Web editor gives Portainer only that text, with none of
the files the build actually needs — it'll fail with an error like
`failed to read dockerfile: ... no such file or directory`. The
Repository method has Portainer clone the whole repo itself, so
every file the build needs is actually present.

1. In Portainer: **Stacks** (left sidebar) → **Add stack**.
2. Name it (e.g. `musicmind-slim` or `musicmind-full`).
3. Under **Build method**, choose **Repository** (not Web editor).
   Fill in:
   - **Repository URL:**
     `https://github.com/earthmonkey419/musicmindforplex.git`
   - **Repository reference:** `refs/heads/v3-dev`
   - **Compose path:** `docker-compose.slim.yml` **or**
     `docker-compose.full.yml` (not both — they're separate stacks
     by design, not one combined file, so you can run either
     independently and switch later without conflict)
4. Portainer should detect the `${VARIABLE}` placeholders and show an
   **Environment variables** section below the pasted YAML — fill in
   the real values there, never in the pasted YAML itself.

   **This section expects plain `KEY=VALUE` lines — one variable per
   line, no dashes, no `$`, no quotes.** It's easy to accidentally
   paste the YAML's own `environment:` block instead (the part
   inside the compose file that looks like `- PLEX_URL=${PLEX_URL}`)
   — don't do that; it'll fail with an error like `key cannot
   contain a space`, since Portainer is reading `- PLEX_URL` as one
   malformed key. Correct format looks like this:

   ```
   PLEX_URL=http://10.0.0.251:32400
   PLEX_TOKEN=your-real-plex-token
   OPENAI_KEY=sk-proj-your-real-key
   MUSIC_PATH=/volume1/your/real/music/folder
   MUSIC_LIB=Music
   MUSICMIND_PORT=7787
   LASTFM_KEY=
   LASTFM_USER=
   PATH_MAP_JSON={}
   ```

   - `PLEX_URL`, `PLEX_TOKEN`, `OPENAI_KEY` — required
   - `MUSIC_PATH` — required; the real folder on this host where your
     music lives (see the mount note inside the compose file for the
     one detail that actually matters — it needs to match Plex's own
     reported path). **If Plex itself also runs in its own Docker
     container** (not natively on this host), the path Plex reports
     for a track (via Get Info → View XML, look for the `file="..."`
     attribute) is very likely *not* a real host path — it's whatever
     internal mount name Plex's own container uses (commonly
     `/music`). In that case, run `docker inspect <your-plex-
     container-name>` and look for the `Mounts` section — the real
     host path is the `Source` value paired with a `Destination` of
     whatever Plex reported (e.g. `/music`). Use that real `Source`
     path as `MUSIC_PATH`, and see `PATH_MAP_JSON` below to bridge
     the difference.
   - `MUSICMIND_PORT` — only if something else on this host already
     uses 8787 (e.g. an existing native install)
   - `MUSIC_LIB` — the exact Plex library **section** name (visible
     under Settings → Manage → Libraries in Plex's own web app, not
     any nickname or server name shown elsewhere in Plex's UI).
     Defaults to `Music` if left blank, which covers most setups.
   - `LASTFM_KEY`, `LASTFM_USER` — optional, leave blank to disable
     Last.fm features
   - `PATH_MAP_JSON` — optional, only needed if Plex's reported path
     doesn't match a real host path (see the Plex-in-Docker note
     above). Example: `{"/music": "/volume1/your/real/music/folder"}`
   - If your Portainer version doesn't auto-detect the variables,
     add them manually as the same names shown above, same
     `KEY=VALUE` format

   **⚠️ All four required variables — `PLEX_URL`, `PLEX_TOKEN`,
   `OPENAI_KEY`, `MUSIC_PATH` — must have a real value before you
   deploy.** Unlike the optional ones, there's no fallback default
   for these, and `MUSIC_PATH` in particular is used directly inside
   the file-sharing (volume) setup — if it's left blank, Docker
   itself will reject the whole deploy with an error like:

   ```
   invalid spec: ::ro: empty section between colons
   ```

   That error is confusing on its own, but it means exactly one
   thing: `MUSIC_PATH` was left empty. Go back to the Environment
   variables section, fill it in with the real path (e.g.
   `/volume1/music`), and redeploy.
5. **Deploy the stack.** Watch the container's logs from Portainer's
   own Containers view for the first-run output — on full, you
   should see the VI model download happen automatically.
6. **Run initial setup before visiting the app.** A freshly deployed
   container has an empty database — no tables exist yet. Visiting
   the app before this step will show a **500 error**; the container
   logs (Portainer → Containers → `musicmind-slim` or `-full` →
   Logs) will show `sqlite3.OperationalError: no such table: tracks`.
   That error means exactly this — run initial setup, not a sign
   anything is broken. From Portainer's Console (or `docker exec -it
   musicmind-slim sh` from the command line), run once, in order:

   ```bash
   python3 musicmind_ingest.py
   python3 plex_tag_tracks.py
   python3 mb_enrich_artists.py
   python3 enrich_artists.py
   python3 enrich_compilations.py
   python3 lastfm_sync.py
   python3 lastfm_gaps.py
   python3 listening_context.py
   ```

   The 500 error clears as soon as `musicmind_ingest.py` finishes
   (it's the one that creates the `tracks` table) — you don't need
   to wait for the rest to reload the page, though the rest fill in
   tagging, enrichment, and Last.fm data and are worth letting run
   to completion before real use. Same commands, same order, as the
   native README's Quick Start — just run inside the container
   instead of directly on the host.
7. Visit `http://YOUR_HOST:PORT` and `.../admin` to run your first
   Full Sync.

## Quick start — command line

If you'd rather use `docker compose` directly instead of Portainer:

```bash
export PLEX_URL=http://YOUR_NAS_IP:32400
export PLEX_TOKEN=YOUR_PLEX_TOKEN
export OPENAI_KEY=sk-proj-YOUR_KEY
export MUSIC_PATH=/path/to/your/real/music/folder
docker compose -f docker-compose.slim.yml up -d --build
docker compose -f docker-compose.slim.yml logs -f
```
(swap in `docker-compose.full.yml` for the full variant)

## Getting your Plex token

See the main README for the standard way to find your Plex token
(via any existing media file's "Get Info" → "View XML" in the Plex
web app, or Plex's own support article on the subject).

## Environment variables reference

| Variable | Required | Notes |
|---|---|---|
| `PLEX_URL` | Yes | e.g. `http://10.0.0.251:32400` |
| `PLEX_TOKEN` | Yes | |
| `OPENAI_KEY` | Yes | `sk-proj-...` |
| `MUSIC_PATH` | Yes | The real folder on this host where your music lives — see the mount note in the compose file for the one detail that actually matters (needs to match Plex's own reported path) |
| `MUSICMIND_PORT` | No | Defaults to `8787`. Only set this if something else on this host already uses that port (e.g. an existing native install) |
| `MUSIC_LIB` | No | Defaults to `Music` |
| `LASTFM_KEY` | No | Leave unset to disable Last.fm features |
| `LASTFM_USER` | No | |
| `PATH_MAP_JSON` | No | Only needed if Plex's reported paths can't match this container's mount directly — see the compose file's comment. JSON object, e.g. `{"J:\\Music": "/mnt/j/Music"}` |

If you'd rather manage `config.py` yourself instead of environment
variables, mount your own pre-filled file directly to `/app/config.py`
— `docker-entrypoint.sh` only ever generates one if none already
exists, and never overwrites a file that's already there.

## Volumes

- `musicmind_slim_data` / `musicmind_full_data` — the real database,
  survives rebuilds and upgrades. Back this up like you would any
  real data. Named separately per variant since they're now
  independent stacks — see the note above about switching variants
  later if you want one to carry over the other's data instead.
- `musicmind_full_models` — full variant only. The downloaded VI
  model. Deleting this volume just means it re-downloads on the
  next start.
- Your music library — mounted **read-only**. This app never writes
  to your music files.

## Running scripts manually inside the container

Everything documented in the Guide's CLI Commands section works the
same way here, just prefixed with `docker exec` (container name is
`musicmind-slim` or `musicmind-full`, matching whichever you deployed):

```bash
docker exec -it musicmind-slim python3 resolve_recording_mbids.py --dry-run
docker exec -it musicmind-slim python3 lastfm_sync.py --rematch
```

## Troubleshooting

**"No module named 'essentia'" or a shared library error on first
Synapse/VI run** — essentia is a compiled C++ library, and its own
build documentation lists real system dependencies (`libfftw3`,
`libyaml`, `libsamplerate`, `libtag`, `libsndfile`, and similar).
The Dockerfile deliberately doesn't guess at these package names up
front, since a wrong version number would break the entire build.
If you hit this:
```bash
docker exec -it musicmind-full python3 -c "import essentia"
```
Whatever the real error names as missing, install the runtime
package for it (not the `-dev` version) in the Dockerfile's
`apt-get install` line and rebuild. Worth reporting back what was
actually needed, so the Dockerfile can be updated for everyone.

## A few honest things worth knowing

- This container runs as `root`, matching how this app already runs
  in its existing real-world deployment (a Synology NAS via pm2) —
  a deliberate choice for this first Docker release, not an
  oversight. A more hardened non-root setup is a reasonable future
  improvement once this base path is proven working across real
  installs.
- The app runs its own built-in Flask development server directly
  (matching its existing production behavior) rather than a
  separate production WSGI server — consistent with how it already
  runs today, not a new architectural decision introduced here.
- This has been tested thoroughly at the logic level (the entrypoint
  script's real behavior, every real Python dependency verified
  against actual imports, YAML syntax validated) but **not yet
  through an actual `docker build`**, since Docker isn't available
  in the environment this was built in. The first real build should
  be treated as the real test — if anything surfaces, it's genuinely
  useful information, not a sign anything was rushed.

# Changelog

All notable changes to MusicMind for Plex are documented here.

## [Unreleased]

## [3.1.2] — 2026-11-09

### Added
- **Gospel genre bucket.** Traditional, contemporary, southern, soul and
  country gospel (and related tags) now have their own bucket for Genre
  focus. The plain `gospel` tag used to sit inside Soul / Funk / R&B,
  which left gospel hard to reach on its own. Gospel-influenced R&B stays
  in Soul / Funk / R&B.
- **Richer Data Integrity Checks on the Tests page.** A failing check now
  shows a breakdown of what is wrong, a sample of the affected rows and
  suggested repair steps. The checks still only read your database; the
  repair steps are for you to run yourself.
- `artist_meta.mb_country_checked_at`: a marker, added automatically the
  next time MusicBrainz enrichment runs, recording that an artist's
  country has been looked up. The "every MBID has a country" check uses
  it so artists MusicBrainz has no country for stop failing the check.

### Changed
- In-app guide: the Tests page section describes the new check output.
- Docs: added the Pipeline Lifecycle scope doc for v4.

## [3.1.1] — 2026-11-09

### Fixed
- **Upgrading from 3.0 with "Update Now" or `git pull` no longer breaks
  country features.** 3.1.0 made `pycountry` a hard import, but Update
  Now only pulls code and never installs packages, so the Stats page,
  the Country dropdown and the country filter errored until you ran
  `pip install -r requirements.txt`. They now keep working without it
  (country *codes* like "IN" stay unconverted and a warning is logged)
  and become fully correct once `pycountry` is installed.

### Changed
- In-app guide: Quick Start now installs `pycountry`; added Resync Item
  and the ID3 compilation step to Back Office; the Country filter and
  genre-bucket descriptions are current; the Update section now says to
  check the changelog for new dependencies.
- Docs: Resync Item is described correctly as re-pulling one
  artist/album's metadata.

## [3.1.0] — 2026-11-09

### ⚠️ Upgrade notes

- **New dependency: `pycountry`.** Run `pip install -r requirements.txt`.
  Docker users must rebuild the image.
- **DJ-ify is now always on.** The UI toggle is gone; every generated
  playlist gets tempo-arc sequencing.

### Added
- **Chant / Choral / Sacred genre bucket**, so chant, choral and sacred
  tracks are no longer invisible to Genre-focus filtering.
- **Country filter normalization.** The Country dropdown is now built
  from your data, and a canonical alias map (backed by `pycountry`)
  reconciles full country names, ISO codes and city-level values, so
  e.g. India and "US"/"United States" each show up once and filter
  correctly. The selected country is also included in auto-generated
  playlist names.
- **Resync Item** admin tool and `resync_item.py`, to re-pull one
  artist/album's metadata from Plex without a full re-ingest.
- `make_plex_token.py` -- creates a dedicated Plex token for MusicMind
  (registered as its own device in Plex's Authorized Devices) instead of
  copying one out of Plex Web, whose token dies when that browser signs
  out. `--write` updates `config.py` with a timestamped backup.
- `restore_real_artist_from_va_results.py` -- recovers `real_artist`
  values from the `va_results` audit table.
- Mobile/PWA icons and manifest, plus Open Graph / Twitter Card tags on
  all app pages.

### Changed
- The stats page "Library by Country" chart uses the canonical country
  map and no longer hides every other label.
- Admin pages: unified navigation order and "Back to the Stacks" links.
- Docs (README, USER-MANUAL, DOCKER, in-app guide) now point to
  `make_plex_token.py` for getting a token.
- License holder is now Verbena Projects LLC.
- `.gitignore` and `.dockerignore` now cover `*.bak-*` backups.

### Fixed
- **Full Sync no longer wipes `is_instrumental`, `real_artist` or
  `genres_written`.** The ingest upsert now preserves analysis results.
  The old unsafe `INSERT OR REPLACE` ingest script is deprecated and
  renamed `plex_music_brain_ingest.py.DEPRECATED-unsafe-upsert`.
- Incremental ingest, Various Artists resolution fallback and
  MusicBrainz retry gaps in metadata sync.
- "Various Artists" / "Unknown Artist" placeholders are excluded from
  artist enrichment.
- The OpenAI fallback no longer skips artists that have an MBID but a
  NULL country.
- Genre-only prompts (e.g. "samba rock") no longer fall through to
  unfiltered results.
- OpenAI rate limits (HTTP 429) and other upstream errors on `/preview`
  now return a clear message and the right status code instead of a
  generic HTTP 500.

## [3.0.0] — 2026-08-16

### ⚠️ Breaking change — database filename

The default database filename changed from `plex_music_brain.db` to
`musicmind.db`, matching the app's rebrand. **Existing v2 installs
must run the migration script before starting v3** — see
[Upgrading from v2](README.md#upgrading-from-v2) in the README.

Fresh installs are unaffected; this only matters for existing
installs upgrading in place.

### Added
- **Docker support** — two variants (slim / full), deployable via
  Portainer or `docker compose`. See [DOCKER.md](DOCKER.md).
- `migrate_v2_to_v3.py` — one-time migration script for existing v2
  installs (renames the database file, updates `config.py`, backs
  up before touching anything, safe to run more than once).
- A startup guard now refuses to silently create a fresh, empty
  database if an unmigrated v2 database is found sitting next to
  where the new one should be — points you at the migration script
  instead of letting your real library data look like it vanished.

## [2.0.0] — 2026-07-07

### Added
- **Synapse** — real audio analysis via Essentia. Measures tempo (BPM),
  musical key, and danceability directly from your audio files. Fully
  local, no API cost. Includes a dedicated dashboard with Count,
  Estimate, Limited Run, and Full Run modes, persistent error logging,
  and a live status indicator.
- **BPM and Danceability filters** on the main playlist generator,
  using real distribution data from full-library analysis to set
  sensible range boundaries.
- **DJ-ify** — optional deterministic tempo-arc sequencing for
  generated playlists (ascend to a peak, then descend).
- **Last.fm date search**, two ways:
  - Typed: `lastfm: played in december 2023` — natural language date
    range parsing.
  - **On This Day** — a date-picker control that returns tracks
    scrobbled within an 8-day window around a chosen date, with no AI
    call involved.
- New Guide sections for Synapse and Last.fm search.

### Fixed
- Stats page: gender chart was silently splitting into duplicate
  categories due to inconsistent capitalization between two different
  enrichment sources. Normalized at the source and backfilled.
- Stats page: Top 10 Artists chart was silently dropping to 5 labels
  due to Chart.js's default label-skipping behavior on longer artist
  names.
- Stats page: Top Genres chart legend was truncating multi-word tags
  (e.g. "art rock" and "art pop" both showing as just "art").
- Playlist sidebar links were broken for every user except the
  original developer — the Plex server's machine ID was hardcoded
  instead of fetched dynamically.
- Synapse's Full Run could be silently killed by an app restart —
  now runs fully detached from the web app's process.
- Synapse could report a stale "running" status after a process was
  manually killed, due to a liveness check that didn't account for
  processes owned by a different user.
- Synapse occasionally logged legitimate, healthy tracks as permanent
  failures due to transient database lock collisions with the
  scheduled sync job — these now retry automatically instead.
- A handful of silent/unanalyzable audio tracks were producing
  physically implausible BPM readings (e.g. 738 BPM) that got stored
  as valid data — now caught and flagged for review instead.

### Changed
- "AI-powered" language updated to "AI-enhanced" throughout the docs
  and app.

## [1.0.0] — 2026-06-09

Initial public release. Natural language playlist generation, AI
genre tagging, Last.fm integration, MusicBrainz artist enrichment,
library gap analysis, instrumental detection, and The Collection
stats dashboard.

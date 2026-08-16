# Changelog

All notable changes to MusicMind for Plex are documented here.

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

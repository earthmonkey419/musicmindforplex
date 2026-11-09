# v4 Scope: Country Filter — Data Normalization + Dynamic Dropdown

**Status:** Scoped, not started. First v4 item — branched as `v4-dev`
off `main` (`d47ee9d`).

## The real problem this solves

Found while investigating a simple-sounding question: why isn't India
in the Country filter dropdown? The actual answer turned out to be
three separate, real bugs stacked on top of each other, not one
missing `<option>` tag.

**Bug 1 — the dropdown is hardcoded, not data-driven.** Confirmed
directly in `web/templates/index.html`: 10 countries (US, UK, Brazil,
France, Japan, Australia, Ireland, Canada, Sweden, Germany) typed
manually into the `<select>`, unlike the Genre dropdown, which is
already populated dynamically from real tag data via `/genres`. This
is the same class of bug the Country / Americana / Bluegrass bucket
fix (2026-08-09, `6482b85`) already found and fixed once for genre
buckets — hardcoded template options silently invisible to users
regardless of what the backend/database actually contains.

**Bug 2 — the two enrichment paths write country in different
formats, and the filter only handles one.** Confirmed directly in
source:
- `mb_enrich_artists.py` (the primary, free path) writes
  `country = area.get("name")` — full names like "United Kingdom,"
  "Brazil," "Greece."
- `enrich_artists.py`'s OpenAI fallback (only runs when MusicBrainz
  can't confidently match) writes 2-letter ISO codes per its own
  prompt instruction — "US," "UK," "BR."
- The filter query in `brain.py` does `am.country IN (?, ?)` with
  only a UK/GB alias pair — an exact string match expecting ISO
  codes. Selecting "Brazil" from the old hardcoded dropdown sends
  `"BR"`, but most Brazil-tagged rows say `"Brazil"`. No match.

This means the Country filter has likely been silently failing for
the majority of the library — not a missing-option problem, a
broken-matching problem — for as long as MusicBrainz has been the
primary enrichment path.

**Bug 3 — `area.get("name")` isn't reliably country-level.** Real
production data (`artist_meta`, confirmed via direct query,
2026-08-27):

```
United States|2107    US|161      Germany|120    Canada|94
United Kingdom|748    UK|20       Sweden|72      Netherlands|54
Brazil|49              France|47   Italy|39       Jamaica|33
Japan|27               India|26    Denmark|24     Belgium|20
Ireland|19              England|17  New York|15    Los Angeles|14
Spain|13                Norway|13   London|12      New Zealand|11
Austria|11               Nashville|10  JM|9        GB|9
CA|9                     South Korea|7  Romania|7   DE|7
Switzerland|6            Singapore|6  Israel|6      Greece|6
[Worldwide]|5            Russia|5    Puerto Rico|5
```

Three distinct problems visible in this one query:
1. **Same country, multiple strings** — United States/US (2268
   combined), United Kingdom/UK/GB/England (794 combined).
2. **City-level values, not countries** — New York, Los Angeles,
   London, Nashville. MusicBrainz's `area` field is whatever the
   artist's most specific "begin area" is — not guaranteed to be
   country-level.
3. **A non-country marker** — `[Worldwide]` is MusicBrainz's own
   special value for artists without a fixed geographic origin, not
   a real country.

India is confirmed present and correctly enriched — 26 real artists,
clean data, zero variant spellings found. It was never a data gap.
It was invisible for the same structural reason "Brazil" silently
returns wrong results today.

## Proposed fix — three parts

### 1. Dynamic dropdown, same pattern as `/genres`

New `/countries` endpoint in `web/app.py`, same shape as the
existing `/genres` route (`sqlite3` connection, `busy_timeout`,
`GROUP BY`, `ORDER BY cnt DESC`) — but grouping by *canonical* name,
not raw stored value, so "United States" and "US" collapse into one
entry instead of showing as two.

`web/templates/index.html`'s `<select id="country">` loses its
hardcoded options (keeping only `Any`) and gets a `loadCountries()`
function mirroring the existing `loadGenres()` — fetch, sort
alphabetically, populate `<option>` elements with real counts.

### 2. A canonical alias map, not a DB rewrite

Deliberately **not** proposing an `UPDATE artist_meta SET country =
...` rewrite against production data — too blunt an instrument for a
field with city-level noise mixed in, and not reversible without a
backup step this doc hasn't scoped yet. Instead, a small Python
mapping table (covering every value actually seen in the query
above, since "measure, don't guess" applies here same as everywhere
else this project has used it):

```python
COUNTRY_ALIASES = {
    "United States": ["United States", "US", "New York", "Los Angeles", "Nashville"],
    "United Kingdom": ["United Kingdom", "UK", "GB", "England", "London"],
    "Canada": ["Canada", "CA"],
    "Germany": ["Germany", "DE"],
    "Jamaica": ["Jamaica", "JM"],
    # ... one entry per canonical country, remaining values map 1:1
}
```

Used in two places:
- `/countries` endpoint groups raw values into canonical buckets
  before counting, so the dropdown shows one clean entry per real
  country.
- `brain.py`'s filter query expands a canonical selection into its
  full alias list in the `IN (...)` clause, instead of today's
  hardcoded UK/GB-only pair — so selecting "United States" correctly
  matches rows stored as either "United States" or "US."

`[Worldwide]` is deliberately excluded from the canonical map
entirely — not a country, not filterable.

### 3. Stop the drift going forward

`enrich_artists.py`'s OpenAI prompt currently instructs `country:
2-letter ISO country code`. Change it to request full country names
matching MusicBrainz's own convention, so future OpenAI-fallback
enrichments stop introducing new format variants. This doesn't fix
already-enriched rows (handled by the alias map above) but stops the
split from getting wider with every new artist OpenAI resolves.

## What this deliberately does NOT solve

- **Retroactive cleanup of city-level values in the database itself**
  — New York/Los Angeles/London/Nashville stay as-is in
  `artist_meta`; the alias map folds them into their country for
  filtering purposes only, it doesn't correct the underlying stored
  value. A real fix for *that* would mean re-deriving country from
  MusicBrainz's actual country-level area hierarchy (not just
  whatever `area.get("name")` happens to return), which is a bigger,
  separate piece of work.
- **Countries with real artists but zero enriched rows yet** — this
  only surfaces what `artist_meta` already has. Same limitation the
  Genre dropdown already has relative to `track_tags`.
- **`[Worldwide]` artists** — excluded from filtering, not resolved
  to a real country.

## Rough complexity estimate

Small-to-moderate, well-scoped:
- 1 new Flask route (`/countries`), directly mirrors existing
  `/genres` — low risk, proven pattern.
- 1 template change (remove hardcoded options, add `loadCountries()`
  JS), directly mirrors existing `loadGenres()`.
- 1 shared alias-map module, used by both the new endpoint and the
  existing filter query in `brain.py`.
- 1 one-line prompt change in `enrich_artists.py`.

No schema migration, no destructive data rewrite. Confirmed against
real production data before writing this doc, not assumed.

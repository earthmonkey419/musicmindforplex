"""
Canonical country name mapping for artist_meta.country.

Why this exists: mb_enrich_artists.py writes country as the full name
from MusicBrainz's area.get("name") (e.g. "United Kingdom", "Brazil"),
while enrich_artists.py's OpenAI fallback historically wrote 2-letter
ISO codes (fixed 2026-08-27 to write full names going forward, but
already-enriched rows keep whatever format they were written in).
MusicBrainz's area field is also not reliably country-level -- some
rows are city-level (New York, London, Nashville).

--- Why this is pycountry-based, not another hand-curated list ---

The first version of this module (2026-08-27) was a hand-curated map
built from the top ~40 rows of a `GROUP BY country ORDER BY cnt DESC`
query. That's a real, structural blind spot: sampling the top of a
distribution can never see the long tail by construction, no matter
how much real signal is in it. Confirmed concretely two days later
(2026-08-29): "IN" alone turned out to be 51 artists -- more than
several codes that WERE in the original top-40 sample -- plus a
dozen more real codes (SE, GR, DK, PR, NL, IT, AT, ES, TT, IS, BB,
AM) that the sample never saw. A hand-maintained whitelist of ISO
codes will always be one artist away from the next silent gap.

This version uses `pycountry` (real ISO 3166-1 data, no network
calls, ships as a static dataset) as the primary resolver for any
raw value that looks like a 2-3 letter code -- closing this entire
class of gap permanently instead of patching it one straggler at a
time. The hand-curated MANUAL_ALIASES map below is now deliberately
small: it only holds cases pycountry genuinely cannot resolve on its
own (colloquial "UK" is not the official ISO code -- "GB" is -- and
city-level values MusicBrainz's area field sometimes returns instead
of a real country).

Full country *names* not yet seen by this module are NOT silently
dropped either -- they pass through as their own canonical value.
The alternative (returning None for anything unmapped) would just
move the exact same "silently invisible until someone thinks to add
it" bug from ISO codes to full country names instead of eliminating
it.

COMMON_NAME_OVERRIDES exists because pycountry's official ISO names
sometimes diverge from MusicBrainz's own more colloquial naming --
confirmed real divergence: alpha_2 "KR" resolves via pycountry to
"Korea, Republic of", while MusicBrainz enrichment already writes
"South Korea" directly as a full name for the same country. Without
this override table, a future artist enriched with the raw code "KR"
would silently create a brand-new split ("Korea, Republic of" vs.
"South Korea") -- the exact fragmentation this module exists to
prevent, just relocated to a different pair of strings. This list is
deliberately not exhaustive -- covers realistic real-world cases for
a personal music library, add more as real cases actually surface
(same "measure, don't guess" discipline as everywhere else in this
project), not pre-populated speculatively for countries that may
never appear.

[Worldwide] is MusicBrainz's own marker for artists without a fixed
geographic origin -- deliberately excluded, not a real country.
"Ely" is a confirmed real data artifact (2026-08-29) -- an English
cathedral city, not a country; likely area.get("name") returning a
city-level value for some artist. Excluded rather than guessed at.
"""
import pycountry

# Cases pycountry genuinely cannot resolve on its own -- not ISO
# codes at all (colloquial "UK"), or city-level values MusicBrainz's
# area field returned instead of a country. Every entry here is a
# raw value actually observed in production artist_meta, not
# speculative.
MANUAL_ALIASES = {
    "United Kingdom": ["UK", "England", "London"],
    "United States": ["New York", "Los Angeles", "Nashville"],
}

# Values to exclude entirely -- never treated as a real country, no
# matter how they're spelled.
EXCLUDED_RAW_VALUES = {"[Worldwide]", "Ely"}

# Confirmed real divergence between pycountry's official ISO name and
# the more colloquial name MusicBrainz itself already uses. Applied
# uniformly regardless of whether a country was resolved via ISO code
# lookup or matched as an already-stored full name.
COMMON_NAME_OVERRIDES = {
    "Korea, Republic of": "South Korea",
    "Korea, Democratic People's Republic of": "North Korea",
    "Russian Federation": "Russia",
    "Viet Nam": "Vietnam",
    "Iran, Islamic Republic of": "Iran",
    "Syrian Arab Republic": "Syria",
    "Tanzania, United Republic of": "Tanzania",
    "Bolivia, Plurinational State of": "Bolivia",
    "Venezuela, Bolivarian Republic of": "Venezuela",
    "Moldova, Republic of": "Moldova",
    "Lao People's Democratic Republic": "Laos",
    "Taiwan, Province of China": "Taiwan",
    "Congo, The Democratic Republic of the": "DR Congo",
    "Brunei Darussalam": "Brunei",
}

_MANUAL_RAW_TO_CANONICAL = {
    raw: canonical
    for canonical, raws in MANUAL_ALIASES.items()
    for raw in raws
}


def canonicalize_country(raw_value):
    """
    Map a raw artist_meta.country value to its canonical display
    name. Returns None only for values confirmed to not be real
    countries (EXCLUDED_RAW_VALUES). Anything else -- a known manual
    alias, a real ISO code (resolved via pycountry), or an
    already-reasonable full name never seen before -- resolves to a
    real canonical string rather than silently vanishing.
    """
    if not raw_value:
        return None
    raw_value = raw_value.strip()
    if not raw_value or raw_value in EXCLUDED_RAW_VALUES:
        return None

    if raw_value in _MANUAL_RAW_TO_CANONICAL:
        return _MANUAL_RAW_TO_CANONICAL[raw_value]

    # Real ISO 3166-1 alpha-2/alpha-3 codes -- the systemic fix.
    # Resolves ANY valid code, not just ones this module has
    # previously been told about.
    if 2 <= len(raw_value) <= 3 and raw_value.isalpha():
        country = pycountry.countries.get(alpha_2=raw_value.upper())
        if not country:
            country = pycountry.countries.get(alpha_3=raw_value.upper())
        if country:
            return COMMON_NAME_OVERRIDES.get(country.name, country.name)

    return COMMON_NAME_OVERRIDES.get(raw_value, raw_value)


def get_country_aliases(canonical_name):
    """
    Given a canonical name (e.g. "India"), return every raw value
    that should match it in a SQL IN (...) clause: the canonical name
    itself, any known manual alias, and the real ISO alpha-2/alpha-3
    codes for that country (via pycountry) -- so selecting "India"
    also matches legacy rows stored as the raw code "IN", without
    needing every code hand-listed here.
    """
    aliases = {canonical_name}
    aliases.update(MANUAL_ALIASES.get(canonical_name, []))

    # Reverse an override (e.g. "South Korea" -> "Korea, Republic of")
    # so a lookup by the friendly name still finds the right pycountry
    # entry, and so any already-existing rows stored under the
    # official name before this fix still match too.
    lookup_name = canonical_name
    for official, friendly in COMMON_NAME_OVERRIDES.items():
        if friendly == canonical_name:
            aliases.add(official)
            lookup_name = official
            break

    try:
        country = pycountry.countries.get(name=lookup_name)
        if not country:
            results = pycountry.countries.search_fuzzy(lookup_name)
            country = results[0] if results else None
        if country:
            aliases.add(country.alpha_2)
            aliases.add(country.alpha_3)
            aliases.add(country.name)
    except LookupError:
        pass

    return list(aliases)

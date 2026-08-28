"""
Canonical country name mapping for artist_meta.country.

Why this exists: mb_enrich_artists.py writes country as the full name
from MusicBrainz's area.get("name") (e.g. "United Kingdom", "Brazil"),
while enrich_artists.py's OpenAI fallback wrote 2-letter ISO codes
(e.g. "UK", "BR") until this same v4 pass fixed that prompt. Older
OpenAI-enriched rows still have codes. MusicBrainz's area field is
also not reliably country-level -- some rows are city-level ("New
York", "London", "Nashville"). This module folds all known variants
into one canonical display name per real country.

Built directly from a real query against production artist_meta
(2026-08-27) -- every raw value below was actually observed, not
guessed. New raw values should be added here as they're actually
found (same "measure, don't guess" discipline as the rest of this
project), not pre-populated speculatively.

One deliberate exception to "only observed values": the 2-letter
codes brain.py's classify_prompt() country_map can already emit for
AI-detected filters (e.g. "Brazilian artists" -> "BR") are included
even where no artist_meta row currently uses that exact code, since
this map needs to canonicalize whatever the classifier hands it, not
just what's already stored. Nigeria and Cuba are added as their own
canonical entries for the same reason -- both are valid
classify_prompt() outputs with no matching canonical entry
otherwise.

[Worldwide] is MusicBrainz's own marker for artists without a fixed
geographic origin -- deliberately excluded, not a real country.
"""

# canonical display name -> every raw value seen in artist_meta.country
# that should be treated as that country.
CANONICAL_COUNTRIES = {
    "United States":  ["United States", "US", "New York", "Los Angeles", "Nashville"],
    "United Kingdom": ["United Kingdom", "UK", "GB", "England", "London"],
    "Germany":        ["Germany", "DE"],
    "Canada":         ["Canada", "CA"],
    "Sweden":         ["Sweden"],
    "Australia":      ["Australia", "AU"],
    "Netherlands":    ["Netherlands"],
    "Brazil":         ["Brazil", "BR"],
    "France":         ["France", "FR"],
    "Italy":          ["Italy"],
    "Jamaica":        ["Jamaica", "JM"],
    "Japan":          ["Japan", "JP"],
    "India":          ["India"],
    "Denmark":        ["Denmark"],
    "Belgium":        ["Belgium"],
    "Ireland":        ["Ireland"],
    "Spain":          ["Spain"],
    "Norway":         ["Norway"],
    "New Zealand":    ["New Zealand"],
    "Austria":        ["Austria"],
    "South Korea":    ["South Korea"],
    "Romania":        ["Romania"],
    "Switzerland":    ["Switzerland"],
    "Singapore":      ["Singapore"],
    "Israel":         ["Israel"],
    "Greece":         ["Greece"],
    "Russia":         ["Russia"],
    # Not yet observed in artist_meta -- included because
    # classify_prompt()'s country_map already emits these codes for
    # AI-detected filters (e.g. "Nigerian artists" -> "NG").
    "Nigeria":        ["Nigeria", "NG"],
    "Cuba":           ["Cuba", "CU"],
    # Kept distinct from "United States" deliberately -- MusicBrainz
    # treats it as its own area, and collapsing it into the US is a
    # real judgment call this doc isn't making unilaterally.
    "Puerto Rico":    ["Puerto Rico"],
}

# Values that exist in the raw data but are deliberately excluded from
# filtering entirely -- not real countries.
EXCLUDED_RAW_VALUES = {"[Worldwide]"}

# Reverse lookup: raw stored value -> canonical name. Built once at
# import time from CANONICAL_COUNTRIES above.
_RAW_TO_CANONICAL = {
    raw: canonical
    for canonical, raws in CANONICAL_COUNTRIES.items()
    for raw in raws
}


def canonicalize_country(raw_value):
    """
    Map a raw artist_meta.country value to its canonical display name.
    Returns None for excluded values (e.g. "[Worldwide]") or values
    not yet in the map -- callers should skip/ignore None, not treat
    it as an error, since new unmapped values are expected to surface
    over time as the library grows.
    """
    if not raw_value or raw_value in EXCLUDED_RAW_VALUES:
        return None
    return _RAW_TO_CANONICAL.get(raw_value)


def get_country_aliases(canonical_name):
    """
    Given a canonical name (e.g. "United Kingdom"), return every raw
    value that should match it in a SQL IN (...) clause. Returns
    [canonical_name] unchanged if it's not a known canonical name --
    safe fallback so an exact-match filter still works even for a
    country not yet added to this map.
    """
    return CANONICAL_COUNTRIES.get(canonical_name, [canonical_name])

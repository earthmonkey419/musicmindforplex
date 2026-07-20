#!/usr/bin/env python3
"""
MusicMind for Plex - Core Engine
Shared logic for prompt expansion, track search, and playlist creation.
"""

import sqlite3
from openai import OpenAI
from plexapi.server import PlexServer
from config import PLEX_URL, PLEX_TOKEN, MUSIC_LIB, DB_PATH, OPENAI_KEY

# --- Config ---

# Defensive strip: a stray invisible Unicode character (e.g. U+2028
# LINE SEPARATOR) silently pasted at the end of a credential will pass
# every visual check but crash EVERY OpenAI API call with a confusing
# httpx header-encoding error deep in a library traceback — found the
# hard way July 15, 2026. .strip() catches this and all similar
# whitespace-class Unicode contamination, in any environment.
OPENAI_KEY = OPENAI_KEY.strip() if OPENAI_KEY else OPENAI_KEY
PLEX_TOKEN = PLEX_TOKEN.strip() if PLEX_TOKEN else PLEX_TOKEN

client = OpenAI(api_key=OPENAI_KEY)

# --- Tag buckets (added July 2026) ---
# Built from real tag frequency data + fuzzy-matched/manually-corrected
# categorization (see MUSICMIND-TAG-BUCKETING-FINAL-v2.md). Three pools:
#   ERA_TAGS, MOOD_ENERGY  — always injected regardless of bucket choice,
#                            these are cross-genre and shouldn't disappear
#                            just because someone picked a narrow genre.
#   BUCKETS                — what the genre checkboxes actually narrow.
#                            Empty selection = full get_known_tags() pool,
#                            today's exact unchanged behavior.
ERA_TAGS = {
    '1960s',
    '1970s',
    '1980s',
    '60s',
    '80s',
    '60s beat',
}

MOOD_ENERGY = {
    '60s nostalgia',
    'aggressive',
    'ambient',
    'anthemic',
    'atmospheric',
    'catchy',
    'celebratory',
    'chill-out',
    'chillout',
    'cinematic',
    'concept album',
    'confident',
    'danceable',
    'dark',
    'dark ambient',
    'dark ballad',
    'dark humor',
    'demo',
    'downtempo',
    'dramatic',
    'dreamy',
    'emotional',
    'emotional ballad',
    'emotive',
    'energetic',
    'epic',
    'ethereal',
    'fast-paced',
    'festive',
    'groovy',
    'heartfelt',
    'humorous',
    'instrumental',
    'intense',
    'intimate',
    'introspective',
    'laid-back',
    'live',
    'live performance',
    'lo-fi',
    'lo-fi indie',
    'lyrical',
    'meditative',
    'melancholic',
    'melodic',
    'nature sounds',
    'nostalgic',
    'optimistic',
    'party',
    'party anthem',
    'playful',
    'quirky',
    'raw',
    'raw energy',
    'rebellious',
    'reflective',
    'relaxation',
    'romantic',
    'sentimental',
    'social commentary',
    'soulful',
    'spiritual',
    'storytelling',
    'surrealist',
    'theatrical',
    'upbeat',
    'uplifting',
    'vocal harmony',
    'whimsical',
}

BUCKETS = [
    ("New Wave / Post-Punk / Synth", [
        '80s synth',
        'dark cabaret',
        'dark pop',
        'dark wave',
        'darkwave',
        'ethereal wave',
        'freakbeat',
        'goth rock',
        'gothic blues',
        'gothic pop',
        'gothic rock',
        'new age',
        'new wave',
        'no wave',
        'post-bop',
        'post-punk',
        'post-punk revival',
        'punk',
        'synth-pop',
        'synthwave',
    ]),
    ("Psych / Art Rock / Experimental", [
        'art pop',
        'art rock',
        'avant-garde',
        'avant-garde pop',
        'drone rock',
        'empowerment',
        'experimental',
        'experimental electronic',
        'experimental r&b',
        'experimental reggae',
        'experimental rock',
        'neo-psychedelia',
        'no wave',
        'noise rock',
        'progressive pop',
        'progressive rock',
        'psych rock',
        'psychedelic',
        'psychedelic rock',
        'space age pop',
        'space rock',
    ]),
    ("Classic / Garage / Alt / Punk Rock", [
        '1960s pop',
        '1970s rock',
        '1980s rock',
        '60s rock',
        '70s rock',
        '80s alternative',
        '80s punk',
        '80s rock',
        'acid rock',
        'acoustic rock',
        'alternative',
        'alternative pop',
        'alternative rap',
        'alternative rock',
        'arena rock',
        'art punk',
        'beat music',
        'blues rock',
        'british invasion',
        'california punk',
        'california sound',
        'classic rock',
        'dance',
        'dance rock',
        'dance-punk',
        'dance-rock',
        'desert rock',
        'east coast hip-hop',
        'feel-good',
        'female rock vocalist',
        'feminine rock',
        'folk punk',
        'folk rock',
        'freakbeat',
        'funk rock',
        'fuzz rock',
        'garage rock',
        'glam metal',
        'glam rock',
        'hair metal',
        'hard rock',
        'hardcore punk',
        'heartland rock',
        'heavy metal',
        'indie rock',
        'industrial rock',
        'instrumental rock',
        'jam band',
        'jangle pop',
        'jazz-influenced rock',
        'khmer rock',
        'lo-fi rock',
        'melodic punk',
        'melodic rock',
        'merseybeat',
        'mod',
        'no wave',
        'political',
        'political punk',
        'political rock',
        'post-hardcore',
        'post-rock',
        'proto-punk',
        'psychedelic folk',
        'pub rock',
        'punk blues',
        'punk rock',
        'raw rock',
        'reggae rock',
        'reggae-influenced rock',
        'rock',
        'rock and roll',
        'rockabilly',
        'satirical',
        'satirical punk',
        'shoegaze',
        'ska punk',
        'slacker rock',
        'soft rock',
        'southern rock',
        'spiritual rock',
        'stoner rock',
        'surf rock',
        'swedish rock',
        'symphonic rock',
        'upbeat rock',
    ]),
    ("Soul / Funk / R&B", [
        '1950s r&b',
        '60s ballad',
        '60s girl group',
        '60s soul',
        '70s r&b',
        '70s soul',
        '90s r&b',
        '90s soul',
        'adult contemporary',
        'alternative r&b',
        'ambient rock',
        'ballad',
        'blue-eyed soul',
        'classic r&b',
        'classic soul',
        'contemporary r&b',
        'contemporary soul',
        'cosmic funk',
        'disco',
        'doo-wop',
        'doowop',
        'electronic soul',
        'funk',
        'funk rap',
        'funk-infused',
        'funky',
        'girl group',
        'gospel',
        'groove rock',
        'hi-nrg',
        'jazz-influenced r&b',
        'modern soul',
        'motown',
        'neo-soul',
        'new jack swing',
        'nu-disco',
        'piano solo',
        'psychedelic funk',
        'psychedelic soul',
        'r&b',
        'rhythm and blues',
        'romantic ballad',
        'slow jam',
        'smooth r&b',
        'smooth soul',
        'sophisticated soul',
        'soul',
        'soul ballad',
        'soul jazz',
        'soulful blues',
        'soulful electronic',
        'soulful r&b',
        'soulful reggae',
        'southern soul',
        'stax',
        'urban',
        'urban contemporary',
    ]),
    ("Jazz", [
        'acid jazz',
        'avant-garde jazz',
        'bebop',
        'big band',
        'blues jazz',
        'brazilian jazz',
        'classic jazz',
        'contemporary jazz',
        'cool jazz',
        'easy listening',
        'electronic jazz',
        'experimental jazz',
        'free jazz',
        'fusion',
        'hard bop',
        'instrumental jazz',
        'jazz',
        'jazz fusion',
        'jazz influence',
        'jazz rap',
        'jazz vocal',
        'jazz-funk',
        'jazz-inflected',
        'jazz-influenced',
        'lounge',
        'lyrical jazz',
        'modal jazz',
        'modern jazz',
        'nu jazz',
        'piano',
        'piano jazz',
        'romantic jazz',
        'smooth jazz',
        'spiritual jazz',
        'swing',
        'traditional jazz',
        'vocal jazz',
        'world jazz',
    ]),
    ("World / Reggae / Latin / Afro", [
        '2 tone ska',
        'african drumming',
        'afrobeat',
        'afrofuturism',
        'andean folk',
        'bossa nova',
        'brazilian funk',
        'brazilian pop',
        'brazilian rock',
        'classic reggae',
        'conscious reggae',
        'dancehall',
        'dub',
        'dub reggae',
        'ethnic fusion',
        'exotic pop',
        'exotica',
        'indian classical',
        'instrumental reggae',
        'jamaican reggae',
        'japanese electronic',
        'latin rock',
        'lovers rock',
        'mambo',
        'mpb',
        'political reggae',
        'psychedelic reggae',
        'raga',
        'reggae',
        'reggae fusion',
        'rocksteady',
        'roots reggae',
        'samba',
        'samba rock',
        'sitar',
        'sitar music',
        'ska',
        'ska punk',
        'spiritual reggae',
        'tropicalia',
        'world fusion',
        'world music',
        'world music fusion',
        'worldbeat',
    ]),
    ("Hip-Hop / Rap", [
        '90s hip-hop',
        'alternative hip-hop',
        'club rap',
        'conscious hip-hop',
        'conscious rap',
        'east coast hip-hop',
        'electronic rap',
        'experimental hip-hop',
        'experimental rap',
        'feminist hip-hop',
        'feminist rap',
        'funk rap',
        'g-funk',
        'golden age hip-hop',
        'hip hop',
        'hip-hop',
        'lyrical rap',
        'old school hip-hop',
        'party rap',
        'political rap',
        'southern hip-hop',
        'trap',
        'west coast hip-hop',
    ]),
    ("Pop", [
        '1950s pop',
        '60s pop',
        '80s pop',
        'avant-pop',
        'baroque pop',
        'chamber pop',
        'classic pop',
        'contemporary pop',
        'dance-pop',
        'dream pop',
        'exotic pop',
        'experimental pop',
        'folk-pop',
        'french pop',
        'gothic pop',
        'indie pop',
        'instrumental pop',
        'melodic pop',
        'orchestral pop',
        'pop',
        'pop ballad',
        'pop rock',
        'power ballad',
        'power pop',
        'psychedelic pop',
        'quirky pop',
        'romantic pop',
        'sophisti-pop',
        'sophisticated pop',
        'space age pop',
        'sunshine pop',
        'teen pop',
        'theatrical pop',
        'traditional pop',
    ]),
    ("Classical / Orchestral / Cinematic", [
        'baroque',
        'chamber music',
        'classical',
        'classical crossover',
        'classical guitar',
        'classical piano',
        'film score',
        'impressionist',
        'musical theatre',
        'neoclassical',
        'orchestral',
        'prelude',
        'romantic era',
        'soundtrack',
        'symphonic',
        'symphonic electronic',
    ]),
    ("Folk / Singer-Songwriter / Acoustic / Blues", [
        'a cappella',
        'acoustic',
        'acoustic blues',
        'blues',
        'chicago blues',
        'contemporary folk',
        'counterculture',
        'country',
        'country rock',
        'delta blues',
        'electric blues',
        'folk',
        'folk blues',
        'indie folk',
        'lyrical storytelling',
        'narrative',
        'narrative songwriting',
        'protest song',
        'singer-songwriter',
        'singer-songwriter 60s',
        'singer-songwriter 70s',
        'singer-songwriter 80s',
        'spoken word',
        'torch song',
        'traditional blues',
    ]),
    ("Electronic / House / Techno / Downtempo", [
        '80s electronic',
        'ambient electronic',
        'ambient pop',
        'ambient techno',
        'big beat',
        'chill',
        'chillwave',
        'cosmic disco',
        'deep house',
        'electronic',
        'electronic rock',
        'electropop',
        'house',
        'indie electronic',
        'progressive house',
        'techno',
        'trip-hop',
    ]),
]

GENRE_BUCKET_NAMES = [name for name, _ in BUCKETS]

DEFAULT_FILTERS = {
    "unplayed":       False,
    "genre":          None,
    "min_year":       None,
    "max_year":       None,
    "min_plays":      None,
    "max_plays":      None,
    "limit":          30,
    "max_per_artist": 3,
    "gender":         None,
    "country":        None,
    "era":            None,
    "instrumental":   None,
    "title_search":   None,
    "artist_search":  None,
    "year_search":    None,
    "intent":         "mood",
    "bpm_min":        None,
    "bpm_max":        None,
    "lastfm_rating_keys": None,
    "danceability":   None,
}

# --- Prompt Expansion ---

INSTRUMENTAL_KEYWORDS = ['instrumental', 'no vocals', 'no singing', 'without vocals', 'music only']
VOCAL_KEYWORDS = ['vocal', 'with vocals', 'singing', 'singer', 'with lyrics']

def detect_instrumental_intent(prompt):
    """Returns 1 for instrumental, 0 for vocal, None for no preference."""
    p = prompt.lower()
    if any(k in p for k in INSTRUMENTAL_KEYWORDS):
        return 1
    if any(k in p for k in VOCAL_KEYWORDS):
        return 0
    return None

def classify_prompt(prompt):
    """
    Multi-dimensional prompt analysis. Returns structured dict with:
    - intent: "mood", "title_search", "artist_search", or "filter_only"
    - mood: mood/vibe description if present (for expand_prompt)
    - genre: explicit genre mentioned if any
    - title_search: specific title words to search for
    - artist_search: specific artist name to search for
    - filters: dict of detected filters {gender, country, era, year}
    """
    import json

    country_map = {
        'brazilian': 'BR', 'brazil': 'BR',
        'jamaican': 'JM', 'jamaica': 'JM',
        'british': 'UK', 'uk': 'UK', 'english': 'UK',
        'american': 'US', 'usa': 'US',
        'french': 'FR', 'france': 'FR',
        'nigerian': 'NG', 'nigeria': 'NG',
        'cuban': 'CU', 'cuba': 'CU',
        'japanese': 'JP', 'japan': 'JP',
        'german': 'DE', 'germany': 'DE',
        'australian': 'AU', 'australia': 'AU',
    }

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{
            "role": "user",
            "content": f"""Analyze this music search prompt across multiple dimensions.

Prompt: "{prompt}"

Answer each dimension:

1. INTENT: What is the primary intent?
   - "title_search" — searching for songs with specific words IN THE TITLE (e.g. "songs with ocean in the name")
   - "artist_search" — searching for songs BY A SPECIFIC NAMED ARTIST (e.g. "songs by Miles Davis", "tracks by The Beatles"). ONLY use this if a specific artist name is mentioned.
   - "filter_only" — filtering by attributes with no mood (e.g. "female Brazilian artists from the 1970s", "unplayed reggae")
   - "mood" — describing a feeling, vibe, activity, or situation

2. MOOD: If there is a mood/vibe/feeling/activity, describe it in 3-5 words. null if none.

3. GENRE: Is a specific genre explicitly mentioned? (e.g. "jazz", "reggae", "classical"). null if none.

4. TITLE_SEARCH: If intent is title_search, what words to search for in track titles? null if not title search.

5. ARTIST_SEARCH: If a SPECIFIC artist name is mentioned, what is it? null if no specific artist named. Do NOT use this for demographic descriptions like "female artists" or "Brazilian artists".

6. FILTERS: Detect any of these filters from the prompt:
   - gender: "female", "male", or "mixed" if mentioned. null if not mentioned.
   - country: 2-letter country code if a nationality/country is mentioned. null if not.
   - era: decade like "70s", "80s" if mentioned. null if not.
   - year: specific year like "1975" if mentioned. null if not.
   - min_plays: if the prompt asks for "comfort picks", "old favorites",
     "songs I've heard a lot", "on repeat", or similar — set a reasonable
     minimum play count threshold (5-10 is a sensible default). null if
     not requested.

Respond ONLY with valid JSON, no explanation:
{{
  "intent": "mood",
  "mood": "late night intimate jazz",
  "genre": "jazz",
  "title_search": null,
  "artist_search": null,
  "filters": {{
    "gender": "female",
    "country": "BR",
    "era": "70s",
    "year": null,
    "min_plays": null
  }}
}}"""
        }]
    )

    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]

    result = json.loads(raw)

    # Normalize filters
    f = result.get("filters", {}) or {}
    result["filters"] = {
        "gender":     f.get("gender"),
        "country":    f.get("country"),
        "era":        f.get("era"),
        "year":       f.get("year"),
        "min_plays":  f.get("min_plays"),
    }

    return result


def get_known_tags(limit=200):
    """Returns the most common tags actually present in track_tags,
    used to ground OpenAI's tag suggestions in real, matchable vocabulary."""
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    tags = [row[0] for row in conn.execute("""
        SELECT tag FROM track_tags
        GROUP BY tag ORDER BY COUNT(*) DESC LIMIT ?
    """, (limit,)).fetchall()]
    conn.close()
    return tags


def get_known_tags_bucketed(bucket_names=None, strict=False):
    """Same purpose as get_known_tags(), but narrows the offered
    vocabulary to specific genre buckets when the user has selected
    any. ERA_TAGS and MOOD_ENERGY are always included regardless of
    bucket choice — they're cross-genre and shouldn't disappear just
    because someone picked a narrow genre bucket.

    No buckets selected -> today's exact unchanged behavior
    (get_known_tags(), the full ~200-tag pool).

    strict=True (CONFIRMED DEFAULT as of July 2026 — see app.py's
    /preview route, which always passes strict=True whenever any
    bucket is selected): when a bucket IS selected, skip ERA_TAGS/
    MOOD_ENERGY entirely — offer ONLY that bucket's own tags. Proven
    3/3 on real production data that this produces genuinely
    genre-coherent results (real jazz artists for a jazz bucket, real
    hip-hop for a hip-hop bucket, etc.) instead of generic mood words
    crowding out every bucket's own vocabulary. The AI still reads
    the full prompt text and interprets its mood — it just does so
    THROUGH the selected genre's own vocabulary rather than reaching
    for generic cross-genre mood words. Has no effect when
    bucket_names is empty either way (unbucketed search unaffected).

    Cross-checks the static bucket assignments against LIVE track_tags
    data, so a bucket built from an old snapshot can never offer a tag
    that's since disappeared from the library (drift protection).
    """
    if not bucket_names:
        return get_known_tags()

    if strict:
        candidate_pool = set()
    else:
        candidate_pool = set(ERA_TAGS) | set(MOOD_ENERGY)
    bucket_map = dict(BUCKETS)
    for name in bucket_names:
        if name in bucket_map:
            candidate_pool |= set(bucket_map[name])

    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    live_tags = set(row[0] for row in conn.execute(
        "SELECT DISTINCT tag FROM track_tags"
    ).fetchall())
    conn.close()

    # Only offer tags that genuinely still exist in this library
    return sorted(candidate_pool & live_tags)


def expand_prompt(prompt, bucket_names=None, strict=False):
    """
    Send a natural language prompt to OpenAI and get back
    a list of specific music tags/genres/moods to search for.
    Tags are constrained to vocabulary that actually exists in this
    library's track_tags table, so results are guaranteed matchable.
    Logs full request/response to query_log table.

    bucket_names: optional list of genre bucket names to narrow the
    offered tag vocabulary to (see GENRE_BUCKET_NAMES). None/empty
    means today's unchanged full-pool behavior.

    strict: confirmed default whenever bucket_names is set — see get_known_tags_bucketed().
    """
    import json, time, sqlite3

    known_tags = get_known_tags_bucketed(bucket_names, strict=strict)
    tag_list = ", ".join(known_tags)

    system_msg = """You are an eclectic music curator who hosts a late-night college radio show. You have deep knowledge of subgenres, world music, jazz, post-punk, electronic, African music, Latin music, and everything in between. When given a theme, vibe, or situation, you think laterally — you find the emotional core and translate it into specific music tags."""
    user_msg = f"""The user wants: "{prompt}"

You may ONLY choose tags from this exact list — do not invent new tags,
do not modify spelling or wording, use them exactly as written:

{tag_list}

Identify 2-3 specific vibes that best capture this prompt.
If the prompt describes a situation or activity, identify the emotional feeling of that moment.
For each vibe, select 4-5 closely related tags from the list above.
Be decisive — commit to specific vibes, do not scatter across unrelated genres.
Total tags: 8-15, all tightly grouped around your chosen vibes, all from the list above.

Respond ONLY with a flat JSON array of tag strings, using exact spelling from the list above. No explanation."""

    t_start = time.time()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.4,
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user",   "content": user_msg}
        ]
    )
    duration_ms = int((time.time() - t_start) * 1000)

    raw = response.choices[0].message.content.strip()
    raw_response = raw

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    tags = json.loads(raw)
    tags = [t.strip().lower() for t in tags if t.strip()]

    # Safety net: drop anything the model returned that isn't actually
    # in the allowed vocabulary, in case it didn't perfectly obey the
    # hard constraint above.
    known_lower = set(t.lower() for t in known_tags)
    filtered_tags = [t for t in tags if t in known_lower]
    if len(filtered_tags) < len(tags):
        dropped = set(tags) - set(filtered_tags)
        print(f"expand_prompt: dropped invented tags not in library vocabulary: {dropped}")
    tags = filtered_tags

    # Log to DB
    # NOTE: result_count is NOT known yet at this point — search_tracks()
    # hasn't run. We return log_id so the caller can UPDATE this row with
    # the real count once results exist, instead of it silently sitting
    # as NULL forever (the "0 tracks" display bug found July 14).
    log_id = None
    try:
        prompt_tokens     = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        # gpt-4o-mini pricing: $0.15/1M input, $0.60/1M output
        cost_usd = (prompt_tokens * 0.00000015) + (completion_tokens * 0.0000006)

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.execute("""
            INSERT INTO query_log
                (prompt, tags, buckets, openai_request, openai_response,
                 prompt_tokens, completion_tokens, cost_usd, duration_ms)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            prompt,
            json.dumps(tags),
            json.dumps(bucket_names) if bucket_names else None,
            user_msg,
            raw_response,
            prompt_tokens,
            completion_tokens,
            round(cost_usd, 6),
            duration_ms
        ))
        log_id = cursor.lastrowid
        conn.commit()
        conn.close()
    except Exception as log_err:
        print(f"Log error: {log_err}")

    return tags, log_id


def update_query_log_result_count(log_id, result_count, filters=None):
    """Backfills result_count (and, if provided, filters) on a query_log
    row once search_tracks() has actually run. Neither is known at
    INSERT time inside expand_prompt() — filters gets built afterward
    in the /preview route. Safe no-op if log_id is None (e.g. logging
    failed or this prompt never went through expand_prompt at all).
    (filters backfill added July 15 — same class of gap as
    result_count, found via view_logs.py --analyze showing a
    default-filters mismatch instead of the real filters used.)"""
    if log_id is None:
        return
    import json
    try:
        conn = sqlite3.connect(DB_PATH)
        if filters is not None:
            conn.execute(
                "UPDATE query_log SET result_count = ?, filters = ? WHERE id = ?",
                (result_count, json.dumps(filters), log_id)
            )
        else:
            conn.execute(
                "UPDATE query_log SET result_count = ? WHERE id = ?",
                (result_count, log_id)
            )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"update_query_log_result_count error: {e}")

# --- Track Search ---

def sequence_for_flow(tracks):
    """
    Reorders a track list into a genuine tempo arc — ascending BPM to
    a peak, then descending back down — rather than the default
    match-score ordering.

    Deliberately deterministic (plain sorting), not AI-reasoned.
    Tested directly: asking an LLM to reason about BPM numbers and
    produce a smooth arc produced plausible-sounding but genuinely
    jagged results (verified by re-plotting its own output); a simple
    sort produces a mathematically clean, verifiable arc for free, no
    API call needed. AI is good at generating confident-sounding
    reasoning about sequencing; it isn't reliably good at actually
    doing the numeric sequencing itself.

    Tracks with no BPM data (Synapse hasn't analyzed them, or analysis
    failed) are appended at the end in their original order, since
    they can't be meaningfully placed on a tempo arc.
    """
    with_bpm = [t for t in tracks if t.get("bpm")]
    without_bpm = [t for t in tracks if not t.get("bpm")]

    if not with_bpm:
        return tracks  # nothing to sequence, return unchanged

    arc = sorted(with_bpm, key=lambda t: t["bpm"])
    half = (len(arc) + 1) // 2
    build_up = arc[:half]
    wind_down = list(reversed(arc[half:]))

    return build_up + wind_down + without_bpm


def get_scrobbled_tracks_around_date(target_date, window_days=4):
    """
    Returns distinct rating_keys for tracks scrobbled within
    window_days on either side of target_date (so a window_days=4
    gives an 8-day span total: 4 days before through 4 days after).

    target_date is a string like "2024-01-05". Only counts scrobbles
    that were successfully matched to a local track (matched = 1).
    """
    import sqlite3
    from datetime import datetime, timedelta

    center = datetime.strptime(target_date, "%Y-%m-%d")
    start = center - timedelta(days=window_days)
    end = center + timedelta(days=window_days) + timedelta(days=1)  # inclusive of the target day itself

    start_epoch = int(start.timestamp())
    end_epoch = int(end.timestamp())

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT DISTINCT rating_key FROM lastfm_scrobbles
        WHERE timestamp >= ? AND timestamp < ? AND matched = 1
    """, (start_epoch, end_epoch)).fetchall()
    conn.close()

    return [r[0] for r in rows]


def get_scrobbled_tracks_in_range(start_date, end_date):
    """
    Returns distinct rating_keys for tracks scrobbled between
    start_date and end_date (inclusive), both as "YYYY-MM-DD" strings.
    Only counts scrobbles successfully matched to a local track.
    """
    import sqlite3
    from datetime import datetime, timedelta

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)  # inclusive of end date

    start_epoch = int(start.timestamp())
    end_epoch = int(end.timestamp())

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("""
        SELECT DISTINCT rating_key FROM lastfm_scrobbles
        WHERE timestamp >= ? AND timestamp < ? AND matched = 1
    """, (start_epoch, end_epoch)).fetchall()
    conn.close()

    return [r[0] for r in rows]


def extract_lastfm_dates(text):
    """
    Extracts a date range from natural language text (used for the
    typed `lastfm: ...` prompt prefix). Narrow, single-purpose prompt —
    tested directly against 5 real phrasings including specific dates,
    month ranges, explicit ranges, and relative references ("last New
    Year's Eve") — all parsed correctly.
    """
    import json
    from datetime import datetime

    today_str = datetime.now().strftime("%Y-%m-%d")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[{
            "role": "user",
            "content": f"""Extract a date range from this text. Today's date is {today_str}.

Text: "{text}"

Respond ONLY with JSON: {{"start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD"}}
A single specific date should have start_date equal to end_date.
If the text mentions a holiday or relative date (e.g. "New Year's Eve", "my birthday" with no year), use your best reasonable interpretation, defaulting to the most recent past occurrence."""
        }]
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
    return json.loads(raw)


def search_tracks(tags, filters=None):
    """
    Query the database for tracks matching the given tags.
    Applies filters and caps results per artist.
    Returns list of dicts.
    Tags is optional — if empty, just applies filters.
    """
    f = {**DEFAULT_FILTERS, **(filters or {})}

    params = []

    if tags:
        keyword_conditions = " OR ".join(["tt.tag LIKE ?" for _ in tags])
        params = [f"%{tag}%" for tag in tags]
        where_tags = f"({keyword_conditions})"
    else:
        where_tags = "1=1"

    query = f"""
        SELECT
            t.rating_key,
            t.title,
            COALESCE(t.real_artist, t.artist) as artist,
            t.album,
            t.genre,
            t.year,
            t.play_count,
            t.user_rating,
            taf.bpm,
            taf.danceability,
            COUNT(DISTINCT tt.tag) as match_score
        FROM tracks t
        LEFT JOIN track_tags tt ON t.rating_key = tt.rating_key
        LEFT JOIN artist_meta am ON am.artist = COALESCE(t.real_artist, t.artist)
        LEFT JOIN track_audio_features taf ON taf.rating_key = t.rating_key
        WHERE {where_tags}
          AND t.title IS NOT NULL
          AND t.artist IS NOT NULL
          AND t.artist != ''
    """

    if f["unplayed"]:
        query += " AND t.play_count = 0"
    if f["genre"]:
        genre_val = f["genre"].lower().strip()
        # Detect decade patterns: "50s", "60s", "1950s", "1960s" etc
        import re
        decade_match = re.match(r'^(?:19)?(\d0)s', genre_val)
        if decade_match:
            decade = decade_match.group(1) + 's'  # normalize to "50s", "60s" etc
            query += " AND am.era = ?"
            params.append(decade)
        else:
            # Match any tag containing the genre string
            query += " AND EXISTS (SELECT 1 FROM track_tags WHERE track_tags.rating_key = t.rating_key AND track_tags.tag LIKE ?)"
            params.append(f"%{genre_val}%")
    if f["min_year"]:
        query += " AND t.year >= ?"
        params.append(f["min_year"])
    if f["max_year"]:
        query += " AND t.year <= ?"
        params.append(f["max_year"])
    if f["min_plays"] is not None:
        query += " AND t.play_count >= ?"
        params.append(f["min_plays"])
    if f["max_plays"] is not None:
        query += " AND t.play_count <= ?"
        params.append(f["max_plays"])
    if f.get("min_rating") is not None:
        query += " AND t.user_rating >= ?"
        params.append(f["min_rating"])
    if f.get("gender"):
        query += " AND am.gender = ?"
        params.append(f["gender"])
    if f.get("country"):
        query += " AND am.country IN (?, ?)"
        # normalize UK/GB
        c = f["country"]
        alt = "GB" if c == "UK" else ("UK" if c == "GB" else c)
        params.extend([c, alt])
    if f.get("era"):
        query += " AND am.era = ?"
        params.append(f["era"])
    if f.get("instrumental") is not None:
        query += " AND t.is_instrumental = ?"
        params.append(f["instrumental"])
    if f.get("title_search"):
        query += " AND LOWER(t.title) LIKE ?"
        params.append(f"%{f['title_search'].lower()}%")
    if f.get("artist_search"):
        query += " AND (LOWER(t.artist) LIKE ? OR LOWER(t.real_artist) LIKE ?)"
        params.extend([f"%{f['artist_search'].lower()}%", f"%{f['artist_search'].lower()}%"])
    if f.get("year_search"):
        import re as _re
        ys = str(f["year_search"])
        decade = _re.match(r"(\d{3,4})s?$", ys)
        if decade:
            base = int(decade.group(1))
            if base < 100: base += 1900
            query += " AND t.year >= ? AND t.year <= ?"
            params.extend([base, base + 9])
        else:
            query += " AND t.year = ?"
            params.append(int(ys))
    if f.get("bpm_min") is not None:
        query += " AND taf.bpm >= ?"
        params.append(f["bpm_min"])
    if f.get("bpm_max") is not None:
        query += " AND taf.bpm <= ?"
        params.append(f["bpm_max"])
    if f.get("danceability"):
        # Buckets based on real distribution from full-library analysis:
        # low < 1.0, medium 1.0-1.4, high > 1.4
        level = f["danceability"]
        if level == "low":
            query += " AND taf.danceability < 1.0 AND taf.danceability IS NOT NULL"
        elif level == "medium":
            query += " AND taf.danceability >= 1.0 AND taf.danceability <= 1.4"
        elif level == "high":
            query += " AND taf.danceability > 1.4"

    if f.get("lastfm_rating_keys") is not None:
        # Restrict to a specific set of rating_keys (from a Last.fm
        # date/range query). Empty list means the date query found no
        # scrobbles — should genuinely return zero results, not be
        # ignored, so this check is `is not None` rather than truthy.
        keys = f["lastfm_rating_keys"]
        if keys:
            placeholders = ",".join("?" for _ in keys)
            query += f" AND t.rating_key IN ({placeholders})"
            params.extend(keys)
        else:
            query += " AND 1=0"  # no scrobbles found — force zero results

    query += """
        GROUP BY t.artist, t.title
        ORDER BY match_score DESC, t.play_count ASC
    """

    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(query, params).fetchall()
    conn.close()

    # Cap per artist
    artist_counts = {}
    results = []
    for row in rows:
        rating_key, title, artist, album, genre, year, play_count, user_rating, bpm, danceability, match_score = row
        artist_counts[artist] = artist_counts.get(artist, 0)
        if artist_counts[artist] >= f["max_per_artist"]:
            continue
        artist_counts[artist] += 1
        results.append({
            "rating_key":   rating_key,
            "title":        title,
            "artist":       artist,
            "album":        album,
            "genre":        genre,
            "year":         year,
            "play_count":   play_count,
            "user_rating":  user_rating,
            "bpm":          bpm,
            "danceability": danceability,
            "match_score":  match_score,
        })
        if len(results) >= f["limit"]:
            break

    return results

# --- Playlist Creation ---

def create_playlist(name, rating_keys):
    """
    Create a playlist in Plex from a list of rating keys.
    Replaces existing playlist with the same name.
    Returns number of tracks added.
    """
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)

    tracks = []
    for rk in rating_keys:
        try:
            tracks.append(plex.fetchItem(int(rk)))
        except Exception as e:
            print(f"  Warning: could not fetch {rk}: {e}")

    if not tracks:
        return 0

    for pl in plex.playlists():
        if pl.title == name:
            pl.delete()

    plex.createPlaylist(name, items=tracks)
    return len(tracks)

# --- Quick test ---

if __name__ == "__main__":
    print("Testing prompt expansion...")
    tags, _log_id = expand_prompt("sunny day driving with the windows down")
    print(f"Tags: {tags}\n")

    print("Searching tracks...")
    tracks = search_tracks(tags, {"limit": 5, "max_per_artist": 2})
    for t in tracks:
        print(f"  [{t['match_score']}] {t['artist']} - {t['title']} ({t['year']})")

#!/usr/bin/env python3
"""
Plex Music Brain - Core Engine
Shared logic for prompt expansion, track search, and playlist creation.
"""

import sqlite3
from openai import OpenAI
from plexapi.server import PlexServer
from config import PLEX_URL, PLEX_TOKEN, MUSIC_LIB, DB_PATH, OPENAI_KEY

# --- Config ---

client = OpenAI(api_key=OPENAI_KEY)

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
    "year": null
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
        "gender":  f.get("gender"),
        "country": f.get("country"),
        "era":     f.get("era"),
        "year":    f.get("year"),
    }

    return result


def expand_prompt(prompt):
    """
    Send a natural language prompt to OpenAI and get back
    a list of specific music tags/genres/moods to search for.
    Logs full request/response to query_log table.
    """
    import json, time, sqlite3

    system_msg = """You are an eclectic music curator who hosts a late-night college radio show. You have deep knowledge of obscure subgenres, world music, jazz, post-punk, electronic, African music, Latin music, and everything in between. When given a theme, vibe, or situation, you think laterally — you find the emotional core and translate it into specific, sometimes unexpected music tags. You never default to the obvious. You favor specificity over breadth."""
    user_msg = f"""The user wants: "{prompt}"

Identify 2-3 specific vibes that best capture this prompt.
If the prompt describes a situation or activity, identify the emotional feeling of that moment.
For each vibe, generate 4-5 closely related music tags (subgenres, moods, styles, tempos, eras).
Be decisive — commit to specific vibes, do not scatter across unrelated genres.
Total tags: 8-15, all tightly grouped around your chosen vibes.

Respond ONLY with a flat JSON array of tag strings. No explanation.
Example: ["sunshine pop", "bossa nova", "upbeat", "60s soul", "feel-good", "tropical", "warmth"]"""

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

    # Log to DB
    try:
        prompt_tokens     = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        # gpt-4o-mini pricing: $0.15/1M input, $0.60/1M output
        cost_usd = (prompt_tokens * 0.00000015) + (completion_tokens * 0.0000006)

        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO query_log
                (prompt, tags, openai_request, openai_response,
                 prompt_tokens, completion_tokens, cost_usd, duration_ms)
            VALUES (?,?,?,?,?,?,?,?)
        """, (
            prompt,
            json.dumps(tags),
            user_msg,
            raw_response,
            prompt_tokens,
            completion_tokens,
            round(cost_usd, 6),
            duration_ms
        ))
        conn.commit()
        conn.close()
    except Exception as log_err:
        print(f"Log error: {log_err}")

    return tags

# --- Track Search ---

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
            COUNT(DISTINCT tt.tag) as match_score
        FROM tracks t
        LEFT JOIN track_tags tt ON t.rating_key = tt.rating_key
        LEFT JOIN artist_meta am ON am.artist = COALESCE(t.real_artist, t.artist)
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
        rating_key, title, artist, album, genre, year, play_count, user_rating, match_score = row
        artist_counts[artist] = artist_counts.get(artist, 0)
        if artist_counts[artist] >= f["max_per_artist"]:
            continue
        artist_counts[artist] += 1
        results.append({
            "rating_key":  rating_key,
            "title":       title,
            "artist":      artist,
            "album":       album,
            "genre":       genre,
            "year":        year,
            "play_count":  play_count,
            "user_rating": user_rating,
            "match_score": match_score,
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
    tags = expand_prompt("sunny day driving with the windows down")
    print(f"Tags: {tags}\n")

    print("Searching tracks...")
    tracks = search_tracks(tags, {"limit": 5, "max_per_artist": 2})
    for t in tracks:
        print(f"  [{t['match_score']}] {t['artist']} - {t['title']} ({t['year']})")

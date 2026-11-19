"""Create and upgrade MusicMind's local SQLite schema."""


def init_all(conn, db_path=None):
    """Create the tables and columns shared by MusicMind workflows."""
    conn.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tracks (
            rating_key   TEXT PRIMARY KEY,
            title        TEXT,
            artist       TEXT,
            album        TEXT,
            genre        TEXT,
            year         INTEGER,
            duration_ms  INTEGER,
            play_count   INTEGER DEFAULT 0,
            last_played  TEXT,
            user_rating  REAL,
            added_at     TEXT,
            updated_at   TEXT,
            real_artist  TEXT,
            is_instrumental INTEGER,
            genres_written  INTEGER DEFAULT 0,
            rating_count INTEGER
        )
    """)
    # Columns added after the original schema — upgrade existing DBs in place
    for col, decl in [
        ("real_artist", "TEXT"),
        ("is_instrumental", "INTEGER"),
        ("genres_written", "INTEGER DEFAULT 0"),
        ("rating_count", "INTEGER"),
    ]:
        try:
            conn.execute(f"ALTER TABLE tracks ADD COLUMN {col} {decl}")
        except Exception:
            pass  # column already exists
    # Core tables other pipeline steps depend on — ingest owns the schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS track_tags (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            rating_key  TEXT NOT NULL,
            tag         TEXT NOT NULL,
            source      TEXT DEFAULT 'openai',
            created_at  TEXT DEFAULT (datetime('now')),
            UNIQUE(rating_key, tag)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS artist_meta (
            artist        TEXT PRIMARY KEY,
            gender        TEXT,
            country       TEXT,
            era           TEXT,
            group_type    TEXT,
            active_since  INTEGER,
            mbid          TEXT,
            enriched_at   TEXT
        )
    """)
    try:
        conn.execute("ALTER TABLE artist_meta ADD COLUMN mbid TEXT")
    except Exception:
        pass  # column already exists

    # track_audio_features is also created by synapse_analyze.py, but
    # brain.py's core playlist search LEFT JOINs against it unconditionally
    # — playlist generation must work even if Synapse has never been run.
    conn.execute("""
        CREATE TABLE IF NOT EXISTS track_audio_features (
            rating_key    TEXT PRIMARY KEY,
            bpm           REAL,
            key           TEXT,
            scale         TEXT,
            key_strength  REAL,
            danceability  REAL,
            analyzed_at   TEXT,
            bpm_reliable  INTEGER DEFAULT 1
        )
    """)
    try:
        conn.execute(
            "ALTER TABLE track_audio_features ADD COLUMN bpm_reliable INTEGER DEFAULT 1"
        )
    except Exception:
        pass  # column already exists (or table just created with it)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS synapse_errors (
            rating_key    TEXT PRIMARY KEY,
            filepath      TEXT,
            error         TEXT,
            failed_at     TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS query_log (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp         TEXT DEFAULT (datetime('now')),
            prompt            TEXT,
            tags              TEXT,
            filters           TEXT,
            buckets           TEXT,
            intent            TEXT,
            result_count      INTEGER,
            duration_ms       INTEGER,
            error             TEXT,
            openai_request    TEXT,
            openai_response   TEXT,
            prompt_tokens     INTEGER,
            completion_tokens INTEGER,
            cost_usd          REAL
        )
    """)
    try:
        conn.execute("ALTER TABLE query_log ADD COLUMN buckets TEXT")
    except Exception:
        pass  # column already exists
    try:
        conn.execute("ALTER TABLE query_log ADD COLUMN intent TEXT")
    except Exception:
        pass  # column already exists
    conn.commit()
    print(f"Database ready: {db_path or 'MusicMind database'}\n")

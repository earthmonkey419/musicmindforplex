# Plex Music Brain - Configuration
# Copy this file to config.py and fill in your values.
# Never commit config.py to git — it contains your credentials.

import os

# Base directory — all paths derived from here
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DB_PATH = os.path.join(BASE_DIR, "plex_music_brain.db")

# Plex
PLEX_URL   = "http://YOUR_NAS_IP:32400"   # e.g. http://10.0.0.251:32400
PLEX_TOKEN = "YOUR_PLEX_TOKEN"             # see README for how to get this
MUSIC_LIB  = "Music"                       # your Plex music library name

# OpenAI
OPENAI_KEY = "YOUR_OPENAI_API_KEY"         # sk-proj-...

# Last.fm (optional — leave blank to disable Last.fm features)
# Get a free API key at https://www.last.fm/api/account/create
LASTFM_KEY  = ""    # from last.fm/api — leave blank to disable
LASTFM_USER = ""    # your last.fm username — leave blank to disable

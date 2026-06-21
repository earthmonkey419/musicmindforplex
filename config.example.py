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

# Last.fm
LASTFM_KEY  = "YOUR_LASTFM_API_KEY"        # from last.fm/api
LASTFM_USER = "YOUR_LASTFM_USERNAME"

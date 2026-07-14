# MusicMind for Plex - Configuration
# Copy this file to config.py and fill in your values.
# Never commit config.py to git — it contains your credentials.

import os

# Base directory — all paths derived from here
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database
DB_PATH = os.path.join(BASE_DIR, "musicmind.db")

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

# Optional: translate Plex-reported file paths to local paths.
# Needed when Plex runs on a different OS or machine than MusicMind
# (e.g. Plex on Windows + MusicMind in WSL or Docker).
# Longest matching prefix wins; backslashes become forward slashes.
# Example — Plex on Windows sees J:\Music, MusicMind in WSL sees /mnt/j/Music:
# PATH_MAP = {
#     "J:\\Music": "/mnt/j/Music",
# }
PATH_MAP = {}

# Internal flag — distinguishes the maintainer's own production instance
# (enables extra update-page controls). Leave as False.
IS_MASTER = False

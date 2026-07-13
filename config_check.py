"""
Shared config validation. Import and call check_config(...) with the
names of the values a script actually needs, right after importing
them from config.py. Exits with one friendly message instead of
letting an unedited config.py cause a wall of raw tracebacks.
"""

PLACEHOLDERS = {
    "PLEX_URL":   "YOUR_NAS_IP",
    "PLEX_TOKEN": "YOUR_PLEX_TOKEN",
    "OPENAI_KEY": "YOUR_OPENAI_API_KEY",
}

def check_config(**values):
    """
    Usage: check_config(PLEX_URL=PLEX_URL, PLEX_TOKEN=PLEX_TOKEN)
    Checks each named value against its known placeholder and against
    being blank. Exits with a single clear message if anything's unset.
    """
    missing = []
    for name, value in values.items():
        placeholder = PLACEHOLDERS.get(name)
        if not value or (placeholder and placeholder.lower() in str(value).lower()):
            missing.append(name)
    if missing:
        print("=" * 60)
        print("Configuration not set up yet.")
        print("=" * 60)
        print(f"Missing or still-default: {', '.join(missing)}")
        print()
        print("Edit config.py and fill these in before running this script.")
        print("(If you haven't yet: cp config.example.py config.py)")
        print("See the README for where to get your Plex token and")
        print("OpenAI API key.")
        print("=" * 60)
        raise SystemExit(1)

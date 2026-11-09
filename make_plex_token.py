#!/usr/bin/env python3
"""Create a dedicated Plex token for MusicMind.

Why: a token copied from Plex Web belongs to that browser session, and
dies the moment you sign that browser out. This registers MusicMind as
its own device ("MusicMind" under plex.tv -> Authorized Devices), so
only removing *that* entry can revoke it.

Needs: plexapi and requests (both already required by MusicMind)

Usage (from the app folder):
    python3.12 make_plex_token.py            # prints the token
    python3.12 make_plex_token.py --write    # also updates PLEX_TOKEN in config.py
                                            # and/or .env if they exist
Backups are saved as <file>.bak-<timestamp> (git-ignored).
Then restart the app:  PM2: sudo pm2 restart musicmind
                       Docker: set PLEX_TOKEN in your stack/.env and RECREATE the
                       container (a plain restart keeps the old generated config.py)
"""
import argparse
import os
import re
import shutil
import sys
import time
import uuid

APP_NAME = "MusicMind"

# config.py, either style:  PLEX_TOKEN = "abc"   or
#                           PLEX_TOKEN = os.environ.get("PLEX_TOKEN", "abc")
_PY_ENVGET = re.compile(
    r'^(PLEX_TOKEN\s*=\s*os\.environ\.get\(\s*["\']PLEX_TOKEN["\']\s*,\s*)(["\']).*?\2', re.M)
_PY_PLAIN = re.compile(r'^(PLEX_TOKEN\s*=\s*)(["\']).*?\2', re.M)
# .env:  PLEX_TOKEN=abc
_ENV_LINE = re.compile(r'^(PLEX_TOKEN\s*=\s*).*$', re.M)


def update_file(path, token, kind):
    """Rewrite PLEX_TOKEN in `path` (kind: 'py' or 'env'), saving a
    timestamped, git-ignored backup first. Returns a status string."""
    if not os.path.exists(path):
        return "missing"
    with open(path, encoding="utf-8") as f:
        src = f.read()
    if kind == "env":
        pattern, repl = _ENV_LINE, (lambda m: f"{m.group(1)}{token}")
    elif _PY_ENVGET.search(src):
        pattern, repl = _PY_ENVGET, (lambda m: f'{m.group(1)}"{token}"')
    else:
        pattern, repl = _PY_PLAIN, (lambda m: f'{m.group(1)}"{token}"')
    if not pattern.search(src):
        return "no PLEX_TOKEN line"
    try:
        shutil.copyfile(path, f"{path}.bak-{time.strftime('%Y%m%d-%H%M%S')}")
        with open(path, "w", encoding="utf-8") as f:
            f.write(pattern.sub(repl, src, count=1))
    except OSError as e:
        return f"FAILED ({type(e).__name__}: {e.strerror or e}) -- try again with sudo"
    return "updated"


def verify(token):
    """Try the token against the PLEX_URL this app is configured with."""
    try:
        sys.path.insert(0, os.getcwd())
        import config
        import requests
        r = requests.get(config.PLEX_URL.rstrip("/") + "/library/sections",
                         headers={"X-Plex-Token": token}, timeout=8)
        if r.status_code == 200:
            return True, f"Plex at {config.PLEX_URL} accepted the new token."
        return False, f"Plex at {config.PLEX_URL} answered HTTP {r.status_code}."
    except Exception as e:
        return None, f"Couldn't verify against Plex ({type(e).__name__}); that's okay."


def main():
    ap = argparse.ArgumentParser(description=f"Create a dedicated Plex token for {APP_NAME}.")
    ap.add_argument("--write", action="store_true",
                    help="update PLEX_TOKEN in config.py and/or .env (timestamped backups)")
    ap.add_argument("--timeout", type=int, default=300,
                    help="seconds to wait for you to approve in the browser")
    args = ap.parse_args()

    try:
        import plexapi
        from plexapi.myplex import MyPlexPinLogin
    except ImportError:
        print("plexapi isn't installed here. Try: sudo python3.12 -m pip install plexapi requests --break-system-packages")
        return 1

    headers = dict(plexapi.BASE_HEADERS)
    headers.update({
        "X-Plex-Product": APP_NAME,
        "X-Plex-Device-Name": APP_NAME,
        "X-Plex-Client-Identifier": f"{re.sub(r'[^a-z0-9]+', '-', APP_NAME.lower())}-{uuid.uuid4()}",
    })
    login = MyPlexPinLogin(headers=headers, oauth=True)
    print("\nOpen this link in any browser, sign in to Plex, and approve:\n")
    print("  " + login.oauthUrl() + "\n")
    print(f"Waiting up to {args.timeout}s...")
    login.run(timeout=args.timeout)
    login.waitForLogin()
    token = login.token
    if not token:
        print("\nNo approval received (expired or cancelled). Run it again.")
        return 1

    ok, msg = verify(token)
    print("\n" + msg)
    if ok is False:
        print("Not saving a token Plex just rejected.")
        return 1

    if args.write:
        results = {p: update_file(p, token, k) for p, k in (("config.py", "py"), (".env", "env"))}
        for p, status in results.items():
            if status != "missing":
                print(f"  {p}: {status}")
        if "updated" in results.values():
            print("Old file(s) kept as <name>.bak-<timestamp>.")
            print("Docker/Portainer: config.py is generated from the PLEX_TOKEN variable, "
                  "so update the variable there too and recreate the container.")
        if "updated" not in results.values():
            print("Nothing was updated. Set it yourself:")
            print(f"  PLEX_TOKEN={token}")
    else:
        print("\nYour token (put it in config.py, .env, or your Docker/Portainer variable):\n")
        print(f"  PLEX_TOKEN={token}")
    print(f'\nIn Plex it appears as a device named "{APP_NAME}" -- don\'t remove that entry.')
    print("Then restart the app (PM2: sudo pm2 restart musicmind | Docker: recreate the container).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

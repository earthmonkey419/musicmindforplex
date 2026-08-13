# MusicMind for Plex — Dockerfile
#
# Two variants via a build arg, not two separate Dockerfiles (avoids
# drift between them):
#
#   docker build --build-arg VARIANT=slim -t musicmind:slim .   (default)
#   docker build --build-arg VARIANT=full -t musicmind:full .
#
# slim: plain `essentia` only. Synapse's core BPM/key/danceability
#       measurement works immediately. VI (voice/instrumental
#       detection) is unavailable — the app already handles this
#       gracefully (the existing "no_essentia" state), no new error
#       handling needed here.
#
# full: `essentia-tensorflow` (adds real TensorFlow — a genuinely
#       large dependency, hundreds of MB). VI becomes *capable*.
#       The actual VI model file is never baked into this image
#       layer, deliberately — it's a CC BY-NC-SA licensed file, and
#       .gitignore already states the real principle for this repo:
#       "link don't bundle". docker-entrypoint.sh downloads it
#       directly from essentia.upf.edu (the original source) into a
#       persistent volume on first boot, automatically, only for the
#       full variant, so redistributing this image never carries
#       someone else's licensed file along with it.
#
# Runs as root, matching how this app already runs in its existing
# real-world deployment (Synology DSM via pm2) — a conscious choice,
# not an oversight, since getting a non-root user's permissions right
# for arbitrary host-side volume mounts can't be verified without a
# real Docker environment to test against. A hardened non-root setup
# is a reasonable future improvement once this base path is proven.

FROM python:3.12-slim

ARG VARIANT=slim
ENV MUSICMIND_VARIANT=${VARIANT}

# System dependencies:
#   ffmpeg   — transcode fallback for files fpcalc/essentia can't
#              read directly (proven pattern, recovers most real
#              production failures rather than giving up)
#   sqlite3  — CLI, for direct DB inspection/debugging convenience
#              (the app itself only needs Python's built-in sqlite3
#              module, already part of the base image)
#   curl     — used by docker-entrypoint.sh for the full variant's
#              first-run model download
#   procps   — general container debugging convenience (ps, etc.)
#
# essentia is a compiled C++ library — its own build docs list real
# system dependencies (libfftw3, libyaml, libsamplerate, libtag,
# etc.) for compiling from source. Deliberately NOT added here
# speculatively: guessing at exact package version numbers risks
# breaking this entire apt-get install atomically if even one
# doesn't exist in this specific Debian release, which is a worse
# failure mode than a discoverable Python import error. If essentia
# fails to import at runtime with a "shared library not found"
# error, see DOCKER.md's troubleshooting section for how to diagnose
# and add exactly what's actually missing.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    sqlite3 \
    curl \
    procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Python dependencies first, separately from the app code, so this
# layer only rebuilds when dependencies actually change, not on every
# code edit.
COPY requirements.txt requirements-full.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && if [ "$VARIANT" = "full" ]; then \
         pip install --no-cache-dir -r requirements-full.txt; \
       else \
         pip install --no-cache-dir essentia; \
       fi

# App code
COPY . .

# bin/fpcalc is a real, committed binary (statically-linked x86-64
# Linux, verified — no glibc compatibility concerns on this base
# image) but git doesn't reliably preserve the executable bit across
# clones/COPY operations. Set it explicitly rather than assume.
RUN chmod +x bin/fpcalc docker-entrypoint.sh

# Real, separate volumes for anything that must survive a container
# rebuild: the database, logs, and (full variant only) the
# downloaded VI model. Config is handled via environment variables
# by docker-entrypoint.sh, not a volume, unless the user explicitly
# mounts their own config.py (supported, see docker-compose.yml).
VOLUME ["/app/data", "/app/models"]

EXPOSE 8787

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python3", "web/app.py"]

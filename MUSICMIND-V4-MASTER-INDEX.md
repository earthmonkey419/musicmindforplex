# MusicMind for Plex — v4 Master Index

**Purpose:** single-source view of everything currently slated for
v4, pulled together from the individual scope docs, the v4 synopsis,
and the v3 punch list's "v4 basket." Nothing new proposed here —
this is an index, not a new scoping pass.

**Branch:** `v4-dev`, correctly based on `main` @ `d47ee9d` (fixed
2026-08-27 — was mistakenly branched from a stale `v3-dev` commit,
`73e1217`, missing 16 real commits; reset and re-pushed).

**Confidence key:**
- 🟢 **Formally scoped** — has its own dedicated `MUSICMIND-V4-SCOPE-*.md`
- 🟡 **Described, not formally scoped** — real and discussed, no
  dedicated scope doc exists yet
- ⚪ **Considered and declined** — deliberately not pursuing, kept
  here so it doesn't get silently re-proposed later

---

## 🟢 Formally scoped items

### 1. Country filter — data normalization + dynamic dropdown
*See `MUSICMIND-V4-SCOPE-COUNTRY-NORMALIZATION.md`*

**Status:** 🟢 SHIPPED to production 2026-08-27. First v4 item —
motivated the `v4-dev` branch. Found while investigating why India
wasn't in the Country dropdown: three real bugs — a hardcoded (not
data-driven) dropdown, a format mismatch between MusicBrainz
enrichment (full country names) and OpenAI-fallback enrichment
(2-letter ISO codes) that the filter query only handled one side of,
and `area.get("name")` sometimes returning city-level values instead
of countries. Confirmed against real production data (40 distinct
`country` values in `artist_meta`). India itself: 26 correctly
enriched artists, never actually a data gap.

Delivered as: new `country_aliases.py` canonical alias map, a new
`/countries` endpoint mirroring `/genres`, a dynamic dropdown
replacing the hardcoded one, the `brain.py` filter query fixed to
expand canonical → all raw aliases instead of a hardcoded UK/GB-only
pair, and `enrich_artists.py`'s OpenAI prompt fixed to stop writing
ISO codes going forward. Confirmed real-world impact on playlist
results immediately after deploy.

**Follow-up fixes, same evening (undocumented tweaks, not separately
scoped):**
- **Auto-generated playlist name now includes the selected country**
  — e.g. `My Playlist (World / Reggae / Latin / Afro)(India)`.
  Previously the bucket suffix showed but the country choice was
  silently dropped from the name.
- **Stats page "Library by Country" chart was a separate, un-fixed
  code path** — its own raw `artist_meta.country` query inside the
  main `/stats` route, never touched by the `/countries` endpoint
  fix. Confirmed via screenshot: city-level values (Virginia,
  Memphis, Baltimore) and split country spellings showing side by
  side in the same "Top 100" chart. Fixed with the same
  `country_aliases.canonicalize_country()` approach, canonicalizing
  and summing *before* applying the `country_limit`, not after —
  the naive order would have let "US"/"United States" each occupy a
  separate top-N slot.
- **Chart hiding every other country label** — unrelated to the data
  fix itself, a pre-existing Chart.js default (`autoSkip: true` on
  category axes silently drops alternating tick labels when
  vertical space is tight, even though every bar still renders). The
  page already had a working precedent for this exact fix on another
  chart; the country chart just never got the same
  `autoSkip: false` treatment. One-line fix.

### 2. MusicBrainz artist alias integration
*See `MUSICMIND-V4-SCOPE-ARTIST-ALIASES.md`*

**Status:** Scoped, not started. Most fully scoped item prior to the
country-normalization doc. Real motivating case: Mos Def (142 real
scrobbles) vs. the library's Yasiin Bey — genuinely different names
for the same artist, not a formatting difference no amount of string
normalization can bridge. MusicBrainz's own alias API
(`?inc=aliases`) already covers the confirmed motivating case.
Recommended first pass: gap analysis (`lastfm_gaps.py`) only, before
extending to scrobble matching or search.

### 3. Thematic relevance scoring
*See `MUSICMIND-V4-SCOPE-THEMATIC-RELEVANCE.md`* — already committed
to `main`.

**Status:** Scoped. Addresses the core, confirmed gap that the full
185-tag vocabulary describes sound, not meaning — zero lyrical/
thematic coverage. An LLM pass pulling a wider candidate pool
(60–100 tracks) and filtering for thematic fit before returning the
final 30, validated against real failure cases ("love songs",
"breakup songs" as the test bar — no lucky tag-name overlap allowed).

### 4. Tracklist import
*See `MUSICMIND-V4-SCOPE-TRACKLIST-IMPORT.md`*

**Status:** Scoped. Plain `.txt` upload (`Artist - Title` per line),
three-bucket match report (matched / ambiguous / unmatched) before
finalizing, strict source-order preservation. **Depends on the
artist-aliases feature** (#2 above) — matching quality benefits
directly from alias resolution.

### 5. Artist-name normalization for AcoustID vote counting
*See `MUSICMIND-V4-SCOPE-VA-VOTE-NORMALIZATION.md`*

**Status:** Scoped 2026-08-27. Promoted from the v3 punch list's
"leave as-is for now (July 25)" entry — real evidence now exists,
which was the explicit condition for revisiting it. A read-only
diagnostic against real production `va_results` (8,766 resolved
tracks) found 923 (10.5%) with a close vote between top two
candidates; scanning them shows a real, repeated pattern (case,
"and"/"&", "The" prefix, Unicode punctuation, "Orchestra"-suffix
phrasing), not noise — including Percy Faith's 22 real votes
fragmented five ways. `chosen_artist` writes directly to
`tracks.real_artist`, which tagging, enrichment, and MBID backfill
all read from downstream, so a bad split doesn't stay contained to
one field.

Proposed fix reuses the already-proven `normalize_for_matching()`
(handles case, Unicode punctuation, "and"↔"&") for vote-counting
keys only — display name stays the original string. Explicitly does
NOT attempt "The"-prefix stripping or "Orchestra"-suffix collapsing
in this first pass (both real, but riskier, separate follow-ups).
Open question, not yet decided: fix going forward only, vs. a
targeted re-tabulation pass over the 923 already-identified
close-vote tracks (cheap — re-tabulates existing `votes_json`, no
re-fingerprinting needed).

---

## 🟡 Described, not formally scoped

These are real and have been discussed with enough specificity to
act on, but don't have a dedicated `MUSICMIND-V4-SCOPE-*.md` the way
the four items above do. Flagging that distinction explicitly rather
than treating them as equally ready — worth a proper scope doc each
before starting, same discipline as the rest of v4.

### 6. Date-range playlist generator
Date range as a composable filter dimension, combinable with
existing tag/mood/bucket filtering (optional, not required). Gating
question: confirming a reliable "date added" field exists
consistently across the full library. No dependency on the alias or
thematic-relevance work — could be picked up independently.

### 7. Ollama integration (local LLM inference)
Goal: reduce or eliminate OpenAI dependency for tagging. Docker/
Portainer install path preferred over a standard script, since DSM
lacks systemd. A hardware upgrade (mini PC with a newer CPU) has been
informally discussed but not decided. Only appears as a single line
in the general roadmap doc currently — no scope doc yet.

### 8. `fullsync.lock` file-based lock
Prevents `pm2 restart` from killing a Full Sync run mid-execution.
Explicitly deferred until the SSE/subprocess threading fix (already
shipped — `tail_subprocess()`, commit `8dee1f4`) proves stable over
more real-world runs first.

### 9. Streamline analysis speed
*Discussed in `MUSICMIND-V4-SYNOPSIS.md` item 2, and the v3 punch
list's "v4 basket."* Real target: the one-time initial backlog clear,
not ongoing incremental syncs. Levers, roughly by likely impact:
parallelize across tracks (Synapse/VI currently fully sequential,
single process — likely the biggest lever on multi-core NAS
hardware); sample instead of full-track decode for BPM/key/
danceability. Explicitly ruled out: sharing one decode between
Synapse and VI (already proven to hurt accuracy via a real
ground-truth BPM test). Hard external ceiling: AcoustID's 3 req/s
rate limit.

### 10. Additional self-hosted audio tools
*Discussed in `MUSICMIND-V4-SYNOPSIS.md` item 3.* Essentia's own
pre-trained mood/genre classifiers (same library already integrated
for BPM/key/danceability and voice/instrumental detection — no new
dependency). An alternative beat-tracking algorithm as a cross-check
(e.g. `madmom`) — born from the octave-error investigation.
Lyrics-based search as a genuinely new search modality — "find songs
about heartbreak" — the one idea here that changes what MusicMind can
be *asked*, not just how well it answers what it's asked today;
working Mureka lyrics-extraction code already exists from a related
project, Musixmatch is another path if licensing works out.

### 11. A real "calm/ambient" signal distinct from raw BPM
*Discussed in `MUSICMIND-V4-SYNOPSIS.md` item 5.* Found investigating
`bpm_reliable`: reverb-heavy, atmospheric material can measure as
genuinely slow-tempo while still feeling tense or driving rather than
restful. Low BPM is a real signal but an incomplete proxy for
"relaxing." Nothing built, no scope decided yet — a confirmed gap
worth considering.

### 12. Second-opinion re-check for already-flagged tracks
*From the v3 punch list, noted as "genuinely good future direction,
not abandoned."* A targeted re-analysis pass for tracks already
flagged suspicious by three existing signals together: `bpm_reliable
= 0`, VA-resolution **REVIEW** confidence (the ~15.5% that didn't
resolve at the 84.5% HIGH-confidence rate), and thin tag coverage.
Not a general second-opinion system — narrowly scoped to tracks
multiple independent signals already agree are worth a second look.
Nothing built, no scope doc yet.

### 13. Chanting and chorales handling
*Raised 2026-08-28, roadmap-level placeholder only.* Noted for the
roadmap; details of the actual problem (mistagging, VI/instrumental
detection false positives, missing genre coverage, something else)
not yet described. Needs a real problem statement before this can
move toward being scoped — captured here so it isn't lost, not
because it's understood yet.

---

## ⚪ Considered and declined

Kept here explicitly so these don't get silently re-proposed.

### Mureka's audio-analysis API
*Discussed in `MUSICMIND-V4-SYNOPSIS.md` item 4.* Feasibility
genuinely tested (not just discussed) — the `/v1/song/describe`
endpoint works, real signal quality confirmed both on a clear-cut
case and an honestly-ambiguous one. **Decided PASS for now**: freeform
tags don't map onto the existing hand-curated genre vocabulary, no
BPM/key numbers returned, a full-library pass means uploading the
entire library's actual audio, and simple time/scope. A narrowly-
scoped "second opinion for already-flagged tracks" version remains a
real future option, not fully closed.

### Sharing one audio decode between Synapse and VI
Proven to hurt accuracy directly via a real ground-truth BPM test — a
closed door, not an open one.

### Loudness normalization (ReplayGain/EBU R128) and stem separation
(Demucs/Spleeter)
Explicitly ruled out when self-hosted audio tool ideas were discussed.

### A hand-maintained artist alias table as the *primary* mechanism
Too reactive, doesn't scale — only ever helps after a specific
mismatch is personally noticed. A small manual override table remains
a reasonable *secondary* fallback alongside the MusicBrainz-driven
approach (#2 above), not a replacement for it.

### A "scrobble grammar" convention for Louis to manually follow
Doesn't solve historical scrobble data, and asks too much consistency
of a human over years of listening.

---

## Suggested sequencing

Not a commitment, just a reasonable order given what's actually
scoped and what depends on what:

1. ~~**Country normalization** (#1)~~ — 🟢 shipped 2026-08-27.
2. **Artist aliases** (#2) — foundational; tracklist import (#4)
   depends on it. Next up.
3. **Tracklist import** (#4) — once aliases land.
4. **Thematic relevance** (#3) — independent of the above, can slot
   in anywhere; the most complex of the remaining scoped items (LLM
   candidate-pool pass), worth its own dedicated stretch.
5. **VA vote-count normalization** (#5) — small, self-contained,
   confirmed against real data (923/8,766 close-vote tracks). Could
   reasonably jump the queue given how cheap it is relative to its
   confirmed real impact — worth considering ahead of #2–#4 rather
   than strictly after them.
6. Everything in the 🟡 section (#6–#12) — pick up opportunistically,
   but each deserves its own scope doc (matching the discipline
   already applied to #1–#5) before implementation starts, not a
   shortcut straight to code.

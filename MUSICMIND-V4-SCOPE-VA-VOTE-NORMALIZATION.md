# v4 Scope: Artist-Name Normalization for AcoustID Vote Counting

**Status:** Scoped 2026-08-27. Promoted from the v3 punch list's
"leave as-is for now (July 25)" entry to a real v4 item, per that
entry's own stated condition: *"revisit only if a real track resolves
incorrectly because of a split vote... with real evidence."* That
evidence now exists.

## Why this moved from theoretical to real

`va_resolve.py` resolves Various Artists tracks via AcoustID
fingerprinting, picking the winning artist by plurality vote across
candidate recordings, keyed on the exact artist-name string returned
by each match. In July, the concern that the same real artist could
appear under multiple spellings and split its own vote count stayed
"purely theoretical" — it hadn't caused a problem on any real run,
including the full 4,254/5,033 production run.

A read-only diagnostic (`diagnose_va_vote_splits.py`) against the
real, current `va_results` table — now 8,766 resolved tracks, having
grown since July — checked every resolved track's raw `votes_json`
for cases where the top two candidates landed within 1 vote of each
other (the actual scenario where a spelling split can flip the
outcome). Result: **923 of 8,766 tracks (10.5%)** had a close vote.
Not every one of those is a bug — many are genuine plurality
disagreements between different real artists (different cover
versions, duet-credit variations) — but scanning the output surfaces
a clear, repeated, real pattern, not noise. Representative confirmed
cases:

- **"&" vs "and":** Dion & The Belmonts (3) vs. Dion and The
  Belmonts (2); Paul Revere and the Raiders (2) *tied* with Paul
  Revere & the Raiders (2)
- **"The" prefix:** The Gentlemen (2) vs. Gentlemen (1); The Uncalled
  For (1) *tied* with Uncalled For (1)
- **Pure case:** DEVO (2) vs. Devo (1)
- **Unicode hyphen** (the exact class of bug `normalize_for_matching()`
  was already built to catch elsewhere in this project): X-Ray Spex
  vs. X‑Ray Spex
- **"Orchestra"-suffix fragmentation, badly:** Percy Faith's 22 real
  votes split five ways — Percy Faith & His Orchestra (8), Percy
  Faith Orchestra (3), Percy Faith and His Orchestra (1), Percy
  Faith, His Orchestra (1), plus the winning "Percy Faith" (9) itself
  — landing HIGH confidence more by luck of the split than by a
  correctly counted plurality

## Why this matters beyond the resolution step itself

`chosen_artist` isn't just stored for reference — `va_resolve.py`
writes it directly to `tracks.real_artist`, which (per the July 21
VA-tagging fix already shipped) is what AI tagging reads from for
context, what artist enrichment (`mb_enrich_artists.py`,
`enrich_artists.py`) keys off of, and what
`resolve_recording_mbids.py` uses for free MBID backfill. A wrongly-
split vote doesn't just mislabel one field in isolation — it can
propagate into tags, artist metadata, and recording MBIDs downstream.

## Proposed fix — reuse what already works, know what it won't catch

`normalize_for_matching()` (in `lastfm_gaps.py`) is already proven in
production for exactly this class of problem — it currently handles:
curly quotes → straight, Unicode hyphens/dashes → ASCII, lowercasing,
whitespace collapse, "and" → "&", and apostrophe/hyphen stripping.
It is **not currently applied** to `va_resolve.py`'s vote-counting
keys at all.

**Checked against the real cases above, not assumed:**
- ✅ Would merge: DEVO/Devo (case), Dion & The Belmonts/Dion and The
  Belmonts ("and"→"&"), X-Ray Spex/X‑Ray Spex (Unicode hyphen)
- ❌ Would NOT merge: The Gentlemen/Gentlemen ("The" prefix — no
  existing logic strips this), Percy Faith & His Orchestra/Percy
  Faith Orchestra/Percy Faith, His Orchestra (no existing logic
  handles "Orchestra"-suffix phrasing variance), any case requiring
  multi-artist list reordering (e.g. "A, B" vs "B, A")

Proposed change to `va_resolve.py`'s `resolve()`: run each candidate
artist string through `normalize_for_matching()` before counting into
`votes`/`title_votes`, but keep the **original, unnormalized string**
as the value stored and eventually written to `real_artist` — the
vote key changes, not the display name. This means votes that differ
only by case/and-&/Unicode-punctuation correctly consolidate, while
still resolving to a real, human-readable artist name rather than a
lowercased normalized form.

Left explicitly unfixed by this pass (real, still-open sub-problems,
not silently ignored):
- **"The" prefix stripping** — genuinely risky to add blindly (some
  artists are legitimately different with/without "The" — needs a
  confirmed-safe rule, not blanket stripping)
- **"Orchestra"/"and His Orchestra"/", His Orchestra" suffix
  collapsing** — a real pattern in the big-band/orchestra corner of
  the library specifically, not handled by any existing normalization
  function
- **Multi-artist list reordering** — theorized in July, still
  theoretical; no confirmed case in the 923 found where reordering
  alone was the deciding factor

## Open question: already-resolved tracks

Two options, not decided yet:

1. **Fix going forward only** — apply the normalization to future
   `va_resolve.py` runs, leave the 8,766 already-resolved tracks as
   they are. Lowest risk, but the confirmed cases above (Percy Faith
   fragmented across 5 spellings, etc.) stay wrong until those tracks
   happen to get re-fingerprinted for some other reason.
2. **Targeted re-resolution pass** — similar precedent to how the
   July VA-tagging fix was paired with `clear_va_tags_for_retag.py`
   (a narrow, one-off script that only ever touched tracks meeting a
   specific real condition). Here: re-run `resolve()` only for tracks
   whose stored `votes_json` shows a close-vote pattern (exactly what
   `diagnose_va_vote_splits.py` already identifies), not the full
   8,766. Re-fingerprinting isn't needed — the raw AcoustID vote data
   is already sitting in `votes_json`; this is closer to a
   re-tabulation than a re-resolution, cheap and safe to run.

Leaning toward option 2, since the diagnostic already does the
identification work and re-tabulating from existing `votes_json` is
inexpensive — but flagging as an open decision, not resolved by this
doc.

## What this deliberately does NOT solve

- "The" prefix and "Orchestra"-suffix normalization (see above —
  real, but a separate, riskier follow-up, not bundled into this
  first pass)
- Multi-artist reordering — still no confirmed real case
- Any case where a close vote reflects genuinely different real
  artists (duet credits, cover versions) — that's correct plurality
  behavior, not a bug, and this fix must not incorrectly merge those

## Rough complexity estimate

Small: one function call added inside `resolve()`'s vote-counting
loop, reusing an already-proven normalization function — no new
fuzzy-matching logic for the first pass. The re-resolution-pass
question (if option 2) adds a narrow, `votes_json`-only re-tabulation
script, no re-fingerprinting required. Confirmed against real
production data (8,766 tracks, 923 close-vote cases) before writing
this doc, not assumed or guessed.

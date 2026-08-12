# v4 Scope: Thematic Relevance Scoring for Mood Playlists

**Status:** Scoped, not started. Core-product priority, not a
peripheral feature — this addresses a gap in what the mood-playlist
feature actually delivers, not a bug in the code that already exists.

## The real problem this solves

Confirmed via direct data from the Playlist Audit page (August 2026):
a "love songs" playlist, generated twice with near-identical prompts
("I want to hear some love songs" / "Songs about love"), returned 30
tracks of which roughly 4-5 were actually about love. The rest were
genre-and-mood-correct but thematically unrelated or actively
contradictory — most notably "Blasphemous Rumours" (Depeche Mode, a
song about a suicide attempt) and "Psycho Killer" (Talking Heads, a
song about a murderer) sitting in a "love songs" playlist.

This is not a tag-selection or bucket-selection bug. Directly
confirmed by re-running `view_logs.py --analyze` on both queries:
`classify_prompt()` correctly identified the mood as "romantic and
emotional," and `expand_prompt()` correctly selected 8 tags
tightly grouped around that vibe, constrained to the exact
manually-chosen buckets (New Wave / Post-Punk / Synth, Psych / Art
Rock / Experimental). Every part of the existing pipeline did its
job as designed.

The real gap: **every tag in the system describes sound — genre,
subgenre, era, style. Nothing describes subject matter.** "Love
songs" as a mood will always resolve to *some* genre/style subset,
because that's the only axis of information that exists. A
post-punk song about betrayal and a post-punk song about love are
indistinguishable to the current pipeline — they carry identical
tags.

## Why this is core, not a follow-on feature

Mood-based generation ("songs about X," "I want to hear Y") is a
primary entry point to the app, not an edge case. Prompts like
"tribal sounding songs" or "modern stuff" — where the user is
describing *sound*, not *subject* — work correctly today and don't
need this fix. But prompts describing a *theme* ("love songs,"
"breakup songs," "songs about summer," "songs about loss") will
silently produce the same failure mode demonstrated above, for any
theme, in any genre bucket, until this exists. This is a systemic
gap in the mood pipeline, not a one-off bad result.

## Confirmed: not a bucket-restriction artifact

A natural hypothesis after the first two failures: maybe the problem
was the manually-selected buckets (New Wave / Post-Punk / Synth,
Psych / Art Rock / Experimental) starving `expand_prompt()` of any
thematically-relevant tags, and removing bucket restriction would
fix it. Tested directly, not assumed: re-ran the same prompt
("love songs") with no bucket restriction, against the full library
tag pool (query #177). Result: 30/30 tracks read as genuine love
songs on manual review — "When a Man Loves a Woman," "Love Hurts,"
"Dedicated to the One I Love," "A Woman's Worth," and so on.

This looked at first like a fix, but it isn't one, and it's worth
being precise about why. `expand_prompt()` did exactly the same
thing it did in the failed runs — pick tags that sound close to
"romantic and emotional." The only difference is that this time the
candidate tag list it was choosing from happened to include several
tags that lean thematic rather than purely sonic: **romantic**,
**ballad**, **emotional**, **reflective**, alongside **soul**,
**soft rock**, **dream pop**, **singer-songwriter**. Those aren't
theme-evaluation — they're a lucky overlap between a handful of
mood-adjacent tag *names* and this specific prompt's *theme*. The
system still has no mechanism that reads "Blasphemous Rumours" or
"Psycho Killer" and knows those aren't about love — it just wasn't
offered tags that would have let a similarly wrong pick happen this
time.

The real test of that claim: a thematic prompt without a
conveniently-named tag in the pool. There is no **breakup**,
**grief**, **loss**, or **loneliness** tag anywhere in the full
185-tag list captured in query #177. A prompt like "breakup songs"
or "songs about losing someone" run today, bucketed or not, has no
reason to fare better than the original "love songs" failures — the
pipeline would fall back to whatever adjacent mood/style tags exist
(**melancholic**, **introspective**, **reflective**) and produce the
same style-correct, theme-blind result. This should be the next
real test case, not "love songs" again, since "love songs" is now
the one prompt we know can get lucky.

**Conclusion, and why this doesn't change the proposed mechanism:**
removing bucket restriction is not the fix. It's a smaller-scale
version of the same underlying failure — a system that matches mood
prompts against tag *names* rather than actually evaluating a
candidate track's theme. The gap is systemic to mood/theme matching
generally, confirmed to exist independent of bucket selection, and
the LLM relevance-scoring pass proposed below remains the real
mechanism — not a fallback to reach for only when the lucky-tag-name
path fails.

## What this deliberately is not

Not a request to rebuild tag-based matching. Genre/style tags remain
the correct mechanism for "sound" prompts and for narrowing the
candidate pool before thematic filtering — rebuilding that would be
solving a problem that doesn't exist. This scope is specifically
about adding a second, independent axis — thematic fit — that acts
*after* tag-based candidate selection, not instead of it.

## Proposed mechanism: LLM relevance scoring pass

Rather than a new structural data source (lyrics ingestion, a new
`theme_tags` table), the fastest real fix given "measure, don't
guess": add a scoring/filtering step using the same OpenAI
integration already proven throughout the pipeline (`expand_prompt()`,
`classify_prompt()`), applied to the *candidate list*, not the tag
selection.

Rough shape:

1. `classify_prompt()` already extracts `mood` (e.g. "romantic and
   emotional") — no new classification work needed there.
2. Tag-based matching runs as it does today, but pulls a **wider**
   candidate pool than the final 30 (e.g. 60-100), specifically so
   there's real headroom for a relevance filter to narrow *from*
   rather than re-ranking a pool that was already too small to
   filter meaningfully.
3. A new scoring call sends the candidate list (title + artist,
   batched — not one call per track) to OpenAI with the original
   mood/prompt, and asks it to flag which candidates are
   thematically consistent with the prompt versus merely
   genre/style-consistent.
4. Flagged-relevant tracks fill the final 30 first; if too few pass,
   fall back to genre/style-only tracks to still hit the requested
   count rather than returning a short playlist — but this fallback
   should be visible in `query_log` (a new field, e.g.
   `theme_filtered_count`), not silent, so a thin thematic match
   rate is measurable rather than invisible the way this bug was
   invisible until manually audited.
5. Only activates for `intent: mood` prompts where `mood` is
   thematic ("about X," "songs about Y") rather than purely
   sonic/situational ("driving to the airport," "modern stuff") —
   this distinction itself may need a `mood`/`theme` split similar
   to how `classify_prompt()` already splits other dimensions,
   rather than assuming every mood prompt needs the extra pass.

## Real open questions — need direct testing, not assumption

1. **Title/artist alone, or does this need real lyric content?**
   "Psycho Killer" is a case where title alone (with the model's own
   world knowledge of the song) correctly signals "not a love song."
   But plenty of songs have neutral or misleading titles relative to
   their actual lyrical content ("Love Song" as a title doesn't
   guarantee the lyrics are about love, and plenty of genuine love
   songs have titles that give no indication either way). Needs
   direct testing against real audited examples — not assumed to
   work from title/artist alone just because it worked for this
   specific case.
2. **Cost and latency at real scale.** A batched call against
   60-100 candidates adds real, measurable latency and OpenAI cost
   to every thematic mood-playlist generation, on top of the
   existing `classify_prompt()` + `expand_prompt()` calls. Needs a
   real cost/latency measurement against actual usage patterns
   before deciding this is the right long-term mechanism versus a
   heavier one-time investment (lyric-derived tags) that has zero
   marginal cost per generation afterward.
3. **Where "thematic" mood ends and "sonic/situational" mood
   begins**, so the extra pass only fires where it's actually
   needed. Prompts like "sad songs" or "songs about heartbreak" are
   clearly thematic. "Late night jazz" or "driving to the airport"
   are clearly not. There will be real ambiguous cases in between
   that need to be tested against, not designed for in the
   abstract.
4. **Batch size and prompt design for the scoring call itself** —
   how many candidates per call before quality degrades, and what
   the model actually needs (mood phrase alone, or the original
   full prompt) to score accurately. Needs a real test pass against
   this exact "love songs" case as the first validation, since it's
   already fully audited and the wrong answers are already known.

## Longer-term alternative, not proposed as the first pass

A real `theme_tags` table populated from an actual lyrics data
source, structurally parallel to `track_tags`, would remove the
per-generation cost entirely and could support thematic search
(`title_search`-style) directly, not just mood-filtering. This is a
meaningfully heavier lift — a new external data dependency, a new
ingestion/enrichment script, and real questions about lyrics API
coverage and licensing — closer in shape and cost to the MusicBrainz
alias work than to a quick fix. Worth keeping in view once the
scoring-pass approach is measured against real usage, but not the
right starting point: "measure, don't guess" argues for validating
that thematic filtering actually solves the problem, cheaply, before
committing to a bigger data-ingestion investment.

## Validation plan

Before considering this done, re-run the exact two failed prompts
from this session ("I want to hear some love songs," "Songs about
love") against the same buckets and confirm, via the Playlist Audit
page, that tracks like "Blasphemous Rumours" and "Psycho Killer" are
now correctly excluded and that the thematically-relevant tracks
already found ("Modern Love," "Love Song," "Vote for Love," "Running
Up That Hill") are retained. Matches the same discipline already
used throughout this project — re-run the exact failed case to
confirm a fix genuinely works, not just that it passes in the
abstract.

Critically, also test a prompt with no lucky tag-name overlap in the
pool — e.g. "breakup songs" or "songs about losing someone" — since
"love songs" is now confirmed to be the easy case. A fix that only
solves "love songs" (already solvable today, without bucket
restriction, by accident) hasn't actually solved the systemic gap.
The real bar is a thematic prompt with no matching tag name at all,
correctly returning tracks that are actually about that theme
regardless of what tags happen to exist in the vocabulary.

## Rough complexity estimate

- Wider candidate pool pull before final selection: small, mostly a
  query-limit change
- New scoring/filtering call + prompt design: moderate — new prompt
  engineering, needs real testing against the audited failure case
- `theme_filtered_count` (or similar) logging so thin thematic match
  rates are visible going forward, not silently discovered again by
  manual audit: small, same shape as the existing `buckets` logging
  already added to `query_log` this session
- Mood/theme dimension split in `classify_prompt()`, if needed to
  gate when the extra pass fires: small-to-moderate, same shape as
  existing dimension additions

Not yet estimated: cost/latency impact at real scale, which needs
direct measurement (open question #2) before this can be called a
complete estimate.

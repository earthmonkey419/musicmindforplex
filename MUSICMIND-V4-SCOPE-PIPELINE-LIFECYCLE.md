# v4 Scope: Pipeline Lifecycle (stop, lock, and restart-safety)

**Status:** Scoped 2026-11-09. First item in the reviewed v4 priority
order. Opened as a problem area 2026-08-30 with two symptoms and no
scope doc; this is that doc. Nothing is built.

**Evidence key:** **VERIFIED** = read directly in the code on `v4-dev`
(3.1.0 + two follow-on commits) while writing this doc. **NOT VERIFIED**
= inferred, or needs a real experiment before it can drive a design.

## The two symptoms, and the one question under them

1. **No clean way to stop a running job.** The admin page has no Stop
   control anywhere. The only way to interrupt anything is
   `pm2 restart`.
2. **Nothing stops outside interference mid-run.** Only two scripts
   take a lock; a restart, a second click, or a scheduled shell chain
   can overlap a Full Sync.

Both reduce to one question: **what is the safe-shutdown contract for
a running pipeline** — whether the interruption is deliberate (a Stop
button) or accidental (`pm2 restart` racing a run)? Everything below
is an attempt to answer that once, in one place.

## What the code actually does today

- **VERIFIED — run state lives in memory only.** `running = {}` in
  `web/app.py` holds booleans keyed by script name. No PID, no process
  handle, no start time. It is empty after any app restart.
- **VERIFIED — two runner paths, different plumbing.** Generic
  `/run/<script>` (the admin "Run Now" dispatcher, 12 scripts) reads
  `proc.stdout` through a `PIPE` inside the SSE generator. Full Sync
  runs on a background thread (`_run_fullsync_pipeline`) and uses
  `tail_subprocess()`, which is file-backed. Both launch children with
  `start_new_session=True`. There are also dedicated routes
  (`synapse-full`, `resync`, `synapse-count/estimate/limited`, tests).
- **VERIFIED — Full Sync's orchestrator is a daemon thread inside the
  Flask process.** It walks 11 steps in order and stops on the first
  non-zero exit. If the Flask process dies, the thread dies with it.
- **VERIFIED — only two scripts have lock files:** `synapse_analyze.py`
  (`synapse.lock`) and `lastfm_sync.py` (`lastfm_sync.lock`). Both use
  the same pattern: write own PID; on start, if a lock exists, check
  `/proc/<pid>/cmdline` to confirm the PID is genuinely that script
  (PID reuse), and treat a dead PID as a stale lock to overwrite.
  The other nine pipeline scripts take no lock.
- **VERIFIED — no signal handling anywhere** (`signal.signal` and
  `SIGTERM` appear in no script or in `web/app.py`). A SIGTERM is the
  default: immediate death, no cleanup.
- **VERIFIED — `/admin/other-processes-status` scans `/proc` cmdlines**
  for 12 known script names. It is advisory and the only thing that
  can see scripts launched outside the app (SSH, scheduled chain).
  **NOT VERIFIED:** whether any start route consults it before
  launching.
- **VERIFIED — an existing UI line says a dropped connection does not
  stop a sync** (`admin.html`), which is true but leaves the user with
  no stop affordance at all.

### Consequence for a restart during Full Sync (derived from the above)

The current step's child process is detached, but the orchestrator
thread dies with Flask. So the step in flight can finish **orphaned**,
steps after it **never start**, `running['fullsync']` is `False` again
so the UI offers a fresh Full Sync, and a second run can overlap the
orphan on the same SQLite file. Of the steps, only Synapse and
Last.fm would refuse to double-run. **NOT VERIFIED:** that sequence
end to end; and `streamlog_*.log` temp files may be left behind in the
app directory when the generator's `finally` never runs.

### One contradiction to settle before designing anything

The July fix comment in `run_script` says `start_new_session=True`
protects a child from `pm2 restart`. The Aug 30 problem notes say
`pm2 restart` kills coupled subprocesses mid-run. Both could be true
(PM2 may kill by walking the process tree rather than the process
group, which `start_new_session` does not escape). **Phase 0 below
resolves this with a real experiment.** The design differs
depending on the answer.

## The contract (proposed)

**Invariant: every pipeline script must be safe to re-run after being
interrupted at any instant.** Graceful stop is an optimization that
saves work; correctness never depends on it. This is already true in
spirit (Synapse is documented as resumable; most steps select on
"not yet processed"), but it has never been stated or tested per
script.

Run states: `running` → `stopping` → `stopped` (clean) or `killed`
(forced), plus `finished` and `failed`. Stop escalates: ask nicely
(SIGTERM to the process group), wait a bounded time, then SIGKILL.

## Proposed design

**1. One lock helper, used by every script.** Generalize the proven
Synapse/Last.fm pattern into a small shared module (working name
`pipeline_lock.py`): `acquire(name)`, `release(name)`,
`is_alive(name)`, PID + cmdline verification, stale-lock takeover.
Locks are taken **by the script itself, not by the web app**, so a
scheduled shell chain or an SSH-run script respects them too. This is
the main reason not to do it app-side.

**2. `fullsync.lock`, taken by the orchestrator.** Holds PID, start
time, current step index and label. Starting any admin script while
it is live is refused with a plain-language reason.

**3. A graceful-stop handler for the long-running scripts.** One shared
`install_stop_handler()`: SIGTERM sets a flag; the script finishes the
current unit of work (track, batch), commits, releases its lock, exits
with a distinct code. Applied first to the scripts where interruption
costs the most (Synapse, fingerprinting, VA resolve, tagging,
enrichment, Last.fm). Scripts not covered still honor the invariant by
being resumable; they just lose the in-flight batch.

**4. A Stop control.** Per running job and for Full Sync. Reads the PID
from the lock file, `killpg` to the child's session, bounded wait, then
escalate. Confirm dialog. After a stop, the page shows where it
stopped ("stopped during step 4 of 11") and offers **Resume** (run the
remaining steps; safe because steps are idempotent) or **Start over**.

**5. Move Full Sync's orchestrator out of the Flask process.**
Run it as its own detached process (same shape as the existing
`synapse-full` route: start, lock, status endpoint), with the Flask app
only starting, observing and stopping it. A `pm2 restart` then becomes
harmless by construction rather than by luck, and it removes the
orphan scenario above. This is the largest change and is last.

**6. Reconcile at app startup.** Replace the in-memory `running` dict
as the source of truth with the lock files: on boot, scan them; a dead
PID means clean it up, a live PID means adopt it and reattach the log
tail. Keep the dict as a cache.

### Alternative considered: patch the thread model only

Keep the daemon-thread orchestrator and add startup recovery that
detects an orphaned step and offers Resume. Smaller, but it leaves
`pm2 restart` as a hazard and the design depends on the orphan
surviving, which is exactly the **NOT VERIFIED** point above. Kept as
the fallback if Phase 5 proves more than it is worth.

## Per-script interruption safety (to be filled in by Phase 0)

Counts below are `commit()` calls, **VERIFIED**; they are a hint at
granularity, not a safety verdict.

| Script | commit() calls | Interruption verdict |
|---|---|---|
| `musicmind_ingest.py` | 5 | **To test** — upsert is `ON CONFLICT DO UPDATE` since 2026-09-06; commits inside the loop and once at the end |
| `fingerprint_tracks.py` | 3 | To test |
| `copy_forward_analysis.py` | 2 | To test |
| `va_resolve.py` | 3 | To test (documented resumable) |
| `enrich_compilations.py` | 2 | To test |
| `resolve_recording_mbids.py` | 3 | To test |
| `lastfm_sync.py` | 8 | To test (has lock already) |
| `mb_enrich_artists.py` | 4 | To test |
| `enrich_artists.py` | 2 | To test |
| `plex_tag_tracks.py` | 2 | To test |
| `synapse_analyze.py` | 2 | Documented resumable; has lock |

## Phases

- **Phase 0 — two experiments, no code.** (a) Settle the
  `pm2 restart` contradiction: start a long job, restart the app, and
  see whether the child survives. (b) Interrupt each script above
  mid-run with `kill -TERM` and `kill -9` against a **copy** of
  `musicmind.db`, run the integrity assertions on the Tests page, and
  record the verdict in the table. Output: a filled-in table and a
  decision on step 5.
- **Phase 1 — lock helper and `fullsync.lock`.** No UI change.
  Immediately closes the overlap hole, including for scheduled chains.
- **Phase 2 — graceful-stop handler** in the high-value scripts.
- **Phase 3 — Stop button and Resume.**
- **Phase 4 — detached Full Sync runner and startup reconciliation**
  (or the fallback above, per Phase 0).

Each phase is independently shippable and independently useful.

## Test plan (real data, per the usual rule)

Every test runs against a copy of `musicmind.db`, with a
`musicmind.pre-<name>.db` backup taken first. After **each**
interruption, run the Tests-page integrity assertions and compare
before/after counts — especially `is_instrumental` NULLs and
`real_artist`, since an interruption during ingest is exactly the
shape of the 2026-09-06 data-loss incident. Required cases: double
start refused; stop mid-step then resume completes the pipeline;
`kill -9` of the orchestrator then app restart reconciles cleanly;
scheduled-chain script refused while Full Sync holds the lock; stale
lock from a dead PID is taken over; Docker (PID namespace) behaves the
same as native.

## Open questions for Louis

1. Should **Stop** on Full Sync mean "stop now" or "finish the current
   step, then stop"? (Proposed: offer both; default to finish-step.)
2. Should the existing scheduled shell chain be switched to run
   through the same lock, or left alone and merely refused when a
   lock is held?
3. Is losing the in-flight batch on a hard kill acceptable for the
   scripts without a stop handler, as long as re-running is safe?

## What this deliberately does NOT solve

- Pause/resume of a single item mid-flight.
- A job queue, scheduler, or running jobs in parallel on purpose.
- Moving to an external task runner (Celery, RQ). A lock file and a
  detached process are enough for one NAS and one user.
- Making a hard `kill -9` lossless. The goal is that it is always
  recoverable, not that nothing is ever lost.
- Windows-native support. The `/proc`-based checks are Linux-only,
  which already matches every supported install (NAS, Linux, WSL,
  Docker).

## Rough complexity estimate

Smallest, highest-value piece: **Phase 1** (a shared helper and one
new lock). **Phase 3** is moderate (UI plus `killpg` plumbing).
**Phase 4** is the largest and the only one that touches how Full Sync
is started. No dependency on aliases, thematic relevance, or any other
v4 item.

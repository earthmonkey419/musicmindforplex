"""Stable command names for the web UI and documented CLI workflows."""

MODULES = {
    "ingest.py": "musicmind.ingest",
    "sync.py": "musicmind.lastfm.sync",
    "gaps.py": "musicmind.lastfm.gaps",
    "tag_tracks.py": "musicmind.plex.tag_tracks",
    "listening_context.py": "musicmind.analysis.listening_context",
    "synapse_analyze.py": "musicmind.analysis.synapse_analyze",
    "fingerprint_tracks.py": "musicmind.analysis.fingerprint_tracks",
    "copy_forward_analysis.py": "musicmind.analysis.copy_forward_analysis",
    "dedup_report.py": "musicmind.analysis.dedup_report",
    "va_resolve.py": "musicmind.enrichment.va_resolve",
    "resolve_recording_mbids.py": "musicmind.enrichment.resolve_recording_mbids",
    "mb_enrich_artists.py": "musicmind.enrichment.mb_enrich_artists",
    "enrich_artists.py": "musicmind.enrichment.enrich_artists",
    "enrich_compilations.py": "musicmind.enrichment.enrich_compilations",
    "resync_item.py": "musicmind.resync_item",
}

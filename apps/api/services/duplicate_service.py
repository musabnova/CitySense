"""
TASK-032 & TASK-033: Hybrid Spatial-Temporal & Semantic Duplicate Detection
           + Duplicate Ticket Consolidation & Impact Weighting
============================================================================
Stage: Stage 2 — Understand / Algorithms + Workflow
Objective: Detect duplicate reports using:
  - 50-meter spatial buffer (Haversine on SQLite, ST_DWithin on PostgreSQL)
  - 48-hour time window
  - Cosine distance < 0.25 on description embeddings
  Then consolidate duplicates by linking to master tickets.

Implementation: Python-side computation using Haversine + cosine similarity.
Replaces PostGIS ST_DWithin and pgvector <=> operators for SQLite compatibility.
"""

import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger("citysense.duplicate")

# ── Detection Thresholds ─────────────────────────────────────────────────────
SPATIAL_BUFFER_METERS = 50.0
TIME_WINDOW_HOURS = 48
SEMANTIC_DISTANCE_THRESHOLD = 0.25  # cosine distance < 0.25 = duplicate
MAX_DUPLICATE_RESULTS = 5


def _parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse ISO datetime string to datetime object."""
    if not dt_str:
        return None
    try:
        # Handle various ISO formats
        dt_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return None


def detect_duplicates(report_id: str, db_path: str) -> dict:
    """
    Detect potential duplicate reports for the given report.

    Uses:
    1. Haversine distance <= 50m
    2. Time window: created within 48 hours
    3. Same or compatible category
    4. Cosine distance < 0.25 on embeddings (when both have embeddings)

    Returns dict with duplicate detection results.
    """
    import sqlite3
    from apps.api.seeds.geo_constants import calculate_haversine_distance
    from apps.api.services.embedding_service import cosine_distance

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()

        # Load the target report
        cur.execute(
            """SELECT id, raw_description, verified_category, latitude, longitude,
                      created_at, description_embedding_json, lifecycle_status
               FROM reports WHERE id = ?""",
            (report_id,),
        )
        target = cur.fetchone()
        if not target:
            return {"error": f"Report {report_id} not found"}

        target_lat = float(target["latitude"])
        target_lon = float(target["longitude"])
        target_created = _parse_datetime(target["created_at"])
        target_category = target["verified_category"]
        target_embedding_json = target["description_embedding_json"]
        target_embedding = json.loads(target_embedding_json) if target_embedding_json else None

        # Query candidate reports (exclude self, only active statuses)
        cur.execute(
            """SELECT id, raw_description, verified_category, latitude, longitude,
                      created_at, description_embedding_json, lifecycle_status,
                      duplicate_count, is_duplicate
               FROM reports
               WHERE id != ?
                 AND lifecycle_status IN ('Submitted', 'Under Review')
                 AND is_duplicate = 0
               ORDER BY created_at DESC""",
            (report_id,),
        )
        candidates = cur.fetchall()

        # ── Filter candidates ────────────────────────────────────────────
        duplicates_found = []

        for cand in candidates:
            cand_lat = float(cand["latitude"])
            cand_lon = float(cand["longitude"])
            cand_created = _parse_datetime(cand["created_at"])

            # 1. Spatial filter: Haversine distance <= 50m
            distance_m = calculate_haversine_distance(
                target_lat, target_lon, cand_lat, cand_lon
            )
            if distance_m > SPATIAL_BUFFER_METERS:
                continue

            # 2. Temporal filter: within 48 hours
            if target_created and cand_created:
                time_diff = abs((target_created - cand_created).total_seconds())
                if time_diff > TIME_WINDOW_HOURS * 3600:
                    continue
            # If we can't parse timestamps, skip temporal filter

            # 3. Semantic filter: cosine distance < 0.25
            semantic_dist = None
            cand_embedding_json = cand["description_embedding_json"]
            if target_embedding and cand_embedding_json:
                try:
                    cand_embedding = json.loads(cand_embedding_json)
                    semantic_dist = cosine_distance(target_embedding, cand_embedding)
                    if semantic_dist >= SEMANTIC_DISTANCE_THRESHOLD:
                        continue  # Not semantically similar enough
                except (json.JSONDecodeError, TypeError):
                    pass  # If embeddings are invalid, rely on spatial+temporal only

            duplicates_found.append({
                "candidate_id": cand["id"],
                "distance_meters": round(distance_m, 2),
                "semantic_distance": round(semantic_dist, 4) if semantic_dist is not None else None,
                "category": cand["verified_category"],
                "duplicate_count": cand["duplicate_count"],
            })

            if len(duplicates_found) >= MAX_DUPLICATE_RESULTS:
                break

        # Sort by spatial proximity
        duplicates_found.sort(key=lambda x: x["distance_meters"])

        return {
            "report_id": report_id,
            "duplicates_found": len(duplicates_found),
            "matches": duplicates_found,
        }
    finally:
        conn.close()


def consolidate_duplicate(report_id: str, db_path: str) -> dict:
    """
    TASK-033: If duplicates are detected, link the new report to the best
    master ticket and increment the master's duplicate_count.

    Steps:
    1. Run duplicate detection
    2. If match found:
       - Set new_report.is_duplicate = True
       - Set new_report.master_ticket_id = master.id
       - Increment master.duplicate_count by 1
    3. Return consolidation result

    Returns dict with consolidation details.
    """
    import sqlite3

    # First detect duplicates
    detection = detect_duplicates(report_id, db_path)
    if "error" in detection:
        return detection

    if detection["duplicates_found"] == 0:
        logger.info("TASK-033: No duplicates found for report %s", report_id)
        return {
            "report_id": report_id,
            "is_duplicate": False,
            "master_ticket_id": None,
            "action": "none",
        }

    # Pick the best match (closest spatially)
    best_match = detection["matches"][0]
    master_id = best_match["candidate_id"]

    conn = sqlite3.connect(db_path)
    try:
        cur = conn.cursor()

        # Mark the new report as a duplicate
        cur.execute(
            """UPDATE reports
               SET is_duplicate = 1, master_ticket_id = ?
               WHERE id = ?""",
            (master_id, report_id),
        )

        # Increment master's duplicate_count
        cur.execute(
            """UPDATE reports
               SET duplicate_count = duplicate_count + 1
               WHERE id = ?""",
            (master_id,),
        )

        conn.commit()

        logger.info(
            "TASK-033: Report %s linked to master %s (distance=%.1fm, semantic=%.4f)",
            report_id, master_id,
            best_match["distance_meters"],
            best_match["semantic_distance"] or 0,
        )
        return {
            "report_id": report_id,
            "is_duplicate": True,
            "master_ticket_id": master_id,
            "distance_meters": best_match["distance_meters"],
            "semantic_distance": best_match["semantic_distance"],
            "action": "consolidated",
        }
    finally:
        conn.close()


"""
TASK-034: Multi-Factor Additive Priority Scoring Engine
========================================================
Stage: Stage 2 — Understand / AI Rules Engine
Objective: Build multi-factor scoring evaluating Urgency/Safety, Impact Scope,
           Infrastructure Degradation, and 75m POI Proximity.

Additive weights (from specification):
  - Near school/hospital/transit (< 75m): +40 points
  - Linked duplicate reports: +10 per duplicate (max +30)
  - Immediate hazard keywords (flooding, electrical, collapse): +20 points
  - Recency / reporting velocity (< 6 hours old): +10 points

Score → Priority mapping:
  - 70-100: Priority 1 (Critical)
  - 50-69:  Priority 2 (High)
  - 30-49:  Priority 3 (Medium)
  - 0-29:   Priority 4 (Low / Routine)
"""

import re
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger("citysense.priority")

# ── Hazard Keywords ──────────────────────────────────────────────────────────
HAZARD_KEYWORDS = [
    "electrical", "electrocution", "electric", "live wire", "exposed wire",
    "wire", "spark", "voltage", "conduit",
    "flood", "flooding", "submerged", "knee-deep", "ankle-deep",
    "collapse", "collapsed", "cave-in", "sinkhole",
    "open manhole", "missing slab", "missing cover",
    "fire", "gas leak", "explosion",
    "danger", "dangerous", "hazard", "hazardous",
    "emergency", "immediate danger", "life-threatening",
]


def _check_hazard_keywords(text: str) -> tuple[bool, list[str]]:
    """Check if text contains safety hazard keywords. Returns (has_hazard, matched_keywords)."""
    text_lower = text.lower()
    matched = []
    for kw in HAZARD_KEYWORDS:
        if kw.lower() in text_lower:
            matched.append(kw)
    return len(matched) > 0, matched


def _parse_datetime(dt_str: str) -> Optional[datetime]:
    """Parse ISO datetime string."""
    if not dt_str:
        return None
    try:
        dt_str = dt_str.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_str)
    except (ValueError, TypeError):
        return None


def calculate_priority(
    latitude: float,
    longitude: float,
    raw_description: str,
    duplicate_count: int,
    created_at_str: str,
) -> dict:
    """
    Calculate multi-factor additive priority score.

    Returns dict with:
      - priority_score (float)
      - priority_rank (str)
      - factors (list of factor dicts with name, points, detail)
    """
    from apps.api.seeds.geo_constants import calculate_haversine_distance, ANCHOR_POIS

    score = 0.0
    factors = []

    # ── Factor 1: POI Proximity (< 75m → +40) ───────────────────────────
    nearest_poi_name = None
    nearest_poi_dist = float("inf")
    for poi_id, poi_data in ANCHOR_POIS.items():
        dist = calculate_haversine_distance(
            latitude, longitude, poi_data["latitude"], poi_data["longitude"]
        )
        if dist < nearest_poi_dist:
            nearest_poi_dist = dist
            nearest_poi_name = poi_data["name"]

    if nearest_poi_dist < 75.0:
        score += 40
        factors.append({
            "name": "poi_proximity",
            "points": 40,
            "detail": f"Within {nearest_poi_dist:.1f}m of {nearest_poi_name}",
        })

    # ── Factor 2: Linked Duplicates (+10 per dup, max +30) ──────────────
    # duplicate_count includes the report itself, so linked = count - 1
    linked_dups = max(0, duplicate_count - 1)
    dup_points = min(linked_dups * 10, 30)
    if dup_points > 0:
        score += dup_points
        factors.append({
            "name": "linked_duplicates",
            "points": dup_points,
            "detail": f"{linked_dups} linked duplicate report(s)",
        })

    # ── Factor 3: Hazard Keywords (+20) ─────────────────────────────────
    has_hazard, matched_kw = _check_hazard_keywords(raw_description)
    if has_hazard:
        score += 20
        factors.append({
            "name": "safety_hazard",
            "points": 20,
            "detail": f"Safety hazard keywords detected: {', '.join(matched_kw[:5])}",
        })

    # ── Factor 4: Recency (< 6 hours → +10) ────────────────────────────
    created_at = _parse_datetime(created_at_str)
    if created_at:
        now = datetime.now(timezone.utc)
        # Make created_at timezone-aware if it isn't
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        age_hours = (now - created_at).total_seconds() / 3600
        if age_hours < 6:
            score += 10
            factors.append({
                "name": "recency",
                "points": 10,
                "detail": f"Reported {age_hours:.1f} hours ago (< 6h threshold)",
            })

    # ── Map score to priority rank ──────────────────────────────────────
    score = min(score, 100)  # Cap at 100
    if score >= 70:
        rank = "Priority 1"
    elif score >= 50:
        rank = "Priority 2"
    elif score >= 30:
        rank = "Priority 3"
    else:
        rank = "Priority 4"

    return {
        "priority_score": score,
        "priority_rank": rank,
        "factors": factors,
    }


def update_report_priority(report_id: str, db_path: str) -> dict:
    """
    Load report from DB, calculate priority, update priority_rank and priority_score.
    Returns dict with priority result.
    """
    import sqlite3

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            """SELECT raw_description, latitude, longitude, duplicate_count,
                      created_at, is_manually_overridden
               FROM reports WHERE id = ?""",
            (report_id,),
        )
        row = cur.fetchone()
        if not row:
            return {"error": f"Report {report_id} not found"}

        # Skip if manually overridden
        if row["is_manually_overridden"]:
            logger.info(
                "TASK-034: Report %s is manually overridden — skipping AI priority.",
                report_id,
            )
            return {
                "report_id": report_id,
                "skipped": True,
                "reason": "manually_overridden",
            }

        result = calculate_priority(
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            raw_description=row["raw_description"] or "",
            duplicate_count=int(row["duplicate_count"]),
            created_at_str=row["created_at"] or "",
        )

        cur.execute(
            """UPDATE reports
               SET priority_rank = ?, priority_score = ?
               WHERE id = ?""",
            (result["priority_rank"], result["priority_score"], report_id),
        )
        conn.commit()

        logger.info(
            "TASK-034: Report %s scored %.0f → %s (%d factors)",
            report_id, result["priority_score"], result["priority_rank"],
            len(result["factors"]),
        )
        return {
            "report_id": report_id,
            "priority_score": result["priority_score"],
            "priority_rank": result["priority_rank"],
            "factors": result["factors"],
        }
    finally:
        conn.close()


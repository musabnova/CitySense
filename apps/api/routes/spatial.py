"""
FastAPI Route Handlers for Spatial Endpoints (Phase 6: Reveal)
=============================================================
TASK-037: GET /api/v1/spatial/reports
TASK-039: GET /api/v1/spatial/hotspots
"""

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Optional, List, Dict, Any
from pathlib import Path
import sqlite3

from apps.api.services.clustering_service import detect_spatial_clusters

router = APIRouter(prefix="/api/v1/spatial", tags=["spatial"])
DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "citysense.db"


@router.get("/reports")
def get_spatial_reports_geojson(
    ward_id: Optional[str] = Query(None),
    lifecycle_status: Optional[str] = Query(None),
    priority_rank: Optional[str] = Query(None)
) -> Dict[str, Any]:
    """
    TASK-037: Returns an RFC 7946-compliant GeoJSON FeatureCollection of reports.
    Geometry coordinates are strictly [longitude, latitude].
    """
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        query = "SELECT * FROM reports WHERE 1=1"
        args = []

        if lifecycle_status:
            query += " AND lifecycle_status = ?"
            args.append(lifecycle_status)
        if priority_rank:
            query += " AND priority_rank = ?"
            args.append(priority_rank)

        query += " ORDER BY created_at DESC"
        cur.execute(query, tuple(args))
        rows = [dict(r) for r in cur.fetchall()]

        features = []
        for r in rows:
            lon = float(r["longitude"])
            lat = float(r["latitude"])
            feature = {
                "type": "Feature",
                "id": r["id"],
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]  # GeoJSON standard: [lon, lat]
                },
                "properties": {
                    "id": r["id"],
                    "tracking_id": r["tracking_id"],
                    "raw_description": r["raw_description"],
                    "user_category": r["user_category"],
                    "verified_category": r["verified_category"],
                    "media_url": r["media_url"],
                    "formatted_address": r["formatted_address"],
                    "concise_summary": r["concise_summary"],
                    "is_duplicate": bool(r["is_duplicate"]),
                    "master_ticket_id": r["master_ticket_id"],
                    "duplicate_count": int(r["duplicate_count"]),
                    "priority_rank": r["priority_rank"],
                    "priority_score": float(r["priority_score"]),
                    "priority_rationale": r["priority_rationale"],
                    "lifecycle_status": r["lifecycle_status"],
                    "assigned_department": r["assigned_department"],
                    "created_at": r["created_at"]
                }
            }
            features.append(feature)

        return {
            "type": "FeatureCollection",
            "features": features
        }
    finally:
        conn.close()


@router.get("/hotspots")
def get_spatial_hotspots() -> List[Dict[str, Any]]:
    """
    TASK-039: Returns array of hotspot clusters with counts, category breakdown,
    center point and boundary GeoJSON.
    """
    clusters = detect_spatial_clusters(db_path=str(DB_PATH))
    output = []
    for c in clusters:
        output.append({
            "cluster_id": c["cluster_id"],
            "title": c["title"],
            "total_reports": c["total_reports"],
            "category_breakdown": c["category_breakdown"],
            "center_point": c["center_point"],
            "boundary_geojson": c["boundary_geojson"]
        })
    return output


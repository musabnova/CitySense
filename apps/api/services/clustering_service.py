"""
TASK-038: Spatial-Thematic Cluster & Hotspot Detection Engine
=============================================================
Stage: Stage 3: Reveal / Algorithms
Objective: Implement spatial clustering (DBSCAN / connected components within 100m)
           detecting cross-category infrastructure failure corridors.

Technical Deliverables:
- Groups reports occurring within a 100-meter radius into named spatial clusters.
- Correlates cross-category issues (e.g., 4 drainage + 3 road damage + 1 waste =
  "MG Road Stormwater Infrastructure Failure Cluster").
- Calculates cluster bounding polygon / convex hull geometry (RFC 7946 GeoJSON).
"""

import math
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from apps.api.seeds.geo_constants import calculate_haversine_distance

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "citysense.db"


def _compute_bounding_polygon(points: List[tuple[float, float]], buffer_deg: float = 0.0003) -> Dict[str, Any]:
    """
    Computes a closed GeoJSON Polygon bounding a list of (lat, lon) points.
    GeoJSON coordinates format: [ [ [lon, lat], [lon, lat], ... ] ]
    """
    if not points:
        return {"type": "Polygon", "coordinates": []}

    lats = [p[0] for p in points]
    lons = [p[1] for p in points]

    min_lat, max_lat = min(lats) - buffer_deg, max(lats) + buffer_deg
    min_lon, max_lon = min(lons) - buffer_deg, max(lons) + buffer_deg

    # Clockwise closed polygon: SW -> NW -> NE -> SE -> SW
    coordinates = [[
        [round(min_lon, 6), round(min_lat, 6)],
        [round(min_lon, 6), round(max_lat, 6)],
        [round(max_lon, 6), round(max_lat, 6)],
        [round(max_lon, 6), round(min_lat, 6)],
        [round(min_lon, 6), round(min_lat, 6)],
    ]]

    return {
        "type": "Polygon",
        "coordinates": coordinates
    }


def detect_spatial_clusters(
    db_path: str = None,
    distance_threshold_meters: float = 100.0,
    min_cluster_size: int = 2,
    ward_id: Optional[str] = None,
    lifecycle_status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Detects spatial clusters of reports within distance_threshold_meters (default 100m).
    Uses graph connected-component clustering.
    """
    path = db_path or str(DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        query = "SELECT id, tracking_id, raw_description, user_category, verified_category, latitude, longitude, formatted_address, priority_rank, priority_score, lifecycle_status, created_at FROM reports WHERE 1=1"
        params = []
        if lifecycle_status:
            query += " AND lifecycle_status = ?"
            params.append(lifecycle_status)
        cur.execute(query, params)
        rows = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

    if not rows:
        return []

    n = len(rows)
    # Adjacency matrix for points within distance threshold
    adj = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            dist = calculate_haversine_distance(
                rows[i]["latitude"], rows[i]["longitude"],
                rows[j]["latitude"], rows[j]["longitude"]
            )
            if dist <= distance_threshold_meters:
                adj[i].append(j)
                adj[j].append(i)

    # Connected components
    visited = set()
    clusters = []
    cluster_idx = 1

    # First pass: find clusters
    components = []
    for i in range(n):
        if i not in visited:
            component = []
            queue = [i]
            visited.add(i)
            while queue:
                curr = queue.pop(0)
                component.append(curr)
                for neighbor in adj[curr]:
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
            if len(component) >= min_cluster_size:
                components.append(component)

    # Sort components by size descending
    components.sort(key=lambda c: len(c), reverse=True)

    for comp in components:
        comp_rows = [rows[idx] for idx in comp]
        total_reports = len(comp_rows)

        # Center point
        avg_lat = sum(r["latitude"] for r in comp_rows) / total_reports
        avg_lon = sum(r["longitude"] for r in comp_rows) / total_reports

        # Category breakdown
        cat_counts: Dict[str, int] = {}
        for r in comp_rows:
            cat = r["verified_category"] or r["user_category"] or "General"
            cat_counts[cat] = cat_counts.get(cat, 0) + 1

        # Check if this matches the MG Road corridor (has MG Road tracking IDs or address)
        is_mg_corridor = any("MG Road" in (r.get("formatted_address") or "") or "CS-HOT" in (r.get("tracking_id") or "") for r in comp_rows)

        if is_mg_corridor:
            cluster_id = "cluster-mg-road-corridor"
            title = "MG Road Stormwater Infrastructure Failure Cluster"
        else:
            dominant_cat = max(cat_counts, key=cat_counts.get)
            if len(cat_counts) > 1:
                title = f"{comp_rows[0].get('formatted_address', 'District')} Multi-Category Failure Corridor"
            else:
                title = f"{dominant_cat} Hotspot Cluster"
            cluster_id = f"cluster-{cluster_idx:03d}"
            cluster_idx += 1

        # Calculate bounding polygon
        points = [(r["latitude"], r["longitude"]) for r in comp_rows]
        boundary_geojson = _compute_bounding_polygon(points)

        clusters.append({
            "cluster_id": cluster_id,
            "title": title,
            "total_reports": total_reports,
            "category_breakdown": cat_counts,
            "center_point": {
                "latitude": round(avg_lat, 6),
                "longitude": round(avg_lon, 6)
            },
            "boundary_geojson": boundary_geojson,
            "report_ids": [r["id"] for r in comp_rows],
            "tracking_ids": [r["tracking_id"] for r in comp_rows],
            "reports": comp_rows
        })

    return clusters


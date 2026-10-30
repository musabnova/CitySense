"""
TASK-042: Spatial Analytics & Hotspot API Integration Test Suite
================================================================
Stage: Stage 3: Reveal / Testing
Validates:
1. GeoJSON Reports API (RFC 7946 compliance, [lon, lat] coordinates, properties, filters)
2. Spatial Clustering (aggregates the 8 MG Road corridor reports into single cluster)
3. Hotspots API Endpoint (returns cluster boundaries and summaries)
4. Action Brief Synthesis (identifies both drainage and road repair steps)
5. Action Brief API Endpoint (auth check, HTTP 200 within time limit)
"""

import sys
import json
import time
import socket
import threading
import urllib.request
import urllib.error
from pathlib import Path

# Force UTF-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from apps.api.standalone_server import CitySenseApiHandler, http
from apps.api.services.clustering_service import detect_spatial_clusters
from apps.api.services.action_brief_service import generate_action_brief_from_reports
from apps.api.core.auth import create_access_token, ROLE_DISPATCHER, ROLE_PUBLIC

DB_PATH = str(PROJECT_ROOT / "citysense.db")


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def run_tests():
    print("=" * 70)
    print("STARTING SPATIAL ANALYTICS & HOTSPOT API TESTS (PHASE 6: REVEAL)")
    print("=" * 70)

    port = find_free_port()
    server = http.server.HTTPServer(("127.0.0.1", port), CitySenseApiHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    base_url = f"http://127.0.0.1:{port}"

    def http_get(path, headers=None):
        req = urllib.request.Request(f"{base_url}{path}", headers=headers or {})
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return resp.status, data
        except urllib.error.HTTPError as e:
            data = json.loads(e.read().decode("utf-8"))
            return e.code, data

    def http_post(path, payload, headers=None):
        req_headers = {"Content-Type": "application/json"}
        if headers:
            req_headers.update(headers)
        data_bytes = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(f"{base_url}{path}", data=data_bytes, headers=req_headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return resp.status, data
        except urllib.error.HTTPError as e:
            data = json.loads(e.read().decode("utf-8"))
            return e.code, data

    try:
        time.sleep(0.1)

        # ── TEST 1: TASK-037 GeoJSON Reports Endpoint ────────────────────────
        print("\nTest 1: GET /api/v1/spatial/reports (RFC 7946 GeoJSON compliance)")
        code, geojson = http_get("/api/v1/spatial/reports")
        assert code == 200, f"Expected 200, got {code}"
        assert geojson.get("type") == "FeatureCollection", "Root type must be FeatureCollection"
        features = geojson.get("features", [])
        assert len(features) >= 40, f"Expected >= 40 features, got {len(features)}"

        # Validate coordinate format: strictly [longitude, latitude]
        sample_f = features[0]
        assert sample_f.get("type") == "Feature"
        geom = sample_f.get("geometry", {})
        assert geom.get("type") == "Point"
        coords = geom.get("coordinates")
        assert isinstance(coords, list) and len(coords) == 2, "Coordinates must be [lon, lat]"
        lon, lat = coords[0], coords[1]
        assert -180.0 <= lon <= 180.0 and -90.0 <= lat <= 90.0
        # Ward 12 center is ~12.97, 77.59
        assert 77.0 <= lon <= 78.0, f"Longitude {lon} out of expected Bangalore range"
        assert 12.0 <= lat <= 13.5, f"Latitude {lat} out of expected Bangalore range"

        # Validate feature properties
        props = sample_f.get("properties", {})
        assert "tracking_id" in props
        assert "verified_category" in props
        assert "priority_rank" in props
        assert "lifecycle_status" in props
        print(f"  [PASS] RFC 7946 GeoJSON FeatureCollection verified with {len(features)} reports. First coordinates: [lon={lon}, lat={lat}]")

        # Test query filters
        code, filtered_geojson = http_get("/api/v1/spatial/reports?priority_rank=Priority%201")
        assert code == 200
        p1_features = filtered_geojson.get("features", [])
        assert len(p1_features) >= 1
        assert all(f["properties"]["priority_rank"] == "Priority 1" for f in p1_features)
        print(f"  [PASS] GeoJSON priority_rank filter verified. Retrieved {len(p1_features)} Priority 1 features.")

        # ── TEST 2: TASK-038 Spatial-Thematic Clustering Engine ──────────────
        print("\nTest 2: TASK-038 Spatial Clustering over Seeded MG Road Corridor")
        clusters = detect_spatial_clusters(db_path=DB_PATH)
        assert len(clusters) >= 1, "Must detect at least 1 cluster"

        # Find MG Road corridor cluster
        mg_cluster = None
        for c in clusters:
            if c["cluster_id"] == "cluster-mg-road-corridor" or "mg road" in c["title"].lower():
                mg_cluster = c
                break

        assert mg_cluster is not None, "MG Road corridor cluster must be detected"
        # Check that all 8 seeded MG Road corridor reports are aggregated
        hot_tracking_ids = [t for t in mg_cluster["tracking_ids"] if "CS-HOT" in t]
        assert len(hot_tracking_ids) == 8, f"Expected 8 CS-HOT reports in cluster, got {len(hot_tracking_ids)}: {hot_tracking_ids}"

        # Cross-category breakdown check (must contain both Waterlogging and Road Failure)
        breakdown = mg_cluster["category_breakdown"]
        assert "Waterlogging & Drainage" in breakdown, "Must contain drainage issues"
        assert "Road Failure & Potholes" in breakdown, "Must contain road failure issues"
        assert breakdown["Waterlogging & Drainage"] >= 4
        assert breakdown["Road Failure & Potholes"] >= 3

        # Validate bounding polygon
        poly = mg_cluster["boundary_geojson"]
        assert poly["type"] == "Polygon"
        assert len(poly["coordinates"][0]) >= 4, "Polygon must have at least 4 coordinate vertices"
        print(f"  [PASS] MG Road cluster successfully aggregated {len(hot_tracking_ids)} corridor reports with cross-category breakdown: {breakdown}")

        # ── TEST 3: TASK-039 Spatial Hotspots API Endpoint ───────────────────
        print("\nTest 3: GET /api/v1/spatial/hotspots")
        code, hotspots = http_get("/api/v1/spatial/hotspots")
        assert code == 200, f"Expected 200, got {code}"
        assert isinstance(hotspots, list) and len(hotspots) >= 1
        mg_hotspot = next((h for h in hotspots if h["cluster_id"] == "cluster-mg-road-corridor"), None)
        assert mg_hotspot is not None, "cluster-mg-road-corridor must be in hotspots response"
        assert "center_point" in mg_hotspot
        assert "boundary_geojson" in mg_hotspot
        print(f"  [PASS] Hotspots API returned {len(hotspots)} clusters. MG Road corridor verified (reports count: {mg_hotspot['total_reports']}).")

        # ── TEST 4: TASK-040 Action Brief LLM Synthesis Engine ───────────────
        print("\nTest 4: TASK-040 Action Brief Synthesis Service")
        brief = generate_action_brief_from_reports(
            cluster_id=mg_cluster["cluster_id"],
            cluster_title=mg_cluster["title"],
            reports=mg_cluster["reports"],
            center_point=mg_cluster["center_point"]
        )
        assert brief["cluster_id"] == "cluster-mg-road-corridor"
        assert "MG Road" in brief["cluster_name_location"]
        assert brief["affected_reports_count"] >= 8

        # Acceptance Criterion: Brief must identify both drainage and road repair steps
        rec_action = brief["recommended_action"].lower()
        has_drainage_step = "drain" in rec_action or "silt" in rec_action or "water" in rec_action
        has_road_step = "asphalt" in rec_action or "road" in rec_action or "patch" in rec_action or "pavement" in rec_action
        assert has_drainage_step, f"Action brief must include drainage steps: {brief['recommended_action']}"
        assert has_road_step, f"Action brief must include road repair steps: {brief['recommended_action']}"
        print(f"  [PASS] Action brief successfully generated. Identified dual actions: drainage and road repair.")
        print(f"         Primary Action: {brief['recommended_action'][:100]}...")

        # ── TEST 5: TASK-041 Action Brief API Endpoint ───────────────────────
        print("\nTest 5: POST /api/v1/clusters/{cluster_id}/action-brief (RBAC protected)")

        # 5a. Unauthenticated request should return HTTP 401
        code, err_res = http_post(f"/api/v1/clusters/{mg_cluster['cluster_id']}/action-brief", {})
        assert code == 401, f"Expected 401 for unauthenticated brief generation, got {code}"
        print("  [PASS] Unauthenticated request correctly rejected with HTTP 401.")

        # 5b. Authenticated Dispatcher request should succeed in < 10 seconds
        dispatcher_token = create_access_token(user_id="disp_101", role=ROLE_DISPATCHER)
        auth_header = {"Authorization": f"Bearer {dispatcher_token}"}

        start_time = time.monotonic()
        code, brief_res = http_post(
            f"/api/v1/clusters/{mg_cluster['cluster_id']}/action-brief",
            {},
            headers=auth_header
        )
        elapsed = time.monotonic() - start_time

        assert code == 200, f"Expected 200 with dispatcher token, got {code}: {brief_res}"
        assert elapsed < 10.0, f"Brief generation took {elapsed:.2f}s, expected < 10s"
        assert brief_res["cluster_id"] == "cluster-mg-road-corridor"
        assert "technical_problem" in brief_res
        assert "suggested_department" in brief_res
        print(f"  [PASS] Action Brief API returned HTTP 200 in {elapsed:.3f}s. Department: {brief_res['suggested_department']}.")

        print("\n" + "=" * 70)
        print("ALL PHASE 6 SPATIAL ANALYTICS & HOTSPOT API TESTS PASSED!")
        print("=" * 70)
        return True

    finally:
        server.shutdown()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)


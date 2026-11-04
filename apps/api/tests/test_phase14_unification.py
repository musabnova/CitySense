"""
Phase 14 Task 1: FastAPI Backend Unification Automated Test Suite
================================================================
Comprehensive verification of apps.api.main:app:
- GET /api/health/db
- GET /api/v1/reports (and query filtering)
- POST /api/v1/reports (JSON & Multipart & File upload)
- GET /api/v1/reports/track/{tracking_id}
- GET /api/v1/spatial/reports
- GET /api/v1/spatial/hotspots
- GET /api/v1/field/tasks (RBAC: 401, 403, and 200 with Field Lead JWT)
- POST /api/v1/reports/{id}/assign (RBAC: 401, 403, 200 + dispatch triggers)
- POST /api/v1/reports/{id}/resolve (RBAC: 401, 403, 422, 200 + mock events + 400 duplicate)
- GET /api/v1/mock-integration-logs
"""

import sys
import os
import json
import uuid
from typing import List, Dict, Any
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.core.auth import (
    create_access_token,
    ROLE_FIELD_LEAD,
    ROLE_DISPATCHER,
    ROLE_PUBLIC,
    ROLE_PLATFORM_ADMIN,
)

client = TestClient(app)

# Test Tokens
DRAINAGE_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiJmaWVsZF9kcmFpbmFnZV8wMSIsInJvbGUiOiJGaWVsZCBMZWFkIiwiZGVwYXJ0bWVudCI6IkRyYWluYWdlIENyZXcgQSIsImlhdCI6MTc5MzM1OTAyMCwiZXhwIjoxODI0ODk1MDIwfQ."
    "VTkZjFDwO_lsskaDPpWuExzaneNnAOg20DsKXdHsmnM"
)
ROAD_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiJmaWVsZF9yb2FkXzAxIiwicm9sZSI6IkZpZWxkIExlYWQiLCJkZXBhcnRtZW50IjoiUm9hZCBSZXBhaXIgVGVhbSAyIiwiaWF0IjoxNzkzMzU5MDIwLCJleHAiOjE4MjQ4OTUwMjB9."
    "4MsUP08j5SATxB9PNbMfy6so9ieNBHVEyxpJfrGcGN0"
)
DISPATCHER_TOKEN = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiJkaXNwYXRjaGVyXzAxIiwicm9sZSI6IkRpc3BhdGNoZXIiLCJleHAiOjE3OTU5NDk4Mzh9."
    "ltQl8SO5IHCUPmCtjoo35mnpHB4ch6by4QXiTr296EU"
)
PUBLIC_ROLE_TOKEN = create_access_token("citizen_01", ROLE_PUBLIC)

passed_count = 0
failed_count = 0
failures: List[str] = []


def record_pass(description: str):
    global passed_count
    passed_count += 1
    print(f"  [PASS] {description}")


def record_fail(description: str, error: str):
    global failed_count
    failed_count += 1
    err_msg = error if error else "AssertionError"
    failures.append(f"{description}: {err_msg}")
    print(f"  [FAIL] {description} -> {err_msg}")


# ─────────────────────────────────────────────────────────────────────────────
# Suite 1: Health Probes
# ─────────────────────────────────────────────────────────────────────────────
def suite_1_health_db():
    print("\n--- Suite 1: Database Health Check (GET /api/health/db) ---")
    try:
        res = client.get("/api/health/db")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data.get("status") == "healthy", f"Expected healthy, got: {data}"
        assert "engine" in data
        assert data.get("query_test") == "SELECT 1 returned 1"
        record_pass("Database health probe returns healthy status with SELECT 1 verification")
    except Exception as e:
        record_fail("Database health probe", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Suite 2: Incident Listing & Filtering
# ─────────────────────────────────────────────────────────────────────────────
def suite_2_reports_listing():
    print("\n--- Suite 2: Report Listing & Filtering (GET /api/v1/reports) ---")
    try:
        res = client.get("/api/v1/reports")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert isinstance(data, list)
        assert len(data) > 0
        record_pass(f"Fetched listing of {len(data)} total reports from database")
    except Exception as e:
        record_fail("Reports listing fetch", str(e))

    try:
        res_filter = client.get("/api/v1/reports?priority_rank=Priority 1")
        assert res_filter.status_code == 200
        filtered = res_filter.json()
        for r in filtered:
            assert r["priority_rank"] == "Priority 1"
        record_pass(f"Query filtering by priority_rank=Priority 1 returned {len(filtered)} items correctly")
    except Exception as e:
        record_fail("Priority rank query filter", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Suite 3: JSON Report Submission
# ─────────────────────────────────────────────────────────────────────────────
def suite_3_post_reports_json():
    print("\n--- Suite 3: Citizen Complaint Submission (POST /api/v1/reports via JSON) ---")
    # 3a. Invalid submission (description too short)
    try:
        res_inv = client.post("/api/v1/reports", json={
            "raw_description": "leak",
            "latitude": 12.9716,
            "longitude": 77.5946
        })
        assert res_inv.status_code == 422, f"Expected 422, got {res_inv.status_code}"
        record_pass("Invalid description (<5 chars) rejected with HTTP 422 Unprocessable Content")
    except Exception as e:
        record_fail("Invalid description 422 check", str(e))

    # 3b. Invalid coordinates
    try:
        res_coord = client.post("/api/v1/reports", json={
            "raw_description": "Valid incident description",
            "latitude": 95.0,  # Invalid latitude > 90
            "longitude": 77.5946
        })
        assert res_coord.status_code == 422, f"Expected 422 for lat=95, got {res_coord.status_code}"
        record_pass("Out-of-range coordinates rejected with HTTP 422")
    except Exception as e:
        record_fail("Out-of-range coordinates check", str(e))

    # 3c. Valid submission via JSON
    try:
        valid_payload = {
            "raw_description": "Massive stormwater pipe burst flooding pedestrian subway",
            "latitude": 12.9718,
            "longitude": 77.5948,
            "user_category": "Waterlogging & Drainage",
            "formatted_address": "Subway Crossing, Ward 12",
            "media_url": "https://example.com/subway_flood.jpg"
        }
        res = client.post("/api/v1/reports", json=valid_payload)
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.text}"
        data = res.json()
        assert data.get("id"), "Missing id"
        assert data.get("tracking_id"), "Missing tracking_id"
        assert data.get("lifecycle_status") in ["Submitted", "Under Review"]
        assert data.get("verified_category") in ["Waterlogging & Drainage", "Public Utilities"], f"Unexpected category: {data.get('verified_category')}"
        record_pass(f"Valid JSON submission created ticket: ID={data['id']} | Tracking={data['tracking_id']}")
        return data
    except Exception as e:
        record_fail("Valid JSON submission", str(e))
        return None


# ─────────────────────────────────────────────────────────────────────────────
# Suite 4: Multipart Form & Photo Upload Submission
# ─────────────────────────────────────────────────────────────────────────────
def suite_4_post_reports_multipart():
    print("\n--- Suite 4: Complaint Submission (POST /api/v1/reports via Multipart & Files) ---")
    # 4a. Multipart form fields
    try:
        form_data = {
            "raw_description": "Broken overhead streetlight fixture hanging dangerously",
            "latitude": "12.9732",
            "longitude": "77.5962",
            "user_category": "Electrical & Utilities",
            "formatted_address": "Avenue 4, Ward 12"
        }
        res_form = client.post("/api/v1/reports", data=form_data)
        assert res_form.status_code == 201, f"Expected 201, got {res_form.status_code}: {res_form.text}"
        data = res_form.json()
        assert data.get("tracking_id")
        record_pass(f"Multipart form data submission created tracking ID: {data['tracking_id']}")
    except Exception as e:
        record_fail("Multipart form submission", str(e))

    # 4b. True multipart with binary photo attachment
    try:
        photo_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdbmockjpeg"
        files = {"photo": ("pothole_evidence.jpg", photo_bytes, "image/jpeg")}
        form_fields = {
            "raw_description": "Severe deep pothole causing vehicle axle damage near intersection",
            "latitude": "12.9740",
            "longitude": "77.5970",
            "user_category": "Road Failure & Potholes"
        }
        res_photo = client.post("/api/v1/reports", data=form_fields, files=files)
        assert res_photo.status_code == 201, f"Expected 201, got {res_photo.status_code}: {res_photo.text}"
        data_photo = res_photo.json()
        assert data_photo.get("tracking_id")
        record_pass(f"Multipart photo file upload created tracking ID: {data_photo['tracking_id']}")
    except Exception as e:
        record_fail("Multipart photo file upload", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Suite 5: Status Tracking Lookups
# ─────────────────────────────────────────────────────────────────────────────
def suite_5_track_report():
    print("\n--- Suite 5: Citizen Ticket Tracking (GET /api/v1/reports/track/{tracking_id}) ---")
    try:
        res = client.get("/api/v1/reports/track/CS-HAZD-1001")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        data = res.json()
        assert data["tracking_id"] == "CS-HAZD-1001"
        assert "lifecycle_status" in data
        assert "priority_rank" in data
        record_pass(f"Existing tracking ID lookup succeeded (Status: {data['lifecycle_status']})")
    except Exception as e:
        record_fail("Tracking ID lookup", str(e))

    try:
        res_404 = client.get("/api/v1/reports/track/CS-INVALID-9999")
        assert res_404.status_code == 404, f"Expected 404, got {res_404.status_code}"
        record_pass("Non-existent tracking ID correctly returns HTTP 404 Not Found")
    except Exception as e:
        record_fail("Tracking ID 404 check", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Suite 6: Spatial Reports & Hotspots
# ─────────────────────────────────────────────────────────────────────────────
def suite_6_spatial():
    print("\n--- Suite 6: Spatial Reports & Hotspots GeoJSON Endpoints ---")
    try:
        res_spatial = client.get("/api/v1/spatial/reports")
        assert res_spatial.status_code == 200, f"Expected 200, got {res_spatial.status_code}"
        fc = res_spatial.json()
        assert fc.get("type") == "FeatureCollection"
        assert "features" in fc
        assert len(fc["features"]) > 0
        feat = fc["features"][0]
        assert feat["geometry"]["type"] == "Point"
        coords = feat["geometry"]["coordinates"]
        assert len(coords) == 2  # [lon, lat]
        record_pass(f"GET /api/v1/spatial/reports returns RFC 7946 FeatureCollection ({len(fc['features'])} points)")
    except Exception as e:
        record_fail("Spatial reports GeoJSON", str(e))

    try:
        res_hotspots = client.get("/api/v1/spatial/hotspots")
        assert res_hotspots.status_code == 200, f"Expected 200, got {res_hotspots.status_code}"
        hotspots = res_hotspots.json()
        assert isinstance(hotspots, list)
        assert len(hotspots) > 0
        first_h = hotspots[0]
        assert "cluster_id" in first_h
        assert "title" in first_h
        assert "total_reports" in first_h
        record_pass(f"GET /api/v1/spatial/hotspots returns {len(hotspots)} detected clusters")
    except Exception as e:
        record_fail("Spatial hotspots query", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Suite 7: Field Officer Tasks & RBAC
# ─────────────────────────────────────────────────────────────────────────────
def suite_7_field_tasks_rbac():
    print("\n--- Suite 7: Field Lead Tasks Queue & RBAC Enforcement (GET /api/v1/field/tasks) ---")
    # 7a. Missing token -> 401
    try:
        res_no_tok = client.get("/api/v1/field/tasks")
        assert res_no_tok.status_code == 401, f"Expected 401, got {res_no_tok.status_code}"
        record_pass("Request without Authorization header returns HTTP 401 Unauthorized")
    except Exception as e:
        record_fail("Missing token 401 check", str(e))

    # 7b. Malformed token -> 401
    try:
        res_malformed = client.get("/api/v1/field/tasks", headers={"Authorization": "Bearer not.a.valid.jwt"})
        assert res_malformed.status_code == 401, f"Expected 401, got {res_malformed.status_code}"
        record_pass("Request with malformed JWT returns HTTP 401 Unauthorized")
    except Exception as e:
        record_fail("Malformed token 401 check", str(e))

    # 7c. Forbidden role (Public/Citizen role) -> 403
    try:
        res_forbid = client.get("/api/v1/field/tasks", headers={"Authorization": f"Bearer {PUBLIC_ROLE_TOKEN}"})
        assert res_forbid.status_code == 403, f"Expected 403, got {res_forbid.status_code}"
        record_pass("Request with Citizen/Public role returns HTTP 403 Forbidden")
    except Exception as e:
        record_fail("Forbidden role 403 check", str(e))

    # 7d. Valid Field Lead token (Drainage Crew A) -> 200 with department isolation
    try:
        res_drainage = client.get("/api/v1/field/tasks", headers={"Authorization": f"Bearer {DRAINAGE_TOKEN}"})
        assert res_drainage.status_code == 200, f"Expected 200, got {res_drainage.status_code}: {res_drainage.text}"
        data_d = res_drainage.json()
        assert data_d["department"] == "Drainage Crew A"
        assert "tasks" in data_d
        for t in data_d["tasks"]:
            assert t["assigned_department"] == "Drainage Crew A"
        record_pass(f"Valid Field Lead JWT returns HTTP 200 with {data_d['total']} isolated tasks for Drainage Crew A")
    except Exception as e:
        record_fail("Valid Field Lead tasks fetch", str(e))

    # 7e. Valid Field Lead token (Road Repair Team 2) -> 200
    try:
        res_road = client.get("/api/v1/field/tasks", headers={"Authorization": f"Bearer {ROAD_TOKEN}"})
        assert res_road.status_code == 200
        data_r = res_road.json()
        assert data_r["department"] == "Road Repair Team 2"
        record_pass(f"Road Repair Team 2 JWT returns isolated queue (Department: {data_r['department']})")
    except Exception as e:
        record_fail("Road Repair Team 2 tasks fetch", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Suite 8: Work Order Assignment & Job Resolution Lifecycle
# ─────────────────────────────────────────────────────────────────────────────
def suite_8_assign_and_resolve_lifecycle():
    print("\n--- Suite 8: Assignment & Field Resolution Lifecycle ---")
    # 8a. Create a fresh ticket
    created = client.post("/api/v1/reports", json={
        "raw_description": "Blocked culvert causing roadway submersion during thunderstorm",
        "latitude": 12.9712,
        "longitude": 77.5942,
        "user_category": "Waterlogging & Drainage"
    }).json()
    report_id = created["id"]
    tracking_id = created["tracking_id"]

    # 8b. Assign without token -> 401
    try:
        res_assign_no_auth = client.post(f"/api/v1/reports/{report_id}/assign", json={"department_name": "Drainage Crew A"})
        assert res_assign_no_auth.status_code == 401, f"Expected 401, got {res_assign_no_auth.status_code}"
        record_pass("Work order assignment without token returns HTTP 401 Unauthorized")
    except Exception as e:
        record_fail("Assign without token 401 check", str(e))

    # 8c. Assign with Field Lead token (forbidden: only Dispatcher / Admin can dispatch) -> 403
    try:
        res_assign_forbid = client.post(
            f"/api/v1/reports/{report_id}/assign",
            json={"department_name": "Drainage Crew A"},
            headers={"Authorization": f"Bearer {DRAINAGE_TOKEN}"}
        )
        assert res_assign_forbid.status_code == 403, f"Expected 403, got {res_assign_forbid.status_code}"
        record_pass("Work order assignment by Field Lead correctly rejected with HTTP 403 Forbidden")
    except Exception as e:
        record_fail("Assign by unauthorized role 403 check", str(e))

    # 8d. Valid assignment via Dispatcher token -> 200
    try:
        assign_payload = {
            "department_name": "Drainage Crew A",
            "justification": "Dispatched emergency crew for stormwater clearing"
        }
        res_assign = client.post(
            f"/api/v1/reports/{report_id}/assign",
            json=assign_payload,
            headers={"Authorization": f"Bearer {DISPATCHER_TOKEN}"}
        )
        assert res_assign.status_code == 200, f"Expected 200, got {res_assign.status_code}: {res_assign.text}"
        data_assign = res_assign.json()
        assert data_assign["lifecycle_status"] == "Assigned"
        assert "mock_integrations" in data_assign
        record_pass("Dispatcher assignment succeeded with HTTP 200 and triggered simulated SMS & ERP dispatch sync")
    except Exception as e:
        record_fail("Valid assignment by Dispatcher", str(e))

    # 8e. Resolve without token -> 401
    try:
        res_res_no_auth = client.post(f"/api/v1/reports/{report_id}/resolve", json={"resolution_notes": "Done"})
        assert res_res_no_auth.status_code == 401, f"Expected 401, got {res_res_no_auth.status_code}"
        record_pass("Resolution without token returns HTTP 401 Unauthorized")
    except Exception as e:
        record_fail("Resolution without token 401 check", str(e))

    # 8f. Resolve without notes -> 422
    try:
        res_res_empty = client.post(
            f"/api/v1/reports/{report_id}/resolve",
            json={"resolution_notes": ""},
            headers={"Authorization": f"Bearer {DRAINAGE_TOKEN}"}
        )
        assert res_res_empty.status_code == 422, f"Expected 422, got {res_res_empty.status_code}"
        record_pass("Resolution with empty notes rejected with HTTP 422 Unprocessable Content")
    except Exception as e:
        record_fail("Resolution empty notes 422 check", str(e))

    # 8g. Valid resolution by Field Lead -> 200
    try:
        resolve_payload = {
            "resolution_notes": "Debris extracted from intake chamber. Water drained. Culvert fully restored.",
            "evidence_photo_url": "https://example.com/culvert_cleared.jpg",
            "justification": "Field crew resolved via mobile portal."
        }
        res_resolve = client.post(
            f"/api/v1/reports/{report_id}/resolve",
            json=resolve_payload,
            headers={"Authorization": f"Bearer {DRAINAGE_TOKEN}"}
        )
        assert res_resolve.status_code == 200, f"Expected 200, got {res_resolve.status_code}: {res_resolve.text}"
        data_resolve = res_resolve.json()
        assert data_resolve["lifecycle_status"] == "Resolved"
        assert data_resolve["resolution_notes"] == resolve_payload["resolution_notes"]
        assert "mock_integrations" in data_resolve
        record_pass(f"Field Lead resolution succeeded (State: Resolved, Tracking: {tracking_id})")
    except Exception as e:
        record_fail("Valid Field Lead resolution", str(e))

    # 8h. Duplicate resolution attempt on terminal state -> 400
    try:
        res_dup_resolve = client.post(
            f"/api/v1/reports/{report_id}/resolve",
            json={"resolution_notes": "Attempting secondary resolution"},
            headers={"Authorization": f"Bearer {DRAINAGE_TOKEN}"}
        )
        assert res_dup_resolve.status_code == 400, f"Expected 400, got {res_dup_resolve.status_code}"
        record_pass("Re-resolving an already Resolved ticket correctly rejected with HTTP 400 Bad Request")
    except Exception as e:
        record_fail("Re-resolving terminal ticket 400 check", str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Suite 9: Mock External Integrations
# ─────────────────────────────────────────────────────────────────────────────
def suite_9_mock_integration_logs():
    print("\n--- Suite 9: Mocked External Integration Audit Logs (GET /api/v1/mock-integration-logs) ---")
    try:
        res = client.get("/api/v1/mock-integration-logs")
        assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.text}"
        logs = res.json()
        assert "sms_gateway" in logs, f"Missing 'sms_gateway' in logs"
        assert "erp_adapter" in logs, f"Missing 'erp_adapter' in logs"
        sms_count = logs["sms_gateway"]["total_events"]
        erp_count = logs["erp_adapter"]["total_events"]
        assert sms_count > 0, "No mock SMS events recorded"
        assert erp_count > 0, "No mock ERP events recorded"
        assert "[Demo Data - Mocked SMS Service]" in logs["sms_gateway"]["label"]
        assert "[Simulated ERP Sync]" in logs["erp_adapter"]["label"]
        record_pass(f"Mock integration audit logs verified: {sms_count} SMS events, {erp_count} ERP events")
    except Exception as e:
        record_fail("Mock integration audit logs", str(e))


def run_all_suites():
    print("=" * 75)
    print("CITYSENSE PHASE 14 TASK 1: COMPLETE FASTAPI UNIFICATION VERIFICATION")
    print("=" * 75)

    suite_1_health_db()
    suite_2_reports_listing()
    suite_3_post_reports_json()
    suite_4_post_reports_multipart()
    suite_5_track_report()
    suite_6_spatial()
    suite_7_field_tasks_rbac()
    suite_8_assign_and_resolve_lifecycle()
    suite_9_mock_integration_logs()

    print("\n" + "=" * 75)
    print(f"TEST EXECUTION SUMMARY: {passed_count} PASSED | {failed_count} FAILED")
    print("=" * 75)
    if failed_count > 0:
        print("\nFAILURES:")
        for f in failures:
            print(f" - {f}")
        sys.exit(1)
    else:
        print("\nALL 9 TEST SUITES COMPLETED WITH 100% SUCCESS!")
        sys.exit(0)


if __name__ == "__main__":
    run_all_suites()

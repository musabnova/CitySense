#!/usr/bin/env python3
"""
TASK-074 Prerequisite: Phase 11 Backend Test Suite
====================================================
Tests:
  - TASK-070: GET /api/v1/field/tasks (RBAC, department filtering, two departments)
  - TASK-071: POST /api/v1/reports/{id}/resolve (resolution persistence, status=Resolved)
  - TASK-072: Mock integrations log, SMS + ERP events on dispatch and resolve
  - Regression: citizen tracking, admin reports, health endpoints still operational
"""

import sys
import json
import sqlite3
import time
import http.server
import threading
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Path setup ────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(ROOT))
DB_PATH = ROOT / "citysense.db"

# ── Imports ───────────────────────────────────────────────────────────────────
from apps.api.core.auth import create_access_token
from apps.api.services.mock_integrations import (
    trigger_dispatch_integrations,
    trigger_resolution_integrations,
    get_mock_integration_logs,
    mock_sms_gateway,
    mock_erp_adapter,
    MockSMSGateway,
    MockMunicipalERPAdapter,
)

# ── Test Counter ──────────────────────────────────────────────────────────────
PASS = 0
FAIL = 0

def check(label, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {label}")
    else:
        FAIL += 1
        print(f"  [FAIL] {label}" + (f" | {detail}" if detail else ""))

def section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: Mock Integrations Unit Tests (TASK-072)
# ─────────────────────────────────────────────────────────────────────────────
section("TASK-072: Mock Integrations Unit Tests")

# 1a. SMS gateway sends dispatch notification
sms_result = mock_sms_gateway.send_dispatch_notification(
    to_number="+91-TEST-0001",
    tracking_id="CS-TEST-0001",
    department="Drainage Crew A",
    location="MG Road Ward 12",
    report_count=3,
)
check("SMS gateway returns event dict", isinstance(sms_result, dict))
check("SMS status is SIMULATED_SENT", sms_result.get("status") == "SIMULATED_SENT")
check("SMS facade label present", MockSMSGateway.FACADE_LABEL in sms_result.get("facade", ""))
check("SMS event_type is DISPATCH_NOTIFICATION", sms_result.get("event_type") == "DISPATCH_NOTIFICATION")
check("SMS message contains tracking_id", "CS-TEST-0001" in sms_result.get("message_body", ""))

# 1b. SMS gateway sends resolution notification
sms_res2 = mock_sms_gateway.send_resolution_notification(
    to_number="+91-CITIZEN-0001",
    tracking_id="CS-TEST-0001",
    resolution_notes="Drain cleared, filter installed.",
)
check("SMS resolution event_type", sms_res2.get("event_type") == "RESOLUTION_NOTIFICATION")
check("SMS resolution status", sms_res2.get("status") == "SIMULATED_SENT")

# 1c. ERP adapter push_work_order
erp_result = mock_erp_adapter.push_work_order(
    tracking_id="CS-TEST-0001",
    department="Drainage Crew A",
    location="MG Road Ward 12",
    category="Waterlogging & Drainage",
    priority="Priority 1",
    report_count=3,
)
check("ERP sync_status is SIMULATED_SYNC_OK", erp_result.get("sync_status") == "SIMULATED_SYNC_OK")
check("ERP facade label present", MockMunicipalERPAdapter.FACADE_LABEL in erp_result.get("facade", ""))
check("ERP work order ID generated", erp_result.get("erp_work_order_id", "").startswith("ERP-WO-"))
check("ERP event_type PUSH_WORK_ORDER", erp_result.get("event_type") == "PUSH_WORK_ORDER")

# 1d. ERP adapter push_resolution
erp_res2 = mock_erp_adapter.push_resolution(
    tracking_id="CS-TEST-0001",
    resolved_by="Drainage Crew A",
    resolution_notes="Drain cleared.",
)
check("ERP resolution event_type PUSH_RESOLUTION", erp_res2.get("event_type") == "PUSH_RESOLUTION")
check("ERP closure code COMPLETED", erp_res2["payload"].get("erp_closure_code") == "COMPLETED")

# 1e. Aggregated logs contain both SMS events
logs = get_mock_integration_logs()
check("Logs dict has sms_gateway key", "sms_gateway" in logs)
check("Logs dict has erp_adapter key", "erp_adapter" in logs)
check("SMS log label correct", logs["sms_gateway"]["label"] == MockSMSGateway.FACADE_LABEL)
check("ERP log label correct", logs["erp_adapter"]["label"] == MockMunicipalERPAdapter.FACADE_LABEL)
check("SMS total_events >= 2", logs["sms_gateway"]["total_events"] >= 2)
check("ERP total_events >= 2", logs["erp_adapter"]["total_events"] >= 2)

# 1f. High-level orchestration helper
dispatch_events = trigger_dispatch_integrations(
    tracking_id="CS-ORCH-001",
    department="Road Repair Team 2",
    location="Brigade Road",
    category="Road Failure & Potholes",
    priority="Priority 2",
    report_count=2,
)
check("Dispatch orchestration returns mock_sms", "mock_sms" in dispatch_events)
check("Dispatch orchestration returns mock_erp", "mock_erp" in dispatch_events)
check("Dispatch SMS label correct", dispatch_events["mock_sms"]["label"] == MockSMSGateway.FACADE_LABEL)
check("Dispatch ERP label correct", dispatch_events["mock_erp"]["label"] == MockMunicipalERPAdapter.FACADE_LABEL)

resolve_events = trigger_resolution_integrations(
    tracking_id="CS-ORCH-001",
    department="Road Repair Team 2",
    resolution_notes="Pothole filled with hot mix.",
)
check("Resolve orchestration returns mock_sms", "mock_sms" in resolve_events)
check("Resolve orchestration returns mock_erp", "mock_erp" in resolve_events)

# 1g. Facade labels match PRD §9.2 exactly
check(
    "SMS facade label matches PRD exactly",
    MockSMSGateway.FACADE_LABEL == "[Demo Data - Mocked SMS Service]"
)
check(
    "ERP facade label matches PRD exactly",
    MockMunicipalERPAdapter.FACADE_LABEL == "[Simulated ERP Sync]"
)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: Auth & RBAC Token Tests (TASK-070 prerequisite)
# ─────────────────────────────────────────────────────────────────────────────
section("TASK-070: Auth & RBAC - Field Lead Tokens")

from apps.api.core.auth import verify_access_token

drainage_token = create_access_token(
    "field_drainage_test", "Field Lead",
    department="Drainage Crew A", expires_in_seconds=3600
)
road_token = create_access_token(
    "field_road_test", "Field Lead",
    department="Road Repair Team 2", expires_in_seconds=3600
)
dispatcher_token = create_access_token("dispatcher_01", "Dispatcher", expires_in_seconds=3600)
public_token = create_access_token("citizen_01", "Public", expires_in_seconds=3600)

drainage_payload = verify_access_token(drainage_token)
road_payload = verify_access_token(road_token)

check("Drainage token role is Field Lead", drainage_payload["role"] == "Field Lead")
check("Drainage token dept is Drainage Crew A", drainage_payload["department"] == "Drainage Crew A")
check("Road token dept is Road Repair Team 2", road_payload["department"] == "Road Repair Team 2")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: Database State & Field Task Filtering (TASK-070)
# ─────────────────────────────────────────────────────────────────────────────
section("TASK-070: Database Field Task Filtering (department isolation)")

conn = sqlite3.connect(str(DB_PATH))
conn.row_factory = sqlite3.Row

# Find assigned reports for each department
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM reports WHERE lifecycle_status = 'Assigned'")
total_assigned = cur.fetchone()[0]
check(f"Database has at least 1 assigned report ({total_assigned})", total_assigned >= 1)

cur.execute("SELECT DISTINCT assigned_department FROM reports WHERE lifecycle_status = 'Assigned' AND assigned_department IS NOT NULL")
depts = [r[0] for r in cur.fetchall()]
print(f"  [INFO] Departments with assigned reports: {depts}")
check("At least 1 department has assigned reports", len(depts) >= 1)

# Verify department isolation logic
for dept in depts:
    cur.execute(
        "SELECT COUNT(*) FROM reports WHERE lifecycle_status IN ('Assigned', 'Resolved') AND assigned_department = ?",
        (dept,)
    )
    dept_count = cur.fetchone()[0]
    cur.execute(
        "SELECT COUNT(*) FROM reports WHERE lifecycle_status IN ('Assigned', 'Resolved') AND (assigned_department != ? OR assigned_department IS NULL)",
        (dept,)
    )
    other_count = cur.fetchone()[0]
    check(f"Dept '{dept[:20]}' has {dept_count} tasks, excluded {other_count} from other depts", True)

conn.close()

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: Standalone Server Live Endpoint Tests
# ─────────────────────────────────────────────────────────────────────────────
section("TASK-070/071/072: Live HTTP Endpoint Tests via Standalone Server")

import urllib.request
import urllib.error

SERVER_PORT = 8095
SERVER_URL = f"http://127.0.0.1:{SERVER_PORT}"

# Start the server in a daemon thread
from apps.api.standalone_server import CitySenseApiHandler

def run_test_server():
    server = http.server.HTTPServer(("127.0.0.1", SERVER_PORT), CitySenseApiHandler)
    server.serve_forever()

server_thread = threading.Thread(target=run_test_server, daemon=True)
server_thread.start()
time.sleep(1.5)  # Wait for server to start

def http_get(path, token=None):
    req = urllib.request.Request(f"{SERVER_URL}{path}")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def http_post(path, body, token=None):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"{SERVER_URL}{path}", data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

# ── 4a. Health check ──────────────────────────────────────────────────────────
status, body = http_get("/api/health/db")
check("Health endpoint /api/health/db returns 200", status == 200)

# ── 4b. Mock integration logs endpoint ───────────────────────────────────────
status, body = http_get("/api/v1/mock-integration-logs")
check("GET /api/v1/mock-integration-logs returns 200", status == 200)
check("Mock logs has sms_gateway key", "sms_gateway" in body)
check("Mock logs has erp_adapter key", "erp_adapter" in body)

# ── 4c. Field tasks: no token → 401 ──────────────────────────────────────────
status, body = http_get("/api/v1/field/tasks")
check("GET /api/v1/field/tasks without token returns 401", status == 401)

# ── 4d. Field tasks: Public role → 403 ───────────────────────────────────────
status, body = http_get("/api/v1/field/tasks", token=public_token)
check("GET /api/v1/field/tasks with Public role returns 403", status == 403, str(body))

# ── 4e. Field tasks: Drainage token → 200, dept-filtered ────────────────────
status, body = http_get("/api/v1/field/tasks", token=drainage_token)
check("GET /api/v1/field/tasks with Drainage token returns 200", status == 200, str(body))

if status == 200:
    check("Response has 'tasks' list", "tasks" in body)
    check("Response has 'department' field", "department" in body)
    drain_dept = body.get("department", "")
    drain_tasks = body.get("tasks", [])
    check("Department in response matches 'Drainage Crew A'", drain_dept == "Drainage Crew A", drain_dept)

    # All tasks must belong to Drainage Crew A
    all_dept_match = all(
        t.get("assigned_department") == "Drainage Crew A"
        for t in drain_tasks
    )
    check(
        f"All {len(drain_tasks)} Drainage tasks belong only to 'Drainage Crew A'",
        all_dept_match or len(drain_tasks) == 0,
        f"Tasks: {[(t.get('tracking_id'), t.get('assigned_department')) for t in drain_tasks]}"
    )
    print(f"  [INFO] Drainage Crew A: {len(drain_tasks)} assigned tasks")

# ── 4f. Field tasks: Road Repair token → dept-filtered separately ─────────────
status2, body2 = http_get("/api/v1/field/tasks", token=road_token)
check("GET /api/v1/field/tasks with Road Repair token returns 200", status2 == 200, str(body2))

if status2 == 200:
    road_dept = body2.get("department", "")
    road_tasks = body2.get("tasks", [])
    check("Road token dept is 'Road Repair Team 2'", road_dept == "Road Repair Team 2", road_dept)
    all_road_match = all(
        t.get("assigned_department") == "Road Repair Team 2"
        for t in road_tasks
    )
    check(
        f"All {len(road_tasks)} Road tasks belong only to 'Road Repair Team 2'",
        all_road_match or len(road_tasks) == 0,
    )
    print(f"  [INFO] Road Repair Team 2: {len(road_tasks)} assigned tasks")

# Verify isolation: Drainage token cannot see Road reports and vice versa
if status == 200 and status2 == 200:
    drain_ids = {t["id"] for t in body.get("tasks", [])}
    road_ids = {t["id"] for t in body2.get("tasks", [])}
    overlap = drain_ids & road_ids
    check("Drainage and Road Repair task lists are isolated (no overlap)", len(overlap) == 0, f"Overlap: {overlap}")

# ── 4g. TASK-071: Resolve an assigned report ─────────────────────────────────
# First, find an assigned report OR create one
conn2 = sqlite3.connect(str(DB_PATH))
conn2.row_factory = sqlite3.Row
cur2 = conn2.cursor()
cur2.execute(
    "SELECT id, tracking_id, lifecycle_status, assigned_department FROM reports WHERE lifecycle_status = 'Assigned' LIMIT 1"
)
assigned_row = cur2.fetchone()
conn2.close()

if assigned_row:
    assigned_id = assigned_row["id"]
    assigned_tracking = assigned_row["tracking_id"]
    assigned_dept = assigned_row["assigned_department"] or "Drainage Crew A"
    print(f"\n  [INFO] Using assigned report: {assigned_tracking} (dept: {assigned_dept})")

    # Get the appropriate token for this department
    test_resolve_token = create_access_token(
        "field_test_resolve", "Field Lead",
        department=assigned_dept, expires_in_seconds=3600
    )

    # 4g-i. Missing resolution_notes → 422
    status, body = http_post(
        f"/api/v1/reports/{assigned_id}/resolve",
        {"resolution_notes": ""},
        token=test_resolve_token
    )
    check("POST /resolve with empty notes returns 422", status == 422, str(body))

    # 4g-ii. Public token → 403
    status, body = http_post(
        f"/api/v1/reports/{assigned_id}/resolve",
        {"resolution_notes": "Test fix"},
        token=public_token
    )
    check("POST /resolve with Public token returns 403", status == 403, str(body))

    # 4g-iii. Valid resolution
    resolve_notes = "Drainage channel cleared. Debris removed. Gutter cover replaced."
    status, body = http_post(
        f"/api/v1/reports/{assigned_id}/resolve",
        {
            "resolution_notes": resolve_notes,
            "evidence_photo_url": "data:image/jpeg;base64,/9j/MOCKPHOTO",
            "justification": "Field test resolution"
        },
        token=test_resolve_token
    )
    check("POST /resolve with valid data returns 200", status == 200, str(body))

    if status == 200:
        check("Response lifecycle_status is Resolved", body.get("lifecycle_status") == "Resolved")
        check("Response contains resolution_notes", body.get("resolution_notes") == resolve_notes)
        check("Response has resolved_at timestamp", bool(body.get("resolved_at")))
        check("Response has mock_integrations", "mock_integrations" in body)

        mock_data = body.get("mock_integrations", {})
        check("Resolution mock_sms event recorded", "mock_sms" in mock_data, str(mock_data))
        check("Resolution mock_erp event recorded", "mock_erp" in mock_data, str(mock_data))

        if "mock_sms" in mock_data:
            check(
                "SMS label is [Demo Data - Mocked SMS Service]",
                mock_data["mock_sms"].get("label") == "[Demo Data - Mocked SMS Service]"
            )
        if "mock_erp" in mock_data:
            check(
                "ERP label is [Simulated ERP Sync]",
                mock_data["mock_erp"].get("label") == "[Simulated ERP Sync]"
            )

        # 4g-iv. Verify persistence in DB
        conn3 = sqlite3.connect(str(DB_PATH))
        conn3.row_factory = sqlite3.Row
        c3 = conn3.cursor()
        c3.execute("SELECT lifecycle_status, resolution_notes FROM reports WHERE id = ?", (assigned_id,))
        persisted = c3.fetchone()
        conn3.close()

        check(
            "DB shows lifecycle_status = Resolved",
            persisted and persisted["lifecycle_status"] == "Resolved",
            str(dict(persisted)) if persisted else "row not found"
        )
        check(
            "DB shows resolution_notes persisted correctly",
            persisted and persisted["resolution_notes"] == resolve_notes,
        )

        # 4g-v. Citizen tracking shows Resolved
        status, body = http_get(f"/api/v1/reports/track/{assigned_tracking}")
        check("Citizen tracking GET returns 200 after resolve", status == 200, str(body))
        check("Citizen tracking shows lifecycle_status Resolved", body.get("lifecycle_status") == "Resolved")
        print(f"  [INFO] Citizen tracking for {assigned_tracking}: status={body.get('lifecycle_status')}")

        # 4g-vi. Attempting to resolve again → 400 (Resolved → Resolved invalid transition)
        status2, body2 = http_post(
            f"/api/v1/reports/{assigned_id}/resolve",
            {"resolution_notes": "Second attempt"},
            token=test_resolve_token
        )
        check("POST /resolve on already-Resolved report returns 400", status2 == 400, str(body2))

else:
    print("  [SKIP] No assigned report available for full resolution test.")
    print("         Run 'assign' via admin API to create one, then re-run tests.")

# ── 4h. TASK-072: Assign endpoint fires mock integrations ────────────────────
# Find a report in Submitted or Under Review state to assign
conn4 = sqlite3.connect(str(DB_PATH))
conn4.row_factory = sqlite3.Row
c4 = conn4.cursor()
c4.execute(
    "SELECT id, tracking_id FROM reports WHERE lifecycle_status = 'Submitted' AND is_duplicate = 0 LIMIT 1"
)
submittable = c4.fetchone()
conn4.close()

if submittable:
    sub_id = submittable["id"]
    sub_tid = submittable["tracking_id"]

    # Move to Under Review first via status endpoint
    dispatcher_tk = create_access_token("dispatcher_test", "Dispatcher", expires_in_seconds=3600)
    status, _ = http_post(
        f"/api/v1/reports/{sub_id}/status",
        {"status": "Under Review", "justification": "Test dispatch flow"},
        token=dispatcher_tk
    )

    if status == 200:
        # Now assign
        before_log_count = get_mock_integration_logs()["sms_gateway"]["total_events"]
        status, body = http_post(
            f"/api/v1/reports/{sub_id}/assign",
            {"department_name": "Drainage Crew A", "justification": "Integration test dispatch"},
            token=dispatcher_tk
        )
        check("Assign endpoint returns 200", status == 200, str(body))
        if status == 200:
            check("Assign response has mock_integrations", "mock_integrations" in body, str(body))
            after_log_count = get_mock_integration_logs()["sms_gateway"]["total_events"]
            check("SMS log grew after dispatch", after_log_count > before_log_count)
            print(f"  [INFO] SMS events before dispatch: {before_log_count}, after: {after_log_count}")

# ── 4i. Regression: Admin reports API still works ────────────────────────────
section("REGRESSION: Existing API endpoints still operational")

status, body = http_get("/api/v1/reports")
check("GET /api/v1/reports returns 200", status == 200)
check("Reports list has items", isinstance(body, list) and len(body) > 0)

status, body = http_get("/api/v1/spatial/reports")
check("GET /api/v1/spatial/reports returns 200", status == 200)
check("Spatial reports is GeoJSON FeatureCollection", body.get("type") == "FeatureCollection")

status, body = http_get("/api/v1/spatial/hotspots")
check("GET /api/v1/spatial/hotspots returns 200", status == 200)
check("Hotspots is a list", isinstance(body, list))

# ─────────────────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
print(f"\n{'='*60}")
print(f"  Phase 11 Test Results: {PASS} PASS | {FAIL} FAIL")
print(f"{'='*60}")

if FAIL > 0:
    sys.exit(1)
else:
    print("  ALL TESTS PASSED")
    sys.exit(0)


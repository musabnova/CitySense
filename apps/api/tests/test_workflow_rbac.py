"""
TASK-048: Workflow State Transition & Security Integration Test Suite
======================================================================
Stage: Stage 4: Act / Testing
Validates:
1. Strict state machine transitions (Submitted -> Under Review -> Assigned -> Resolved)
   and rejection of illegal state transitions (HTTP 400).
2. Departmental work order assignment with atomic child duplicate synchronization (TASK-044).
3. Administrative priority override and audit logging (TASK-045).
4. Immutable audit history trail retrieval (TASK-046).
5. Role-based access control: HTTP 401 unauthenticated, HTTP 403 unauthorized role,
   HTTP 200 authorized dispatcher/admin (TASK-047).
"""

import sys
import json
import time
import socket
import threading
import sqlite3
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
from apps.api.core.auth import (
    create_access_token,
    ROLE_PUBLIC,
    ROLE_DISPATCHER,
    ROLE_FIELD_LEAD,
    ROLE_PLATFORM_ADMIN
)

DB_PATH = str(PROJECT_ROOT / "citysense.db")


def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def run_tests():
    print("=" * 70)
    print("STARTING WORKFLOW, OVERRIDE & RBAC SECURITY TESTS (PHASE 7: ACT)")
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

        # Generate tokens
        dispatcher_token = create_access_token(user_id="disp_101", role=ROLE_DISPATCHER)
        admin_token = create_access_token(user_id="admin_001", role=ROLE_PLATFORM_ADMIN)
        public_token = create_access_token(user_id="citizen_999", role=ROLE_PUBLIC)

        disp_headers = {"Authorization": f"Bearer {dispatcher_token}"}
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        public_headers = {"Authorization": f"Bearer {public_token}"}

        # ── Setup a fresh test report in Submitted state ─────────────────────
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, tracking_id FROM reports WHERE tracking_id = 'CS-HAZD-1001'")
        hazard1 = dict(cur.fetchone())
        cur.execute("UPDATE reports SET lifecycle_status = 'Submitted', priority_rank = 'Priority 1' WHERE id = ?", (hazard1["id"],))
        conn.commit()
        conn.close()

        # ── TEST 1: TASK-043 Lifecycle State Machine Progression & Rejection ─
        print("\nTest 1: TASK-043 Strict State Machine Controller")

        # 1a. Attempt illegal transition: Submitted -> Resolved directly (must fail with HTTP 400)
        code, err_res = http_post(
            f"/api/v1/reports/{hazard1['id']}/status",
            {"status": "Resolved", "justification": "Trying illegal skip"},
            headers=disp_headers
        )
        assert code == 400, f"Expected 400 for illegal transition Submitted -> Resolved, got {code}: {err_res}"
        print(f"  [PASS] Illegal transition Submitted -> Resolved correctly rejected with HTTP 400: '{err_res['detail']}'.")

        # 1b. Valid transition: Submitted -> Under Review
        code, trans1 = http_post(
            f"/api/v1/reports/{hazard1['id']}/status",
            {"status": "Under Review", "justification": "AI triage review"},
            headers=disp_headers
        )
        assert code == 200, f"Expected 200, got {code}"
        assert trans1["lifecycle_status"] == "Under Review"

        # 1c. Valid transition: Under Review -> Assigned
        code, trans2 = http_post(
            f"/api/v1/reports/{hazard1['id']}/status",
            {"status": "Assigned", "justification": "Assigned to crew"},
            headers=disp_headers
        )
        assert code == 200
        assert trans2["lifecycle_status"] == "Assigned"

        # 1d. Valid transition: Assigned -> Resolved
        code, trans3 = http_post(
            f"/api/v1/reports/{hazard1['id']}/status",
            {"status": "Resolved", "justification": "Field crew completed hazard isolation"},
            headers=disp_headers
        )
        assert code == 200
        assert trans3["lifecycle_status"] == "Resolved"
        print("  [PASS] Sequential lifecycle progression Submitted -> Under Review -> Assigned -> Resolved verified.")

        # ── TEST 2: TASK-044 Work Order Assignment & Child Ticket Sync ────────
        print("\nTest 2: TASK-044 Departmental Assignment & Child Ticket Synchronization")

        # Find a master report with child duplicates (e.g. CS-DUPL-2001 which has 2 child reports)
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT id, tracking_id FROM reports WHERE tracking_id = 'CS-DUPL-2001'")
        master = dict(cur.fetchone())
        cur.execute("SELECT id, tracking_id FROM reports WHERE master_ticket_id = ?", (master["id"],))
        children = [dict(r) for r in cur.fetchall()]
        conn.close()

        print(f"  Master ticket: {master['tracking_id']} (id={master['id']}) with {len(children)} child duplicates.")

        # Assign master ticket to "Public Works - Stormwater Drainage Division"
        code, assign_res = http_post(
            f"/api/v1/reports/{master['id']}/assign",
            {"department_name": "Public Works - Stormwater Drainage Division", "justification": "Urgent drainage dispatch"},
            headers=disp_headers
        )
        assert code == 200, f"Expected 200, got {code}: {assign_res}"
        assert assign_res["lifecycle_status"] == "Assigned"
        assert assign_res["assigned_department"] == "Public Works - Stormwater Drainage Division"
        assert assign_res["synchronized_children_count"] >= 1

        # Verify in DB: master AND all children must have status = Assigned and assigned_department set
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT lifecycle_status, assigned_department, dispatch_timestamp FROM reports WHERE id = ?", (master["id"],))
        m_row = dict(cur.fetchone())
        assert m_row["lifecycle_status"] == "Assigned"
        assert m_row["assigned_department"] == "Public Works - Stormwater Drainage Division"
        assert m_row["dispatch_timestamp"] is not None

        for child in children:
            cur.execute("SELECT lifecycle_status, assigned_department, dispatch_timestamp FROM reports WHERE id = ?", (child["id"],))
            c_row = dict(cur.fetchone())
            assert c_row["lifecycle_status"] == "Assigned", f"Child {child['tracking_id']} was not synchronized to Assigned!"
            assert c_row["assigned_department"] == "Public Works - Stormwater Drainage Division"
            assert c_row["dispatch_timestamp"] is not None
        conn.close()

        total_synced = 1 + len(children)
        print(f"  [PASS] Atomic assignment verified: master + {len(children)} children ({total_synced} total rows) synchronized simultaneously to 'Assigned'.")

        # ── TEST 3: TASK-045 Administrative Priority Override ────────────────
        print("\nTest 3: TASK-045 Administrative Priority Override")

        # Reset hazard 1 priority to Priority 1
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("UPDATE reports SET priority_rank = 'Priority 1', is_manually_overridden = 0 WHERE id = ?", (hazard1["id"],))
        conn.commit()
        conn.close()

        # Override priority from Priority 1 to Priority 3 with officer justification
        code, override_res = http_post(
            f"/api/v1/reports/{hazard1['id']}/override",
            {
                "action": "SET_PRIORITY",
                "new_priority": "Priority 3",
                "justification": "Site inspection showed power was disconnected; immediate hazard neutralized."
            },
            headers=disp_headers
        )
        assert code == 200, f"Expected 200, got {code}: {override_res}"
        assert override_res["action"] == "SET_PRIORITY"
        assert override_res["previous_priority"] == "Priority 1"
        assert override_res["priority_rank"] == "Priority 3"
        assert override_res["is_manually_overridden"] is True

        # Verify persistence in DB
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT priority_rank, is_manually_overridden, override_reason FROM reports WHERE id = ?", (hazard1["id"],))
        row = dict(cur.fetchone())
        assert row["priority_rank"] == "Priority 3"
        assert row["is_manually_overridden"] == 1
        assert "power was disconnected" in row["override_reason"]
        conn.close()
        print("  [PASS] Administrative priority override Priority 1 -> Priority 3 verified in DB with officer justification.")

        # ── TEST 4: TASK-046 Audit Trail Retrieval ───────────────────────────
        print("\nTest 4: TASK-046 Audit Trail Inspection Service")
        code, trail = http_get(f"/api/v1/reports/{hazard1['id']}/audit-trail")
        assert code == 200, f"Expected 200, got {code}"
        assert isinstance(trail, list) and len(trail) >= 1

        override_audit = next((a for a in trail if a["action_type"] == "SET_PRIORITY"), None)
        assert override_audit is not None, "Audit log must contain SET_PRIORITY entry"
        assert override_audit["previous_value"] == "Priority 1"
        assert override_audit["new_value"] == "Priority 3"
        assert "power was disconnected" in override_audit["justification"]
        assert override_audit["timestamp"] is not None
        print(f"  [PASS] Audit trail verified: found {len(trail)} chronological records. SET_PRIORITY record verified.")

        # ── TEST 5: TASK-047 Role-Based Access Control (RBAC) ────────────────
        print("\nTest 5: TASK-047 Role-Based Access Control (RBAC) Enforcement")

        # 5a. Unauthenticated request to dispatch endpoint -> HTTP 401
        code, res_401 = http_post(
            f"/api/v1/reports/{hazard1['id']}/override",
            {"action": "SET_PRIORITY", "new_priority": "Priority 2", "justification": "No auth test"}
        )
        assert code == 401, f"Expected 401 for unauthenticated request, got {code}"
        print("  [PASS] Unauthenticated request to override endpoint correctly rejected with HTTP 401.")

        # 5b. Unauthorized role (Public citizen trying to dispatch / override) -> HTTP 403
        code, res_403 = http_post(
            f"/api/v1/reports/{hazard1['id']}/override",
            {"action": "SET_PRIORITY", "new_priority": "Priority 2", "justification": "Public user unauthorized test"},
            headers=public_headers
        )
        assert code == 403, f"Expected 403 for Public role on dispatcher endpoint, got {code}"
        print("  [PASS] Unauthorized role (Public) correctly rejected with HTTP 403 Forbidden.")

        # 5c. Authorized role (Dispatcher) -> HTTP 200
        code, res_200 = http_post(
            f"/api/v1/reports/{hazard1['id']}/override",
            {"action": "SET_PRIORITY", "new_priority": "Priority 2", "justification": "Dispatcher authorized override"},
            headers=disp_headers
        )
        assert code == 200, f"Expected 200 for Dispatcher role, got {code}"
        print("  [PASS] Authorized role (Dispatcher) succeeded with HTTP 200.")

        print("\n" + "=" * 70)
        print("ALL PHASE 7 WORKFLOW, OVERRIDE & RBAC TESTS PASSED SUCCESSFULLY!")
        print("=" * 70)
        return True

    finally:
        server.shutdown()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)


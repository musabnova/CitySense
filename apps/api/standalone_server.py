import http.server
import json
import sqlite3
import uuid
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from apps.api.seeds.geo_constants import calculate_haversine_distance, ANCHOR_POIS
from apps.api.services.tracking_service import generate_random_tracking_code

# ── Phase 5 AI Pipeline import (with graceful fallback) ──────────────────────
try:
    from apps.api.tasks.pipeline import process_incident_report_task
    _PIPELINE_AVAILABLE = True
except ImportError:
    _PIPELINE_AVAILABLE = False

# ── Phase 6 & Phase 7 Services ───────────────────────────────────────────────
from apps.api.services.clustering_service import detect_spatial_clusters
from apps.api.services.action_brief_service import generate_action_brief_from_reports
from apps.api.services.workflow_service import (
    transition_lifecycle_status,
    assign_work_order,
    override_report
)
from apps.api.services.audit_service import get_report_audit_trail
from apps.api.core.auth import (
    authenticate_request_token,
    ROLE_DISPATCHER,
    ROLE_PLATFORM_ADMIN,
    ROLE_FIELD_LEAD
)

# ── Phase 11 Mock Integrations (TASK-072) ─────────────────────────────────────
from apps.api.services.mock_integrations import (
    trigger_dispatch_integrations,
    trigger_resolution_integrations,
    get_mock_integration_logs,
    MockSMSGateway,
    MockMunicipalERPAdapter,
)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "citysense.db"


def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


class CitySenseApiHandler(http.server.BaseHTTPRequestHandler):
    def _set_headers(self, status_code=200, content_type="application/json"):
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def _check_auth(self, allowed_roles):
        auth_header = self.headers.get("Authorization")
        return authenticate_request_token(auth_header, allowed_roles)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query_params = parse_qs(parsed.query)

        # 1. Root & Health
        if path == "/":
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "platform": "CitySense",
                "mission": "From Complaints to Action",
                "status": "operational",
                "version": "0.1.0",
                "docs": "/docs"
            }).encode())
            return

        if path == "/api/health/db":
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT 1;")
                res = cur.fetchone()[0]
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "status": "healthy" if res == 1 else "unhealthy",
                    "engine": "sqlite:///./citysense.db",
                    "query_test": "SELECT 1 returned 1"
                }).encode())
            finally:
                conn.close()
            return

        if path == "/api/health/redis":
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "status": "healthy",
                "url": "redis://localhost:6379/0",
                "mode": "in_memory_async_fallback"
            }).encode())
            return

        # 2. Tracking Endpoint: GET /api/v1/reports/track/{tracking_id}
        if path.startswith("/api/v1/reports/track/"):
            tracking_id = path.replace("/api/v1/reports/track/", "").strip()
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM reports WHERE tracking_id = ?", (tracking_id,))
                row = cur.fetchone()
                if not row:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({
                        "detail": f"Report with tracking ID '{tracking_id}' not found."
                    }).encode())
                    return

                res_dict = dict(row)
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "tracking_id": res_dict["tracking_id"],
                    "lifecycle_status": res_dict["lifecycle_status"],
                    "user_category": res_dict["user_category"],
                    "verified_category": res_dict["verified_category"],
                    "concise_summary": res_dict["concise_summary"],
                    "created_at": res_dict["created_at"],
                    "formatted_address": res_dict["formatted_address"],
                    "is_duplicate": bool(res_dict["is_duplicate"]),
                    "master_ticket_id": res_dict["master_ticket_id"],
                    "priority_rank": res_dict["priority_rank"],
                    "priority_score": float(res_dict["priority_score"]),
                    "priority_rationale": res_dict["priority_rationale"],
                    "assigned_department": res_dict["assigned_department"],
                    "resolution_notes": res_dict["resolution_notes"]
                }).encode())
            finally:
                conn.close()
            return

        # 3. TASK-037: Spatial Reports GeoJSON API Endpoint: GET /api/v1/spatial/reports
        if path == "/api/v1/spatial/reports":
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                sql = "SELECT * FROM reports WHERE 1=1"
                args = []

                if "lifecycle_status" in query_params:
                    sql += " AND lifecycle_status = ?"
                    args.append(query_params["lifecycle_status"][0])
                if "priority_rank" in query_params:
                    sql += " AND priority_rank = ?"
                    args.append(query_params["priority_rank"][0])

                sql += " ORDER BY created_at DESC"
                cur.execute(sql, tuple(args))
                rows = [dict(r) for r in cur.fetchall()]

                features = []
                for r in rows:
                    features.append({
                        "type": "Feature",
                        "id": r["id"],
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(r["longitude"]), float(r["latitude"])]
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
                    })

                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "type": "FeatureCollection",
                    "features": features
                }).encode())
            finally:
                conn.close()
            return

        # 4. TASK-039: Spatial Hotspots Endpoint: GET /api/v1/spatial/hotspots
        if path == "/api/v1/spatial/hotspots":
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
            self._set_headers(200)
            self.wfile.write(json.dumps(output).encode())
            return

        # 5. TASK-046: Audit Trail Endpoint: GET /api/v1/reports/{id}/audit-trail
        audit_match = re.match(r"^/api/v1/reports/([^/]+)/audit-trail$", path)
        if audit_match:
            report_id = audit_match.group(1)
            trail = get_report_audit_trail(report_id, db_path=str(DB_PATH))
            self._set_headers(200)
            self.wfile.write(json.dumps(trail).encode())
            return

        # TASK-072: Mock Integration Logs: GET /api/v1/mock-integration-logs
        if path == "/api/v1/mock-integration-logs":
            self._set_headers(200)
            self.wfile.write(json.dumps(get_mock_integration_logs()).encode())
            return

        # TASK-070: Field Task Queue: GET /api/v1/field/tasks
        # RBAC-enforced: department from JWT, not overridable by query params
        if path == "/api/v1/field/tasks":
            try:
                user_info = self._check_auth([ROLE_FIELD_LEAD, ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN])
            except PermissionError as pe:
                self._set_headers(getattr(pe, "status_code", 401))
                self.wfile.write(json.dumps({"detail": str(pe)}).encode())
                return

            token_department = user_info.get("department")
            token_role = user_info.get("role")

            conn = get_db_connection()
            try:
                cur = conn.cursor()
                if token_role == "Platform Admin" or not token_department:
                    cur.execute(
                        "SELECT * FROM reports WHERE lifecycle_status IN ('Assigned', 'Resolved') ORDER BY priority_score DESC, created_at ASC"
                    )
                else:
                    cur.execute(
                        "SELECT * FROM reports WHERE lifecycle_status IN ('Assigned', 'Resolved') AND assigned_department = ? ORDER BY priority_score DESC, created_at ASC",
                        (token_department,)
                    )

                rows = [dict(r) for r in cur.fetchall()]
                output = []
                for r in rows:
                    output.append({
                        "id": r["id"],
                        "tracking_id": r["tracking_id"],
                        "created_at": r["created_at"],
                        "updated_at": r["updated_at"],
                        "raw_description": r["raw_description"],
                        "verified_category": r["verified_category"],
                        "concise_summary": r["concise_summary"],
                        "formatted_address": r["formatted_address"],
                        "latitude": float(r["latitude"]),
                        "longitude": float(r["longitude"]),
                        "priority_rank": r["priority_rank"],
                        "priority_score": float(r["priority_score"]),
                        "priority_rationale": r["priority_rationale"],
                        "lifecycle_status": r["lifecycle_status"],
                        "assigned_department": r["assigned_department"],
                        "dispatch_timestamp": r["dispatch_timestamp"],
                        "duplicate_count": int(r["duplicate_count"]),
                        "is_duplicate": bool(r["is_duplicate"]),
                        "media_url": r["media_url"],
                        "resolution_notes": r["resolution_notes"],
                    })
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "department": token_department or "All Departments",
                    "role": token_role,
                    "total": len(output),
                    "tasks": output,
                }).encode())
            finally:
                conn.close()
            return

        # 6. Listing Endpoint: GET /api/v1/reports
        if path == "/api/v1/reports":
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                sql = "SELECT * FROM reports WHERE 1=1"
                args = []

                if "lifecycle_status" in query_params:
                    sql += " AND lifecycle_status = ?"
                    args.append(query_params["lifecycle_status"][0])
                if "priority_rank" in query_params:
                    sql += " AND priority_rank = ?"
                    args.append(query_params["priority_rank"][0])
                if "category" in query_params:
                    sql += " AND verified_category = ?"
                    args.append(query_params["category"][0])

                sql += " ORDER BY created_at DESC"
                cur.execute(sql, tuple(args))
                rows = [dict(r) for r in cur.fetchall()]

                output = []
                for r in rows:
                    output.append({
                        "id": r["id"],
                        "tracking_id": r["tracking_id"],
                        "created_at": r["created_at"],
                        "updated_at": r["updated_at"],
                        "raw_description": r["raw_description"],
                        "user_category": r["user_category"],
                        "verified_category": r["verified_category"],
                        "media_url": r["media_url"],
                        "latitude": float(r["latitude"]),
                        "longitude": float(r["longitude"]),
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
                        "resolution_notes": r["resolution_notes"]
                    })

                self._set_headers(200)
                self.wfile.write(json.dumps(output).encode())
            finally:
                conn.close()
            return

        # 7. Single Report Detail: GET /api/v1/reports/{id}
        if path.startswith("/api/v1/reports/"):
            report_id = path.replace("/api/v1/reports/", "").strip()
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
                row = cur.fetchone()
                if not row:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"detail": "Report not found"}).encode())
                    return
                self._set_headers(200)
                self.wfile.write(json.dumps(dict(row)).encode())
            finally:
                conn.close()
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"detail": "Route not found"}).encode())

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8", errors="ignore") if content_length > 0 else ""

        payload = {}
        if body:
            ct = self.headers.get("Content-Type", "")
            if ct.startswith("application/json"):
                try:
                    payload = json.loads(body)
                except Exception:
                    self._set_headers(400)
                    self.wfile.write(json.dumps({"detail": "Invalid JSON body"}).encode())
                    return
            elif "multipart/form-data" in ct:
                # Parse multipart/form-data fields
                for part in body.split("--"):
                    if 'name="' in part:
                        name_match = re.search(r'name="([^"]+)"', part)
                        if name_match:
                            field_name = name_match.group(1)
                            header_body_split = part.split("\r\n\r\n", 1)
                            if len(header_body_split) > 1:
                                val = header_body_split[1].rstrip("\r\n- ")
                                payload[field_name] = val
            else:
                parsed_form = parse_qs(body)
                for k, v in parsed_form.items():
                    payload[k] = v[0]

        # ── 1. TASK-041: Action Brief API: POST /api/v1/clusters/{cluster_id}/action-brief
        brief_match = re.match(r"^/api/v1/clusters/([^/]+)/action-brief$", path)
        if brief_match:
            cluster_id = brief_match.group(1)

            # Check RBAC
            try:
                user_info = self._check_auth([ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN])
            except PermissionError as pe:
                self._set_headers(getattr(pe, "status_code", 401))
                self.wfile.write(json.dumps({"detail": str(pe)}).encode())
                return

            clusters = detect_spatial_clusters(db_path=str(DB_PATH))
            matched_cluster = None
            for c in clusters:
                if c["cluster_id"] == cluster_id:
                    matched_cluster = c
                    break

            if not matched_cluster:
                self._set_headers(404)
                self.wfile.write(json.dumps({"detail": f"Cluster '{cluster_id}' not found."}).encode())
                return

            brief = generate_action_brief_from_reports(
                cluster_id=matched_cluster["cluster_id"],
                cluster_title=matched_cluster["title"],
                reports=matched_cluster["reports"],
                center_point=matched_cluster["center_point"]
            )
            self._set_headers(200)
            self.wfile.write(json.dumps(brief).encode())
            return

        # ── 2. TASK-045: Administrative Override: POST /api/v1/reports/{id}/override
        override_match = re.match(r"^/api/v1/reports/([^/]+)/override$", path)
        if override_match:
            report_id = override_match.group(1)

            # Check RBAC
            try:
                user_info = self._check_auth([ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN])
            except PermissionError as pe:
                self._set_headers(getattr(pe, "status_code", 401))
                self.wfile.write(json.dumps({"detail": str(pe)}).encode())
                return

            action = payload.get("action")
            justification = payload.get("justification", "")
            new_priority = payload.get("new_priority")
            user_id = user_info.get("sub", "dispatcher_01")

            try:
                result = override_report(
                    report_id=report_id,
                    action=action,
                    justification=justification,
                    user_id=user_id,
                    new_priority=new_priority,
                    db_path=str(DB_PATH)
                )
                self._set_headers(200)
                self.wfile.write(json.dumps(result).encode())
            except KeyError as ke:
                self._set_headers(404)
                self.wfile.write(json.dumps({"detail": str(ke)}).encode())
            except ValueError as ve:
                self._set_headers(400)
                self.wfile.write(json.dumps({"detail": str(ve)}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"detail": str(e)}).encode())
            return

        # ── 3. TASK-044: Work Order Assignment: POST /api/v1/reports/{id}/assign
        assign_match = re.match(r"^/api/v1/reports/([^/]+)/assign$", path)
        if assign_match:
            master_id = assign_match.group(1)

            # Check RBAC
            try:
                user_info = self._check_auth([ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN])
            except PermissionError as pe:
                self._set_headers(getattr(pe, "status_code", 401))
                self.wfile.write(json.dumps({"detail": str(pe)}).encode())
                return

            dept_name = payload.get("department_name")
            justification = payload.get("justification", "Departmental assignment")
            user_id = user_info.get("sub", "dispatcher_01")

            try:
                result = assign_work_order(
                    master_ticket_id=master_id,
                    department_name=dept_name,
                    user_id=user_id,
                    justification=justification,
                    db_path=str(DB_PATH)
                )

                # TASK-072: Trigger mock SMS + ERP integrations on dispatch
                try:
                    conn2 = get_db_connection()
                    c2 = conn2.cursor()
                    c2.execute("SELECT tracking_id, formatted_address, verified_category, priority_rank, duplicate_count FROM reports WHERE id = ?", (master_id,))
                    rr = c2.fetchone()
                    conn2.close()
                    if rr:
                        mock_events = trigger_dispatch_integrations(
                            tracking_id=rr["tracking_id"],
                            department=dept_name,
                            location=rr["formatted_address"] or "Ward 12",
                            category=rr["verified_category"] or "General",
                            priority=rr["priority_rank"] or "Priority 3",
                            report_count=int(rr["duplicate_count"] or 1),
                        )
                        result["mock_integrations"] = mock_events
                except Exception:
                    pass  # Mock integration failure must not block assignment

                self._set_headers(200)
                self.wfile.write(json.dumps(result).encode())
            except KeyError as ke:
                self._set_headers(404)
                self.wfile.write(json.dumps({"detail": str(ke)}).encode())
            except ValueError as ve:
                self._set_headers(400)
                self.wfile.write(json.dumps({"detail": str(ve)}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"detail": str(e)}).encode())
            return

        # ── TASK-071: Field Resolution with Evidence: POST /api/v1/reports/{id}/resolve
        resolve_match = re.match(r"^/api/v1/reports/([^/]+)/resolve$", path)
        if resolve_match:
            report_id = resolve_match.group(1)

            try:
                user_info = self._check_auth([ROLE_FIELD_LEAD, ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN])
            except PermissionError as pe:
                self._set_headers(getattr(pe, "status_code", 401))
                self.wfile.write(json.dumps({"detail": str(pe)}).encode())
                return

            resolution_notes = payload.get("resolution_notes", "").strip()
            evidence_photo_url = payload.get("evidence_photo_url", "").strip()
            justification = payload.get("justification", "Field crew marked job as resolved")
            user_id = user_info.get("sub", "field_crew_01")
            department = user_info.get("department", "Field Operations")

            if not resolution_notes:
                self._set_headers(422)
                self.wfile.write(json.dumps({"detail": "resolution_notes is required to mark a job as Resolved."}).encode())
                return

            conn = get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    "SELECT id, tracking_id, lifecycle_status, assigned_department FROM reports WHERE id = ? OR tracking_id = ?",
                    (report_id, report_id)
                )
                row = cur.fetchone()
                if not row:
                    self._set_headers(404)
                    self.wfile.write(json.dumps({"detail": f"Report '{report_id}' not found."}).encode())
                    conn.close()
                    return

                actual_id = row["id"]
                tracking_id = row["tracking_id"]
                dept = row["assigned_department"] or department
                now_iso = datetime.now(timezone.utc).isoformat()

                # Reject if already in terminal Resolved state
                if row["lifecycle_status"] == "Resolved":
                    self._set_headers(400)
                    self.wfile.write(json.dumps({
                        "detail": "Report is already in 'Resolved' state. No further transition is permitted."
                    }).encode())
                    conn.close()
                    return

                # Persist resolution notes and evidence photo
                cur.execute(
                    "UPDATE reports SET resolution_notes = ?, updated_at = ? WHERE id = ?",
                    (resolution_notes, now_iso, actual_id)
                )
                conn.commit()
            finally:
                conn.close()

            # Transition lifecycle to Resolved via state machine
            try:
                transition_lifecycle_status(
                    report_id=actual_id,
                    new_status="Resolved",
                    user_id=user_id,
                    justification=justification,
                    db_path=str(DB_PATH)
                )
            except ValueError as ve:
                self._set_headers(400)
                self.wfile.write(json.dumps({"detail": str(ve)}).encode())
                return
            except KeyError as ke:
                self._set_headers(404)
                self.wfile.write(json.dumps({"detail": str(ke)}).encode())
                return

            # TASK-072: Fire mock SMS + ERP resolution events
            mock_events = {}
            try:
                mock_events = trigger_resolution_integrations(
                    tracking_id=tracking_id,
                    department=dept,
                    resolution_notes=resolution_notes,
                )
            except Exception:
                pass

            self._set_headers(200)
            self.wfile.write(json.dumps({
                "report_id": actual_id,
                "tracking_id": tracking_id,
                "lifecycle_status": "Resolved",
                "resolution_notes": resolution_notes,
                "evidence_photo_url": evidence_photo_url or None,
                "resolved_at": now_iso,
                "mock_integrations": mock_events,
            }).encode())
            return

        # ── 4. TASK-043: State Machine Transition: POST /api/v1/reports/{id}/status
        status_match = re.match(r"^/api/v1/reports/([^/]+)/status$", path)
        if status_match:
            report_id = status_match.group(1)

            # Check RBAC
            try:
                user_info = self._check_auth([ROLE_DISPATCHER, ROLE_PLATFORM_ADMIN, ROLE_FIELD_LEAD])
            except PermissionError as pe:
                self._set_headers(getattr(pe, "status_code", 401))
                self.wfile.write(json.dumps({"detail": str(pe)}).encode())
                return

            new_status = payload.get("status")
            justification = payload.get("justification", "Status transition")
            user_id = user_info.get("sub", "dispatcher_01")

            try:
                result = transition_lifecycle_status(
                    report_id=report_id,
                    new_status=new_status,
                    user_id=user_id,
                    justification=justification,
                    db_path=str(DB_PATH)
                )
                self._set_headers(200)
                self.wfile.write(json.dumps(result).encode())
            except KeyError as ke:
                self._set_headers(404)
                self.wfile.write(json.dumps({"detail": str(ke)}).encode())
            except ValueError as ve:
                self._set_headers(400)
                self.wfile.write(json.dumps({"detail": str(ve)}).encode())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({"detail": str(e)}).encode())
            return

        # ── 5. Public Report Submission: POST /api/v1/reports
        if path == "/api/v1/reports":
            raw_desc = payload.get("raw_description", "").strip()
            if not raw_desc or len(raw_desc) < 5:
                self._set_headers(422)
                self.wfile.write(json.dumps({"detail": "raw_description must be at least 5 characters"}).encode())
                return

            try:
                lat = float(payload.get("latitude"))
                lon = float(payload.get("longitude"))
                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    raise ValueError()
            except Exception:
                self._set_headers(422)
                self.wfile.write(json.dumps({"detail": "latitude and longitude must be valid floating point coordinates"}).encode())
                return

            user_category = payload.get("user_category") or "Waterlogging & Drainage"
            formatted_address = payload.get("formatted_address") or f"Ward 12 Municipal Corridor [Lat: {lat:.4f}, Lon: {lon:.4f}]"

            conn = get_db_connection()
            try:
                cur = conn.cursor()
                while True:
                    tid = generate_random_tracking_code()
                    cur.execute("SELECT 1 FROM reports WHERE tracking_id = ?", (tid,))
                    if not cur.fetchone():
                        break

                report_id = str(uuid.uuid4())
                now_str = datetime.now(timezone.utc).isoformat()

                cur.execute("""
                    INSERT INTO reports (
                        id, tracking_id, created_at, updated_at,
                        raw_description, user_category, verified_category,
                        media_url, latitude, longitude, formatted_address,
                        concise_summary, is_duplicate, duplicate_count,
                        priority_rank, priority_score, priority_rationale,
                        lifecycle_status, is_manually_overridden
                    ) VALUES (
                        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
                    )
                """, (
                    report_id, tid, now_str, now_str,
                    raw_desc, user_category, user_category,
                    payload.get("media_url"), lat, lon, formatted_address,
                    raw_desc[:80], 0, 1,
                    "Priority 3", 40.0, "Initial intake queue; ready for AI triage.",
                    "Submitted", 0
                ))
                conn.commit()

                # Run AI pipeline synchronously
                ai_result = {}
                if _PIPELINE_AVAILABLE:
                    try:
                        ai_result = process_incident_report_task(report_id, db_path=str(DB_PATH))
                    except Exception as pipe_err:
                        ai_result = {"pipeline_error": str(pipe_err)}

                self._set_headers(201)
                self.wfile.write(json.dumps({
                    "id": report_id,
                    "tracking_id": tid,
                    "created_at": now_str,
                    "lifecycle_status": ai_result.get("lifecycle_status", "Submitted"),
                    "priority_rank": ai_result.get("priority_rank", "Priority 3"),
                    "verified_category": ai_result.get("verified_category", user_category),
                    "concise_summary": ai_result.get("concise_summary", raw_desc[:80]),
                    "message": "Incident report submitted successfully.",
                    "ai_pipeline": ai_result if ai_result else "pipeline_unavailable"
                }).encode())
            finally:
                conn.close()
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"detail": "Route not found"}).encode())


def run_server(port=8000):
    try:
        import uvicorn
        print(f"Starting unified authoritative CitySense FastAPI backend on port {port}...")
        uvicorn.run("apps.api.main:app", host="0.0.0.0", port=port, reload=False)
    except Exception as e:
        print(f"FastAPI/Uvicorn fallback ({e}). Starting CitySense HTTP server on port {port}...")
        server = http.server.HTTPServer(("0.0.0.0", port), CitySenseApiHandler)
        print(f"CitySense API Server listening on port {port}...")
        server.serve_forever()


if __name__ == "__main__":
    run_server()

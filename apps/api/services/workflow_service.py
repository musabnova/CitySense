"""
TASK-043: Lifecycle State Machine Controller
TASK-044: Departmental Work Order Assignment & Child Ticket Sync Service
TASK-045: Administrative Priority & Duplicate Override Service
=============================================================================
Stage: Stage 4: Act / State Machine, Dispatch & Human-in-the-Loop
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from apps.api.services.audit_service import record_audit_log

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "citysense.db"

# Strict Lifecycle Progression Definition
VALID_STATUSES = ["Submitted", "Under Review", "Assigned", "Resolved"]
PERMITTED_TRANSITIONS = {
    "Submitted": ["Under Review"],
    "Under Review": ["Assigned"],
    "Assigned": ["Resolved"],
    "Resolved": []  # Terminal state (can be re-opened via administrative override)
}

VALID_PRIORITIES = ["Priority 1", "Priority 2", "Priority 3", "Priority 4"]


def transition_lifecycle_status(
    report_id: str,
    new_status: str,
    user_id: str = "dispatcher_01",
    justification: str = "Standard workflow progression",
    db_path: str = None
) -> Dict[str, Any]:
    """
    Enforces strict state machine transitions:
    Submitted -> Under Review -> Assigned -> Resolved.
    Rejects invalid state transitions by raising ValueError (mapping to HTTP 400).
    """
    if new_status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{new_status}'. Allowed statuses: {VALID_STATUSES}")

    path = db_path or str(DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, tracking_id, lifecycle_status FROM reports WHERE id = ?", (report_id,))
        row = cur.fetchone()
        if not row:
            raise KeyError(f"Report '{report_id}' not found.")

        current_status = row["lifecycle_status"]

        if current_status == new_status:
            return {"report_id": report_id, "current_status": current_status, "updated": False}

        allowed_next = PERMITTED_TRANSITIONS.get(current_status, [])
        if new_status not in allowed_next:
            raise ValueError(
                f"Illegal state transition from '{current_status}' to '{new_status}'. "
                f"Permitted progression: {' -> '.join(VALID_STATUSES)}"
            )

        now_iso = datetime.now(timezone.utc).isoformat()
        cur.execute("""
            UPDATE reports
            SET lifecycle_status = ?, updated_at = ?
            WHERE id = ?
        """, (new_status, now_iso, report_id))
        conn.commit()

        # Audit logging
        record_audit_log(
            report_id=report_id,
            user_id=user_id,
            action_type="LIFECYCLE_TRANSITION",
            previous_value=current_status,
            new_value=new_status,
            justification=justification,
            db_path=path
        )

        return {
            "report_id": report_id,
            "previous_status": current_status,
            "lifecycle_status": new_status,
            "updated_at": now_iso
        }
    finally:
        conn.close()


def assign_work_order(
    master_ticket_id: str,
    department_name: str,
    user_id: str = "dispatcher_01",
    justification: str = "Dispatched work order to municipal department",
    db_path: str = None
) -> Dict[str, Any]:
    """
    TASK-044: Atomically assigns a master ticket to department and automatically
    synchronizes all linked child duplicates to 'Assigned'.
    """
    if not department_name or not department_name.strip():
        raise ValueError("department_name is required for work order assignment.")

    path = db_path or str(DEFAULT_DB_PATH)
    now_iso = datetime.now(timezone.utc).isoformat()

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        # Find master ticket (by ID or tracking_id)
        cur.execute("""
            SELECT id, tracking_id, lifecycle_status, assigned_department
            FROM reports WHERE id = ? OR tracking_id = ?
        """, (master_ticket_id, master_ticket_id))
        master_row = cur.fetchone()
        if not master_row:
            raise KeyError(f"Master ticket '{master_ticket_id}' not found.")

        actual_master_id = master_row["id"]
        prev_dept = master_row["assigned_department"] or "Unassigned"
        prev_status = master_row["lifecycle_status"]

        # Update Master ticket
        cur.execute("""
            UPDATE reports
            SET lifecycle_status = 'Assigned',
                assigned_department = ?,
                dispatch_timestamp = ?,
                updated_at = ?
            WHERE id = ?
        """, (department_name, now_iso, now_iso, actual_master_id))

        # Find all linked child reports
        cur.execute("SELECT id, tracking_id FROM reports WHERE master_ticket_id = ?", (actual_master_id,))
        child_rows = cur.fetchall()
        child_ids = [c["id"] for c in child_rows]

        # Atomically update all child reports
        if child_ids:
            placeholders = ",".join("?" for _ in child_ids)
            cur.execute(f"""
                UPDATE reports
                SET lifecycle_status = 'Assigned',
                    assigned_department = ?,
                    dispatch_timestamp = ?,
                    updated_at = ?
                WHERE id IN ({placeholders})
            """, [department_name, now_iso, now_iso] + child_ids)

        conn.commit()

        # Audit logs for master and children
        record_audit_log(
            report_id=actual_master_id,
            user_id=user_id,
            action_type="ASSIGN_WORK_ORDER",
            previous_value=f"status={prev_status}, dept={prev_dept}",
            new_value=f"status=Assigned, dept={department_name}",
            justification=justification,
            db_path=path
        )

        for cid in child_ids:
            record_audit_log(
                report_id=cid,
                user_id=user_id,
                action_type="CHILD_TICKET_SYNC",
                previous_value="status=Under Review",
                new_value=f"status=Assigned, dept={department_name} (synced from master {actual_master_id})",
                justification=f"Automated child ticket synchronization from master ticket {actual_master_id}",
                db_path=path
            )

        return {
            "master_ticket_id": actual_master_id,
            "master_tracking_id": master_row["tracking_id"],
            "assigned_department": department_name,
            "lifecycle_status": "Assigned",
            "dispatch_timestamp": now_iso,
            "synchronized_children_count": len(child_ids),
            "affected_child_ids": child_ids,
            "total_updated_reports": 1 + len(child_ids)
        }
    finally:
        conn.close()


def override_report(
    report_id: str,
    action: str,
    justification: str,
    user_id: str = "dispatcher_01",
    new_priority: Optional[str] = None,
    db_path: str = None
) -> Dict[str, Any]:
    """
    TASK-045: Administrative priority & duplicate override endpoint handler.
    Supports actions: 'SET_PRIORITY', 'UNLINK_DUPLICATE'.
    Updates reports and writes audit entry into report_audit_logs.
    """
    if not justification or len(justification.strip()) < 5:
        raise ValueError("A clear justification (minimum 5 characters) is required for administrative override.")

    path = db_path or str(DEFAULT_DB_PATH)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT id, tracking_id, priority_rank, priority_score,
                   is_duplicate, master_ticket_id, duplicate_count
            FROM reports WHERE id = ? OR tracking_id = ?
        """, (report_id, report_id))
        row = cur.fetchone()
        if not row:
            raise KeyError(f"Report '{report_id}' not found.")

        actual_id = row["id"]
        now_iso = datetime.now(timezone.utc).isoformat()

        if action == "SET_PRIORITY":
            if new_priority not in VALID_PRIORITIES:
                raise ValueError(f"Invalid new_priority '{new_priority}'. Allowed: {VALID_PRIORITIES}")

            old_priority = row["priority_rank"]
            cur.execute("""
                UPDATE reports
                SET priority_rank = ?,
                    is_manually_overridden = 1,
                    override_reason = ?,
                    overridden_by_user_id = ?,
                    updated_at = ?
                WHERE id = ?
            """, (new_priority, justification, user_id, now_iso, actual_id))
            conn.commit()

            record_audit_log(
                report_id=actual_id,
                user_id=user_id,
                action_type="SET_PRIORITY",
                previous_value=old_priority,
                new_value=new_priority,
                justification=justification,
                db_path=path
            )

            return {
                "report_id": actual_id,
                "action": "SET_PRIORITY",
                "previous_priority": old_priority,
                "priority_rank": new_priority,
                "is_manually_overridden": True,
                "justification": justification
            }

        elif action == "UNLINK_DUPLICATE":
            old_master_id = row["master_ticket_id"]
            if not row["is_duplicate"] and not old_master_id:
                raise ValueError(f"Report '{actual_id}' is not currently marked as a duplicate.")

            # Decrement master duplicate_count
            if old_master_id:
                cur.execute("""
                    UPDATE reports
                    SET duplicate_count = MAX(1, duplicate_count - 1),
                        updated_at = ?
                    WHERE id = ?
                """, (now_iso, old_master_id))

            # Unlink report
            cur.execute("""
                UPDATE reports
                SET is_duplicate = 0,
                    master_ticket_id = NULL,
                    is_manually_overridden = 1,
                    override_reason = ?,
                    overridden_by_user_id = ?,
                    updated_at = ?
                WHERE id = ?
            """, (justification, user_id, now_iso, actual_id))
            conn.commit()

            record_audit_log(
                report_id=actual_id,
                user_id=user_id,
                action_type="UNLINK_DUPLICATE",
                previous_value=f"master_ticket_id={old_master_id}",
                new_value="master_ticket_id=None, is_duplicate=False",
                justification=justification,
                db_path=path
            )

            return {
                "report_id": actual_id,
                "action": "UNLINK_DUPLICATE",
                "unlinked_from_master_id": old_master_id,
                "is_duplicate": False,
                "is_manually_overridden": True,
                "justification": justification
            }

        else:
            raise ValueError(f"Unknown override action '{action}'. Supported actions: SET_PRIORITY, UNLINK_DUPLICATE.")

    finally:
        conn.close()

